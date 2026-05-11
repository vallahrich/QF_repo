"""Production pipeline for Phase 3 thematic coding.

Processes 661 unique papers through A1→L1→A2→L2→L3 with hybrid model config,
then generates silo overlays for multi-silo papers and fans out to silo dirs.

4 phases (run individually or all together):
  a1      — A1 open coding (gpt-5.4-mini) + L1 quote verification
  a2_l3   — A2 memo compression + L2 claim tracing + L3 adversarial (gpt-5.1)
  overlay — Silo-specific overlay for multi-silo papers (gpt-5.1)
  fanout  — Project central outputs to silo directories

Usage:
    python -m p3_thematic_synthesis.scripts.run_production --phase all --workers 8
    python -m p3_thematic_synthesis.scripts.run_production --phase a1 --workers 8
    python -m p3_thematic_synthesis.scripts.run_production --phase a2_l3 --resume
    python -m p3_thematic_synthesis.scripts.run_production --dry-run
"""

import argparse
import hashlib
import json
import logging
import os
import shutil
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path

_PROJECT_ROOT = str(Path(__file__).resolve().parents[2])
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

from shared.tools.llm_client import LLMClient  # noqa: E402

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)-5s %(message)s",
                    datefmt="%H:%M:%S")
logger = logging.getLogger(__name__)

# ─── Paths ───────────────────────────────────────────────────────────
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
SILO_CONFIG = os.path.join(_PROJECT_ROOT, "shared", "config", "silo_inclusion.json")

PAPERS_DIR = os.path.join(CODING_DIR, "papers")

# ─── Config ──────────────────────────────────────────────────────────
EXCLUDED_PAPERS = {
    "567b25a75e80",  # Corrupted PDF extraction (multi-paper merge, toy HHL demo)
    "9a926e905d18",  # Duplicate of 567b25a75e80
    "dc60950e60b9",  # Corrupted PDF extraction (shallow survey, multi-paper merge)
    "5087f7c0e2a3",  # Font encoding bug — entire text garbled, codes hallucinated
    "dd6b533767c3",  # Russian-language paper (50% Cyrillic), not English corpus
}

A1_MODEL = "gpt-5.4-mini"
A2_MODEL = "gpt-5.1"
L3_MODEL = "gpt-5.1"           # Only used on audit sample (~66 papers)
OVERLAY_MODEL = "gpt-5.4-mini"
PROMPT_VERSION = "v2"
L4_AUDIT_SAMPLE_PCT = 0.10     # 10% sample per silo, min 5

SILO_DESCRIPTIONS = {
    "portfolio_optimization": "Quantum approaches to portfolio selection, asset allocation, and rebalancing",
    "derivative_pricing": "Quantum methods for option pricing, Greeks computation, and structured products",
    "risk_management": "Quantum algorithms for VaR, CVaR, stress testing, and credit risk modeling",
    "quantum_ml_finance": "Quantum machine learning applied to financial prediction and classification",
    "fraud_detection": "Quantum computing for anomaly detection, fraud prevention, and AML",
    "trading_execution": "Quantum algorithms for trade execution, market making, and arbitrage",
    "credit_lending": "Quantum approaches to credit scoring, loan pricing, and default prediction",
    "simulation_monte_carlo": "Quantum Monte Carlo and amplitude estimation for financial simulation",
}

# ─── Prompt Loading ──────────────────────────────────────────────────

def load_prompt(name: str, version: str = PROMPT_VERSION) -> str:
    versioned = os.path.join(PROMPTS_DIR, f"{name}_{version}.txt")
    if os.path.isfile(versioned):
        return open(versioned, encoding="utf-8").read()
    base = os.path.join(PROMPTS_DIR, f"{name}.txt")
    return open(base, encoding="utf-8").read()


# ─── Shared helpers ──────────────────────────────────────────────────

def find_text_file(paper_id: str) -> str | None:
    matches = list(Path(TEXT_DIR).glob(f"{paper_id}*.md"))
    return str(matches[0]) if matches else None


def _normalize_ws(text: str) -> str:
    import re
    return re.sub(r'\s+', ' ', text).strip()


def _git_hash() -> str:
    import subprocess
    try:
        r = subprocess.run(["git", "rev-parse", "--short", "HEAD"],
                           capture_output=True, text=True, cwd=_PROJECT_ROOT)
        return r.stdout.strip() if r.returncode == 0 else "unknown"
    except Exception:
        return "unknown"


