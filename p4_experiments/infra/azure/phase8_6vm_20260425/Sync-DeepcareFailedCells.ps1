param(
    [string]$AdminUser = 'azureuser',
    [switch]$SkipSummarize
)

$ErrorActionPreference = 'Continue'
$BundleDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$RepoRoot = Resolve-Path (Join-Path $BundleDir '..\..')
$Dest = Join-Path $RepoRoot 'p4_experiments\canonical\outputs\phase08d_qae_hhl_scout\results'
$SshOptions = @('-o', 'StrictHostKeyChecking=no', '-o', 'BatchMode=yes', '-o', 'ConnectTimeout=20')

$Vms = @(
    [pscustomobject]@{ name = 'qf-dc-fx4-wus2'; ip = '40.65.93.57'; location = 'westus2' },
    [pscustomobject]@{ name = 'qf-dc-fx4-eus2'; ip = '20.242.33.50'; location = 'eastus2' },
    [pscustomobject]@{ name = 'qf-dc-fx4-weu'; ip = '20.105.248.87'; location = 'westeurope' },
    [pscustomobject]@{ name = 'qf-dc-fx4-neu'; ip = '52.138.253.127'; location = 'northeurope' },
    [pscustomobject]@{ name = 'qf-dc-fx4-frc'; ip = '20.216.131.43'; location = 'francecentral' },
    [pscustomobject]@{ name = 'qf-dc-fx4-gwc'; ip = '51.116.177.227'; location = 'germanywestcentral' },
    [pscustomobject]@{ name = 'qf-dc-fx4-sec'; ip = '20.91.136.252'; location = 'swedencentral' },
    [pscustomobject]@{ name = 'qf-dc-fx4-cus'; ip = '74.249.152.13'; location = 'centralus' }
)

New-Item -ItemType Directory -Force -Path $Dest | Out-Null

foreach ($vm in $Vms) {
    $target = "$AdminUser@$($vm.ip)"
    Write-Host "--- Syncing $($vm.name) $($vm.location) ---" -ForegroundColor Cyan
    & scp @SshOptions "${target}:~/qf-phase8-20260425/quantum-finance/p4_experiments/canonical/outputs/phase08d_qae_hhl_scout/results/*.json" $Dest
    if ($LASTEXITCODE -ne 0) {
        Write-Warning "No failed-cell results synced or scp failed for $($vm.name)."
    }
}

Write-Host "QAE/HHL scout results directory: $Dest" -ForegroundColor Green

if (-not $SkipSummarize) {
    $QfRoot = Resolve-Path (Join-Path $RepoRoot '..')
    $Python = Join-Path $QfRoot '.venv\Scripts\python.exe'
    if (Test-Path $Python) {
        Push-Location $RepoRoot
        try {
            & $Python -m p4_experiments.canonical.phase8d_qae_hhl_scout --summarize
        }
        finally {
            Pop-Location
        }
    } else {
        Write-Warning "Python not found for scout summarizer: $Python"
    }
}