#!/usr/bin/env python3
"""DEPRECATED — single-paper diagnostic orchestrator.

.. deprecated:: 2026-05-02 (pre-freeze)
   This script is **not** the path that produced the 777-paper corpus under
   ``output/processed/``. The production path is
   ``s2_classification/scripts/run_classification.py`` (Pipeline C: 6-step
   cached-prefix batch with parallel workers). Use this script only for
   single-paper diagnostics or when ``fetch_from_zotero.py`` shells out to
   it (see ``scripts/fetch_from_zotero.py:412``). Do **not** use it to
   produce or augment the production corpus.

Usage:
    python -m p2_systematic_review.s2_classification.scripts.extract_paper --pdf output/raw_pdfs/paper.pdf --name 2024_Author_Title.md
"""

import argparse
import os
import shutil
import sys
from pathlib import Path

# Ensure project root and p2_systematic_review root are on sys.path
_STEP2_ROOT = str(Path(__file__).resolve().parents[2])
_PROJECT_ROOT = str(Path(__file__).resolve().parents[3])
for p in (_STEP2_ROOT, _PROJECT_ROOT):
    if p not in sys.path:
        sys.path.insert(0, p)

from p2_systematic_review.s2_classification.scripts.extract_pdf_text import extract_text
from shared.tools.logger import get_logger
from p2_systematic_review.s2_classification.utils.step_runner import run_step

logger = get_logger("extract_paper")

STEP2_ROOT = _STEP2_ROOT
PROCESSED_DIR = os.path.join(STEP2_ROOT, "output", "processed")
RAW_PDFS_DIR = os.path.join(STEP2_ROOT, "output", "raw_pdfs")
TEMPLATE_PATH = os.path.join(STEP2_ROOT, "s2_classification", "templates", "paper_base.md")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run full extraction pipeline on a single paper.",
    )
    parser.add_argument("--pdf", required=True, help="Path to the PDF file")
    parser.add_argument(
        "--name",
        required=True,
        help="Output filename (e.g. 2024_Author_Title.md)",
    )
    parser.add_argument(
        "--from-step",
        type=int,
        default=1,
        choices=range(1, 7),
        dest="from_step",
        help="Start from this step (default: 1)",
    )
    args = parser.parse_args()

    # Validate PDF
    if not os.path.isfile(args.pdf):
        logger.error("PDF not found: %s", args.pdf)
        sys.exit(1)

    paper_name = args.name
    if not paper_name.endswith(".md"):
        paper_name += ".md"

    paper_path = os.path.join(PROCESSED_DIR, paper_name)

    # Create paper file from template if needed
    if not os.path.isfile(paper_path):
        os.makedirs(PROCESSED_DIR, exist_ok=True)
        shutil.copy2(TEMPLATE_PATH, paper_path)
        logger.info("Created paper file from template: %s", paper_name)

    # Extract PDF text (or load from cache)
    cache_path = os.path.join(RAW_PDFS_DIR, paper_name.replace(".md", ".txt"))
    if os.path.isfile(cache_path):
        logger.info("Loading cached PDF text from %s", cache_path)
        with open(cache_path, "r", encoding="utf-8") as f:
            pdf_text = f.read()
    else:
        pdf_text, is_valid = extract_text(args.pdf)
        if not is_valid:
            logger.warning(
                "PDF has very little extractable text (likely scanned): %s",
                args.pdf,
            )
        os.makedirs(RAW_PDFS_DIR, exist_ok=True)
        with open(cache_path, "w", encoding="utf-8") as f:
            f.write(pdf_text)
        logger.info("Cached PDF text to %s", cache_path)

    # Run steps
    steps = list(range(args.from_step, 7))
    succeeded: list[int] = []
    failed: list[int] = []

    for step_num in steps:
        try:
            run_step(
                paper_path,
                step_num,
                pdf_text=pdf_text if step_num <= 5 else None,
            )
            succeeded.append(step_num)
            logger.info("Step %d completed successfully", step_num)
        except Exception as exc:
            logger.error("Step %d failed: %s", step_num, exc)
            failed.append(step_num)
            break  # Stop on first failure

    # Summary
    print(f"\n{'=' * 50}")
    print(f"Paper: {paper_name}")
    print(f"Steps completed: {succeeded}")
    if failed:
        print(f"Steps failed: {failed}")
        skipped = [s for s in steps if s not in succeeded and s not in failed]
        if skipped:
            print(f"Steps skipped: {skipped}")
    print(f"Output: {paper_path}")
    print(f"{'=' * 50}")

    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