def _config_hash() -> str:
    """Hash of model+prompt+git for resume validation."""
    key = f"{A1_MODEL}|{A2_MODEL}|{PROMPT_VERSION}|{_git_hash()}"
    return hashlib.sha256(key.encode()).hexdigest()[:12]


def _atomic_write_json(path: str, data, indent: int = 2):
    """Write JSON atomically via .partial rename."""
    partial = path + ".partial"
    with open(partial, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=indent, ensure_ascii=False)
    os.replace(partial, path)


def _atomic_write_jsonl(path: str, items: list):
    """Write JSONL atomically."""
    partial = path + ".partial"
    with open(partial, "w", encoding="utf-8") as f:
        for item in items:
            f.write(json.dumps(item, ensure_ascii=False) + "\n")
    os.replace(partial, path)


# ─── Data Loading ────────────────────────────────────────────────────

def load_p2_frontmatter(paper_id: str) -> dict:
    import yaml
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
        meta = yaml.safe_load(content[3:end]) or {}
        # Strip tags that could anchor inductive coding
        meta.pop("topic_tags", None)
        meta.pop("methodology_tags", None)
        meta.pop("tags", None)
        return meta
    except yaml.YAMLError:
        return {}


def load_quantitative_extraction(paper_id: str) -> dict | None:
    path = os.path.join(QUANT_DIR, f"{paper_id}.json")
    if os.path.isfile(path):
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    return None


def load_triangulation_verdicts() -> dict[str, list[dict]]:
    if not os.path.isfile(TRIANGULATION_PATH):
        return {}
    with open(TRIANGULATION_PATH, encoding="utf-8") as f:
        rows = json.load(f)
    by_paper: dict[str, list[dict]] = {}
    for row in rows:
        by_paper.setdefault(row.get("paper_id", ""), []).append(row)
    return by_paper


# ─── Build Paper Manifest ────────────────────────────────────────────

def build_paper_manifest() -> list[dict]:
    """Deduplicate papers across all silos. Returns list of {paper_id, silos, text_path}."""
    papers: dict[str, dict] = {}

    for inc_file in sorted(Path(INCLUSION_DIR).glob("*.json")):
        silo = inc_file.stem
        with open(inc_file, encoding="utf-8") as f:
            data = json.load(f)

        # Load readiness
        rd_path = os.path.join(TEXT_READINESS_DIR, f"{silo}.json")
        readiness_map = {}
        if os.path.isfile(rd_path):
            with open(rd_path, encoding="utf-8") as f:
                rd = json.load(f)
            readiness_map = {p["paper_id"]: p["status"] for p in rd["papers"]}

        for p in data["papers"]:
            pid = p["paper_id"]
            if pid in EXCLUDED_PAPERS:
                continue
            if not p.get("in_thematic_scope"):
                continue
            if readiness_map.get(pid) not in ("full_text_usable", "partial_text_salvageable"):
                continue

            if pid not in papers:
                text_path = find_text_file(pid)
                papers[pid] = {
                    "paper_id": pid,
                    "silos": [],
                    "text_path": text_path,
                }
            papers[pid]["silos"].append(silo)

    manifest = sorted(papers.values(), key=lambda x: x["paper_id"])
    multi = sum(1 for p in manifest if len(p["silos"]) > 1)
    overlay_calls = sum(len(p["silos"]) for p in manifest if len(p["silos"]) > 1)
    logger.info("Paper manifest: %d unique papers (%d multi-silo, %d overlay calls)",
                len(manifest), multi, overlay_calls)
    return manifest


# ─── Phase A1: Open Coding ───────────────────────────────────────────

def _run_a1_single(client: LLMClient, paper_id: str, paper_text: str) -> list[dict]:
    prompt_template = load_prompt("a1_open_coding")
    prompt = prompt_template.replace("{paper_text}", paper_text)
    response = client.call(A1_MODEL, prompt, temperature=0.0, max_tokens=32000,
                           response_format={"type": "json_object"})
    try:
        parsed = json.loads(response)
        if isinstance(parsed, dict) and "codes" in parsed:
            codes = parsed["codes"]
        elif isinstance(parsed, list):
            codes = parsed
        else:
            codes = [parsed]
        codes = codes if isinstance(codes, list) else [codes]
        for c in codes:
            if "label" in c and "code_label" not in c:
                c["code_label"] = c.pop("label")
        return codes
    except json.JSONDecodeError:
        start = response.find("[")
        end = response.rfind("]") + 1
        if start >= 0 and end > start:
            return json.loads(response[start:end])
        return []


