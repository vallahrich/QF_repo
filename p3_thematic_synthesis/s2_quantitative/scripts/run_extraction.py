"""P3 Quantitative Benchmark Extraction — 5-step cached-prefix pipeline.

Reads classified papers from P2 output, routes each to its P1 silo, and
runs a 5-step LLM extraction pipeline to produce structured benchmark
data conforming to benchmark_schema.json.

Architecture mirrors P2's Pipeline C: paper text is the prefix for steps
1-4 so Azure caches it after step 1, giving 88% discount on steps 2-4.
Step 5 is a synthesis step that does not use the paper text.

Usage:
    # Full run on all quantitative papers
    python -m p3_thematic_synthesis.s2_quantitative.scripts.run_extraction --parallel 8

    # Dry run
    python -m p3_thematic_synthesis.s2_quantitative.scripts.run_extraction --dry-run

    # Single paper
    python -m p3_thematic_synthesis.s2_quantitative.scripts.run_extraction --paper-id 02db829631f9

    # From manifest file
    python -m p3_thematic_synthesis.s2_quantitative.scripts.run_extraction --manifest work_manifest.json
"""

import argparse
import hashlib
import json
import logging
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import date, datetime, timezone
from pathlib import Path

# ── Path setup ────────────────────────────────────────────────────────────

_QUANT_ROOT = Path(__file__).resolve().parents[1]
_P3_ROOT = Path(__file__).resolve().parents[2]
_PROJECT_ROOT = Path(__file__).resolve().parents[3]

_project_root_str = str(_PROJECT_ROOT)
if _project_root_str not in sys.path:
    sys.path.insert(0, _project_root_str)
elif sys.path[0] != _project_root_str:
    sys.path.remove(_project_root_str)
    sys.path.insert(0, _project_root_str)

# Clear stale shared module cache
_shared_mod = sys.modules.get("shared")
if _shared_mod is not None:
    _shared_file = getattr(_shared_mod, "__file__", None) or ""
    if _PROJECT_ROOT.as_posix() not in Path(_shared_file).as_posix() if _shared_file else True:
        for _key in [k for k in sys.modules if k == "shared" or k.startswith("shared.")]:
            del sys.modules[_key]

from shared.tools.llm_client import LLMClient  # noqa: E402
from shared.tools.text_chunker import truncate_tokens  # noqa: E402

from p3_thematic_synthesis.s2_quantitative.scripts.validate_benchmarks import (  # noqa: E402
    compute_quality_score,
    normalize_extraction_metrics,
    validate_extraction,
)

# ── Logging ───────────────────────────────────────────────────────────────

logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s: %(message)s",
)
logger = logging.getLogger("p3_extraction")

# ── Config ────────────────────────────────────────────────────────────────

CONFIG_PATH = _QUANT_ROOT / "config" / "extraction_config.json"
SILO_METRICS_PATH = _QUANT_ROOT / "config" / "silo_metrics.json"
PROMPTS_DIR = _QUANT_ROOT / "prompts"
OUTPUT_DIR = _QUANT_ROOT / "output" / "extractions"
P2_OUTPUT_DIR = _PROJECT_ROOT / "p2_systematic_review" / "output" / "processed"
TEXT_DIR = _PROJECT_ROOT / "shared" / "extracted_text" / "text"

SKIP_SOURCE_TYPES = {"survey", "editorial", "meta-analysis", "book-chapter", "commentary"}

# Thesis scope: gate-based quantum computing only. Quantum annealing (D-Wave,
# adiabatic, pure QUBO-on-annealer) is out of scope. SA-01 in the P1 codebook
# maps to methodology_tag "quantum-annealing-qubo".
SCOPE_OUT_METHODOLOGY_TAGS = {
    "quantum-annealing-qubo",
    # Defensive: catch any raw tag drift from P2 re-runs or manual edits
    "SA-01",
    "quantum-annealing",
    "annealing",
    "qubo",
    "d-wave",
}


