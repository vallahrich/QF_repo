#!/usr/bin/env python
"""Extract the per-silo drafting data sheet for Chapter 6 silo drafting.

For each silo, consolidates:
- paper count (from projection_manifest.json)
- descriptive themes (DT) with title + paper count
- analytical themes (AT) with title + interpretation + C2 verdict + flagged_papers
- C3 crosswalk entries for each retained AT

Output: one markdown data sheet per silo in p3_thematic_synthesis/scripts/output/
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
S4 = ROOT / "p3_thematic_synthesis" / "s4_thematic_coding"
C3_PATH = ROOT / "p3_thematic_synthesis" / "s5_cross_silo" / "c3_crosswalk.json"
OUT_DIR = ROOT / "p3_thematic_synthesis" / "scripts" / "output"

SILO_ORDER = [
    "fraud_detection",
    "quantum_ml_finance",
    "trading_execution",
    "credit_lending",
    "derivative_pricing",
    "portfolio_optimization",
    "simulation_monte_carlo",
]


def load_c3():
    if not C3_PATH.exists():
        return {}
    raw = json.loads(C3_PATH.read_text(encoding="utf-8"))
    by_theme = {}
    for t in raw.get("crosswalk", []):
        tid = t.get("theme_id")
        if not tid:
            continue
        by_theme[tid] = t.get("entries", [])
    return by_theme


def extract_silo(slug, c3_by_theme):
    silo_dir = S4 / slug
    b2 = json.loads((silo_dir / "themes" / "b2_silo_themes.json").read_text(encoding="utf-8"))
    c2 = json.loads((silo_dir / "themes" / "c2_grounding_check.json").read_text(encoding="utf-8"))
    manifest = json.loads((silo_dir / "projection_manifest.json").read_text(encoding="utf-8"))

    out = b2.get("output", b2)
    dt_list = out.get("descriptive_themes", [])
    at_list = out.get("analytical_themes", [])
    c2_by_id = {t["theme_id"]: t for t in c2.get("grounding_checks", [])}

    total = manifest.get("total_papers", "?")
    single_list = manifest.get("single_silo", [])
    multi_list = manifest.get("multi_silo", [])
    single_n = len(single_list) if isinstance(single_list, list) else manifest.get("single_silo_count", "?")
    multi_n = len(multi_list) if isinstance(multi_list, list) else manifest.get("multi_silo_count", "?")

    lines = []
    lines.append(f"# Silo data sheet — {slug}")
    lines.append("")
    lines.append(f"- total papers: **{total}**  (single-silo: {single_n}, multi-silo: {multi_n})")
    lines.append(f"- DT count: {len(dt_list)}")
    lines.append(f"- AT count: {len(at_list)}")
    lines.append("")
    lines.append("## Descriptive themes (DT)")
    lines.append("")
    for dt in dt_list:
        n_papers = len(dt.get("supporting_papers", []))
        lines.append(f"### {dt.get('theme_id')} · {n_papers} papers")
        lines.append(f"**{dt.get('theme_label','')}**")
        lines.append("")
        lines.append(dt.get("description", ""))
        lines.append("")

    lines.append("## Analytical themes (AT)")
    lines.append("")
    for at in at_list:
        tid = at.get("theme_id")
        c2t = c2_by_id.get(tid, {})
        verdict = c2t.get("verdict", "?")
        conf = c2t.get("confidence", "?")
        lines.append(f"### {tid} · C2={verdict} ({conf})")
        lines.append(f"**{at.get('theme_label','')}**")
        lines.append("")
        lines.append("_Interpretation:_ " + at.get("interpretation", ""))
        lines.append("")
        lines.append(f"_grounded_in DT:_ {', '.join(at.get('grounded_in', []))}")
        lines.append("")
        ce = at.get("counter_evidence", [])
        if ce:
            lines.append("**B2 counter_evidence:**")
            for c in ce:
                lines.append(f"- `{c.get('paper_id')}` ({c.get('evidence_type')}): {c.get('reason','')}")
            lines.append("")
        flagged = c2t.get("flagged_papers", [])
        if flagged:
            lines.append("**C2 flagged_papers:**")
            for f in flagged:
                lines.append(f"- `{f.get('paper_id')}` ({f.get('issue')}): {f.get('note','')}")
            lines.append("")
        if c2t.get("reason"):
            lines.append("_C2 reason:_ " + c2t["reason"])
            lines.append("")
        xs = c3_by_theme.get(tid, [])
        if xs:
            lines.append("**C3 crosswalk entries:**")
            for e in xs:
                rel = e.get("relationship", "?")
                conf = e.get("stance_confidence", "?")
                rev = e.get("review_paper_id", "?")
                title = e.get("review_title_short", "")
                quote = (e.get("quoted_claim") or "").strip().replace("\n", " ")
                lines.append(f"- **{rel}** ({conf}) · `{rev}` *{title}*")
                lines.append(f"  > \"{quote}\"")
            lines.append("")

    summary = c2.get("silo_summary", {})
    if summary:
        lines.append("## C2 silo summary")
        lines.append("")
        for k, v in summary.items():
            lines.append(f"- **{k}**: {v}")

    return "\n".join(lines)


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    c3_by_theme = load_c3()
    targets = SILO_ORDER if len(sys.argv) < 2 else sys.argv[1:]
    for slug in targets:
        try:
            text = extract_silo(slug, c3_by_theme)
        except Exception as e:
            print(f"[SKIP] {slug}: {e}")
            continue
        out_path = OUT_DIR / f"silo_sheet_{slug}.md"
        out_path.write_text(text, encoding="utf-8")
        print(f"[ok] {out_path.relative_to(ROOT)}  ({len(text)} chars)")


if __name__ == "__main__":
    main()
