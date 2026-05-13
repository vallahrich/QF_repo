param(
    [ValidateSet('floquet', 'surface', 'all')]
    [string]$Plan = 'all',
    [string]$AdminUser = 'azureuser',
    [int]$TimeoutSeconds = 36000,
    [string]$VmNames = 'qf-p8-vm1,qf-p8-vm2,qf-p8-vm3'
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
    throw "Selection manifest not found: $SelectionManifest"
}

$vmNameList = @($VmNames -split '[,;]' | ForEach-Object { $_.Trim() } | Where-Object { $_ })
$vms = @()
foreach ($name in $vmNameList) {
    $vm = $Manifest.vms | Where-Object { $_.name -eq $name } | Select-Object -First 1
    if ($null -eq $vm) {
        throw "VM not found in manifest: $name"
    }
    $vms += $vm
}
if ($vms.Count -eq 0) { throw 'No VMs selected.' }

$shardCount = $vms.Count
$shardIndex = 0
foreach ($vm in $vms) {
    $target = "$AdminUser@$($vm.publicIp)"
    Write-Host "--- Preparing overnight QAE/HHL scout on $($vm.name) shard=$shardIndex/$shardCount plan=$Plan ---" -ForegroundColor Cyan

    & scp @SshOptions $ScoutModule "${target}:~/qf-phase8-20260425/quantum-finance/p4_experiments/canonical/phase8d_qae_hhl_scout.py"
    if ($LASTEXITCODE -ne 0) { throw "Failed to copy scout module to $($vm.name)" }
    & ssh @SshCommandOptions $target "mkdir -p ~/qf-phase8-20260425/quantum-finance/p4_experiments/canonical/outputs/phase08d_qae_hhl_scout"
    if ($LASTEXITCODE -ne 0) { throw "Failed to create scout directory on $($vm.name)" }
    & scp @SshOptions $SelectionManifest "${target}:~/qf-phase8-20260425/quantum-finance/p4_experiments/canonical/outputs/phase08d_qae_hhl_scout/selection_manifest.json"
    if ($LASTEXITCODE -ne 0) { throw "Failed to copy selection manifest to $($vm.name)" }

    $remoteScript = @"
#!/usr/bin/env bash
set -Eeuo pipefail
source "`$HOME/phase8_6vm.env"
RUN_ROOT="`${PHASE8_RUN_ROOT:-`$HOME/qf-phase8-20260425}"
REPO="`$RUN_ROOT/quantum-finance"
VENV="`$RUN_ROOT/.venv"
LOG_DIR="`$RUN_ROOT/logs"
RESULT_DIR="`$REPO/p4_experiments/canonical/outputs/phase08d_qae_hhl_scout/results"
mkdir -p "`$LOG_DIR" "`$RESULT_DIR"
source "`$VENV/bin/activate"
cd "`$REPO"
export PYTHONHASHSEED="`${PYTHONHASHSEED:-0}"
export PYTHONIOENCODING="`${PYTHONIOENCODING:-utf-8}"
export P4_SCOUT_CELL_TIMEOUT_S="$TimeoutSeconds"
export OMP_NUM_THREADS="`${OMP_NUM_THREADS:-1}"
export MKL_NUM_THREADS="`${MKL_NUM_THREADS:-1}"
export OPENBLAS_NUM_THREADS="`${OPENBLAS_NUM_THREADS:-1}"
export NUMEXPR_NUM_THREADS="`${NUMEXPR_NUM_THREADS:-1}"
CHAIN_LOG="`$LOG_DIR/qae_hhl_scout_overnight_${Plan}_$($vm.name)_`$(date -u +%Y%m%dT%H%M%SZ).log"
exec > >(tee -a "`$CHAIN_LOG") 2>&1
echo "[overnight] started vm=$($vm.name) shard=$shardIndex/$shardCount plan=$Plan timeout_s=$TimeoutSeconds utc=`$(date -u +%Y-%m-%dT%H:%M:%SZ)"
while pgrep -af '[p]4_experiments.canonical.phase8d_qae_hhl_scout --plan canary|[r]un_qae_hhl_scout_canary' >/dev/null; do
  echo "[overnight] waiting for canary to finish utc=`$(date -u +%Y-%m-%dT%H:%M:%SZ)"
  sleep 60
done
if pgrep -af '[p]4_experiments.canonical.phase8d_qae_hhl_scout --plan $Plan|[r]un_qae_hhl_scout_${Plan}' >/dev/null; then
  echo "[overnight] $Plan already appears to be running; exiting duplicate launcher"
  exit 0
fi
python - <<'PY'
import json
from pathlib import Path

final = {"ok", "engine_failure", "timeout"}
result_dir = Path("p4_experiments/canonical/outputs/phase08d_qae_hhl_scout/results")
removed = 0
for path in result_dir.glob("*.json"):
    try:
        status = json.loads(path.read_text(encoding="utf-8")).get("status")
    except Exception:
        status = None
    if status not in final:
        path.unlink(missing_ok=True)
        removed += 1
print(f"[overnight] removed_nonfinal_records={removed}", flush=True)
PY
echo "[overnight] launching plan=$Plan utc=`$(date -u +%Y-%m-%dT%H:%M:%SZ)"
set +e
python -u -m p4_experiments.canonical.phase8d_qae_hhl_scout --plan "$Plan" --timeout-s "$TimeoutSeconds" --shard-index "$shardIndex" --shard-count "$shardCount"
rc=`$?
set -e
python -u -m p4_experiments.canonical.phase8d_qae_hhl_scout --summarize || true
echo "[overnight] finished plan=$Plan rc=`$rc utc=`$(date -u +%Y-%m-%dT%H:%M:%SZ)"
exit `$rc
"@

    $tmp = New-TemporaryFile
    try {
        $utf8NoBom = [System.Text.UTF8Encoding]::new($false)
        [System.IO.File]::WriteAllText($tmp.FullName, ($remoteScript -replace "`r?`n", "`n"), $utf8NoBom)
        $remoteLauncher = "~/qf-phase8-20260425/run_qae_hhl_scout_overnight_${Plan}_shard${shardIndex}.sh"
        & scp @SshOptions $tmp "${target}:$remoteLauncher"
        if ($LASTEXITCODE -ne 0) { throw "Failed to copy overnight launcher to $($vm.name)" }
        $remote = "chmod +x $remoteLauncher; nohup bash $remoteLauncher > ~/qf-phase8-20260425/logs/qae_hhl_scout_overnight_${Plan}_shard${shardIndex}.nohup.log 2>&1 < /dev/null & echo overnight_pid=`$!"
        & ssh @SshCommandOptions $target $remote
        if ($LASTEXITCODE -ne 0) { throw "Failed to launch overnight scout on $($vm.name)" }
    }
    finally {
        Remove-Item -Force $tmp -ErrorAction SilentlyContinue
    }
    $shardIndex += 1
}

Write-Host "Overnight QAE/HHL scout handoff launched on $($vms.Count) VM(s)." -ForegroundColor Green
