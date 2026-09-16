[CmdletBinding()]
param(
    [ValidateSet('Check', 'Install', 'Rollback')]
    [string]$Mode = 'Check',
    [string]$Version,
    [string]$DockerHost = '192.168.20.102',
    [string]$SshKeyPath
)

$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest

$repo = 'https://github.com/andymai/gridfinity-layout-tool.git'
$tagPrefix = 'gridfinity-layout-tool-v'
$stackPath = '/opt/stacks/gridfinity-layout-tool'
$sshTarget = "root@$DockerHost"
$stateDirectory = Join-Path $env:ProgramData 'home-automation-project'
$stateFile = Join-Path $stateDirectory 'gridfinity-layout-tool.version'
$lastCheckFile = Join-Path $stateDirectory 'gridfinity-layout-tool.last-check.json'
$initialInstalledTag = 'gridfinity-layout-tool-v4.249.0'

function Invoke-External {
    param([string]$FilePath, [string[]]$Arguments)

    $output = & $FilePath @Arguments 2>&1
    if ($LASTEXITCODE -ne 0) {
        throw "$FilePath failed with exit code $LASTEXITCODE.`n$output"
    }
    return $output
}

function Get-ReleaseTags {
    $lines = Invoke-External git @('ls-remote', '--tags', '--refs', $repo, "$tagPrefix*")
    $tags = foreach ($line in $lines) {
        if ($line -match "refs/tags/($([regex]::Escape($tagPrefix))(?<version>\d+(?:\.\d+)+))$") {
            [pscustomobject]@{
                Tag = $Matches[1]
                Version = [version]$Matches['version']
            }
        }
    }
    if (-not $tags) {
        throw "No release tags matching $tagPrefix* were found."
    }
    return $tags | Sort-Object Version -Descending
}

function Get-InstalledTag {
    # The scheduled check is deliberately local: docker-host has no routine WAN
    # access and this workstation may not have a non-interactive SSH credential.
    # The first-run value is the release deployed when this workflow was added.
    $tag = if (Test-Path -LiteralPath $stateFile) {
        (Get-Content -LiteralPath $stateFile -Raw).Trim()
    }
    else {
        Set-InstalledTag $initialInstalledTag
        $initialInstalledTag
    }
    if ($tag -notmatch "^$([regex]::Escape($tagPrefix))\d+(?:\.\d+)+$") {
        throw "The local Gridfinity version marker is missing or invalid: '$tag'."
    }
    return $tag
}

function Set-InstalledTag {
    param([string]$Tag)
    New-Item -ItemType Directory -Path $stateDirectory -Force | Out-Null
    Set-Content -LiteralPath $stateFile -Value $Tag -NoNewline
}

function Write-CheckRecord {
    param([pscustomobject]$Record)
    New-Item -ItemType Directory -Path $stateDirectory -Force | Out-Null
    $Record | ConvertTo-Json | Set-Content -LiteralPath $lastCheckFile
}

function Get-SshOptions {
    $options = @('-o', 'ConnectTimeout=10')
    if ($SshKeyPath) {
        if (-not (Test-Path -LiteralPath $SshKeyPath)) {
            throw "SSH key file not found: $SshKeyPath"
        }
        $options += @('-i', $SshKeyPath)
    }
    return $options
}

function Assert-ReleaseTag {
    param([string]$Tag)
    if ($Tag -notmatch "^$([regex]::Escape($tagPrefix))\d+(?:\.\d+)+$") {
        throw "Version must be a release tag such as ${tagPrefix}4.249.0."
    }
}

