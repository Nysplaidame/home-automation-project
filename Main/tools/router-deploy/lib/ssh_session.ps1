Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Invoke-NativeCapture {
    param([scriptblock]$Command)

    $oldErrorActionPreference = $ErrorActionPreference
    $nativePreference = Get-Variable -Name PSNativeCommandUseErrorActionPreference -ErrorAction SilentlyContinue
    $oldNativePreference = if ($nativePreference) { $nativePreference.Value } else { $null }

    try {
        $ErrorActionPreference = "Continue"
        if ($nativePreference) {
            $PSNativeCommandUseErrorActionPreference = $false
        }

        $raw = & $Command 2>&1
        $exitCode = $LASTEXITCODE
    }
    catch {
        $raw = @($_.Exception.Message)
        $exitCode = if ($LASTEXITCODE -ne $null) { $LASTEXITCODE } else { 1 }
    }
    finally {
        $ErrorActionPreference = $oldErrorActionPreference
        if ($nativePreference) {
            $PSNativeCommandUseErrorActionPreference = $oldNativePreference
        }
    }

    [PSCustomObject]@{
        ExitCode = $exitCode
        Output   = ($raw -join "`n")
    }
}

function Get-RouterSshTarget {
    param(
        [string]$RouterIp = "192.168.1.1",
        [string]$User = "root"
    )
    return "$User@$RouterIp"
}

function Test-RouterAlive {
    param(
        [string]$KeyPath,
        [string]$RouterIp = "192.168.1.1",
        [string]$User = "root",
        [int]$ConnectTimeoutSeconds = 7
    )
    $target = Get-RouterSshTarget -RouterIp $RouterIp -User $User
    $sshArgs = @(
        "-i", $KeyPath,
        "-o", "BatchMode=yes",
        "-o", "StrictHostKeyChecking=accept-new",
        "-o", "ConnectTimeout=$ConnectTimeoutSeconds",
        $target,
        "echo OK"
    )
    $r = Invoke-NativeCapture { & ssh @sshArgs }
    return ($r.ExitCode -eq 0 -and $r.Output -match "OK")
}

function Wait-ForRouter {
    param(
        [string]$KeyPath,
        [string]$RouterIp = "192.168.1.1",
        [string]$User = "root",
        [int]$TimeoutSeconds = 60,
        [int]$PollSeconds = 5
    )
    $deadline = (Get-Date).AddSeconds($TimeoutSeconds)
    do {
        if (Test-RouterAlive -KeyPath $KeyPath -RouterIp $RouterIp -User $User) {
            return $true
        }
        Start-Sleep -Seconds $PollSeconds
    } while ((Get-Date) -lt $deadline)
    return $false
}

function Invoke-RouterCommand {
    param(
        [Parameter(Mandatory = $true)][string]$KeyPath,
        [Parameter(Mandatory = $true)][string]$Command,
        [string]$RouterIp = "192.168.1.1",
        [string]$User = "root",
        [int]$ConnectTimeoutSeconds = 10
    )

    $target = Get-RouterSshTarget -RouterIp $RouterIp -User $User
    $sshArgs = @(
        "-i", $KeyPath,
        "-o", "BatchMode=yes",
        "-o", "StrictHostKeyChecking=accept-new",
        "-o", "ConnectTimeout=$ConnectTimeoutSeconds",
        $target,
        $Command
    )
    Invoke-NativeCapture { & ssh @sshArgs }
}

function Invoke-RouterScript {
    param(
        [Parameter(Mandatory = $true)][string]$KeyPath,
        [Parameter(Mandatory = $true)][string]$Script,
        [string]$RouterIp = "192.168.1.1",
        [string]$User = "root",
        [int]$ConnectTimeoutSeconds = 10
    )

    $scriptBody = $Script.Replace("`r`n", "`n").Replace("`r", "`n")
    if (-not $scriptBody.EndsWith("`n")) {
        $scriptBody = "$scriptBody`n"
    }

    $name = "router-deploy-check-$([guid]::NewGuid().ToString('N')).sh"
    $localPath = Join-Path ([IO.Path]::GetTempPath()) $name
    $remotePath = "/tmp/$name"

    try {
        [IO.File]::WriteAllText($localPath, $scriptBody, [Text.UTF8Encoding]::new($false))
        if (-not (Copy-ToRouter -KeyPath $KeyPath -LocalPath $localPath -RemotePath $remotePath -RouterIp $RouterIp -User $User)) {
            return [PSCustomObject]@{
                ExitCode = 1
                Output   = "Failed to copy validation script to $remotePath"
            }
        }

        $remoteCommand = "sh $remotePath; rc=`$?; rm -f $remotePath; exit `$rc"
        Invoke-RouterCommand -KeyPath $KeyPath -RouterIp $RouterIp -User $User -ConnectTimeoutSeconds $ConnectTimeoutSeconds -Command $remoteCommand
    }
    finally {
        Remove-Item -LiteralPath $localPath -Force -ErrorAction SilentlyContinue
    }
}

function Copy-ToRouter {
    param(
        [Parameter(Mandatory = $true)][string]$KeyPath,
        [Parameter(Mandatory = $true)][string]$LocalPath,
        [Parameter(Mandatory = $true)][string]$RemotePath,
        [string]$RouterIp = "192.168.1.1",
        [string]$User = "root"
    )
    $target = Get-RouterSshTarget -RouterIp $RouterIp -User $User
    $sshArgs = @(
        "-O",
        "-i", $KeyPath,
        "-o", "BatchMode=yes",
        "-o", "StrictHostKeyChecking=accept-new",
        $LocalPath,
        "${target}:${RemotePath}"
    )
    $r = Invoke-NativeCapture { & scp @sshArgs }
    return ($r.ExitCode -eq 0)
}

function Copy-FromRouter {
    param(
        [Parameter(Mandatory = $true)][string]$KeyPath,
        [Parameter(Mandatory = $true)][string]$RemotePath,
        [Parameter(Mandatory = $true)][string]$LocalPath,
        [string]$RouterIp = "192.168.1.1",
        [string]$User = "root"
    )
    $target = Get-RouterSshTarget -RouterIp $RouterIp -User $User
    $sshArgs = @(
        "-O",
        "-i", $KeyPath,
        "-o", "BatchMode=yes",
        "-o", "StrictHostKeyChecking=accept-new",
        "-r",
        "${target}:${RemotePath}",
        $LocalPath
    )
    $r = Invoke-NativeCapture { & scp @sshArgs }
    return ($r.ExitCode -eq 0)
}
