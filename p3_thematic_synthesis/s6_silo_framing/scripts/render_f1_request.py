"""Render a per-paper F1 request bundle (deduplicated, paper-keyed).

Writes one frozen request bundle per paper to:

    s6_silo_framing/extractions/_requests/{paper_id}.request.json

Multi-silo papers get exactly ONE bundle. The bundle's `silos` field
records all silos the paper projects into; F2 aggregation per silo uses
that field.

Usage:
  # Render bundles for one silo's papers:
  python -m p3_thematic_synthesis.s6_silo_framing.scripts.render_f1_request \
      --silo portfolio_optimization
  # Render bundles for ALL silos:
  python -m p3_thematic_synthesis.s6_silo_framing.scripts.render_f1_request \
      --all-silos
  # Render one specific paper:
  python -m p3_thematic_synthesis.s6_silo_framing.scripts.render_f1_request \
      --paper_id 05a01a257cc7
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
S6_ROOT = REPO_ROOT / "p3_thematic_synthesis" / "s6_silo_framing"
PROMPT_VERSION = "f1_v2"
PROMPT_PATH = S6_ROOT / "prompts" / f"f1_per_paper_extraction_v2.txt"
INDEX_PATH = S6_ROOT / "input_index" / "paper_silo_index.json"


def load_index() -> dict:
    with INDEX_PATH.open("r", encoding="utf-8") as f:
        return json.load(f)


def render_request(paper_id: str, silos: list[str], text_path: str, text_filename: str, prompt_text: str) -> dict:
    rendered_request = (
        f"Extract financial-problem framing from the paper with paper_id "
        f"`{paper_id}` (silos: {', '.join(silos)}).\n\n"
        f"Read the file at:\n  {text_path}\n\n"
        f"Apply the F1 extraction prompt below verbatim. Return ONLY a JSON "
        f"object matching the schema. No markdown wrapping.\n\n"
        f"--- F1 PROMPT (template version {PROMPT_VERSION}) ---\n\n"
        f"{prompt_text}"
    )
    return {
        "paper_id": paper_id,
        "silos": silos,
        "text_path": text_path,
        "text_filename": text_filename,
        "prompt_template_version": PROMPT_VERSION,
        "prompt_text": prompt_text,
        "rendered_request": rendered_request,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--silo", default=None,
                        help="Render bundles for all paper_ids in this silo.")
    parser.add_argument("--all-silos", action="store_true",
                        help="Render bundles for every paper in the index (deduplicated).")
    parser.add_argument("--paper_id", default=None,
                        help="Render only this specific paper.")
    parser.add_argument("--overwrite", action="store_true",
                        help="Overwrite existing request bundles.")
    args = parser.parse_args()

    n_modes = sum(int(x is not None and x is not False) for x in
                  [args.silo, args.paper_id]) + int(args.all_silos)
    if n_modes != 1:
        raise SystemExit("Provide exactly one of: --silo, --all-silos, --paper_id")

    if not PROMPT_PATH.exists():
        raise FileNotFoundError(f"Prompt not found: {PROMPT_PATH}")
    prompt_text = PROMPT_PATH.read_text(encoding="utf-8")

    index = load_index()

    # Build a deduplicated target set of paper_ids
    if args.paper_id is not None:
        if args.paper_id not in index["papers"]:
            raise SystemExit(f"paper_id {args.paper_id} not in index")
        target_ids: list[str] = [args.paper_id]
    elif args.all_silos:
        target_ids = sorted(index["papers"].keys())
    else:  # --silo
        if args.silo not in index["by_silo"]:
            raise SystemExit(f"Unknown silo: {args.silo}")
        target_ids = sorted(index["by_silo"][args.silo]["paper_ids"])

    out_dir = S6_ROOT / "extractions" / "_requests"
    out_dir.mkdir(parents=True, exist_ok=True)

    n_written = 0
    n_skipped = 0
    n_missing_text = 0
    for pid in target_ids:
        rec = index["papers"][pid]
        if rec["text_path"] is None:
            print(f"  [missing text] {pid}")
            n_missing_text += 1
            continue
        out_path = out_dir / f"{pid}.request.json"
        if out_path.exists() and not args.overwrite:
            n_skipped += 1
            continue
        bundle = render_request(
            paper_id=pid,
            silos=rec["silos"],
            text_path=rec["text_path"],
            text_filename=rec["text_filename"],
            prompt_text=prompt_text,
        )
        with out_path.open("w", encoding="utf-8") as f:
            json.dump(bundle, f, indent=2, ensure_ascii=False)
        n_written += 1

    print(f"papers targeted: {len(target_ids)}")
    print(f"  bundles written: {n_written}")
    print(f"  bundles skipped (already exist): {n_skipped}")
    print(f"  papers missing text: {n_missing_text}")
    print(f"  output dir: {out_dir}")


if __name__ == "__main__":
    main()
