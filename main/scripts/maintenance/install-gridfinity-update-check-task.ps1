[CmdletBinding()]
param(
    [datetime]$At = (Get-Date '09:00'),
    [switch]$AutoDeploy,
    [string]$SshKeyPath
)

$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest

$checkTaskName = 'Gridfinity Layout Tool Update Check'
$taskName = if ($AutoDeploy) { 'Gridfinity Layout Tool Autodeploy' } else { $checkTaskName }
$checkScript = Join-Path $PSScriptRoot 'gridfinity-layout-tool-update.ps1'
$logDirectory = Join-Path $env:ProgramData 'home-automation-project'
$logFile = Join-Path $logDirectory 'gridfinity-layout-tool.update-check.log'

New-Item -ItemType Directory -Path $logDirectory -Force | Out-Null

if ($AutoDeploy) {
    if (-not $SshKeyPath) {
        $SshKeyPath = Join-Path $env:USERPROFILE '.ssh\gridfinity-layout-tool-autodeploy'
    }
    if (-not (Test-Path -LiteralPath $SshKeyPath)) {
        throw "Autodeploy SSH key not found: $SshKeyPath"
    }
    $command = "& '$checkScript' -Mode Install -SshKeyPath '$SshKeyPath' *>> '$logFile'"
}
else {
    $command = "& '$checkScript' -Mode Check *>> '$logFile'"
}
$action = New-ScheduledTaskAction -Execute "$env:SystemRoot\System32\WindowsPowerShell\v1.0\powershell.exe" `
    -Argument "-NoProfile -NonInteractive -ExecutionPolicy Bypass -Command `"$command`""
$trigger = New-ScheduledTaskTrigger -Daily -At $At
$settings = New-ScheduledTaskSettingsSet -StartWhenAvailable -MultipleInstances IgnoreNew
$currentUser = [System.Security.Principal.WindowsIdentity]::GetCurrent().Name
$principal = New-ScheduledTaskPrincipal -UserId $currentUser -LogonType Interactive -RunLevel Limited

Register-ScheduledTask -TaskName $taskName -Action $action -Trigger $trigger -Principal $principal -Settings $settings -Force | Out-Null
if ($AutoDeploy -and (Get-ScheduledTask -TaskName $checkTaskName -ErrorAction SilentlyContinue)) {
    Unregister-ScheduledTask -TaskName $checkTaskName -Confirm:$false
}
Write-Host "Installed '$taskName' for $currentUser to run daily at $($At.ToString('HH:mm')) while that user is signed in."
Write-Host "Latest result: $logDirectory\gridfinity-layout-tool.last-check.json"
