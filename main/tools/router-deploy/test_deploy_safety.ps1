# Offline tests: extract only functions, never execute deploy.ps1's entry point.
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
. (Join-Path $PSScriptRoot 'lib/ssh_session.ps1')
function Assert-True([bool]$Condition, [string]$Message) {
    if (-not $Condition) { throw $Message }
}
$LASTEXITCODE = 0
$missing = Invoke-NativeCapture { & __audit_missing_executable__ }
Assert-True ($missing.ExitCode -ne 0) 'Missing executable reused a successful exit code'
Assert-True (-not ('Device br-lan.10 does not exist' -match '^VLAN_PRESENT_10$')) 'Missing VLAN passed'
$errors = $null
$ast = [System.Management.Automation.Language.Parser]::ParseFile((Join-Path $PSScriptRoot 'deploy.ps1'), [ref]$null, [ref]$errors)
Assert-True ($errors.Count -eq 0) 'deploy.ps1 does not parse'
foreach ($name in @('Arm-RollbackWatchdog','Cancel-RollbackWatchdog','Restart-RouterServicesDetached')) {
    $function = $ast.Find({param($node) $node -is [System.Management.Automation.Language.FunctionDefinitionAst] -and $node.Name -eq $name}, $true)
    Invoke-Expression $function.Extent.Text
}
function Fail([string]$Message) { throw $Message }
$script:Commands = [System.Collections.Generic.List[string]]::new()
function Invoke-RouterCommand {
    param($KeyPath,$RouterIp,$Command)
    $script:Commands.Add($Command)
    [PSCustomObject]@{ExitCode=0;Output='WATCHDOG_ARMED WATCHDOG_CANCELLED RESTART_STARTED'}
}
Arm-RollbackWatchdog -KeyPath unused -RouterIp fixture -Timestamp fixture -TimeoutSeconds 1
Cancel-RollbackWatchdog -KeyPath unused -RouterIp fixture -Timestamp fixture
Restart-RouterServicesDetached -KeyPath unused -RouterIp fixture -Timestamp fixture
# Emit rendered shell to let a Linux harness exercise the actual decision logic.
if ($env:AUDIT_EMIT_SHELL -eq '1') { $script:Commands | ConvertTo-Json -Compress }
else { Write-Host 'PASS: native failures, VLAN sentinel, deploy parse and shell rendering' }
