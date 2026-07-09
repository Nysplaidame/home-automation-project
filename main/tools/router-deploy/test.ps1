param(
    [string]$RouterIp = "192.168.1.1",
    [ValidateSet("first-flight", "full")]
    [string]$Profile = "first-flight"
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$ScriptRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
. (Join-Path $ScriptRoot "lib\ssh_session.ps1")

$results = New-Object System.Collections.Generic.List[object]

trap {
    Write-Host "[ERROR] $($_.Exception.Message)" -ForegroundColor Red
    $resVar = Get-Variable -Name results -Scope Script -ErrorAction SilentlyContinue
    if ($resVar -and $resVar.Value.Count -gt 0) {
        Write-Host ""
        Write-Host "Partial Results:"
        $resVar.Value | Format-Table -AutoSize
    }
    exit 1
}

$KeyPath = Join-Path $ScriptRoot "keys\router_deploy"

if (-not (Test-Path $KeyPath)) {
    Write-Host "[ERROR] Missing key: $KeyPath" -ForegroundColor Red
    exit 1
}

if (-not (Test-RouterAlive -KeyPath $KeyPath -RouterIp $RouterIp)) {
    Write-Host "[ERROR] Router not reachable with key auth." -ForegroundColor Red
    exit 1
}

function Add-Result {
    param(
        [string]$Name,
        [string]$Status,
        [string]$Detail
    )
    $results.Add([PSCustomObject]@{
        Name = $Name
        Status = $Status
        Detail = $Detail
    })
    $color = if ($Status -eq "PASS") { "Green" } elseif ($Status -eq "WARN") { "Yellow" } else { "Red" }
    Write-Host "[$Status] $Name - $Detail" -ForegroundColor $color
}

function Run-Check {
    param(
        [string]$Name,
        [string]$Command,
        [string]$MatchRegex,
        [switch]$WarnOnly
    )
    $r = Invoke-RouterScript -KeyPath $KeyPath -RouterIp $RouterIp -Script $Command
    if ($r.ExitCode -eq 0 -and $r.Output -match $MatchRegex) {
        Add-Result -Name $Name -Status "PASS" -Detail "matched '$MatchRegex'"
    }
    else {
        $status = if ($WarnOnly) { "WARN" } else { "FAIL" }
        Add-Result -Name $Name -Status $status -Detail ($r.Output.Trim())
    }
}

Write-Host "Router Post-Deploy Validation"
Write-Host "============================="
Write-Host "Profile: $Profile"

# VLAN interfaces present
foreach ($vlan in @(1,10,20,30,35,40,50,60,70,99)) {
    Run-Check -Name "VLAN $vlan interface" -Command "ip -4 addr show br-lan.$vlan || true" -MatchRegex "br-lan\.$vlan"
}

# DHCP scopes present
foreach ($iface in @("lan","management","automation","nvr","printers","storage","HomeIoT","monitoring","dmz","guest")) {
    Run-Check -Name "DHCP scope $iface" -Command "uci show dhcp.$iface 2>/dev/null || true" -MatchRegex "dhcp\.$iface="
}

# SSID checks via UCI, not scan
foreach ($ssid in @("HomeMain","HomeAdmin","HomePrinters","HomeIoT","HomeGuest")) {
    Run-Check -Name "SSID $ssid configured" -Command "uci show wireless | grep -F `"ssid='$ssid'`" || true" -MatchRegex ([regex]::Escape($ssid))
}

$wifiIfaces = @(
    "main_2g",
    "main_5g",
    "admin_5g",
    "admin_2g",
    "printers_2g",
    "printers_5g",
    "iot_2g",
    "guest_2g"
)
if ($Profile -eq "first-flight") {
    foreach ($iface in $wifiIfaces) {
        Run-Check -Name "WiFi iface $iface disabled (first-flight)" -Command "v=`$(uci -q get wireless.$iface.disabled || true); [ `"`$v`" = `"1`" ] && echo DISABLED || true" -MatchRegex "DISABLED"
    }
    Run-Check -Name "WiFi iface dmz_5g disabled (first-flight)" -Command "v=`$(uci -q get wireless.dmz_5g.disabled || true); [ `"`$v`" = `"1`" ] && echo DISABLED || true" -MatchRegex "DISABLED"
}
else {
    foreach ($iface in $wifiIfaces) {
        Run-Check -Name "WiFi iface $iface enabled (full)" -Command "v=`$(uci -q get wireless.$iface.disabled || true); [ `"`$v`" != `"1`" ] && echo ENABLED || true" -MatchRegex "ENABLED"
    }
    Run-Check -Name "WiFi iface dmz_5g disabled (full)" -Command "v=`$(uci -q get wireless.dmz_5g.disabled || true); [ `"`$v`" = `"1`" ] && echo DISABLED || true" -MatchRegex "DISABLED"
}

# DNS local host entries
foreach ($dnsHost in @("homeassistant.home.local","docker-host.home.local","bambuddy.home.local","adguard.home.local","immich.home.local","homepage.home.local","dozzle.home.local","frigate.home.local","p1s.home.local","athena2.home.local","nas.home.local","omv.home.local","omv-nas.home.local","printers.home.local","nvr.home.local")) {
    Run-Check -Name "DNS local mapping $dnsHost" -Command "uci show dhcp | grep -F `"$dnsHost`" || true" -MatchRegex ([regex]::Escape($dnsHost))
}

