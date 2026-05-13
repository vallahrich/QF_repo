param(
    [ValidateSet('all')]
    [string]$Plan = 'all',
    [string]$AdminUser = 'azureuser',
    [int]$TimeoutSeconds = 36000,
    [int]$CheckIntervalSeconds = 300,
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

if (-not (Test-Path $ScoutModule)) { throw "Scout module not found: $ScoutModule" }
if (-not (Test-Path $SelectionManifest)) { throw "Selection manifest not found: $SelectionManifest" }

$vmNameList = @($VmNames -split '[,;]' | ForEach-Object { $_.Trim() } | Where-Object { $_ })
$vms = @()
foreach ($name in $vmNameList) {
    $vm = $Manifest.vms | Where-Object { $_.name -eq $name } | Select-Object -First 1
    if ($null -eq $vm) { throw "VM not found in manifest: $name" }
    $vms += $vm
}
if ($vms.Count -eq 0) { throw 'No VMs selected.' }

$shardCount = $vms.Count
$shardIndex = 0
foreach ($vm in $vms) {
    $target = "$AdminUser@$($vm.publicIp)"
    Write-Host "--- Preparing QAE/HHL supervisor on $($vm.name) shard=$shardIndex/$shardCount plan=$Plan ---" -ForegroundColor Cyan

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
PLAN="$Plan"
SHARD_INDEX="$shardIndex"
SHARD_COUNT="$shardCount"
TIMEOUT_SECONDS="$TimeoutSeconds"
CHECK_INTERVAL_SECONDS="$CheckIntervalSeconds"
LAUNCHER="`$RUN_ROOT/run_qae_hhl_scout_overnight_${Plan}_shard${shardIndex}.sh"
LOCK_DIR="`$RUN_ROOT/qae_hhl_scout_supervisor_${Plan}_shard${shardIndex}.lock"
SUPERVISOR_LOG="`$LOG_DIR/qae_hhl_scout_supervisor_${Plan}_$($vm.name)_`$(date -u +%Y%m%dT%H%M%SZ).log"
mkdir -p "`$LOG_DIR" "`$RESULT_DIR"
if mkdir "`$LOCK_DIR" 2>/dev/null; then
  echo "`$`$" > "`$LOCK_DIR/pid"
else
  existing_pid="`$(cat "`$LOCK_DIR/pid" 2>/dev/null || true)"
  if [ -n "`$existing_pid" ] && kill -0 "`$existing_pid" 2>/dev/null; then
    echo "[supervisor] already running pid=`$existing_pid"
    exit 0
  fi
  rm -rf "`$LOCK_DIR"
  mkdir "`$LOCK_DIR"
  echo "`$`$" > "`$LOCK_DIR/pid"
fi
trap 'rm -rf "`$LOCK_DIR"' EXIT
exec >> "`$SUPERVISOR_LOG" 2>&1
echo "[supervisor] started vm=$($vm.name) shard=`$SHARD_INDEX/`$SHARD_COUNT plan=`$PLAN interval=`$CHECK_INTERVAL_SECONDS timeout=`$TIMEOUT_SECONDS utc=`$(date -u +%Y-%m-%dT%H:%M:%SZ)"

source "`$VENV/bin/activate"
cd "`$REPO"
export PYTHONHASHSEED="`${PYTHONHASHSEED:-0}"
export PYTHONIOENCODING="`${PYTHONIOENCODING:-utf-8}"
export P4_SCOUT_CELL_TIMEOUT_S="`$TIMEOUT_SECONDS"
export OMP_NUM_THREADS="`${OMP_NUM_THREADS:-1}"
export MKL_NUM_THREADS="`${MKL_NUM_THREADS:-1}"
export OPENBLAS_NUM_THREADS="`${OPENBLAS_NUM_THREADS:-1}"
export NUMEXPR_NUM_THREADS="`${NUMEXPR_NUM_THREADS:-1}"

shard_done() {
  python - "`$PLAN" "`$SHARD_INDEX" "`$SHARD_COUNT" <<'PY'
import argparse
import json
import sys
from p4_experiments.canonical import phase8d_qae_hhl_scout as scout

plan, shard_index, shard_count = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
args = argparse.Namespace(
    plan=plan,
    entities=None,
    n_values=None,
    m_values=None,
    profiles=None,
    epsilons=None,
    shard_index=shard_index,
    shard_count=shard_count,
)
final = {"ok", "engine_failure", "timeout"}
missing = []
nonfinal = []
for cell in scout.build_plan(args):
    path = scout._record_path(*cell)
    if not path.exists():
        missing.append(path.name)
        continue
    try:
        status = json.loads(path.read_text(encoding="utf-8")).get("status")
    except Exception:
        status = "unreadable"
    if status not in final:
        nonfinal.append(f"{path.name}:{status}")
print(f"[supervisor] shard_check planned={len(scout.build_plan(args))} missing={len(missing)} nonfinal={len(nonfinal)}", flush=True)
if missing[:5]:
    print("[supervisor] missing_sample=" + ",".join(missing[:5]), flush=True)
if nonfinal[:5]:
    print("[supervisor] nonfinal_sample=" + ",".join(nonfinal[:5]), flush=True)
raise SystemExit(0 if not missing and not nonfinal else 2)
PY
}

while true; do
  if shard_done; then
    echo "[supervisor] shard complete; exiting utc=`$(date -u +%Y-%m-%dT%H:%M:%SZ)"
    exit 0
  fi

  if pgrep -af '[p]4_experiments.canonical.phase8d_qae_hhl_scout|[r]un_qae_hhl_scout_overnight_all|[r]un_qae_hhl_scout_canary' >/dev/null; then
    echo "[supervisor] active scout/handoff process present; next_check_seconds=`$CHECK_INTERVAL_SECONDS utc=`$(date -u +%Y-%m-%dT%H:%M:%SZ)"
  else
    echo "[supervisor] no active process and shard incomplete; relaunching utc=`$(date -u +%Y-%m-%dT%H:%M:%SZ)"
    if [ -x "`$LAUNCHER" ]; then
      nohup bash "`$LAUNCHER" > "`$LOG_DIR/qae_hhl_scout_supervisor_relaunch_${Plan}_shard${shardIndex}_`$(date -u +%Y%m%dT%H%M%SZ).nohup.log" 2>&1 < /dev/null &
      echo "[supervisor] relaunch_pid=`$!"
    else
      echo "[supervisor] missing launcher: `$LAUNCHER"
    fi
  fi
  sleep "`$CHECK_INTERVAL_SECONDS"
done
"@

    $tmp = New-TemporaryFile
    try {
        $utf8NoBom = [System.Text.UTF8Encoding]::new($false)
        [System.IO.File]::WriteAllText($tmp.FullName, ($remoteScript -replace "`r?`n", "`n"), $utf8NoBom)
        $remoteSupervisor = "~/qf-phase8-20260425/run_qae_hhl_scout_supervisor_${Plan}_shard${shardIndex}.sh"
        & scp @SshOptions $tmp "${target}:$remoteSupervisor"
        if ($LASTEXITCODE -ne 0) { throw "Failed to copy supervisor to $($vm.name)" }
        $remote = @'
supervisor="$HOME/qf-phase8-20260425/run_qae_hhl_scout_supervisor___PLAN___shard__SHARD__.sh"
log="$HOME/qf-phase8-20260425/logs/qae_hhl_scout_supervisor___PLAN___shard__SHARD__.nohup.log"
chmod +x "$supervisor"
nohup bash "$supervisor" > "$log" 2>&1 < /dev/null &
echo supervisor_pid=$!
'@
        $remote = $remote.Replace('__PLAN__', $Plan).Replace('__SHARD__', $shardIndex.ToString()) -replace "`r?`n", "`n"
        & ssh @SshCommandOptions $target $remote
        if ($LASTEXITCODE -ne 0) { throw "Failed to launch supervisor on $($vm.name)" }
    }
    finally {
        Remove-Item -Force $tmp -ErrorAction SilentlyContinue
    }
    $shardIndex += 1
}

Write-Host "QAE/HHL scout supervisors launched or confirmed on $($vms.Count) VM(s)." -ForegroundColor Green
