"""F1 financial-framing extraction via Azure OpenAI gpt-5.4-mini.

Reads per-paper request bundles from extractions/_requests/, calls the
Azure OpenAI deployment via shared.tools.llm_client.LLMClient, writes raw
responses atomically to extractions/_raw/. Then sanitize_and_persist_f1.py
turns each raw response into the verified structured JSON in
extractions/papers/.

Storage is deduplicated and paper-keyed: multi-silo papers are extracted
once, with silo membership recorded in the bundle\'s `silos` field.

Production primitives:
  - Resume: skip if raw response already exists
  - Atomic writes: .partial -> rename
  - Concurrency: ThreadPoolExecutor with --workers
  - Exclusions: hardcoded EXCLUDED_PAPERS set
  - Dry-run: --dry-run reports targets without calling

Usage:
  python -m p3_thematic_synthesis.s6_silo_framing.scripts.run_f1_api --all-papers --workers 8
  python -m p3_thematic_synthesis.s6_silo_framing.scripts.run_f1_api --silo portfolio_optimization
  python -m p3_thematic_synthesis.s6_silo_framing.scripts.run_f1_api --paper_id 1d715e0cd1aa
  python -m p3_thematic_synthesis.s6_silo_framing.scripts.run_f1_api --all-papers --dry-run
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path
from threading import Lock

REPO_ROOT = Path(__file__).resolve().parents[3]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from shared.tools.llm_client import LLMClient  # noqa: E402

S6_ROOT = REPO_ROOT / "p3_thematic_synthesis" / "s6_silo_framing"
LOGS_PATH = S6_ROOT / "logs" / "f1_calls.jsonl"
INDEX_PATH = S6_ROOT / "input_index" / "paper_silo_index.json"
EXTRACT_ROOT = S6_ROOT / "extractions"
REQ_DIR = EXTRACT_ROOT / "_requests"
RAW_DIR = EXTRACT_ROOT / "_raw"

API_MODEL = "gpt-5.4-mini"
API_TEMPERATURE = 0.1
MAX_TOKENS = 4000

EXCLUDED_PAPERS = {
    "567b25a75e80",  # A1: corrupted PDF (multi-paper merge)
    "9a926e905d18",  # A1: duplicate of 567b25a75e80
    "dc60950e60b9",  # A1: corrupted PDF
    "5087f7c0e2a3",  # A1: font encoding bug
    "dd6b533767c3",  # A1: Russian-language paper
    "4eb84ca51d29",  # F1: proceedings volume (~840 KB, ~210K tokens)
}

_log_lock = Lock()


def append_log(entry):
    LOGS_PATH.parent.mkdir(parents=True, exist_ok=True)
    with _log_lock:
        with LOGS_PATH.open("a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")


def atomic_write_text(path, text):
    partial = path.with_suffix(path.suffix + ".partial")
    partial.write_text(text, encoding="utf-8")
    os.replace(partial, path)


def build_user_message(paper_id, silos, paper_text):
    return (
        f"## Inputs\n\n"
        f"- paper_id: `{paper_id}`\n"
        f"- silos: {json.dumps(silos)}\n\n"
        f"## Paper text (verbatim, from shared/extracted_text/text/)\n\n"
        f"```\n{paper_text}\n```\n\n"
        f"Apply the F1 extraction protocol from the system prompt to the paper "
        f"text above. Return ONLY the JSON object \u2014 no markdown, no commentary."
    )


def call_api_for_paper(paper_id, client, force=False):
    request_path = REQ_DIR / f"{paper_id}.request.json"
    raw_path = RAW_DIR / f"{paper_id}.raw_response.txt"
    if not request_path.exists():
        return {"paper_id": paper_id, "status": "no_request"}
    if not force and raw_path.exists() and raw_path.stat().st_size > 0:
        return {"paper_id": paper_id, "status": "skipped_existing"}

    with request_path.open("r", encoding="utf-8") as f:
        bundle = json.load(f)
    text_path = Path(bundle["text_path"])
    if not text_path.exists():
        return {"paper_id": paper_id, "status": "missing_text_file"}

    paper_text = text_path.read_text(encoding="utf-8", errors="replace")
    system_prompt = bundle["prompt_text"]
    user_message = build_user_message(paper_id, bundle["silos"], paper_text)
    started_at = datetime.now(timezone.utc).isoformat()
    RAW_DIR.mkdir(parents=True, exist_ok=True)

    base_log = {
        "call_id": f"f1-{paper_id}",
        "stage": "f1",
        "paper_id": paper_id,
        "silos": bundle.get("silos"),
        "started_at": started_at,
        "channel": "azure_openai_api",
        "model_requested": API_MODEL,
        "model_actual_reported_by_runtime": API_MODEL,
        "temperature_requested": API_TEMPERATURE,
        "temperature_enforced": True,
        "max_tokens": MAX_TOKENS,
        "prompt_template_version": bundle["prompt_template_version"],
        "request_bundle_path": str(request_path.relative_to(REPO_ROOT)),
    }

    try:
        response = client.simple_completion(
            model=API_MODEL,
            system=system_prompt,
            user=user_message,
            temperature=API_TEMPERATURE,
            max_tokens=MAX_TOKENS,
            timeout=300,
        )
    except Exception as exc:
        append_log({**base_log,
                    "finished_at": datetime.now(timezone.utc).isoformat(),
                    "raw_response_path": None,
                    "status": "api_error",
                    "error": str(exc)})
        return {"paper_id": paper_id, "status": "api_error", "error": str(exc)}

    atomic_write_text(raw_path, response)
    append_log({**base_log,
                "finished_at": datetime.now(timezone.utc).isoformat(),
                "raw_response_path": str(raw_path.relative_to(REPO_ROOT)),
                "status": "ok",
                "response_length_chars": len(response)})
    return {"paper_id": paper_id, "status": "ok"}


def resolve_targets(silo, all_papers, paper_id, paper_ids):
    n_modes = sum(int(x is not None and x is not False) for x in [silo, paper_id, paper_ids]) + int(all_papers)
    if n_modes != 1:
        raise SystemExit("Provide exactly one of: --silo, --all-papers, --paper_id, --paper_ids")
    index = json.loads(INDEX_PATH.read_text(encoding="utf-8"))

    if paper_id is not None:
        if paper_id not in index["papers"]:
            raise SystemExit(f"paper_id {paper_id} not in index")
        if paper_id in EXCLUDED_PAPERS:
            raise SystemExit(f"paper_id {paper_id} is in EXCLUDED_PAPERS")
        return [paper_id]
    if paper_ids is not None:
        explicit = [p.strip() for p in paper_ids.split(",") if p.strip()]
        return [p for p in explicit if p not in EXCLUDED_PAPERS]
    if all_papers:
        return [p for p in sorted(index["papers"].keys()) if p not in EXCLUDED_PAPERS]
    if silo not in index["by_silo"]:
        raise SystemExit(f"Unknown silo: {silo}")
    return [p for p in sorted(index["by_silo"][silo]["paper_ids"]) if p not in EXCLUDED_PAPERS]


def run_targets(targets, workers, force, client):
    counts = {}
    total = len(targets)
    done = 0

    if workers <= 1:
        for pid in targets:
            r = call_api_for_paper(pid, client, force=force)
            status = r["status"]
            counts[status] = counts.get(status, 0) + 1
            done += 1
            if done % 25 == 0 or done == total:
                print(f"  {done}/{total} processed (last: {pid} -> {status})")
        return counts

    with ThreadPoolExecutor(max_workers=workers) as pool:
        futures = {pool.submit(call_api_for_paper, pid, client, force): pid for pid in targets}
        for future in as_completed(futures):
            pid = futures[future]
            try:
                r = future.result()
                status = r["status"]
            except Exception as exc:
                status = "worker_exception"
                print(f"  worker exception for {pid}: {exc}")
            counts[status] = counts.get(status, 0) + 1
            done += 1
            if done % 25 == 0 or done == total:
                print(f"  {done}/{total} processed")
    return counts


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--silo", default=None)
    parser.add_argument("--all-papers", action="store_true")
    parser.add_argument("--paper_id", default=None)
    parser.add_argument("--paper_ids", default=None)
    parser.add_argument("--workers", type=int, default=1)
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    targets = resolve_targets(args.silo, args.all_papers, args.paper_id, args.paper_ids)
    already = sum(1 for pid in targets
                  if (RAW_DIR / f"{pid}.raw_response.txt").exists()
                  and (RAW_DIR / f"{pid}.raw_response.txt").stat().st_size > 0)
    remaining = len(targets) - already
    mode = "DRY RUN" if args.dry_run else "LIVE"
    print(f"F1 plan ({mode}, model={API_MODEL}, "
          f"temp={API_TEMPERATURE}, workers={args.workers}, force={args.force}):")
    print(f"  targets:       {len(targets)}")
    print(f"  already done:  {already}")
    print(f"  to call:       {remaining if not args.force else len(targets)}")

    if args.dry_run:
        return

    client = LLMClient()
    counts = run_targets(targets, args.workers, args.force, client)
    print("=== F1 run complete ===")
    for status, n in sorted(counts.items()):
        print(f"  {status}: {n}")


if __name__ == "__main__":
    main()