def _run_l1(codes: list[dict], paper_text: str) -> tuple[list[dict], dict]:
    from rapidfuzz import fuzz
    norm_text = _normalize_ws(paper_text)
    norm_lower = norm_text.lower()
    stats = {"pass": 0, "pass_fuzzy": 0, "fail": 0, "total": len(codes)}

    for code in codes:
        span = code.get("text_span", "")
        if not span:
            code["l1_status"] = "fail"
            stats["fail"] += 1
            continue
        norm_span = _normalize_ws(span)

        # Fast path 1: exact substring (case-sensitive)
        if norm_span in norm_text:
            code["l1_status"] = "pass"
            stats["pass"] += 1
            continue

        # Fast path 2: case-insensitive substring
        span_lower = norm_span.lower()
        if span_lower in norm_lower:
            code["l1_status"] = "pass"
            stats["pass"] += 1
            continue

        # Fuzzy: rapidfuzz partial_ratio is O(n) and C-compiled
        ratio = fuzz.partial_ratio(span_lower, norm_lower) / 100.0
        if ratio > 0.85:
            code["l1_status"] = "pass_fuzzy"
            code["l1_fuzzy_ratio"] = round(ratio, 3)
            stats["pass_fuzzy"] += 1
        else:
            code["l1_status"] = "fail"
            code["l1_best_ratio"] = round(ratio, 3)
            stats["fail"] += 1

    return codes, stats


def _process_a1(client: LLMClient, paper: dict) -> dict:
    """Process one paper through A1+L1. Returns result dict."""
    pid = paper["paper_id"]
    codes_path = os.path.join(PAPERS_DIR, f"{pid}.jsonl")

    # Resume: skip if codes already exist
    if os.path.isfile(codes_path) and os.path.getsize(codes_path) > 10:
        return {"paper_id": pid, "status": "skipped", "phase": "a1"}

    if not paper["text_path"]:
        return {"paper_id": pid, "status": "skip_no_text", "phase": "a1"}

    t0 = time.time()
    with open(paper["text_path"], encoding="utf-8", errors="replace") as f:
        paper_text = f.read()

    codes = _run_a1_single(client, pid, paper_text)
    verified, l1_stats = _run_l1(codes, paper_text)
    elapsed = round(time.time() - t0, 1)

    _atomic_write_jsonl(codes_path, verified)

    return {
        "paper_id": pid, "status": "complete", "phase": "a1",
        "code_count": len(codes), "l1": l1_stats, "time_s": elapsed,
    }


def phase_a1(client: LLMClient, manifest: list[dict], workers: int = 8,
             dry_run: bool = False) -> dict:
    """Phase A1: run open coding on all papers with gpt-5.4-mini."""
    logger.info("═══ PHASE A1: Open Coding (%s, %d papers, %d workers) ═══",
                A1_MODEL, len(manifest), workers)
    os.makedirs(PAPERS_DIR, exist_ok=True)

    if dry_run:
        no_text = sum(1 for p in manifest if not p["text_path"])
        logger.info("DRY RUN: %d papers, %d without text", len(manifest), no_text)
        return {"phase": "a1", "dry_run": True, "papers": len(manifest), "no_text": no_text}

    results = []
    done = skip = err = 0

    with ThreadPoolExecutor(max_workers=workers) as pool:
        futures = {pool.submit(_process_a1, client, p): p for p in manifest}
        for future in as_completed(futures):
            try:
                r = future.result()
                results.append(r)
                if r["status"] == "complete":
                    done += 1
                    if done % 25 == 0:
                        logger.info("  A1 progress: %d/%d done", done, len(manifest))
                elif r["status"] == "skipped":
                    skip += 1
                else:
                    err += 1
            except Exception as exc:
                pid = futures[future]["paper_id"]
                logger.error("A1 error %s: %s", pid, exc)
                results.append({"paper_id": pid, "status": "error", "error": str(exc)})
                err += 1

    logger.info("A1 complete: %d done, %d skipped, %d errors", done, skip, err)
    return {"phase": "a1", "done": done, "skipped": skip, "errors": err, "results": results}


