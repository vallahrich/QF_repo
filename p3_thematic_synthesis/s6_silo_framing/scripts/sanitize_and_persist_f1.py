"""Sanitise + persist F1 raw responses (deduplicated, paper-keyed).

Reads:
  s6_silo_framing/extractions/_requests/{paper_id}.request.json
  s6_silo_framing/extractions/_raw/{paper_id}.raw_response.txt

Writes:
  s6_silo_framing/extractions/papers/{paper_id}.json          (sanitised)
  s6_silo_framing/extractions/_raw/{paper_id}.sanitize_log.json

Sanitisation rules (L1-equivalent, mirroring B1 sanitiser):
  1. Strip any markdown fencing the model wrapped around the JSON.
  2. Parse JSON. If invalid -> mark as parse_failed; write nothing to papers/.
  3. For every *_quotes array: verify each quote is a verbatim substring of
     the supplied paper text. Drop quotes that fail verification. Three
     normalisation tiers handle benign formatting variants (whitespace
     collapse, OCR hyphen rejoin across line breaks, inline hyphen strip).
     A hallucinated quote cannot pass — the underlying text must be present.
  4. If a non-null field has zero surviving quotes after verification, set
     the field to null and add a sanitise_log entry.
  5. Required-keys check: every schema key must be present in output.
  6. The output paper_id must match the requested paper_id.

Usage:
  # Sanitise one paper:
  python -m p3_thematic_synthesis.s6_silo_framing.scripts.sanitize_and_persist_f1 \
      --paper_id 05a01a257cc7
  # Sanitise everything currently in _raw/ (resume-friendly):
  python -m p3_thematic_synthesis.s6_silo_framing.scripts.sanitize_and_persist_f1
"""
from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
S6_ROOT = REPO_ROOT / "p3_thematic_synthesis" / "s6_silo_framing"
EXTRACT_ROOT = S6_ROOT / "extractions"
REQ_DIR = EXTRACT_ROOT / "_requests"
RAW_DIR = EXTRACT_ROOT / "_raw"
PAPERS_DIR = EXTRACT_ROOT / "papers"

REQUIRED_KEYS = [
    "paper_id",
    "silos",
    "problem_statement",
    "problem_statement_quotes",
    "classical_baseline",
    "classical_baseline_quotes",
    "classical_difficulty",
    "classical_difficulty_quotes",
    "business_stakes",
    "business_stakes_quotes",
    "extraction_confidence",
    "extraction_notes",
]

QUOTE_FIELDS = [
    ("problem_statement", "problem_statement_quotes"),
    ("classical_baseline", "classical_baseline_quotes"),
    ("classical_difficulty", "classical_difficulty_quotes"),
    ("business_stakes", "business_stakes_quotes"),
]


def strip_markdown_fences(s: str) -> str:
    s = s.strip()
    # Strip common ```json ... ``` fencing
    if s.startswith("```"):
        # Drop first fence line
        first_nl = s.find("\n")
        if first_nl != -1:
            s = s[first_nl + 1 :]
        if s.endswith("```"):
            s = s[: -3]
    return s.strip()


# Characters that models commonly wrap around quotes. We strip matched pairs.
WRAPPER_CHARS = '"\'\u201c\u201d\u2018\u2019\u00ab\u00bb\u201e\u201a'


def strip_quote_wrappers(quote: str) -> str:
    """Strip a single layer of matched leading/trailing quotation-mark wrappers.

    Models often wrap their quotations in literal quote marks. The underlying
    text in the paper does not contain those wrapper marks, so we strip them
    before the substring check. We only strip when leading and trailing chars
    are both quote-like (not necessarily the same character — e.g., curly
    open + curly close), and we strip at most one layer.
    """
    s = quote.strip()
    if len(s) >= 2 and s[0] in WRAPPER_CHARS and s[-1] in WRAPPER_CHARS:
        s = s[1:-1].strip()
    return s


