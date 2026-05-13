param(
    [string]$AdminUser = 'azureuser',
    [int]$TimeoutSeconds = 36000,
    [switch]$NoCleanRemoteResults
)

$ErrorActionPreference = 'Stop'

$BundleDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$RepoRoot = Resolve-Path (Join-Path $BundleDir '..\..')
$ResultDir = Join-Path $RepoRoot 'p4_experiments\canonical\outputs\phase08d_qae_hhl_scout\results'
$SshOptions = @('-o', 'StrictHostKeyChecking=no', '-o', 'BatchMode=yes', '-o', 'ConnectTimeout=20')
$SshCommandOptions = @('-n') + $SshOptions
$Utf8NoBom = [System.Text.UTF8Encoding]::new($false)

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

if (-not (Test-Path $ResultDir)) {
    throw "Result directory not found: $ResultDir"
}

$Failed = Get-ChildItem $ResultDir -Filter '*.json' | ForEach-Object {
    $record = Get-Content $_.FullName -Raw | ConvertFrom-Json
    if ($record.status -ne 'engine_failure') { return }
    $match = [regex]::Match($_.Name, '^(?<entity>.+)__N(?<n>\d+)__m(?<m>\d+)__(?<profile>.+)__eps(?<eps>.+)\.json$')
    if (-not $match.Success) { throw "Could not parse result filename: $($_.Name)" }
    $entity = $match.Groups['entity'].Value
    $n = [int]$match.Groups['n'].Value
    $precision = [int]$match.Groups['m'].Value
    $profile = $match.Groups['profile'].Value
    $epsilon = $match.Groups['eps'].Value
    $multiplier = 1.0
    if ($entity -eq 'hhl_s2_fixed_m') {
        $multiplier = 2.0
    } elseif ($entity -eq 'qae_simmc_fixed_m') {
        $multiplier = 1.5
    }
    [pscustomobject]@{
        file = $_.Name
        entity = $entity
        n = $n
        m = $precision
        profile = $profile
        epsilon = $epsilon
        weight = [int]($n * [Math]::Pow(2, $precision) * $multiplier)
    }
}

$Failed = @($Failed)
if ($Failed.Count -eq 0) {
    throw 'No local engine_failure scout records found to rerun.'
}

$VmNames = @($Vms | ForEach-Object { $_.name })
$Loads = @{}
$Assignments = @{}
foreach ($name in $VmNames) {
    $Loads[$name] = 0
    $Assignments[$name] = New-Object System.Collections.Generic.List[object]
}

foreach ($cell in ($Failed | Sort-Object weight -Descending)) {
    $targetName = $VmNames | Sort-Object { $Loads[$_] } | Select-Object -First 1
    $Assignments[$targetName].Add($cell)
    $Loads[$targetName] += $cell.weight
}

Write-Host "Failed cells selected: $($Failed.Count)" -ForegroundColor Cyan
foreach ($vm in $Vms) {
    Write-Host ("{0}: cells={1} load={2}" -f $vm.name, $Assignments[$vm.name].Count, $Loads[$vm.name])
}

