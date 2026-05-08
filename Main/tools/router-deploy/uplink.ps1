param(
    [ValidateSet("enable", "disable", "status")]
    [string]$Action = "status",
    [string]$RouterIp = "192.168.1.1",
    [string]$ConfigPath = ""
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

trap {
    Write-Host "[ERROR] $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

$ScriptRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
. (Join-Path $ScriptRoot "lib\ssh_session.ps1")

$KeyPath = Join-Path $ScriptRoot "keys\router_deploy"
if ([string]::IsNullOrWhiteSpace($ConfigPath)) {
    $ConfigPath = Join-Path $ScriptRoot "keys\uplink_wifi.json"
}

function Fail([string]$Message) {
    throw $Message
}

function Escape-ShSingle([string]$Value) {
    return ($Value -replace "'", "'\''")
}

function Require-RouterConnection {
    if (-not (Test-Path $KeyPath)) {
        Fail "Missing key: $KeyPath"
    }
    if (-not (Test-RouterAlive -KeyPath $KeyPath -RouterIp $RouterIp)) {
        Fail "Router not reachable with key auth at root@$RouterIp"
    }
}

function Load-UplinkConfig {
    if (-not (Test-Path $ConfigPath)) {
        Fail "Missing uplink config: $ConfigPath (copy keys/uplink_wifi.example.json to keys/uplink_wifi.json and fill values)"
    }
    $cfg = Get-Content -Raw -LiteralPath $ConfigPath | ConvertFrom-Json
    if ([string]::IsNullOrWhiteSpace($cfg.ssid)) {
        Fail "uplink config missing 'ssid'"
    }
    if ([string]::IsNullOrWhiteSpace($cfg.psk)) {
        Fail "uplink config missing 'psk'"
    }
    if ($null -eq $cfg.PSObject.Properties["device"] -or [string]::IsNullOrWhiteSpace($cfg.device)) {
        $cfg | Add-Member -NotePropertyName device -NotePropertyValue "radio1" -Force
    }
    if ($null -eq $cfg.PSObject.Properties["encryption"] -or [string]::IsNullOrWhiteSpace($cfg.encryption)) {
        $cfg | Add-Member -NotePropertyName encryption -NotePropertyValue "psk2" -Force
    }
    if ($null -eq $cfg.PSObject.Properties["bssid"]) {
        $cfg | Add-Member -NotePropertyName bssid -NotePropertyValue "" -Force
    }
    # Validate fields used inside shell double-quoted regex contexts where
    # Escape-ShSingle (single-quote escape) does not protect them. Restricting
    # to a simple identifier keeps grep-regex/sed contexts safe and avoids
    # both shell injection and false-negative matches against UCI output.
    if ($cfg.device -notmatch '^[A-Za-z0-9_-]+$') {
        Fail "uplink config 'device' must be [A-Za-z0-9_-]+ (got: '$($cfg.device)')"
    }
    if ($cfg.encryption -notmatch '^[A-Za-z0-9_+-]+$') {
        Fail "uplink config 'encryption' must be [A-Za-z0-9_+-]+ (got: '$($cfg.encryption)')"
    }
    if ($cfg.bssid -and $cfg.bssid -notmatch '^[0-9A-Fa-f:]+$') {
        Fail "uplink config 'bssid' must be a MAC literal (got: '$($cfg.bssid)')"
    }
    return $cfg
}

function Enable-Uplink {
    $cfg = Load-UplinkConfig
    $ssid = Escape-ShSingle $cfg.ssid
    $psk = Escape-ShSingle $cfg.psk
    $device = Escape-ShSingle $cfg.device
    $encryption = Escape-ShSingle $cfg.encryption
    $bssidCmd = ""
    if (-not [string]::IsNullOrWhiteSpace($cfg.bssid)) {
        $bssid = Escape-ShSingle $cfg.bssid
        $bssidCmd = "uci set wireless.router_uplink.bssid='$bssid' || return 1"
    }

    $warnCmd = @"
ACTIVE_APS=`$(uci show wireless 2>/dev/null | grep "\.device='$device'" | sed 's/\.device=.*//' | while read -r s; do uci -q get "`${s}.mode" 2>/dev/null; done | grep -q "^ap" && echo yes || true)
if [ -n "`$ACTIVE_APS" ]; then
  echo UPLINK_WARN_ACTIVE_AP_SAME_RADIO
fi
"@
    $warn = Invoke-RouterScript -KeyPath $KeyPath -RouterIp $RouterIp -Script $warnCmd
    if ($warn.ExitCode -eq 0 -and $warn.Output -match "UPLINK_WARN_ACTIVE_AP_SAME_RADIO") {
        Write-Host "[WARN] Active AP interface(s) detected on $($cfg.device). Enabling STA uplink may force 5GHz channel alignment with upstream AP." -ForegroundColor Yellow
    }

    $cmd = @"
set -e
TS=`$(date +%Y%m%d_%H%M%S)
BACKDIR=/tmp/router-uplink-backup/`$TS
mkdir -p "`$BACKDIR"
cp /etc/config/network "`$BACKDIR"/network
cp /etc/config/wireless "`$BACKDIR"/wireless
cp /etc/config/firewall "`$BACKDIR"/firewall
rollback_uplink() {
  cp "`$BACKDIR"/network /etc/config/network
  cp "`$BACKDIR"/wireless /etc/config/wireless
  cp "`$BACKDIR"/firewall /etc/config/firewall
  ifdown wwan_uplink 2>/dev/null || true
  wifi reload || true
  /etc/init.d/network reload || true
  sleep 4
  /etc/init.d/firewall restart
  echo UPLINK_ROLLBACK_OK
}
fail_rollback() {
  rollback_uplink
  exit 1
}

# do_uplink uses explicit '|| return 1' on each command rather than relying on
# 'set -e' inside a '{...} || handler' block — POSIX shells suspend 'set -e'
# inside grouped commands of an AND-OR list, so intermediate failures would be
# silently ignored. With explicit checks, any failed command triggers rollback.
do_uplink() {
  uci -q delete network.wwan_uplink
  uci -q delete wireless.router_uplink
  uci set network.wwan_uplink='interface' || return 1
  uci set network.wwan_uplink.proto='dhcp' || return 1
  uci set network.wwan_uplink.metric='30' || return 1
  uci set wireless.router_uplink='wifi-iface' || return 1
  uci set wireless.router_uplink.device='$device' || return 1
  uci set wireless.router_uplink.mode='sta' || return 1
  uci set wireless.router_uplink.network='wwan_uplink' || return 1
  uci set wireless.router_uplink.ssid='$ssid' || return 1
  uci set wireless.router_uplink.encryption='$encryption' || return 1
  uci set wireless.router_uplink.key='$psk' || return 1
  uci set wireless.router_uplink.disabled='0' || return 1
  $bssidCmd

  WAN_IDX=`$(uci show firewall | sed -n "s/^firewall\.@zone\[\([0-9]\+\)\]\.name='wan'$/\1/p" | head -n 1)
  [ -n "`$WAN_IDX" ] || return 1
  if ! uci show firewall.@zone[`$WAN_IDX].network 2>/dev/null | grep -qw "wwan_uplink"; then
    uci add_list firewall.@zone[`$WAN_IDX].network='wwan_uplink' || return 1
  fi

  uci commit network || return 1
  uci commit wireless || return 1
  uci commit firewall || return 1
  wifi reload || return 1
  ifup wwan_uplink 2>/dev/null || true
  sleep 6
  /etc/init.d/firewall restart || return 1
}
do_uplink || fail_rollback

OK=0
for TRY in 1 2 3 4 5 6; do
  if ifstatus wwan_uplink 2>/dev/null | grep -q '"up": true'; then
    OK=1
    break
  fi
  sleep 5
done
if [ "`$OK" != "1" ]; then
  echo UPLINK_NOT_UP
  ifstatus wwan_uplink 2>/dev/null || true
  fail_rollback
fi
ifstatus wwan_uplink
echo UPLINK_ENABLED
"@
    $r = Invoke-RouterScript -KeyPath $KeyPath -RouterIp $RouterIp -Script $cmd
    if ($r.ExitCode -ne 0 -or $r.Output -notmatch "UPLINK_ENABLED") {
        Fail "Enable uplink failed: $($r.Output)"
    }
    Write-Host "UPLINK ENABLED" -ForegroundColor Green
}

function Disable-Uplink {
    $cmd = @"
set -e
WAN_IDX=`$(uci show firewall | sed -n "s/^firewall\.@zone\[\([0-9]\+\)\]\.name='wan'$/\1/p" | head -n 1)
if [ -n "`$WAN_IDX" ]; then
  uci del_list firewall.@zone[`$WAN_IDX].network='wwan_uplink' 2>/dev/null || true
fi
uci -q delete wireless.router_uplink
uci -q delete network.wwan_uplink
uci commit wireless
uci commit network
uci commit firewall
/etc/init.d/network restart
sleep 4
/etc/init.d/firewall restart
echo UPLINK_DISABLED
"@
    $r = Invoke-RouterScript -KeyPath $KeyPath -RouterIp $RouterIp -Script $cmd
    if ($r.ExitCode -ne 0 -or $r.Output -notmatch "UPLINK_DISABLED") {
        Fail "Disable uplink failed: $($r.Output)"
    }
    Write-Host "UPLINK DISABLED" -ForegroundColor Yellow
}

function Show-UplinkStatus {
    $cmd = @"
set +e
echo "=== network.wwan_uplink ==="
uci show network.wwan_uplink 2>/dev/null || echo "(missing)"
echo "=== wireless.router_uplink ==="
uci show wireless.router_uplink 2>/dev/null | sed "s/\.key='.*'/.key='REDACTED'/" || echo "(missing)"
echo "=== firewall wan zone networks ==="
WAN_IDX=`$(uci show firewall | sed -n "s/^firewall\.@zone\[\([0-9]\+\)\]\.name='wan'$/\1/p" | head -n 1)
if [ -n "`$WAN_IDX" ]; then
  uci show firewall.@zone[`$WAN_IDX].network 2>/dev/null || true
fi
echo "=== ifstatus wwan_uplink ==="
ifstatus wwan_uplink 2>/dev/null || echo "(down or missing)"
"@
    $r = Invoke-RouterScript -KeyPath $KeyPath -RouterIp $RouterIp -Script $cmd
    if ($r.ExitCode -ne 0) {
        Fail "Status command failed: $($r.Output)"
    }
    Write-Host $r.Output
}

Write-Host "Router Temporary WiFi Uplink Helper"
Write-Host "==================================="
Require-RouterConnection

switch ($Action) {
    "enable" { Enable-Uplink; break }
    "disable" { Disable-Uplink; break }
    "status" { Show-UplinkStatus; break }
    default { Fail "Unknown action: $Action" }
}

exit 0
