"""Phase 8d audit for the canonical fixed-precision QAE/HHL scout."""
from __future__ import annotations
import json
from pathlib import Path

from p4_experiments.canonical.pipeline import phase08d_qae_hhl_scout as scout
from p4_experiments.canonical.pipeline.phase08d_finalize_qae_hhl import (
    FINAL_STATUSES,
    STATUS_PATH,
    SELECTION_PATH,
    detect_stage,
    expected_cells,
    selected_expected_cells,
)

ROOT = Path(__file__).resolve().parents[3]
CANON = ROOT / "p4_experiments" / "canonical"
REPORT = CANON / "reports" / "audit" / "audit_phase8d.json"
COHORT = CANON / "cohort.json"


def _cell_key(rec: dict) -> tuple[str, int, int, str, float] | None:
    try:
        return (
            str(rec["entity_id"]),
            int(rec["n_value"]),
            int(rec["m_precision_qubits"]),
            str(rec["hardware_profile"]),
            float(rec["epsilon"]),
        )
    except Exception:
        return None


def _load_records() -> list[tuple[Path, dict]]:
    records = []
    if not scout.RESULTS_DIR.exists():
        return records
    for path in sorted(scout.RESULTS_DIR.glob("*.json")):
        try:
            records.append((path, json.loads(path.read_text(encoding="utf-8"))))
        except Exception as exc:
            records.append((path, {"_parse_error": str(exc)}))
    return records


