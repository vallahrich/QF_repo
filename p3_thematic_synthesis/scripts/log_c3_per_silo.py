"""Append an AI-compliance log entry for a per-silo C3 run.

Records: timestamp, stage, silo, prompt/rendered SHAs, response SHA, theme/review counts,
model, attempts, manual patches, validator status. Mirrors the audit-trail pattern used
for the cross-silo C3 run (see s5_cross_silo/c3_crosswalk.meta.json provenance).
"""
from __future__ import annotations
import argparse
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LOG_PATH = ROOT.parent / "logs" / f"{datetime.now(timezone.utc):%Y-%m-%d}_c3_per_silo.jsonl"


def sha256_of(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--silo", required=True)
    ap.add_argument("--attempts", type=int, default=1)
    ap.add_argument("--manual-patches", type=int, default=0)
    ap.add_argument("--patch-notes", default="")
    ap.add_argument("--status", choices=["pass", "fail"], required=True)
    args = ap.parse_args()

    base = ROOT / "s4_thematic_coding" / args.silo / "themes"
    meta = json.loads((base / "c3_crosswalk.meta.json").read_text(encoding="utf-8"))
    raw_path = base / "c3_crosswalk.raw_response.txt"
    persisted = base / "c3_crosswalk.json"

    entry = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "stage": "C3",
        "scope": "per_silo",
        "silo": args.silo,
        "silo_code": meta["silo_code"],
        "model_invoked_as": "claude-opus-4.6 (via Copilot Explore subagent acting as stateless LLM endpoint)",
        "model_intended": meta["model_intended"],
        "prompt_file": meta["prompt_file"],
        "prompt_sha256": meta["prompt_sha256"],
        "rendered_sha256": meta["rendered_sha256"],
        "rendered_chars": meta["prompt_chars"],
        "approx_tokens_k": meta["approx_tokens_k"],
        "theme_count": meta["theme_count"],
        "theme_ids": meta["theme_ids"],
        "review_pool_size": meta["review_pool_size"],
        "review_ids": meta["review_ids"],
        "raw_response_sha256": sha256_of(raw_path) if raw_path.exists() else None,
        "persisted_sha256": sha256_of(persisted) if persisted.exists() else None,
        "subagent_call_attempts": args.attempts,
        "manual_patches": args.manual_patches,
        "patch_notes": args.patch_notes,
        "validator": "validate_and_persist_c3_per_silo.py",
        "validator_status": args.status,
        "tool_restrictions_imposed": [
            "read_file (single path: c3_crosswalk.prompt.txt) only",
            "no grep_search / semantic_search / file_search / list_dir",
            "no run_in_terminal / fetch_webpage / memory",
        ],
        "audit_note": (
            "Subagent invoked in isolation, mimicking an HTTP API call. The prompt is the "
            "sole input; output JSON is captured verbatim and validated by L-C3 (verbatim "
            "quote check, theme coverage, stance discrimination)."
        ),
    }

    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with LOG_PATH.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    print(f"logged: {LOG_PATH.name} <- {args.silo} ({args.status})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