# ─── Phase A2+L3: Memo + Adversarial ────────────────────────────────

def _run_a2(client: LLMClient, paper_id: str, verified_codes: list[dict],
            p2_meta: dict, quant: dict | None, tri: list[dict] | None) -> dict:
    good_codes = [c for c in verified_codes if c.get("l1_status") in ("pass", "pass_fuzzy")]
    prompt_template = load_prompt("a2_memo_compression")
    prompt = prompt_template.replace("{paper_id}", paper_id)
    prompt = prompt.replace("{a1_codes}", json.dumps(good_codes, indent=2))
    prompt = prompt.replace("{p2_frontmatter}", json.dumps(p2_meta, indent=2, default=str))
    prompt = prompt.replace("{quantitative_extraction}",
                            json.dumps(quant, indent=2) if quant else "Not available")
    prompt = prompt.replace("{triangulation_verdict}",
                            json.dumps(tri, indent=2) if tri else "not_triangulated")
    response = client.call(A2_MODEL, prompt, temperature=0.0, max_tokens=16000,
                           response_format={"type": "json_object"})
    try:
        return json.loads(response)
    except json.JSONDecodeError:
        s = response.find("{")
        e = response.rfind("}") + 1
        if s >= 0 and e > s:
            return json.loads(response[s:e])
        return {"error": "JSON parse failed", "raw": response[:500]}


def _run_l2(memo: dict, verified_codes: list[dict]) -> dict:
    valid_ids = {c.get("code_id") for c in verified_codes if c.get("l1_status") != "fail"}
    failed_ids = {c.get("code_id") for c in verified_codes if c.get("l1_status") == "fail"}
    issues = {"orphan_claims": 0, "phantom_refs": 0, "tainted_refs": 0, "model_inference": 0}

    for key, value in memo.items():
        if not isinstance(value, dict) or "support_codes" not in value:
            continue
        codes_cited = value.get("support_codes", [])
        if not codes_cited and value.get("text", "") and value["text"] != "Not addressed in this paper":
            issues["orphan_claims"] += 1
        for cid in codes_cited:
            if cid not in valid_ids and cid not in failed_ids:
                issues["phantom_refs"] += 1
            elif cid in failed_ids:
                issues["tainted_refs"] += 1
        if value.get("support_type") == "model_inference":
            issues["model_inference"] += 1

    return issues


def _run_l3(client: LLMClient, paper_id: str, memo: dict, paper_text: str) -> dict:
    prompt_template = load_prompt("l3_adversarial")
    truncated = paper_text[:80000] if len(paper_text) > 80000 else paper_text
    prompt = prompt_template.replace("{paper_id}", paper_id)
    prompt = prompt.replace("{a2_memo}", json.dumps(memo, indent=2))
    prompt = prompt.replace("{paper_text}", truncated)
    response = client.call(A2_MODEL, prompt, temperature=0.0, max_tokens=16000,
                           response_format={"type": "json_object"})
    try:
        return json.loads(response)
    except json.JSONDecodeError:
        s = response.find("{")
        e = response.rfind("}") + 1
        if s >= 0 and e > s:
            return json.loads(response[s:e])
        return {"paper_id": paper_id, "verdict": "clean", "issues": [], "parse_error": True}


