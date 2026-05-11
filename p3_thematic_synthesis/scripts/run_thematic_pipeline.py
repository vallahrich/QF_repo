"""Thematic coding pipeline — Step 3.5.

Runs the per-paper thematic analysis pipeline:
  A1 (open coding) → L1 (quote verification) → A2 (memo compression)
  → L2 (claim tracing) → L3 (adversarial check)

Reads inclusion lists and text-readiness from shared/phase3/.
Outputs to p3_thematic_synthesis/s4_thematic_coding/<silo>/{codes,memos}/.

Usage:
    # Pilot: single silo, single model
    python -m p3_thematic_synthesis.scripts.run_thematic_pipeline --silo trading_execution --model gpt-5-mini

    # Pilot: single silo, both models (comparison)
    python -m p3_thematic_synthesis.scripts.run_thematic_pipeline --silo trading_execution --model gpt-5-mini --model gpt-5.1

    # Production: all silos
    python -m p3_thematic_synthesis.scripts.run_thematic_pipeline --all

    # Dry run (no LLM calls)
    python -m p3_thematic_synthesis.scripts.run_thematic_pipeline --silo trading_execution --dry-run
"""

import argparse
import json
import logging
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import yaml

_PROJECT_ROOT = str(Path(__file__).resolve().parents[2])
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

from shared.tools.llm_client import LLMClient  # noqa: E402

logging.basicConfig(level=logging.INFO, format="%(levelname)s  %(message)s")
logger = logging.getLogger(__name__)

# Paths
INCLUSION_DIR = os.path.join(_PROJECT_ROOT, "shared", "phase3", "inclusion")
TEXT_READINESS_DIR = os.path.join(_PROJECT_ROOT, "shared", "phase3", "text_readiness")
TEXT_DIR = os.path.join(_PROJECT_ROOT, "shared", "extracted_text", "text")
P2_PROCESSED_DIR = os.path.join(_PROJECT_ROOT, "p2_systematic_review", "output", "processed")
PROMPTS_DIR = os.path.join(_PROJECT_ROOT, "p3_thematic_synthesis", "prompts")
CODING_DIR = os.path.join(_PROJECT_ROOT, "p3_thematic_synthesis", "s4_thematic_coding")
QUANT_DIR = os.path.join(_PROJECT_ROOT, "p3_thematic_synthesis", "s2_quantitative",
                         "output", "extractions_preQ0_20260417_095811")
TRIANGULATION_PATH = os.path.join(_PROJECT_ROOT, "p3_thematic_synthesis", "s3_quantum_advantage",
                                  "combined", "output", "triangulation_matrix.json")


# Default prompt version — override with --prompt-version
DEFAULT_PROMPT_VERSION = "v2"


def load_prompt(name: str, version: str = DEFAULT_PROMPT_VERSION) -> str:
    """Load a prompt template. Tries <name>_<version>.txt first, falls back to <name>.txt."""
    versioned_path = os.path.join(PROMPTS_DIR, f"{name}_{version}.txt")
    if os.path.isfile(versioned_path):
        return open(versioned_path, encoding="utf-8").read()
    # No versioned file — prompt has only one version
    base_path = os.path.join(PROMPTS_DIR, f"{name}.txt")
    return open(base_path, encoding="utf-8").read()


def find_text_file(paper_id: str) -> str | None:
    """Find extracted text file for a paper_id."""
    text_dir = Path(TEXT_DIR)
    matches = list(text_dir.glob(f"{paper_id}*.md"))
    return str(matches[0]) if matches else None


def load_p2_frontmatter(paper_id: str) -> dict:
    """Load P2 frontmatter for a paper."""
    path = os.path.join(P2_PROCESSED_DIR, f"{paper_id}.md")
    if not os.path.isfile(path):
        return {}
    with open(path, encoding="utf-8") as f:
        content = f.read()
    if not content.startswith("---"):
        return {}
    end = content.find("---", 3)
    if end == -1:
        return {}
    try:
        return yaml.safe_load(content[3:end]) or {}
    except yaml.YAMLError:
        return {}


def load_quantitative_extraction(paper_id: str) -> dict | None:
    """Load quantitative extraction JSON if available."""
    path = os.path.join(QUANT_DIR, f"{paper_id}.json")
    if os.path.isfile(path):
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    return None