def normalise_for_substring_check(text: str) -> str:
    """Collapse whitespace runs to single spaces. We do NOT lowercase."""
    return re.sub(r"\s+", " ", text)


def normalise_with_hyphen_rejoin(text: str) -> str:
    """Same as normalise_for_substring_check, but also rejoin hyphenated words
    that were broken across line breaks in the OCR'd paper text. Models often
    quote the rejoined form (e.g. 'complex-ity') when the paper has
    'complex-\\nity'. After this normalisation, both forms collapse.
    """
    # Replace hyphen-followed-by-whitespace with nothing (rejoin words)
    rejoined = re.sub(r"-\s+", "", text)
    return re.sub(r"\s+", " ", rejoined)


def normalise_strip_inline_hyphens(text: str) -> str:
    """Final-tier fallback: strip ALL hyphens that appear between non-space
    characters. This handles the case where the model returned a half-OCR
    form (e.g. 'complex-ity' with literal hyphen, no whitespace) while the
    paper has 'complex-\\nity' or 'complexity'.

    Side effect: 'real-world' becomes 'realworld'. Acceptable because we
    apply the SAME transform to both sides of the substring check, so it
    cannot accept a hallucinated quote — only a benign formatting variant.
    """
    # Remove hyphens that are between word characters (no whitespace on either side)
    stripped = re.sub(r"(?<=\w)-(?=\w)", "", text)
    # Also rejoin hyphen+whitespace pattern
    stripped = re.sub(r"-\s+", "", stripped)
    return re.sub(r"\s+", " ", stripped)


def verify_quote(quote: str, paper_text_norm: str, paper_text_norm_rejoined: str,
                 paper_text_norm_no_hyphens: str) -> bool:
    if not isinstance(quote, str):
        return False
    stripped = strip_quote_wrappers(quote)
    if not stripped.strip():
        return False
    needle_norm = normalise_for_substring_check(stripped)
    if needle_norm in paper_text_norm:
        return True
    needle_rejoined = normalise_with_hyphen_rejoin(stripped)
    if needle_rejoined in paper_text_norm_rejoined:
        return True
    needle_no_hyphens = normalise_strip_inline_hyphens(stripped)
    if needle_no_hyphens in paper_text_norm_no_hyphens:
        return True
    return False


def sanitise_record(parsed: dict, paper_id: str, silos: list[str], paper_text: str) -> tuple[dict | None, dict]:
    """Return (sanitised_record_or_None, sanitise_log_dict)."""
    log: dict = {
        "paper_id": paper_id,
        "checked_at": datetime.now(timezone.utc).isoformat(),
        "missing_keys": [],
        "paper_id_mismatch": None,
        "field_actions": [],
        "result": None,
    }

    # Required-keys check
    for k in REQUIRED_KEYS:
        if k not in parsed:
            log["missing_keys"].append(k)
    if log["missing_keys"]:
        log["result"] = "rejected_missing_keys"
        return None, log

    # paper_id match
    if parsed.get("paper_id") != paper_id:
        log["paper_id_mismatch"] = {"got": parsed.get("paper_id"), "expected": paper_id}
        log["result"] = "rejected_paper_id_mismatch"
        return None, log

    # Force silos to the canonical set from the index, regardless of what model returned
    parsed["silos"] = silos

    paper_text_norm = normalise_for_substring_check(paper_text)
    paper_text_norm_rejoined = normalise_with_hyphen_rejoin(paper_text)
    paper_text_norm_no_hyphens = normalise_strip_inline_hyphens(paper_text)

    sanitised = dict(parsed)
    for field, quote_field in QUOTE_FIELDS:
        original_quotes = sanitised.get(quote_field) or []
        if not isinstance(original_quotes, list):
            original_quotes = []
        kept = []
        dropped = []
        for q in original_quotes:
            if verify_quote(q, paper_text_norm, paper_text_norm_rejoined,
                            paper_text_norm_no_hyphens):
                # Keep the quote with wrapper marks stripped, since the wrappers
                # weren't in the source paper.
                kept.append(strip_quote_wrappers(q) if isinstance(q, str) else q)
            else:
                dropped.append(q)
        sanitised[quote_field] = kept

        # If the field has a non-null statement but zero surviving quotes -> null it.
        statement = sanitised.get(field)
        if statement is not None and not kept:
            sanitised[field] = None
            log["field_actions"].append({
                "field": field,
                "action": "nulled_no_surviving_quote",
                "dropped_quote_count": len(dropped),
            })
        elif dropped:
            log["field_actions"].append({
                "field": field,
                "action": "dropped_quotes",
                "dropped_quote_count": len(dropped),
                "kept_quote_count": len(kept),
            })

    # Confidence sanity-check
    conf = sanitised.get("extraction_confidence")
    if conf not in {"high", "medium", "low"}:
        sanitised["extraction_confidence"] = "low"
        log["field_actions"].append({
            "field": "extraction_confidence",
            "action": "coerced_to_low",
            "original": conf,
        })

    log["result"] = "accepted"
    return sanitised, log