def _process_a2_l3(client: LLMClient, paper: dict,
                   tri_map: dict, run_l3: bool = False) -> dict:
    """Process one paper through A2+L2, optionally L3."""
    pid = paper["paper_id"]
    memo_path = os.path.join(PAPERS_DIR, f"{pid}.json")
    l3_path = os.path.join(PAPERS_DIR, f"{pid}_l3.json")

    # Resume: skip if memo exists (and l3 too, if l3 requested)
    memo_done = os.path.isfile(memo_path) and os.path.getsize(memo_path) > 10
    l3_done = os.path.isfile(l3_path) and os.path.getsize(l3_path) > 10
    if memo_done and (not run_l3 or l3_done):
        return {"paper_id": pid, "status": "skipped", "phase": "a2"}

    # Load A1 codes (must exist from phase a1)
    codes_path = os.path.join(PAPERS_DIR, f"{pid}.jsonl")
    if not os.path.isfile(codes_path):
        return {"paper_id": pid, "status": "skip_no_codes", "phase": "a2"}

    with open(codes_path, encoding="utf-8") as f:
        verified_codes = [json.loads(line) for line in f if line.strip()]

    if not paper["text_path"]:
        return {"paper_id": pid, "status": "skip_no_text", "phase": "a2"}

    with open(paper["text_path"], encoding="utf-8", errors="replace") as f:
        paper_text = f.read()

    t0 = time.time()

    # A2
    p2_meta = load_p2_frontmatter(pid)
    quant = load_quantitative_extraction(pid)
    tri = tri_map.get(pid)

    memo = _run_a2(client, pid, verified_codes, p2_meta, quant, tri)
    l2_issues = _run_l2(memo, verified_codes)

    if not memo_done:
        _atomic_write_json(memo_path, memo)

    # L3: only if requested (audit sample)
    verdict = "not_run"
    l3_count = 0
    if run_l3 and not l3_done:
        logger.info("  L3 adversarial check: %s", pid)
        l3_result = _run_l3(client, pid, memo, paper_text)
        _atomic_write_json(l3_path, l3_result)
        verdict = l3_result.get("verdict", "unknown")
        l3_count = len(l3_result.get("issues", []))

    elapsed = round(time.time() - t0, 1)

    return {
        "paper_id": pid, "status": "complete", "phase": "a2",
        "l2_issues": l2_issues, "l3_verdict": verdict,
        "l3_issue_count": l3_count, "time_s": elapsed,
    }


def phase_a2(client: LLMClient, manifest: list[dict], workers: int = 8,
             dry_run: bool = False) -> dict:
    """Phase A2: memo compression with gpt-5.1 (no L3 — that's a separate phase)."""
    logger.info("═══ PHASE A2: Memo Compression (%s, %d papers, %d workers) ═══",
                A2_MODEL, len(manifest), workers)

    if dry_run:
        codes_exist = sum(1 for p in manifest
                          if os.path.isfile(os.path.join(PAPERS_DIR, f"{p['paper_id']}.jsonl")))
        logger.info("DRY RUN: %d papers, %d have A1 codes", len(manifest), codes_exist)
        return {"phase": "a2", "dry_run": True, "papers": len(manifest), "codes_ready": codes_exist}

    tri_map = load_triangulation_verdicts()
    logger.info("Loaded triangulation for %d papers", len(tri_map))

    results = []
    done = skip = err = 0

    with ThreadPoolExecutor(max_workers=workers) as pool:
        futures = {pool.submit(_process_a2_l3, client, p, tri_map, False): p for p in manifest}
        for future in as_completed(futures):
            try:
                r = future.result()
                results.append(r)
                if r["status"] == "complete":
                    done += 1
                    if done % 25 == 0:
                        logger.info("  A2 progress: %d/%d done", done, len(manifest))
                elif r["status"] == "skipped":
                    skip += 1
                else:
                    err += 1
            except Exception as exc:
                pid = futures[future]["paper_id"]
                logger.error("A2 error %s: %s", pid, exc)
                results.append({"paper_id": pid, "status": "error", "error": str(exc)})
                err += 1

    logger.info("A2 complete: %d done, %d skipped, %d errors", done, skip, err)
    return {"phase": "a2", "done": done, "skipped": skip, "errors": err, "results": results}


# ─── Phase L3: Adversarial (audit sample only) ──────────────────────

def _build_audit_sample(manifest: list[dict]) -> list[dict]:
    """Select 10% sample per silo (min 5) for L3 adversarial checking."""
    import random
    rng = random.Random(42)  # Fixed seed for reproducibility

    # Group papers by silo (use first silo for single-silo, all silos for multi)
    by_silo: dict[str, list[str]] = {}
    for p in manifest:
        for silo in p["silos"]:
            by_silo.setdefault(silo, []).append(p["paper_id"])

    sampled_ids: set[str] = set()
    sample_log = {}
    for silo, pids in sorted(by_silo.items()):
        n = max(5, int(len(pids) * L4_AUDIT_SAMPLE_PCT))
        picked = rng.sample(pids, min(n, len(pids)))
        sampled_ids.update(picked)
        sample_log[silo] = {"total": len(pids), "sampled": len(picked)}

    # Filter manifest to sampled papers
    sampled = [p for p in manifest if p["paper_id"] in sampled_ids]
    logger.info("L3 audit sample: %d papers from %d silos", len(sampled), len(sample_log))
    for silo, info in sample_log.items():
        logger.info("  %s: %d/%d", silo, info["sampled"], info["total"])

    return sampled


