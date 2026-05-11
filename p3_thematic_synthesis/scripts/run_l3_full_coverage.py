"""Stage A — extend L3 adversarial-check coverage from 108 → 654 papers.

Closes GL-10 G-03 by upgrading the L3 safeguard from a 16.5% deterministic
sample to 100% of the P2 corpus that survived A2 memo compression.

Calibration is held constant with the existing 108 records:
- prompt: p3_thematic_synthesis/prompts/l3_adversarial_v2.txt (unchanged)
- model:  A2_MODEL = "gpt-5.1"
- temperature: 0.0
- response_format: {"type": "json_object"}
- max_tokens: 16000
This script reuses `_run_l3`, `_atomic_write_json`, `find_text_file`,
`PAPERS_DIR` and `EXCLUDED_PAPERS` from run_production.py to guarantee that.

Resume-friendly: any paper whose `{pid}_l3.json` already exists (and is
non-empty) is skipped. The 108 existing L3 records are therefore left
untouched.

Usage:
    python -m p3_thematic_synthesis.scripts.run_l3_full_coverage --workers 8
    python -m p3_thematic_synthesis.scripts.run_l3_full_coverage --workers 8 --limit 5     # dry-run on 5
    python -m p3_thematic_synthesis.scripts.run_l3_full_coverage --dry-run                 # show plan only
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path

_PROJECT_ROOT = str(Path(__file__).resolve().parents[2])
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

from shared.tools.llm_client import LLMClient  # noqa: E402
from p3_thematic_synthesis.scripts.run_production import (  # noqa: E402
    PAPERS_DIR,
    EXCLUDED_PAPERS,
    A2_MODEL,
    _atomic_write_json,
    find_text_file,
    load_prompt,
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)-5s %(message)s",
                    datefmt="%H:%M:%S")
logger = logging.getLogger(__name__)

LOG_DIR = os.path.join(_PROJECT_ROOT, "logs")
LOG_PATH = os.path.join(LOG_DIR, "l3_calls.jsonl")

_log_lock = threading.Lock()


def _run_l3_with_model(client: LLMClient, model: str, paper_id: str,
                      memo: dict, paper_text: str, prompt_version: str = "v2") -> dict:
    """L3 call parameterised by model and prompt version. Mirrors
    run_production._run_l3 exactly (same JSON mode, max_tokens, truncation,
    parse fallback) but lets the caller pick model + prompt version."""
    prompt_template = load_prompt("l3_adversarial", version=prompt_version)
    truncated = paper_text[:80000] if len(paper_text) > 80000 else paper_text
    prompt = prompt_template.replace("{paper_id}", paper_id)
    prompt = prompt.replace("{a2_memo}", json.dumps(memo, indent=2))
    prompt = prompt.replace("{paper_text}", truncated)
    response = client.call(model, prompt, temperature=0.0, max_tokens=16000,
                           response_format={"type": "json_object"})
    try:
        return json.loads(response)
    except json.JSONDecodeError:
        s = response.find("{")
        e = response.rfind("}") + 1
        if s >= 0 and e > s:
            return json.loads(response[s:e])
        return {"paper_id": paper_id, "verdict": "clean", "issues": [], "parse_error": True}


def _append_log(row: dict) -> None:
    with _log_lock:
        with open(LOG_PATH, "a", encoding="utf-8") as f:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")


def discover_targets(out_dir: str) -> list[str]:
    """Return paper_ids that have an A2 memo but no L3 record yet in out_dir."""
    paper_dir = Path(PAPERS_DIR)
    out_path = Path(out_dir)
    a2_ids: set[str] = set()
    l3_done: set[str] = set()

    # A2 memos always live in PAPERS_DIR.
    for p in paper_dir.glob("*.json"):
        if p.name.endswith("_l3.json"):
            continue
        stem = p.stem
        if stem in EXCLUDED_PAPERS:
            continue
        a2_ids.add(stem)

    # L3 records may live in PAPERS_DIR (production) or a sandbox dir.
    if out_path.is_dir():
        for p in out_path.glob("*_l3.json"):
            if p.stat().st_size > 0:
                l3_done.add(p.name[: -len("_l3.json")])

    pending = sorted(a2_ids - l3_done)
    return pending


def process_one(client: LLMClient, model: str, paper_id: str, out_dir: str,
                prompt_version: str = "v2") -> dict:
    memo_path = os.path.join(PAPERS_DIR, f"{paper_id}.json")
    l3_path = os.path.join(out_dir, f"{paper_id}_l3.json")

    # Defensive resume guard inside the worker as well.
    if os.path.isfile(l3_path) and os.path.getsize(l3_path) > 0:
        return {"paper_id": paper_id, "status": "already_done"}

    if not os.path.isfile(memo_path):
        return {"paper_id": paper_id, "status": "no_memo"}

    text_path = find_text_file(paper_id)
    if not text_path:
        return {"paper_id": paper_id, "status": "no_text"}

    with open(memo_path, encoding="utf-8") as f:
        memo = json.load(f)
    with open(text_path, encoding="utf-8", errors="replace") as f:
        paper_text = f.read()

    t0 = time.time()
    try:
        result = _run_l3_with_model(client, model, paper_id, memo, paper_text,
                                    prompt_version=prompt_version)
    except Exception as exc:
        elapsed = round(time.time() - t0, 2)
        _append_log({
            "ts": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "paper_id": paper_id, "status": "error", "error": str(exc),
            "elapsed_s": elapsed,
        })
        return {"paper_id": paper_id, "status": "error", "error": str(exc)}

    elapsed = round(time.time() - t0, 2)
    _atomic_write_json(l3_path, result)

    problems = result.get("problems", []) or result.get("issues", []) or []
    _append_log({
        "ts": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "paper_id": paper_id, "status": "complete",
        "problems_found": bool(result.get("problems_found")),
        "problem_count": int(result.get("problem_count", len(problems))),
        "verdict": result.get("verdict"),
        "elapsed_s": elapsed,
    })
    return {"paper_id": paper_id, "status": "complete", "elapsed_s": elapsed,
            "problem_count": int(result.get("problem_count", len(problems)))}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workers", type=int, default=8)
    parser.add_argument("--limit", type=int, default=None,
                        help="Process only the first N pending papers (for dry-run/calibration check)")
    parser.add_argument("--dry-run", action="store_true",
                        help="List the pending paper count and exit (no LLM calls)")
    parser.add_argument("--model", default=A2_MODEL,
                        help="LLM model id (default: A2_MODEL = gpt-5.1, matches existing 108 records)")
    parser.add_argument("--out-dir", default=PAPERS_DIR,
                        help="Where to write {pid}_l3.json (default: production PAPERS_DIR; "
                             "override for sensitivity probes)")
    parser.add_argument("--paper-ids", default=None,
                        help="Comma-separated paper_ids to override discovery (probe mode)")
    parser.add_argument("--prompt-version", default="v2",
                        help="Prompt version suffix (default: v2 = matches existing 108 records)")
    args = parser.parse_args()

    os.makedirs(LOG_DIR, exist_ok=True)
    os.makedirs(args.out_dir, exist_ok=True)

    if args.paper_ids:
        pending = [pid.strip() for pid in args.paper_ids.split(",") if pid.strip()]
        logger.info("Paper-ids override: %d explicit targets", len(pending))
    else:
        pending = discover_targets(args.out_dir)
        logger.info("Pending L3 targets in %s: %d", args.out_dir, len(pending))
    logger.info("Model: %s   Out-dir: %s   Prompt: %s", args.model, args.out_dir, args.prompt_version)

    if args.dry_run:
        logger.info("DRY-RUN: would process %d papers (workers=%d)", len(pending), args.workers)
        return 0

    if args.limit is not None:
        pending = pending[: args.limit]
        logger.info("Limit applied: processing first %d papers", len(pending))

    if not pending:
        logger.info("Nothing to do.")
        return 0

    client = LLMClient()
    done = err = 0
    t0 = time.time()
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        futs = {pool.submit(process_one, client, args.model, pid, args.out_dir, args.prompt_version): pid for pid in pending}
        for i, fut in enumerate(as_completed(futs), 1):
            try:
                r = fut.result()
                if r["status"] == "complete":
                    done += 1
                elif r["status"] in ("no_memo", "no_text", "already_done"):
                    pass
                else:
                    err += 1
                if i % 10 == 0 or i == len(pending):
                    logger.info("Progress: %d/%d  done=%d  err=%d  elapsed=%.1fs",
                                i, len(pending), done, err, time.time() - t0)
            except Exception as exc:
                pid = futs[fut]
                logger.error("Future error %s: %s", pid, exc)
                err += 1

    logger.info("DONE  total=%d  complete=%d  errors=%d  elapsed=%.1fs",
                len(pending), done, err, time.time() - t0)
    return 0 if err == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
