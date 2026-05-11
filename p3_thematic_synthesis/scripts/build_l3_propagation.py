"""Stage B — L3 propagation audit + AT/DT flag annotation (relevance-aware).

Naive paper-level propagation overcounts: a paper may carry a `major` L3 flag
on its `dimension_5_stated_limitations` while an AT cites the paper *only* for
`dimension_2_quantum_method`. The flag does not undermine that AT's claim.

This script implements relevance-aware propagation:

1. For every (AT/DT, paper) edge, compute `relied_dims`: the set of A2 memo
   dimensions the theme actually depends on, derived from the code_ids the
   theme (or its grounding DTs, for ATs) cites for that paper.
2. For every L3 flag on that paper, attribute the flag to a memo dimension by
   matching the flag's `memo_sentence` against each dimension's `text` (longest
   60-char window match, threshold = 40 chars). Unmatched flags are tagged
   `dimension_unknown` and treated conservatively as relevant.
3. A flag is RELEVANT to a theme if its dimension is in the theme's relied set
   (or is unknown).
4. Annotate each AT/DT in place with:
       l3_flags        : list of {paper_id, problem_count, severity_max, has_major,
                                  problem_types, relevant_problem_count, relevant_has_major}
       l3_unflagged_support_ratio : {
           "any":              <ratio with naive any-flag denominator>,
           "any_major":        <ratio with naive any-major-flag denominator>,
           "relevant":         <ratio with relevance-filtered any-flag denominator>,
           "relevant_major":   <ratio with relevance-filtered major-flag denominator>,
       }
5. Per-silo manifest: p3_thematic_synthesis/s4_thematic_coding/{silo}/themes/l3_propagation.json
6. Global summary: p3_thematic_synthesis/s4_thematic_coding/output/l3_propagation_summary.md

Read-only over: L3 records, A2 memos, c2/c3.
Modifies in place (additive, schema-preserving): b1_batch_*.json, b2_silo_themes.json.
Does NOT call an LLM. Does NOT touch the manuscript.
"""

from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
S4_ROOT = REPO_ROOT / "p3_thematic_synthesis" / "s4_thematic_coding"
PAPERS_DIR = S4_ROOT / "papers"
OUTPUT_DIR = S4_ROOT / "output"

ACTIVE_SILOS = [
    "credit_lending",
    "derivative_pricing",
    "fraud_detection",
    "portfolio_optimization",
    "quantum_ml_finance",
    "risk_management",
    "simulation_monte_carlo",
    "trading_execution",
]

SEVERITY_RANK = {"minor": 1, "major": 2}


# ─── Relevance match ─────────────────────────────────────────────────

def _normalize(s: str) -> str:
    return re.sub(r"\s+", " ", (s or "").lower()).strip().strip('"')


def match_dimension(memo_sentence: str, memo: dict) -> str:
    """Return the memo dimension key whose `text` best contains memo_sentence
    (or vice versa). Returns 'dimension_unknown' if no dimension matches >=40 chars."""
    ms = _normalize(memo_sentence)
    if len(ms) < 20:
        return "dimension_unknown"
    best_score = 0
    best_dim = "dimension_unknown"
    for k, v in memo.items():
        if not isinstance(v, dict):
            continue
        text = _normalize(v.get("text") or "")
        if not text:
            continue
        score = 0
        for start in range(0, max(1, len(ms) - 60), 30):
            chunk = ms[start:start + 60]
            if chunk in text:
                score = max(score, len(chunk))
        for start in range(0, max(1, len(text) - 60), 30):
            chunk = text[start:start + 60]
            if chunk in ms:
                score = max(score, len(chunk))
        if score > best_score:
            best_score = score
            best_dim = k
    return best_dim if best_score >= 40 else "dimension_unknown"


# ─── L3 indexing ─────────────────────────────────────────────────────

def load_l3_index() -> dict[str, dict]:
    """Map paper_id -> {problems: [{type, severity, memo_sentence, dim?}, ...],
                         problem_count, has_major, severity_max, problem_types}.
    Dimension attribution is deferred to per-paper resolution (needs the memo).
    """
    idx: dict[str, dict] = {}
    for p in PAPERS_DIR.glob("*_l3.json"):
        with p.open(encoding="utf-8") as f:
            rec = json.load(f)
        pid = rec.get("paper_id") or p.stem.removesuffix("_l3")
        problems = rec.get("problems", []) or []
        sev_ranks = [SEVERITY_RANK.get(pr.get("severity", ""), 0) for pr in problems]
        sev_max = max(sev_ranks) if sev_ranks else 0
        sev_label = "major" if sev_max == 2 else "minor" if sev_max == 1 else "none"
        idx[pid] = {
            "problems": problems,                 # raw, with memo_sentence
            "problem_count": int(rec.get("problem_count", len(problems))),
            "has_major": any(s == 2 for s in sev_ranks),
            "severity_max": sev_label,
            "problem_types": sorted({pr.get("type", "?") for pr in problems}),
        }
    return idx


