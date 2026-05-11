"""DEPRECATED — CLI interface for running extraction steps on papers.

.. deprecated:: 2026-05-02 (pre-freeze)
   This script is **not** the path that produced the 777-paper corpus.
   Use ``run_classification.py`` (Pipeline C) for production batch runs.
   This single-step CLI is retained for diagnostic re-runs of one paper /
   one step (e.g., debugging a step-3 prompt change). Per-step prompts
   ``step{1..6}_*.txt`` are *not* the production prompt set; the cached
   ``cached_step{1..5}.txt`` + ``step6_synthesis.txt`` pair is.

Usage examples:
    # Run a specific step on a specific paper
    python scripts/run_extraction_step.py --paper 2023_Bova_QuantumFinance.md --step 1

    # Run from a step onwards
    python scripts/run_extraction_step.py --paper 2023_Bova_QuantumFinance.md --from-step 3

    # Batch mode (all papers in papers/processed/)
    python scripts/run_extraction_step.py --batch --step 6

    # Batch with filter
    python scripts/run_extraction_step.py --batch --filter auto_detected=false --from-step 2

    # New paper from PDF
    python scripts/run_extraction_step.py --paper 2023_Bova_QuantumFinance.md --step 1 --pdf papers/raw_pdfs/bova.pdf
"""

import argparse
import os
import shutil
import sys
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

# Ensure project root is on sys.path
_STEP2_ROOT = str(Path(__file__).resolve().parents[2])
_PROJECT_ROOT = str(Path(__file__).resolve().parents[3])
for p in (_STEP2_ROOT, _PROJECT_ROOT):
    if p not in sys.path:
        sys.path.insert(0, p)

from p2_systematic_review.s2_classification.scripts.extract_pdf_text import extract_text  # noqa: E402
from p2_systematic_review.s2_classification.utils.frontmatter import read_frontmatter  # noqa: E402
from shared.tools.logger import get_logger  # noqa: E402
from p2_systematic_review.s2_classification.utils.processing_log import (  # noqa: E402
    get_paper_status,
    get_papers_by_filter,
    load_log,
)
from p2_systematic_review.s2_classification.utils.step_runner import run_step  # noqa: E402

logger = get_logger("run_extraction_step")


STEP2_ROOT = _STEP2_ROOT
PROCESSED_DIR = os.path.join(STEP2_ROOT, "output", "processed")
RAW_PDFS_DIR = os.path.join(STEP2_ROOT, "output", "raw_pdfs")
TEMPLATE_PATH = os.path.join(STEP2_ROOT, "s2_classification", "templates", "paper_base.md")


def _load_pdf_text(paper_name: str, pdf_path: str | None = None) -> str | None:
    """Load PDF text, using cache if available.

    Priority:
    1. Cached text file in papers/raw_pdfs/{paper_name}.txt
    2. Extract from --pdf path, then cache
    3. None (caller must handle)
    """
    # Check for cached text
    cache_path = os.path.join(RAW_PDFS_DIR, paper_name.replace(".md", ".txt"))
    if os.path.isfile(cache_path):
        logger.info("Loading cached PDF text from %s", cache_path)
        with open(cache_path, "r", encoding="utf-8") as f:
            return f.read()

    # Extract from PDF if path provided
    if pdf_path:
        if not os.path.isfile(pdf_path):
            logger.error("PDF file not found: %s", pdf_path)
            return None

        text, is_valid = extract_text(pdf_path)
        if not is_valid:
            logger.warning(
                "PDF has very little extractable text (likely scanned/image-only): %s",
                pdf_path,
            )

        # Cache the extracted text
        os.makedirs(RAW_PDFS_DIR, exist_ok=True)
        with open(cache_path, "w", encoding="utf-8") as f:
            f.write(text)
        logger.info("Cached PDF text to %s", cache_path)

        return text

    return None


def _ensure_paper_file(paper_name: str) -> str:
    """Ensure the paper .md file exists, creating from template if needed.

    Returns the full path to the paper file.
    """
    paper_path = os.path.join(PROCESSED_DIR, paper_name)
    if not os.path.isfile(paper_path):
        os.makedirs(PROCESSED_DIR, exist_ok=True)
        shutil.copy2(TEMPLATE_PATH, paper_path)
        logger.info("Created paper file from template: %s", paper_name)
    return paper_path


def _get_batch_papers(filter_str: str | None = None) -> list[str]:
    """Get list of paper filenames for batch processing.

    If filter_str is provided (format: key=value), filter papers using
    the processing log. Otherwise, return all .md files in papers/processed/.
    """
    if filter_str:
        if "=" not in filter_str:
            logger.error("Invalid filter format. Use key=value (e.g. auto_detected=false)")
            return []

        key, value = filter_str.split("=", 1)

        # Type-coerce common values
        if value.lower() == "true":
            value = True
        elif value.lower() == "false":
            value = False
        elif value.isdigit():
            value = int(value)

        papers = get_papers_by_filter(key, value)
        logger.info("Filter %s=%s matched %d papers", key, value, len(papers))
        return papers

    # All .md files in papers/processed/
    if not os.path.isdir(PROCESSED_DIR):
        return []
    return sorted(
        f for f in os.listdir(PROCESSED_DIR)
        if f.endswith(".md")
    )


