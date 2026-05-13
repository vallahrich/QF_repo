param(
    [string]$AdminUser = 'azureuser',
    [string]$VmNames = '',
    [switch]$CleanDestination,
    [switch]$SkipSummarize
)

$ErrorActionPreference = 'Continue'
$BundleDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$RepoRoot = Resolve-Path (Join-Path $BundleDir '..\..')
$Manifest = Get-Content (Join-Path $BundleDir 'manifest.json') -Raw | ConvertFrom-Json
$Dest = Join-Path $RepoRoot 'p4_experiments\canonical\outputs\phase08d_qae_hhl_scout\results'
$SshOptions = @('-o', 'StrictHostKeyChecking=no', '-o', 'BatchMode=yes', '-o', 'ConnectTimeout=20')
New-Item -ItemType Directory -Force -Path $Dest | Out-Null

$vms = @($Manifest.vms)
if ($VmNames.Trim()) {
    $wanted = @{}
    foreach ($name in @($VmNames -split '[,;]' | ForEach-Object { $_.Trim() } | Where-Object { $_ })) {
        $wanted[$name] = $true
    }
    $vms = @($vms | Where-Object { $wanted.ContainsKey($_.name) })
    if ($vms.Count -ne $wanted.Count) {
        throw "One or more -VmNames were not found in manifest.json"
    }
}

if ($CleanDestination) {
    Write-Host "Cleaning local QAE/HHL scout JSON files before sync: $Dest" -ForegroundColor Yellow
    Get-ChildItem -Path $Dest -File -Filter '*.json' -ErrorAction SilentlyContinue | Remove-Item -Force
}

foreach ($vm in $vms) {
    $target = "$AdminUser@$($vm.publicIp)"
    Write-Host "--- Syncing QAE/HHL scout from $($vm.name) $($vm.location) ---" -ForegroundColor Cyan
    & scp @SshOptions "${target}:~/qf-phase8-20260425/quantum-finance/p4_experiments/canonical/outputs/phase08d_qae_hhl_scout/results/*.json" $Dest
    if ($LASTEXITCODE -ne 0) {
        Write-Warning "No QAE/HHL scout results synced or scp failed for $($vm.name)."
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