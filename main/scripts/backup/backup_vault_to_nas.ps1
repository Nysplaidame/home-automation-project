[CmdletBinding()]
param(
    [string]$SourcePath = (Resolve-Path (Join-Path $PSScriptRoot "..\..\..")),
    [string]$DestinationPath = "\\192.168.40.50\NAS\configs\home-automation-project",
    [switch]$Execute,
    [string]$LogPath = (Join-Path $env:LOCALAPPDATA "HomeAutomationProject\logs\vault-backup.log")
)

$ErrorActionPreference = "Stop"

$source = [System.IO.Path]::GetFullPath($SourcePath).TrimEnd("\")
$approvedDestinationRoot = "\\192.168.40.50\NAS\configs"
$destination = $DestinationPath.TrimEnd("\")

if (-not (Test-Path -LiteralPath $source -PathType Container)) {
    throw "Vault source does not exist: $source"
}

if (-not ($destination -ieq $approvedDestinationRoot -or
        $destination.StartsWith("$approvedDestinationRoot\", [System.StringComparison]::OrdinalIgnoreCase))) {
    throw "Destination must stay under $approvedDestinationRoot"
}

if (-not (Test-Path -LiteralPath $approvedDestinationRoot -PathType Container)) {
    throw "NAS backup root is unavailable: $approvedDestinationRoot"
}

$logDirectory = Split-Path -Parent $LogPath
if (-not (Test-Path -LiteralPath $logDirectory -PathType Container)) {
    New-Item -ItemType Directory -Path $logDirectory -Force | Out-Null
}

$arguments = @(
    $source,
    $destination,
    "/E",
    "/COPY:DAT",
    "/DCOPY:DAT",
    "/XJ",
    "/FFT",
    "/Z",
    "/R:2",
    "/W:5",
    "/NP",
    "/TEE",
    "/LOG+:$LogPath"
)

if (-not $Execute) {
    $arguments += "/L"
    Write-Host "DRY RUN: no NAS files will be created, changed, or removed."
}

Write-Host "Source:      $source"
Write-Host "Destination: $destination"
Write-Host "Log:         $LogPath"

& robocopy.exe @arguments
$robocopyExit = $LASTEXITCODE

# Robocopy uses 0-7 for successful/no-op/copy-with-extra-file outcomes.
if ($robocopyExit -gt 7) {
    throw "Robocopy failed with exit code $robocopyExit. Review $LogPath"
}

Write-Host "Vault backup validation completed with robocopy exit code $robocopyExit."
if (-not $Execute) {
    Write-Host "Re-run with -Execute only after reviewing the dry-run log."
}