def main() -> int:
    results, blockers_failed = [], 0

    def add(cid, status, msg, blocker=True):
        nonlocal blockers_failed
        if status == "FAIL" and blocker:
            blockers_failed += 1
        results.append({"id": cid, "status": status,
                        "blocker": blocker, "message": msg})

    records = _load_records()
    parsed = [rec for _path, rec in records if "_parse_error" not in rec]
    selection = None

    # P8d.S - selection manifest derived from 8a/8b/8c.
    if SELECTION_PATH.exists():
        try:
            selection = json.loads(SELECTION_PATH.read_text(encoding="utf-8"))
        except Exception as exc:
            add("P8d.S", "FAIL", f"selection_manifest.json parse error: {exc}")
    if not any(r["id"] == "P8d.S" for r in results):
        ok = bool(selection) and selection.get("status") == "complete" and not selection.get("blockers")
        add("P8d.S", "PASS" if ok else "FAIL",
            "selection manifest complete" if ok
            else f"selection manifest incomplete/missing; blockers={(selection or {}).get('blockers')}")

    # P8d.A - synced records + finalizer status exist.
    status = None
    if STATUS_PATH.exists():
        try:
            status = json.loads(STATUS_PATH.read_text(encoding="utf-8"))
        except Exception as exc:
            add("P8d.A", "FAIL", f"phase8d_status.json parse error: {exc}")
    if not any(r["id"] == "P8d.A" for r in results):
        ok = bool(records) and status is not None
        add("P8d.A", "PASS" if ok else "FAIL",
            f"records={len(records)} status_file={'yes' if status else 'no'}")

    # P8d.B - record schema and terminal status validity.
    bad = []
    required = (
        "schema", "phase", "entity_id", "entity_kind", "family", "n_value",
        "m_precision_qubits", "precision_role", "hardware_profile", "epsilon",
        "accounting_mode", "instance_synthetic", "measured", "status",
        "sweep_provenance",
    )
    for path, rec in records:
        if "_parse_error" in rec:
            bad.append((path.name, f"json parse: {rec['_parse_error']}"))
            continue
        missing = [key for key in required if key not in rec]
        if missing:
            bad.append((path.name, f"missing {missing}"))
            continue
        if rec.get("schema") != "phase8d_qae_hhl_scout.1.0":
            bad.append((path.name, f"bad schema {rec.get('schema')}"))
        if rec.get("phase") != "8d_qae_hhl_high_n_scout":
            bad.append((path.name, f"bad phase {rec.get('phase')}"))
        if rec.get("status") not in FINAL_STATUSES:
            bad.append((path.name, f"nonfinal status {rec.get('status')}"))
    add("P8d.B", "PASS" if not bad else "FAIL",
        f"{len(bad)} schema/status issues" + (f"; first: {bad[:3]}" if bad else ""))

    # P8d.C - N is problem size and m is precision, never m=N by construction.
    coupling_bad = []
    for path, rec in records:
        if "_parse_error" in rec:
            continue
        inst = rec.get("instance_synthetic") or {}
        m = rec.get("m_precision_qubits")
        n = rec.get("n_value")
        expected_power = 2 ** (int(m) - 1) if isinstance(m, int) and m > 0 else None
        provenance = rec.get("sweep_provenance") or {}
        if inst.get("fixed_precision") is not True:
            coupling_bad.append((path.name, "fixed_precision not true"))
        if inst.get("controlled_power_max") != expected_power:
            coupling_bad.append((path.name, "controlled_power_max != 2^(m-1)"))
        if rec.get("family") == "qae" and inst.get("m_eval_qubits") != m:
            coupling_bad.append((path.name, "qae m_eval_qubits mismatch"))
        if rec.get("family") == "hhl" and inst.get("m_clock_qubits") != m:
            coupling_bad.append((path.name, "hhl m_clock_qubits mismatch"))
        if rec.get("family") == "qae" and inst.get("n_state") != n:
            coupling_bad.append((path.name, "qae n_state mismatch"))
        if rec.get("family") == "hhl" and inst.get("n_b") != n:
            coupling_bad.append((path.name, "hhl n_b mismatch"))
        if provenance.get("problem_size_decoupled_from_precision") is not True:
            coupling_bad.append((path.name, "missing decoupling provenance"))
    add("P8d.C", "PASS" if not coupling_bad else "FAIL",
        f"{len(coupling_bad)} fixed-precision defects"
        + (f"; first: {coupling_bad[:3]}" if coupling_bad else ""))

    # P8d.D - staged grid completeness.
    rows = [{
        "entity_id": rec.get("entity_id"),
        "n_value": rec.get("n_value"),
        "m_precision_qubits": rec.get("m_precision_qubits"),
        "hardware_profile": rec.get("hardware_profile"),
        "epsilon": rec.get("epsilon"),
    } for rec in parsed]
    stage = (status or {}).get("stage") or detect_stage(rows)
    selected_entities = [str(entity_id) for entity_id in (selection or {}).get("selected_entities", [])]
    expected = selected_expected_cells(stage, selected_entities) if selected_entities else expected_cells(stage)
    observed = {key for rec in parsed if (key := _cell_key(rec)) is not None}
    missing = sorted(expected - observed)
    add("P8d.D", "PASS" if not missing else "FAIL",
        f"stage={stage} records={len(observed)} expected={len(expected)} missing={len(missing)}"
        + (f"; first={missing[:3]}" if missing else ""))

    # P8d.E - canary-first discipline before larger grids.
    canary_expected = selected_expected_cells("canary", selected_entities) if selected_entities else expected_cells("canary")
    canary_missing = sorted(canary_expected - observed)
    add("P8d.E", "PASS" if not canary_missing else "FAIL",
        "canary gate present" if not canary_missing
        else f"missing canary cells: {canary_missing[:3]}")

    # P8d.F - appendix-only disclosure and no canonical Phase 8 mutation.
    disclosure_ok = bool(status) and all([
        status.get("appendix_only") is True,
        status.get("headline_excludes_phase8d") is True,
        status.get("problem_size_decoupled_from_precision") is True,
        status.get("canonical_phase8_results_unchanged") is True,
    ])
    if COHORT.exists():
        cohort = json.loads(COHORT.read_text(encoding="utf-8"))
        p8d = (cohort.get("_phase_status") or {}).get("phase8d") or {}
        disclosure_ok = disclosure_ok and p8d.get("track") == "qae_hhl_fixed_precision_high_n"
    add("P8d.F", "PASS" if disclosure_ok else "FAIL",
        "appendix disclosure and cohort phase status OK" if disclosure_ok
        else "missing appendix/disclosure/cohort status fields")

    if stage == "canary":
        add("P8d.G", "WARN",
            "canary stage only; do not cite as full high-N sweep", blocker=False)
    elif stage == "floquet":
        add("P8d.G", "PASS",
            "primary floquet grid complete; surface extension remains optional", blocker=False)
    else:
        add("P8d.G", "PASS", "floquet + surface grids complete", blocker=False)

    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps({
        "phase": "8d",
        "track": "qae_hhl_fixed_precision_high_n",
        "results": results,
        "totals": {
            "blockers_failed": blockers_failed,
            "n_pass": sum(1 for r in results if r["status"] == "PASS"),
            "n_fail": sum(1 for r in results if r["status"] == "FAIL"),
            "n_warn": sum(1 for r in results if r["status"] == "WARN"),
        },
    }, indent=2), encoding="utf-8")
    n_pass = sum(1 for r in results if r["status"] == "PASS")
    n_fail = sum(1 for r in results if r["status"] == "FAIL")
    n_warn = sum(1 for r in results if r["status"] == "WARN")
    print(f"[Phase 8d audit] {n_pass} PASS / {n_fail} FAIL / {n_warn} WARN; "
          f"blockers_failed={blockers_failed}")
    for r in results:
        marker = "[ok]" if r["status"] == "PASS" else ("[warn]" if r["status"] == "WARN" else "[FAIL]")
        print(f"  {marker} {r['id']}: {r['message']}")
    print(f"[Phase 8d audit] Report -> {REPORT}")
    return 1 if blockers_failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
