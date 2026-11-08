[CmdletBinding()]
param(
    [ValidatePattern('^[A-Za-z0-9._-]+$')]
    [string]$DeployHost
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$appRoot = Split-Path -Parent $PSScriptRoot
$releaseFiles = @('dist', 'docker-compose.yml', 'nginx.conf')

Push-Location $appRoot
try {
    npm ci
    if ($LASTEXITCODE -ne 0) { throw 'npm ci failed' }

    node scripts/build.mjs
    if ($LASTEXITCODE -ne 0) { throw 'Mermaid Viewer build failed' }

    node scripts/verify-diagrams.mjs
    if ($LASTEXITCODE -ne 0) { throw 'Mermaid Viewer verification failed' }

    foreach ($relativePath in $releaseFiles) {
        if (-not (Test-Path -LiteralPath (Join-Path $appRoot $relativePath))) {
            throw "Release input is missing: $relativePath"
        }
    }

    Write-Output 'Release artifact built and verified: dist/'
    Get-Content -LiteralPath (Join-Path $appRoot 'dist/SHA256SUMS')

    if ([string]::IsNullOrWhiteSpace($DeployHost)) {
        Write-Output 'Packaging check complete; no deploy host was supplied.'
        exit 0
    }

    $releaseId = (Get-FileHash -Algorithm SHA256 -LiteralPath (Join-Path $appRoot 'dist/SHA256SUMS')).Hash.ToLowerInvariant().Substring(0, 16)
    $remoteStage = "/tmp/mermaid-viewer-release-$releaseId"

    ssh $DeployHost "test ! -e '$remoteStage' && install -d -m 0755 '$remoteStage'"
    if ($LASTEXITCODE -ne 0) { throw 'Could not create remote release staging directory' }

    scp -r @releaseFiles (Join-Path $PSScriptRoot 'deploy.sh') "${DeployHost}:$remoteStage/"
    if ($LASTEXITCODE -ne 0) { throw 'Could not upload the release artifact' }

    ssh $DeployHost "sh '$remoteStage/deploy.sh' '$remoteStage'"
    if ($LASTEXITCODE -ne 0) { throw 'Remote deployment failed; inspect the reported rollback state' }
} finally {
    Pop-Location
}
