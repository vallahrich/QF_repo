#!/usr/bin/env python3
"""Batch classification — Pipeline C (6-step cached prefix) for 777 papers.

Uses cached-prefix prompts (paper text first) so steps 2-5 get Azure's
88% cached-input discount. Papers >200K tokens are split into overlapping
chunks and results merged.

Usage:
    # Dry run — show what would be processed, no LLM calls
    python -m p2_systematic_review.s2_classification.scripts.run_classification --dry-run

    # Run all 6 steps on all unprocessed papers
    python -m p2_systematic_review.s2_classification.scripts.run_classification

    # Run only specific steps
    python -m p2_systematic_review.s2_classification.scripts.run_classification --step 1
    python -m p2_systematic_review.s2_classification.scripts.run_classification --from-step 3

    # Limit to N papers (for testing)
    python -m p2_systematic_review.s2_classification.scripts.run_classification --limit 5

    # Process a single paper
    python -m p2_systematic_review.s2_classification.scripts.run_classification --paper-id 0067a26ce270

    # Use a specific model
    python -m p2_systematic_review.s2_classification.scripts.run_classification --model gpt-5-mini
"""

import argparse
import csv
import json
import os
import shutil
import sys
import time
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

# ── Path setup ────────────────────────────────────────────────────────────

_SCRIPT_DIR = Path(__file__).resolve().parent
_S2_ROOT = _SCRIPT_DIR.parent                     # s2_classification/
_P2_ROOT = _S2_ROOT.parent                        # p2_systematic_review/
_PROJECT_ROOT = _P2_ROOT.parent                   # quantum-finance/

for p in (str(_P2_ROOT), str(_PROJECT_ROOT)):
    if p not in sys.path:
        sys.path.insert(0, p)

from shared.tools.llm_client import LLMClient
from shared.tools.logger import get_logger

logger = get_logger("run_classification")

# ── Config ────────────────────────────────────────────────────────────────

TEXT_DIR = _PROJECT_ROOT / "shared" / "extracted_text" / "text"
INCLUDED_CSV = _P2_ROOT / "s1_slr" / "03_screening" / "included_for_coding.csv"
PROCESSED_DIR = _P2_ROOT / "output" / "processed"
TEMPLATE_PATH = _S2_ROOT / "templates" / "paper_base.md"
PROMPTS_DIR = _S2_ROOT / "prompts"

DEFAULT_MODEL = "gpt-5-mini"
TEMPERATURE = 0.2

# Chunking: split papers >800K chars (~200K tokens) into overlapping chunks
MAX_CHUNK_CHARS = 800000
OVERLAP_CHARS = 4000

# Step definitions: (prompt_file, extra_variables, max_output_tokens)
# Steps 1-5 use cached_step*.txt (paper text as prefix for caching)
# Step 6 uses step6_synthesis.txt (reads extracted content, not paper text)
STEP_DEFS = {
    1: ("cached_step1.txt", {}, 2000),
    2: ("cached_step2.txt", {"source_type": "unknown"}, 4000),
    3: ("cached_step3.txt", {"source_type": "unknown"}, 10000),
    4: ("cached_step4.txt", {"source_type": "unknown"}, 8000),
    5: ("cached_step5.txt", {"source_type": "unknown"}, 6000),
    6: ("step6_synthesis.txt", {}, 8000),
}


# ── Helpers ───────────────────────────────────────────────────────────────

def load_included_ids() -> set[str]:
    with open(INCLUDED_CSV, "r", encoding="utf-8") as f:
        return {row["paper_id"] for row in csv.DictReader(f)}


def find_text_file(paper_id: str) -> str | None:
    matches = [
        f for f in os.listdir(TEXT_DIR)
        if f.endswith(".md") and f.startswith(paper_id)
    ]
    if not matches:
        return None
    matches.sort(key=len, reverse=True)
    return str(TEXT_DIR / matches[0])


def load_full_text(path: str) -> str:
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        return f.read()


def load_prompt(filename: str) -> str:
    with open(PROMPTS_DIR / filename, "r", encoding="utf-8") as f:
        return f.read()