foreach ($vm in $Vms) {
    $target = "$AdminUser@$($vm.ip)"
    Write-Host "--- Checking setup on $($vm.name) $($vm.location) ---" -ForegroundColor Cyan
    $status = (& ssh @SshCommandOptions $target 'cat ~/qf-phase8-20260425/setup_status.txt 2>/dev/null || echo missing') -join "`n"
    if ($status.Trim() -ne 'setup_complete') {
        throw "$($vm.name) setup is not complete: $status"
    }

    $cleanLine = if ($NoCleanRemoteResults) { ':' } else { 'rm -f "$RESULT_DIR"/*.json' }
    $cellJsonItems = foreach ($cell in $Assignments[$vm.name]) {
        [pscustomobject]@{
            entity = $cell.entity
            n = $cell.n
            m = $cell.m
            profile = $cell.profile
            epsilon = $cell.epsilon
        } | ConvertTo-Json -Compress
    }
    $cellsJson = '[' + ($cellJsonItems -join ',') + ']'

    $remoteScript = @'
#!/usr/bin/env bash
set -uo pipefail
source "$HOME/phase8_6vm.env"
RUN_ROOT="${PHASE8_RUN_ROOT:-$HOME/qf-phase8-20260425}"
REPO="$RUN_ROOT/quantum-finance"
VENV="$RUN_ROOT/.venv"
LOG_DIR="$RUN_ROOT/logs"
RESULT_DIR="$REPO/p4_experiments/canonical/outputs/phase08d_qae_hhl_scout/results"
CELLS_JSON="$RUN_ROOT/failed_cells___VM_NAME__.json"
mkdir -p "$LOG_DIR" "$RESULT_DIR"
__CLEAN_LINE__
source "$VENV/bin/activate"
cd "$REPO"
export PYTHONHASHSEED="${PYTHONHASHSEED:-0}"
export PYTHONIOENCODING="${PYTHONIOENCODING:-utf-8}"
export P4_SCOUT_CELL_TIMEOUT_S="__TIMEOUT_SECONDS__"
export OMP_NUM_THREADS="${OMP_NUM_THREADS:-1}"
export MKL_NUM_THREADS="${MKL_NUM_THREADS:-1}"
export OPENBLAS_NUM_THREADS="${OPENBLAS_NUM_THREADS:-1}"
export NUMEXPR_NUM_THREADS="${NUMEXPR_NUM_THREADS:-1}"
LOG="$LOG_DIR/qae_hhl_failed___VM_NAME___$(date -u +%Y%m%dT%H%M%SZ).log"
echo "=== failed-cell rerun start __VM_NAME__ $(date -u +%FT%TZ) ===" | tee -a "$LOG"
python -u - "$CELLS_JSON" <<'PY' 2>&1 | tee -a "$LOG"
import json
import os
import sys
import time
from pathlib import Path

from p4_experiments.canonical.phase8d_qae_hhl_scout import _run_cell_subprocess, summarize_results

cells_path = Path(sys.argv[1])
cells = json.loads(cells_path.read_text(encoding="utf-8"))
timeout_s = int(os.environ.get("P4_SCOUT_CELL_TIMEOUT_S", "36000"))
counts = {"ok": 0, "engine_failure": 0, "timeout": 0, "missing": 0, "other": 0}
started = time.perf_counter()
print(f"[deepcare failed rerun] cells={len(cells)} timeout_s={timeout_s}", flush=True)
for index, cell in enumerate(cells, start=1):
    entity = str(cell["entity"])
    n = int(cell["n"])
    precision = int(cell["m"])
    profile = str(cell["profile"])
    epsilon = float(cell["epsilon"])
    print(
        f"[deepcare failed rerun] cell {index}/{len(cells)} "
        f"{entity} N={n} m={precision} {profile} eps={epsilon:.0e}",
        flush=True,
    )
    rc = _run_cell_subprocess((entity, n, precision, profile, epsilon), timeout_s=timeout_s, force=True)
    print(f"[deepcare failed rerun] cell {index}/{len(cells)} rc={rc}", flush=True)

summary = summarize_results()
for row in summary.get("rows", []):
    status = str(row.get("status") or "other")
    if status not in counts:
        status = "other"
    counts[status] += 1
elapsed = time.perf_counter() - started
print(f"[deepcare failed rerun] done elapsed={elapsed:.1f}s counts={counts}", flush=True)
PY
echo "=== failed-cell rerun end __VM_NAME__ $(date -u +%FT%TZ) ===" | tee -a "$LOG"
exit 0
'@
    $remoteScript = $remoteScript.Replace('__VM_NAME__', $vm.name)
    $remoteScript = $remoteScript.Replace('__CLEAN_LINE__', $cleanLine)
    $remoteScript = $remoteScript.Replace('__TIMEOUT_SECONDS__', $TimeoutSeconds.ToString())
    $remoteScript = $remoteScript -replace "`r?`n", "`n"

    $tmp = New-TemporaryFile
    $tmpJson = New-TemporaryFile
    try {
        [System.IO.File]::WriteAllText($tmpJson.FullName, $cellsJson, $Utf8NoBom)
        [System.IO.File]::WriteAllText($tmp.FullName, $remoteScript, $Utf8NoBom)
        $remotePath = "~/qf-phase8-20260425/run_failed_cells_$($vm.name).sh"
        $remoteJsonPath = "~/qf-phase8-20260425/failed_cells_$($vm.name).json"
        Write-Host "--- Launching $($vm.name): cells=$($Assignments[$vm.name].Count) ---" -ForegroundColor Yellow
        & scp @SshOptions $tmpJson.FullName "${target}:$remoteJsonPath"
        if ($LASTEXITCODE -ne 0) { throw "scp JSON failed for $($vm.name)" }
        & scp @SshOptions $tmp.FullName "${target}:$remotePath"
        if ($LASTEXITCODE -ne 0) { throw "scp failed for $($vm.name)" }
        $remote = "chmod +x $remotePath; nohup bash $remotePath > ~/qf-phase8-20260425/logs/qae_hhl_failed_$($vm.name).nohup.log 2>&1 < /dev/null & echo failed_pid=`$!"
        & ssh @SshCommandOptions $target $remote
        if ($LASTEXITCODE -ne 0) { throw "ssh launch failed for $($vm.name)" }
    }
    finally {
        Remove-Item -Force $tmp.FullName -ErrorAction SilentlyContinue
        Remove-Item -Force $tmpJson.FullName -ErrorAction SilentlyContinue
    }
}

Write-Host 'Failed-cell reruns launched on all Deepcare FX4 VMs.' -ForegroundColor Green