def load_memo(pid: str) -> dict | None:
    p = PAPERS_DIR / f"{pid}.json"
    if not p.is_file():
        return None
    with p.open(encoding="utf-8") as f:
        return json.load(f)


# ─── Theme → relied dimensions ───────────────────────────────────────

def relied_dims_for(theme: dict, pid: str, b2_dts_by_id: dict, memo: dict) -> set[str]:
    """Compute which A2 memo dimensions this theme actually relies on for paper pid.

    For DTs: theme.support_code_ids[pid] is the cited-code set directly.
    For ATs: union over theme.grounded_in DTs of dt.support_code_ids[pid].
    """
    cited_codes: set[str] = set()
    if "grounded_in" in theme:
        for dt_id in theme.get("grounded_in", []):
            dt = b2_dts_by_id.get(dt_id, {})
            cited_codes.update(dt.get("support_code_ids", {}).get(pid, []))
    else:
        cited_codes.update(theme.get("support_code_ids", {}).get(pid, []))

    dims: set[str] = set()
    for k, v in memo.items():
        if isinstance(v, dict) and "support_codes" in v:
            sc = set(v.get("support_codes", []))
            if cited_codes & sc:
                dims.add(k)
    return dims


# ─── Annotate one theme ──────────────────────────────────────────────

def annotate_theme(theme: dict, l3_idx: dict, memo_cache: dict, b2_dts_by_id: dict) -> dict:
    """Annotate theme in place; return per-theme classification record."""
    supporting = list(theme.get("supporting_papers", []))
    n_total = len(supporting)
    flags = []
    n_any = n_major = n_relevant_any = n_relevant_major = 0

    for pid in supporting:
        rec = l3_idx.get(pid)
        memo = memo_cache.get(pid) if rec else None
        if memo is None:
            memo = load_memo(pid)
            memo_cache[pid] = memo
        if rec is None:
            flags.append({
                "paper_id": pid,
                "problem_count": 0,
                "severity_max": "no_l3_record",
                "has_major": False,
                "problem_types": [],
                "relevant_problem_count": 0,
                "relevant_has_major": False,
            })
            continue
        if rec["problem_count"] == 0:
            continue

        n_any += 1
        if rec["has_major"]:
            n_major += 1

        # Compute relied dims and relevance per flag
        relied = relied_dims_for(theme, pid, b2_dts_by_id, memo) if memo else set()
        rel_count = 0
        rel_has_major = False
        flag_breakdown = []
        for pr in rec["problems"]:
            dim = match_dimension(pr.get("memo_sentence", ""), memo) if memo else "dimension_unknown"
            is_relevant = (dim == "dimension_unknown") or (dim in relied)
            if is_relevant:
                rel_count += 1
                if pr.get("severity") == "major":
                    rel_has_major = True
            flag_breakdown.append({
                "type": pr.get("type"),
                "severity": pr.get("severity"),
                "dimension": dim,
                "relevant": is_relevant,
            })

        if rel_count > 0:
            n_relevant_any += 1
            if rel_has_major:
                n_relevant_major += 1

        flags.append({
            "paper_id": pid,
            "problem_count": rec["problem_count"],
            "severity_max": rec["severity_max"],
            "has_major": rec["has_major"],
            "problem_types": rec["problem_types"],
            "relevant_problem_count": rel_count,
            "relevant_has_major": rel_has_major,
            "relied_dimensions": sorted(relied),
            "flag_dimensions": flag_breakdown,
        })

    def ratio(flagged: int) -> float:
        return round((n_total - flagged) / n_total, 3) if n_total else 1.0

    theme["l3_flags"] = flags
    theme["l3_unflagged_support_ratio"] = {
        "any":            ratio(n_any),
        "any_major":      ratio(n_major),
        "relevant":       ratio(n_relevant_any),
        "relevant_major": ratio(n_relevant_major),
    }

    return {
        "theme_id": theme.get("theme_id"),
        "theme_label": theme.get("theme_label"),
        "n_supporting": n_total,
        "flagged_any":            n_any,
        "flagged_any_major":      n_major,
        "flagged_relevant":       n_relevant_any,
        "flagged_relevant_major": n_relevant_major,
        "ratios": theme["l3_unflagged_support_ratio"],
    }


