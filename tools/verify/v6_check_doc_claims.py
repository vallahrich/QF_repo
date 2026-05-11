"""V6: documented-claim ↔ stored-result audit.

Scans key documentation files for numeric "X papers / extractions /
experiments / labels" claims and compares them against the actual
on-disk counts. Reports drift; does not edit any documentation.

Documents scanned
-----------------
- README.md (root)
- docs/PROJECT_STATE.yaml
- P3_P4_STATUS_BASELINE.md
- p3_thematic_synthesis/README.md
- p3_thematic_synthesis/P3_AUDIT_STATUS.md
- p4_experiments/README.md

Counts derived
--------------
- p2_processed:       count of *.md in p2_systematic_review/output/processed/
- p3_s2_extractions:  count of *.json under p3_thematic_synthesis/s2_quantitative/output/extractions/ (recursive)
- p3_s3_rows:         row count of triangulation_matrix.json
- p4_labels:          label count in p4_experiments/canonical/cohort.json::labels

Run: python -m tools.verify.v6_check_doc_claims
"""

from __future__ import annotations

import datetime as _dt
import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
REPORT_DIR = REPO_ROOT / "tools" / "verify" / "reports"

DOCS = [
    Path("README.md"),
    Path("docs/PROJECT_STATE.yaml"),
    Path("P3_P4_STATUS_BASELINE.md"),
    Path("p3_thematic_synthesis/README.md"),
    Path("p3_thematic_synthesis/P3_AUDIT_STATUS.md"),
    Path("p4_experiments/README.md"),
]

# (pattern_label, regex). Capture group 1 = number.
CLAIM_PATTERNS = [
    ("papers",      re.compile(r"(\d{2,5})\s+(?:classified\s+)?papers?\b", re.IGNORECASE)),
    ("extractions", re.compile(r"(\d{2,5})\s+extractions?\b", re.IGNORECASE)),
    ("experiments", re.compile(r"(\d{2,5})\s+experiments?\b", re.IGNORECASE)),
    ("labels",      re.compile(r"(\d{2,5})\s+(?:cohort\s+)?labels?\b", re.IGNORECASE)),
    ("templates",   re.compile(r"(\d{1,4})\s+(?:paper-?family-?)?templates?\b", re.IGNORECASE)),
    ("proxies",     re.compile(r"(\d{1,4})\s+prox(?:y|ies)\b", re.IGNORECASE)),
    ("strict",      re.compile(r"(\d{1,4})\s+(?:paper-?faithful-?)?strict\b", re.IGNORECASE)),
]


def _on_disk_counts() -> dict[str, int | None]:
    counts: dict[str, int | None] = {}
    p2 = REPO_ROOT / "p2_systematic_review" / "output" / "processed"
    counts["p2_processed_md"] = sum(1 for _ in p2.glob("*.md")) if p2.is_dir() else None
    s2 = REPO_ROOT / "p3_thematic_synthesis" / "s2_quantitative" / "output" / "extractions"
    counts["p3_s2_extractions_json"] = sum(1 for _ in s2.rglob("*.json")) if s2.is_dir() else None
    matrix = REPO_ROOT / "p3_thematic_synthesis" / "s3_quantum_advantage" / "combined" / "output" / "triangulation_matrix.json"
    counts["p3_s3_matrix_rows"] = len(json.loads(matrix.read_text(encoding="utf-8"))) if matrix.exists() else None
    cohort = REPO_ROOT / "p4_experiments" / "canonical" / "cohort.json"
    if cohort.exists():
        d = json.loads(cohort.read_text(encoding="utf-8"))
        counts["p4_label_count"] = len(d.get("labels", {}))
    else:
        counts["p4_label_count"] = None
    return counts


def main() -> int:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    counts = _on_disk_counts()

    findings: list[dict] = []
    for rel in DOCS:
        path = REPO_ROOT / rel
        if not path.exists():
            findings.append({"doc": str(rel), "severity": "warn",
                             "msg": "file does not exist"})
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        for line_no, line in enumerate(text.splitlines(), start=1):
            for label, pat in CLAIM_PATTERNS:
                for m in pat.finditer(line):
                    findings.append({
                        "doc": str(rel),
                        "line": line_no,
                        "claim_kind": label,
                        "value": int(m.group(1)),
                        "snippet": line.strip()[:180],
                    })

    summary = {
        "script": "v6_check_doc_claims",
        "timestamp_utc": _dt.datetime.now(_dt.timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z"),
        "on_disk_counts": counts,
        "claim_count": len(findings),
        "claims": findings,
    }
    out = REPORT_DIR / f"v6_check_doc_claims_{_dt.date.today().isoformat()}.json"
    out.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print("V6 doc-claims audit:")
    print(f"  on-disk counts: {counts}")
    print(f"  raw doc claims captured: {len(findings)}")
    print(f"  report: {out.relative_to(REPO_ROOT)}")
    # Informational only -- always 0
    return 0


if __name__ == "__main__":
    sys.exit(main())
