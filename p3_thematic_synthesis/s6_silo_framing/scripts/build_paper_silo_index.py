"""Build the canonical paper -> silo(s) -> text-file index for s6_silo_framing.

Reads all 8 projection_manifest.json files from
p3_thematic_synthesis/s4_thematic_coding/{silo}/projection_manifest.json
and the file listing of shared/extracted_text/text/, then produces:

    s6_silo_framing/input_index/paper_silo_index.json

Schema:

{
  "generated_at": "<iso timestamp>",
  "n_papers_total": <int>,
  "n_papers_single_silo": <int>,
  "n_papers_multi_silo": <int>,
  "n_papers_missing_text": <int>,
  "by_silo": {
    "<silo_name>": {
      "n_papers": <int>,
      "paper_ids": ["..."]
    },
    ...
  },
  "papers": {
    "<paper_id>": {
      "silos": ["..."],
      "memo_types": {"<silo>": "central" | "overlay", ...},
      "text_path": "<absolute path>" | null,
      "text_filename": "<basename>" | null
    },
    ...
  },
  "missing_text": ["<paper_id>", ...]
}
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
P3_ROOT = REPO_ROOT / "p3_thematic_synthesis"
S4_ROOT = P3_ROOT / "s4_thematic_coding"
S6_ROOT = P3_ROOT / "s6_silo_framing"
TEXT_DIR = REPO_ROOT / "shared" / "extracted_text" / "text"

ACTIVE_SILOS = [
    "credit_lending",
    "derivative_pricing",
    "fraud_detection",
    "portfolio_optimization",
    "quantum_ml_finance",
    "risk_management",
    "simulation_monte_carlo",
    "trading_execution",
]


def load_projection_manifest(silo: str) -> dict:
    path = S4_ROOT / silo / "projection_manifest.json"
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def build_text_file_index() -> dict[str, str]:
    """Map paper_id -> filename (basename) for files in shared/extracted_text/text/.

    Filenames look like: "{paper_id}_{slug}.md" or just "{paper_id}.md".
    """
    index: dict[str, str] = {}
    for entry in TEXT_DIR.iterdir():
        if not entry.is_file() or entry.suffix != ".md":
            continue
        name = entry.name
        stem = entry.stem
        # paper_id is the leading 12-hex-char token before underscore (or whole stem)
        if "_" in stem:
            pid = stem.split("_", 1)[0]
        else:
            pid = stem
        if len(pid) == 12 and all(c in "0123456789abcdef" for c in pid):
            if pid in index:
                # Ambiguous: two files for the same paper_id. Prefer the first deterministically.
                if name < index[pid]:
                    index[pid] = name
            else:
                index[pid] = name
    return index


def main() -> None:
    text_index = build_text_file_index()

    papers: dict[str, dict] = {}
    by_silo: dict[str, dict] = {}

    for silo in ACTIVE_SILOS:
        manifest = load_projection_manifest(silo)
        silo_paper_ids: list[str] = []
        for entry in manifest.get("papers", []):
            pid = entry["paper_id"]
            silo_paper_ids.append(pid)

            if pid not in papers:
                papers[pid] = {
                    "silos": [],
                    "memo_types": {},
                    "text_path": None,
                    "text_filename": None,
                }
            if silo not in papers[pid]["silos"]:
                papers[pid]["silos"].append(silo)
            papers[pid]["memo_types"][silo] = entry.get("memo_type")

        by_silo[silo] = {
            "n_papers": len(silo_paper_ids),
            "paper_ids": silo_paper_ids,
        }

    # Resolve text paths
    missing: list[str] = []
    for pid, rec in papers.items():
        fname = text_index.get(pid)
        if fname is None:
            missing.append(pid)
        else:
            rec["text_filename"] = fname
            rec["text_path"] = str((TEXT_DIR / fname).resolve())

    n_total = len(papers)
    n_single = sum(1 for r in papers.values() if len(r["silos"]) == 1)
    n_multi = n_total - n_single

    output = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "n_papers_total": n_total,
        "n_papers_single_silo": n_single,
        "n_papers_multi_silo": n_multi,
        "n_papers_missing_text": len(missing),
        "by_silo": by_silo,
        "papers": papers,
        "missing_text": sorted(missing),
    }

    out_path = S6_ROOT / "input_index" / "paper_silo_index.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print(f"Wrote {out_path}")
    print(f"  papers total: {n_total}")
    print(f"  single-silo:  {n_single}")
    print(f"  multi-silo:   {n_multi}")
    print(f"  missing text: {len(missing)}")
    if missing:
        print(f"  first few missing: {missing[:5]}")


if __name__ == "__main__":
    main()
