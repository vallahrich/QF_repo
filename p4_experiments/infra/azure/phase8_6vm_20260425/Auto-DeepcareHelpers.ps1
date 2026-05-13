param(
    [string]$AdminUser = 'azureuser',
    [int]$TimeoutSeconds = 36000,
    [int]$MaxCellsPerHelper = 5,
    [switch]$DryRun
)

$ErrorActionPreference = 'Stop'

$BundleDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$LogDir = Join-Path $BundleDir 'monitor_logs'
$StatePath = Join-Path $LogDir 'deepcare_auto_helpers_latest.json'
$HistoryPath = Join-Path $LogDir 'deepcare_auto_helpers_history.jsonl'
$SshOptions = @('-o', 'StrictHostKeyChecking=no', '-o', 'BatchMode=yes', '-o', 'ConnectTimeout=20')
$SshCommandOptions = @('-n') + $SshOptions
$Utf8NoBom = [System.Text.UTF8Encoding]::new($false)
$Invariant = [System.Globalization.CultureInfo]::InvariantCulture

New-Item -ItemType Directory -Force -Path $LogDir | Out-Null

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

function Get-EpsilonKey {
    param([object]$Value)
    return ([double]$Value).ToString('R', $Invariant)
}

function Get-CellKey {
    param([object]$Cell)
    return '{0}|{1}|{2}|{3}|{4}' -f `
        $Cell.entity, `
        ([int]$Cell.n), `
        ([int]$Cell.m), `
        $Cell.profile, `
        (Get-EpsilonKey $Cell.epsilon)
}

function Get-CellWeight {
    param([object]$Cell)
    $multiplier = 1.0
    if ($Cell.entity -eq 'hhl_s2_fixed_m') {
        $multiplier = 2.0
    } elseif ($Cell.entity -eq 'qae_simmc_fixed_m') {
        $multiplier = 1.5
    }
    return [int](([int]$Cell.n) * [Math]::Pow(2, [int]$Cell.m) * $multiplier)
}

function Invoke-RemotePython {
    param(
        [object]$Vm,
        [string]$Code
    )
    $target = "$AdminUser@$($Vm.ip)"
    $output = $Code | & ssh @SshOptions $target python3 -
    if ($LASTEXITCODE -ne 0) {
        throw "remote python failed on $($Vm.name)"
    }
    return ($output -join "`n")
}

