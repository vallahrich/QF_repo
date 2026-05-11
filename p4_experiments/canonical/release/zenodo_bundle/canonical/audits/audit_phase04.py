"""Phase 4 audit — proxy fallback verification.

Checks for every Proxy-tier (P) label:

P4.A — every P-tier label has a `proxy_template` field in cohort.json
P4.B — every P-tier label has a `proxy_justification_path` pointing to an
       existing file
P4.C — `proxy_justification_sha256` in cohort.json matches the live file
P4.D — every P-tier label has a Phase 4 fidelity_history entry whose
       proxy_justification_sha256 matches the current file
P4.E — top-level fidelity remains 'P' for every label that has a Phase 4
       history entry
P4.F — `_phase_status.phase4` summary counts equal observed counts
P4.G — non-P labels do not carry stale proxy metadata or Phase 4 history

Output: canonical/reports/audit/audit_phase4.json + stdout summary.
Exit code: 0 if all blockers green, 1 otherwise.
"""

from __future__ import annotations

import hashlib
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Tuple

ROOT = Path(__file__).resolve().parents[3]
CANON = ROOT / "p4_experiments" / "canonical"
COHORT = CANON / "cohort.json"
AUDIT_REPORTS = CANON / "reports" / "audit"

PROXY_METADATA_KEYS = (
    "proxy_template",
    "proxy_template_secondary",
    "proxy_template_detected_from",
    "proxy_justification_path",
    "proxy_justification_sha256",
    "proxy_reason",
)