def load_triangulation_verdicts() -> dict[str, list[dict]]:
    """Load triangulation matrix, indexed by paper_id."""
    if not os.path.isfile(TRIANGULATION_PATH):
        return {}
    with open(TRIANGULATION_PATH, encoding="utf-8") as f:
        rows = json.load(f)
    by_paper: dict[str, list[dict]] = {}
    for row in rows:
        pid = row.get("paper_id", "")
        by_paper.setdefault(pid, []).append(row)
    return by_paper


# ─── Pass A1: Open Coding ───────────────────────────────────────────

def run_a1(client: LLMClient, model: str, paper_id: str, paper_text: str) -> list[dict]:
    """Pass A1: LLM inductive open coding."""
    prompt_template = load_prompt("a1_open_coding")
    prompt = prompt_template.replace("{paper_text}", paper_text)

    response = client.call(model, prompt, temperature=0.0, max_tokens=32000,
                           response_format={"type": "json_object"})
    try:
        parsed = json.loads(response)
        # Handle both {"codes": [...]} wrapper and bare array
        if isinstance(parsed, dict) and "codes" in parsed:
            codes = parsed["codes"]
        elif isinstance(parsed, list):
            codes = parsed
        else:
            codes = [parsed]
        codes = codes if isinstance(codes, list) else [codes]
        # Normalize field names (some models use "label" instead of "code_label")
        for c in codes:
            if "label" in c and "code_label" not in c:
                c["code_label"] = c.pop("label")
        return codes
    except json.JSONDecodeError:
        logger.warning("A1 JSON parse error for %s, attempting extraction", paper_id)
        # Try to extract JSON array from response
        start = response.find("[")
        end = response.rfind("]") + 1
        if start >= 0 and end > start:
            return json.loads(response[start:end])
        return []


# ─── Safeguard L1: Quote Verification ───────────────────────────────

def _normalize_whitespace(text: str) -> str:
    """Collapse all whitespace (newlines, tabs, multiple spaces) to single spaces."""
    import re
    return re.sub(r'\s+', ' ', text).strip()


def run_l1(codes: list[dict], paper_text: str) -> tuple[list[dict], dict]:
    """Safeguard L1: Verify A1 quotes exist in source text."""
    from difflib import SequenceMatcher

    # Normalize whitespace for matching (OCR and extraction artifacts)
    norm_text = _normalize_whitespace(paper_text)

    stats = {"pass": 0, "pass_fuzzy": 0, "fail": 0, "total": len(codes)}
    verified_codes = []

    for code in codes:
        span = code.get("text_span", "")
        if not span:
            code["l1_status"] = "fail"
            code["l1_reason"] = "empty text_span"
            stats["fail"] += 1
            verified_codes.append(code)
            continue

        norm_span = _normalize_whitespace(span)

        # Exact match (on normalized text)
        if norm_span in norm_text:
            code["l1_status"] = "pass"
            stats["pass"] += 1
        else:
            # Fuzzy match
            best_ratio = 0.0
            span_lower = norm_span.lower()
            text_lower = norm_text.lower()
            window = len(span_lower)
            for i in range(len(text_lower) - window + 1):
                chunk = text_lower[i:i + window]
                ratio = SequenceMatcher(None, span_lower, chunk).ratio()
                if ratio > best_ratio:
                    best_ratio = ratio
                if ratio > 0.90:
                    break

            if best_ratio > 0.85:
                code["l1_status"] = "pass_fuzzy"
                code["l1_fuzzy_ratio"] = round(best_ratio, 3)
                stats["pass_fuzzy"] += 1
            else:
                code["l1_status"] = "fail"
                code["l1_best_ratio"] = round(best_ratio, 3)
                stats["fail"] += 1

        verified_codes.append(code)

    return verified_codes, stats


# ─── Pass A2: Memo Compression ──────────────────────────────────────

