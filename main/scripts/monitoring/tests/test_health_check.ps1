# Offline contract tests: load only function definitions, never the probe entrypoint.
$ErrorActionPreference = 'Stop'
$source = Join-Path $PSScriptRoot '../health_check.ps1'
$parseErrors = $null
$ast = [System.Management.Automation.Language.Parser]::ParseFile($source, [ref]$null, [ref]$parseErrors)
if ($parseErrors) { throw $parseErrors }
foreach ($definition in $ast.FindAll({ param($node) $node -is [System.Management.Automation.Language.FunctionDefinitionAst] }, $false)) {
    Invoke-Expression $definition.Extent.Text
}
$results = [System.Collections.Generic.List[object]]::new()
$script:httpCode = 200
$script:httpThrows = $false
$script:verified = $false
function Invoke-HealthHttp([string]$Uri, [switch]$VerifyTls) {
    $script:verified = [bool]$VerifyTls
    if ($script:httpThrows) { throw 'Private transport detail must not escape' }
    return $script:httpCode
}
$script:dnsAnswers = @()
$script:dnsThrows = $false
$script:dnsTimeout = $false
function Resolve-HealthDns([string]$Name) {
    if ($script:dnsTimeout) { Write-Error -Message 'Private resolver detail' -ErrorId 'ERROR_TIMEOUT' -ErrorAction Stop }
    if ($script:dnsThrows) { throw 'Private resolver detail must not escape' }
    return $script:dnsAnswers
}
function Assert-Last([string]$Expected) {
    if ($results[-1].Status -ne $Expected) { throw "Expected $Expected, received $($results[-1].Status)" }
}
Test-Http 'plain' 'Reachability' 'https://example.invalid/'
Assert-Last 'PASS'
if ($script:verified -or $results[-1].Detail -notmatch 'trust not assessed') { throw 'Reachability misrepresented as trust' }
Test-Http 'trusted' 'Trust' 'https://example.invalid/' -VerifyTls
Assert-Last 'PASS'
if (-not $script:verified) { throw 'TLS verification flag lost' }
$script:httpCode = 401
Test-Http 'auth' 'Listener' 'https://example.invalid/' -VerifyTls
Assert-Last 'PASS' # Listener, not successful login.
$script:httpCode = 503
Test-Http 'unavailable' 'Listener' 'https://example.invalid/'
Assert-Last 'FAIL'
$script:httpThrows = $true
Test-Http 'broken' 'Trust' 'https://example.invalid/' -VerifyTls
Assert-Last 'FAIL'
if ($results[-1].Detail -match 'Private') { throw 'Exception detail leaked' }
$script:dnsAnswers = @([pscustomobject]@{ Type='A'; IPAddress='192.168.20.102' })
Test-Dns 'local' 'Local DNS' 'homepage.home.local' '192.168.20.102'
Assert-Last 'PASS'
$script:dnsAnswers += [pscustomobject]@{ Type='A'; IPAddress='192.168.20.103' }
Test-Dns 'wrong' 'Local DNS' 'homepage.home.local' '192.168.20.102'
Assert-Last 'FAIL'
Test-Dns 'public' 'Public DNS' 'example.com'
Assert-Last 'PASS'
$script:dnsAnswers = @()
Test-Dns 'empty' 'Public DNS' 'example.com'
Assert-Last 'FAIL'
$script:dnsThrows = $true
Test-Dns 'missing' 'Public DNS' 'example.com'
Assert-Last 'UNKNOWN'
if ($results[-1].Detail -match 'Private') { throw 'Resolver detail leaked' }
$script:dnsThrows = $false
$script:dnsTimeout = $true
Test-Dns 'timeout' 'Public DNS' 'example.com'
Assert-Last 'FAIL'
if ($results[-1].Detail -notmatch 'ERROR_TIMEOUT' -or $results[-1].Detail -match 'Private') { throw 'Timeout classification or redaction failed' }
Write-Output "PASS: $($results.Count) offline HTTP/DNS cases; no probes executed."
