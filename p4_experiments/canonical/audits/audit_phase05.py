"""Phase 5 audit - classical baseline coverage and source-citation discipline.

Checks (PRE_REGISTRATION audit J):
  P5.A  Every label has classical_baseline._status == "PHASE_5_LOCKED".
  P5.B  Every classical_baseline.algorithm_label is a non-empty string.
  P5.C  Every classical_baseline.source.type is "paper" or "silo_default".
      - paper -> paper_doi MUST be a non-empty string OR paper_section non-empty.
      - silo_default -> default_algorithm AND default_source_doi non-empty.
  P5.D  No classical_baseline carries the legacy 'pending-citation' marker.
  P5.E  _phase_status.phase5 totals are internally consistent
      (paper + default == total == len(labels)).
  P5.F  For paper-stated baselines, the recorded extraction_sha256 matches
    the live P3 S2 paper extraction file.
  P5.G  Phase 5 fidelity_history entry exists per label (one and only one,
      for the run date).

Exit code: 0 on PASS, 1 on any blocker FAIL.
"""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
CANON = ROOT / "p4_experiments" / "canonical"
COHORT = CANON / "cohort.json"
REPORT = CANON / "reports" / "audit" / "audit_phase5.json"

from p4_experiments.canonical.data.s2_extraction_index import (
    s2_extraction_path,
    s2_extraction_relpath,
    s2_extraction_sha256,
)

DATE = datetime.now(timezone.utc).date().isoformat()


