from __future__ import annotations

import argparse
import json
import shutil
import stat
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


BUNDLE_DIR = Path(__file__).resolve().parent
MANIFEST = BUNDLE_DIR / "manifest.json"
LOG_DIR = BUNDLE_DIR / "monitor_logs"
LATEST_MD = LOG_DIR / "latest.md"
HISTORY_JSONL = LOG_DIR / "history.jsonl"
HELPER_STATE = LOG_DIR / "helper_state.json"
HELPER_SYNC_DIR = LOG_DIR / "helper_sync"
EXPECTED_PER_LABEL = 36

SSH_OPTIONS = [
    "-o",
    "StrictHostKeyChecking=no",
    "-o",
    "BatchMode=yes",
    "-o",
    "ConnectTimeout=20",
]


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def run_ssh(target: str, remote: str, timeout: int = 45) -> tuple[int, str, str]:
    proc = subprocess.run(
        ["ssh", "-n", *SSH_OPTIONS, target, remote],
        text=True,
        encoding="utf-8",
        errors="replace",
        capture_output=True,
        timeout=timeout,
    )
    return proc.returncode, proc.stdout, proc.stderr


def run_scp(args: list[str], timeout: int = 120) -> tuple[int, str, str]:
    proc = subprocess.run(
        ["scp", *SSH_OPTIONS, *args],
        text=True,
        encoding="utf-8",
        errors="replace",
        capture_output=True,
        timeout=timeout,
    )
    return proc.returncode, proc.stdout, proc.stderr


def parse_kv(text: str) -> dict[str, str]:
    out: dict[str, str] = {}
    for line in text.splitlines():
        if "=" in line:
            key, value = line.split("=", 1)
            out[key.strip()] = value.strip()
    return out


def vm_target(vm: dict[str, Any], admin_user: str) -> str:
    return f"{admin_user}@{vm['publicIp']}"


def load_helper_state() -> dict[str, Any]:
    if not HELPER_STATE.exists():
        return {"assignments": []}
    try:
        state = json.loads(HELPER_STATE.read_text(encoding="utf-8"))
    except Exception:
        return {"assignments": []}
    if not isinstance(state, dict):
        return {"assignments": []}
    state.setdefault("assignments", [])
    return state


