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
    param([string]$Name, [string]$Status, [string]$Detail)
    $results.Add([PSCustomObject]@{ Name = $Name; Status = $Status; Detail = $Detail })
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
    } else {
        $status = if ($WarnOnly) { "WARN" } else { "FAIL" }
        Add-Result -Name $Name -Status $status -Detail ($r.Output.Trim())
    }
}

# VID -> UCI interface name mapping. Must match vlan-config.conf bridge-vlan entries.
# Update this table if VIDs change in the source config.
$VlanDefs = @(
    @{ VID = 1;  UCI = "lan";         Label = "LAN"         },
    @{ VID = 10; UCI = "management";  Label = "Management"  },
    @{ VID = 20; UCI = "automation";  Label = "Automation"  },
    @{ VID = 30; UCI = "nvr";         Label = "NVR"         },
    @{ VID = 35; UCI = "printers";    Label = "Printers"    },
    @{ VID = 40; UCI = "storage";     Label = "Storage"     },
    @{ VID = 50; UCI = "HomeIoT"; Label = "IoT Sensors" },
    @{ VID = 60; UCI = "monitoring";  Label = "Monitoring"  },
    @{ VID = 70; UCI = "dmz";         Label = "DMZ"         },
    @{ VID = 99; UCI = "guest";       Label = "Guest"       }
)

Write-Host "Router Connectivity Validation"
Write-Host "=============================="
Write-Host "Profile: $Profile"

# ============================================================
# SECTION 1 — PER-VLAN L3-UP PROBES
# Verifies each VLAN interface is live with an inet address
# and that the router can ping its own gateway IP on each
# segment — catching cases where UCI config loaded but the
# interface failed to come up.
# ============================================================
Write-Host ""
Write-Host "--- Section 1: Per-VLAN L3 Interface Health ---"