def run_a2(client: LLMClient, model: str, paper_id: str,
           verified_codes: list[dict], p2_meta: dict,
           quant_extraction: dict | None, triangulation: list[dict] | None) -> dict:
    """Pass A2: Compress codes into structured analytical memo."""
    # Filter to passing codes only
    good_codes = [c for c in verified_codes if c.get("l1_status") in ("pass", "pass_fuzzy")]

    prompt_template = load_prompt("a2_memo_compression")
    prompt = prompt_template.replace("{paper_id}", paper_id)
    prompt = prompt.replace("{a1_codes}", json.dumps(good_codes, indent=2))
    prompt = prompt.replace("{p2_frontmatter}", json.dumps(p2_meta, indent=2, default=str))
    prompt = prompt.replace("{quantitative_extraction}",
                            json.dumps(quant_extraction, indent=2) if quant_extraction else "Not available")
    prompt = prompt.replace("{triangulation_verdict}",
                            json.dumps(triangulation, indent=2) if triangulation else "not_triangulated")

    response = client.call(model, prompt, temperature=0.0, max_tokens=16000,
                           response_format={"type": "json_object"})
    try:
        memo = json.loads(response)
        return memo
    except json.JSONDecodeError:
        start = response.find("{")
        end = response.rfind("}") + 1
        if start >= 0 and end > start:
            return json.loads(response[start:end])
        return {"error": "JSON parse failed", "raw": response[:500]}


# ─── Safeguard L2: Claim Tracing ────────────────────────────────────

def run_l2(memo: dict, verified_codes: list[dict]) -> dict:
    """Safeguard L2: Verify memo claims trace back to A1 codes."""
    valid_code_ids = {c.get("code_id") for c in verified_codes if c.get("l1_status") != "fail"}
    failed_code_ids = {c.get("code_id") for c in verified_codes if c.get("l1_status") == "fail"}

    issues = {"orphan_claims": 0, "phantom_refs": 0, "tainted_refs": 0, "model_inference": 0}
    flagged_dimensions = []

    for key, value in memo.items():
        if not isinstance(value, dict) or "support_codes" not in value:
            continue
        codes_cited = value.get("support_codes", [])
        support_type = value.get("support_type", "")

        if not codes_cited and value.get("text", "") and value["text"] != "Not addressed in this paper":
            issues["orphan_claims"] += 1
            flagged_dimensions.append({"dimension": key, "issue": "orphan_claim"})

        for cid in codes_cited:
            if cid not in valid_code_ids and cid not in failed_code_ids:
                issues["phantom_refs"] += 1
                flagged_dimensions.append({"dimension": key, "issue": "phantom_ref", "code_id": cid})
            elif cid in failed_code_ids:
                issues["tainted_refs"] += 1
                flagged_dimensions.append({"dimension": key, "issue": "tainted_ref", "code_id": cid})

        if support_type == "model_inference":
            issues["model_inference"] += 1
            flagged_dimensions.append({"dimension": key, "issue": "model_inference"})

    return {"issues": issues, "flagged_dimensions": flagged_dimensions}


# ─── Safeguard L3: Adversarial Error-Finding ────────────────────────

def run_l3(client: LLMClient, model: str, paper_id: str,
           memo: dict, paper_text: str) -> dict:
    """Safeguard L3: Adversarial pass checking memo against source."""
    prompt_template = load_prompt("l3_adversarial")
    # Truncate paper text if too long (keep first 80K chars)
    truncated_text = paper_text[:80000] if len(paper_text) > 80000 else paper_text

    prompt = prompt_template.replace("{paper_id}", paper_id)
    prompt = prompt.replace("{a2_memo}", json.dumps(memo, indent=2))
    prompt = prompt.replace("{paper_text}", truncated_text)

    response = client.call(model, prompt, temperature=0.0, max_tokens=16000,
                           response_format={"type": "json_object"})
    try:
        result = json.loads(response)
        return result
    except json.JSONDecodeError:
        start = response.find("{")
        end = response.rfind("}") + 1
        if start >= 0 and end > start:
            return json.loads(response[start:end])
        return {"paper_id": paper_id, "verdict": "clean", "issues": [],
                "parse_error": True}


# ─── Main Pipeline ──────────────────────────────────────────────────

