[CmdletBinding()]
param([datetime]$At = (Get-Date '09:00'))
$ErrorActionPreference = 'Stop'
$python = (Get-Command python -ErrorAction Stop).Source
$directory = 'K:\Documents\home-automation-update-staging\bambuddy'
New-Item -ItemType Directory -Path $directory -Force | Out-Null
$script = Join-Path $PSScriptRoot 'bambuddy-stage-update.py'
$log = Join-Path $directory 'stage.log'
# Rotate a single bounded log; report failures to Task Scheduler with nonzero status.
$command = "try { `$ErrorActionPreference = 'Stop'; if ((Test-Path -LiteralPath '$log') -and (Get-Item -LiteralPath '$log').Length -gt 1MB) { Move-Item -LiteralPath '$log' -Destination '$log.previous' -Force }; & '$python' '$script' *>> '$log'; exit `$LASTEXITCODE } catch { exit 1 }"
$action = New-ScheduledTaskAction -Execute "$env:SystemRoot\System32\WindowsPowerShell\v1.0\powershell.exe" -Argument "-NoProfile -NonInteractive -ExecutionPolicy Bypass -Command `"$command`""
$trigger = New-ScheduledTaskTrigger -Daily -At $At
$settings = New-ScheduledTaskSettingsSet -StartWhenAvailable -MultipleInstances IgnoreNew -ExecutionTimeLimit (New-TimeSpan -Hours 2)
$user = [System.Security.Principal.WindowsIdentity]::GetCurrent().Name
$principal = New-ScheduledTaskPrincipal -UserId $user -LogonType Interactive -RunLevel Limited
Register-ScheduledTask -TaskName 'Bambuddy Offline Release Staging' -Action $action -Trigger $trigger -Principal $principal -Settings $settings -Force | Out-Null
Write-Host "Staging scheduled daily at $($At.ToString('HH:mm')) while $user is signed in. Log: $log"