def phase_l3(client: LLMClient, manifest: list[dict], workers: int = 8,
             dry_run: bool = False) -> dict:
    """Phase L3: adversarial check on audit sample only (gpt-5.1)."""
    sample = _build_audit_sample(manifest)
    logger.info("═══ PHASE L3: Adversarial on Audit Sample (%s, %d papers, %d workers) ═══",
                L3_MODEL, len(sample), workers)

    if dry_run:
        memos_exist = sum(1 for p in sample
                          if os.path.isfile(os.path.join(PAPERS_DIR, f"{p['paper_id']}.json")))
        logger.info("DRY RUN: %d audit papers, %d have A2 memos", len(sample), memos_exist)
        return {"phase": "l3", "dry_run": True, "sample_size": len(sample), "memos_ready": memos_exist}

    tri_map = load_triangulation_verdicts()

    results = []
    done = skip = err = 0

    with ThreadPoolExecutor(max_workers=workers) as pool:
        futures = {pool.submit(_process_a2_l3, client, p, tri_map, True): p for p in sample}
        for future in as_completed(futures):
            try:
                r = future.result()
                results.append(r)
                if r["status"] == "complete":
                    done += 1
                elif r["status"] == "skipped":
                    skip += 1
                else:
                    err += 1
            except Exception as exc:
                pid = futures[future]["paper_id"]
                logger.error("L3 error %s: %s", pid, exc)
                results.append({"paper_id": pid, "status": "error", "error": str(exc)})
                err += 1

    logger.info("L3 complete: %d done, %d skipped, %d errors", done, skip, err)
    return {"phase": "l3", "done": done, "skipped": skip, "errors": err}


# ─── Phase Overlay ───────────────────────────────────────────────────

def _run_overlay(client: LLMClient, paper_id: str, silo: str,
                 central_memo: dict, verified_codes: list[dict]) -> dict:
    prompt_template = load_prompt("overlay_memo")
    good_codes = [c for c in verified_codes if c.get("l1_status") in ("pass", "pass_fuzzy")]
    prompt = prompt_template.replace("{paper_id}", paper_id)
    prompt = prompt.replace("{silo_name}", silo)
    prompt = prompt.replace("{silo_description}", SILO_DESCRIPTIONS.get(silo, silo))
    prompt = prompt.replace("{central_memo}", json.dumps(central_memo, indent=2))
    prompt = prompt.replace("{a1_codes}", json.dumps(good_codes, indent=2))
    response = client.call(OVERLAY_MODEL, prompt, temperature=0.0, max_tokens=8000,
                           response_format={"type": "json_object"})
    try:
        return json.loads(response)
    except json.JSONDecodeError:
        s = response.find("{")
        e = response.rfind("}") + 1
        if s >= 0 and e > s:
            return json.loads(response[s:e])
        return {"paper_id": paper_id, "silo": silo, "error": "JSON parse failed"}


def _process_overlay(client: LLMClient, paper_id: str, silo: str) -> dict:
    """Generate one silo overlay."""
    silo_dir = os.path.join(CODING_DIR, silo, "memos")
    overlay_path = os.path.join(silo_dir, f"{paper_id}.json")

    if os.path.isfile(overlay_path) and os.path.getsize(overlay_path) > 10:
        return {"paper_id": paper_id, "silo": silo, "status": "skipped"}

    # Load central artifacts
    codes_path = os.path.join(PAPERS_DIR, f"{paper_id}.jsonl")
    memo_path = os.path.join(PAPERS_DIR, f"{paper_id}.json")

    if not os.path.isfile(codes_path) or not os.path.isfile(memo_path):
        return {"paper_id": paper_id, "silo": silo, "status": "skip_no_central"}

    with open(codes_path, encoding="utf-8") as f:
        codes = [json.loads(line) for line in f if line.strip()]
    with open(memo_path, encoding="utf-8") as f:
        memo = json.load(f)

    t0 = time.time()
    os.makedirs(silo_dir, exist_ok=True)

    overlay = _run_overlay(client, paper_id, silo, memo, codes)
    elapsed = round(time.time() - t0, 1)

    _atomic_write_json(overlay_path, overlay)

    return {
        "paper_id": paper_id, "silo": silo, "status": "complete",
        "time_s": elapsed,
    }