def load_config() -> dict:
    with open(CONFIG_PATH, encoding="utf-8") as f:
        return json.load(f)


def _compute_prompt_version_hash() -> str:
    """SHA-256 of the three active pipeline prompts, for freeze provenance."""
    h = hashlib.sha256()
    for name in ("step2_experiments.txt", "step3_silo_results.txt", "step4_validation.txt"):
        p = PROMPTS_DIR / name
        if p.is_file():
            h.update(p.read_bytes())
    return h.hexdigest()[:16]


_PROMPT_VERSION_HASH: str | None = None


def get_prompt_version_hash() -> str:
    global _PROMPT_VERSION_HASH
    if _PROMPT_VERSION_HASH is None:
        _PROMPT_VERSION_HASH = _compute_prompt_version_hash()
    return _PROMPT_VERSION_HASH


def load_silo_metrics() -> dict:
    with open(SILO_METRICS_PATH, encoding="utf-8") as f:
        return json.load(f)


def load_prompt(filename: str) -> str:
    with open(PROMPTS_DIR / filename, encoding="utf-8") as f:
        return f.read()


def _parse_json(response, step_name: str) -> dict:
    """Parse JSON from LLM response, handling code fences and retries.

    Robust to non-string responses: some Azure-OpenAI streaming code paths
    occasionally return ``list[str]`` (one element per chunk) instead of a
    single concatenated ``str``. Joining such a list keeps the historical
    contract (`response: str`) without crashing the post-processing step
    with ``'list' object has no attribute 'strip'`` (root cause of the
    three step2 failures observed on 2026-04-17 for paper IDs
    ``0fb65bb44954``, ``48cd8220e3b2``, ``bcd1adfba1e5``).
    """
    import re
    if isinstance(response, list):
        response = "".join(str(part) for part in response)
    elif not isinstance(response, str):
        response = str(response)
    cleaned = re.sub(r"```(?:json)?\s*\n?", "", response).strip().rstrip("`").strip()
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        pass
    # Try extracting outermost JSON object
    first = cleaned.find("{")
    last = cleaned.rfind("}")
    if first != -1 and last > first:
        try:
            return json.loads(cleaned[first:last + 1])
        except json.JSONDecodeError:
            pass
    # Try to repair truncated JSON by closing open brackets
    if first != -1 and len(cleaned) > 500:
        truncated = cleaned[first:]
        # Remove trailing incomplete string/value
        # Find last complete key-value pair
        for trim in range(min(200, len(truncated)), 0, -1):
            candidate = truncated[:len(truncated) - trim]
            # Close open brackets
            open_braces = candidate.count("{") - candidate.count("}")
            open_brackets = candidate.count("[") - candidate.count("]")
            repaired = candidate + "]" * max(0, open_brackets) + "}" * max(0, open_braces)
            try:
                result = json.loads(repaired)
                logger.warning("%s: repaired truncated JSON (trimmed %d chars)", step_name, trim)
                return result
            except json.JSONDecodeError:
                continue
    raise ValueError(f"{step_name}: Could not parse JSON (len={len(response)}): {response[:150]}")


def _llm_call_with_retry(client: LLMClient, model: str, prompt: str,
                         temperature: float, max_tokens: int,
                         step_name: str, retry_temp: float = 0) -> dict:
    """Call LLM and parse JSON response. Retry once on parse failure."""
    response = client.call(model, prompt, temperature, max_tokens)
    try:
        return _parse_json(response, step_name)
    except ValueError:
        logger.warning("  %s: JSON parse failed, retrying with temp=%s", step_name, retry_temp)
        response = client.call(model, prompt, retry_temp, max_tokens)
        return _parse_json(response, step_name)


# ── Manifest Building ────────────────────────────────────────────────────