def _run_steps_on_paper(
    paper_name: str,
    steps: list[int],
    pdf_path: str | None = None,
) -> bool:
    """Run a list of steps on a single paper. Returns True if all succeed."""
    paper_path_full = _ensure_paper_file(paper_name)

    # Load PDF text if needed (steps 1-5)
    pdf_text = None
    needs_pdf = any(s <= 5 for s in steps)
    if needs_pdf:
        pdf_text = _load_pdf_text(paper_name, pdf_path)
        if pdf_text is None:
            logger.error(
                "No PDF text available for %s. "
                "Provide --pdf or ensure cached text exists in papers/raw_pdfs/",
                paper_name,
            )
            return False

    all_ok = True
    for step_num in steps:
        try:
            run_step(paper_path_full, step_num, pdf_text=pdf_text)
        except Exception as exc:
            logger.error(
                "Step %d failed for %s: %s",
                step_num,
                paper_name,
                exc,
            )
            all_ok = False
            break  # Stop running further steps on failure

    return all_ok


def build_parser() -> argparse.ArgumentParser:
    """Build the argument parser."""
    parser = argparse.ArgumentParser(
        description="Run extraction steps on papers in the SLR pipeline.",
        epilog=(
            "Examples:\n"
            "  %(prog)s --paper 2023_Bova_QF.md --step 1\n"
            "  %(prog)s --paper 2023_Bova_QF.md --from-step 3\n"
            "  %(prog)s --batch --step 6\n"
            "  %(prog)s --batch --filter auto_detected=false --from-step 2\n"
            "  %(prog)s --paper 2023_Bova_QF.md --step 1 --pdf papers/raw_pdfs/bova.pdf\n"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--paper",
        help="Filename of the paper (e.g. 2023_Bova_QuantumFinance.md)",
    )
    parser.add_argument(
        "--step",
        type=int,
        choices=range(1, 7),
        help="Run a specific step (1-6)",
    )
    parser.add_argument(
        "--from-step",
        type=int,
        choices=range(1, 7),
        dest="from_step",
        help="Run from this step through step 6",
    )
    parser.add_argument(
        "--batch",
        action="store_true",
        help="Run on all papers in papers/processed/",
    )
    parser.add_argument(
        "--filter",
        help="Filter papers by processing_log field (format: key=value). Requires --batch.",
    )
    parser.add_argument(
        "--pdf",
        help="Path to the PDF file. Used to extract text for a new paper.",
    )
    parser.add_argument(
        "--workers",
        type=int,
        default=10,
        help="Number of parallel workers for batch mode (default: 10)",
    )
    return parser


def validate_args(args: argparse.Namespace) -> str | None:
    """Validate argument combinations. Returns error message or None."""
    if not args.batch and not args.paper:
        return "Either --paper or --batch is required."

    if not args.step and not args.from_step:
        return "Either --step or --from-step is required."

    if args.step and args.from_step:
        return "--step and --from-step are mutually exclusive."

    if args.filter and not args.batch:
        return "--filter requires --batch."

    if args.batch and args.paper:
        return "--batch and --paper are mutually exclusive."

    if args.workers and args.workers < 1:
        return "--workers must be at least 1."

    return None


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    error = validate_args(args)
    if error:
        parser.error(error)

    # Determine which steps to run
    if args.step:
        steps = [args.step]
    else:
        steps = list(range(args.from_step, 7))

    # Single paper mode
    if args.paper:
        success = _run_steps_on_paper(args.paper, steps, pdf_path=args.pdf)
        sys.exit(0 if success else 1)

    # Batch mode
    papers = _get_batch_papers(args.filter)
    if not papers:
        logger.warning("No papers found for processing.")
        sys.exit(0)

    total = len(papers)
    workers = min(args.workers, total)
    logger.info(
        "Batch processing %d papers, steps %s, workers %d",
        total, steps, workers,
    )

    # Thread-safe counters
    _counter_lock = threading.Lock()
    succeeded = 0
    failed = 0

    if workers == 1:
        # Sequential fallback — no threading overhead
        for paper_name in papers:
            ok = _run_steps_on_paper(paper_name, steps, pdf_path=args.pdf)
            if ok:
                succeeded += 1
            else:
                failed += 1
            logger.info(
                "[%d/%d] %s — %s",
                succeeded + failed, total, paper_name,
                "ok" if ok else "FAILED",
            )
    else:
        with ThreadPoolExecutor(max_workers=workers) as pool:
            futures = {
                pool.submit(_run_steps_on_paper, p, steps, args.pdf): p
                for p in papers
            }
            for future in as_completed(futures):
                paper_name = futures[future]
                try:
                    ok = future.result()
                except Exception as exc:
                    logger.error("Unhandled error for %s: %s", paper_name, exc)
                    ok = False
                with _counter_lock:
                    if ok:
                        succeeded += 1
                    else:
                        failed += 1
                    done = succeeded + failed
                logger.info(
                    "[%d/%d] %s — %s (%d failed so far)",
                    done, total, paper_name,
                    "ok" if ok else "FAILED", failed,
                )

    logger.info(
        "Batch complete: %d succeeded, %d failed out of %d",
        succeeded,
        failed,
        total,
    )
    sys.exit(0 if failed == 0 else 1)


if __name__ == "__main__":
    main()
