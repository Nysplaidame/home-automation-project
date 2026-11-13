[CmdletBinding()]
param(
    [switch]$Apply,
    [switch]$Remove,
    [string]$HostsPath = "$env:SystemRoot/System32/drivers/etc/hosts"
)

$ErrorActionPreference = 'Stop'
$entry = '192.168.20.102 vault.home.local # home-automation-project: local Vaultwarden'
$path = (Resolve-Path -LiteralPath $HostsPath).Path
$bytes = [IO.File]::ReadAllBytes($path)
$text = [Text.Encoding]::UTF8.GetString($bytes)
$lines = $text -split '\r?\n'
$matches = @($lines | Where-Object {
    $fields = ($_ -split '#', 2)[0].Trim() -split '\s+'
    $fields.Count -gt 1 -and $fields[1..($fields.Count - 1)] -contains 'vault.home.local'
})
if ($Remove) {
    if ($matches | Where-Object { $_ -ne $entry }) { throw 'Unmanaged Vaultwarden entry exists; inspect manually.' }
    $newText = $text.Replace($entry + "`r`n", '').Replace($entry + "`n", '')
    if ($newText.EndsWith($entry)) { $newText = $newText.Substring(0, $newText.Length - $entry.Length) }
} else {
    if ($matches.Count) {
        foreach ($line in $matches) {
            if (($line.Trim() -split '\s+')[0] -ne '192.168.20.102') { throw 'Conflicting Vaultwarden address; inspect manually.' }
        }
        Write-Output 'Expected Vaultwarden mapping already exists; no changes.'
        return
    }
    $newline = if ($text.Contains("`r`n")) { "`r`n" } else { "`n" }
    $separator = if ($text.EndsWith("`n") -or $text.Length -eq 0) { '' } else { $newline }
    $newText = $text + $separator + $entry + $newline
}
if ($newText -eq $text) { Write-Output 'No changes needed.'; return }
if (-not $Apply) {
    Write-Output "Preview only: $(if ($Remove) { 'remove' } else { 'add' }) $entry"
    Write-Output 'Use -Apply in an Administrator PowerShell window. Mullvad settings are not changed.'
    return
}
$backup = Join-Path ([IO.Path]::GetTempPath()) ('hosts-before-local-vault-' + [guid]::NewGuid().ToString('N') + '.bak')
[IO.File]::WriteAllBytes($backup, $bytes)
# Preserve all existing text. This fixed entry contains no secret and affects no public name.
[IO.File]::WriteAllText($path, $newText, [Text.UTF8Encoding]::new($false))
Write-Output "Updated $path; backup: $backup"
Write-Output 'Restart affected browsers if they cached a failed lookup. Roll back this entry with -Remove -Apply.'