def process_one(paper_id: str) -> dict:
    request_path = REQ_DIR / f"{paper_id}.request.json"
    raw_path = RAW_DIR / f"{paper_id}.raw_response.txt"
    out_path = PAPERS_DIR / f"{paper_id}.json"
    log_path = RAW_DIR / f"{paper_id}.sanitize_log.json"

    if not request_path.exists():
        return {"paper_id": paper_id, "status": "no_request"}
    if not raw_path.exists():
        return {"paper_id": paper_id, "status": "no_raw_response"}

    with request_path.open("r", encoding="utf-8") as f:
        request_bundle = json.load(f)
    text_path = Path(request_bundle["text_path"])
    if not text_path.exists():
        return {"paper_id": paper_id, "status": "missing_text_file"}
    paper_text = text_path.read_text(encoding="utf-8", errors="replace")

    raw = raw_path.read_text(encoding="utf-8")
    cleaned = strip_markdown_fences(raw)

    try:
        parsed = json.loads(cleaned)
    except json.JSONDecodeError as e:
        log = {
            "paper_id": paper_id,
            "checked_at": datetime.now(timezone.utc).isoformat(),
            "result": "rejected_parse_failed",
            "error": str(e),
        }
        log_path.parent.mkdir(parents=True, exist_ok=True)
        with log_path.open("w", encoding="utf-8") as f:
            json.dump(log, f, indent=2, ensure_ascii=False)
        return {"paper_id": paper_id, "status": "parse_failed"}

    sanitised, log = sanitise_record(
        parsed=parsed,
        paper_id=paper_id,
        silos=request_bundle["silos"],
        paper_text=paper_text,
    )

    log_path.parent.mkdir(parents=True, exist_ok=True)
    with log_path.open("w", encoding="utf-8") as f:
        json.dump(log, f, indent=2, ensure_ascii=False)

    if sanitised is None:
        return {"paper_id": paper_id, "status": log["result"]}

    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8") as f:
        json.dump(sanitised, f, indent=2, ensure_ascii=False)
    return {"paper_id": paper_id, "status": "accepted"}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--paper_id", default=None,
                        help="If provided, sanitise only this paper. Else all raw responses present.")
    args = parser.parse_args()

    if args.paper_id is not None:
        result = process_one(args.paper_id)
        print(result)
        return

    if not RAW_DIR.exists():
        print(f"No raw responses dir: {RAW_DIR}")
        return

    targets = sorted(p.stem.replace(".raw_response", "") for p in RAW_DIR.glob("*.raw_response.txt"))
    if not targets:
        print(f"No raw responses found in {RAW_DIR}")
        return

    counts: dict[str, int] = {}
    for pid in targets:
        result = process_one(pid)
        counts[result["status"]] = counts.get(result["status"], 0) + 1
    print(f"processed {len(targets)} raw responses")
    for status, n in sorted(counts.items()):
        print(f"  {status}: {n}")


if __name__ == "__main__":
    main()
