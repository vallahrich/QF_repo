"""Phase 7 - Canonical pipeline orchestrator.

One-command rebuild for the QF P4 canonical pipeline. Runs every phase
script in dependency order, tracks per-phase status in
``cohort.json._phase_status``, and writes
``reports/audit/audit_report.json`` summarizing each audit's pass/fail counts.

Usage:
    python -m p4_experiments.canonical.run_pipeline --from-scratch --seed 0x50414D50

Flags:
    --from-scratch    Reset _phase_status before running (forces all phases).
    --seed HEX        Pre-registration seed (default: 0x50414D50).
    --resume          Skip phases already marked status='complete' in cohort.
    --phases LIST     Comma-separated subset (e.g. "phase4,phase5,phase6").
    --skip-big-run    Run everything except Phase 8 (the multi-day big run).
    --dry-run         Print the planned phase order without executing.

Exit code: 0 if every executed phase exits 0 AND every audit reports
blockers_failed=0; 1 otherwise.

Determinism. The seed is fixed at the PRE_REGISTRATION value
(0x50414D50). All scripts that consume RNG read it from
``cohort.json._phase_status.seed``.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
CANON = ROOT / "p4_experiments" / "canonical"
COHORT = CANON / "cohort.json"
REPORTS = CANON / "reports"
AUDIT_REPORTS = REPORTS / "audit"
AUDIT_REPORT = AUDIT_REPORTS / "audit_report.json"
S2_MANIFEST_PIN = CANON / "cohort_s2_manifest.sha256"
S2_EXTRACTIONS_DIR = ROOT / "p3_thematic_synthesis" / "s2_quantitative" / "output" / "extractions"

PYTHON = sys.executable

# Phase ladder. Each entry: (phase_id, action_script, audit_script).
# `action_script=None` means audit-only (or already-complete).
PHASES: list[dict[str, Any]] = [
    {"id": "phase3_compare", "name": "S2 fidelity comparison", "script": "pipeline/phase03_compare.py", "audit": None},
    {"id": "phase3", "name": "Apply S2 fidelity review",       "script": "pipeline/phase03_update_cohort.py",                "audit": "audits/audit_phase03.py"},
    {"id": "phase4", "name": "Proxy justification fallback", "script": "pipeline/phase04_proxy_justifications.py","audit": "audits/audit_phase04.py", "extra_audits": ["audits/audit_phase04_paper_coverage.py", "audits/audit_phase04_faithfulness.py"]},
    {"id": "phase5", "name": "Classical baselines",          "script": "pipeline/phase05_classical_baselines.py",   "audit": "audits/audit_phase05.py"},
    {"id": "phase6", "name": "Lift trapped-ion skip",        "script": "pipeline/phase06_lift_skip.py",                    "audit": "audits/audit_phase06.py"},
    # Phase 7 is the orchestrator itself; nothing to dispatch.
    {"id": "phase8", "name": "Big run (cohort x 36 cells)",  "script": "pipeline/phase08_resource_grid.py",                      "audit": "audits/audit_phase08.py"},
    # Phase 8b (added 2026-04-19): measures the classical baseline
    # wall-clock for every Faithful label so H4 criterion C2 is not
    # silently vacuous. Two scripts: the kernel runner produces JSON
    # records under common/output/classical_results/, then the cohort
    # updater backfills cohort.json[labels][label].classical_baseline.
    {"id": "phase8b_run", "name": "Classical baseline measurement",
        "script": "pipeline/phase08b_classical_baselines.py", "audit": None},
    {"id": "phase8b_cohort", "name": "Backfill classical baselines into cohort",
        "script": "pipeline/phase08b_update_cohort.py", "audit": None},
    # Phase 8c (added 2026-04-19): all-cohort top-3 classical alternatives.
    # Runs the silo-default top-3 numpy/scipy kernels at each label's
    # instance scale. Provides the cohort-coverage
    # table and the strongest-of-3 baseline used by Phase 9 H4 sensitivity.
    {"id": "phase8c_alternatives", "name": "Classical top-3 alternatives",
        "script": "pipeline/phase08c_classical_alternatives.py", "audit": None},
        {"id": "phase9", "name": "Stats + sensitivity grid",     "script": "pipeline/phase09_stats.py",                        "audit": "audits/audit_phase09.py"},
    # Phase 8d is external VM compute: first lock a data-derived selection
    # manifest, launch/sync the fixed-precision QAE/HHL scout separately,
    # then include/finalize it here. It is optional and appendix-only, never
    # part of the headline Phase 8/9 verdict.
    {"id": "phase8d_select", "name": "QAE/HHL high-N scout selection",
        "script": "pipeline/phase08d_select_experiments.py", "audit": None,
     "optional_external": True},
    {"id": "phase8d", "name": "QAE/HHL high-N scout finalize",
        "script": "pipeline/phase08d_finalize_qae_hhl.py", "audit": "audits/audit_phase08d.py",
     "optional_external": True},
        {"id": "phase10", "name": "Manuscript artifacts",        "script": "pipeline/phase10_manuscript_artifacts.py",        "audit": "audits/audit_phase10.py"},
    # Phase 8e (added 2026-04-20, doc-only): per-silo synthesis cards.
    # Sits between phase10 and phase11 because it consumes manuscript
    # artifacts (key_numbers.json) and emits per-silo LaTeX tables that
    # phase11 packages into the Zenodo bundle.
    {"id": "phase8e", "name": "Per-silo synthesis cards",
     "script": "pipeline/phase08e_per_silo_synthesis.py", "audit": "audits/audit_phase08e.py"},
    {"id": "phase11", "name": "Zenodo bundle",               "script": "pipeline/phase11_zenodo_bundle.py",               "audit": "audits/audit_phase11.py"},
]


def _load_cohort() -> dict:
    return json.loads(COHORT.read_text(encoding="utf-8"))


def _save_cohort(cohort: dict) -> None:
    COHORT.write_text(json.dumps(cohort, indent=2), encoding="utf-8")


def _assert_s2_manifest(*, allow_drift: bool) -> bool:
    """Refuse to run if the upstream P3 S2 extractions have drifted from the
    pinned cohort_s2_manifest.sha256 (added 2026-05-02; reproducibility guard).

    Returns True if (a) drift is allowed by --allow-s2-drift, (b) the manifest
    file is missing (legacy mode), or (c) the live concat sha256 matches the
    pinned value. Returns False on a fatal mismatch.
    """
    import hashlib  # local import keeps the orchestrator's top-level surface unchanged
    if not S2_MANIFEST_PIN.exists():
        print(f"[orchestrator] No S2 manifest pin at {S2_MANIFEST_PIN.relative_to(ROOT)}; skipping S2 drift check.")
        return True
    try:
        pin = json.loads(S2_MANIFEST_PIN.read_text(encoding="utf-8"))
        expected = pin["concat_sha256"]
    except Exception as exc:  # noqa: BLE001
        print(f"[orchestrator] WARNING: cohort_s2_manifest.sha256 unreadable ({exc}); skipping S2 drift check.")
        return True

    cohort = _load_cohort()
    ids = sorted({L["paper_id"] for L in cohort.get("labels", {}).values()})
    hashes: list[str] = []
    missing: list[str] = []
    for pid in ids:
        cands = list(S2_EXTRACTIONS_DIR.rglob(f"{pid}.json"))
        if cands:
            hashes.append(f"{pid}\t{hashlib.sha256(cands[0].read_bytes()).hexdigest()}\n")
        else:
            missing.append(pid)
    live = hashlib.sha256("".join(hashes).encode("utf-8")).hexdigest()
    if missing:
        print(f"[orchestrator] WARNING: {len(missing)} cohort paper_ids are not resolvable to S2 extractions: {missing[:5]}{'...' if len(missing) > 5 else ''}")

    if live == expected:
        print(f"[orchestrator] S2 manifest OK ({len(hashes)} extractions; concat sha256 matches pin).")
        return True
    if allow_drift:
        print(f"[orchestrator] S2 manifest drift accepted (--allow-s2-drift): live={live[:16]} pin={expected[:16]}")
        return True
    print(
        "[orchestrator] FATAL: S2 extraction manifest does not match the pinned value.\n"
        f"  pinned : {expected}\n"
        f"  live   : {live}\n"
        f"  pin source: {S2_MANIFEST_PIN.relative_to(ROOT)}\n"
        "  If this is intentional (you regenerated the S2 corpus), re-run with\n"
        "  --allow-s2-drift, then update the pin via\n"
        "  `python tools/verify/_oneshot_phase7_cohort_manifest.py`."
    )
    return False


def _run(script: Path) -> int:
    """Run a script under the canonical interpreter; stream its output.

    Adds ROOT to PYTHONPATH so phase scripts can import sibling modules
    via the ``p4_experiments.canonical.*`` package path (otherwise
    Python's automatic sys.path[0] is the script directory, not ROOT).
    """
    print(f"\n--- Running {script.name} ---", flush=True)
    env = os.environ.copy()
    existing = env.get("PYTHONPATH", "")
    env["PYTHONPATH"] = str(ROOT) + (os.pathsep + existing if existing else "")
    # Pin BLAS threading to 1 so wall-clock measurements in phase8b/8c/8d
    # are reproducible across machines (single-threaded numpy/scipy/Aer).
    # Operators can override per-process by exporting these before invoking
    # run_pipeline.py; we only set defaults if the caller did not.
    for _k in ("OMP_NUM_THREADS", "MKL_NUM_THREADS",
               "OPENBLAS_NUM_THREADS", "NUMEXPR_NUM_THREADS"):
        env.setdefault(_k, "1")
    proc = subprocess.run([PYTHON, str(script)], cwd=str(ROOT), env=env)
    return proc.returncode


def _phase_status(cohort: dict, phase_id: str) -> dict:
    ps = cohort.get("_phase_status")
    if not isinstance(ps, dict):
        return {}
    return ps.get(phase_id) or {}


def _is_complete(cohort: dict, phase_id: str) -> bool:
    return _phase_status(cohort, phase_id).get("status") == "complete"


def _record_phase_status(phase_id: str, status: str, extra: dict | None = None) -> None:
    cohort = _load_cohort()
    ps = cohort.get("_phase_status")
    if not isinstance(ps, dict):
        ps = {"_legacy": ps} if ps is not None else {}
    cur = ps.get(phase_id) or {}
    cur.update({
        "status": status,
        "orchestrator_run_utc": datetime.now(timezone.utc).isoformat(),
    })
    if extra:
        cur.update(extra)
    ps[phase_id] = cur
    cohort["_phase_status"] = ps
    _save_cohort(cohort)


def _record_audit(phase_id: str, audit_path: Path) -> dict:
    """Read an audit_phaseN.json report (if present) and return a summary."""
    if not audit_path.exists():
        return {"phase_id": phase_id, "status": "missing", "report_path": str(audit_path.relative_to(ROOT))}
    rep = json.loads(audit_path.read_text(encoding="utf-8"))
    return {
        "phase_id": phase_id,
        "status": "pass" if rep.get("totals", {}).get("blockers_failed", 1) == 0 else "fail",
        "report_path": str(audit_path.relative_to(ROOT)),
        "totals": rep.get("totals"),
    }


def _audit_json_path(audit_path: Path) -> Path:
    stem = re.sub(r"^audit_phase0(?=\d)", "audit_phase", audit_path.stem)
    return AUDIT_REPORTS / f"{stem}.json"


def main() -> int:
    parser = argparse.ArgumentParser(description="Canonical pipeline orchestrator")
    parser.add_argument("--from-scratch", action="store_true",
                        help="Reset _phase_status (forces all phases to re-run).")
    parser.add_argument("--seed", default="0x50414D50",
                        help="PRE_REGISTRATION seed (hex, default 0x50414D50).")
    parser.add_argument("--resume", action="store_true",
                        help="Skip phases already marked status='complete'.")
    parser.add_argument("--phases", default=None,
                        help="Comma-separated subset (e.g. 'phase4,phase5').")
    parser.add_argument("--skip-big-run", action="store_true",
                        help="Skip Phase 8 (the multi-day big run).")
    parser.add_argument("--include-phase8d", action="store_true",
                        help="Finalize/audit synced external Phase 8d QAE/HHL scout results.")
    parser.add_argument("--dry-run", action="store_true",
                        help="Print plan without executing.")
    parser.add_argument("--allow-s2-drift", action="store_true",
                        help=("Skip the upstream S2 extraction sha256 "
                              "manifest assertion (cohort_s2_manifest.sha256). "
                              "Use only when you have intentionally regenerated "
                              "the S2 corpus and need to re-pin downstream."))
    args = parser.parse_args()

    # Reproducibility guard 2026-05-02: refuse to run if the upstream P3 S2
    # extractions have drifted from the pinned cohort_s2_manifest.sha256
    # without an explicit --allow-s2-drift override. Without this guard the
    # canonical pipeline can silently produce different numbers when the S2
    # corpus is updated, because the per-label SHA in classical_baseline
    # provenance is checked too late (Phase 5+).
    if not _assert_s2_manifest(allow_drift=args.allow_s2_drift):
        return 1

    seed = int(args.seed, 0)

    requested = set(args.phases.split(",")) if args.phases else None
    plan: list[dict[str, Any]] = []
    for ph in PHASES:
        if requested is not None and ph["id"] not in requested:
            continue
        if requested is None and ph.get("optional_external") and not args.include_phase8d:
            print(f"[orchestrator] Skipping {ph['id']} (external appendix; use --include-phase8d)")
            continue
        if args.skip_big_run and ph["id"] == "phase8":
            print(f"[orchestrator] Skipping {ph['id']} (--skip-big-run)")
            continue
        plan.append(ph)

    print(f"[orchestrator] Plan ({len(plan)} phases):")
    for ph in plan:
        print(f"  - {ph['id']:8s} {ph['name']}  (script={ph['script']}, audit={ph['audit']})")

    if args.dry_run:
        return 0

    if args.from_scratch:
        cohort = _load_cohort()
        cohort["_phase_status"] = {
            "seed": hex(seed),
            "reset_utc": datetime.now(timezone.utc).isoformat(),
        }
        _save_cohort(cohort)
        print(f"[orchestrator] Reset _phase_status (seed={hex(seed)})")
    else:
        cohort = _load_cohort()
        ps = cohort.get("_phase_status")
        if not isinstance(ps, dict):
            cohort["_phase_status"] = {"seed": hex(seed)}
            _save_cohort(cohort)
        elif "seed" not in ps:
            ps["seed"] = hex(seed)
            cohort["_phase_status"] = ps
            _save_cohort(cohort)

    audit_summaries: list[dict] = []
    fail_phase: str | None = None

    for ph in plan:
        cohort = _load_cohort()
        if args.resume and _is_complete(cohort, ph["id"]):
            print(f"[orchestrator] {ph['id']}: already complete, skipping (--resume).")
            audit_summaries.append({"phase_id": ph["id"], "status": "skipped_resume"})
            continue

        script_path = CANON / ph["script"]
        if not script_path.exists():
            msg = f"[orchestrator] {ph['id']}: action script {script_path.name} not found; pipeline exits."
            print(msg, flush=True)
            _record_phase_status(ph["id"], "missing_script", {"missing": ph["script"]})
            audit_summaries.append({"phase_id": ph["id"], "status": "missing_script", "missing": ph["script"]})
            fail_phase = ph["id"]
            break

        rc = _run(script_path)
        if rc != 0:
            print(f"[orchestrator] {ph['id']}: action exited with code {rc}; pipeline aborted.")
            _record_phase_status(ph["id"], "action_failed", {"returncode": rc})
            audit_summaries.append({"phase_id": ph["id"], "status": "action_failed", "returncode": rc})
            fail_phase = ph["id"]
            break

        if ph["audit"]:
            audit_path = CANON / ph["audit"]
            arc = _run(audit_path)
            audit_json = _audit_json_path(audit_path)
            summary = _record_audit(ph["id"], audit_json)
            summary["audit_returncode"] = arc
            audit_summaries.append(summary)
            if arc != 0 or summary["status"] == "fail":
                print(f"[orchestrator] {ph['id']}: audit FAILED; pipeline aborted.")
                _record_phase_status(ph["id"], "audit_failed",
                                     {"audit_returncode": arc, "audit_summary": summary})
                fail_phase = ph["id"]
                break
        else:
            audit_summaries.append({"phase_id": ph["id"], "status": "no_audit"})

        # Optional auxiliary audits (non-blocking-by-phase, but still must
        # PASS or the pipeline aborts). Used for cross-phase coverage
        # checks like Phase 4 paper-coverage.
        for extra in ph.get("extra_audits", []) or []:
            extra_path = CANON / extra
            erc = _run(extra_path)
            extra_json = _audit_json_path(extra_path)
            esum = _record_audit(f"{ph['id']}+{extra_path.stem}", extra_json)
            esum["audit_returncode"] = erc
            audit_summaries.append(esum)
            if erc != 0 or esum["status"] == "fail":
                print(f"[orchestrator] {ph['id']}+{extra_path.stem}: extra audit FAILED; pipeline aborted.")
                _record_phase_status(ph["id"], "extra_audit_failed",
                                     {"audit": extra, "audit_returncode": erc})
                fail_phase = ph["id"]
                break
        if fail_phase:
            break

    AUDIT_REPORT.parent.mkdir(parents=True, exist_ok=True)
    AUDIT_REPORT.write_text(json.dumps({
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "seed": hex(seed),
        "phases_planned": [p["id"] for p in plan],
        "phases_executed": [s["phase_id"] for s in audit_summaries],
        "fail_phase": fail_phase,
        "summaries": audit_summaries,
    }, indent=2), encoding="utf-8")

    print(f"\n[orchestrator] audit_report.json -> {AUDIT_REPORT.relative_to(ROOT)}")
    if fail_phase:
        print(f"[orchestrator] Pipeline FAILED at {fail_phase}.")
        return 1
    print(f"[orchestrator] Pipeline OK ({len(audit_summaries)} phases).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