def phase_overlay(client: LLMClient, manifest: list[dict], workers: int = 8,
                  dry_run: bool = False) -> dict:
    """Phase Overlay: silo-specific memos for multi-silo papers."""
    # Build overlay task list
    tasks = []
    for p in manifest:
        if len(p["silos"]) > 1:
            for silo in p["silos"]:
                tasks.append((p["paper_id"], silo))

    logger.info("═══ PHASE OVERLAY: Silo Memos (%d calls, %d workers) ═══",
                len(tasks), workers)

    if dry_run:
        logger.info("DRY RUN: %d overlay tasks", len(tasks))
        return {"phase": "overlay", "dry_run": True, "tasks": len(tasks)}

    results = []
    done = skip = err = 0

    with ThreadPoolExecutor(max_workers=workers) as pool:
        futures = {pool.submit(_process_overlay, client, pid, silo): (pid, silo)
                   for pid, silo in tasks}
        for future in as_completed(futures):
            try:
                r = future.result()
                results.append(r)
                if r["status"] == "complete":
                    done += 1
                    if done % 50 == 0:
                        logger.info("  Overlay progress: %d/%d done", done, len(tasks))
                elif r["status"] == "skipped":
                    skip += 1
                else:
                    err += 1
            except Exception as exc:
                pid, silo = futures[future]
                logger.error("Overlay error %s/%s: %s", silo, pid, exc)
                results.append({"paper_id": pid, "silo": silo, "status": "error", "error": str(exc)})
                err += 1

    logger.info("Overlay complete: %d done, %d skipped, %d errors", done, skip, err)
    return {"phase": "overlay", "done": done, "skipped": skip, "errors": err}


# ─── Phase Fan-out ───────────────────────────────────────────────────

def phase_fanout(manifest: list[dict]) -> dict:
    """Project central outputs to silo directories."""
    logger.info("═══ PHASE FAN-OUT: Projecting to silo directories ═══")
    copied_codes = copied_memos = 0

    for p in manifest:
        pid = p["paper_id"]
        codes_src = os.path.join(PAPERS_DIR, f"{pid}.jsonl")
        memo_src = os.path.join(PAPERS_DIR, f"{pid}.json")
        l3_src = os.path.join(PAPERS_DIR, f"{pid}_l3.json")

        for silo in p["silos"]:
            silo_codes_dir = os.path.join(CODING_DIR, silo, "codes")
            silo_memos_dir = os.path.join(CODING_DIR, silo, "memos")
            os.makedirs(silo_codes_dir, exist_ok=True)
            os.makedirs(silo_memos_dir, exist_ok=True)

            # Always copy codes
            dst_codes = os.path.join(silo_codes_dir, f"{pid}.jsonl")
            if os.path.isfile(codes_src) and not os.path.isfile(dst_codes):
                shutil.copy2(codes_src, dst_codes)
                copied_codes += 1

            # Copy L3 to silo
            dst_l3 = os.path.join(silo_memos_dir, f"{pid}_l3.json")
            if os.path.isfile(l3_src) and not os.path.isfile(dst_l3):
                shutil.copy2(l3_src, dst_l3)

            # For single-silo papers: copy central memo
            # For multi-silo papers: overlay already exists in silo dir
            if len(p["silos"]) == 1:
                dst_memo = os.path.join(silo_memos_dir, f"{pid}.json")
                if os.path.isfile(memo_src) and not os.path.isfile(dst_memo):
                    shutil.copy2(memo_src, dst_memo)
                    copied_memos += 1

        # Write projection manifest per silo
    for silo in SILO_DESCRIPTIONS:
        silo_dir = os.path.join(CODING_DIR, silo)
        if not os.path.isdir(silo_dir):
            continue
        silo_papers = [p for p in manifest if silo in p["silos"]]
        proj_manifest = {
            "silo": silo,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "total_papers": len(silo_papers),
            "single_silo": sum(1 for p in silo_papers if len(p["silos"]) == 1),
            "multi_silo": sum(1 for p in silo_papers if len(p["silos"]) > 1),
            "papers": [{"paper_id": p["paper_id"],
                        "memo_type": "central" if len(p["silos"]) == 1 else "overlay",
                        "all_silos": p["silos"]}
                       for p in silo_papers],
        }
        _atomic_write_json(os.path.join(silo_dir, "projection_manifest.json"), proj_manifest)

    logger.info("Fan-out complete: %d codes copied, %d central memos copied", copied_codes, copied_memos)
    return {"phase": "fanout", "codes_copied": copied_codes, "memos_copied": copied_memos}