def process_paper(client: LLMClient, model: str, paper_id: str,
                  triangulation_by_paper: dict, dry_run: bool = False) -> dict:
    """Run the full A1→L1→A2→L2→L3 pipeline for one paper."""
    result = {
        "paper_id": paper_id, "model": model,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "status": "pending",
    }

    # Load paper text
    text_path = find_text_file(paper_id)
    if not text_path:
        result["status"] = "skip_no_text"
        return result
    with open(text_path, encoding="utf-8", errors="replace") as f:
        paper_text = f.read()

    # Load enrichment data
    p2_meta = load_p2_frontmatter(paper_id)
    quant_extraction = load_quantitative_extraction(paper_id)
    triangulation = triangulation_by_paper.get(paper_id)

    if dry_run:
        result["status"] = "dry_run"
        result["text_length"] = len(paper_text)
        result["has_quant"] = quant_extraction is not None
        result["has_triangulation"] = triangulation is not None
        return result

    # A1: Open coding
    logger.info("  A1 open coding: %s", paper_id)
    codes = run_a1(client, model, paper_id, paper_text)
    result["a1_code_count"] = len(codes)

    # L1: Quote verification
    verified_codes, l1_stats = run_l1(codes, paper_text)
    result["l1_stats"] = l1_stats

    # A2: Memo compression
    logger.info("  A2 memo compression: %s", paper_id)
    memo = run_a2(client, model, paper_id, verified_codes, p2_meta, quant_extraction, triangulation)
    result["a2_dimensions"] = len([k for k in memo.keys() if k.startswith("dimension_")])

    # L2: Claim tracing
    l2_result = run_l2(memo, verified_codes)
    result["l2_issues"] = l2_result["issues"]

    # L3: Adversarial check
    logger.info("  L3 adversarial check: %s", paper_id)
    l3_result = run_l3(client, model, paper_id, memo, paper_text)
    # Handle both old schema (problems_found) and new schema (verdict)
    verdict = l3_result.get("verdict", "")
    if verdict:
        result["l3_verdict"] = verdict
        result["l3_issue_count"] = len(l3_result.get("issues", []))
    else:
        result["l3_verdict"] = "material_issue" if l3_result.get("problems_found") else "clean"
        result["l3_issue_count"] = l3_result.get("problem_count", 0)

    result["status"] = "complete"
    return result, codes, memo, l3_result


def _get_git_commit_hash() -> str:
    """Get the current git commit hash for provenance tracking."""
    import subprocess
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            capture_output=True, text=True, cwd=_PROJECT_ROOT,
        )
        return result.stdout.strip() if result.returncode == 0 else "unknown"
    except Exception:
        return "unknown"


def _get_next_iteration(pilot_silo_dir: str) -> int:
    """Find the next iteration number by scanning existing iter_NN_* folders."""
    existing = []
    if os.path.isdir(pilot_silo_dir):
        for name in os.listdir(pilot_silo_dir):
            if name.startswith("iter_") and os.path.isdir(os.path.join(pilot_silo_dir, name)):
                try:
                    num = int(name.split("_")[1])
                    existing.append(num)
                except (IndexError, ValueError):
                    pass
    return max(existing, default=0) + 1


def _build_run_id(model: str, pilot_silo_dir: str | None = None) -> str:
    """Build a unique run identifier. Uses iteration numbering for pilot runs."""
    model_suffix = model.replace(".", "_")
    if pilot_silo_dir:
        iteration = _get_next_iteration(pilot_silo_dir)
        prompt_version = f"v{_get_git_commit_hash()[:7]}"
        return f"iter_{iteration:02d}_{model_suffix}_{prompt_version}"
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"run_{ts}_{model_suffix}"


def _build_run_manifest(run_id: str, model: str, silo: str,
                        pilot: bool, temperature: float = 0.0) -> dict:
    """Build a provenance manifest for GenAI compliance (Pillars 3+4)."""
    return {
        "run_id": run_id,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "model": model,
        "silo": silo,
        "pilot": pilot,
        "git_commit": _get_git_commit_hash(),
        "temperature": temperature,
        "response_format": "json_object",
        "prompts": {
            "a1": "p3_thematic_synthesis/prompts/a1_open_coding.txt",
            "a2": "p3_thematic_synthesis/prompts/a2_memo_compression.txt",
            "l3": "p3_thematic_synthesis/prompts/l3_adversarial.txt",
        },
        "pipeline_script": "p3_thematic_synthesis/scripts/run_thematic_pipeline.py",
        "inclusion_source": f"shared/phase3/inclusion/{silo}.json",
        "text_readiness_source": f"shared/phase3/text_readiness/{silo}.json",
        "azure_endpoint": os.getenv("AZURE_ENDPOINT", ""),
        "azure_api_version": os.getenv("AZURE_API_VERSION", "2025-04-01-preview"),
    }


