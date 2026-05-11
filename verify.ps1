# verify.ps1 - aggregate verification harness for the quantum-finance repo.
#
# Runs every tools/verify/v*.py script in numeric order. Non-zero exit if any
# single check fails. Reports are written to tools/verify/reports/.
#
# Usage:
#   pwsh ./verify.ps1
#   pwsh ./verify.ps1 -Only v1
#
[CmdletBinding()]
param(
    [string]$Only = ""
)

$ErrorActionPreference = "Stop"
$repoRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $repoRoot

$scripts = Get-ChildItem -Path "tools/verify" -Filter "v*.py" |
    Where-Object { $_.Name -match '^v[0-9_]+_.*\.py$' } |
    Sort-Object Name

if ($Only) {
    $scripts = $scripts | Where-Object { $_.BaseName -like "$Only*" }
}

if (-not $scripts) {
    Write-Host "No verify scripts found." -ForegroundColor Yellow
    exit 0
}

$failures = @()
foreach ($s in $scripts) {
    $modulePath = "tools.verify." + $s.BaseName
    Write-Host ""
    Write-Host "=== $($s.BaseName) ===" -ForegroundColor Cyan
    & python -m $modulePath
    $rc = $LASTEXITCODE
    if ($rc -ne 0) {
        $failures += "$($s.BaseName) (exit $rc)"
    }
}

Write-Host ""
if ($failures.Count -eq 0) {
    Write-Host "All verification checks passed." -ForegroundColor Green
    exit 0
} else {
    Write-Host "FAILED checks:" -ForegroundColor Red
    $failures | ForEach-Object { Write-Host "  - $_" -ForegroundColor Red }
    exit 1
}