function Get-RemoteState {
    param([object]$Vm)

    $remote = @'
import json
import subprocess
from pathlib import Path

name = "__VM_NAME__"
run_root = Path.home() / "qf-phase8-20260425"
repo = run_root / "quantum-finance"
scout_root = repo / "p4_experiments" / "canonical" / "outputs" / "phase08d_qae_hhl_scout"
result_dir = scout_root / "results"

def read_json(path, default):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return default

def norm_cell(cell, owner=None, helper=None, source=None):
    return {
        "entity": str(cell.get("entity") or cell.get("entity_id")),
        "n": int(cell.get("n") if cell.get("n") is not None else cell.get("n_value")),
        "m": int(cell.get("m") if cell.get("m") is not None else cell.get("m_precision_qubits")),
        "profile": str(cell.get("profile") or cell.get("hardware_profile")),
        "epsilon": float(cell.get("epsilon")),
        "owner": owner or cell.get("owner"),
        "helper": helper,
        "source": source,
    }

def pgrep(pattern):
    proc = subprocess.run(
        ["pgrep", "-af", pattern],
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        text=True,
        check=False,
    )
    return [line for line in proc.stdout.splitlines() if line.strip()]

setup_status = "missing"
setup_path = run_root / "setup_status.txt"
if setup_path.exists():
    setup_status = setup_path.read_text(encoding="utf-8", errors="replace").strip()

processes = pgrep("phase8d_qae_hhl_scout|run_failed_cells|run_helper|helper_results|helper_cells|qae_hhl_helper")
owner_active = any(
    f"run_failed_cells_{name}" in line
    or ("-m p4_experiments.canonical.phase8d_qae_hhl_scout" in line and "--run-cell" in line)
    for line in processes
)
helper_active = any(
    f"run_helper_{name}" in line
    or f"helper_results_{name}" in line
    or f"helper_cells_{name}" in line
    or f"qae_hhl_helper_{name}" in line
    for line in processes
)

owner_assignments = []
for path in [run_root / f"failed_cells_{name}.json", run_root / f"failed_cells_{name}.json"]:
    payload = read_json(path, None)
    if isinstance(payload, list):
        owner_assignments = [norm_cell(cell, owner=name, source=path.name) for cell in payload]
        break

owner_results = []
for path in sorted(result_dir.glob("*.json")):
    rec = read_json(path, None)
    if not isinstance(rec, dict):
        continue
    try:
        cell = norm_cell(rec, owner=name, source=path.name)
    except Exception:
        continue
    cell["status"] = rec.get("status")
    cell["reason"] = rec.get("reason")
    owner_results.append(cell)

helper_assignments = []
for path in sorted(run_root.glob("helper_cells_*.json")):
    payload = read_json(path, None)
    if not isinstance(payload, list):
        continue
    helper = path.stem.replace("helper_cells_", "", 1)
    for cell in payload:
        try:
            helper_assignments.append(norm_cell(cell, owner=cell.get("owner"), helper=helper, source=path.name))
        except Exception:
            pass

helper_results = []
for directory in sorted(scout_root.glob("helper_results_*")):
    if not directory.is_dir():
        continue
    helper = directory.name.replace("helper_results_", "", 1)
    for path in sorted(directory.glob("*.json")):
        rec = read_json(path, None)
        if not isinstance(rec, dict):
            continue
        try:
            cell = norm_cell(rec, helper=helper, source=path.name)
        except Exception:
            continue
        cell["status"] = rec.get("status")
        cell["reason"] = rec.get("reason")
        helper_results.append(cell)

print(json.dumps({
    "name": name,
    "setup_status": setup_status,
    "owner_active": owner_active,
    "helper_active": helper_active,
    "processes": processes,
    "owner_assignments": owner_assignments,
    "owner_results": owner_results,
    "helper_assignments": helper_assignments,
    "helper_results": helper_results,
}, sort_keys=True))
'@
    $remote = $remote.Replace('__VM_NAME__', $Vm.name)
    $json = Invoke-RemotePython -Vm $Vm -Code $remote
    return $json | ConvertFrom-Json
}

