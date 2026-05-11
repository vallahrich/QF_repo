"""Render a per-silo F2 request bundle.

For each silo, gathers all F1 papers belonging to that silo from
extractions/papers/, computes coverage statistics deterministically,
and writes a frozen request bundle to:

  s6_silo_framing/briefs/{silo}/_request/f2_request.json

The bundle is what gets handed to the LLM verbatim. It contains:
  - silo
  - prompt_template_version
  - prompt_text (system prompt content)
  - silo_paper_set (canonical paper_id list for this silo, F1-accepted)
  - coverage_stats (deterministic counts; LLM does not need to recount)
  - f1_records (full F1 records for the LLM to synthesise from)

The runner reads this bundle and constructs the user message.

Usage:
  python -m p3_thematic_synthesis.s6_silo_framing.scripts.render_f2_request \
      --silo portfolio_optimization
  python -m p3_thematic_synthesis.s6_silo_framing.scripts.render_f2_request \
      --all-silos
"""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
S6_ROOT = REPO_ROOT / "p3_thematic_synthesis" / "s6_silo_framing"
PROMPT_VERSION = "f2_v1"
PROMPT_PATH = S6_ROOT / "prompts" / "f2_per_silo_aggregation_v1.txt"
INDEX_PATH = S6_ROOT / "input_index" / "paper_silo_index.json"
PAPERS_DIR = S6_ROOT / "extractions" / "papers"
BRIEFS_ROOT = S6_ROOT / "briefs"


def load_f1_records_for_silo(silo: str, silo_paper_ids: list[str]) -> list[dict]:
    """Load all available F1 records for paper_ids in this silo.

    Quote arrays are dropped from the records embedded in F2 bundles —
    the quotes are already verified at sanitise time and persisted in
    extractions/papers/{paper_id}.json for traceability. F2 synthesises
    across the already-verified prose; including quotes again would
    triple bundle size and exceed model context for the larger silos.
    Coverage stats and quote-level evidence remain accessible via the
    paper-keyed F1 outputs.
    """
    quote_fields = {
        "problem_statement_quotes",
        "classical_baseline_quotes",
        "classical_difficulty_quotes",
        "business_stakes_quotes",
    }
    records = []
    for pid in silo_paper_ids:
        path = PAPERS_DIR / f"{pid}.json"
        if not path.exists():
            continue
        with path.open("r", encoding="utf-8") as f:
            full = json.load(f)
        slim = {k: v for k, v in full.items() if k not in quote_fields}
        records.append(slim)
    return records


def compute_coverage(records: list[dict]) -> dict:
    n = len(records)
    fields = ["problem_statement", "classical_baseline", "classical_difficulty", "business_stakes"]
    stats = {"n_papers_in_silo_with_f1": n}
    for f in fields:
        stats[f"n_papers_with_{f}"] = sum(1 for r in records if r.get(f))
    stats["confidence_distribution"] = {}
    for c in ("high", "medium", "low"):
        stats["confidence_distribution"][c] = sum(
            1 for r in records if r.get("extraction_confidence") == c
        )
    return stats


def render_bundle(silo: str, silo_paper_ids: list[str], records: list[dict],
                  prompt_text: str) -> dict:
    accepted_ids = sorted(r["paper_id"] for r in records)
    return {
        "silo": silo,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "prompt_template_version": PROMPT_VERSION,
        "prompt_text": prompt_text,
        "silo_paper_set": accepted_ids,
        "n_papers_in_silo_projection": len(silo_paper_ids),
        "coverage_stats": compute_coverage(records),
        "f1_records": records,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--silo", default=None,
                        help="Render for this silo only.")
    parser.add_argument("--all-silos", action="store_true",
                        help="Render for all 8 silos.")
    parser.add_argument("--overwrite", action="store_true",
                        help="Overwrite existing F2 request bundles.")
    args = parser.parse_args()

    if args.all_silos and args.silo is not None:
        raise SystemExit("Provide --silo OR --all-silos, not both")
    if not args.all_silos and args.silo is None:
        raise SystemExit("Provide --silo or --all-silos")

    if not PROMPT_PATH.exists():
        raise FileNotFoundError(f"F2 prompt not found: {PROMPT_PATH}")
    prompt_text = PROMPT_PATH.read_text(encoding="utf-8")

    index = json.loads(INDEX_PATH.read_text(encoding="utf-8"))
    silos = sorted(index["by_silo"].keys()) if args.all_silos else [args.silo]

    for silo in silos:
        if silo not in index["by_silo"]:
            raise SystemExit(f"Unknown silo: {silo}")
        silo_paper_ids = index["by_silo"][silo]["paper_ids"]
        records = load_f1_records_for_silo(silo, silo_paper_ids)

        out_dir = BRIEFS_ROOT / silo / "_request"
        out_dir.mkdir(parents=True, exist_ok=True)
        out_path = out_dir / "f2_request.json"
        if out_path.exists() and not args.overwrite:
            print(f"  {silo}: bundle exists, skipped (--overwrite to refresh)")
            continue

        bundle = render_bundle(silo, silo_paper_ids, records, prompt_text)
        with out_path.open("w", encoding="utf-8") as f:
            json.dump(bundle, f, indent=2, ensure_ascii=False)
        cov = bundle["coverage_stats"]
        print(f"  {silo}: f1_records={cov['n_papers_in_silo_with_f1']}/"
              f"{bundle['n_papers_in_silo_projection']}  "
              f"problem={cov['n_papers_with_problem_statement']} "
              f"baseline={cov['n_papers_with_classical_baseline']} "
              f"difficulty={cov['n_papers_with_classical_difficulty']} "
              f"stakes={cov['n_papers_with_business_stakes']}  "
              f"-> {out_path.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
