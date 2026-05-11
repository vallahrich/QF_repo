"""Run A2 + L3 only on existing A1 codes (hybrid model testing).

Takes codes from one iteration and runs A2 memo + L3 adversarial
with a different model. For testing hypothesis: mini A1 + 5.1 A2.

Usage:
    python p3_thematic_synthesis/scripts/run_a2_l3_only.py \
        --codes-dir iter_10_.../codes \
        --output-dir iter_10_.../memos \
        --model gpt-5.1 \
        --prompt-version v2
"""

import json, logging, os, sys, glob
from datetime import datetime, timezone
from pathlib import Path

_PROJECT_ROOT = str(Path(__file__).resolve().parents[2])
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

from shared.tools.llm_client import LLMClient
from p3_thematic_synthesis.scripts.run_thematic_pipeline import (
    load_prompt, run_a2, run_l3, load_p2_frontmatter,
    load_quantitative_extraction, load_triangulation_verdicts,
    find_text_file, DEFAULT_PROMPT_VERSION, _normalize_whitespace,
)

logging.basicConfig(level=logging.INFO, format="%(levelname)s  %(message)s")
logger = logging.getLogger(__name__)

P2_PROCESSED_DIR = os.path.join(_PROJECT_ROOT, "p2_systematic_review", "output", "processed")


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Run A2+L3 on existing codes")
    parser.add_argument("--codes-dir", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--model", required=True)
    parser.add_argument("--prompt-version", default=DEFAULT_PROMPT_VERSION)
    args = parser.parse_args()

    os.makedirs(args.output_dir, exist_ok=True)
    client = LLMClient()
    triangulation_by_paper = load_triangulation_verdicts()

    code_files = sorted(Path(args.codes_dir).glob("*.jsonl"))
    logger.info("Found %d code files, model=%s, prompts=%s", len(code_files), args.model, args.prompt_version)

    processed = 0
    errors = 0

    for i, code_file in enumerate(code_files, 1):
        paper_id = code_file.stem
        memo_path = os.path.join(args.output_dir, f"{paper_id}.json")

        # Skip if already done
        if os.path.isfile(memo_path) and os.path.getsize(memo_path) > 0:
            logger.info("[%d/%d] Skipping %s — already processed", i, len(code_files), paper_id)
            continue

        # Skip empty code files
        if code_file.stat().st_size == 0:
            logger.info("[%d/%d] Skipping %s — empty codes", i, len(code_files), paper_id)
            continue

        logger.info("[%d/%d] Processing %s", i, len(code_files), paper_id)

        try:
            # Load codes
            codes = []
            for line in open(code_file, encoding="utf-8"):
                if line.strip():
                    codes.append(json.loads(line))

            # Filter to passing codes
            good_codes = [c for c in codes if c.get("l1_status") in ("pass", "pass_fuzzy")]

            # Load enrichment
            p2_meta = load_p2_frontmatter(paper_id)
            quant = load_quantitative_extraction(paper_id)
            tri = triangulation_by_paper.get(paper_id)

            # A2
            logger.info("  A2 memo compression: %s", paper_id)
            memo = run_a2(client, args.model, paper_id, good_codes, p2_meta, quant, tri)

            with open(memo_path, "w", encoding="utf-8") as f:
                json.dump(memo, f, indent=2, ensure_ascii=False)

            # L3
            text_path = find_text_file(paper_id)
            if text_path:
                with open(text_path, encoding="utf-8", errors="replace") as f:
                    paper_text = f.read()
                logger.info("  L3 adversarial check: %s", paper_id)
                l3 = run_l3(client, args.model, paper_id, memo, paper_text)
                with open(os.path.join(args.output_dir, f"{paper_id}_l3.json"), "w", encoding="utf-8") as f:
                    json.dump(l3, f, indent=2, ensure_ascii=False)

            processed += 1

        except Exception as e:
            logger.error("Error on %s: %s", paper_id, e)
            errors += 1

    logger.info("Done: %d processed, %d errors", processed, errors)


if __name__ == "__main__":
    main()