def build_work_manifest() -> list[dict]:
    """Build manifest from P2 classification outputs.
    
    Filters to papers with has_quantitative_results=True, excludes
    surveys/editorials, and assigns primary silo from topic_tags.
    """
    manifest = []
    silo_metrics = load_silo_metrics()
    valid_silos = set(silo_metrics.keys())

    for jp in sorted(P2_OUTPUT_DIR.glob("*.json")):
        paper_id = jp.stem.replace("_extraction", "")
        try:
            d = json.loads(jp.read_text("utf-8"))
        except (json.JSONDecodeError, OSError):
            continue

        # Filter: must have quantitative results
        if not d.get("has_quantitative_results"):
            continue

        # Filter: skip surveys/editorials
        source_type = d.get("source_type", "")
        if source_type in SKIP_SOURCE_TYPES:
            continue

        # Filter: thesis scope is gate-based quantum computing only.
        # Drop papers whose primary methodology is quantum annealing / QUBO-on-annealer.
        methodology_tags = d.get("methodology_tags", []) or []
        if any(t in SCOPE_OUT_METHODOLOGY_TAGS for t in methodology_tags):
            logger.debug("scope_out: %s (methodology_tags=%s)", paper_id, methodology_tags)
            continue

        # Assign primary silo from first matching topic_tag
        topic_tags = d.get("topic_tags", [])
        primary_silo = None
        secondary_silos = []
        for tag in topic_tags:
            if tag in valid_silos:
                if primary_silo is None:
                    primary_silo = tag
                else:
                    secondary_silos.append(tag)

        if primary_silo is None:
            primary_silo = "other"

        # Find text file
        text_path = None
        for tp in TEXT_DIR.glob(f"{paper_id}*"):
            text_path = str(tp)
            break

        if not text_path:
            continue

        manifest.append({
            "paper_id": paper_id,
            "primary_silo": primary_silo,
            "secondary_silos": secondary_silos,
            "methodology_tags": d.get("methodology_tags", []),
            "source_type": source_type,
            "text_path": text_path,
            "p2_metadata": {
                "title": d.get("title", ""),
                "authors": d.get("authors", []),
                "year": d.get("year"),
                "doi": d.get("doi", ""),
                "quantum_advantage_claim": d.get("quantum_advantage_claim", ""),
            },
        })

    return manifest


# ── Pipeline Steps (4-step: skip step 1, P2 provides has_quantitative_results) ──

def _build_p2_context(entry: dict) -> str:
    """Build a compact P2 context string for prompts."""
    meta = entry.get("p2_metadata", {})
    return json.dumps({
        "silo": entry["primary_silo"],
        "methodology_tags": entry.get("methodology_tags", []),
        "source_type": entry.get("source_type", ""),
        "quantum_advantage_claim": meta.get("quantum_advantage_claim", ""),
    }, indent=1)


def run_step2(client: LLMClient, paper_text: str,
              entry: dict, config: dict) -> dict:
    """Step 2: Experiments + resources + hardware + complexity (gpt-5.1)."""
    prompt_template = load_prompt("step2_experiments.txt")
    p2_context = _build_p2_context(entry)
    model = config.get("step_models", {}).get("2", config["model"])

    prompt = prompt_template.format(
        paper_text=paper_text,
        p2_context=p2_context,
        primary_silo=entry["primary_silo"],
        methodology_tags=", ".join(entry.get("methodology_tags", [])),
        source_type=entry.get("source_type", "unknown"),
    )
    step_cfg = config["step_definitions"]["2"]
    return _llm_call_with_retry(client, model, prompt,
                                config["temperature"], step_cfg["max_tokens"], "step2")


