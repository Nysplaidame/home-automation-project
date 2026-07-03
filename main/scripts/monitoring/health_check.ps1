[CmdletBinding()]
param([switch]$Full)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"
$results = [System.Collections.Generic.List[object]]::new()

function Add-Result([string]$Name, [string]$Status, [string]$Detail) {
    $results.Add([pscustomobject]@{ Check = $Name; Status = $Status; Detail = $Detail })
}

function Test-Tcp([string]$Name, [string]$HostName, [int]$Port) {
    $client = [Net.Sockets.TcpClient]::new()
    try {
        $pending = $client.BeginConnect($HostName, $Port, $null, $null)
        $ok = $pending.AsyncWaitHandle.WaitOne(3000)
        if ($ok) { $client.EndConnect($pending) }
        Add-Result $Name $(if ($ok) { "PASS" } else { "FAIL" }) "$HostName`:$Port"
    } catch {
        Add-Result $Name "FAIL" "$HostName`:$Port"
    } finally {
        $client.Dispose()
    }
}

function Test-Http([string]$Name, [string]$Uri) {
    $oldCallback = [System.Net.ServicePointManager]::ServerCertificateValidationCallback
    [System.Net.ServicePointManager]::ServerCertificateValidationCallback = { $true }
    try {
        $request = [System.Net.HttpWebRequest]::Create($Uri)
        $request.Method = "GET"
        $request.Timeout = 5000
        $request.AllowAutoRedirect = $false
        $response = $request.GetResponse()
        $status = [int]$response.StatusCode
        $ok = $status -in @(200, 302, 401)
        Add-Result $Name $(if ($ok) { "PASS" } else { "FAIL" }) "HTTP $status"
        $response.Dispose()
    } catch {
        $status = if ($_.Exception.PSObject.Properties.Name -contains "Response" -and $_.Exception.Response) { [int]$_.Exception.Response.StatusCode } else { 0 }
        Add-Result $Name $(if ($status -in @(200, 302, 401)) { "PASS" } else { "FAIL" }) "HTTP $status"
    } finally {
        [System.Net.ServicePointManager]::ServerCertificateValidationCallback = $oldCallback
    }
}

Test-Tcp "Router SSH" "192.168.10.1" 22
Test-Http "Home Assistant" "https://192.168.20.101:8123"
Test-Tcp "Frigate CT SSH" "192.168.30.20" 22
Test-Tcp "Docker host SSH" "192.168.20.102" 22
Test-Http "Bambuddy" "http://192.168.20.102:8000"
Test-Tcp "MQTT TLS" "192.168.20.101" 8883
Test-Http "Grafana" "http://192.168.60.10:3000/api/health"
Test-Http "Uptime Kuma" "http://192.168.60.10:3001"
Test-Http "llama.cpp" "http://192.168.20.104:8081/v1/models"
Test-Tcp "OMV backup NFS" "192.168.40.50" 2049

if ($Full) {
    Test-Tcp "Frigate UI HTTPS" "192.168.30.20" 8971
}

$results | Format-Table -AutoSize
$failed = @($results | Where-Object Status -eq "FAIL").Count
if ($failed) { exit 1 }
exit 0