function New-RemoteHelperScript {
    param(
        [string]$HelperName,
        [string]$BatchId,
        [int]$CellTimeoutSeconds
    )

    $template = @'
#!/usr/bin/env bash
set -uo pipefail
source "$HOME/phase8_6vm.env"
RUN_ROOT="${PHASE8_RUN_ROOT:-$HOME/qf-phase8-20260425}"
REPO="$RUN_ROOT/quantum-finance"
VENV="$RUN_ROOT/.venv"
LOG_DIR="$RUN_ROOT/logs"
HELPER_NAME="__HELPER_NAME__"
BATCH_ID="__BATCH_ID__"
HELPER_DIR="$REPO/p4_experiments/canonical/outputs/phase08d_qae_hhl_scout/helper_results_${HELPER_NAME}_auto_${BATCH_ID}"
CELLS_JSON="$RUN_ROOT/helper_cells_${HELPER_NAME}_auto_${BATCH_ID}.json"
mkdir -p "$LOG_DIR" "$HELPER_DIR"
source "$VENV/bin/activate"
cd "$REPO"
export PYTHONHASHSEED="${PYTHONHASHSEED:-0}"
export PYTHONIOENCODING="${PYTHONIOENCODING:-utf-8}"
export P4_SCOUT_CELL_TIMEOUT_S="__TIMEOUT_SECONDS__"
export OMP_NUM_THREADS="${OMP_NUM_THREADS:-1}"
export MKL_NUM_THREADS="${MKL_NUM_THREADS:-1}"
export OPENBLAS_NUM_THREADS="${OPENBLAS_NUM_THREADS:-1}"
export NUMEXPR_NUM_THREADS="${NUMEXPR_NUM_THREADS:-1}"
LOG="$LOG_DIR/qae_hhl_helper_${HELPER_NAME}_auto_${BATCH_ID}_$(date -u +%Y%m%dT%H%M%SZ).log"
echo "=== auto helper start $HELPER_NAME batch=$BATCH_ID $(date -u +%FT%TZ) ===" | tee -a "$LOG"
python -u - "$CELLS_JSON" "$HELPER_DIR" <<'PY' 2>&1 | tee -a "$LOG"
import json
import os
import subprocess
import sys
import time
from pathlib import Path

from p4_experiments.canonical import phase8d_qae_hhl_scout as scout

cells_path = Path(sys.argv[1])
helper_dir = Path(sys.argv[2])
helper_dir.mkdir(parents=True, exist_ok=True)
scout.RESULTS_DIR = helper_dir
cells = json.loads(cells_path.read_text(encoding="utf-8"))
timeout_s = int(os.environ.get("P4_SCOUT_CELL_TIMEOUT_S", "36000"))
cell_runner = r'''
import json
import sys
from pathlib import Path
from p4_experiments.canonical import phase8d_qae_hhl_scout as scout
helper_dir = Path(sys.argv[1])
entity = sys.argv[2]
n = int(sys.argv[3])
m = int(sys.argv[4])
profile = sys.argv[5]
eps = float(sys.argv[6])
scout.RESULTS_DIR = helper_dir
path = scout.run_one_cell(entity, n, m, profile, eps, force=True)
rec = json.loads(path.read_text(encoding="utf-8"))
raise SystemExit(0 if rec.get("status") == "ok" else 2)
'''
counts = {"ok": 0, "engine_failure": 0, "timeout": 0, "missing": 0, "other": 0}
started = time.perf_counter()
print(f"[auto helper] cells={len(cells)} helper_dir={helper_dir} timeout_s={timeout_s}", flush=True)
for index, cell in enumerate(cells, start=1):
    entity = str(cell["entity"])
    n = int(cell["n"])
    precision = int(cell["m"])
    profile = str(cell["profile"])
    epsilon = float(cell["epsilon"])
    owner = str(cell.get("owner") or "unknown")
    out = helper_dir / scout._record_filename(entity, n, precision, profile, epsilon)
    print(f"[auto helper] cell {index}/{len(cells)} owner={owner} {entity} N={n} m={precision} {profile} eps={epsilon:.0e}", flush=True)
    cell_started = time.perf_counter()
    try:
        completed = subprocess.run(
            [sys.executable, "-c", cell_runner, str(helper_dir), entity, str(n), str(precision), profile, str(epsilon)],
            timeout=timeout_s,
        )
        rc = int(completed.returncode)
        if rc != 0 and not scout._is_final_record(out):
            scout._child_failure_record(entity, n, precision, profile, epsilon, rc, time.perf_counter() - cell_started)
    except subprocess.TimeoutExpired:
        rc = 124
        scout._timeout_record(entity, n, precision, profile, epsilon, timeout_s)
    status = "missing"
    try:
        status = json.loads(out.read_text(encoding="utf-8")).get("status") or "other"
    except Exception:
        status = "missing"
    if status not in counts:
        status = "other"
    counts[status] += 1
    print(f"[auto helper] cell {index}/{len(cells)} rc={rc} status={status}", flush=True)
elapsed = time.perf_counter() - started
print(f"[auto helper] done elapsed={elapsed:.1f}s counts={counts}", flush=True)
PY
echo "=== auto helper end $HELPER_NAME batch=$BATCH_ID $(date -u +%FT%TZ) ===" | tee -a "$LOG"
exit 0
'@

    return $template.Replace('__HELPER_NAME__', $HelperName).Replace('__BATCH_ID__', $BatchId).Replace('__TIMEOUT_SECONDS__', $CellTimeoutSeconds.ToString())
}

