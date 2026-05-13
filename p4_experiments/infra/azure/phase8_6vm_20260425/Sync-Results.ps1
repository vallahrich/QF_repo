param(
    [string]$AdminUser = 'azureuser',
    [switch]$CleanDestination,
    [switch]$SkipFinalize
)

$ErrorActionPreference = 'Continue'
$BundleDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$RepoRoot = Resolve-Path (Join-Path $BundleDir '..\..')
$Manifest = Get-Content (Join-Path $BundleDir 'manifest.json') -Raw | ConvertFrom-Json
$Dest = Join-Path $RepoRoot 'p4_experiments\common\output\results'
$SshOptions = @('-o', 'StrictHostKeyChecking=no', '-o', 'BatchMode=yes', '-o', 'ConnectTimeout=20')
New-Item -ItemType Directory -Force -Path $Dest | Out-Null

if ($CleanDestination) {
    Write-Host "Cleaning local result JSON/log files before sync: $Dest" -ForegroundColor Yellow
    Get-ChildItem -Path $Dest -File |
        Where-Object { $_.Extension -in @('.json', '.log') } |
        Remove-Item -Force
}

foreach ($vm in $Manifest.vms) {
    $target = "$AdminUser@$($vm.publicIp)"
    Write-Host "--- Syncing $($vm.name) $($vm.location) ---" -ForegroundColor Cyan
    & scp @SshOptions "${target}:~/qf-phase8-20260425/quantum-finance/p4_experiments/common/output/results/*.json" $Dest
    if ($LASTEXITCODE -ne 0) {
        Write-Warning "No results synced or scp failed for $($vm.name)."
    }
}

Write-Host "Results directory: $Dest" -ForegroundColor Green

if (-not $SkipFinalize) {
    $QfRoot = Resolve-Path (Join-Path $RepoRoot '..')
    $Python = Join-Path $QfRoot '.venv\Scripts\python.exe'
    if (Test-Path $Python) {
        Push-Location $RepoRoot
        try {
            & $Python -m p4_experiments.canonical.finalize_phase8_results
        }
        finally {
            Pop-Location
        }
        if ($LASTEXITCODE -ne 0) {
            Write-Warning "Phase 8 finalizer reported incomplete local results."
        }
    } else {
        Write-Warning "Python not found for finalizer: $Python"
    }
}
