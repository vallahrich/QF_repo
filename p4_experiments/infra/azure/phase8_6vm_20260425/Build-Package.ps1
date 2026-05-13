$ErrorActionPreference = 'Stop'

$BundleDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$RepoRoot = Resolve-Path (Join-Path $BundleDir '..\..\..\..')
$RepoParent = Split-Path -Parent $RepoRoot
$PackagePath = Join-Path $BundleDir 'qf_phase8_20260425.tar.gz'
$TempPackagePath = Join-Path $env:TEMP 'qf_phase8_20260425.tar.gz'

if (Test-Path $PackagePath) {
    Remove-Item $PackagePath -Force
}
if (Test-Path $TempPackagePath) {
    Remove-Item $TempPackagePath -Force
}

$Excludes = @(
    '--exclude=quantum-finance/.git',
    '--exclude=quantum-finance/.pytest_cache',
    '--exclude=quantum-finance/**/__pycache__',
    '--exclude=quantum-finance/p4_experiments/common/output/results',
    '--exclude=quantum-finance/p4_experiments/common/output/phase8_logs',
    '--exclude=quantum-finance/p4_experiments/infra/azure/phase8_6vm_20260425/qf_phase8_20260425.tar.gz',
    '--exclude=quantum-finance/p4_experiments/infra/azure/phase8_6vm_20260425/qf_phase8_20260425.sha256'
)

$PackageItems = @(
    'quantum-finance/p4_experiments',
    'quantum-finance/README.md',
    'quantum-finance/LICENSE'
)

Write-Host "Building package: $PackagePath" -ForegroundColor Cyan
& tar.exe -czf $TempPackagePath @Excludes -C $RepoParent @PackageItems
if ($LASTEXITCODE -ne 0) {
    throw "tar failed with exit code $LASTEXITCODE"
}

Move-Item -Path $TempPackagePath -Destination $PackagePath -Force

$Hash = Get-FileHash -Algorithm SHA256 $PackagePath
Write-Host "Package SHA256: $($Hash.Hash)" -ForegroundColor Green
$Hash.Hash | Set-Content -Path (Join-Path $BundleDir 'qf_phase8_20260425.sha256') -Encoding ascii