function Start-HelperBatch {
    param(
        [object]$Vm,
        [object[]]$Cells,
        [string]$BatchId
    )

    $target = "$AdminUser@$($Vm.ip)"
    $remoteJsonPath = "~/qf-phase8-20260425/helper_cells_$($Vm.name)_auto_$BatchId.json"
    $remoteScriptPath = "~/qf-phase8-20260425/run_helper_$($Vm.name)_auto_$BatchId.sh"
    $remoteLogPath = "~/qf-phase8-20260425/logs/qae_hhl_helper_$($Vm.name)_auto_$BatchId.nohup.log"
    $cellsJson = @($Cells | ForEach-Object {
        [pscustomobject]@{
            entity = $_.entity
            n = [int]$_.n
            m = [int]$_.m
            profile = $_.profile
            epsilon = (Get-EpsilonKey $_.epsilon)
            owner = $_.owner
        }
    }) | ConvertTo-Json -Compress
    $script = New-RemoteHelperScript -HelperName $Vm.name -BatchId $BatchId -CellTimeoutSeconds $TimeoutSeconds

    if ($DryRun) {
        Write-Host "[dry-run] Would launch $($Vm.name) helper batch $BatchId with $(@($Cells).Count) cells" -ForegroundColor Yellow
        return [pscustomobject]@{ helper = $Vm.name; batch_id = $BatchId; cells = @($Cells).Count; dry_run = $true }
    }

    $tmpJson = New-TemporaryFile
    $tmpScript = New-TemporaryFile
    try {
        [System.IO.File]::WriteAllText($tmpJson.FullName, $cellsJson, $Utf8NoBom)
        $scriptLf = $script.Replace("`r`n", "`n").Replace("`r", "`n")
        [System.IO.File]::WriteAllText($tmpScript.FullName, $scriptLf, $Utf8NoBom)
        & scp @SshOptions $tmpJson.FullName "${target}:$remoteJsonPath"
        if ($LASTEXITCODE -ne 0) { throw "scp helper JSON failed for $($Vm.name)" }
        & scp @SshOptions $tmpScript.FullName "${target}:$remoteScriptPath"
        if ($LASTEXITCODE -ne 0) { throw "scp helper script failed for $($Vm.name)" }
        $remote = "chmod +x $remoteScriptPath; nohup bash $remoteScriptPath > $remoteLogPath 2>&1 < /dev/null & echo helper_pid=`$!"
        $pidLine = (& ssh @SshCommandOptions $target $remote) -join "`n"
        if ($LASTEXITCODE -ne 0) { throw "ssh launch failed for $($Vm.name)" }
        Write-Host "Launched helper $($Vm.name) batch $BatchId with $(@($Cells).Count) cells: $pidLine" -ForegroundColor Green
        return [pscustomobject]@{ helper = $Vm.name; batch_id = $BatchId; cells = @($Cells).Count; pid_line = $pidLine; dry_run = $false }
    }
    finally {
        Remove-Item -Force $tmpJson.FullName -ErrorAction SilentlyContinue
        Remove-Item -Force $tmpScript.FullName -ErrorAction SilentlyContinue
    }
}

$tsUtc = [DateTime]::UtcNow.ToString('o')
$batchId = [DateTime]::UtcNow.ToString('yyyyMMddTHHmmssZ')
Write-Host "[auto-helpers] scan $tsUtc" -ForegroundColor Cyan

$states = foreach ($vm in $Vms) {
    try {
        Get-RemoteState -Vm $vm
    }
    catch {
        Write-Warning "State probe failed for $($vm.name): $($_.Exception.Message)"
        [pscustomobject]@{
            name = $vm.name
            setup_status = 'probe_failed'
            owner_active = $true
            helper_active = $true
            error = $_.Exception.Message
            owner_assignments = @()
            owner_results = @()
            helper_assignments = @()
            helper_results = @()
        }
    }
}