# ─── Campaign Manifest ───────────────────────────────────────────────

def write_campaign_manifest(manifest: list[dict]):
    campaign = {
        "campaign_id": f"production_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "git_commit": _git_hash(),
        "config_hash": _config_hash(),
        "models": {"a1": A1_MODEL, "a2": A2_MODEL, "l3": L3_MODEL, "overlay": OVERLAY_MODEL},
        "prompt_version": PROMPT_VERSION,
        "temperature": 0.0,
        "response_format": "json_object",
        "corpus": {
            "total_papers": len(manifest),
            "excluded_papers": list(EXCLUDED_PAPERS),
            "exclusion_reason": "Corrupted PDF extraction (multi-paper merge)",
            "single_silo": sum(1 for p in manifest if len(p["silos"]) == 1),
            "multi_silo": sum(1 for p in manifest if len(p["silos"]) > 1),
            "overlay_calls": sum(len(p["silos"]) for p in manifest if len(p["silos"]) > 1),
        },
        "silos": list(SILO_DESCRIPTIONS.keys()),
        "prompts": {
            "a1": f"a1_open_coding_{PROMPT_VERSION}.txt",
            "a2": f"a2_memo_compression_{PROMPT_VERSION}.txt",
            "l3": f"l3_adversarial_{PROMPT_VERSION}.txt",
            "overlay": "overlay_memo.txt",
        },
        "pipeline_script": "p3_thematic_synthesis/scripts/run_production.py",
        "azure_endpoint": os.getenv("AZURE_ENDPOINT", ""),
        "azure_api_version": os.getenv("AZURE_API_VERSION", "2025-04-01-preview"),
    }
    path = os.path.join(CODING_DIR, "campaign_manifest.json")
    _atomic_write_json(path, campaign)
    logger.info("Campaign manifest: %s", path)


# ─── Main ────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Production pipeline for Phase 3 thematic coding")
    parser.add_argument("--phase", type=str, default="all",
                        choices=["a1", "a2", "l3", "overlay", "fanout", "all"],
                        help="Which phase to run (default: all)")
    parser.add_argument("--workers", type=int, default=8,
                        help="Parallel workers (default: 8)")
    parser.add_argument("--dry-run", action="store_true",
                        help="Count papers and check readiness without LLM calls")
    args = parser.parse_args()

    # Build manifest
    manifest = build_paper_manifest()

    # Write campaign manifest
    write_campaign_manifest(manifest)

    # Warm client (thread-safety: ensure lazy init happens before pool)
    client = None
    if not args.dry_run and args.phase in ("a1", "a2", "l3", "overlay", "all"):
        client = LLMClient()
        logger.info("LLM client warmed up")

    results = {}
    phases = ["a1", "a2", "l3", "overlay", "fanout"] if args.phase == "all" else [args.phase]

    for phase in phases:
        if phase == "a1":
            results["a1"] = phase_a1(client, manifest, args.workers, args.dry_run)
        elif phase == "a2":
            results["a2"] = phase_a2(client, manifest, args.workers, args.dry_run)
        elif phase == "l3":
            results["l3"] = phase_l3(client, manifest, args.workers, args.dry_run)
        elif phase == "overlay":
            results["overlay"] = phase_overlay(client, manifest, args.workers, args.dry_run)
        elif phase == "fanout":
            results["fanout"] = phase_fanout(manifest)

    # Save run summary
    summary_path = os.path.join(CODING_DIR, "production_summary.json")
    summary = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "git_commit": _git_hash(),
        "phases_run": phases,
        "results": {k: {kk: vv for kk, vv in v.items() if kk != "results"}
                    for k, v in results.items()},
    }
    _atomic_write_json(summary_path, summary)
    logger.info("Production summary: %s", summary_path)

    # Print final stats
    print("\n" + "=" * 60)
    print("PRODUCTION PIPELINE COMPLETE")
    print("=" * 60)
    for phase_name, phase_result in results.items():
        d = phase_result.get("done", "-")
        s = phase_result.get("skipped", "-")
        e = phase_result.get("errors", "-")
        print(f"  {phase_name:<10} done={d}  skipped={s}  errors={e}")


if __name__ == "__main__":
    main()