def run_step3(client: LLMClient, paper_text: str,
              step2: dict, entry: dict, config: dict,
              silo_metrics: dict) -> dict:
    """Step 3: Silo-specific results + baselines + speedups + scalability (gpt-5.1)."""
    prompt_template = load_prompt("step3_silo_results.txt")
    silo = entry["primary_silo"]
    silo_cfg = silo_metrics.get(silo, {})
    model = config.get("step_models", {}).get("3", config["model"])

    prompt = prompt_template.format(
        paper_text=paper_text,
        p2_context=_build_p2_context(entry),
        step2_experiments=json.dumps(step2.get("experiments", []), indent=1),
        silo_name=silo,
        silo_code=silo_cfg.get("code", ""),
        primary_metrics=", ".join(silo_cfg.get("primary_metrics", [])),
        scale_indicator=silo_cfg.get("scale_indicator", "problem_size"),
    )
    step_cfg = config["step_definitions"]["3"]
    return _llm_call_with_retry(client, model, prompt,
                                config["temperature"], step_cfg["max_tokens"], "step3")


def run_step4(client: LLMClient, paper_text: str, merged: dict,
              entry: dict, config: dict) -> dict:
    """Step 4: Verification + Hoefler assessment (reasoning model, WITH paper text)."""
    prompt_template = load_prompt("step4_validation.txt")
    model = config.get("step_models", {}).get("4", config["model"])

    merged_compact = json.dumps(merged, indent=1, default=str)[:12000]
    p2_context = _build_p2_context(entry)

    prompt = prompt_template.format(
        paper_text=paper_text,
        p2_context=p2_context,
        merged_data=merged_compact,
    )
    step_cfg = config["step_definitions"]["4"]
    return _llm_call_with_retry(client, model, prompt,
                                config["temperature"], step_cfg["max_tokens"], "step4")


# ── Merge Logic ───────────────────────────────────────────────────────────

def merge_steps(step2: dict, step3: dict, step4: dict,
                entry: dict, config: dict) -> dict:
    """Merge steps 2-4 into a single benchmark_schema-conformant JSON.
    
    Step 2: experiments + resources + hardware + complexity
    Step 3: silo-specific results + baselines + speedups
    Step 4: QA validation + advantage assessments
    """
    experiments = []
    step2_exps = step2.get("experiments", [])
    step3_results = {r["experiment_id"]: r for r in step3.get("experiment_results", [])}
    step4_assessments = {a["experiment_id"]: a for a in step4.get("experiment_assessments", [])}

    # Build corrections lookup from step 4
    corrections = {}
    for c in step4.get("corrections", []):
        eid = c.get("experiment_id", "")
        corrections.setdefault(eid, []).append(c)

    for exp in step2_exps:
        eid = exp["experiment_id"]
        s3 = step3_results.get(eid, {})
        s4 = step4_assessments.get(eid, {})

        # Merge provenance from step2 (hardware, resources) and step4 (advantage)
        prov_s2 = exp.get("provenance") or {}
        prov_s4 = s4.get("provenance") or {}
        merged_prov = {**prov_s2, **prov_s4}
        # Merge notes arrays from both steps
        notes_s2 = prov_s2.get("notes") or []
        notes_s4 = prov_s4.get("notes") or []
        if notes_s2 or notes_s4:
            merged_prov["notes"] = notes_s2 + notes_s4

        merged_exp = {
            "experiment_id": eid,
            "description": exp.get("description"),
            "algorithm": exp.get("algorithm", {}),
            "problem_formulation": exp.get("problem_formulation", {}),
            "problem_instance": exp.get("problem_instance", {}),
            "quantum_resources": exp.get("quantum_resources", {}),
            "hardware": exp.get("hardware", {}),
            "noise_model": exp.get("noise_model", {}),
            "implementation_details": exp.get("implementation_details", {}),
            "results": s3.get("results", []),
            "classical_baselines": s3.get("classical_baselines", []),
            "speedup_claims": s3.get("speedup_claims", []),
            "scalability_data": s3.get("scalability_data", []),
            "complexity_analysis": exp.get("complexity_analysis"),
            "advantage_assessment": s4.get("advantage_assessment", {}),
            "provenance": merged_prov if merged_prov else None,
        }

        # Apply corrections from step 4 reasoning model
        for corr in corrections.get(eid, []):
            field_path = corr.get("field", "")
            correct_val = corr.get("correct_value")
            # gpt-5.3 occasionally returns list/dict for scalar string fields
            # (e.g. dataset_specification.preprocessing). Downstream
            # normalize_extraction_metrics + validate_ranges assume strings,
            # so coerce here before merging.
            if isinstance(correct_val, list):
                correct_val = ", ".join(str(x) for x in correct_val) if correct_val else None
            elif isinstance(correct_val, dict):
                correct_val = "; ".join(f"{k}={v}" for k, v in correct_val.items()) or None
            if correct_val is not None and "." in field_path:
                parts = field_path.split(".", 1)
                section = merged_exp.get(parts[0])
                if isinstance(section, dict):
                    section[parts[1]] = correct_val

        experiments.append(merged_exp)

    # Add missed experiments from step 4
    for missed in step4.get("missed_experiments", []):
        experiments.append(missed)

    meta = entry.get("p2_metadata", {})
    silo = entry["primary_silo"]
    step_models = config.get("step_models", {})

    return {
        "paper_id": entry["paper_id"],
        "extraction_metadata": {
            "extraction_date": date.today().isoformat(),
            "run_timestamp": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "schema_version": "benchmark_extraction_v1.0",
            "prompt_version_hash": get_prompt_version_hash(),
            "scope": config.get("scope", "gate_based"),
            "models_used": step_models,
            "source_file": Path(entry["text_path"]).name,
            "pipeline": "3-step-v3",
            "quality_score": step4.get("extraction_confidence"),
            "validation_flagged": step4.get("validation", {}).get("flagged_values", 0),
            "validation_total": step4.get("validation", {}).get("total_numeric_values", 0),
        },
        "paper_metadata": {
            "title": meta.get("title", ""),
            "authors": meta.get("authors", []),
            "year": meta.get("year"),
            "doi": meta.get("doi"),
            "scope": "gate_based",
        },
        "finance_domain": {
            "primary_silo": silo,
            "secondary_silos": entry.get("secondary_silos", []),
        },
        "has_quantitative_results": len(experiments) > 0,
        "summary": step4.get("summary", ""),
        "experiments": experiments,
    }