$ownerCells = @{}
$ownerDone = @{}
$helperClaimed = @{}
$terminal = @('ok', 'engine_failure', 'timeout')
foreach ($state in $states) {
    foreach ($cell in @($state.owner_assignments)) {
        $key = Get-CellKey $cell
        if (-not $ownerCells.ContainsKey($key)) { $ownerCells[$key] = $cell }
    }
    foreach ($cell in @($state.owner_results)) {
        if ($terminal -contains [string]$cell.status) {
            $ownerDone[(Get-CellKey $cell)] = $true
        }
    }
    foreach ($cell in @($state.helper_assignments)) {
        if ($state.helper_active) {
            $helperClaimed[(Get-CellKey $cell)] = $true
        }
    }
    foreach ($cell in @($state.helper_results)) {
        $status = [string]$cell.status
        if (($terminal -contains $status) -or $state.helper_active) {
            $helperClaimed[(Get-CellKey $cell)] = $true
        }
    }
}

$availableHelpers = @($states | Where-Object {
    $_.setup_status -eq 'setup_complete' -and -not $_.owner_active -and -not $_.helper_active
})

$remaining = @($ownerCells.Values | Where-Object {
    $key = Get-CellKey $_
    -not $ownerDone.ContainsKey($key) -and -not $helperClaimed.ContainsKey($key)
} | Sort-Object @{ Expression = { Get-CellWeight $_ }; Descending = $true })

Write-Host "[auto-helpers] available helpers: $((@($availableHelpers | ForEach-Object { $_.name }) -join ', '))"
Write-Host "[auto-helpers] owner cells=$($ownerCells.Count) owner_done=$($ownerDone.Count) helper_claimed=$($helperClaimed.Count) remaining_unclaimed=$(@($remaining).Count)"

$launches = @()
$queue = New-Object System.Collections.Generic.List[object]
foreach ($cell in $remaining) { $queue.Add($cell) }

foreach ($state in $availableHelpers) {
    if ($queue.Count -eq 0) { break }
    $vm = $Vms | Where-Object { $_.name -eq $state.name } | Select-Object -First 1
    if (-not $vm) { continue }
    $takeCount = [Math]::Min($MaxCellsPerHelper, $queue.Count)
    $cells = @()
    for ($i = 0; $i -lt $takeCount; $i++) { $cells += $queue[$i] }
    for ($i = 0; $i -lt $takeCount; $i++) { $queue.RemoveAt(0) }
    $launches += Start-HelperBatch -Vm $vm -Cells $cells -BatchId $batchId
}

$statePayload = [pscustomobject]@{
    ts_utc = $tsUtc
    dry_run = [bool]$DryRun
    max_cells_per_helper = $MaxCellsPerHelper
    timeout_seconds = $TimeoutSeconds
    available_helpers = @($availableHelpers | ForEach-Object { $_.name })
    owner_cell_count = $ownerCells.Count
    owner_done_count = $ownerDone.Count
    helper_claimed_count = $helperClaimed.Count
    remaining_unclaimed_count = @($remaining).Count
    launches = $launches
}

$json = $statePayload | ConvertTo-Json -Depth 8
[System.IO.File]::WriteAllText($StatePath, $json + "`n", $Utf8NoBom)
[System.IO.File]::AppendAllText($HistoryPath, (($statePayload | ConvertTo-Json -Compress -Depth 8) + "`n"), $Utf8NoBom)

if (@($launches).Count -eq 0) {
    Write-Host '[auto-helpers] no helper batches launched this pass' -ForegroundColor Yellow
} else {
    Write-Host "[auto-helpers] launched $(@($launches).Count) helper batch(es)" -ForegroundColor Green
}
Write-Host "[auto-helpers] state -> $StatePath" -ForegroundColor Cyan