function Invoke-RemoteDeploy {
    param([string]$Tag, [string]$LocalArchive)

    $remoteArchive = "$stackPath/incoming/$Tag.tgz"
    Invoke-External ssh @((Get-SshOptions) + $sshTarget + "mkdir -p '$stackPath/incoming'") | Out-Host
    Invoke-External scp @((Get-SshOptions) + $LocalArchive + "${sshTarget}:$remoteArchive") | Out-Host

    $deploy = @'
set -euo pipefail
stack="$1"
tag="$2"
archive="$stack/incoming/$tag.tgz"
next="$stack/dist.next"
old="$stack/dist.previous"

rm -rf "$next"
mkdir -p "$next"
tar -xzf "$archive" -C "$next"
test -f "$next/dist/index.html"

rm -rf "$old"
rm -f "$stack/.env.previous"
if [ -d "$stack/dist" ]; then
    mv "$stack/dist" "$old"
fi
if [ -f "$stack/.env" ]; then
    cp "$stack/.env" "$stack/.env.previous"
fi
mv "$next/dist" "$stack/dist"
rmdir "$next"
printf 'GRIDFINITY_VERSION=%s\n' "$tag" > "$stack/.env"

rollback() {
    rm -rf "$stack/dist"
    if [ -d "$old" ]; then mv "$old" "$stack/dist"; fi
    if [ -f "$stack/.env.previous" ]; then mv "$stack/.env.previous" "$stack/.env"; fi
    (cd "$stack" && docker compose up -d --force-recreate) || true
}

if ! (cd "$stack" && docker compose up -d --force-recreate); then
    rollback
    echo "Deployment of $tag failed; restored the prior release." >&2
    exit 1
fi

# Nginx briefly resets its listener while the replacement container starts.
# A retryable polling loop avoids treating that normal handover as a failed
# static release, while still rolling back if the health endpoint never opens.
healthy=0
for attempt in $(seq 1 15); do
    if curl -fsS --connect-timeout 2 http://127.0.0.1:8093/healthz >/dev/null; then
        healthy=1
        break
    fi
    sleep 2
done
if [ "$healthy" -ne 1 ]; then
    rollback
    echo "Deployment of $tag failed; restored the prior release." >&2
    exit 1
fi
rm -f "$archive"
echo "Deployed $tag"
'@
    $deployEncoded = [Convert]::ToBase64String([Text.Encoding]::UTF8.GetBytes($deploy))
    & ssh @(Get-SshOptions) $sshTarget "echo $deployEncoded | base64 -d | bash -s -- '$stackPath' '$Tag'"
    if ($LASTEXITCODE -ne 0) {
        throw "Remote deployment failed with exit code $LASTEXITCODE. The previous static release was restored if a health check failed."
    }
}

