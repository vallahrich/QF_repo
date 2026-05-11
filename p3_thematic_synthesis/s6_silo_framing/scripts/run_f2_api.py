"""F2 per-silo finance-framing aggregation via Azure OpenAI gpt-5.1.

Reads the per-silo F2 request bundles produced by render_f2_request.py
and calls gpt-5.1 (a reasoning model — temperature is omitted by
LLMClient automatically). Writes raw responses atomically to:

  s6_silo_framing/briefs/{silo}/f2.raw_response.txt

Then sanitize_and_persist_f2.py turns each raw response into the
verified silo brief at:

  s6_silo_framing/briefs/{silo}/f2_silo_brief.json

Production primitives:
  - Resume: skip if raw response already exists
  - Atomic writes: .partial -> rename
  - Sequential per silo (only 8 calls total)
  - Audit log appended to logs/f2_calls.jsonl

Usage:
  python -m p3_thematic_synthesis.s6_silo_framing.scripts.run_f2_api --silo portfolio_optimization
  python -m p3_thematic_synthesis.s6_silo_framing.scripts.run_f2_api --all-silos
  python -m p3_thematic_synthesis.s6_silo_framing.scripts.run_f2_api --all-silos --dry-run
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from threading import Lock

REPO_ROOT = Path(__file__).resolve().parents[3]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from shared.tools.llm_client import LLMClient  # noqa: E402

S6_ROOT = REPO_ROOT / "p3_thematic_synthesis" / "s6_silo_framing"
BRIEFS_ROOT = S6_ROOT / "briefs"
LOGS_PATH = S6_ROOT / "logs" / "f2_calls.jsonl"
INDEX_PATH = S6_ROOT / "input_index" / "paper_silo_index.json"

API_MODEL = "gpt-5.1"  # reasoning model; temperature omitted by LLMClient
MAX_TOKENS = 16000

_log_lock = Lock()


def append_log(entry: dict) -> None:
    LOGS_PATH.parent.mkdir(parents=True, exist_ok=True)
    with _log_lock:
        with LOGS_PATH.open("a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")


def atomic_write_text(path: Path, text: str) -> None:
    partial = path.with_suffix(path.suffix + ".partial")
    partial.write_text(text, encoding="utf-8")
    os.replace(partial, path)


def build_user_message(bundle: dict) -> str:
    """Construct the user message from a frozen F2 request bundle."""
    return (
        f"## Inputs\n\n"
        f"- silo: `{bundle['silo']}`\n"
        f"- silo_paper_set (canonical IDs accepted by F1, n="
        f"{len(bundle['silo_paper_set'])}): {json.dumps(bundle['silo_paper_set'])}\n"
        f"- coverage_stats: {json.dumps(bundle['coverage_stats'])}\n\n"
        f"## F1 records (one per paper)\n\n"
        f"```json\n{json.dumps(bundle['f1_records'], ensure_ascii=False)}\n```\n\n"
        f"Apply the F2 aggregation protocol from the system prompt. "
        f"Return ONLY the JSON object — no markdown wrapping, no commentary."
    )


def call_api_for_silo(silo: str, client: LLMClient, force: bool = False) -> dict:
    silo_dir = BRIEFS_ROOT / silo
    request_path = silo_dir / "_request" / "f2_request.json"
    raw_path = silo_dir / "f2.raw_response.txt"

    if not request_path.exists():
        return {"silo": silo, "status": "no_request"}
    if not force and raw_path.exists() and raw_path.stat().st_size > 0:
        return {"silo": silo, "status": "skipped_existing"}

    bundle = json.loads(request_path.read_text(encoding="utf-8"))
    system_prompt = bundle["prompt_text"]
    user_message = build_user_message(bundle)
    started_at = datetime.now(timezone.utc).isoformat()
    silo_dir.mkdir(parents=True, exist_ok=True)

    base_log = {
        "call_id": f"f2-{silo}",
        "stage": "f2",
        "silo": silo,
        "n_papers_in_bundle": len(bundle["f1_records"]),
        "user_message_length_chars": len(user_message),
        "started_at": started_at,
        "channel": "azure_openai_api",
        "model_requested": API_MODEL,
        "model_actual_reported_by_runtime": API_MODEL,
        "temperature_requested": None,  # gpt-5.1 is a reasoning model
        "temperature_enforced": False,
        "max_tokens": MAX_TOKENS,
        "prompt_template_version": bundle["prompt_template_version"],
        "request_bundle_path": str(request_path.relative_to(REPO_ROOT)),
    }

    try:
        response = client.simple_completion(
            model=API_MODEL,
            system=system_prompt,
            user=user_message,
            max_tokens=MAX_TOKENS,
            timeout=600,
        )
    except Exception as exc:
        append_log({**base_log,
                    "finished_at": datetime.now(timezone.utc).isoformat(),
                    "raw_response_path": None,
                    "status": "api_error",
                    "error": str(exc)})
        return {"silo": silo, "status": "api_error", "error": str(exc)}

    atomic_write_text(raw_path, response)
    append_log({**base_log,
                "finished_at": datetime.now(timezone.utc).isoformat(),
                "raw_response_path": str(raw_path.relative_to(REPO_ROOT)),
                "status": "ok",
                "response_length_chars": len(response)})
    return {"silo": silo, "status": "ok"}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--silo", default=None)
    parser.add_argument("--all-silos", action="store_true")
    parser.add_argument("--force", action="store_true",
                        help="Re-run even if raw response already exists.")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    if args.all_silos and args.silo is not None:
        raise SystemExit("Provide --silo OR --all-silos, not both")
    if not args.all_silos and args.silo is None:
        raise SystemExit("Provide --silo or --all-silos")

    index = json.loads(INDEX_PATH.read_text(encoding="utf-8"))
    silos = sorted(index["by_silo"].keys()) if args.all_silos else [args.silo]

    print(f"F2 plan ({'DRY RUN' if args.dry_run else 'LIVE'}, model={API_MODEL}, "
          f"max_tokens={MAX_TOKENS}, force={args.force}):")
    to_call = []
    for silo in silos:
        request_path = BRIEFS_ROOT / silo / "_request" / "f2_request.json"
        raw_path = BRIEFS_ROOT / silo / "f2.raw_response.txt"
        has_request = request_path.exists()
        has_raw = raw_path.exists() and raw_path.stat().st_size > 0
        if not has_request:
            status = "MISSING REQUEST BUNDLE — run render_f2_request first"
        elif has_raw and not args.force:
            status = "skipped (already done)"
        else:
            status = "to call"
            to_call.append(silo)
        print(f"  {silo}: {status}")
    print(f"Calls planned: {len(to_call)}")

    if args.dry_run:
        return

    client = LLMClient()
    summary = {}
    for silo in silos:
        print(f"--- {silo} ---")
        r = call_api_for_silo(silo, client, force=args.force)
        summary[silo] = r["status"]
        print(f"  {silo}: {r}")
    print("=== F2 run complete ===")
    for silo, status in summary.items():
        print(f"  {silo}: {status}")


if __name__ == "__main__":
    main()
