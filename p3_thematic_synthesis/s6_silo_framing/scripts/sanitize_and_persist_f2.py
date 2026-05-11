"""Sanitise + persist F2 raw responses (one per silo).

Reads:
  s6_silo_framing/briefs/{silo}/_request/f2_request.json
  s6_silo_framing/briefs/{silo}/f2.raw_response.txt

Writes:
  s6_silo_framing/briefs/{silo}/f2_silo_brief.json   (sanitised + enriched)
  s6_silo_framing/briefs/{silo}/f2.sanitize_log.json

Sanitisation rules:
  1. Strip markdown fencing if present.
  2. Parse JSON. If invalid -> mark as parse_failed; write nothing to brief.
  3. Required-keys check.
  4. Silo name match.
  5. Verify every supporting_paper_id is in the silo_paper_set; drop
     hallucinated IDs and log them.
  6. Stitch coverage_stats from the request bundle into the persisted
     brief so downstream readers have everything in one file.

Usage:
  python -m p3_thematic_synthesis.s6_silo_framing.scripts.sanitize_and_persist_f2 --silo portfolio_optimization
  python -m p3_thematic_synthesis.s6_silo_framing.scripts.sanitize_and_persist_f2 --all-silos
  python -m p3_thematic_synthesis.s6_silo_framing.scripts.sanitize_and_persist_f2          (sanitise everything that has a raw response)
"""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
S6_ROOT = REPO_ROOT / "p3_thematic_synthesis" / "s6_silo_framing"
BRIEFS_ROOT = S6_ROOT / "briefs"
INDEX_PATH = S6_ROOT / "input_index" / "paper_silo_index.json"

REQUIRED_KEYS = [
    "silo",
    "synthesised_problem_statement",
    "problem_statement_supporting_paper_ids",
    "synthesised_classical_baseline",
    "classical_baseline_supporting_paper_ids",
    "synthesised_classical_difficulty",
    "classical_difficulty_supporting_paper_ids",
    "synthesised_business_stakes",
    "business_stakes_supporting_paper_ids",
    "silo_silence_flags",
    "draft_finance_brief",
]

ID_FIELDS = [
    "problem_statement_supporting_paper_ids",
    "classical_baseline_supporting_paper_ids",
    "classical_difficulty_supporting_paper_ids",
    "business_stakes_supporting_paper_ids",
]


def strip_markdown_fences(s: str) -> str:
    s = s.strip()
    if s.startswith("```"):
        first_nl = s.find("\n")
        if first_nl != -1:
            s = s[first_nl + 1:]
        if s.endswith("```"):
            s = s[:-3]
    return s.strip()


def process_one(silo: str) -> dict:
    silo_dir = BRIEFS_ROOT / silo
    request_path = silo_dir / "_request" / "f2_request.json"
    raw_path = silo_dir / "f2.raw_response.txt"
    out_path = silo_dir / "f2_silo_brief.json"
    log_path = silo_dir / "f2.sanitize_log.json"

    if not request_path.exists():
        return {"silo": silo, "status": "no_request"}
    if not raw_path.exists():
        return {"silo": silo, "status": "no_raw_response"}

    bundle = json.loads(request_path.read_text(encoding="utf-8"))
    silo_paper_set = set(bundle["silo_paper_set"])
    coverage_stats = bundle["coverage_stats"]

    raw = raw_path.read_text(encoding="utf-8")
    cleaned = strip_markdown_fences(raw)

    log: dict = {
        "silo": silo,
        "checked_at": datetime.now(timezone.utc).isoformat(),
        "missing_keys": [],
        "silo_mismatch": None,
        "supporting_paper_actions": [],
        "result": None,
    }

    try:
        parsed = json.loads(cleaned)
    except json.JSONDecodeError as e:
        log["result"] = "rejected_parse_failed"
        log["error"] = str(e)
        log_path.write_text(json.dumps(log, indent=2, ensure_ascii=False), encoding="utf-8")
        return {"silo": silo, "status": "parse_failed"}

    for k in REQUIRED_KEYS:
        if k not in parsed:
            log["missing_keys"].append(k)
    if log["missing_keys"]:
        log["result"] = "rejected_missing_keys"
        log_path.write_text(json.dumps(log, indent=2, ensure_ascii=False), encoding="utf-8")
        return {"silo": silo, "status": "rejected_missing_keys"}

    if parsed.get("silo") != silo:
        log["silo_mismatch"] = {"got": parsed.get("silo"), "expected": silo}
        # Coerce, don't reject — this is a low-cost normalisation
        parsed["silo"] = silo

    sanitised = dict(parsed)
    for f in ID_FIELDS:
        ids = sanitised.get(f) or []
        if not isinstance(ids, list):
            ids = []
        kept = [pid for pid in ids if pid in silo_paper_set]
        dropped = [pid for pid in ids if pid not in silo_paper_set]
        sanitised[f] = kept
        if dropped:
            log["supporting_paper_actions"].append({
                "field": f,
                "dropped_ids": dropped,
                "kept_count": len(kept),
            })

    # If the synthesiser gave a non-null business_stakes but every
    # supporting id was hallucinated, flag it as null
    bs = sanitised.get("synthesised_business_stakes")
    bs_ids = sanitised.get("business_stakes_supporting_paper_ids", [])
    if bs is not None and len(bs_ids) == 0:
        log["supporting_paper_actions"].append({
            "field": "synthesised_business_stakes",
            "action": "nulled_no_surviving_ids",
        })
        sanitised["synthesised_business_stakes"] = None

    # Stitch coverage_stats and provenance into the persisted brief
    enriched = {
        "silo": silo,
        "generated_at_request": bundle.get("generated_at"),
        "generated_at_sanitise": log["checked_at"],
        "prompt_template_version": bundle.get("prompt_template_version"),
        "n_papers_in_silo_projection": bundle.get("n_papers_in_silo_projection"),
        "coverage_stats": coverage_stats,
        **{k: sanitised[k] for k in REQUIRED_KEYS if k != "silo"},
    }

    out_path.write_text(json.dumps(enriched, indent=2, ensure_ascii=False), encoding="utf-8")
    log["result"] = "accepted"
    log_path.write_text(json.dumps(log, indent=2, ensure_ascii=False), encoding="utf-8")
    return {"silo": silo, "status": "accepted"}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--silo", default=None)
    parser.add_argument("--all-silos", action="store_true")
    args = parser.parse_args()

    if args.silo and args.all_silos:
        raise SystemExit("Provide --silo OR --all-silos, not both")

    if args.silo:
        silos = [args.silo]
    elif args.all_silos:
        index = json.loads(INDEX_PATH.read_text(encoding="utf-8"))
        silos = sorted(index["by_silo"].keys())
    else:
        # Sanitise every silo that has a raw response
        silos = sorted(d.name for d in BRIEFS_ROOT.iterdir() if d.is_dir()
                       and (d / "f2.raw_response.txt").exists())
        if not silos:
            print("No raw F2 responses found.")
            return

    counts: dict[str, int] = {}
    for silo in silos:
        r = process_one(silo)
        counts[r["status"]] = counts.get(r["status"], 0) + 1
        print(r)
    print(f"processed {len(silos)} silos")
    for status, n in sorted(counts.items()):
        print(f"  {status}: {n}")


if __name__ == "__main__":
    main()