def save_helper_state(state: dict[str, Any]) -> None:
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    HELPER_STATE.write_text(json.dumps(state, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def remove_tree(path: Path) -> None:
    if not path.exists():
        return
    for child in sorted(path.rglob("*"), reverse=True):
        try:
            child.chmod(stat.S_IREAD | stat.S_IWRITE | stat.S_IEXEC)
        except OSError:
            pass
    try:
        path.chmod(stat.S_IREAD | stat.S_IWRITE | stat.S_IEXEC)
    except OSError:
        pass
    shutil.rmtree(path)


def fresh_sync_dir(path: Path) -> Path:
    if path.exists():
        try:
            remove_tree(path)
        except OSError:
            stamp = utc_now().replace(":", "").replace("-", "")
            path = path.with_name(f"{path.name}_{stamp}")
    path.mkdir(parents=True, exist_ok=True)
    return path


def label_counts_on_vm(vm: dict[str, Any], labels: list[str], admin_user: str) -> dict[str, int]:
    if not labels:
        return {}
    labels_shell = " ".join(labels)
    remote = f"""
set +e
. "$HOME/phase8_6vm.env" 2>/dev/null || true
RUN_ROOT="${{PHASE8_RUN_ROOT:-$HOME/qf-phase8-20260425}}"
RESULT_DIR="$RUN_ROOT/quantum-finance/p4_experiments/common/output/results"
for L in {labels_shell}; do
    C=$(find "$RESULT_DIR" -maxdepth 1 -name "${{L}}_*_eps*.json" 2>/dev/null | wc -l | tr -d ' ')
    echo LABEL_COUNT_${{L}}=$C
done
"""
    try:
        exit_code, stdout, _stderr = run_ssh(vm_target(vm, admin_user), remote)
    except subprocess.TimeoutExpired:
        return {}
    if exit_code != 0:
        return {}
    fields = parse_kv(stdout)
    return {label: int(fields.get(f"LABEL_COUNT_{label}", "0") or "0") for label in labels}


def probe_vm(vm: dict[str, Any], admin_user: str, recover: bool) -> dict[str, Any]:
    target = vm_target(vm, admin_user)
    recover_flag = "1" if recover else "0"
    labels_shell = " ".join(vm["labels"])
    remote = f"""
set +e
RECOVER={recover_flag}
. "$HOME/phase8_6vm.env" 2>/dev/null || true
RUN_ROOT="${{PHASE8_RUN_ROOT:-$HOME/qf-phase8-20260425}}"
REPO="$RUN_ROOT/quantum-finance"
RESULT_DIR="$REPO/p4_experiments/common/output/results"
EXPECTED="${{PHASE8_EXPECTED_CELLS:-{vm['expected_cells']}}}"
TOTAL_RESULTS=$(find "$RESULT_DIR" -maxdepth 1 -name '*.json' 2>/dev/null | wc -l | tr -d ' ')
RESULTS=0
for L in {labels_shell}; do
    C=$(find "$RESULT_DIR" -maxdepth 1 -name "${{L}}_*_eps*.json" 2>/dev/null | wc -l | tr -d ' ')
    RESULTS=$((RESULTS + C))
    echo LABEL_COUNT_${{L}}=$C
done
RUNNING=$(ps -eo args | grep '[p]ython.*p4_experiments.canonical.phase8_big_run' | wc -l | tr -d ' ')
UNIT_RUNNING=$(ps -eo args | grep '[p]ython.*p4_experiments.common.run_unit' | wc -l | tr -d ' ')
ACTION=none
NEW_PID=
if [ "$RESULTS" -ge "$EXPECTED" ]; then
    if [ "$RUNNING" -gt 0 ]; then
        STATUS=helper_running
    else
        STATUS=complete
    fi
elif [ "$RUNNING" -gt 0 ]; then
    STATUS=running
elif [ "$RECOVER" = "1" ]; then
    STATUS=relaunching
    STAMP=$(date -u +%Y%m%dT%H%M%SZ)
    mkdir -p "$RUN_ROOT/logs"
    nohup bash "$RUN_ROOT/run_phase8.sh" > "$RUN_ROOT/logs/phase8_monitor_relaunch_$STAMP.log" 2>&1 < /dev/null &
    NEW_PID=$!
    ACTION=relaunched
else
    STATUS=stopped_incomplete
fi
LAST_LOG=$(ls -1t "$RUN_ROOT"/logs/run_*.log "$RUN_ROOT"/logs/phase8_nohup*.log "$RUN_ROOT"/logs/phase8_monitor_relaunch_*.log "$RUN_ROOT"/logs/phase8_helper_*.log 2>/dev/null | head -1)
LAST_LOG_MTIME=
if [ -n "$LAST_LOG" ]; then
    LAST_LOG_MTIME=$(stat -c %Y "$LAST_LOG" 2>/dev/null || true)
fi
echo VM_NAME=${{PHASE8_VM_NAME:-{vm['name']}}}
echo HOST=$(hostname)
echo STATUS=$STATUS
echo ACTION=$ACTION
echo NEW_PID=$NEW_PID
echo EXPECTED=$EXPECTED
echo RESULTS=$RESULTS
echo TOTAL_RESULTS=$TOTAL_RESULTS
echo RUNNING=$RUNNING
echo UNIT_RUNNING=$UNIT_RUNNING
echo LAST_LOG=$LAST_LOG
echo LAST_LOG_MTIME=$LAST_LOG_MTIME
"""
    try:
        exit_code, stdout, stderr = run_ssh(target, remote)
    except subprocess.TimeoutExpired as exc:
        return {
            "name": vm["name"],
            "publicIp": vm["publicIp"],
            "expected": vm["expected_cells"],
            "status": "ssh_timeout",
            "action": "none",
            "error": str(exc),
            "checked_at": utc_now(),
        }

    fields = parse_kv(stdout)
    expected = int(fields.get("EXPECTED", vm["expected_cells"]))
    results = int(fields.get("RESULTS", "0") or "0")
    total_results = int(fields.get("TOTAL_RESULTS", "0") or "0")
    running = int(fields.get("RUNNING", "0") or "0")
    unit_running = int(fields.get("UNIT_RUNNING", "0") or "0")
    label_counts = {label: int(fields.get(f"LABEL_COUNT_{label}", "0") or "0") for label in vm["labels"]}
    return {
        "name": vm["name"],
        "location": vm["location"],
        "publicIp": vm["publicIp"],
        "expected": expected,
        "results": results,
        "total_results": total_results,
        "label_counts": label_counts,
        "remaining": max(expected - results, 0),
        "running": running,
        "unit_running": unit_running,
        "status": fields.get("STATUS", "unknown") if exit_code == 0 else "ssh_error",
        "action": fields.get("ACTION", "none"),
        "new_pid": fields.get("NEW_PID", ""),
        "last_log": fields.get("LAST_LOG", ""),
        "last_log_mtime": fields.get("LAST_LOG_MTIME", ""),
        "ssh_exit": exit_code,
        "stderr": stderr.strip(),
        "checked_at": utc_now(),
    }


def sync_assignment(assignment: dict[str, Any], vm_by_name: dict[str, dict[str, Any]], admin_user: str) -> dict[str, Any]:
    helper = vm_by_name[assignment["helper"]]
    owner = vm_by_name[assignment["owner"]]
    labels = list(assignment["labels"])
    assignment_id = assignment["id"]
    local_root = HELPER_SYNC_DIR / assignment_id
    local_root.mkdir(parents=True, exist_ok=True)
    synced = 0
    errors: list[str] = []

    owner_target = vm_target(owner, admin_user)
    helper_target = vm_target(helper, admin_user)
    owner_prepare = """
set -e
. "$HOME/phase8_6vm.env" 2>/dev/null || true
RUN_ROOT="${PHASE8_RUN_ROOT:-$HOME/qf-phase8-20260425}"
mkdir -p "$RUN_ROOT/quantum-finance/p4_experiments/common/output/results" "$RUN_ROOT/helper_sync_inbox"
"""
    try:
        run_ssh(owner_target, owner_prepare, timeout=30)
    except subprocess.TimeoutExpired:
        errors.append("owner_prepare_timeout")
        return {"synced": synced, "errors": errors}

    for label in labels:
        label_dir = fresh_sync_dir(local_root / label)
        remote_glob = (
            f"{helper_target}:~/qf-phase8-20260425/quantum-finance/"
            f"p4_experiments/common/output/results/{label}_*_eps*.json"
        )
        try:
            exit_code, _stdout, stderr = run_scp([remote_glob, str(label_dir)], timeout=120)
        except subprocess.TimeoutExpired:
            errors.append(f"{label}:scp_from_helper_timeout")
            continue
        if exit_code != 0:
            if "No such file" not in stderr and "not found" not in stderr:
                errors.append(f"{label}:scp_from_helper_exit_{exit_code}")
            continue
        files = sorted(label_dir.glob("*.json"))
        if not files:
            continue
        owner_dest = f"{owner_target}:~/qf-phase8-20260425/quantum-finance/p4_experiments/common/output/results/"
        try:
            exit_code, _stdout, stderr = run_scp([*(str(path) for path in files), owner_dest], timeout=120)
        except subprocess.TimeoutExpired:
            errors.append(f"{label}:scp_to_owner_timeout")
            continue
        if exit_code != 0:
            errors.append(f"{label}:scp_to_owner_exit_{exit_code}:{stderr.strip()[:120]}")
            continue
        synced += len(files)
    return {"synced": synced, "errors": errors}


def launch_helper(helper: dict[str, Any], owner: dict[str, Any], labels: list[str], admin_user: str) -> dict[str, Any]:
    labels_csv = ",".join(labels)
    owner_name = owner["name"]
    script_name = f"run_phase8_helper_for_{owner_name}.sh"
    remote = f"""
set -Eeuo pipefail
. "$HOME/phase8_6vm.env" 2>/dev/null || true
RUN_ROOT="${{PHASE8_RUN_ROOT:-$HOME/qf-phase8-20260425}}"
LOG_DIR="$RUN_ROOT/logs"
mkdir -p "$LOG_DIR" "$RUN_ROOT/quantum-finance/p4_experiments/common/output/results" "$RUN_ROOT/quantum-finance/p4_experiments/common/output/phase8_logs"
cat > "$RUN_ROOT/{script_name}" <<'RUNHELPER'
#!/usr/bin/env bash
set -Eeuo pipefail
HELPER_LABELS="$1"
HELPER_OWNER="$2"
source "$HOME/phase8_6vm.env"
RUN_ROOT="${{PHASE8_RUN_ROOT:-$HOME/qf-phase8-20260425}}"
REPO="$RUN_ROOT/quantum-finance"
VENV="$RUN_ROOT/.venv"
LOG_DIR="$RUN_ROOT/logs"
mkdir -p "$LOG_DIR" "$REPO/p4_experiments/common/output/results" "$REPO/p4_experiments/common/output/phase8_logs"
source "$VENV/bin/activate"
cd "$REPO"
export PYTHONHASHSEED="${{PYTHONHASHSEED:-0}}"
export PYTHONIOENCODING="${{PYTHONIOENCODING:-utf-8}}"
export P4_CELL_TIMEOUT_S="${{P4_CELL_TIMEOUT_S:-7200}}"
export P4_FIRST_CELL_TIMEOUT_S="${{P4_FIRST_CELL_TIMEOUT_S:-7200}}"
export P4_TI_BARE_TIMEOUT_S="${{P4_TI_BARE_TIMEOUT_S:-7200}}"
export OMP_NUM_THREADS="${{OMP_NUM_THREADS:-1}}"
export MKL_NUM_THREADS="${{MKL_NUM_THREADS:-1}}"
export OPENBLAS_NUM_THREADS="${{OPENBLAS_NUM_THREADS:-1}}"
export NUMEXPR_NUM_THREADS="${{NUMEXPR_NUM_THREADS:-1}}"
STAMP=$(date -u +%Y%m%dT%H%M%SZ)
LOG="$LOG_DIR/phase8_helper_${{PHASE8_VM_NAME}}_for_${{HELPER_OWNER}}_$STAMP.log"
echo "=== Phase 8 helper start: ${{PHASE8_VM_NAME}} for ${{HELPER_OWNER}} $(date -u +%FT%TZ) ===" | tee "$LOG"
echo "helper_labels=$HELPER_LABELS" | tee -a "$LOG"
echo "timeouts P4_CELL_TIMEOUT_S=$P4_CELL_TIMEOUT_S P4_FIRST_CELL_TIMEOUT_S=$P4_FIRST_CELL_TIMEOUT_S P4_TI_BARE_TIMEOUT_S=$P4_TI_BARE_TIMEOUT_S" | tee -a "$LOG"
python -u -m p4_experiments.canonical.phase8_big_run --labels "$HELPER_LABELS" --workers 1 2>&1 | tee -a "$LOG"
echo "=== Phase 8 helper end: ${{PHASE8_VM_NAME}} for ${{HELPER_OWNER}} $(date -u +%FT%TZ) ===" | tee -a "$LOG"
RUNHELPER
chmod +x "$RUN_ROOT/{script_name}"
STAMP=$(date -u +%Y%m%dT%H%M%SZ)
nohup "$RUN_ROOT/{script_name}" "{labels_csv}" "{owner_name}" > "$LOG_DIR/phase8_helper_launcher_{owner_name}_$STAMP.out" 2>&1 < /dev/null &
echo NEW_PID=$!
"""
    try:
        exit_code, stdout, stderr = run_ssh(vm_target(helper, admin_user), remote, timeout=45)
    except subprocess.TimeoutExpired:
        return {"ok": False, "error": "launch_timeout", "pid": ""}
    fields = parse_kv(stdout)
    return {"ok": exit_code == 0, "error": stderr.strip(), "pid": fields.get("NEW_PID", "")}


def manage_helpers(
    rows: list[dict[str, Any]],
    manifest: dict[str, Any],
    admin_user: str,
    enable_helpers: bool,
    labels_per_run: int,
) -> dict[str, Any]:
    state = load_helper_state()
    events: list[str] = []
    if not enable_helpers:
        state["last_helper_check_utc"] = utc_now()
        state["enabled"] = False
        save_helper_state(state)
        return {"state": state, "events": events}

    vm_by_name = {vm["name"]: vm for vm in manifest["vms"]}
    row_by_name = {row["name"]: row for row in rows}

    for assignment in state.get("assignments", []):
        if assignment.get("status") == "complete":
            continue
        sync_info = sync_assignment(assignment, vm_by_name, admin_user)
        assignment["last_sync_utc"] = utc_now()
        assignment["last_sync_files"] = sync_info["synced"]
        assignment["last_sync_errors"] = sync_info["errors"]
        owner_counts = label_counts_on_vm(vm_by_name[assignment["owner"]], assignment["labels"], admin_user)
        assignment["owner_counts"] = owner_counts
        if owner_counts and all(owner_counts.get(label, 0) >= EXPECTED_PER_LABEL for label in assignment["labels"]):
            assignment["status"] = "complete"
            assignment["completed_utc"] = utc_now()
            events.append(f"complete {assignment['helper']} -> {assignment['owner']} labels={','.join(assignment['labels'])}")
            continue
        helper_row = row_by_name.get(assignment["helper"], {})
        if helper_row.get("running", 0) == 0:
            launch = launch_helper(vm_by_name[assignment["helper"]], vm_by_name[assignment["owner"]], assignment["labels"], admin_user)
            assignment["status"] = "running" if launch["ok"] else "launch_failed"
            assignment["last_launch_utc"] = utc_now()
            assignment["last_pid"] = launch.get("pid", "")
            assignment["launch_error"] = launch.get("error", "")
            events.append(f"relaunch {assignment['helper']} -> {assignment['owner']} labels={','.join(assignment['labels'])} pid={assignment['last_pid']}")
        else:
            assignment["status"] = "running"
            assignment["launch_error"] = ""

    active_labels = {
        label
        for assignment in state.get("assignments", [])
        if assignment.get("status") != "complete"
        for label in assignment.get("labels", [])
    }
    idle_helpers = [
        row for row in rows
        if row.get("results", 0) >= row.get("expected", 0) and row.get("running", 0) == 0
    ]
    donor_groups: list[dict[str, Any]] = []
    for row in sorted(rows, key=lambda item: item.get("remaining", 0), reverse=True):
        if row.get("remaining", 0) <= 0:
            continue
        vm = vm_by_name[row["name"]]
        labels = [
            label for label in reversed(vm["labels"])
            if row.get("label_counts", {}).get(label, 0) == 0 and label not in active_labels
        ]
        if labels:
            donor_groups.append({"owner": row["name"], "labels": labels})

    donor_cursor = 0
    for helper_row in idle_helpers:
        helper_name = helper_row["name"]
        if any(a.get("helper") == helper_name and a.get("status") != "complete" for a in state.get("assignments", [])):
            continue
        if not donor_groups:
            break
        picked: dict[str, Any] | None = None
        for _ in range(len(donor_groups)):
            group = donor_groups[donor_cursor % len(donor_groups)]
            donor_cursor += 1
            if group["owner"] == helper_name:
                continue
            labels = [label for label in group["labels"] if label not in active_labels]
            if labels:
                picked = {"owner": group["owner"], "labels": labels[:labels_per_run]}
                group["labels"] = [label for label in group["labels"] if label not in picked["labels"]]
                break
        if not picked:
            continue
        labels = picked["labels"]
        assignment = {
            "id": f"{utc_now().replace(':', '').replace('-', '')}_{helper_name}_for_{picked['owner']}_{'_'.join(labels)}",
            "helper": helper_name,
            "owner": picked["owner"],
            "labels": labels,
            "status": "launching",
            "created_utc": utc_now(),
        }
        launch = launch_helper(vm_by_name[helper_name], vm_by_name[picked["owner"]], labels, admin_user)
        assignment["status"] = "running" if launch["ok"] else "launch_failed"
        assignment["last_launch_utc"] = utc_now()
        assignment["last_pid"] = launch.get("pid", "")
        assignment["launch_error"] = launch.get("error", "")
        state.setdefault("assignments", []).append(assignment)
        active_labels.update(labels)
        events.append(f"launch {helper_name} -> {picked['owner']} labels={','.join(labels)} pid={assignment['last_pid']}")

    state["last_helper_check_utc"] = utc_now()
    state["enabled"] = True
    save_helper_state(state)
    return {"state": state, "events": events}


def write_logs(rows: list[dict[str, Any]], recover: bool, helpers: dict[str, Any]) -> None:
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    checked_at = utc_now()
    total_expected = sum(row.get("expected", 0) for row in rows)
    total_results = sum(row.get("results", 0) for row in rows)
    summary = {
        "checked_at": checked_at,
        "recover": recover,
        "helpers": helpers,
        "total_expected": total_expected,
        "total_results": total_results,
        "total_remaining": max(total_expected - total_results, 0),
        "rows": rows,
    }
    with HISTORY_JSONL.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(summary, sort_keys=True) + "\n")

    lines = [
        f"# Phase 8 VM Monitor - {checked_at}",
        "",
        f"Recover mode: `{recover}`",
        f"Helper mode: `{helpers.get('state', {}).get('enabled', False)}`",
        f"Total: `{total_results}/{total_expected}` results, `{max(total_expected - total_results, 0)}` remaining.",
        "",
        "| VM | Status | Owned Results | Total Results | Running | Unit | Action |",
        "|---|---:|---:|---:|---:|---:|---|",
    ]
    for row in rows:
        lines.append(
            "| {name} | {status} | {results}/{expected} | {total_results} | {running} | {unit_running} | {action}{pid} |".format(
                name=row["name"],
                status=row.get("status", "unknown"),
                results=row.get("results", 0),
                expected=row.get("expected", 0),
                total_results=row.get("total_results", row.get("results", 0)),
                running=row.get("running", 0),
                unit_running=row.get("unit_running", 0),
                action=row.get("action", "none"),
                pid=f" pid={row['new_pid']}" if row.get("new_pid") else "",
            )
        )
    events = helpers.get("events") or []
    if events:
        lines.extend(["", "## Helper Events"])
        lines.extend(f"- {event}" for event in events)
    active = [a for a in helpers.get("state", {}).get("assignments", []) if a.get("status") != "complete"]
    if active:
        lines.extend(["", "## Active Helpers", "", "| Helper | Owner | Labels | Status | PID |", "|---|---|---|---:|---:|"])
        for assignment in active:
            lines.append(
                "| {helper} | {owner} | {labels} | {status} | {pid} |".format(
                    helper=assignment.get("helper", ""),
                    owner=assignment.get("owner", ""),
                    labels=",".join(assignment.get("labels", [])),
                    status=assignment.get("status", ""),
                    pid=assignment.get("last_pid", ""),
                )
            )
    LATEST_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Probe and optionally relaunch six-VM Phase 8 shards.")
    parser.add_argument("--admin-user", default="azureuser")
    parser.add_argument("--recover", action="store_true", help="Relaunch stopped incomplete shards.")
    parser.add_argument("--helpers", action="store_true", help="Use completed idle VMs as helper shards for untouched labels on incomplete VMs.")
    parser.add_argument("--helper-labels-per-run", type=int, default=2)
    args = parser.parse_args()

    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    rows = [probe_vm(vm, args.admin_user, args.recover) for vm in manifest["vms"]]
    helpers = manage_helpers(rows, manifest, args.admin_user, args.helpers, max(1, args.helper_labels_per_run))
    if args.helpers or helpers.get("events"):
        rows = [probe_vm(vm, args.admin_user, args.recover) for vm in manifest["vms"]]
    write_logs(rows, args.recover, helpers)

    total_expected = sum(row.get("expected", 0) for row in rows)
    total_results = sum(row.get("results", 0) for row in rows)
    print(f"Phase 8 monitor: {total_results}/{total_expected} owned results; recover={args.recover} helpers={args.helpers}")
    for row in rows:
        print(
            f"{row['name']}: {row.get('status')} {row.get('results', 0)}/{row.get('expected', 0)} "
            f"total={row.get('total_results', row.get('results', 0))} running={row.get('running', 0)} "
            f"unit={row.get('unit_running', 0)} action={row.get('action', 'none')}"
        )
    for event in helpers.get("events", []):
        print(f"helper: {event}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())