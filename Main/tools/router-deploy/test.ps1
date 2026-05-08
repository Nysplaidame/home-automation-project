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
foreach ($iface in @("lan","management","automation","nvr","printers","storage","iot_sensors","monitoring","dmz","guest")) {
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
foreach ($dnsHost in @("homeassistant.home.local","docker-host.home.local","bambuddy.home.local","frigate.home.local","p1s.home.local","athena2.home.local","nas.home.local","printers.home.local","nvr.home.local")) {
    Run-Check -Name "DNS local mapping $dnsHost" -Command "uci show dhcp | grep -F `"$dnsHost`" || true" -MatchRegex ([regex]::Escape($dnsHost))
}

# External reachability checks (router-level sanity only)
Run-Check -Name "Router reaches 8.8.8.8" -Command "ping -c 1 -W 2 8.8.8.8 >/dev/null 2>&1 && echo OK || true" -MatchRegex "OK" -WarnOnly
Run-Check -Name "Reverse DNS sanity" -Command "nslookup 8.8.8.8 127.0.0.1 2>/dev/null | grep -Ei 'name|domain' || true" -MatchRegex "name|domain" -WarnOnly

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
    "Allow DHCP input iot_sensors",
    "Allow DNS input iot_sensors",
    "Allow DHCP input monitoring",
    "Allow DNS input monitoring",
    "Allow DHCP input dmz",
    "Allow DNS input dmz",
    "Allow DHCP input guest",
    "Allow DNS input guest",
    "Allow DNS input vpn_clients"
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
