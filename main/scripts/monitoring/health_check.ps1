[CmdletBinding()]
param([switch]$Full, [switch]$Json)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"
$results = [System.Collections.Generic.List[object]]::new()

function Add-Result([string]$Key, [string]$Name, [string]$Status, [string]$Detail) {
    $results.Add([pscustomobject]@{ Key = $Key; Check = $Name; Status = $Status; Detail = $Detail })
}

function Test-Tcp([string]$Key, [string]$Name, [string]$HostName, [int]$Port) {
    $client = [Net.Sockets.TcpClient]::new()
    try {
        $pending = $client.BeginConnect($HostName, $Port, $null, $null)
        $ok = $pending.AsyncWaitHandle.WaitOne(3000)
        if ($ok) { $client.EndConnect($pending) }
        Add-Result $Key $Name $(if ($ok) { "PASS" } else { "FAIL" }) "$HostName`:$Port"
    } catch {
        Add-Result $Key $Name "FAIL" "$HostName`:$Port"
    } finally {
        $client.Dispose()
    }
}

function Invoke-HealthHttp([string]$Uri, [switch]$VerifyTls) {
    $handler = [System.Net.Http.HttpClientHandler]::new()
    $handler.AllowAutoRedirect = $false
    if (-not $VerifyTls) {
        $handler.ServerCertificateCustomValidationCallback =
            [System.Net.Http.HttpClientHandler]::DangerousAcceptAnyServerCertificateValidator
    }
    $client = [System.Net.Http.HttpClient]::new($handler)
    $client.Timeout = [TimeSpan]::FromSeconds(5)
    try {
        $response = $client.GetAsync($Uri, [System.Net.Http.HttpCompletionOption]::ResponseHeadersRead).GetAwaiter().GetResult()
        try { return [int]$response.StatusCode } finally { $response.Dispose() }
    } finally {
        $client.Dispose()
        $handler.Dispose()
    }
}

function Test-Http([string]$Key, [string]$Name, [string]$Uri, [switch]$VerifyTls) {
    $scope = if ($VerifyTls) { 'certificate validation enabled' } else { 'reachability only; certificate trust not assessed' }
    try {
        $status = Invoke-HealthHttp -Uri $Uri -VerifyTls:$VerifyTls
        $ok = $status -in @(200, 302, 401)
        Add-Result $Key $Name $(if ($ok) { 'PASS' } else { 'FAIL' }) "HTTP $status; $scope; redirects not followed"
    } catch {
        Add-Result $Key $Name 'FAIL' "HTTP connection/validation failed; $scope"
    }
}

function Resolve-HealthDns([string]$Name) {
    Resolve-DnsName -Name $Name -Server '192.168.10.1' -Type A -DnsOnly -NoHostsFile -QuickTimeout -ErrorAction Stop
}

function Test-Dns([string]$Key, [string]$Name, [string]$Query, [string]$ExpectedAddress = '') {
    try {
        $addresses = @(Resolve-HealthDns $Query | Where-Object Type -eq 'A' | Select-Object -ExpandProperty IPAddress | Sort-Object -Unique)
        $ok = $addresses.Count -gt 0
        if ($ExpectedAddress) { $ok = $addresses.Count -eq 1 -and $addresses[0] -eq $ExpectedAddress }
        $answer = if ($addresses.Count) { $addresses -join ', ' } else { 'no A answer' }
        Add-Result $Key $Name $(if ($ok) { 'PASS' } else { 'FAIL' }) "$Query via 192.168.10.1: $answer"
    } catch {
        $code = $_.FullyQualifiedErrorId.Split(',')[0]
        $knownFailure = $code -in @('ERROR_TIMEOUT', 'DNS_ERROR_RCODE_NAME_ERROR', 'DNS_ERROR_RCODE_SERVER_FAILURE', 'DNS_ERROR_RCODE_REFUSED', 'DNS_ERROR_NO_DNS_SERVERS')
        if ($knownFailure) {
            Add-Result $Key $Name 'FAIL' "$Query via 192.168.10.1: $code"
        } else {
            Add-Result $Key $Name 'UNKNOWN' "$Query via 192.168.10.1: query did not return usable evidence; inspect resolver/client error manually"
        }
    }
}

Test-Tcp "router" "Router SSH" "192.168.10.1" 22
Test-Http "ha_http" "Home Assistant" "https://192.168.20.101:8123"
Test-Tcp "frigate_ping" "Frigate CT SSH" "192.168.30.20" 22
Test-Tcp "docker_host" "Docker host SSH" "192.168.20.102" 22
Test-Http "homepage" "Homepage HTTPS" "https://192.168.20.102/"
Test-Http "bambuddy" "Bambuddy" "http://192.168.20.102:8000"
Test-Tcp "mqtt" "MQTT TLS" "192.168.20.101" 8883
Test-Http "grafana" "Grafana" "http://192.168.60.10:3000/api/health"
Test-Http "uptime_kuma" "Uptime Kuma" "http://192.168.60.10:3001"
Test-Http "llamacpp" "llama.cpp" "http://192.168.20.104:8081/v1/models"
Test-Tcp "nas" "OMV backup NFS" "192.168.40.50" 2049
Test-Tcp "camera_01" "Camera 1 RTSP" "192.168.30.21" 554

if ($Full) {
    Test-Tcp "frigate_http" "Frigate UI HTTPS listener" "192.168.30.20" 8971
    Test-Dns 'dns_local' 'Local DNS answer' 'homepage.home.local' '192.168.20.102'
    Test-Dns 'dns_public' 'Public DNS answer' 'example.com'
    Test-Http 'tls_trust' 'Trusted Homepage HTTPS' 'https://homepage.home.local/' -VerifyTls
    Test-Http 'vault_tls' 'Trusted Vaultwarden HTTPS' 'https://vault.home.local/' -VerifyTls
    Test-Tcp 'proxmox_api' 'Proxmox management listener' '192.168.10.10' 8006
    Test-Tcp 'package_cache' 'APT cache listener from workstation' '192.168.20.102' 3142
    Test-Http 'immich' 'Immich API listener' 'http://192.168.20.102:2283/api/server/ping'
    Test-Http 'openwebui' 'Open WebUI listener' 'http://192.168.20.104:3002/health'

}

$failed = @($results | Where-Object Status -eq "FAIL").Count
$passed = @($results | Where-Object Status -eq "PASS").Count
if ($Json) {
    $checks = [ordered]@{}
    foreach ($result in $results) {
        $checks[$result.Key] = [ordered]@{
            status = $result.Status.ToLowerInvariant()
            detail = $result.Detail
        }
    }
    [pscustomobject]@{
        timestamp = [DateTimeOffset]::Now.ToString("yyyy-MM-ddTHH:mm:sszzz")
        collector = "Windows management workstation"
        summary = [ordered]@{ pass = $passed; fail = $failed; unknown = @($results | Where-Object Status -eq 'UNKNOWN').Count; total = $results.Count }
        checks = $checks
    } | ConvertTo-Json -Depth 4
} else {
    $results | Select-Object Check, Status, Detail | Format-Table -AutoSize
}
if ($failed) { exit 1 }
exit 0
