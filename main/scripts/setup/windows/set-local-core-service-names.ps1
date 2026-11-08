[CmdletBinding()]
param(
    [switch]$Apply,
    [switch]$Remove,
    [string]$HostsPath = "$env:SystemRoot/System32/drivers/etc/hosts"
)

$ErrorActionPreference = 'Stop'
$entries = [ordered]@{
    'homeassistant.home.local' = '192.168.20.101'
    'frigate.home.local'        = '192.168.30.20'
    'grafana.home.local'        = '192.168.60.10'
    'uptime-kuma.home.local'    = '192.168.60.10'
}
$marker = '# home-automation-project: local core service'
$path = (Resolve-Path -LiteralPath $HostsPath).Path
if ($Apply -and $path -eq "$env:SystemRoot\System32\drivers\etc\hosts") {
    $identity = [Security.Principal.WindowsIdentity]::GetCurrent()
    $elevated = ([Security.Principal.WindowsPrincipal]::new($identity)).IsInRole(
        [Security.Principal.WindowsBuiltInRole]::Administrator
    )
    if (-not $elevated) {
        throw 'This shell is not elevated. Open PowerShell with Run as administrator, then run the script with -Apply.'
    }
}
$bytes = [IO.File]::ReadAllBytes($path)
$text = [Text.Encoding]::UTF8.GetString($bytes)
$newline = if ($text.Contains("`r`n")) { "`r`n" } else { "`n" }
$lines = @($text -split '\r?\n')
$add = [Collections.Generic.List[string]]::new()
$removeLines = [Collections.Generic.List[string]]::new()

foreach ($name in $entries.Keys) {
    $ip = $entries[$name]
    $expected = "$ip $name $marker"
    $matches = @($lines | Where-Object {
        $fields = ($_ -split '#', 2)[0].Trim() -split '\s+'
        $fields.Count -gt 1 -and $fields[1..($fields.Count - 1)] -contains $name
    })
    if ($Remove) {
        foreach ($line in $matches) {
            if ($line -ne $expected) { throw "Unmanaged entry for $name exists; inspect manually." }
            $removeLines.Add($line)
        }
    } elseif ($matches.Count -eq 0) {
        $add.Add($expected)
    } else {
        foreach ($line in $matches) {
            if (($line.Trim() -split '\s+')[0] -ne $ip) {
                throw "Conflicting address for $name; inspect manually."
            }
        }
    }
}

if ($add.Count -eq 0 -and $removeLines.Count -eq 0) {
    Write-Output 'Core service mappings already match; no changes needed.'
    return
}
foreach ($line in $add) { Write-Output "Add: $line" }
foreach ($line in $removeLines) { Write-Output "Remove: $line" }
if (-not $Apply) {
    Write-Output 'Preview only. Use -Apply in Administrator PowerShell. Mullvad settings are not changed.'
    return
}

$newLines = @($lines | Where-Object { $removeLines -notcontains $_ })
$newText = $newLines -join $newline
if ($add.Count -gt 0) {
    if ($newText.Length -gt 0 -and -not $newText.EndsWith("`n")) { $newText += $newline }
    $newText += ($add -join $newline) + $newline
}
$backup = Join-Path ([IO.Path]::GetTempPath()) ('hosts-before-core-services-' + [guid]::NewGuid().ToString('N') + '.bak')
[IO.File]::WriteAllBytes($backup, $bytes)
[IO.File]::WriteAllText($path, $newText, [Text.UTF8Encoding]::new($false))
Clear-DnsClientCache
Write-Output "Updated $path; backup: $backup"
Write-Output 'Restart browsers that cached a failed lookup. Roll back these managed entries with -Remove -Apply.'