# ── Chunking for Large Papers ─────────────────────────────────────────────

MAX_CHUNK_CHARS = 240000  # ~60K tokens
OVERLAP_CHARS = 8000      # ~2K tokens overlap between chunks


def chunk_text(text: str) -> list[str]:
    """Split text into overlapping chunks if > MAX_CHUNK_CHARS."""
    if len(text) <= MAX_CHUNK_CHARS:
        return [text]
    chunks = []
    start = 0
    while start < len(text):
        end = start + MAX_CHUNK_CHARS
        if end >= len(text):
            chunks.append(text[start:])
            break
        # Try to split at paragraph boundary
        split_at = text.rfind("\n\n", start + MAX_CHUNK_CHARS - 20000, end)
        if split_at == -1:
            split_at = text.rfind("\n", start + MAX_CHUNK_CHARS - 5000, end)
        if split_at == -1:
            split_at = end
        chunks.append(text[start:split_at])
        start = split_at - OVERLAP_CHARS
    logger.info("  Split %d chars into %d chunks: %s",
                len(text), len(chunks), [len(c) for c in chunks])
    return chunks


def _merge_step_results(results_list: list[dict], key: str) -> dict:
    """Merge results from multiple chunks by experiment_id."""
    if len(results_list) == 1:
        return results_list[0]
    # Merge arrays by experiment_id, deduplicating
    merged = {}
    for result in results_list:
        for exp in result.get(key, []):
            eid = exp.get("experiment_id", "unknown")
            if eid not in merged:
                merged[eid] = exp
            else:
                # Merge arrays within the experiment
                existing = merged[eid]
                for arr_key in ["results", "classical_baselines", "speedup_claims", "scalability_data"]:
                    existing_items = existing.get(arr_key, [])
                    new_items = exp.get(arr_key, [])
                    # Deduplicate by string representation
                    seen = {json.dumps(i, sort_keys=True, default=str) for i in existing_items}
                    for item in new_items:
                        s = json.dumps(item, sort_keys=True, default=str)
                        if s not in seen:
                            existing_items.append(item)
                            seen.add(s)
                    existing[arr_key] = existing_items
                # For dict fields, prefer non-null values
                for dict_key in ["quantum_resources", "hardware", "noise_model",
                                 "complexity_analysis", "convergence_data"]:
                    if not existing.get(dict_key) and exp.get(dict_key):
                        existing[dict_key] = exp[dict_key]
    return {key: list(merged.values())}