# DNS forwarding architecture
Run-Check -Name "DNS upstream first is AdGuard" -Command "uci -q get dhcp.@dnsmasq[0].server | tr ' ' '\n' | head -1" -MatchRegex "^192\.168\.20\.102#53$"
Run-Check -Name "DNS fallback includes Quad9" -Command "uci -q get dhcp.@dnsmasq[0].server | tr ' ' '\n' | grep -Fx '9.9.9.9' || true" -MatchRegex "^9\.9\.9\.9$"
Run-Check -Name "DNS fallback excludes Google" -Command "uci -q get dhcp.@dnsmasq[0].server | tr ' ' '\n' | grep -E '^(8\.8\.8\.8|8\.8\.4\.4)$' || echo NO_GOOGLE" -MatchRegex "^NO_GOOGLE$"
Run-Check -Name "DNS strict order enabled" -Command "uci -q get dhcp.@dnsmasq[0].strictorder || true" -MatchRegex "^1$"
Run-Check -Name "IoT DHCP option 42 absent" -Command "uci -q get dhcp.HomeIoT.dhcp_option | tr ' ' '\n' | grep -E '^42(,|$)' || echo NO_OPTION_42" -MatchRegex "^NO_OPTION_42$"

# Router-local NTP
Run-Check -Name "Router NTP server enabled" -Command "e=`$(uci -q get system.ntp.enabled || true); s=`$(uci -q get system.ntp.enable_server || true); [ `"`$e`" = `"1`" ] && [ `"`$s`" = `"1`" ] && echo NTP_ENABLED || true" -MatchRegex "NTP_ENABLED"
Run-Check -Name "sysntpd running" -Command "/etc/init.d/sysntpd status >/dev/null 2>&1 || pidof sysntpd >/dev/null 2>&1; [ `$? -eq 0 ] && echo SYSNTPD_OK || true" -MatchRegex "SYSNTPD_OK"

# External reachability checks (router-level sanity only)
Run-Check -Name "Router reaches 1.1.1.1" -Command "ping -c 1 -W 2 1.1.1.1 >/dev/null 2>&1 && echo OK || true" -MatchRegex "OK" -WarnOnly
Run-Check -Name "Reverse DNS sanity" -Command "nslookup 1.1.1.1 127.0.0.1 2>/dev/null | grep -Ei 'name|domain' || true" -MatchRegex "name|domain" -WarnOnly

# Critical firewall rule names
$criticalRules = @(
    "Allow DHCP input automation",
    "Allow DNS input automation",
    "Allow DHCP input nvr",
    "Allow DNS input nvr",
    "Allow DHCP input printers",
    "Allow DNS input printers",
    "Allow DHCP input storage",
    "Allow DNS input storage",
    "Allow DHCP input HomeIoT",
    "Allow DNS input HomeIoT",
    "Allow DHCP input monitoring",
    "Allow DNS input monitoring",
    "Allow DHCP input dmz",
    "Allow DNS input dmz",
    "Allow DHCP input guest",
    "Allow DNS input guest",
    "Allow DNS input vpn_clients",
    "Docker Host AdGuard Upstream DNS",
    "Docker Host Tailscale Egress",
    "Docker Host to InfluxDB",
    "LAN to Docker Host App UIs",
    "VPN to OMV NAS",
    "Block VPN to Storage",
    "Automation to Router NTP",
    "NVR to Router NTP",
    "Monitoring to Router NTP",
    "Storage to Router NTP",
    "Printers to Router NTP",
    "IoT to Router NTP"
)
foreach ($rule in $criticalRules) {
    Run-Check -Name "Firewall rule '$rule'" -Command "uci show firewall | grep -F `"name='$rule'`" || true" -MatchRegex ([regex]::Escape($rule))
}

Write-Host ""
$pass = @($results | Where-Object Status -eq "PASS").Count
$warn = @($results | Where-Object Status -eq "WARN").Count
$fail = @($results | Where-Object Status -eq "FAIL").Count
Write-Host "Summary: PASS=$pass WARN=$warn FAIL=$fail"
if ($fail -gt 0) { exit 1 }
if ($warn -gt 0) { exit 2 }
exit 0
