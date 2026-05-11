"""Run one Phase 8 resource-estimation cell.

This is an operational escape hatch for the tail of the distributed Phase 8
run. It writes the same result-record schema as ``run_unit.py`` for one
``(label, hardware_profile, epsilon, accounting_mode)`` cell.
"""

from __future__ import annotations

import argparse
import json
import os
import time
from datetime import datetime, timezone

from p4_experiments.core.circuit_registry import get_builder
from p4_experiments.core.oracle_accounting import apply_accounting, oracle_variant
from p4_experiments.core.qdk_bridge import _decompose_for_qdk, list_profiles
from p4_experiments.core.run_unit import (
    RESULTS,
    _LABEL_TO_INSTANCE,
    _classical_for,
    _engine_failure_measured,
    _estimate_with_timeout,
    _git_commit,
    _import_builder_module,
    _make_record,
    _metric_for,
    _versions,
)


def _record_path(label: str, profile: str, epsilon: float, mode: str):
    return RESULTS / f"{label}_{profile}_eps{epsilon:.0e}_{mode}.json"


def _existing_is_final(path) -> bool:
    if not path.exists():
        return False
    try:
        record = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return False
    status = (record.get("measured") or {}).get("status")
    reason = str((record.get("measured") or {}).get("reason", ""))
    return status in (None, "ok") or (status == "engine_failure" and reason.startswith("timeout_after_"))


def run_cell(label: str, profile: str, epsilon: float, mode: str, timeout_s: int, force: bool) -> str:
    if profile not in set(list_profiles()):
        raise SystemExit(f"Unknown profile: {profile}")
    if mode not in {"bare", "full"}:
        raise SystemExit(f"Unknown accounting mode: {mode}")

    path = _record_path(label, profile, epsilon, mode)
    if _existing_is_final(path) and not force:
        print(f"[{label}] {mode:4s} {profile:15s} eps={epsilon:.0e} CELL-SKIP existing final record: {path.name}", flush=True)
        return "skipped"

    _import_builder_module(label)
    instance_path = _LABEL_TO_INSTANCE[label]
    instance = json.loads(instance_path.read_text(encoding="utf-8"))
    instance_id = instance["instance_id"]
    entry = get_builder(label)

    bare = entry.builder(instance)
    metric = _metric_for(label, bare, instance)
    classical = _classical_for(label, instance)

    circuit = bare if mode == "bare" else apply_accounting(label, mode, instance, bare)
    circuit = _decompose_for_qdk(circuit)

    start = datetime.now(timezone.utc).strftime("%H:%M:%S")
    print(
        f"[{label}] {mode:4s} {profile:15s} eps={epsilon:.0e} "
        f"CELL-START timeout={timeout_s}s t0={start}Z",
        flush=True,
    )
    t0 = time.perf_counter()
    measured, dt, status, reason = _estimate_with_timeout(circuit, profile, epsilon, timeout_s)
    elapsed = time.perf_counter() - t0
    end = datetime.now(timezone.utc).strftime("%H:%M:%S")
    print(
        f"[{label}] {mode:4s} {profile:15s} eps={epsilon:.0e} "
        f"CELL-{status.upper()} in {dt:.1f}s elapsed={elapsed:.1f}s t1={end}Z",
        flush=True,
    )
    if status == "engine_failure":
        measured = _engine_failure_measured(reason or "unknown_engine_failure", dt)
        fail_log = RESULTS / "_engine_failures.log"
        with fail_log.open("a", encoding="utf-8") as handle:
            handle.write(
                f"{datetime.now(timezone.utc).isoformat()} "
                f"label={label} mode={mode} profile={profile} eps={epsilon:.0e} "
                f"reason={measured.get('reason')} dt={dt:.1f}s source=phase8_run_cell\n"
            )

    record = _make_record(
        label=label,
        instance=instance,
        instance_id=instance_id,
        instance_path=instance_path,
        pid=profile,
        eps=epsilon,
        mode=mode,
        measured=measured,
        metric=metric,
        classical=classical,
        versions=_versions(),
        commit=_git_commit(),
        ts=datetime.now(timezone.utc).isoformat(),
        oracle_variant_fn=oracle_variant,
    )
    path.write_text(json.dumps(record, indent=2), encoding="utf-8")
    print(f"[{label}] wrote {path.name}", flush=True)
    return status


def main() -> int:
    parser = argparse.ArgumentParser(description="Run one Phase 8 resource-estimation cell.")
    parser.add_argument("label")
    parser.add_argument("--profile", required=True)
    parser.add_argument("--epsilon", type=float, required=True)
    parser.add_argument("--mode", choices=["bare", "full"], required=True)
    parser.add_argument("--timeout-s", type=int, default=int(os.environ.get("P4_CELL_TIMEOUT_S", "7200")))
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    path = _record_path(args.label, args.profile, args.epsilon, args.mode)
    if args.dry_run:
        print(f"target={path}")
        print(f"exists={path.exists()} final={_existing_is_final(path)}")
        return 0
    status = run_cell(args.label, args.profile, args.epsilon, args.mode, args.timeout_s, args.force)
    return 0 if status in {"ok", "engine_failure", "skipped"} else 1


if __name__ == "__main__":
    raise SystemExit(main())