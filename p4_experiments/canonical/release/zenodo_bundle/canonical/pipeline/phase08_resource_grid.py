"""Phase 8 - Big run driver.

Walks the canonical cohort and invokes
``p4_experiments.core.run_unit.run_unit`` once per label. Each label
produces 6 profiles x 3 epsilon x 2 modes = 36 result records, for a
total of ``len(cohort["labels"]) * 36`` expected records in
``p4_experiments/common/output/results/``.

Operational properties:
  - Phase 6 wired ``_estimate_with_timeout`` (default 1800s per cell)
    so a stalled cell becomes a schema-valid ``engine_failure`` record
    instead of blocking the run.
  - The driver is **resumable**: if a record file already exists it is
    not re-run unless ``--force`` is passed. Resume is the default.
  - The driver writes ``cohort._phase_status.phase8`` with start/end
    timestamps, per-label exit code, total cells written, and a
    final breakdown of ``ok`` vs ``engine_failure`` records.
  - Per-label output is streamed; tee externally if you want a log file.

Usage:
    # Dry-run: list which labels would run
    python -m p4_experiments.canonical.pipeline.phase08_resource_grid --dry-run

    # Subset (debugging)
    python -m p4_experiments.canonical.pipeline.phase08_resource_grid --labels SD3,SQ17,B3

    # Full run (resumable; ~2-3 days)
    python -m p4_experiments.canonical.pipeline.phase08_resource_grid

    # Force re-run all cells (not recommended; loses prior records)
    python -m p4_experiments.canonical.pipeline.phase08_resource_grid --force

Output:
    Records go to p4_experiments/common/output/results/<unit_id>.json,
    one per (label, profile, eps, mode). Engine failures additionally
    appended to p4_experiments/common/output/results/_engine_failures.log.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
import traceback
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
CANON = ROOT / "p4_experiments" / "canonical"
COHORT = CANON / "cohort.json"
RESULTS = ROOT / "p4_experiments" / "common" / "output" / "results"
WORKER_LOGS = ROOT / "p4_experiments" / "common" / "output" / "phase8_logs"

EXPECTED_PER_LABEL = 6 * 3 * 2  # 36
EPSILONS = [1e-3, 1e-4, 1e-6]


def _existing_record_count_for(label: str) -> int:
    """Count files like ``<label>_<profile>_eps<eps>_<mode>.json``."""
    if not RESULTS.exists():
        return 0
    return len(list(RESULTS.glob(f"{label}_*_eps*_*.json")))


def _existing_record_count_total() -> int:
    """Count all result JSON files (excluding internal files like _engine_failures.log)."""
    if not RESULTS.exists():
        return 0
    return len([p for p in RESULTS.glob("*.json") if not p.name.startswith("_")])


def _engine_failure_breakdown() -> dict:
    """Scan all result files; return totals split by status."""
    if not RESULTS.exists():
        return {"total_records": 0, "ok": 0, "engine_failure": 0}
    n_ok = 0
    n_fail = 0
    n_total = 0
    for p in RESULTS.glob("*.json"):
        n_total += 1
        try:
            r = json.loads(p.read_text(encoding="utf-8"))
        except Exception:
            continue
        status = (r.get("measured") or {}).get("status")
        if status == "engine_failure":
            n_fail += 1
        else:
            n_ok += 1
    return {"total_records": n_total, "ok": n_ok, "engine_failure": n_fail}


def _record_phase_status(payload: dict) -> None:
    cohort = json.loads(COHORT.read_text(encoding="utf-8"))
    ps = cohort.get("_phase_status")
    if not isinstance(ps, dict):
        ps = {"_legacy": ps} if ps is not None else {}
    cur = ps.get("phase8") or {}
    cur.update(payload)
    ps["phase8"] = cur
    cohort["_phase_status"] = ps
    COHORT.write_text(json.dumps(cohort, indent=2), encoding="utf-8")


def _run_one_label(label: str) -> dict:
    """Worker entrypoint: import run_unit lazily and execute one label.

    Returns a per-label status dict identical in shape to the one the
    sequential driver produces.
    """
    from p4_experiments.core.run_unit import run_unit  # noqa: WPS433
    t0 = time.perf_counter()
    try:
        written = run_unit(label)
        return {
            "label": label,
            "status": "ok",
            "records_written": len(written),
            "wall_clock_seconds": round(time.perf_counter() - t0, 2),
        }
    except BaseException as exc:  # noqa: BLE001
        return {
            "label": label,
            "status": "driver_error",
            "error": f"{type(exc).__name__}: {exc}",
            "traceback": traceback.format_exc(),
            "wall_clock_seconds": round(time.perf_counter() - t0, 2),
        }


def _run_one_label_subprocess(label: str) -> dict:
    """Run a single label in a fully independent subprocess.

    Avoids the nested-multiprocessing crash on Windows that occurs when
    ProcessPoolExecutor workers each spawn multiprocessing.Process
    children for per-cell timeout isolation.
    """
    t0 = time.perf_counter()
    env = {**os.environ, "PYTHONHASHSEED": "0", "PYTHONIOENCODING": "utf-8"}
    WORKER_LOGS.mkdir(parents=True, exist_ok=True)
    log_path = WORKER_LOGS / f"{label}.log"
    proc = subprocess.Popen(
        [sys.executable, "-u", "-m", "p4_experiments.core.run_unit", label],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        env=env,
        cwd=str(ROOT),
    )
    # Stream output line-by-line so progress is visible immediately.
    # Also write to a per-label log file with line-buffered I/O so the
    # user can `Get-Content phase8_logs/<label>.log -Wait` to follow
    # any worker independently of the parent stdout buffering.
    lines = []
    with open(log_path, "w", encoding="utf-8", buffering=1, newline="\n") as logf:
        ts0 = datetime.now(timezone.utc).isoformat(timespec="seconds")
        logf.write(f"# Phase 8 worker log for label={label} started={ts0}\n")
        for raw_line in proc.stdout:
            line = raw_line.decode("utf-8", errors="replace").rstrip("\n\r")
            lines.append(line)
            print(f"[{label}] " + line if not line.startswith(f"[{label}]") else line, flush=True)
            logf.write(line + "\n")
        ts1 = datetime.now(timezone.utc).isoformat(timespec="seconds")
        logf.write(f"# subprocess exit_code={proc.wait()} ended={ts1}\n")
    dt = round(time.perf_counter() - t0, 2)
    if proc.returncode == 0:
        return {
            "label": label,
            "status": "ok",
            "records_written": _existing_record_count_for(label),
            "wall_clock_seconds": dt,
        }
    return {
        "label": label,
        "status": "driver_error",
        "error": f"subprocess exited with code {proc.returncode}",
        "output_tail": "\n".join(lines[-20:]),
        "wall_clock_seconds": dt,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Phase 8 big-run driver")
    parser.add_argument("--labels", default=None,
                        help="Comma-separated label subset (default: all cohort labels).")
    parser.add_argument("--force", action="store_true",
                        help="Re-run cells even if records exist (default: skip).")
    parser.add_argument("--dry-run", action="store_true",
                        help="List labels and existing record counts; do not run.")
    parser.add_argument("--workers", type=int, default=1,
                        help="Parallel label workers (subprocess). Each worker "
                             "runs one label in its own Python process. "
                             "Default 1 (serial).")
    args = parser.parse_args()

    cohort = json.loads(COHORT.read_text(encoding="utf-8"))
    all_labels = sorted(cohort["labels"].keys())
    if args.labels:
        wanted = [s.strip() for s in args.labels.split(",") if s.strip()]
        unknown = [w for w in wanted if w not in cohort["labels"]]
        if unknown:
            raise SystemExit(f"Unknown labels: {unknown}")
        labels = wanted
    else:
        labels = all_labels

    print(f"[Phase 8] cohort labels in plan: {len(labels)}")
    print(f"[Phase 8] expected cells/label: {EXPECTED_PER_LABEL}")
    print(f"[Phase 8] expected total cells: {len(labels) * EXPECTED_PER_LABEL}")

    plan: list[dict] = []
    for lid in labels:
        existing = _existing_record_count_for(lid)
        complete = (not args.force) and existing >= EXPECTED_PER_LABEL
        plan.append({"label": lid, "existing_records": existing, "skip_resume": complete})

    if args.dry_run:
        for ph in plan:
            tag = "skip-resume" if ph["skip_resume"] else "run"
            print(f"  {ph['label']:6s} existing={ph['existing_records']:>2d}/{EXPECTED_PER_LABEL}  -> {tag}")
        return 0

    # Defer the heavy import until after dry-run handling (saves ~3s startup).
    from p4_experiments.core.run_unit import _LABEL_TO_INSTANCE  # noqa

    unknown_in_runner = [ph["label"] for ph in plan if ph["label"] not in _LABEL_TO_INSTANCE]
    if unknown_in_runner:
        raise SystemExit(
            f"Runner registry missing labels (cohort/run_unit out of sync): "
            f"{unknown_in_runner[:10]}..."
        )

    started_utc = datetime.now(timezone.utc).isoformat()
    n_workers = max(1, int(args.workers))
    _record_phase_status({
        "status": "running",
        "started_utc": started_utc,
        "label_count_in_plan": len(labels),
        "expected_total_cells": len(labels) * EXPECTED_PER_LABEL,
        "workers": n_workers,
    })

    runnable = [ph for ph in plan if not ph["skip_resume"]]
    skipped = [ph for ph in plan if ph["skip_resume"]]
    per_label_status: list[dict] = [
        {"label": ph["label"], "status": "resumed_complete",
         "records": ph["existing_records"]}
        for ph in skipped
    ]
    for ph in skipped:
        print(f"=== [{ph['label']}] resume: {ph['existing_records']}/{EXPECTED_PER_LABEL} records present, skipping ===", flush=True)

    t0_all = time.perf_counter()
    if n_workers == 1:
        for ph in runnable:
            lid = ph["label"]
            print(f"\n=== [{lid}] running ({ph['existing_records']}/{EXPECTED_PER_LABEL} records present) ===", flush=True)
            per_label_status.append(_run_one_label(lid))
    else:
        print(f"\n[Phase 8] running {len(runnable)} labels with {n_workers} parallel workers (subprocess mode)", flush=True)
        print(f"[Phase 8] per-worker logs → {WORKER_LOGS}/", flush=True)
        n_done = 0
        with ThreadPoolExecutor(max_workers=n_workers) as pool:
            futures = {pool.submit(_run_one_label_subprocess, ph["label"]): ph for ph in runnable}
            for fut in as_completed(futures):
                ph = futures[fut]
                result = fut.result()
                per_label_status.append(result)
                n_done += 1
                tag = result["status"].upper()
                wc = result.get("wall_clock_seconds", 0)
                total_now = _existing_record_count_total()
                print(
                    f"[Phase 8] ({n_done}/{len(runnable)}) [{result['label']}] "
                    f"{tag} in {wc:.1f}s  |  total records: {total_now}/{len(labels)*EXPECTED_PER_LABEL}",
                    flush=True,
                )
                if result["status"] == "driver_error":
                    print(f"  error: {result.get('error')}", flush=True)

    dt_all = time.perf_counter() - t0_all
    breakdown = _engine_failure_breakdown()
    _record_phase_status({
        "status": "complete",
        "started_utc": started_utc,
        "completed_utc": datetime.now(timezone.utc).isoformat(),
        "wall_clock_seconds": round(dt_all, 2),
        "label_count_in_plan": len(labels),
        "expected_total_cells": len(labels) * EXPECTED_PER_LABEL,
        "workers": n_workers,
        "per_label_status": per_label_status,
        "results_breakdown": breakdown,
    })

    n_ok_labels = sum(1 for s in per_label_status if s["status"] in ("ok", "resumed_complete"))
    n_fail_labels = sum(1 for s in per_label_status if s["status"] == "driver_error")
    print(f"\n[Phase 8] driver done in {dt_all/3600:.2f} h.")
    print(f"[Phase 8] labels ok={n_ok_labels} driver_error={n_fail_labels}")
    print(f"[Phase 8] records: total={breakdown['total_records']} "
          f"ok={breakdown['ok']} engine_failure={breakdown['engine_failure']}")
    return 0 if n_fail_labels == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