switch ($Mode) {
    'Check' {
        $installed = Get-InstalledTag
        $latest = (Get-ReleaseTags | Select-Object -First 1).Tag
        $record = [pscustomobject]@{
            CheckedAtUtc = (Get-Date).ToUniversalTime().ToString('o')
            Installed = $installed
            Latest = $latest
            UpdateAvailable = ($installed -ne $latest)
            InstallCommand = if ($installed -ne $latest) { ".\\main\\scripts\\maintenance\\gridfinity-layout-tool-update.ps1 -Mode Install -Version $latest" } else { $null }
        }
        Write-CheckRecord $record
        $record | ConvertTo-Json -Compress
    }
    'Install' {
        $tag = if ($Version) { $Version } else { (Get-ReleaseTags | Select-Object -First 1).Tag }
        Assert-ReleaseTag $tag
        $installed = Get-InstalledTag
        if ($tag -eq $installed) {
            Write-CheckRecord ([pscustomobject]@{
                CheckedAtUtc = (Get-Date).ToUniversalTime().ToString('o')
                Installed = $installed
                Latest = $tag
                UpdateAvailable = $false
                InstallCommand = $null
            })
            Write-Host "$tag is already deployed; nothing to install."
            break
        }

        $tempArchive = Join-Path $env:TEMP "gridfinity-layout-tool-$tag.tgz"
        Remove-Item -LiteralPath $tempArchive -Force -ErrorAction SilentlyContinue
        try {
            $drive = [IO.Path]::GetPathRoot($tempArchive).TrimEnd('\').TrimEnd(':').ToLowerInvariant()
            $relativePath = $tempArchive.Substring(3).Replace('\', '/')
            $linuxArchive = "/mnt/$drive/$relativePath"
            $build = @'
set -euo pipefail
tag="$1"
archive="$2"
node_version="24.18.0"
node_root="$HOME/.cache/gridfinity-layout-tool/node-v${node_version}-linux-x64"
if [ ! -x "$node_root/bin/node" ]; then
    mkdir -p "$(dirname "$node_root")"
    curl -fsSL "https://nodejs.org/dist/v${node_version}/node-v${node_version}-linux-x64.tar.xz" -o "$node_root.tar.xz"
    tar -xJf "$node_root.tar.xz" -C "$(dirname "$node_root")"
    rm -f "$node_root.tar.xz"
fi
export PATH="$node_root/bin:$PATH"
test "$(node --version)" = "v${node_version}"
workdir="$(mktemp -d)"
trap 'rm -rf "$workdir"' EXIT
git clone --depth 1 --branch "$tag" https://github.com/andymai/gridfinity-layout-tool.git "$workdir/source"
cd "$workdir/source"
corepack enable
corepack prepare pnpm@11.2.2 --activate
pnpm install --frozen-lockfile
pnpm run build
tar -C "$workdir/source" -czf "$archive" dist
'@
            $buildEncoded = [Convert]::ToBase64String([Text.Encoding]::UTF8.GetBytes($build))
            $buildCommand = "echo $buildEncoded | base64 -d | bash -s -- '$tag' '$linuxArchive'"
            & wsl.exe -- bash -lc $buildCommand
            if ($LASTEXITCODE -ne 0 -or -not (Test-Path -LiteralPath $tempArchive)) {
                throw 'The external WSL/Linux build did not produce a deployable archive.'
            }
            Invoke-RemoteDeploy -Tag $tag -LocalArchive $tempArchive
            Set-InstalledTag $tag
            Write-CheckRecord ([pscustomobject]@{
                CheckedAtUtc = (Get-Date).ToUniversalTime().ToString('o')
                Installed = $tag
                Latest = $tag
                UpdateAvailable = $false
                InstallCommand = $null
            })
            Write-Host "Installed $tag."
        }
        finally {
            Remove-Item -LiteralPath $tempArchive -Force -ErrorAction SilentlyContinue
        }
    }
    'Rollback' {
        $rollback = @'
set -euo pipefail
stack="$1"
test -d "$stack/dist.previous"
test -f "$stack/.env.previous"
rm -rf "$stack/dist.rollback"
mv "$stack/dist" "$stack/dist.rollback"
mv "$stack/dist.previous" "$stack/dist"
mv "$stack/.env" "$stack/.env.rollback"
mv "$stack/.env.previous" "$stack/.env"
if ! (cd "$stack" && docker compose up -d --force-recreate) || ! curl -fsS --retry 8 --retry-delay 2 http://127.0.0.1:8093/healthz >/dev/null; then
    echo 'Rollback health check failed; inspect dist.rollback and .env.rollback.' >&2
    exit 1
fi
echo "Rolled back to $(sed -n 's/^GRIDFINITY_VERSION=//p' "$stack/.env")"
'@
        $rollbackEncoded = [Convert]::ToBase64String([Text.Encoding]::UTF8.GetBytes($rollback))
        $result = & ssh @(Get-SshOptions) $sshTarget "echo $rollbackEncoded | base64 -d | bash -s -- '$stackPath'"
        if ($LASTEXITCODE -ne 0) {
            throw "Rollback failed with exit code $LASTEXITCODE."
        }
        $tag = ($result | Select-Object -Last 1) -replace '^Rolled back to\s+', ''
        Assert-ReleaseTag $tag
        Set-InstalledTag $tag
        $result | Out-Host
    }
}