def chunk_text(text: str) -> list[str]:
    """Split text into overlapping chunks if >MAX_CHUNK_CHARS."""
    if len(text) <= MAX_CHUNK_CHARS:
        return [text]
    chunks = []
    start = 0
    while start < len(text):
        end = start + MAX_CHUNK_CHARS
        if end >= len(text):
            chunks.append(text[start:])
            break
        split_at = text.rfind("\n\n", start + MAX_CHUNK_CHARS - 20000, end)
        if split_at == -1:
            split_at = text.rfind("\n", start + MAX_CHUNK_CHARS - 5000, end)
        if split_at == -1:
            split_at = end
        chunks.append(text[start:split_at])
        start = split_at - OVERLAP_CHARS
    logger.info("Split %d chars into %d chunks: %s",
                len(text), len(chunks), [len(c) for c in chunks])
    return chunks


def merge_chunk_results(results_list: list[dict]) -> dict:
    """Merge extraction results from multiple chunks."""
    if len(results_list) == 1:
        return results_list[0]
    merged = dict(results_list[0])
    list_fields = [
        "algorithms_used", "frameworks", "key_findings", "performance_claims",
        "limitations", "open_questions", "topic_tags", "methodology_tags",
        "idea_tags", "contradiction_flags", "key_ideas", "contradictions",
        "related_papers", "future_work",
    ]
    for field in list_fields:
        combined = []
        seen = set()
        for r in results_list:
            for item in r.get(field, []) or []:
                s = str(item)
                if s not in seen:
                    seen.add(s)
                    combined.append(item)
        merged[field] = combined
    for field in ["results_summary", "methodology_description", "abstract_summary"]:
        parts = [r.get(field, "") for r in results_list if r.get(field)]
        if len(parts) > 1:
            merged[field] = " ".join(parts)
    # Take strongest quantum advantage claim
    qa_rank = {"demonstrated": 4, "theoretical": 3, "speculative": 2, "disputed": 1, "not-applicable": 0}
    best_qa = "not-applicable"
    for r in results_list:
        qa = r.get("quantum_advantage_claim", "not-applicable")
        if qa_rank.get(qa, 0) > qa_rank.get(best_qa, 0):
            best_qa = qa
            merged["quantum_advantage_detail"] = r.get("quantum_advantage_detail", "")
    merged["quantum_advantage_claim"] = best_qa
    merged["has_quantitative_results"] = any(
        r.get("has_quantitative_results", False) for r in results_list
    )
    qubits = [r.get("qubit_count") for r in results_list if r.get("qubit_count")]
    merged["qubit_count"] = max(qubits) if qubits else None
    merged["_chunks_used"] = len(results_list)
    return merged


def ensure_output_file(paper_id: str) -> str:
    """Create output markdown from template if it doesn't exist."""
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    out_path = str(PROCESSED_DIR / f"{paper_id}.md")
    if not os.path.isfile(out_path):
        shutil.copy2(str(TEMPLATE_PATH), out_path)
    return out_path


def get_completed_steps(paper_id: str) -> list[int]:
    """Read completed steps from processing_log.json or infer from output size."""
    # Check processing log first
    log_path = _P2_ROOT / "processing_log.json"
    if log_path.exists():
        with open(log_path, "r", encoding="utf-8") as f:
            log = json.load(f)
        steps = log.get("papers", {}).get(f"{paper_id}.md", {}).get("steps_completed", [])
        if steps:
            return steps
    # Fallback: if output markdown is large (>3KB), all steps were completed
    md_path = PROCESSED_DIR / f"{paper_id}.md"
    if md_path.exists() and md_path.stat().st_size > 3000:
        return [1, 2, 3, 4, 5, 6]
    return []


def save_result(paper_id: str, result: dict) -> None:
    """Save the full extraction result as JSON."""
    path = PROCESSED_DIR / f"{paper_id}_extraction.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False, default=str)


# ── Pipeline C: 6-step cached prefix ─────────────────────────────────────