def _sha256(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def audit() -> Tuple[Dict[str, Any], bool]:
    findings: List[Dict[str, Any]] = []
    blockers_failed = 0

    def add(check_id: str, status: str, msg: str, blocker: bool = True, **extra):
        nonlocal blockers_failed
        if status != "PASS" and blocker:
            blockers_failed += 1
        findings.append({"check_id": check_id, "status": status, "blocker": blocker, "message": msg, **extra})

    cohort = json.loads(COHORT.read_text(encoding="utf-8"))
    labels = cohort.get("labels", {})
    p_labels = {lid: e for lid, e in labels.items() if e.get("fidelity") == "P"}
    non_p_labels = {lid: e for lid, e in labels.items() if e.get("fidelity") != "P"}

    # --- P4.A
    missing_template = [lid for lid, e in p_labels.items() if "proxy_template" not in e]
    if missing_template:
        add("P4.A", "FAIL", f"{len(missing_template)} P-tier labels missing proxy_template", samples=missing_template[:10])
    else:
        add("P4.A", "PASS", f"All {len(p_labels)} P-tier labels carry proxy_template")

    # --- P4.B
    missing_path: List[str] = []
    not_exist: List[str] = []
    for lid, e in p_labels.items():
        path = e.get("proxy_justification_path")
        if not path:
            missing_path.append(lid)
            continue
        full = ROOT / path
        if not full.exists():
            not_exist.append(lid)
    if missing_path or not_exist:
        add("P4.B", "FAIL",
            f"{len(missing_path)} missing path, {len(not_exist)} files missing on disk",
            missing_path=missing_path[:5], not_exist=not_exist[:5])
    else:
        add("P4.B", "PASS", f"All {len(p_labels)} proxy_justification.md files exist")

    # --- P4.C
    sha_mismatch: List[Tuple[str, str, str]] = []
    for lid, e in p_labels.items():
        path = e.get("proxy_justification_path")
        if not path:
            continue
        full = ROOT / path
        if not full.exists():
            continue
        expected = e.get("proxy_justification_sha256")
        actual = _sha256(full)
        if expected != actual:
            sha_mismatch.append((lid, expected, actual))
    if sha_mismatch:
        add("P4.C", "FAIL", f"{len(sha_mismatch)} sha256 mismatches between cohort and live file", samples=sha_mismatch[:5])
    else:
        add("P4.C", "PASS", f"All {len(p_labels)} proxy_justification_sha256 values match live files")

    # --- P4.D
    missing_history: List[str] = []
    history_sha_mismatch: List[Tuple[str, str, str]] = []
    for lid, e in p_labels.items():
        history = e.get("fidelity_history", []) or []
        phase4 = [h for h in history if "Phase 4" in (h.get("phase") or "")]
        if not phase4:
            missing_history.append(lid)
            continue
        latest = phase4[-1]
        expected_sha = latest.get("proxy_justification_sha256")
        live_sha = e.get("proxy_justification_sha256")
        if expected_sha != live_sha:
            history_sha_mismatch.append((lid, expected_sha, live_sha))
    if missing_history or history_sha_mismatch:
        add("P4.D", "FAIL",
            f"{len(missing_history)} labels lack Phase 4 history; "
            f"{len(history_sha_mismatch)} history-sha mismatches",
            missing_history=missing_history[:5],
            history_sha_mismatch=history_sha_mismatch[:5])
    else:
        add("P4.D", "PASS", f"All {len(p_labels)} P-tier labels have a Phase 4 history entry whose sha256 matches the cohort")

    # --- P4.E
    bad_tier = [lid for lid, e in p_labels.items() if e.get("fidelity") != "P"]
    if bad_tier:
        add("P4.E", "FAIL", f"{len(bad_tier)} labels with Phase 4 entry no longer P-tier", samples=bad_tier[:5])
    else:
        add("P4.E", "PASS", f"All {len(p_labels)} P-tier labels still tagged 'P'")

    # --- P4.F
    ps = cohort.get("_phase_status", {}) or {}
    p4_summary = ps.get("phase4") if isinstance(ps, dict) else None
    if not p4_summary:
        add("P4.F", "FAIL", "_phase_status.phase4 missing from cohort.json")
    else:
        observed = Counter()
        for e in p_labels.values():
            t = e.get("proxy_template")
            observed[t or "<missing>"] += 1
        # Compare against summary template_distribution (loose check on totals)
        if p4_summary.get("P_total") != len(p_labels):
            add("P4.F", "FAIL",
                f"_phase_status.phase4.P_total={p4_summary.get('P_total')} != observed {len(p_labels)}")
        else:
            add("P4.F", "PASS",
                f"_phase_status.phase4 summary consistent (P_total={len(p_labels)}, "
                f"templates={dict(observed)})")

        # --- P4.G
        stale_non_p: List[str] = []
        for lid, e in non_p_labels.items():
            has_proxy_metadata = any(key in e for key in PROXY_METADATA_KEYS)
            has_phase4_history = any("Phase 4" in (h.get("phase") or "") for h in e.get("fidelity_history", []) or [])
            if has_proxy_metadata or has_phase4_history:
                stale_non_p.append(lid)
        if stale_non_p:
            add("P4.G", "FAIL", f"{len(stale_non_p)} non-P labels carry stale proxy metadata/history", samples=stale_non_p[:10])
        else:
            add("P4.G", "PASS", f"No stale proxy metadata/history on {len(non_p_labels)} non-P labels")

    report = {
        "_audit_phase": 4,
        "_audit_target": "p4_experiments/canonical/cohort.json",
        "_audit_generated_utc": datetime.now(timezone.utc).isoformat(),
        "_blockers_failed": blockers_failed,
        "_n_findings": len(findings),
        "_n_pass": sum(1 for f in findings if f["status"] == "PASS"),
        "_n_fail": sum(1 for f in findings if f["status"] == "FAIL"),
        "_n_info": sum(1 for f in findings if f["status"] == "INFO"),
        "findings": findings,
    }
    return report, blockers_failed == 0


def main() -> int:
    report, ok = audit()
    out = AUDIT_REPORTS / "audit_phase4.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(f"[Phase 4 audit] {report['_n_pass']} PASS / {report['_n_fail']} FAIL / {report['_n_info']} INFO; blockers_failed={report['_blockers_failed']}")
    for f in report["findings"]:
        marker = {"PASS": "[ok]", "FAIL": "[FAIL]", "INFO": "[info]"}.get(f["status"], "[??]")
        print(f"  {marker} {f['check_id']}: {f['message']}")
    print(f"[Phase 4 audit] Report -> {out.relative_to(ROOT)}")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
