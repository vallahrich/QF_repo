"""B1/B2 orchestration helpers — prep, validate, log.

Design:
- `build_evidence_block(pid, silo, idx)` → multi-line string for one paper.
- `render_b1_prompt(silo, batch_id, paper_ids, idx)` → (rendered_prompt, metadata).
- `validate_b1(response, paper_ids, silo_code, batch_id)` → (ok, errors, parsed).
- `persist_b1(...)` → atomic write + manifest.jsonl + calls.jsonl log.
- Similar for B2.

This module is pure — no LLM calls. Actual Opus invocation is done by the
main agent via the `task` tool, then the response is passed back here for
validation and persistence.

No secrets. All writes are within p3_thematic_synthesis/.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
P3_ROOT = HERE.parent
CODING_DIR = P3_ROOT / "s4_thematic_coding"
PROMPTS_DIR = P3_ROOT / "prompts"
LOGS_DIR = P3_ROOT.parent / "logs"

SILO_CODES = {
    "credit_lending":         "CL",
    "derivative_pricing":     "DP",
    "fraud_detection":        "FD",
    "portfolio_optimization": "PO",
    "quantum_ml_finance":     "QML",
    "risk_management":        "RM",
    "simulation_monte_carlo": "SMC",
    "trading_execution":      "TE",
}

SILO_LABELS = {
    "credit_lending":         "Credit & Lending",
    "derivative_pricing":     "Derivative Pricing",
    "fraud_detection":        "Fraud Detection",
    "portfolio_optimization": "Portfolio Optimization",
    "quantum_ml_finance":     "Quantum ML in Finance",
    "risk_management":        "Risk Management",
    "simulation_monte_carlo": "Simulation & Monte Carlo",
    "trading_execution":      "Trading & Execution",
}

B1_PROMPT_FILE = "b1_descriptive_themes_v1.txt"
B2_PROMPT_FILE = "b2_analytical_themes_v1.txt"


# ──────────────────────────────────────────────────────────────────────
# I/O helpers
# ──────────────────────────────────────────────────────────────────────

def _load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def _load_jsonl(path: Path) -> list[dict]:
    out = []
    with path.open("r", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line:
                out.append(json.loads(line))
    return out


def _atomic_write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    with tmp.open("w", encoding="utf-8") as fh:
        json.dump(data, fh, ensure_ascii=False, indent=2)
    tmp.replace(path)


def _append_jsonl(path: Path, entry: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(entry, ensure_ascii=False) + "\n")


def _sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def load_prompt(name: str) -> str:
    return (PROMPTS_DIR / name).read_text(encoding="utf-8")


def load_index(silo: str) -> dict:
    return _load_json(CODING_DIR / silo / "themes" / "code_memo_index.json")


# ──────────────────────────────────────────────────────────────────────
# Evidence block assembly
# ──────────────────────────────────────────────────────────────────────

def _central_memo_block(memo: dict) -> str:
    """Render the 9-dimension central memo as labelled dimensions."""
    lines: list[str] = []
    dim_keys = sorted(
        (k for k in memo.keys() if k.startswith("dimension_")),
        key=lambda k: int(k.split("_", 2)[1]),
    )
    for key in dim_keys:
        val = memo.get(key) or {}
        if not isinstance(val, dict):
            continue
        text = (val.get("text") or "").strip()
        codes = val.get("support_codes") or []
        # Short dimension label from the key: "dimension_1_problem_framing" -> "DIM_1 PROBLEM_FRAMING"
        parts = key.split("_", 2)
        dim_label = f"DIM_{parts[1]} {parts[2].upper()}" if len(parts) >= 3 else key.upper()
        code_str = ", ".join(codes) if codes else "—"
        lines.append(f"  {dim_label}: {text}")
        lines.append(f"    [codes: {code_str}]")
    return "\n".join(lines)


def _overlay_block(overlay: dict) -> str:
    """Render the silo overlay (silo_relevance + key_points)."""
    lines: list[str] = []
    rel = (overlay.get("silo_relevance") or "").strip()
    if rel:
        lines.append(f"  SILO_RELEVANCE: {rel}")
    score = overlay.get("silo_relevance_score")
    if score is not None:
        lines.append(f"    [silo_relevance_score: {score}]")
    kps = overlay.get("key_points") or []
    for i, kp in enumerate(kps, 1):
        pt = (kp.get("point") or "").strip()
        codes = kp.get("support_codes") or []
        dim_source = kp.get("dimension_source") or "—"
        code_str = ", ".join(codes) if codes else "—"
        lines.append(f"  KEY_POINT {i}: {pt}")
        lines.append(f"    [codes: {code_str}  dim_source: {dim_source}]")
    prim = overlay.get("primary_codes") or []
    if prim:
        lines.append(f"  PRIMARY_CODES: {', '.join(prim)}")
    return "\n".join(lines)


def build_evidence_block(paper_id: str, silo: str) -> str:
    """Assemble the paper's evidence block for B1 input.

    Single-silo paper → central A2 memo (type: central).
    Multi-silo paper  → central memo + silo overlay (type: central+overlay).
    """
    central_path = CODING_DIR / "papers" / f"{paper_id}.json"
    central = _load_json(central_path) if central_path.is_file() else None

    silo_memo_path = CODING_DIR / silo / "memos" / f"{paper_id}.json"
    silo_memo = _load_json(silo_memo_path) if silo_memo_path.is_file() else None

    is_overlay = bool(silo_memo) and "silo_relevance" in silo_memo and "key_points" in silo_memo
    block_type = "central+overlay" if is_overlay else "central"

    parts = [f"=== PAPER {paper_id} (type: {block_type}) ==="]
    if central:
        parts.append("[CENTRAL MEMO]")
        parts.append(_central_memo_block(central))
    elif silo_memo and not is_overlay:
        # Fan-out copy — treat as central
        parts.append("[CENTRAL MEMO]")
        parts.append(_central_memo_block(silo_memo))
    if is_overlay and silo_memo:
        parts.append("[SILO OVERLAY]")
        parts.append(_overlay_block(silo_memo))

    return "\n".join(parts).rstrip()


# ──────────────────────────────────────────────────────────────────────
# Batch partitioning
# ──────────────────────────────────────────────────────────────────────

def _stratified_by_year(paper_ids: list[str], pub_years: dict[str, int | None]) -> list[str]:
    """Interleave papers by year ascending, round-robin.

    If a paper has no year, bucket it as 'unknown' (placed last per round).
    Stable within-year order: sorted by paper_id.
    """
    # Bucket by year; sort bucket keys ascending (None last)
    buckets: dict[Any, list[str]] = {}
    for pid in paper_ids:
        y = pub_years.get(pid)
        buckets.setdefault(y, []).append(pid)
    for v in buckets.values():
        v.sort()
    ordered_years = sorted((y for y in buckets.keys() if y is not None))
    if None in buckets:
        ordered_years.append(None)

    # Round-robin across years
    out: list[str] = []
    bucket_lists = [list(buckets[y]) for y in ordered_years]
    while any(bucket_lists):
        for blist in bucket_lists:
            if blist:
                out.append(blist.pop(0))
    return out


def compute_batches(silo: str, papers_per_batch: int = 260) -> list[dict]:
    """Return list of batches [{batch_id, paper_ids}, ...].

    Default 260: Opus 4.6 has 200K token context; each evidence block is
    ~2-4K tokens; 260 papers ≈ 600-800K tokens. For 1M-context variant,
    headroom is ample. For 200K-context, a silo larger than ~80 papers
    would not fit — but none of our silos exceed 313, and Opus 4.6 via
    Copilot sub-agent uses the 1M variant for long contexts.
    """
    index = load_index(silo)
    paper_ids = sorted(index["papers"].keys())  # deterministic
    n = len(paper_ids)
    if n == 0:
        return []
    # Batch count
    n_batches = max(1, (n + papers_per_batch - 1) // papers_per_batch)
    if n_batches == 1:
        return [{"batch_id": 1, "paper_ids": paper_ids}]
    # Stratify by year when splitting
    pub_years: dict[str, int | None] = {}
    for pid in paper_ids:
        # year is not in the index; try loading from central memo's frontmatter isn't there either
        # For now: extract from A1 codes first locator or None; placeholder
        pub_years[pid] = None
    ordered = _stratified_by_year(paper_ids, pub_years)
    # Round-robin assign to n_batches
    bucketed: list[list[str]] = [[] for _ in range(n_batches)]
    for i, pid in enumerate(ordered):
        bucketed[i % n_batches].append(pid)
    return [{"batch_id": i + 1, "paper_ids": sorted(b)} for i, b in enumerate(bucketed)]


# ──────────────────────────────────────────────────────────────────────
# Prompt rendering
# ──────────────────────────────────────────────────────────────────────

def render_b1_prompt(
    silo: str,
    batch_id: int,
    paper_ids: list[str],
    total_batches: int,
    min_papers_per_theme: int = 3,
) -> tuple[str, dict]:
    template = load_prompt(B1_PROMPT_FILE)
    silo_code = SILO_CODES[silo]
    silo_name = SILO_LABELS[silo]
    blocks = [build_evidence_block(pid, silo) for pid in paper_ids]
    batch_memos = "\n\n".join(blocks)
    rendered = template.format(
        silo_name=silo_name,
        silo_code=silo_code,
        batch_id=str(batch_id),
        batch_id_2d=f"{batch_id:02d}",
        total_batches=total_batches,
        batch_size=len(paper_ids),
        min_papers_per_theme=min_papers_per_theme,
        batch_memos=batch_memos,
    )
    meta = {
        "silo": silo,
        "silo_code": silo_code,
        "batch_id": batch_id,
        "paper_ids": paper_ids,
        "batch_size": len(paper_ids),
        "prompt_file": B1_PROMPT_FILE,
        "prompt_sha256": _sha256(template),
        "rendered_sha256": _sha256(rendered),
        "min_papers_per_theme": min_papers_per_theme,
    }
    return rendered, meta


def render_b2_prompt(silo: str, b1_aggregate: dict, max_analytical: int) -> tuple[str, dict]:
    template = load_prompt(B2_PROMPT_FILE)
    silo_code = SILO_CODES[silo]
    silo_name = SILO_LABELS[silo]
    rendered = template.format(
        silo_name=silo_name,
        silo_code=silo_code,
        silo_paper_count=b1_aggregate["silo_paper_count"],
        max_analytical_themes=max_analytical,
        all_descriptive_themes=json.dumps(b1_aggregate["themes"], ensure_ascii=False, indent=2),
    )
    meta = {
        "silo": silo,
        "silo_code": silo_code,
        "prompt_file": B2_PROMPT_FILE,
        "prompt_sha256": _sha256(template),
        "rendered_sha256": _sha256(rendered),
        "max_analytical_themes": max_analytical,
        "b1_theme_count": len(b1_aggregate["themes"]),
    }
    return rendered, meta


# ──────────────────────────────────────────────────────────────────────
# Response parsing
# ──────────────────────────────────────────────────────────────────────

def extract_json(raw: str) -> Any:
    """Robust JSON extraction: strip markdown fences and leading prose."""
    s = raw.strip()
    # Strip ```json ... ``` fences
    fence = re.match(r"^```(?:json)?\s*(.*?)\s*```\s*$", s, re.DOTALL)
    if fence:
        s = fence.group(1).strip()
    # If still has prose, find first [ or {
    first_obj = s.find("{")
    first_arr = s.find("[")
    candidates = [x for x in (first_obj, first_arr) if x >= 0]
    if not candidates:
        raise ValueError("No JSON object or array found in response")
    start = min(candidates)
    s = s[start:]
    return json.loads(s)


# ──────────────────────────────────────────────────────────────────────
# L-B1 validation
# ──────────────────────────────────────────────────────────────────────

def _valid_a1_code_ids(silo: str, paper_id: str, index: dict) -> set[str]:
    p = index["papers"].get(paper_id, {})
    return {c["code_id"] for c in (p.get("codes") or []) if c.get("code_id")}


def validate_b1(parsed: Any, paper_ids: list[str], silo_code: str, batch_id: int,
                min_papers_per_theme: int, index: dict, silo: str) -> tuple[bool, list[str]]:
    errors: list[str] = []
    if not isinstance(parsed, list):
        return False, ["Top-level output must be a JSON array of themes."]
    if not parsed:
        return False, ["Empty theme array."]

    batch_set = set(paper_ids)
    id_pattern = re.compile(rf"^DT-{re.escape(silo_code)}-B{batch_id:02d}-\d{{3}}$")
    seen_ids: set[str] = set()

    for i, theme in enumerate(parsed):
        tag = f"theme[{i}]"
        if not isinstance(theme, dict):
            errors.append(f"{tag}: not an object")
            continue
        for field in ("theme_id", "theme_label", "description", "supporting_papers", "support_code_ids", "evidence_summary"):
            if field not in theme:
                errors.append(f"{tag}: missing field '{field}'")

        tid = theme.get("theme_id")
        if tid:
            if not id_pattern.match(tid):
                errors.append(f"{tag}: theme_id '{tid}' does not match DT-{silo_code}-B{batch_id:02d}-NNN")
            if tid in seen_ids:
                errors.append(f"{tag}: duplicate theme_id '{tid}'")
            seen_ids.add(tid)

        sp = theme.get("supporting_papers") or []
        if not isinstance(sp, list) or len(sp) < min_papers_per_theme:
            errors.append(f"{tag}: supporting_papers must be a list of ≥ {min_papers_per_theme} papers (got {len(sp) if isinstance(sp, list) else 'not-list'})")
        for pid in sp or []:
            if pid not in batch_set:
                errors.append(f"{tag}: supporting paper '{pid}' not in this batch")

        scids = theme.get("support_code_ids") or {}
        if not isinstance(scids, dict):
            errors.append(f"{tag}: support_code_ids must be an object keyed by paper_id")
        else:
            for pid in sp or []:
                if pid not in scids or not scids[pid]:
                    errors.append(f"{tag}: support_code_ids missing entry for supporting paper '{pid}'")
                    continue
                valid_codes = _valid_a1_code_ids(silo, pid, index)
                # overlay primary_codes should also be valid codes from A1 jsonl (they should reuse same IDs)
                for cid in scids[pid]:
                    if cid not in valid_codes:
                        errors.append(f"{tag}: support_code_id '{cid}' not found in A1 codes for paper '{pid}'")

    ok = len(errors) == 0
    return ok, errors


def validate_b2(parsed: Any, silo: str, silo_paper_ids: set[str],
                valid_b1_theme_ids: set[str], max_analytical: int) -> tuple[bool, list[str]]:
    errors: list[str] = []
    if not isinstance(parsed, dict):
        return False, ["Top-level output must be a JSON object."]
    silo_code = SILO_CODES[silo]

    d_themes = parsed.get("descriptive_themes")
    a_themes = parsed.get("analytical_themes")
    if not isinstance(d_themes, list) or not d_themes:
        errors.append("descriptive_themes must be a non-empty array")
    if not isinstance(a_themes, list):
        errors.append("analytical_themes must be an array")
        return False, errors
    if not (4 <= len(a_themes) <= max_analytical):
        errors.append(f"analytical_themes count {len(a_themes)} outside allowed range [4, {max_analytical}]")

    merged_d_ids: set[str] = set()
    d_paper_union: dict[str, set[str]] = {}

    d_id_pattern = re.compile(rf"^DT-{re.escape(silo_code)}-\d{{3}}$")
    a_id_pattern = re.compile(rf"^AT-{re.escape(silo_code)}-\d{{3}}$")

    for i, t in enumerate(d_themes or []):
        tag = f"descriptive_themes[{i}]"
        if not isinstance(t, dict):
            errors.append(f"{tag}: not an object")
            continue
        tid = t.get("theme_id")
        if not tid or not d_id_pattern.match(tid):
            errors.append(f"{tag}: theme_id '{tid}' does not match DT-{silo_code}-NNN")
        else:
            merged_d_ids.add(tid)
            sp = t.get("supporting_papers") or []
            d_paper_union[tid] = set(sp)
        for field in ("theme_label", "description", "supporting_papers", "merged_from"):
            if field not in t:
                errors.append(f"{tag}: missing field '{field}'")
        for mf in t.get("merged_from") or []:
            if mf not in valid_b1_theme_ids:
                errors.append(f"{tag}: merged_from '{mf}' not in B1 inputs")
        for pid in t.get("supporting_papers") or []:
            if pid not in silo_paper_ids:
                errors.append(f"{tag}: supporting paper '{pid}' not in silo scope")

    for i, t in enumerate(a_themes):
        tag = f"analytical_themes[{i}]"
        if not isinstance(t, dict):
            errors.append(f"{tag}: not an object")
            continue
        tid = t.get("theme_id")
        if not tid or not a_id_pattern.match(tid):
            errors.append(f"{tag}: theme_id '{tid}' does not match AT-{silo_code}-NNN")
        for field in ("theme_label", "interpretation", "grounded_in", "supporting_papers", "implication"):
            if field not in t:
                errors.append(f"{tag}: missing field '{field}'")
        gi = t.get("grounded_in") or []
        if not gi:
            errors.append(f"{tag}: grounded_in is empty")
        grounded_papers: set[str] = set()
        for did in gi:
            if did not in merged_d_ids:
                errors.append(f"{tag}: grounded_in '{did}' not a merged descriptive theme in this output")
            else:
                grounded_papers |= d_paper_union.get(did, set())
        for pid in t.get("supporting_papers") or []:
            if pid not in silo_paper_ids:
                errors.append(f"{tag}: supporting paper '{pid}' not in silo scope")
            elif grounded_papers and pid not in grounded_papers:
                errors.append(f"{tag}: supporting paper '{pid}' not in union of grounded descriptive themes' papers")
        # Counter-evidence
        ce = t.get("counter_evidence")
        ncer = t.get("no_counter_evidence_reason")
        if (not ce) and (not ncer):
            errors.append(f"{tag}: must have either counter_evidence entries OR no_counter_evidence_reason")
        if ce:
            if not isinstance(ce, list):
                errors.append(f"{tag}: counter_evidence must be an array")
            else:
                for j, entry in enumerate(ce):
                    etag = f"{tag}.counter_evidence[{j}]"
                    if not isinstance(entry, dict):
                        errors.append(f"{etag}: not an object")
                        continue
                    pid = entry.get("paper_id")
                    if not pid:
                        errors.append(f"{etag}: missing paper_id")
                    elif pid not in silo_paper_ids:
                        errors.append(f"{etag}: paper_id '{pid}' not in silo scope (possible hallucination)")
                    if not entry.get("reason"):
                        errors.append(f"{etag}: missing reason")
                    etype = entry.get("evidence_type")
                    if etype not in {"opposing_claim", "boundary_condition", "null_result", "methodological_critique"}:
                        errors.append(f"{etag}: invalid evidence_type '{etype}'")

    ok = len(errors) == 0
    return ok, errors


# ──────────────────────────────────────────────────────────────────────
# Persistence + logging
# ──────────────────────────────────────────────────────────────────────

def log_call(stage: str, meta: dict, rendered_prompt: str, raw_response: str,
             model: str, output_path: str, validation_status: str,
             retry_count: int = 0) -> None:
    """Full-content LLM call log (CBS Pillar 3)."""
    entry = {
        "timestamp": _now_iso(),
        "stage": stage,
        "model": model,
        "silo": meta.get("silo"),
        "batch_id": meta.get("batch_id"),
        "prompt_file": meta.get("prompt_file"),
        "prompt_sha256": meta.get("prompt_sha256"),
        "rendered_sha256": meta.get("rendered_sha256"),
        "input_paper_ids": meta.get("paper_ids"),
        "retry_count": retry_count,
        "rendered_prompt": rendered_prompt,
        "raw_response": raw_response,
        "output_path": output_path,
        "validation_status": validation_status,
    }
    _append_jsonl(LOGS_DIR / f"{stage}_calls.jsonl", entry)


def persist_b1(silo: str, batch_id: int, parsed: list, meta: dict,
               rendered_prompt: str, raw_response: str, model: str,
               validation_status: str, retry_count: int = 0) -> Path:
    themes_dir = CODING_DIR / silo / "themes"
    out_path = themes_dir / f"b1_batch_{batch_id:02d}.json"
    payload = {
        "silo": silo,
        "batch_id": batch_id,
        "generated_at": _now_iso(),
        "model": model,
        "prompt_file": meta["prompt_file"],
        "prompt_sha256": meta["prompt_sha256"],
        "rendered_sha256": meta["rendered_sha256"],
        "paper_ids": meta["paper_ids"],
        "themes": parsed,
    }
    _atomic_write_json(out_path, payload)
    _append_jsonl(themes_dir / "b1_manifest.jsonl", {
        "batch_id": batch_id,
        "generated_at": _now_iso(),
        "model": model,
        "prompt_sha256": meta["prompt_sha256"],
        "paper_count": len(meta["paper_ids"]),
        "theme_count": len(parsed),
        "output_path": str(out_path.relative_to(P3_ROOT.parent)),
        "validation_status": validation_status,
    })
    log_call("b1", meta, rendered_prompt, raw_response, model, str(out_path), validation_status, retry_count)
    return out_path


def persist_b2(silo: str, parsed: dict, meta: dict,
               rendered_prompt: str, raw_response: str, model: str,
               validation_status: str, retry_count: int = 0) -> Path:
    themes_dir = CODING_DIR / silo / "themes"
    out_path = themes_dir / "b2_silo_themes.json"
    payload = {
        "silo": silo,
        "generated_at": _now_iso(),
        "model": model,
        "prompt_file": meta["prompt_file"],
        "prompt_sha256": meta["prompt_sha256"],
        "rendered_sha256": meta["rendered_sha256"],
        "b1_theme_count": meta["b1_theme_count"],
        "max_analytical_themes": meta["max_analytical_themes"],
        "output": parsed,
    }
    _atomic_write_json(out_path, payload)
    _append_jsonl(themes_dir / "b2_manifest.jsonl", {
        "generated_at": _now_iso(),
        "model": model,
        "prompt_sha256": meta["prompt_sha256"],
        "descriptive_theme_count": len(parsed.get("descriptive_themes") or []),
        "analytical_theme_count": len(parsed.get("analytical_themes") or []),
        "output_path": str(out_path.relative_to(P3_ROOT.parent)),
        "validation_status": validation_status,
    })
    log_call("b2", meta, rendered_prompt, raw_response, model, str(out_path), validation_status, retry_count)
    return out_path


def aggregate_b1(silo: str) -> dict:
    """Load all b1_batch_*.json for a silo and return the aggregate B1 input for B2."""
    themes_dir = CODING_DIR / silo / "themes"
    all_themes: list[dict] = []
    paper_set: set[str] = set()
    for p in sorted(themes_dir.glob("b1_batch_*.json")):
        # Only accept exact b1_batch_NN.json files, not b1_batch_NN.meta.json or .sanitize_log.json
        if not re.fullmatch(r"b1_batch_\d+\.json", p.name):
            continue
        payload = _load_json(p)
        all_themes.extend(payload["themes"])
        paper_set.update(payload["paper_ids"])
    # Also read the projection manifest for total papers in scope
    proj = _load_json(CODING_DIR / silo / "projection_manifest.json")
    return {
        "silo": silo,
        "silo_paper_count": proj["total_papers"],
        "silo_paper_ids": sorted({p["paper_id"] for p in proj["papers"]}),
        "themes": all_themes,
    }


def size_sensitive_cap(descriptive_count: int) -> int:
    """max_analytical = min(12, max(4, ceil(descriptive_count / 3)))."""
    import math
    return min(12, max(4, math.ceil(descriptive_count / 3)))