def run_silo(client: LLMClient, model: str, silo: str,
             triangulation_by_paper: dict, dry_run: bool = False,
             limit: int | None = None, pilot: bool = False,
             prompt_version: str = DEFAULT_PROMPT_VERSION,
             resume: str | None = None) -> dict:
    """Run the pipeline for all papers in a silo."""
    # Load inclusion list
    inclusion_path = os.path.join(INCLUSION_DIR, f"{silo}.json")
    with open(inclusion_path, encoding="utf-8") as f:
        inclusion = json.load(f)

    # Load text readiness
    readiness_path = os.path.join(TEXT_READINESS_DIR, f"{silo}.json")
    with open(readiness_path, encoding="utf-8") as f:
        readiness = json.load(f)
    readiness_map = {p["paper_id"]: p["status"] for p in readiness["papers"]}

    # Filter to thematic-scope, usable papers
    eligible = [
        p for p in inclusion["papers"]
        if p.get("in_thematic_scope")
        and readiness_map.get(p["paper_id"]) in ("full_text_usable", "partial_text_salvageable")
    ]

    if limit:
        eligible = eligible[:limit]

    logger.info("Silo %s: %d eligible papers (model: %s, dry_run: %s)", silo, len(eligible), model, dry_run)

    # Build run directory — iteration-numbered for pilot, timestamped for production
    if resume:
        # Resume into an existing iteration folder
        if pilot:
            base_dir = os.path.join(CODING_DIR, "pilot", silo, resume)
        else:
            base_dir = os.path.join(CODING_DIR, silo, resume)
        run_id = resume
        if not os.path.isdir(base_dir):
            raise FileNotFoundError(f"Resume directory not found: {base_dir}")
        logger.info("RESUMING into existing run: %s", base_dir)
    elif pilot:
        pilot_silo_dir = os.path.join(CODING_DIR, "pilot", silo)
        run_id = _build_run_id(model, pilot_silo_dir)
        base_dir = os.path.join(pilot_silo_dir, run_id)
    else:
        run_id = _build_run_id(model)
        base_dir = os.path.join(CODING_DIR, silo, run_id)
    codes_dir = os.path.join(base_dir, "codes")
    memos_dir = os.path.join(base_dir, "memos")
    os.makedirs(codes_dir, exist_ok=True)
    os.makedirs(memos_dir, exist_ok=True)

    # Write run manifest (GenAI compliance: Pillar 3 audit trail + Pillar 4 reproducibility)
    manifest = _build_run_manifest(run_id, model, silo, pilot)
    manifest["eligible_papers"] = len(eligible)
    manifest["limit"] = limit
    manifest["prompt_version"] = prompt_version
    manifest_path = os.path.join(base_dir, "run_manifest.json")
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)
    logger.info("Run manifest: %s", manifest_path)

    silo_stats = {"processed": 0, "skipped": 0, "errors": 0, "l1_stats": {}, "l3_stats": {}}
    paper_results = []

    for i, paper in enumerate(eligible, 1):
        paper_id = paper["paper_id"]

        # Resume support: skip papers already processed (non-empty codes file)
        codes_path = os.path.join(codes_dir, f"{paper_id}.jsonl")
        if os.path.isfile(codes_path) and os.path.getsize(codes_path) > 0:
            logger.info("[%d/%d] Skipping %s — already processed", i, len(eligible), paper_id)
            silo_stats["skipped"] += 1
            continue

        logger.info("[%d/%d] Processing %s", i, len(eligible), paper_id)

        try:
            output = process_paper(client, model, paper_id, triangulation_by_paper, dry_run)

            if dry_run:
                paper_results.append(output)
                silo_stats["processed"] += 1
                continue

            result, codes, memo, l3_result = output

            # Save codes
            codes_path = os.path.join(codes_dir, f"{paper_id}.jsonl")
            with open(codes_path, "w", encoding="utf-8") as f:
                for code in codes:
                    f.write(json.dumps(code, ensure_ascii=False) + "\n")

            # Save memo
            memo_path = os.path.join(memos_dir, f"{paper_id}.json")
            with open(memo_path, "w", encoding="utf-8") as f:
                json.dump(memo, f, indent=2, ensure_ascii=False)

            # Save L3 result alongside memo
            l3_path = os.path.join(memos_dir, f"{paper_id}_l3.json")
            with open(l3_path, "w", encoding="utf-8") as f:
                json.dump(l3_result, f, indent=2, ensure_ascii=False)

            paper_results.append(result)
            silo_stats["processed"] += 1

        except Exception as exc:
            logger.error("Error processing %s: %s", paper_id, exc)
            paper_results.append({"paper_id": paper_id, "status": "error", "error": str(exc)})
            silo_stats["errors"] += 1

    # Aggregate L1 stats
    total_l1 = {"pass": 0, "pass_fuzzy": 0, "fail": 0, "total": 0}
    for r in paper_results:
        if isinstance(r, dict) and "l1_stats" in r:
            for k in total_l1:
                total_l1[k] += r["l1_stats"].get(k, 0)
    silo_stats["l1_stats"] = total_l1

    # Save silo summary
    summary = {
        "run_id": run_id,
        "silo": silo, "model": model, "dry_run": dry_run,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "git_commit": _get_git_commit_hash(),
        "stats": silo_stats, "papers": paper_results,
    }

    summary_path = os.path.join(base_dir, "run_summary.json")
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)

    # Append to iteration log (GenAI compliance: tracks all runs for audit trail)
    iteration_log_path = os.path.join(CODING_DIR, "pilot", "iteration_log.jsonl") if pilot else os.path.join(CODING_DIR, "iteration_log.jsonl")
    os.makedirs(os.path.dirname(iteration_log_path), exist_ok=True)
    log_entry = {
        "run_id": run_id,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "silo": silo,
        "model": model,
        "git_commit": _get_git_commit_hash(),
        "temperature": 0.0,
        "prompt_version": prompt_version,
        "papers_eligible": len(eligible),
        "papers_processed": silo_stats["processed"],
        "papers_errors": silo_stats["errors"],
        "l1_pass_rate": round((total_l1["pass"] + total_l1["pass_fuzzy"]) / total_l1["total"] * 100, 1) if total_l1["total"] > 0 else 0,
        "l1_fail_rate": round(total_l1["fail"] / total_l1["total"] * 100, 1) if total_l1["total"] > 0 else 0,
        "output_dir": base_dir,
    }
    with open(iteration_log_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")
    logger.info("Iteration logged: %s", iteration_log_path)

    logger.info("Silo %s complete: %d processed, %d errors", silo, silo_stats["processed"], silo_stats["errors"])
    if total_l1["total"] > 0:
        pass_rate = (total_l1["pass"] + total_l1["pass_fuzzy"]) / total_l1["total"] * 100
        fail_rate = total_l1["fail"] / total_l1["total"] * 100
        logger.info("  L1 quote verification: %.1f%% pass, %.1f%% fail", pass_rate, fail_rate)

    return summary


def main():
    parser = argparse.ArgumentParser(description="Run thematic coding pipeline (Step 3.5)")
    parser.add_argument("--silo", type=str, help="Single silo to process (folder name)")
    parser.add_argument("--all", action="store_true", help="Process all silos")
    parser.add_argument("--model", type=str, action="append", default=[],
                        help="Model(s) to use (can specify multiple for comparison)")
    parser.add_argument("--dry-run", action="store_true", help="Check eligibility without LLM calls")
    parser.add_argument("--limit", type=int, help="Limit papers per silo (for testing)")
    parser.add_argument("--pilot", action="store_true", help="Write outputs to pilot/ directory instead of silo production folders")
    parser.add_argument("--prompt-version", type=str, default=DEFAULT_PROMPT_VERSION, help="Prompt version suffix (default: v2)")
    parser.add_argument("--resume", type=str, help="Resume into existing iteration folder name (e.g. iter_07_gpt-5_1_vfaa20fe)")
    args = parser.parse_args()

    if not args.model:
        args.model = ["gpt-5-mini"]

    if not args.silo and not args.all:
        parser.error("Specify --silo <name> or --all")

    # Load triangulation data once
    logger.info("Loading triangulation matrix...")
    triangulation_by_paper = load_triangulation_verdicts()
    logger.info("Loaded triangulation for %d papers", len(triangulation_by_paper))

    client = LLMClient() if not args.dry_run else None

    # Determine silos
    if args.all:
        silos = [Path(p).stem for p in sorted(Path(INCLUSION_DIR).glob("*.json"))]
    else:
        silos = [args.silo]

    for model in args.model:
        logger.info("=== Model: %s ===", model)
        for silo in silos:
            run_silo(client, model, silo, triangulation_by_paper, args.dry_run, args.limit, args.pilot, args.prompt_version, args.resume)


if __name__ == "__main__":
    main()