def run_paper(
    client: LLMClient,
    paper_id: str,
    text: str,
    target_steps: list[int],
    model: str,
    dry_run: bool,
) -> dict:
    """Run Pipeline C on a single paper.

    Paper text is placed at the start of each prompt (steps 1-5) so Azure
    caches the prefix and charges cached-input rate on steps 2-5.
    """
    chunks = chunk_text(text)
    all_chunk_results = []

    for ci, chunk in enumerate(chunks):
        chunk_label = f"chunk {ci+1}/{len(chunks)}" if len(chunks) > 1 else ""
        results = {}
        source_type = "unknown"

        for step_num in target_steps:
            prompt_file, extra_vars, max_tokens = STEP_DEFS[step_num]

            if step_num <= 5:
                # Steps 1-5: paper text as prefix (cached by Azure)
                variables = {"paper_text": chunk, **extra_vars}
                if "source_type" in variables:
                    variables["source_type"] = source_type
                prompt = load_prompt(prompt_file).format(**variables)
            else:
                # Step 6: synthesis from extracted content (no paper text)
                extracted = json.dumps(results, indent=2)[:8000]
                prompt = load_prompt(prompt_file).format(extracted_content=extracted)

            if dry_run:
                is_cached = 2 <= step_num <= 5
                cached_pct = round(len(chunk) / len(prompt) * 100) if is_cached else 0
                logger.info("  [DRY] step%d %s: %dk tokens (cached=%d%%)",
                            step_num, chunk_label, len(prompt) // 4000, cached_pct)
                continue

            try:
                response = client.call(model, prompt, TEMPERATURE, max_tokens)
                data = json.loads(response)
                results.update(data)
                if "source_type" in data:
                    source_type = data["source_type"]
                logger.info("  step%d %s: OK", step_num, chunk_label)
            except json.JSONDecodeError:
                # Retry once with temperature=0 on JSON parse failure
                logger.warning("  step%d %s: JSON parse failed, retrying temp=0", step_num, chunk_label)
                try:
                    response = client.call(model, prompt, 0, max_tokens)
                    # Strip markdown fences if present
                    import re as _re
                    cleaned = _re.sub(r"```(?:json)?\s*\n?", "", response).strip().rstrip("`").strip()
                    data = json.loads(cleaned)
                    results.update(data)
                    if "source_type" in data:
                        source_type = data["source_type"]
                    logger.info("  step%d %s: OK (retry)", step_num, chunk_label)
                except (json.JSONDecodeError, Exception) as retry_err:
                    logger.warning("  step%d %s: retry also failed: %s", step_num, chunk_label, str(retry_err)[:80])
            except Exception as e:
                logger.error("  step%d %s: %s", step_num, chunk_label, str(e))
                break

        all_chunk_results.append(results)

    if dry_run:
        return {}

    merged = merge_chunk_results(all_chunk_results)

    # Write output markdown (populates frontmatter via step_runner)
    out_path = ensure_output_file(paper_id)
    try:
        from p2_systematic_review.s2_classification.utils.step_runner import (
            _write_step1_results, _write_step2_results, _write_step3_results,
            _write_step4_results, _write_step5_results, _write_step6_results,
        )
        from datetime import datetime

        # Fix 2026-05-02: previously a single ``now`` was computed once per
        # paper and reused across all six writers, producing identical
        # ``step{N}_date`` frontmatter values — making the audit trail
        # fictional at the per-step level. Each writer now stamps with its
        # own ``datetime.now().isoformat()`` so step boundaries are honest.
        if 1 in target_steps and "source_type" in merged:
            _write_step1_results(out_path, merged, model, datetime.now().isoformat())
        if 2 in target_steps and "title" in merged:
            _write_step2_results(out_path, merged, model, datetime.now().isoformat())
        if 3 in target_steps and "methodology_description" in merged:
            _write_step3_results(out_path, merged, model, datetime.now().isoformat())
        if 4 in target_steps and "key_findings" in merged:
            _write_step4_results(out_path, merged, model, datetime.now().isoformat())
        if 5 in target_steps and "limitations" in merged:
            _write_step5_results(out_path, merged, model, datetime.now().isoformat())
        if 6 in target_steps and "topic_tags" in merged:
            _write_step6_results(out_path, merged, model, datetime.now().isoformat())
    except ImportError:
        logger.warning("Could not import step_runner write functions — saving JSON only")

    save_result(paper_id, merged)
    return merged


# ── Main ──────────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Pipeline C: 6-step cached-prefix classification of 777 papers.",
    )
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--step", type=int, choices=range(1, 7))
    parser.add_argument("--from-step", type=int, choices=range(1, 7), dest="from_step")
    parser.add_argument("--limit", type=int)
    parser.add_argument("--paper-id", dest="paper_id")
    parser.add_argument("--paper-list", dest="paper_list",
                        help="Path to text file with one paper ID per line.")
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument("--skip-completed", action="store_true", default=True, dest="skip_completed")
    parser.add_argument("--no-skip-completed", action="store_false", dest="skip_completed")
    parser.add_argument("--parallel", type=int, default=1,
                        help="Number of papers to process in parallel (default: 1). "
                             "Recommended: 4-8 for standard Azure tier.")
    args = parser.parse_args()

    if args.step:
        target_steps = [args.step]
    elif args.from_step:
        target_steps = list(range(args.from_step, 7))
    else:
        target_steps = [1, 2, 3, 4, 5, 6]

    included_ids = load_included_ids()
    if args.paper_id:
        if args.paper_id not in included_ids:
            logger.error("Paper %s not in included_for_coding.csv", args.paper_id)
            sys.exit(1)
        paper_ids = [args.paper_id]
    elif args.paper_list:
        list_ids = [l.strip() for l in Path(args.paper_list).read_text().splitlines() if l.strip()]
        paper_ids = [pid for pid in list_ids if pid in included_ids]
        logger.info("Loaded %d paper IDs from %s", len(paper_ids), args.paper_list)
    else:
        paper_ids = sorted(included_ids)

    if args.limit:
        paper_ids = paper_ids[:args.limit]

    logger.info("Pipeline C (6-step cached) | model=%s | papers=%d | steps=%s | parallel=%d",
                args.model, len(paper_ids), target_steps, args.parallel)

    client = LLMClient() if not args.dry_run else None

    # Pre-filter: build work list
    work_items = []
    skipped = 0
    pre_failed = 0
    for paper_id in paper_ids:
        text_path = find_text_file(paper_id)
        if not text_path:
            logger.warning("%s: no text file", paper_id)
            pre_failed += 1
            continue

        if args.skip_completed:
            done = get_completed_steps(paper_id)
            remaining = [s for s in target_steps if s not in done]
            if not remaining:
                skipped += 1
                continue
        else:
            remaining = target_steps

        text = load_full_text(text_path)
        if len(text.strip()) < 100:
            logger.warning("%s: too short (%d chars)", paper_id, len(text))
            pre_failed += 1
            continue

        work_items.append((paper_id, text, remaining))

    logger.info("Work queue: %d papers to process, %d skipped, %d pre-failed",
                len(work_items), skipped, pre_failed)

    processed = 0
    failed = pre_failed
    _counter_lock = threading.Lock()
    t_start = time.time()

    def _process_one(idx_item):
        nonlocal processed, failed
        idx, (paper_id, text, remaining) = idx_item
        logger.info("[%d/%d] %s (%dk tok) steps=%s",
                    idx + 1, len(work_items), paper_id, len(text) // 4000, remaining)
        result = run_paper(client, paper_id, text, remaining, args.model, args.dry_run)
        with _counter_lock:
            if result or args.dry_run:
                processed += 1
            else:
                failed += 1
        return paper_id, bool(result)

    if args.parallel <= 1:
        # Sequential mode
        for idx, item in enumerate(work_items):
            _process_one((idx, item))
    else:
        # Parallel mode
        with ThreadPoolExecutor(max_workers=args.parallel) as pool:
            futures = {
                pool.submit(_process_one, (idx, item)): item[0]
                for idx, item in enumerate(work_items)
            }
            for future in as_completed(futures):
                pid = futures[future]
                try:
                    future.result()
                except Exception as e:
                    logger.error("%s: unhandled error: %s", pid, str(e))
                    with _counter_lock:
                        failed += 1

    elapsed = time.time() - t_start
    logger.info("=" * 60)
    logger.info("Classification complete")
    logger.info("  Total:     %d", len(paper_ids))
    logger.info("  Processed: %d", processed)
    logger.info("  Skipped:   %d (already done)", skipped)
    logger.info("  Failed:    %d", failed)
    logger.info("  Elapsed:   %.0f seconds", elapsed)
    logger.info("=" * 60)


if __name__ == "__main__":
    main()
