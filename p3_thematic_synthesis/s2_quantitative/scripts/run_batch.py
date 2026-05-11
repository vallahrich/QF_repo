"""Batch runner for benchmark extraction across multiple papers.

.. deprecated::
    This is the LEGACY batch wrapper around ``extract_benchmarks.py``.
    The canonical pipeline is ``run_extraction.py`` (3-step cached-prefix
    architecture with built-in parallelism, validation, and quality scoring).
    Use ``run_extraction.py --parallel 8`` instead.

Loops over paper markdown files, calls extract_benchmarks on each,
logs successes and failures, and writes a batch summary.

Usage:
    # Process 3 papers for testing
    python -m p3_thematic_synthesis.s2_quantitative.scripts.run_batch --limit 3

    # Process specific papers by ID
    python -m p3_thematic_synthesis.s2_quantitative.scripts.run_batch \\
        --paper-ids 02db829631f9 0608ad48d5b8 01877ad38ab2

    # Process all papers (default input: shared/extracted_text/text/)
    python -m p3_thematic_synthesis.s2_quantitative.scripts.run_batch

    # Re-extract even if output already exists
    python -m p3_thematic_synthesis.s2_quantitative.scripts.run_batch --no-skip --limit 5
"""

import argparse
import json
import sys
from pathlib import Path

_QUANT_ROOT = Path(__file__).resolve().parents[1]
_P3_ROOT = Path(__file__).resolve().parents[2]
_PROJECT_ROOT = Path(__file__).resolve().parents[3]

_project_root_str = str(_PROJECT_ROOT)
_p3_str = str(_P3_ROOT)

# Ensure project root is first on sys.path so our 'shared' package wins
if _project_root_str not in sys.path:
    sys.path.insert(0, _project_root_str)
elif sys.path[0] != _project_root_str:
    sys.path.remove(_project_root_str)
    sys.path.insert(0, _project_root_str)
if _p3_str not in sys.path:
    sys.path.insert(1, _p3_str)

_shared_mod = sys.modules.get("shared")
if _shared_mod is not None:
    _shared_file = getattr(_shared_mod, "__file__", None) or ""
    if _PROJECT_ROOT.as_posix() not in Path(_shared_file).as_posix() if _shared_file else True:
        for _key in [k for k in sys.modules if k == "shared" or k.startswith("shared.")]:
            del sys.modules[_key]

from shared.tools.logger import get_logger  # noqa: E402

from p3_thematic_synthesis.s2_quantitative.scripts.extract_benchmarks import (  # noqa: E402
    extract_paper,
)

logger = get_logger("benchmark_batch")

DEFAULT_INPUT = _PROJECT_ROOT / "shared" / "extracted_text" / "text"
OUTPUT_DIR = _QUANT_ROOT / "output" / "extractions"


def _list_papers(
    input_dir: Path,
    paper_ids: list[str] | None = None,
    limit: int | None = None,
) -> list[Path]:
    """List paper markdown files, optionally filtered by IDs or limited."""
    files = sorted(input_dir.glob("*.md"))
    if paper_ids:
        id_set = set(paper_ids)
        files = [f for f in files if f.stem[:12] in id_set]
    if limit:
        files = files[:limit]
    return files


def _already_extracted(paper_path: Path, output_dir: Path) -> bool:
    """Check if an extraction JSON already exists for this paper."""
    paper_id = paper_path.stem[:12]
    return (output_dir / f"{paper_id}.json").is_file()


def run_batch(
    input_dir: str | None = None,
    output_dir: str | None = None,
    paper_ids: list[str] | None = None,
    limit: int | None = None,
    skip_existing: bool = True,
) -> dict:
    """Run extraction on a batch of papers.

    Args:
        input_dir: Directory containing paper markdown files.
        output_dir: Directory for output JSONs.
        paper_ids: Optional list of paper IDs to filter.
        limit: Maximum number of papers to process.
        skip_existing: Skip papers that already have an extraction JSON.

    Returns:
        Summary dict with total, succeeded, failed, skipped counts
        and per-paper results.
    """
    in_dir = Path(input_dir) if input_dir else DEFAULT_INPUT
    out_dir = Path(output_dir) if output_dir else OUTPUT_DIR
    out_dir.mkdir(parents=True, exist_ok=True)

    papers = _list_papers(in_dir, paper_ids, limit)
    logger.info(f"Batch started: {len(papers)} papers in {in_dir}")

    succeeded = 0
    failed = 0
    skipped = 0
    results: list[dict] = []

    for i, paper_path in enumerate(papers, 1):
        paper_id = paper_path.stem[:12]

        if skip_existing and _already_extracted(paper_path, out_dir):
            skipped += 1
            logger.info(f"[{i}/{len(papers)}] Skip {paper_id} (exists)")
            continue

        try:
            logger.info(f"[{i}/{len(papers)}] Extracting {paper_id}...")
            data = extract_paper(str(paper_path), str(out_dir))
            succeeded += 1
            results.append({
                "paper_id": paper_id,
                "status": "success",
                "experiments": len(data.get("experiments", [])),
                "has_quantitative": data.get("has_quantitative_results", False),
            })
        except Exception as exc:
            failed += 1
            logger.error(f"[{i}/{len(papers)}] Failed {paper_id}: {exc}")
            results.append({
                "paper_id": paper_id,
                "status": "error",
                "error": str(exc),
            })

    summary = {
        "total": len(papers),
        "succeeded": succeeded,
        "failed": failed,
        "skipped": skipped,
        "results": results,
    }

    # Save batch log
    log_path = out_dir / "_batch_log.json"
    with open(log_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    logger.info(
        f"Batch complete: {succeeded} ok, {failed} failed, {skipped} skipped"
    )
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description="Batch benchmark extraction.")
    parser.add_argument(
        "--input-dir", default=None,
        help="Directory with paper markdown files. "
             "Defaults to shared/extracted_text/text/.",
    )
    parser.add_argument(
        "--output-dir", default=None,
        help="Output directory for extraction JSONs.",
    )
    parser.add_argument(
        "--paper-ids", nargs="+", default=None,
        help="Extract only these paper IDs (first 12 hex chars of filename).",
    )
    parser.add_argument(
        "--limit", type=int, default=None,
        help="Maximum number of papers to process.",
    )
    parser.add_argument(
        "--no-skip", action="store_true",
        help="Re-extract papers even if output JSON already exists.",
    )
    args = parser.parse_args()

    summary = run_batch(
        input_dir=args.input_dir,
        output_dir=args.output_dir,
        paper_ids=args.paper_ids,
        limit=args.limit,
        skip_existing=not args.no_skip,
    )

    print(
        f"\nBatch complete: {summary['succeeded']} succeeded, "
        f"{summary['failed']} failed, {summary['skipped']} skipped "
        f"(of {summary['total']} total)"
    )


if __name__ == "__main__":
    main()
