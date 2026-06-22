[CmdletBinding()]
param()

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$repoRoot = $PSScriptRoot
$checks = [System.Collections.Generic.List[object]]::new()

function Add-Check {
    param([string]$Name, [bool]$Pass, [string]$Detail)
    $checks.Add([pscustomobject]@{ Check = $Name; Status = if ($Pass) { "PASS" } else { "FAIL" }; Detail = $Detail })
}

Add-Check "Active checkout" (Test-Path (Join-Path $repoRoot "PROJECT-INDEX.md")) $repoRoot

foreach ($tool in @("git", "ssh", "python", "pwsh")) {
    $command = Get-Command $tool -ErrorAction SilentlyContinue
    Add-Check "Tool: $tool" ($null -ne $command) $(if ($command) { $command.Source } else { "not found" })
}

$expected = @(
    "README.md",
    "PROJECT-INDEX.md",
    "TO-DO.md",
    "docs/reference/current-live-state.md",
    "tools/router-deploy/lint.py"
)
foreach ($relativePath in $expected) {
    Add-Check "File: $relativePath" (Test-Path (Join-Path $repoRoot $relativePath)) $relativePath
}

$checks | Format-Table -AutoSize
if ($checks.Status -contains "FAIL") { exit 1 }
exit 0
