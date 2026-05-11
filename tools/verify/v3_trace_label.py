"""V3: P4-cohort traceability.

For each label in `p4_experiments/canonical/cohort.json::labels`, walk:
  label -> P3 S2 extraction file -> P3 triangulation row -> P2 processed
  paper -> bridge DOI / Zotero key.

Emits per-label `breaks` array. Does not modify source artifacts; writes a
dated verifier report under `tools/verify/reports/`.

Run: python -m tools.verify.v3_trace_label
"""

from __future__ import annotations

import csv
import datetime as _dt
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
REPORT_DIR = REPO_ROOT / "tools" / "verify" / "reports"

COHORT = REPO_ROOT / "p4_experiments" / "canonical" / "cohort.json"
S2_EXTRACTIONS = REPO_ROOT / "p3_thematic_synthesis" / "s2_quantitative" / "output" / "extractions"
S3_MATRIX = REPO_ROOT / "p3_thematic_synthesis" / "s3_quantum_advantage" / "combined" / "output" / "triangulation_matrix.json"
P2_PROCESSED = REPO_ROOT / "p2_systematic_review" / "output" / "processed"
BRIDGE = REPO_ROOT / "shared" / "bridge" / "paper_id_bridge.csv"
ALLOWLIST = REPO_ROOT / "tools" / "verify" / "v3_trace_label_allowlist.json"


def _load_bridge() -> dict[str, dict]:
    out: dict[str, dict] = {}
    with BRIDGE.open("r", encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            out[row["slr_paper_id"]] = row
    return out


def _load_allowlist() -> list[dict]:
    if not ALLOWLIST.is_file():
        return []
    data = json.loads(ALLOWLIST.read_text(encoding="utf-8"))
    entries = data.get("accepted_exceptions", []) if isinstance(data, dict) else []
    return [e for e in entries if e.get("accepted") is True]


def _accepted_breaks(label_id: str, paper_id: str | None, exp_id: str | None, breaks: list[str], allowlist: list[dict]) -> tuple[list[dict], list[str]]:
    accepted: list[dict] = []
    unaccepted: list[str] = []
    for break_text in breaks:
        match = None
        for entry in allowlist:
            if entry.get("label") != label_id:
                continue
            if entry.get("paper_id") != paper_id:
                continue
            if entry.get("experiment_id") != exp_id:
                continue
            needle = str(entry.get("break_contains") or "")
            if needle and needle not in break_text:
                continue
            match = entry
            break
        if match:
            accepted.append({
                "break": break_text,
                "classification": match.get("classification"),
                "reason": match.get("reason"),
                "source_artifact": match.get("source_artifact"),
                "claim_bearing_use_allowed": match.get("claim_bearing_use_allowed"),
            })
        else:
            unaccepted.append(break_text)
    return accepted, unaccepted


def _index_matrix() -> dict[tuple[str, str], dict]:
    rows = json.loads(S3_MATRIX.read_text(encoding="utf-8"))
    return {(r["paper_id"], r["experiment_id"]): r for r in rows}


def _find_extraction(paper_id: str) -> Path | None:
    """Extractions live under per-silo subdirectories; flat search."""
    if not S2_EXTRACTIONS.is_dir():
        return None
    flat = S2_EXTRACTIONS / f"{paper_id}.json"
    if flat.exists():
        return flat
    for hit in S2_EXTRACTIONS.rglob(f"{paper_id}.json"):
        return hit
    return None


def main() -> int:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    cohort = json.loads(COHORT.read_text(encoding="utf-8"))
    labels = cohort.get("labels", {})
    matrix = _index_matrix()
    bridge = _load_bridge()
    allowlist = _load_allowlist()

    per_label: list[dict] = []
    for lid in sorted(labels):
        L = labels[lid]
        paper_id = L.get("paper_id")
        exp_id = L.get("experiment_id")
        breaks: list[str] = []

        ext_path = _find_extraction(paper_id) if paper_id else None
        if not ext_path:
            breaks.append(f"S2 extraction not found for paper_id={paper_id}")

        if (paper_id, exp_id) not in matrix:
            breaks.append(f"P3 triangulation row not found for ({paper_id}, {exp_id})")

        p2_path = P2_PROCESSED / f"{paper_id}.md" if paper_id else None
        if p2_path is None or not p2_path.exists():
            breaks.append(f"P2 processed paper not found at {p2_path.relative_to(REPO_ROOT) if p2_path else None}")

        if paper_id and paper_id not in bridge:
            breaks.append(f"paper_id={paper_id} missing from shared/bridge/paper_id_bridge.csv")

        accepted_breaks, unaccepted_breaks = _accepted_breaks(lid, paper_id, exp_id, breaks, allowlist)

        per_label.append({
            "label_id": lid,
            "paper_id": paper_id,
            "experiment_id": exp_id,
            "silo": L.get("silo"),
            "fidelity": L.get("fidelity"),
            "breaks": breaks,
            "accepted_breaks": accepted_breaks,
            "unaccepted_breaks": unaccepted_breaks,
        })

    n = len(per_label)
    broken = [r for r in per_label if r["breaks"]]
    accepted_broken = [r for r in broken if r["accepted_breaks"] and not r["unaccepted_breaks"]]
    unaccepted_broken = [r for r in per_label if r["unaccepted_breaks"]]
    summary = {
        "script": "v3_trace_label",
        "timestamp_utc": _dt.datetime.now(_dt.timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z"),
        "label_count": n,
        "allowlist_path": str(ALLOWLIST.relative_to(REPO_ROOT)).replace("\\", "/") if ALLOWLIST.is_file() else None,
        "allowlist_entries": len(allowlist),
        "labels_with_breaks": len(broken),
        "labels_with_accepted_breaks": len(accepted_broken),
        "labels_with_unaccepted_breaks": len(unaccepted_broken),
        "labels_clean_no_breaks": n - len(broken),
        "labels_clean_or_accepted": n - len(unaccepted_broken),
        "per_label": per_label,
    }
    out = REPORT_DIR / f"v3_trace_label_{_dt.date.today().isoformat()}.json"
    out.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(f"V3 traceability: {summary['labels_clean_no_breaks']}/{n} labels clean with no breaks; "
          f"{summary['labels_with_accepted_breaks']} accepted bridge exceptions; "
          f"{summary['labels_with_unaccepted_breaks']} unaccepted breaks")
    print(f"  report: {out.relative_to(REPO_ROOT)}")
    for r in unaccepted_broken[:10]:
        print(f"  [break] {r['label_id']} ({r['paper_id']}, {r['experiment_id']}): {r['unaccepted_breaks']}")
    if len(unaccepted_broken) > 10:
        print(f"  ... ({len(unaccepted_broken) - 10} more in report)")
    if accepted_broken:
        print(f"  accepted exceptions: {len(accepted_broken)} labels; see {ALLOWLIST.relative_to(REPO_ROOT)}")
    return 0 if not unaccepted_broken else 1


if __name__ == "__main__":
    sys.exit(main())
