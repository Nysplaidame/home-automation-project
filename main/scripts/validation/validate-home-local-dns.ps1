param(
    [string]$DnsServer = "192.168.10.1",
    [switch]$SkipLive
)

$ErrorActionPreference = "Stop"
$projectRoot = Resolve-Path (Join-Path $PSScriptRoot "..\..")
$dhcpPath = Join-Path $projectRoot "configs\openwrt\dhcp-config.conf"
$matrixPath = Join-Path $projectRoot "docs\reference\service-matrix.md"

$dhcpText = Get-Content $dhcpPath -Raw
$recordMatches = [regex]::Matches(
    $dhcpText,
    "(?ms)^config domain\s+option name '([^']+)'\s+option ip '([^']+)'"
)

$records = @{}
foreach ($match in $recordMatches) {
    $name = $match.Groups[1].Value.ToLowerInvariant()
    $ip = $match.Groups[2].Value
    if ($records.ContainsKey($name)) {
        throw "Duplicate OpenWrt DNS alias: $name"
    }
    $records[$name] = $ip
}

$matrixText = Get-Content $matrixPath -Raw
$matrixMatches = [regex]::Matches(
    $matrixText,
    '(?m)^\| `([^`]+\.home\.local)` \| `([0-9.]+)` \|'
)

$matrixRecords = @{}
foreach ($match in $matrixMatches) {
    $name = $match.Groups[1].Value.ToLowerInvariant()
    $ip = $match.Groups[2].Value
    if ($matrixRecords.ContainsKey($name)) {
        throw "Duplicate service-matrix DNS alias: $name"
    }
    $matrixRecords[$name] = $ip
}

$errors = [Collections.Generic.List[string]]::new()
foreach ($name in $matrixRecords.Keys) {
    if (-not $records.ContainsKey($name)) {
        $errors.Add("Missing from OpenWrt config: $name")
    } elseif ($records[$name] -ne $matrixRecords[$name]) {
        $errors.Add(
            "Address mismatch for ${name}: OpenWrt=$($records[$name]) matrix=$($matrixRecords[$name])"
        )
    }
}

if (-not $SkipLive) {
    foreach ($name in ($matrixRecords.Keys | Sort-Object)) {
        try {
            $answers = Resolve-DnsName $name -Server $DnsServer -DnsOnly -QuickTimeout |
                Where-Object Type -eq "A" |
                Select-Object -ExpandProperty IPAddress
            if ($matrixRecords[$name] -notin $answers) {
                $errors.Add(
                    "Live DNS mismatch for ${name}: expected $($matrixRecords[$name]), got $($answers -join ',')"
                )
            }
        } catch {
            $errors.Add("Live DNS lookup failed for ${name}: $($_.Exception.Message)")
        }
    }
}

if ($errors.Count -gt 0) {
    $errors | ForEach-Object { Write-Error $_ -ErrorAction Continue }
    exit 1
}

Write-Output (
    "Validated {0} home.local aliases across OpenWrt, service matrix, and {1}." -f
    $matrixRecords.Count,
    $(if ($SkipLive) { "source only" } else { "DNS server $DnsServer" })
)