foreach ($vlan in $VlanDefs) {
    $vid = $vlan.VID
    $uci = $vlan.UCI
    $label = $vlan.Label

    # 1a: L3 device exists and has an inet address
    Run-Check `
        -Name "VLAN $vid ($label) inet addr" `
        -Command "ip -4 addr show br-lan.$vid 2>/dev/null | grep 'inet '" `
        -MatchRegex "inet \d"

    # 1b: UCI ifstatus reports link up
    Run-Check `
        -Name "VLAN $vid ($label) ifstatus up" `
        -Command "ifstatus $uci 2>/dev/null | grep '""up""'" `
        -MatchRegex '"up"\s*:\s*true'

    # 1c: Gateway self-ping — resolves the interface's own IP via UCI and pings it.
    # Distinguishes between "interface configured" and "interface actually routing."
    $pingCmd = @"
DEV=`$(uci -q get network.$uci.device 2>/dev/null)
if [ -z "`$DEV" ]; then echo NODEV; exit 0; fi
GWIP=`$(ip -4 addr show "`$DEV" 2>/dev/null | awk '/inet /{split(`$2,a,"/"); print a[1]; exit}')
if [ -z "`$GWIP" ]; then echo NOADDR; exit 0; fi
ping -c 1 -W 2 -I "`$DEV" "`$GWIP" >/dev/null 2>&1 && echo PING_OK || echo PING_FAIL
"@
    Run-Check `
        -Name "VLAN $vid ($label) gateway self-ping" `
        -Command $pingCmd `
        -MatchRegex "PING_OK"
}

# ============================================================
# SECTION 2 — DNSMASQ LEASE & RESOLUTION HEALTH
# Checks that dnsmasq is live and serving DNS on this router,
# not just that it was configured. On first-flight no DHCP
# leases are expected so those checks are WARN-only.
# ============================================================
Write-Host ""
Write-Host "--- Section 2: dnsmasq Health ---"

Run-Check `
    -Name "dnsmasq process running" `
    -Command "pidof dnsmasq >/dev/null 2>&1 && echo RUNNING || echo STOPPED" `
    -MatchRegex "RUNNING"

# Verify dnsmasq is bound to port 53 (ss preferred, fall back to netstat).
# Use explicit assignment because piping through `head -1` always exits 0,
# which would defeat a `||` fallback chain.
$listenCmd = @"
RES=`$(ss -ulnp 2>/dev/null | grep ':53 ' | head -1)
if [ -z "`$RES" ]; then RES=`$(netstat -uln 2>/dev/null | grep ':53 ' | head -1); fi
if [ -n "`$RES" ]; then echo LISTENING; else echo NOTLISTENING; fi
"@
Run-Check `
    -Name "dnsmasq listening :53" `
    -Command $listenCmd `
    -MatchRegex "LISTENING" -WarnOnly

# DNS resolution via the router's own resolver for known local hostnames.
# busybox nslookup emits "Address 1:" rather than "Address:", and `|| echo`
# after a pipe doesn't trigger when grep returns 0 — use explicit assignment.
foreach ($dnsName in @("homeassistant.home.local", "docker-host.home.local", "bambuddy.home.local", "adguard.home.local", "immich.home.local", "homepage.home.local", "dozzle.home.local", "ntfy.home.local", "searxng.home.local", "whoogle.home.local", "nas.home.local", "omv.home.local", "omv-nas.home.local", "frigate.home.local")) {
    $dnsCmd = @"
RES=`$(nslookup $dnsName 127.0.0.1 2>/dev/null | grep -iE '^Address' | grep -vF '127.0.0.1' | head -1)
if [ -n "`$RES" ]; then echo "RESOLVED `$RES"; else echo NORESOLVE; fi
"@
    Run-Check `
        -Name "DNS $dnsName resolves" `
        -Command $dnsCmd `
        -MatchRegex "RESOLVED" -WarnOnly
}

Run-Check `
    -Name "Router NTP server enabled" `
    -Command "e=`$(uci -q get system.ntp.enabled || true); s=`$(uci -q get system.ntp.enable_server || true); [ `"`$e`" = `"1`" ] && [ `"`$s`" = `"1`" ] && echo NTP_ENABLED || true" `
    -MatchRegex "NTP_ENABLED"

Run-Check `
    -Name "sysntpd process running" `
    -Command "/etc/init.d/sysntpd status >/dev/null 2>&1 || pidof sysntpd >/dev/null 2>&1; [ `$? -eq 0 ] && echo SYSNTPD_OK || true" `
    -MatchRegex "SYSNTPD_OK"

# Lease file — WARN on first-flight (no clients yet), FAIL on full profile.
# Regex anchor dropped because busybox `wc -l` may add leading whitespace.
$leaseCmd = "test -f /tmp/dhcp.leases && wc -l < /tmp/dhcp.leases || echo 0"
if ($Profile -eq "full") {
    Run-Check -Name "DHCP leases present" -Command $leaseCmd -MatchRegex "[1-9]"
} else {
    Run-Check -Name "DHCP leases present (first-flight: warn only)" -Command $leaseCmd -MatchRegex "[1-9]" -WarnOnly
}

# ============================================================
# SECTION 3 — ACTIVE NFT RULESET CHECKS
# test.ps1 checks 'uci show firewall' (intent).
# This section checks what is actually loaded in the kernel.
# A misconfigured /etc/init.d/firewall restart can leave UCI
# and nftables out of sync.
# ============================================================
Write-Host ""
Write-Host "--- Section 3: Active nftables State ---"

Run-Check `
    -Name "nft fw4 table loaded" `
    -Command "nft list tables 2>/dev/null | grep 'inet fw4' || echo MISSING" `
    -MatchRegex "inet fw4"

# firewall4 generates many chains (input/forward/output per zone + helper chains).
# Fewer than 20 suggests firewall failed to fully apply.
# `[[:space:]]` is portable across busybox grep; `\s` is GNU-only.
Run-Check `
    -Name "nft chain count >= 20" `
    -Command "nft list ruleset 2>/dev/null | grep -cE '^[[:space:]]*chain ' || echo 0" `
    -MatchRegex "^([2-9]\d|\d{3,})"

# Stateful conntrack rules must be loaded — without them accepted traffic
# cannot maintain state and connections silently break.
Run-Check `
    -Name "nft conntrack rules loaded" `
    -Command "nft list ruleset 2>/dev/null | grep -c 'ct state' || echo 0" `
    -MatchRegex "^[1-9]"

# Each zone must have at least an input or forward chain in the active ruleset.
foreach ($zone in @("lan", "management", "automation", "nvr", "printers",
                    "storage", "HomeIoT", "monitoring", "dmz", "guest", "wan")) {
    Run-Check `
        -Name "nft chains present for zone '$zone'" `
        -Command "nft list ruleset 2>/dev/null | grep -cE '^[[:space:]]*chain (input|forward)_$zone' || echo 0" `
        -MatchRegex "^[1-9]"
}

# Sanity: the loaded ruleset should contain reject/drop rules. Word boundaries
# (`\b`) are not portable in busybox grep; substring match is sufficient here.
Run-Check `
    -Name "nft reject/drop rules loaded (>= 5)" `
    -Command "nft list ruleset 2>/dev/null | grep -ciE 'reject|drop' || echo 0" `
    -MatchRegex "^([5-9]|\d{2,})"

# Restricted client zones still need router-originated replies for DHCP, DNS,
# NTP, and local services allowed by explicit input rules.
foreach ($zone in @("automation", "nvr", "printers", "storage", "HomeIoT",
                    "monitoring", "dmz", "guest", "vpn_clients")) {
    $outputCmd = @"
IDX=`$(uci show firewall | sed -n "s/^firewall\.@zone\[\([0-9]\+\)\]\.name='$zone'$/\1/p" | head -n 1)
if [ -n "`$IDX" ]; then
  uci -q get firewall.@zone[`$IDX].output
fi
"@
    Run-Check `
        -Name "firewall zone '$zone' router output allowed" `
        -Command $outputCmd `
        -MatchRegex "^ACCEPT$"
}

# ============================================================
# SECTION 4 — ZONE FORWARDING POLICY (per-pair, structural)
#
# Verifies that the LIVE nft ruleset enforces specific
# (src -> dst) pairs as expected, by inspecting whether
# forward_<src> contains a 'accept_to_<dst>' jump:
#
#   ACCEPT — accept_to_<dst> present in forward_<src>
#            (zone pair is explicitly permitted)
#   BLOCK  — accept_to_<dst> absent AND chain has default
#            reject/drop content (pair falls through to deny)
#
# This is structural, not a live traffic probe — it cannot
# detect rule-ordering bugs that defeat policy at runtime,
# only that the firewall4 ruleset matches the expected pair
# policy. Live traffic verification still requires a client
# on each VLAN.
#
# Depends on firewall4 helper-chain rendering (OpenWrt 22.03+
# default). Configurations that inline policy without the
# 'accept_to_<zone>' jump targets will give false negatives.
# ============================================================
Write-Host ""
Write-Host "--- Section 4: Zone Forwarding Policy (per-pair, structural) ---"

function Test-ZoneForward {
    param(
        [string]$SrcZone,
        [string]$DstZone,
        [ValidateSet("ACCEPT", "BLOCK")]
        [string]$Expected,
        [switch]$WarnOnly
    )
    $label = "nft $SrcZone -> $DstZone : $Expected"

    # firewall4 emits a 'jump accept_to_<dst>' rule in forward_<src> when UCI
    # allows that specific zone pair. The presence of that rule proves the
    # (src, dst) policy is permissive; its absence combined with default
    # reject content proves the pair is blocked by fall-through.
    #
    # Note: this depends on firewall4's helper-chain rendering, which is the
    # default on OpenWrt 22.03+. Configurations that inline rules without
    # the helper jumps (rare) will produce false negatives on ACCEPT checks.
    # `-w` (word match) prevents false positives where `accept_to_lan` would
    # also match a hypothetical `accept_to_lan_subnet` chain. Underscore is a
    # word char so the entire `accept_to_<zone>` token must match exactly.
    if ($Expected -eq "ACCEPT") {
        $cmd = "nft list chain inet fw4 forward_$SrcZone 2>/dev/null | grep -wc 'accept_to_$DstZone'"
        $regex = "^[1-9]"
    } else {
        # `grep -c` always emits a single integer line (including "0" on empty
        # input), so the captured values are safe to use in numeric comparisons.
        $cmd = @"
ACCEPTS=`$(nft list chain inet fw4 forward_$SrcZone 2>/dev/null | grep -wc 'accept_to_$DstZone')
REJECTS=`$(nft list chain inet fw4 forward_$SrcZone 2>/dev/null | grep -cE 'reject|drop')
if [ "`$ACCEPTS" -eq 0 ] && [ "`$REJECTS" -gt 0 ]; then
  echo BLOCKED
else
  echo "PERMITTED_OR_EMPTY accepts=`$ACCEPTS rejects=`$REJECTS"
fi
"@
        $regex = "^BLOCKED"
    }

    Run-Check -Name $label -Command $cmd -MatchRegex $regex -WarnOnly:$WarnOnly
}

function Test-IotAutomationPolicy {
    # IoT sensors have one deliberate exception to Home Assistant MQTT/TLS,
    # followed by broad rejects to the automation zone.
    $cmd = @"
CHAIN=`$(nft list chain inet fw4 forward_HomeIoT 2>/dev/null)
MQTT=`$(printf '%s\n' "`$CHAIN" | grep -c 'ip daddr 192\.168\.20\.101 tcp dport 8883.*accept_to_automation')
REJECT_TCP=`$(printf '%s\n' "`$CHAIN" | grep -c 'meta l4proto tcp.*reject_to_automation')
REJECT_UDP=`$(printf '%s\n' "`$CHAIN" | grep -c 'meta l4proto udp.*reject_to_automation')
if [ "`$MQTT" -ge 1 ] && [ "`$REJECT_TCP" -ge 1 ] && [ "`$REJECT_UDP" -ge 1 ]; then
  echo CONSTRAINED_IOT_TO_HA_ONLY
else
  echo "IOT_AUTOMATION_POLICY_FAIL mqtt=`$MQTT reject_tcp=`$REJECT_TCP reject_udp=`$REJECT_UDP"
fi
"@
    Run-Check `
        -Name "nft HomeIoT -> automation : constrained HA MQTT only" `
        -Command $cmd `
        -MatchRegex "^CONSTRAINED_IOT_TO_HA_ONLY"
}

# Trusted pairs — verify accept_to_<dst> jump exists in forward_<src>
Test-ZoneForward -SrcZone "lan"        -DstZone "wan"        -Expected "ACCEPT"
Test-ZoneForward -SrcZone "management" -DstZone "wan"        -Expected "ACCEPT"
Test-ZoneForward -SrcZone "automation" -DstZone "wan"        -Expected "ACCEPT" -WarnOnly

# Isolated pairs — verify NO accept_to_<dst> jump (traffic falls through to default reject)
Test-ZoneForward -SrcZone "HomeIoT"     -DstZone "lan"        -Expected "BLOCK"
Test-IotAutomationPolicy
Test-ZoneForward -SrcZone "guest"       -DstZone "lan"        -Expected "BLOCK"
Test-ZoneForward -SrcZone "guest"       -DstZone "management" -Expected "BLOCK"
Test-ZoneForward -SrcZone "guest"       -DstZone "HomeIoT"     -Expected "BLOCK"
Test-ZoneForward -SrcZone "dmz"         -DstZone "lan"        -Expected "BLOCK"
Test-ZoneForward -SrcZone "dmz"         -DstZone "automation" -Expected "BLOCK"

# NVR and printers — should not be able to initiate connections to management
Test-ZoneForward -SrcZone "nvr"      -DstZone "management" -Expected "BLOCK" -WarnOnly
Test-ZoneForward -SrcZone "printers" -DstZone "management" -Expected "BLOCK" -WarnOnly

# ============================================================
# SUMMARY
# ============================================================
Write-Host ""
$pass = @($results | Where-Object Status -eq "PASS").Count
$warn = @($results | Where-Object Status -eq "WARN").Count
$fail = @($results | Where-Object Status -eq "FAIL").Count
Write-Host "Summary: PASS=$pass WARN=$warn FAIL=$fail"
if ($fail -gt 0) { exit 1 }
if ($warn -gt 0) { exit 2 }
exit 0