# ── Paper Processing ──────────────────────────────────────────────────────

def process_paper(client: LLMClient, entry: dict, config: dict,
                  silo_metrics: dict, dry_run: bool = False,
                  skip_step4: bool = False) -> dict | None:
    """Run the 3-step pipeline on a single paper, with chunking for large papers.
    
    Step 2: Experiments + resources + hardware + complexity (gpt-5.1)
    Step 3: Silo-specific results + baselines + speedups (gpt-5.1)
    Step 4: QA + Hoefler advantage assessment (gpt-5.2)
    """
    paper_id = entry["paper_id"]
    full_text = Path(entry["text_path"]).read_text("utf-8", errors="replace")

    if dry_run:
        logger.info("[DRY] %s: %dk chars, silo=%s",
                    paper_id, len(full_text) // 1000, entry["primary_silo"])
        return None

    # Step 2 runs on truncated text (experiment identification doesn't need full text)
    text_for_step2 = truncate_tokens(full_text, config.get("input_token_limit", 60000))

    try:
        # Step 2: Experiment identification
        step2 = run_step2(client, text_for_step2, entry, config)
        n_exps = len(step2.get("experiments", []))
        logger.info("  %s step2: %d experiments", paper_id, n_exps)

        if n_exps == 0:
            meta = entry.get("p2_metadata", {})
            result = {
                "paper_id": paper_id,
                "extraction_metadata": {
                    "extraction_date": date.today().isoformat(),
                    "run_timestamp": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                    "schema_version": "benchmark_extraction_v1.0",
                    "prompt_version_hash": get_prompt_version_hash(),
                    "scope": config.get("scope", "gate_based"),
                    "models_used": config.get("step_models", {}),
                    "source_file": Path(entry["text_path"]).name,
                    "pipeline": "3-step-v3",
                    "notes": "step2 returned 0 experiments",
                },
                "paper_metadata": {
                    "title": meta.get("title", "") or f"(no title; paper_id={paper_id})",
                    "authors": meta.get("authors", []),
                    "year": meta.get("year"),
                    "doi": meta.get("doi"),
                    "scope": "gate_based",
                },
                "finance_domain": {
                    "primary_silo": entry["primary_silo"],
                    "secondary_silos": entry.get("secondary_silos", []),
                },
                "has_quantitative_results": False,
                "experiments": [],
                "summary": "No distinct quantum experiments identified.",
            }
            _validate_and_score(result)
            _save_result(result)
            return result

        # Chunk large papers for steps 3-4
        chunks = chunk_text(full_text)
        is_chunked = len(chunks) > 1
        if is_chunked:
            logger.info("  %s: large paper, %d chunks for steps 3-4", paper_id, len(chunks))

        # Step 3: Silo-specific results (per chunk if large)
        step3_parts = []
        for ci, chunk in enumerate(chunks):
            chunk_text_truncated = truncate_tokens(chunk, config.get("input_token_limit", 60000))
            label = f" chunk {ci+1}/{len(chunks)}" if is_chunked else ""
            s3 = run_step3(client, chunk_text_truncated, step2, entry, config, silo_metrics)
            logger.info("  %s step3%s: silo=%s OK", paper_id, label, entry["primary_silo"])
            step3_parts.append(s3)
        step3 = _merge_step_results(step3_parts, "experiment_results") if is_chunked else step3_parts[0]

        # Step 4: Verification + Hoefler (reasoning model reads paper + extracted data)
        if skip_step4:
            logger.info("  %s step4: SKIPPED (--skip-step4)", paper_id)
            step4 = {"experiment_assessments": [], "corrections": [], "missed_experiments": [],
                      "extraction_confidence": None, "summary": ""}
        else:
            pre_merged = {"experiments": step2.get("experiments", []),
                          "results": step3}
            text_for_step4 = truncate_tokens(full_text, config.get("input_token_limit", 60000))
            step4 = run_step4(client, text_for_step4, pre_merged, entry, config)
            logger.info("  %s step4: confidence=%.2f, corrections=%d",
                        paper_id, step4.get("extraction_confidence", 0),
                        len(step4.get("corrections", [])))

        # Full merge
        result = merge_steps(step2, step3, step4, entry, config)
        _validate_and_score(result)
        _save_result(result)
        return result

    except json.JSONDecodeError as e:
        logger.warning("  %s: JSON parse failed at some step: %s", paper_id, str(e)[:100])
        return None
    except Exception as e:
        logger.error("  %s: %s", paper_id, str(e)[:200])
        return None


def _validate_and_score(data: dict) -> None:
    """Normalize, validate, and score an extraction result in-place.

    Mirrors the validation logic from extract_benchmarks.py so that the
    live 3-step pipeline enforces the same quality gates.
    """
    paper_id = data.get("paper_id", "unknown")

    # Ensure extraction_metadata exists
    if "extraction_metadata" not in data:
        data["extraction_metadata"] = {}

    # Normalize metric names to canonical forms
    normalize_extraction_metrics(data)

    # Validate against schema + range checks
    errors, warnings = validate_extraction(data)
    data["extraction_metadata"]["validation_errors"] = len(errors)
    data["extraction_metadata"]["validation_warnings"] = len(warnings)
    data["extraction_metadata"]["validation_passed"] = len(errors) == 0
    if errors:
        data["extraction_metadata"]["validation_error_details"] = errors
    if warnings:
        data["extraction_metadata"]["validation_warning_details"] = warnings

    # Compute quality score
    quality = compute_quality_score(data)
    data["extraction_metadata"]["quality_score"] = quality["score"]
    data["extraction_metadata"]["quality_details"] = quality

    if errors:
        logger.warning("  %s: %d validation errors: %s",
                        paper_id, len(errors), "; ".join(errors[:3]))
    if warnings:
        logger.info("  %s: %d validation warnings", paper_id, len(warnings))


def _save_result(data: dict) -> None:
    """Save extraction result to output directory."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    path = OUTPUT_DIR / f"{data['paper_id']}.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False, default=str)


def is_completed(paper_id: str) -> bool:
    """Check if paper has already been extracted."""
    path = OUTPUT_DIR / f"{paper_id}.json"
    return path.exists() and path.stat().st_size > 500


# ── Main ──────────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(
        description="P3 Quantitative Extraction — 5-step cached-prefix pipeline",
    )
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--paper-id", dest="paper_id")
    parser.add_argument("--silo", help="Run only papers in this silo (e.g., portfolio-optimization)")
    parser.add_argument("--list-silos", action="store_true", help="Show silo paper counts and exit")
    parser.add_argument("--manifest", help="Path to work_manifest.json")
    parser.add_argument("--limit", type=int)
    parser.add_argument("--parallel", type=int, default=1)
    parser.add_argument("--skip-completed", action="store_true", default=True,
                        dest="skip_completed")
    parser.add_argument("--no-skip-completed", action="store_false",
                        dest="skip_completed")
    parser.add_argument("--skip-step4", action="store_true",
                        help="Run only steps 2-3 (extraction). Skip step 4 (verification/Hoefler).")
    args = parser.parse_args()

    config = load_config()
    silo_metrics = load_silo_metrics()

    # Build or load manifest
    if args.manifest:
        with open(args.manifest, encoding="utf-8") as f:
            manifest = json.load(f)
    else:
        logger.info("Building work manifest from P2 outputs...")
        manifest = build_work_manifest()
        logger.info("Manifest: %d papers with quantitative results", len(manifest))

    # List silos mode
    if args.list_silos:
        silo_counts: dict[str, int] = {}
        for entry in manifest:
            s = entry["primary_silo"]
            silo_counts[s] = silo_counts.get(s, 0) + 1
        print(f"\n{'Silo':<30} {'Papers':>7}  {'PD Code':<8}")
        print("-" * 50)
        sm = load_silo_metrics()
        for silo, count in sorted(silo_counts.items(), key=lambda x: -x[1]):
            code = sm.get(silo, {}).get("code", "")
            print(f"{silo:<30} {count:>7}  {code:<8}")
        print(f"{'TOTAL':<30} {len(manifest):>7}")
        return

    # Filter by paper ID
    if args.paper_id:
        manifest = [e for e in manifest if e["paper_id"] == args.paper_id]
        if not manifest:
            logger.error("Paper %s not found in manifest", args.paper_id)
            sys.exit(1)

    # Filter by silo
    if args.silo:
        manifest = [e for e in manifest if e["primary_silo"] == args.silo]
        if not manifest:
            logger.error("No papers found for silo '%s'", args.silo)
            valid = sorted(set(e["primary_silo"] for e in build_work_manifest()))
            logger.info("Available silos: %s", ", ".join(valid))
            sys.exit(1)
        logger.info("Silo filter: %s — %d papers", args.silo, len(manifest))

    if args.limit:
        manifest = manifest[:args.limit]

    # Skip completed
    skipped = 0
    if args.skip_completed:
        filtered = []
        for entry in manifest:
            if is_completed(entry["paper_id"]):
                skipped += 1
            else:
                filtered.append(entry)
        manifest = filtered

    logger.info("Pipeline: %d papers to process, %d skipped | model=%s | parallel=%d",
                len(manifest), skipped, config["model"], args.parallel)

    if not manifest:
        logger.info("Nothing to do.")
        return

    # Silo distribution
    silo_counts: dict[str, int] = {}
    for entry in manifest:
        s = entry["primary_silo"]
        silo_counts[s] = silo_counts.get(s, 0) + 1
    for silo, count in sorted(silo_counts.items(), key=lambda x: -x[1]):
        logger.info("  %s: %d papers", silo, count)

    # Process
    client = LLMClient()
    processed = 0
    failed = 0
    t_start = time.time()
    _lock = threading.Lock()

    def _process_one(idx_entry):
        nonlocal processed, failed
        idx, entry = idx_entry
        pid = entry["paper_id"]
        logger.info("[%d/%d] %s (silo=%s)", idx + 1, len(manifest), pid, entry["primary_silo"])

        result = process_paper(client, entry, config, silo_metrics, args.dry_run,
                               skip_step4=args.skip_step4)

        with _lock:
            if args.dry_run:
                processed += 1
            elif result is not None:
                processed += 1
            else:
                failed += 1

    if args.parallel > 1 and not args.dry_run:
        with ThreadPoolExecutor(max_workers=args.parallel) as pool:
            futures = [pool.submit(_process_one, (i, e)) for i, e in enumerate(manifest)]
            for f in as_completed(futures):
                try:
                    f.result()
                except Exception as exc:
                    logger.error("Thread error: %s", exc)
                    with _lock:
                        failed += 1
    else:
        for i, entry in enumerate(manifest):
            _process_one((i, entry))

    elapsed = time.time() - t_start
    logger.info("Done: %d processed, %d failed, %.1f min elapsed",
                processed, failed, elapsed / 60)


if __name__ == "__main__":
    main()
