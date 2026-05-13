param(
    [ValidateSet('canary', 'floquet', 'surface', 'all')]
    [string]$Plan = 'canary',
    [string]$AdminUser = 'azureuser',
    [int]$TimeoutSeconds = 36000,
    [string]$Entities = '',
    [string[]]$VmNames = @(),
    [switch]$Force,
    [switch]$DryRun,
    [switch]$SkipIdleCheck
)

$ErrorActionPreference = 'Stop'
$BundleDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$RepoRoot = Resolve-Path (Join-Path $BundleDir '..\..')
$Manifest = Get-Content (Join-Path $BundleDir 'manifest.json') -Raw | ConvertFrom-Json
$SshOptions = @('-o', 'StrictHostKeyChecking=no', '-o', 'BatchMode=yes', '-o', 'ConnectTimeout=20')
$SshCommandOptions = @('-n') + $SshOptions
$ScoutModule = Join-Path $RepoRoot 'p4_experiments\canonical\phase8d_qae_hhl_scout.py'
$SelectionManifest = Join-Path $RepoRoot 'p4_experiments\canonical\outputs\phase08d_qae_hhl_scout\selection_manifest.json'

if (-not (Test-Path $ScoutModule)) {
    throw "Scout module not found: $ScoutModule"
}
if (-not (Test-Path $SelectionManifest)) {
    throw "Selection manifest not found: $SelectionManifest. Run phase8d_select_experiments.py after Phase 8/8a, 8b, and 8c are complete."
}
$selection = Get-Content $SelectionManifest -Raw | ConvertFrom-Json
if ($selection.status -ne 'complete') {
    throw "Selection manifest is not complete; blockers=$($selection.blockers -join ',')"
}

$vms = @($Manifest.vms)
if ($VmNames.Count -gt 0) {
    $wanted = @{}
    foreach ($name in $VmNames) { $wanted[$name] = $true }
    $vms = @($vms | Where-Object { $wanted.ContainsKey($_.name) })
    if ($vms.Count -ne $VmNames.Count) {
        throw "One or more -VmNames were not found in manifest.json"
    }
}
if ($vms.Count -eq 0) { throw 'No VMs selected.' }

$shardCount = $vms.Count
$shardIndex = 0
foreach ($vm in $vms) {
    $target = "$AdminUser@$($vm.publicIp)"
    Write-Host "--- Preparing QAE/HHL scout on $($vm.name) shard=$shardIndex/$shardCount plan=$Plan ---" -ForegroundColor Cyan

    if (-not $SkipIdleCheck) {
        $running = (& ssh @SshCommandOptions $target "pgrep -af '[p]4_experiments.canonical.phase8_big_run' || true") -join "`n"
        if ($running.Trim()) {
            throw "$($vm.name) still has Phase 8 big-run processes. Re-run after Phase 8 is done, or pass -SkipIdleCheck intentionally."
        }
    }

    & scp @SshOptions $ScoutModule "${target}:~/qf-phase8-20260425/quantum-finance/p4_experiments/canonical/phase8d_qae_hhl_scout.py"
    if ($LASTEXITCODE -ne 0) { throw "Failed to copy scout module to $($vm.name)" }
    & ssh @SshCommandOptions $target "mkdir -p ~/qf-phase8-20260425/quantum-finance/p4_experiments/canonical/outputs/phase08d_qae_hhl_scout"
    if ($LASTEXITCODE -ne 0) { throw "Failed to create scout directory on $($vm.name)" }
    & scp @SshOptions $SelectionManifest "${target}:~/qf-phase8-20260425/quantum-finance/p4_experiments/canonical/outputs/phase08d_qae_hhl_scout/selection_manifest.json"
    if ($LASTEXITCODE -ne 0) { throw "Failed to copy selection manifest to $($vm.name)" }

    $forceArg = if ($Force) { ' --force' } else { '' }
    $dryRunArg = if ($DryRun) { ' --dry-run' } else { '' }
    $entitiesArg = if ($Entities.Trim()) { " --entities `"$Entities`"" } else { '' }
    $remoteScript = @"
#!/usr/bin/env bash
set -Eeuo pipefail
source "`$HOME/phase8_6vm.env"
RUN_ROOT="`${PHASE8_RUN_ROOT:-`$HOME/qf-phase8-20260425}"
REPO="`$RUN_ROOT/quantum-finance"
VENV="`$RUN_ROOT/.venv"
LOG_DIR="`$RUN_ROOT/logs"
mkdir -p "`$LOG_DIR" "`$REPO/p4_experiments/canonical/outputs/phase08d_qae_hhl_scout/results"
source "`$VENV/bin/activate"
cd "`$REPO"
export PYTHONHASHSEED="`${PYTHONHASHSEED:-0}"
export PYTHONIOENCODING="`${PYTHONIOENCODING:-utf-8}"
export P4_SCOUT_CELL_TIMEOUT_S="$TimeoutSeconds"
export OMP_NUM_THREADS="`${OMP_NUM_THREADS:-1}"
export MKL_NUM_THREADS="`${MKL_NUM_THREADS:-1}"
export OPENBLAS_NUM_THREADS="`${OPENBLAS_NUM_THREADS:-1}"
export NUMEXPR_NUM_THREADS="`${NUMEXPR_NUM_THREADS:-1}"
LOG="`$LOG_DIR/qae_hhl_scout_${Plan}_$($vm.name)_`$(date -u +%Y%m%dT%H%M%SZ).log"
python -u -m p4_experiments.canonical.phase8d_qae_hhl_scout --plan "$Plan"$entitiesArg --timeout-s "$TimeoutSeconds" --shard-index "$shardIndex" --shard-count "$shardCount"$forceArg$dryRunArg 2>&1 | tee -a "`$LOG"
"@

    $tmp = New-TemporaryFile
    try {
        $utf8NoBom = [System.Text.UTF8Encoding]::new($false)
        [System.IO.File]::WriteAllText($tmp.FullName, ($remoteScript -replace "`r?`n", "`n"), $utf8NoBom)
        $remoteLauncher = "~/qf-phase8-20260425/run_qae_hhl_scout_${Plan}_shard${shardIndex}.sh"
        & scp @SshOptions $tmp "${target}:$remoteLauncher"
        if ($LASTEXITCODE -ne 0) { throw "Failed to copy launcher to $($vm.name)" }
        $remote = "chmod +x $remoteLauncher; nohup bash $remoteLauncher > ~/qf-phase8-20260425/logs/qae_hhl_scout_${Plan}_shard${shardIndex}.nohup.log 2>&1 < /dev/null & echo scout_pid=`$!"
        & ssh @SshCommandOptions $target $remote
        if ($LASTEXITCODE -ne 0) { throw "Failed to launch scout on $($vm.name)" }
    }
    finally {
        Remove-Item -Force $tmp -ErrorAction SilentlyContinue
    }
    $shardIndex += 1
}

Write-Host "QAE/HHL scout launched on $($vms.Count) VM(s). Use Sync-QAEHHLScout.ps1 after completion." -ForegroundColor Green