# ─── Per-silo processing ─────────────────────────────────────────────

def process_silo(silo: str, l3_idx: dict) -> dict:
    themes_dir = S4_ROOT / silo / "themes"
    b1_files = sorted(themes_dir.glob("b1_batch_*.json"))
    b2_path = themes_dir / "b2_silo_themes.json"

    memo_cache: dict[str, dict] = {}
    dt_records: list[dict] = []
    at_records: list[dict] = []

    # Build the b2 DT lookup first (needed for AT relied-dims walk).
    b2 = json.loads(b2_path.read_text(encoding="utf-8")) if b2_path.is_file() else None
    dts_by_id: dict[str, dict] = {}
    if b2:
        out = b2.get("output", {}) or {}
        dts_by_id = {dt["theme_id"]: dt for dt in out.get("descriptive_themes", [])}

    # Annotate b1 DTs
    for b1_path in b1_files:
        with b1_path.open(encoding="utf-8") as f:
            b1 = json.load(f)
        for theme in b1.get("themes", []):
            row = annotate_theme(theme, l3_idx, memo_cache, dts_by_id)
            row["source"] = "b1"
            row["source_file"] = b1_path.name
            dt_records.append(row)
        with b1_path.open("w", encoding="utf-8") as f:
            json.dump(b1, f, indent=2, ensure_ascii=False)

    # Annotate b2 DTs and ATs
    if b2:
        out = b2.get("output", {}) or {}
        for theme in out.get("descriptive_themes", []):
            row = annotate_theme(theme, l3_idx, memo_cache, dts_by_id)
            row["source"] = "b2_DT"
            row["source_file"] = b2_path.name
            dt_records.append(row)
        for theme in out.get("analytical_themes", []):
            row = annotate_theme(theme, l3_idx, memo_cache, dts_by_id)
            row["source"] = "b2_AT"
            row["source_file"] = b2_path.name
            at_records.append(row)
        with b2_path.open("w", encoding="utf-8") as f:
            json.dump(b2, f, indent=2, ensure_ascii=False)

    manifest = {
        "_generated": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "_purpose": "Stage B propagation audit — paper-level L3 flags lifted to AT/DT level with relevance filtering.",
        "_views": {
            "any":            "Naive: paper flagged if it has any L3 problem (98.2 % corpus rate; threshold-vacuous).",
            "any_major":      "Naive: paper flagged if it has any major-severity L3 problem (91.7 % corpus rate; still saturated).",
            "relevant":       "Relevance-filtered: paper flagged only if at least one L3 problem targets a memo dimension the theme actually relies on (or has unknown dimension; conservative).",
            "relevant_major": "Relevance-filtered AND major-severity: recommended primary view for downstream R1 review.",
        },
        "_recommended_view": "relevant_major",
        "_note_no_threshold": "No retain/queue verdict is computed at this layer. The original `> 0.5` rule was designed when L3 was a 16.5 % sparse sample; under 100 %-coverage mini+v3 it is non-discriminative even after relevance filtering. Verdicts are deferred to the R1 stratified review (see .github/skills/p3-r1-review/), which uses these annotations as evidence packs.",
        "silo": silo,
        "ats": at_records,
        "dts": dt_records,
        "totals": _silo_totals(at_records, dt_records),
    }
    out_path = themes_dir / "l3_propagation.json"
    with out_path.open("w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)

    return manifest


def _silo_totals(ats: list[dict], dts: list[dict]) -> dict:
    def agg(rows, key):
        return sum(r.get(key, 0) for r in rows)
    return {
        "n_ats": len(ats),
        "n_dts": len(dts),
        "ats_total_supporting":            agg(ats, "n_supporting"),
        "ats_flagged_any":                 agg(ats, "flagged_any"),
        "ats_flagged_any_major":           agg(ats, "flagged_any_major"),
        "ats_flagged_relevant":            agg(ats, "flagged_relevant"),
        "ats_flagged_relevant_major":      agg(ats, "flagged_relevant_major"),
        "dts_total_supporting":            agg(dts, "n_supporting"),
        "dts_flagged_any":                 agg(dts, "flagged_any"),
        "dts_flagged_any_major":           agg(dts, "flagged_any_major"),
        "dts_flagged_relevant":            agg(dts, "flagged_relevant"),
        "dts_flagged_relevant_major":      agg(dts, "flagged_relevant_major"),
        "ats_with_zero_relevant_major":    sum(1 for r in ats if r["flagged_relevant_major"] == 0),
        "dts_with_zero_relevant_major":    sum(1 for r in dts if r["flagged_relevant_major"] == 0),
        "ats_fully_relevant_major_flagged": sum(1 for r in ats if r["n_supporting"] > 0 and r["flagged_relevant_major"] == r["n_supporting"]),
        "dts_fully_relevant_major_flagged": sum(1 for r in dts if r["n_supporting"] > 0 and r["flagged_relevant_major"] == r["n_supporting"]),
    }


# ─── Summary ─────────────────────────────────────────────────────────

def render_summary(per_silo: list[dict]) -> str:
    lines = [
        "# Stage B — L3 propagation audit summary (relevance-aware)",
        "",
        f"_Generated: {datetime.now(timezone.utc).isoformat(timespec='seconds')}_  ",
        "_Script: `p3_thematic_synthesis/scripts/build_l3_propagation.py`_",
        "",
        "## Method",
        "",
        "Every AT and DT in the 8 active silos has been annotated in place (in",
        "`b1_batch_*.json` and `b2_silo_themes.json`) with two new fields:",
        "",
        "- `l3_flags`: per-paper flag breakdown including the L3-attributed memo",
        "  dimension and a `relevant` bit per flag (whether that dimension is one",
        "  the theme actually relies on).",
        "- `l3_unflagged_support_ratio`: four parallel views of",
        "  `(unflagged_supporting_papers / total_supporting_papers)`.",
        "",
        "### The four views",
        "",
        "| View | What counts as flagged | Corpus base rate | Use |",
        "|---|---|---|---|",
        "| `any` | Any L3 problem at all | 98.2 % | Saturated; documentation only. |",
        "| `any_major` | Any major-severity problem | 91.7 % | Saturated; documentation only. |",
        "| `relevant` | Any flag whose memo dimension overlaps the theme's relied set (or is unknown). | Theme-specific | Filters out limitation-section nags etc. |",
        "| `relevant_major` | Relevant + major. | Theme-specific | **Recommended primary view for R1 evidence packs.** |",
        "",
        "Dimension attribution: each flag's `memo_sentence` is matched against",
        "the per-dimension `text` field of the paper's A2 memo (longest 60-char",
        "window; threshold = 40 chars). Unmatched flags are tagged",
        "`dimension_unknown` and treated *conservatively as relevant*.",
        "",
        "### No retain/queue verdict at this layer",
        "",
        "The original `unflagged > 0.5 = retained, else queued` rule was designed",
        "when L3 was a 16.5 % sparse sample. Under the new 100 %-coverage mini+v3",
        "safeguard the rule is non-discriminative even on `relevant_major` (the",
        "model's tendency to flag every limitation as `MISSING_LIMITATION` keeps",
        "the base rate high). Per-theme verdicts are therefore deferred to the R1",
        "stratified review, which uses the per-paper `l3_flags` lists as evidence",
        "packs.",
        "",
        "## Per-silo evidence",
        "",
        "Each row reports the *count of supporting papers* under each view, then",
        "the *count of themes whose every supporting paper is relevant-major-flagged*",
        "(saturated themes — likely highest-priority for R1 attention).",
        "",
        "| Silo | ATs | DTs | AT support flagged (any / any-major / relevant / relevant-major) | DT support flagged (any / any-major / relevant / relevant-major) | ATs fully rel-major flagged | DTs fully rel-major flagged |",
        "|---|---:|---:|---|---|---:|---:|",
    ]
    tot = {"n_ats": 0, "n_dts": 0, "ats_full": 0, "dts_full": 0,
           "at_a": 0, "at_am": 0, "at_r": 0, "at_rm": 0,
           "at_tot": 0, "dt_tot": 0,
           "dt_a": 0, "dt_am": 0, "dt_r": 0, "dt_rm": 0}
    for m in per_silo:
        t = m["totals"]
        lines.append(
            f"| {m['silo']} | {t['n_ats']} | {t['n_dts']} | "
            f"{t['ats_flagged_any']} / {t['ats_flagged_any_major']} / "
            f"{t['ats_flagged_relevant']} / {t['ats_flagged_relevant_major']} "
            f"(of {t['ats_total_supporting']}) | "
            f"{t['dts_flagged_any']} / {t['dts_flagged_any_major']} / "
            f"{t['dts_flagged_relevant']} / {t['dts_flagged_relevant_major']} "
            f"(of {t['dts_total_supporting']}) | "
            f"{t['ats_fully_relevant_major_flagged']} | "
            f"{t['dts_fully_relevant_major_flagged']} |"
        )
        tot["n_ats"] += t["n_ats"]; tot["n_dts"] += t["n_dts"]
        tot["ats_full"] += t["ats_fully_relevant_major_flagged"]
        tot["dts_full"] += t["dts_fully_relevant_major_flagged"]
        tot["at_a"]  += t["ats_flagged_any"]
        tot["at_am"] += t["ats_flagged_any_major"]
        tot["at_r"]  += t["ats_flagged_relevant"]
        tot["at_rm"] += t["ats_flagged_relevant_major"]
        tot["at_tot"] += t["ats_total_supporting"]
        tot["dt_a"]  += t["dts_flagged_any"]
        tot["dt_am"] += t["dts_flagged_any_major"]
        tot["dt_r"]  += t["dts_flagged_relevant"]
        tot["dt_rm"] += t["dts_flagged_relevant_major"]
        tot["dt_tot"] += t["dts_total_supporting"]

    lines.append(
        f"| **TOTAL** | **{tot['n_ats']}** | **{tot['n_dts']}** | "
        f"**{tot['at_a']} / {tot['at_am']} / {tot['at_r']} / {tot['at_rm']}** "
        f"(of **{tot['at_tot']}**) | "
        f"**{tot['dt_a']} / {tot['dt_am']} / {tot['dt_r']} / {tot['dt_rm']}** "
        f"(of **{tot['dt_tot']}**) | **{tot['ats_full']}** | **{tot['dts_full']}** |"
    )
    rel_drop_at = (1 - tot["at_rm"] / tot["at_am"]) * 100 if tot["at_am"] else 0
    rel_drop_dt = (1 - tot["dt_rm"] / tot["dt_am"]) * 100 if tot["dt_am"] else 0
    lines += [
        "",
        f"**Relevance filter effect**: AT-supporting flagged paper-edges drop from "
        f"**{tot['at_am']}** (any-major) to **{tot['at_rm']}** (relevant-major) — "
        f"a **{rel_drop_at:.1f} %** reduction. DT edges drop from "
        f"**{tot['dt_am']}** to **{tot['dt_rm']}** ({rel_drop_dt:.1f} % reduction).",
        "",
        "## Per-silo manifests",
        "",
    ]
    for m in per_silo:
        lines.append(f"- `p3_thematic_synthesis/s4_thematic_coding/{m['silo']}/themes/l3_propagation.json`")
    lines += [
        "",
        "## Source-file annotations",
        "",
        "Each AT and DT in `b1_batch_*.json` and `b2_silo_themes.json` now carries",
        "`l3_flags` (with per-flag dimension + relevance) and",
        "`l3_unflagged_support_ratio` (with the four views above). The original",
        "`theme_id`, `theme_label`, `description`/`interpretation`, `supporting_papers`,",
        "`support_code_ids`, `grounded_in`, `counter_evidence`, and `implication`",
        "fields are unchanged — annotation is strictly additive.",
        "",
    ]
    return "\n".join(lines)


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    print("Loading L3 index...")
    l3_idx = load_l3_index()
    print(f"  {len(l3_idx)} L3 records")

    per_silo: list[dict] = []
    for silo in ACTIVE_SILOS:
        print(f"\nSilo: {silo}")
        m = process_silo(silo, l3_idx)
        t = m["totals"]
        print(f"  {t['n_ats']} ATs, {t['n_dts']} DTs")
        print(f"  AT supports flagged: any={t['ats_flagged_any']}  any_major={t['ats_flagged_any_major']}  "
              f"relevant={t['ats_flagged_relevant']}  relevant_major={t['ats_flagged_relevant_major']}  "
              f"(of {t['ats_total_supporting']})")
        print(f"  DT supports flagged: any={t['dts_flagged_any']}  any_major={t['dts_flagged_any_major']}  "
              f"relevant={t['dts_flagged_relevant']}  relevant_major={t['dts_flagged_relevant_major']}  "
              f"(of {t['dts_total_supporting']})")
        print(f"  Themes fully relevant-major-flagged: ATs={t['ats_fully_relevant_major_flagged']}  "
              f"DTs={t['dts_fully_relevant_major_flagged']}")
        per_silo.append(m)

    md = render_summary(per_silo)
    out_md = OUTPUT_DIR / "l3_propagation_summary.md"
    out_md.write_text(md, encoding="utf-8")
    print(f"\nwrote {out_md}")


if __name__ == "__main__":
    main()
