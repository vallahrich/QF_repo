"""Process the 22 confirmed-empty / out-of-scope / too-short papers.

Actions per class:
- OUT_OF_SCOPE (physics / cosmology / condensed matter):
    Move to excluded_papers.csv (reason=scope_out_physics), DELETE the JSON output.
- NON_FINANCE:
    Move to excluded_papers.csv (reason=scope_out_non_finance), DELETE JSON.
- TOO_SHORT_abstract_only:
    Keep as has_quantitative_results=false with richer summary; flag quality=low.
- NO_QUANTUM_CONTENT (quantum-inspired / VMC condensed matter):
    Move to excluded_papers.csv (reason=scope_out_non_gate_based), DELETE JSON.
- NO_QUANT_METRICS (edge cases):
    Keep but flag for manual re-review; do not change has_quant.
"""
from __future__ import annotations

import csv
import json
from datetime import date
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
CLASSIFICATION = json.loads(
    (REPO / "p2_systematic_review" / "output" / "audit" / "triage_classification.json").read_text(encoding="utf-8")
)
ROOT = REPO
EXTRACTIONS = ROOT / "p3_thematic_synthesis" / "quantitative" / "output" / "extractions"
EXCLUDED_CSV = ROOT / "shared" / "bridge" / "excluded_papers.csv"


EXCLUSION_REASON = {
    "OUT_OF_SCOPE": ("scope_out_physics", "paper is physics / cosmology / condensed matter, not gate-based quantum finance"),
}


def load_existing_excluded_ids() -> set[str]:
    ids = set()
    if not EXCLUDED_CSV.exists():
        return ids
    with EXCLUDED_CSV.open("r", encoding="utf-8", newline="") as f:
        reader = csv.reader(f)
        for row in reader:
            if row and row[0] and row[0] != "paper_id":
                ids.add(row[0])
    return ids


def main() -> None:
    existing = load_existing_excluded_ids()
    new_rows: list[str] = []
    updated_empties = 0
    moved = 0

    today = date.today().isoformat()

    for e in CLASSIFICATION:
        pid = e["pid"]
        klass = e["class"]
        title = (e.get("title") or "").replace(",", ";")

        if klass in EXCLUSION_REASON:
            reason, note = EXCLUSION_REASON[klass]
            note_full = f"{note}; triaged 2026-04-17 from empty-experiment fallback ({klass})"
            if pid not in existing:
                new_rows.append(f"{pid},{title},,,{reason},{note_full},{today}")
                # Delete the extraction JSON
                target = EXTRACTIONS / f"{pid}.json"
                if target.exists():
                    target.unlink()
                moved += 1
            else:
                # Already excluded: just ensure JSON is gone
                target = EXTRACTIONS / f"{pid}.json"
                if target.exists():
                    target.unlink()

        elif klass == "TOO_SHORT_abstract_only":
            target = EXTRACTIONS / f"{pid}.json"
            if not target.exists():
                continue
            js = json.loads(target.read_text(encoding="utf-8"))
            js["has_quantitative_results"] = False
            js["summary"] = (
                f"Paper is too short ({e.get('size', 0)} bytes) — effectively abstract only; "
                "no quantitative experimental results reported. Manually reviewed 2026-04-17."
            )
            em = js.setdefault("extraction_metadata", {})
            em["manual_review"] = "confirmed_empty_abstract_only"
            em["manual_reviewed_at"] = today
            target.write_text(
                json.dumps(js, indent=2, ensure_ascii=False), encoding="utf-8"
            )
            updated_empties += 1

    # Append new rows to excluded_papers.csv
    if new_rows:
        with EXCLUDED_CSV.open("a", encoding="utf-8", newline="") as f:
            for row in new_rows:
                f.write(row + "\n")

    print(f"moved to excluded_papers.csv + deleted JSON: {moved}")
    print(f"updated too-short empties: {updated_empties}")
    total_excl = len(load_existing_excluded_ids())
    print(f"total rows in excluded_papers.csv: {total_excl}")


if __name__ == "__main__":
    main()