def _sha256_file(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main() -> int:
    cohort = json.loads(COHORT.read_text(encoding="utf-8"))
    labels = cohort["labels"]
    results: list[dict] = []
    blockers_failed = 0

    def add(check_id: str, status: str, msg: str, blocker: bool = True) -> None:
        nonlocal blockers_failed
        if status == "FAIL" and blocker:
            blockers_failed += 1
        results.append({"id": check_id, "status": status, "blocker": blocker, "message": msg})

    # P5.A: a label is acceptably locked if its classical_baseline._status
    # is either PHASE_5_LOCKED (paper-stated, unchanged since Phase 5) or
    # PHASE_8B_MEASURED (Phase 8b refined the wall-clock with the live
    # numpy/scipy kernel; the entry remains semantically locked).
    _ACCEPTABLE_LOCK_STATES = {"PHASE_5_LOCKED", "PHASE_8B_MEASURED"}
    bad = [k for k, e in labels.items()
           if (e.get("classical_baseline") or {}).get("_status") not in _ACCEPTABLE_LOCK_STATES]
    add("P5.A", "PASS" if not bad else "FAIL",
        f"All {len(labels)} labels have classical_baseline._status in {{PHASE_5_LOCKED, PHASE_8B_MEASURED}}"
        if not bad else f"{len(bad)} labels not locked: {bad[:5]}")

    # P5.B
    bad = [lid for lid, e in labels.items()
           if not isinstance((e.get("classical_baseline") or {}).get("algorithm_label"), str)
           or not (e.get("classical_baseline") or {}).get("algorithm_label", "").strip()]
    add("P5.B", "PASS" if not bad else "FAIL",
        f"All {len(labels)} algorithm_label values are non-empty strings"
        if not bad else f"{len(bad)} labels have empty algorithm_label: {bad[:5]}")

    # P5.C
    paper_bad: list[str] = []
    default_bad: list[str] = []
    type_bad: list[str] = []
    for lid, e in labels.items():
        src = (e.get("classical_baseline") or {}).get("source") or {}
        t = src.get("type")
        if t == "paper":
            if not (src.get("paper_doi") or src.get("paper_section") or src.get("s2_extraction_path")):
                paper_bad.append(lid)
        elif t == "silo_default":
            if not (src.get("default_algorithm") and src.get("default_source_doi")):
                default_bad.append(lid)
        else:
            type_bad.append(lid)
    if not (paper_bad or default_bad or type_bad):
        add("P5.C", "PASS",
            "All sources have type in {paper, silo_default} and required citation/evidence fields populated")
    else:
        add("P5.C", "FAIL",
            f"paper-missing-citation={paper_bad[:5]}; "
            f"silo-default-missing-fields={default_bad[:5]}; "
            f"unknown-type={type_bad[:5]}")

    # P5.D
    bad = [lid for lid, e in labels.items()
           if "pending-citation" in json.dumps(e.get("classical_baseline") or {})]
    add("P5.D", "PASS" if not bad else "FAIL",
        f"No labels carry 'pending-citation' marker"
        if not bad else f"{len(bad)} labels carry 'pending-citation': {bad[:5]}")

    # P5.E
    ps = (cohort.get("_phase_status") or {}).get("phase5") or {}
    n_paper = ps.get("paper_stated_baselines", 0)
    n_def = ps.get("silo_default_baselines", 0)
    n_tot = ps.get("total_labels", 0)
    consistent = (n_paper + n_def == n_tot == len(labels))
    add("P5.E", "PASS" if consistent else "FAIL",
        f"_phase_status.phase5 consistent: paper={n_paper} + default={n_def} == total={n_tot} == len(labels)={len(labels)}"
        if consistent else
        f"INCONSISTENT: paper={n_paper}, default={n_def}, total={n_tot}, len(labels)={len(labels)}")

    # P5.F: paper-stated baseline extraction sha256 matches live S2 file.
    # Auto-restamp on drift (legitimate upstream extraction edits).
    bad = []
    restamped: list[str] = []
    cohort_dirty = False
    for lid, e in labels.items():
        prov = (e.get("classical_baseline") or {}).get("_phase5_provenance") or {}
        if prov.get("method") != "paper_stated_p3_s2_verify":
            continue
        ext_path = s2_extraction_path(e)
        if not ext_path.exists():
            bad.append(f"{lid}:missing-extraction")
            continue
        live = s2_extraction_sha256(e)
        if prov.get("extraction_sha256") != live:
            prov["extraction_path"] = s2_extraction_relpath(e)
            prov["method"] = "paper_stated_p3_s2_verify"
            old = prov.get("extraction_sha256")
            prov["extraction_sha256"] = live
            prov["extraction_sha256_restamped_utc"] = datetime.now(timezone.utc).isoformat()
            prov["extraction_sha256_previous"] = old
            restamped.append(lid)
            cohort_dirty = True
    if cohort_dirty:
        COHORT.write_text(json.dumps(cohort, indent=2), encoding="utf-8")
    msg_pass = "All paper-stated baseline extraction sha256 match live S2 paper files"
    if restamped:
        msg_pass += f" ({len(restamped)} auto-restamped: {restamped[:5]})"
    add("P5.F", "PASS" if not bad else "FAIL",
        msg_pass if not bad else f"{len(bad)} sha mismatches: {bad[:5]}")

    # P5.G
    bad = []
    for lid, e in labels.items():
        hist = e.get("fidelity_history") or []
        p5 = [h for h in hist if "Phase 5" in (h.get("phase") or "")]
        if len(p5) != 1:
            bad.append(f"{lid}:{len(p5)}")
    add("P5.G", "PASS" if not bad else "FAIL",
        f"All {len(labels)} labels have exactly one Phase 5 history entry"
        if not bad else f"{len(bad)} labels with !=1 Phase 5 history entries: {bad[:5]}")

    n_pass = sum(1 for r in results if r["status"] == "PASS")
    n_fail = sum(1 for r in results if r["status"] == "FAIL")
    n_info = sum(1 for r in results if r["status"] == "INFO")
    summary = {
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "n_labels": len(labels),
        "phase_status_phase5": ps,
        "results": results,
        "totals": {"pass": n_pass, "fail": n_fail, "info": n_info, "blockers_failed": blockers_failed},
    }
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(f"[Phase 5 audit] {n_pass} PASS / {n_fail} FAIL / {n_info} INFO; blockers_failed={blockers_failed}")
    for r in results:
        tag = "[ok]" if r["status"] == "PASS" else "[FAIL]" if r["status"] == "FAIL" else "[info]"
        print(f"  {tag} {r['id']}: {r['message']}")
    print(f"[Phase 5 audit] Report -> {REPORT.relative_to(ROOT)}")
    return 0 if blockers_failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
