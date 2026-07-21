[CmdletBinding()]
param(
    [switch]$SkipInstall,
    [switch]$SkipFrontend
)

$ErrorActionPreference = 'Stop'
$RootDir = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path

Write-Host '== backend deterministic tests =='
Push-Location (Join-Path $RootDir 'backend')
try { python -m pytest tests -m 'not live' -q }
finally { Pop-Location }

if (-not $SkipFrontend) {
    Write-Host '== frontend build checks =='
    Push-Location (Join-Path $RootDir 'frontend')
    try {
        if (-not $SkipInstall) { npm.cmd ci }
        npm.cmd test -- --run
        npm.cmd run build
    }
    finally { Pop-Location }
}

Write-Host '== release/security checks =='
python (Join-Path $RootDir 'scripts/verify_release.py')
