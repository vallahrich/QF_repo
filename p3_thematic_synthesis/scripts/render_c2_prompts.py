"""Render per-silo C2 grounding-check prompts.

For each of the 8 silos:
  - load b2_silo_themes.json, extract analytical themes (trim to essentials)
  - for each analytical theme, collect supporting_papers (capped at 8 per theme
    to bound payload; sampled deterministically)
  - load A1 memos for the union of supporting papers across all themes
  - render prompt from c2_grounding_check_v1.txt template
  - write to s4_thematic_coding/<silo>/themes/c2_grounding_check.prompt.txt
"""
import hashlib
import json
from pathlib import Path
from datetime import datetime, timezone
import random

ROOT = Path(__file__).resolve().parents[1]
SILOS = [
    ("trading_execution", "TE"),
    ("credit_lending", "CL"),
    ("fraud_detection", "FD"),
    ("derivative_pricing", "DP"),
    ("risk_management", "RM"),
    ("simulation_monte_carlo", "SMC"),
    ("portfolio_optimization", "PO"),
    ("quantum_ml_finance", "QML"),
]
PAPERS_PER_THEME_CAP = 8  # Deterministic sample cap to bound payload.


def sample_papers(paper_ids: list[str], cap: int, seed: str) -> list[str]:
    if len(paper_ids) <= cap:
        return sorted(paper_ids)
    rng = random.Random(seed)
    sample = sorted(rng.sample(paper_ids, cap))
    return sample


def trim_memo(memo: dict) -> dict:
    """Keep only fields useful for grounding check.

    Two memo schemas exist in the wild:
    1. Silo-overlaid: first-class `key_points[]` array of {point, support_codes,
       dimension_source, silo_note}. Preferred path.
    2. Raw 8-dimension A1: content lives under `dimension_{1..8}_*` keys with
       sub-fields {text, support_codes, support_type}. Fall back to these when
       `key_points` is absent or empty so the verifier is not starved.
    """
    kp = memo.get("key_points") or []
    trimmed_kps = []
    for p in kp:
        trimmed_kps.append({
            "point": p.get("point"),
            "silo_note": p.get("silo_note"),
            "dimension": p.get("dimension_source"),
        })
    out = {
        "paper_id": memo.get("paper_id"),
        "silo_relevance": memo.get("silo_relevance"),
        "silo_relevance_score": memo.get("silo_relevance_score"),
    }
    if trimmed_kps:
        out["key_points"] = trimmed_kps
        return out

    # Fallback: 8-dimension schema. Expose the dimension text directly so the
    # verifier can ground or refute claims. Dimensions are labelled explicitly
    # so GPT-5.4 can cite them verbatim in the reason field.
    DIM_LABELS = {
        "dimension_1_problem_framing": "problem_framing",
        "dimension_2_quantum_method": "quantum_method",
        "dimension_3_key_results": "key_results",
        "dimension_4_classical_comparison": "classical_comparison",
        "dimension_5_stated_limitations": "stated_limitations",
        "dimension_6_future_work": "future_work",
        "dimension_7_novelty_claim": "novelty_claim",
        "dimension_8_methodological_notes": "methodological_notes",
        "dimension_9_miscellaneous": "miscellaneous",
    }
    dims = {}
    for key, label in DIM_LABELS.items():
        v = memo.get(key)
        if isinstance(v, dict) and v.get("text"):
            dims[label] = v["text"]
        elif isinstance(v, str) and v:
            dims[label] = v
    if dims:
        out["dimension_texts"] = dims
        out["_schema"] = "raw_8_dimension_fallback"
    else:
        out["_schema"] = "empty"
    return out


def render_for_silo(silo_name: str, silo_code: str) -> dict:
    silo_dir = ROOT / "s4_thematic_coding" / silo_name
    b2 = json.loads((silo_dir / "themes" / "b2_silo_themes.json").read_text(encoding="utf-8"))
    ats = b2["output"].get("analytical_themes", [])

    # Trim analytical themes to grounding-relevant fields + sample supporting papers
    trimmed_ats = []
    papers_needed = set()
    for at in ats:
        sup_all = at.get("supporting_papers", [])
        sup = sample_papers(sup_all, PAPERS_PER_THEME_CAP, seed=at["theme_id"])
        papers_needed.update(sup)
        trimmed_ats.append({
            "theme_id": at["theme_id"],
            "theme_label": at["theme_label"],
            "interpretation": at.get("interpretation"),
            "supporting_papers_sampled": sup,
            "supporting_paper_total": len(sup_all),
            "counter_evidence": at.get("counter_evidence", []),
        })

    # Load A1 memos for needed papers
    memos = {}
    memos_dir = silo_dir / "memos"
    for pid in sorted(papers_needed):
        p = memos_dir / f"{pid}.json"
        if not p.exists():
            memos[pid] = {"paper_id": pid, "_missing": True}
            continue
        memos[pid] = trim_memo(json.loads(p.read_text(encoding="utf-8")))

    # Render prompt
    tpl = (ROOT / "prompts" / "c2_grounding_check_v1.txt").read_text(encoding="utf-8")
    prompt_sha = hashlib.sha256(tpl.encode("utf-8")).hexdigest()
    rendered = tpl.format(
        silo_name=silo_name,
        silo_code=silo_code,
        analytical_themes_json=json.dumps(trimmed_ats, indent=2, ensure_ascii=False),
        a1_memos_json=json.dumps(memos, indent=2, ensure_ascii=False),
    )
    rendered_sha = hashlib.sha256(rendered.encode("utf-8")).hexdigest()

    out_path = silo_dir / "themes" / "c2_grounding_check.prompt.txt"
    out_path.write_text(rendered, encoding="utf-8")

    meta = {
        "silo": silo_code,
        "silo_name": silo_name,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "prompt_file": "c2_grounding_check_v1.txt",
        "prompt_sha256": prompt_sha,
        "rendered_sha256": rendered_sha,
        "prompt_chars": len(rendered),
        "approx_tokens_k": round(len(rendered) / 4000, 1),
        "analytical_theme_count": len(trimmed_ats),
        "papers_loaded": len(memos),
        "papers_with_missing_memo": sum(1 for m in memos.values() if m.get("_missing")),
        "memo_schema_key_points": sum(1 for m in memos.values() if m.get("key_points")),
        "memo_schema_dim_fallback": sum(1 for m in memos.values() if m.get("_schema") == "raw_8_dimension_fallback"),
        "memo_schema_empty": sum(1 for m in memos.values() if m.get("_schema") == "empty"),
        "model_intended": "gpt-5.4",
        "render_version": "v2_dim_fallback",
    }
    (silo_dir / "themes" / "c2_grounding_check.meta.json").write_text(
        json.dumps(meta, indent=2), encoding="utf-8"
    )
    return meta


def main():
    all_meta = []
    for silo_name, silo_code in SILOS:
        m = render_for_silo(silo_name, silo_code)
        all_meta.append(m)
        print(f"{silo_code}: themes={m['analytical_theme_count']} papers={m['papers_loaded']} tokens_k={m['approx_tokens_k']} missing={m['papers_with_missing_memo']}")
    total_tokens = sum(m["approx_tokens_k"] for m in all_meta)
    print(f"\nTotal tokens across 8 silos: {total_tokens:.1f}K")


if __name__ == "__main__":
    main()
