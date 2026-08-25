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

function Test-Http([string]$Key, [string]$Name, [string]$Uri) {
    $handler = [System.Net.Http.HttpClientHandler]::new()
    $handler.ServerCertificateCustomValidationCallback =
        [System.Net.Http.HttpClientHandler]::DangerousAcceptAnyServerCertificateValidator
    $client = [System.Net.Http.HttpClient]::new($handler)
    $client.Timeout = [TimeSpan]::FromSeconds(5)
    try {
        $response = $client.GetAsync($Uri).GetAwaiter().GetResult()
        $status = [int]$response.StatusCode
        $ok = $status -in @(200, 302, 401)
        Add-Result $Key $Name $(if ($ok) { "PASS" } else { "FAIL" }) "HTTP $status"
        $response.Dispose()
    } catch {
        Add-Result $Key $Name "FAIL" "HTTP request failed: $($_.Exception.Message)"
    } finally {
        $client.Dispose()
        $handler.Dispose()
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
    Test-Tcp "frigate_http" "Frigate UI HTTPS" "192.168.30.20" 8971
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
        timestamp = (Get-Date).ToString("yyyy-MM-dd HH:mm:ss")
        collector = "Windows management workstation"
        summary = [ordered]@{ pass = $passed; fail = $failed; total = $results.Count }
        checks = $checks
    } | ConvertTo-Json -Depth 4
} else {
    $results | Select-Object Check, Status, Detail | Format-Table -AutoSize
}
if ($failed) { exit 1 }
exit 0
