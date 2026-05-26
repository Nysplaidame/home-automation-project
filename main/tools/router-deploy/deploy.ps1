param(
    [switch]$Force,
    [string]$RouterIp = "192.168.1.1",
    [ValidateRange(60, 3600)]
    [int]$WatchdogSeconds = 360,
    [ValidateSet("first-flight", "full")]
    [string]$Profile = "first-flight"
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

trap {
    Write-Host "[ERROR] $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

$ScriptRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$LibPath = Join-Path $ScriptRoot "lib\ssh_session.ps1"
. $LibPath

$KeysDir = Join-Path $ScriptRoot "keys"
$GeneratedDir = Join-Path $ScriptRoot "generated"
$SnapshotsDir = Join-Path $ScriptRoot "snapshots"
$LogsDir = Join-Path $ScriptRoot "logs"
$KeyPath = Join-Path $KeysDir "router_deploy"
$SummaryPath = Join-Path $GeneratedDir "summary.json"

New-Item -ItemType Directory -Force -Path $SnapshotsDir, $LogsDir | Out-Null

function Fail([string]$Message) {
    throw $Message
}

function Run-PythonStep([string]$Name, [string]$ScriptPath, [string[]]$Arguments = @()) {
    Write-Host "Running $Name..."
    & python $ScriptPath @Arguments
    if ($LASTEXITCODE -ne 0) {
        Fail "$Name failed with exit code $LASTEXITCODE"
    }
}

function Confirm-Deploy {
    if ($Force) { return }
    Write-Host ""
    Write-Host "Type 'DEPLOY ROUTER' to continue (or anything else to abort):"
    $answer = Read-Host
    if ($answer -ne "DEPLOY ROUTER") {
        Fail "User aborted deploy"
    }
}

function Verify-RouterIdentity {
    param([string]$KeyPath, [string]$RouterIp)
    $board = Invoke-RouterCommand -KeyPath $KeyPath -RouterIp $RouterIp -Command "cat /tmp/sysinfo/board_name 2>/dev/null || ubus call system board | grep -i model || true"
    if ($board.ExitCode -ne 0) {
        Fail "Could not query router identity"
    }
    $text = $board.Output
    if ($text -notmatch "mt6000|GL-MT6000|glinet") {
        Write-Host "[WARN] Could not positively match GL-MT6000 in identity output:" -ForegroundColor Yellow
        Write-Host $text
        if (-not $Force) {
            Fail "Identity gate failed. Re-run with -Force only if you have verified target manually."
        }
    }
}

function Write-LocalSnapshot {
    param([string]$KeyPath, [string]$RouterIp, [string]$Timestamp)
    $remoteDir = "/tmp/router-deploy-snapshots/$Timestamp"
    $localDir = Join-Path $SnapshotsDir $Timestamp
    $ok = Copy-FromRouter -KeyPath $KeyPath -RouterIp $RouterIp -RemotePath $remoteDir -LocalPath $SnapshotsDir
    if (-not $ok) {
        Fail "Could not pull snapshot copy to laptop. Aborting before any router changes."
    }
    if (-not (Test-Path $localDir)) {
        Fail "Snapshot pull reported success but local snapshot directory is missing at $localDir"
    }
    $localFiles = @(Get-ChildItem -LiteralPath $localDir -File -Recurse -ErrorAction SilentlyContinue)
    if ($localFiles.Count -eq 0) {
        Fail "Snapshot pull reported success but copied zero files. Aborting before any router changes."
    }
}

function Arm-RollbackWatchdog {
    param([string]$KeyPath, [string]$RouterIp, [string]$Timestamp, [int]$TimeoutSeconds)
    $watchdogPath = "/tmp/router-deploy-watchdog-$Timestamp.sh"
    $cancelPath = "/tmp/router-deploy-watchdog-$Timestamp.cancel"
    $resultPath = "/tmp/router-deploy-watchdog-$Timestamp.result"
    $logPath = "/tmp/router-deploy-watchdog-$Timestamp.log"
    $remoteSnap = "/tmp/router-deploy-snapshots/$Timestamp"
    $cmd = @"
cat > '$watchdogPath' <<'EOF'
#!/bin/sh
set -e
sleep $TimeoutSeconds
if [ -e '$cancelPath' ]; then
  exit 0
fi
if [ -d '$remoteSnap' ]; then
    cp '$remoteSnap'/* /etc/config/
    /etc/init.d/network restart
    sleep 5
    wifi reload || true
    /etc/init.d/dnsmasq restart
    /etc/init.d/firewall restart
    /etc/init.d/sysntpd restart
    echo WATCHDOG_ROLLBACK_OK > '$resultPath'
else
  echo WATCHDOG_SNAPSHOT_MISSING > '$resultPath'
fi
EOF
chmod +x '$watchdogPath'
rm -f '$cancelPath' '$resultPath' '$logPath'
if command -v nohup >/dev/null 2>&1; then
  nohup sh '$watchdogPath' > '$logPath' 2>&1 &
else
  sh '$watchdogPath' > '$logPath' 2>&1 &
fi
echo WATCHDOG_ARMED
"@
    $r = Invoke-RouterCommand -KeyPath $KeyPath -RouterIp $RouterIp -Command $cmd
    if ($r.ExitCode -ne 0 -or $r.Output -notmatch "WATCHDOG_ARMED") {
        Fail "Could not arm rollback watchdog: $($r.Output)"
    }
}

function Cancel-RollbackWatchdog {
    param([string]$KeyPath, [string]$RouterIp, [string]$Timestamp)
    $cancelPath = "/tmp/router-deploy-watchdog-$Timestamp.cancel"
    $cmd = "touch '$cancelPath' && echo WATCHDOG_CANCELLED"
    $r = Invoke-RouterCommand -KeyPath $KeyPath -RouterIp $RouterIp -Command $cmd
    if ($r.ExitCode -ne 0 -or $r.Output -notmatch "WATCHDOG_CANCELLED") {
        Fail "Deployment health checks passed, but rollback watchdog could not be cancelled: $($r.Output)"
    }
}

function Apply-ConfigFile {
    param(
        [string]$KeyPath,
        [string]$RouterIp,
        [string]$LocalFile,
        [string]$ConfigName
    )
    if (-not (Test-Path $LocalFile)) {
        Fail "Generated file missing: $LocalFile"
    }
    $remoteTempPath = "/tmp/$ConfigName.new"
    $copied = Copy-ToRouter -KeyPath $KeyPath -RouterIp $RouterIp -LocalPath $LocalFile -RemotePath $remoteTempPath
    if (-not $copied) { Fail "Failed to copy $LocalFile to router" }
    $cmd = @"
set -e
cp '$remoteTempPath' '/etc/config/$ConfigName'
chmod 600 '/etc/config/$ConfigName'
"@
    $r = Invoke-RouterCommand -KeyPath $KeyPath -RouterIp $RouterIp -Command $cmd
    if ($r.ExitCode -ne 0) {
        Fail "Failed to apply /etc/config/$ConfigName from $LocalFile : $($r.Output)"
    }
}

function Soft-Rollback {
    param([string]$KeyPath, [string]$RouterIp, [string]$Timestamp)
    Write-Host "[WARN] Attempting soft rollback from snapshot $Timestamp..." -ForegroundColor Yellow
    $cmd = @"
set -e
if [ -d /tmp/router-deploy-snapshots/$Timestamp ]; then
  cp /tmp/router-deploy-snapshots/$Timestamp/* /etc/config/
  touch /tmp/router-deploy-watchdog-$Timestamp.cancel 2>/dev/null || true
  echo ROLLBACK_CONFIG_RESTORED
else
  echo SNAPSHOT_MISSING
  exit 1
fi
"@
    $r = Invoke-RouterCommand -KeyPath $KeyPath -RouterIp $RouterIp -Command $cmd
    if ($r.ExitCode -eq 0 -and $r.Output -match "ROLLBACK_CONFIG_RESTORED") {
        Restart-RouterServicesDetached -KeyPath $KeyPath -RouterIp $RouterIp -Timestamp $Timestamp -Phase "rollback"
        Start-Sleep -Seconds 12
        if (Wait-ForRouter -KeyPath $KeyPath -RouterIp $RouterIp -TimeoutSeconds 60 -PollSeconds 5) {
            Write-Host "DEPLOYMENT FAILED, ROLLED BACK" -ForegroundColor Yellow
        }
        else {
            Write-Host "DEPLOYMENT FAILED, rollback configs restored but router did not come back within timeout." -ForegroundColor Red
        }
        exit 1
    }
    Fail "Rollback failed or snapshot missing. Manual recovery via lan5 is required."
}

function Restart-RouterServicesDetached {
    param(
        [string]$KeyPath,
        [string]$RouterIp,
        [string]$Timestamp,
        [string]$Phase = "deploy"
    )
    $restartPath = "/tmp/router-deploy-$Phase-restart-$Timestamp.sh"
    $resultPath = "/tmp/router-deploy-$Phase-restart-$Timestamp.result"
    $logPath = "/tmp/router-deploy-$Phase-restart-$Timestamp.log"
    $cmd = @"
cat > '$restartPath' <<'EOF'
#!/bin/sh
set -e
sleep 2
/etc/init.d/network restart
sleep 5
wifi reload || true
  /etc/init.d/dnsmasq restart
  /etc/init.d/firewall restart
  /etc/init.d/sysntpd restart
  echo RESTART_OK > '$resultPath'
EOF
chmod +x '$restartPath'
rm -f '$resultPath' '$logPath'
if command -v nohup >/dev/null 2>&1; then
  nohup sh '$restartPath' > '$logPath' 2>&1 &
else
  sh '$restartPath' > '$logPath' 2>&1 &
fi
echo RESTART_STARTED
"@
    $r = Invoke-RouterCommand -KeyPath $KeyPath -RouterIp $RouterIp -Command $cmd
    if ($r.ExitCode -ne 0 -or $r.Output -notmatch "RESTART_STARTED") {
        Fail "Could not start detached service restart: $($r.Output)"
    }
}

function Wait-ForRouterCommandMatch {
    param(
        [string]$KeyPath,
        [string]$RouterIp,
        [string]$Command,
        [string]$Pattern,
        [int]$TimeoutSeconds = 60,
        [int]$PollSeconds = 3
    )

    $deadline = (Get-Date).AddSeconds($TimeoutSeconds)
    $last = [PSCustomObject]@{
        ExitCode = 1
        Output   = ""
    }

    do {
        $last = Invoke-RouterCommand -KeyPath $KeyPath -RouterIp $RouterIp -Command $Command
        if ($last.ExitCode -eq 0 -and $last.Output -match $Pattern) {
            return [PSCustomObject]@{
                Matched  = $true
                ExitCode = $last.ExitCode
                Output   = $last.Output
            }
        }
        Start-Sleep -Seconds $PollSeconds
    } while ((Get-Date) -lt $deadline)

    return [PSCustomObject]@{
        Matched  = $false
        ExitCode = $last.ExitCode
        Output   = $last.Output
    }
}

Write-Host "Router Deploy - Hardened Workflow"
Write-Host "================================="
Write-Host "Profile: $Profile"

if (-not (Test-Path $KeyPath)) {
    Fail "Key not found at $KeyPath. Generate it with: ssh-keygen -t ed25519 -f `"$KeyPath`" -N `"`""
}

if (-not (Test-RouterAlive -KeyPath $KeyPath -RouterIp $RouterIp)) {
    Fail "Key-based SSH check failed for root@$RouterIp"
}

Verify-RouterIdentity -KeyPath $KeyPath -RouterIp $RouterIp

Run-PythonStep -Name "lint.py" -ScriptPath (Join-Path $ScriptRoot "lint.py")
$compileArgs = @("--profile", $Profile)
Run-PythonStep -Name "compile.py" -ScriptPath (Join-Path $ScriptRoot "compile.py") -Arguments $compileArgs

if (-not (Test-Path $SummaryPath)) {
    Fail "Missing compile summary: $SummaryPath"
}

$summaryJson = Get-Content -Raw -LiteralPath $SummaryPath | ConvertFrom-Json
Write-Host ""
Write-Host "Compile summary:"
$summaryJson | ConvertTo-Json -Depth 8

if (-not $summaryJson.invariants.lan5_vlan1_untagged -or
    -not $summaryJson.invariants.lan_on_br_lan_1 -or
    -not $summaryJson.invariants.lan_gateway_expected_192_168_1_1) {
    Fail "Compile invariant failure detected in summary.json"
}
$strippedTempRules = $null
if ($summaryJson.PSObject.Properties.Name -contains "stripped_temp_rules") {
    $strippedTempRules = [int]$summaryJson.stripped_temp_rules
}
elseif (
    ($summaryJson.PSObject.Properties.Name -contains "first_flight_adjustments") -and
    ($summaryJson.first_flight_adjustments -ne $null) -and
    ($summaryJson.first_flight_adjustments.PSObject.Properties.Name -contains "stripped_temp_firewall_rules")
) {
    # Backward compatibility for older summary schema.
    $strippedTempRules = [int]$summaryJson.first_flight_adjustments.stripped_temp_firewall_rules
}
else {
    Fail "Compile summary missing stripped TEMP firewall rule count."
}

if ($Profile -eq "first-flight" -and ($strippedTempRules -lt 2)) {
    Fail "First-flight compile did not strip temporary WAN exception rules from firewall artifact."
}

Confirm-Deploy

$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$remoteSnap = "/tmp/router-deploy-snapshots/$timestamp"

Write-Host "Creating router snapshot..."
$snapCmd = @"
set -e
mkdir -p '$remoteSnap'
for f in /etc/config/*; do
  [ -f "`$f" ] && cp -p "`$f" '$remoteSnap/'
done
if ! find '$remoteSnap' -type f | grep -q .; then
  echo SNAPSHOT_EMPTY
  exit 1
fi
"@
$snapRes = Invoke-RouterCommand -KeyPath $KeyPath -RouterIp $RouterIp -Command $snapCmd
if ($snapRes.ExitCode -ne 0) {
    Fail "Snapshot creation failed: $($snapRes.Output)"
}
Write-LocalSnapshot -KeyPath $KeyPath -RouterIp $RouterIp -Timestamp $timestamp
Write-Host "Arming rollback watchdog ($WatchdogSeconds seconds)..."
Arm-RollbackWatchdog -KeyPath $KeyPath -RouterIp $RouterIp -Timestamp $timestamp -TimeoutSeconds $WatchdogSeconds

try {
    Write-Host "Applying generated config files..."
    Apply-ConfigFile -KeyPath $KeyPath -RouterIp $RouterIp -LocalFile (Join-Path $GeneratedDir "network.uci") -ConfigName "network"
    Apply-ConfigFile -KeyPath $KeyPath -RouterIp $RouterIp -LocalFile (Join-Path $GeneratedDir "dhcp.uci") -ConfigName "dhcp"
    Apply-ConfigFile -KeyPath $KeyPath -RouterIp $RouterIp -LocalFile (Join-Path $GeneratedDir "wireless.uci") -ConfigName "wireless"

    $systemCmd = @'
set -e
uci -q get system.@system[0] >/dev/null
uci set system.@system[0].hostname='home-router'
uci set system.@system[0].timezone='GMT0BST,M3.5.0/1,M10.5.0'
uci set system.@system[0].zonename='Europe/London'
uci set system.ntp='timeserver'
uci set system.ntp.enabled='1'
uci set system.ntp.enable_server='1'
uci -q delete system.ntp.server || true
uci add_list system.ntp.server='0.openwrt.pool.ntp.org'
uci add_list system.ntp.server='1.openwrt.pool.ntp.org'
uci add_list system.ntp.server='2.openwrt.pool.ntp.org'
uci add_list system.ntp.server='3.openwrt.pool.ntp.org'
uci commit system
echo SYSTEM_NTP_CONFIGURED
'@
    $systemExec = Invoke-RouterCommand -KeyPath $KeyPath -RouterIp $RouterIp -Command $systemCmd
    if ($systemExec.ExitCode -ne 0 -or $systemExec.Output -notmatch "SYSTEM_NTP_CONFIGURED") {
        Fail "System/NTP configuration failed: $($systemExec.Output)"
    }

    $fwLocal = Join-Path $GeneratedDir "firewall.sh"
    if (-not (Copy-ToRouter -KeyPath $KeyPath -RouterIp $RouterIp -LocalPath $fwLocal -RemotePath "/tmp/firewall.sh")) {
        Fail "Failed to copy firewall.sh"
    }
    $fwExec = Invoke-RouterCommand -KeyPath $KeyPath -RouterIp $RouterIp -Command "sh /tmp/firewall.sh"
    if ($fwExec.ExitCode -ne 0) {
        Fail "Firewall script execution failed: $($fwExec.Output)"
    }
    $validateCmd = @"
set -e
uci -q show network >/dev/null
uci -q show dhcp >/dev/null
uci -q show wireless >/dev/null
uci -q show firewall >/dev/null
uci -q show system >/dev/null
echo CONFIG_VALID
"@
    $validate = Invoke-RouterCommand -KeyPath $KeyPath -RouterIp $RouterIp -Command $validateCmd
    if ($validate.ExitCode -ne 0 -or $validate.Output -notmatch "CONFIG_VALID") {
        Fail "Config parse step failed: $($validate.Output)"
    }
    Restart-RouterServicesDetached -KeyPath $KeyPath -RouterIp $RouterIp -Timestamp $timestamp -Phase "deploy"
}
catch {
    Write-Host "[ERROR] Apply phase failed: $($_.Exception.Message)" -ForegroundColor Red
    Soft-Rollback -KeyPath $KeyPath -RouterIp $RouterIp -Timestamp $timestamp
}

Write-Host "Waiting for router stabilization..."
Start-Sleep -Seconds 12
if (-not (Wait-ForRouter -KeyPath $KeyPath -RouterIp $RouterIp -TimeoutSeconds 60 -PollSeconds 5)) {
    Write-Host "[ERROR] Router did not become reachable after detached restart." -ForegroundColor Red
    Soft-Rollback -KeyPath $KeyPath -RouterIp $RouterIp -Timestamp $timestamp
}

$restartResultCmd = "cat /tmp/router-deploy-deploy-restart-$timestamp.result 2>/dev/null || true; echo ---LOG---; cat /tmp/router-deploy-deploy-restart-$timestamp.log 2>/dev/null || true"
$restartResult = Wait-ForRouterCommandMatch -KeyPath $KeyPath -RouterIp $RouterIp -Command $restartResultCmd -Pattern "RESTART_OK" -TimeoutSeconds 75 -PollSeconds 3
if (-not $restartResult.Matched) {
    Write-Host "[ERROR] Detached deploy restart did not report RESTART_OK:" -ForegroundColor Red
    Write-Host $restartResult.Output
    Soft-Rollback -KeyPath $KeyPath -RouterIp $RouterIp -Timestamp $timestamp
}

Write-Host "Running staged health checks..."
$healthCmd = @'
lan_ok=0
vlan_ok=0
ports_ok=0
dnsmasq_ok=0
ntp_cfg_ok=0
ntp_proc_ok=0

if ifstatus lan >/dev/null 2>&1; then
  echo IFSTATUS_LAN_OK
  lan_ok=1
else
  echo IFSTATUS_LAN_FAIL
fi

vlan_value=$(uci -q get 'network.@bridge-vlan[0].vlan' 2>/dev/null || true)
if [ "$vlan_value" = "1" ]; then
  echo VLAN1_UCI_OK
  vlan_ok=1
else
  echo VLAN1_UCI_FAIL
  echo "network.@bridge-vlan[0].vlan=$vlan_value"
  uci show network | grep "\.vlan=" || true
fi

ports_value=$(uci -q get 'network.@bridge-vlan[0].ports' 2>/dev/null || true)
if echo "$ports_value" | grep -F "lan5:u*" >/dev/null; then
  echo LAN5_PORT_UCI_OK
  ports_ok=1
else
  echo LAN5_PORT_UCI_FAIL
  echo "network.@bridge-vlan[0].ports=$ports_value"
  uci show network | grep "\.ports=" || true
fi

if /etc/init.d/dnsmasq status >/dev/null 2>&1 || pidof dnsmasq >/dev/null; then
  echo DNSMASQ_OK
  dnsmasq_ok=1
else
  echo DNSMASQ_FAIL
  /etc/init.d/dnsmasq status 2>&1 || true
fi

ntp_server=$(uci -q get system.ntp.enable_server 2>/dev/null || true)
ntp_enabled=$(uci -q get system.ntp.enabled 2>/dev/null || true)
if [ "$ntp_server" = "1" ] && [ "$ntp_enabled" = "1" ]; then
  echo NTP_CONFIG_OK
  ntp_cfg_ok=1
else
  echo NTP_CONFIG_FAIL
  echo "system.ntp.enabled=$ntp_enabled system.ntp.enable_server=$ntp_server"
fi

if /etc/init.d/sysntpd status >/dev/null 2>&1 || pidof sysntpd >/dev/null; then
  echo SYSNTPD_OK
  ntp_proc_ok=1
else
  echo SYSNTPD_FAIL
  /etc/init.d/sysntpd status 2>&1 || true
fi

/etc/init.d/firewall status >/dev/null 2>&1 || true

if [ "$lan_ok$vlan_ok$ports_ok$dnsmasq_ok$ntp_cfg_ok$ntp_proc_ok" = "111111" ]; then
  echo HEALTH_OK
else
  exit 1
fi
'@
$health = Wait-ForRouterCommandMatch -KeyPath $KeyPath -RouterIp $RouterIp -Command $healthCmd -Pattern "HEALTH_OK" -TimeoutSeconds 150 -PollSeconds 5
if (-not $health.Matched) {
    Write-Host "[ERROR] Health checks failed:" -ForegroundColor Red
    Write-Host $health.Output
    Soft-Rollback -KeyPath $KeyPath -RouterIp $RouterIp -Timestamp $timestamp
}

Cancel-RollbackWatchdog -KeyPath $KeyPath -RouterIp $RouterIp -Timestamp $timestamp
Write-Host "DEPLOYMENT SUCCEEDED" -ForegroundColor Green
exit 0
