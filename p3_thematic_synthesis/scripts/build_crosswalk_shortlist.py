"""Build theme-to-literature crosswalk shortlist (G0.3).

Selects 2 grounded + top-10 partially_grounded analytical themes for crosswalk
to prior reviews. Uses supporting_paper_count as strength score and len(grounded_in)
as richness tiebreak. Drops unsupported themes.

Output: docs/THEME_CROSSWALK_SHORTLIST.md (human-review-ready).
"""
import json
from pathlib import Path
from datetime import datetime, timezone

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
PARTIAL_CAP = 10


def main():
    rows = []
    for silo_name, silo_code in SILOS:
        b2 = json.loads((ROOT / "s4_thematic_coding" / silo_name / "themes"
                         / "b2_silo_themes.json").read_text(encoding="utf-8"))
        c2 = json.loads((ROOT / "s4_thematic_coding" / silo_name / "themes"
                         / "c2_grounding_check.json").read_text(encoding="utf-8"))
        c2_by_id = {g["theme_id"]: g for g in c2["grounding_checks"]}
        for at in b2["output"]["analytical_themes"]:
            tid = at["theme_id"]
            gc = c2_by_id.get(tid, {})
            rows.append({
                "silo_code": silo_code,
                "silo_name": silo_name,
                "theme_id": tid,
                "theme_label": at["theme_label"],
                "interpretation": at.get("interpretation", ""),
                "verdict": gc.get("verdict", "unknown"),
                "confidence": gc.get("confidence", ""),
                "supporting_paper_count": len(at.get("supporting_papers", [])),
                "grounded_in_count": len(at.get("grounded_in", [])),
                "counter_evidence_count": len(at.get("counter_evidence", [])),
                "flagged_paper_count": len(gc.get("flagged_papers", [])),
            })

    grounded = [r for r in rows if r["verdict"] == "grounded"]
    partial = [r for r in rows if r["verdict"] == "partially_grounded"]
    unsupported = [r for r in rows if r["verdict"] == "unsupported"]

    # Rank partial by supporting_paper_count desc, grounded_in_count desc
    partial_ranked = sorted(
        partial,
        key=lambda r: (r["supporting_paper_count"], r["grounded_in_count"]),
        reverse=True,
    )
    shortlist = grounded + partial_ranked[:PARTIAL_CAP]

    # Check silo balance
    silos_represented = {r["silo_code"] for r in shortlist}
    missing_silos = [c for _, c in SILOS if c not in silos_represented]
    backfill = []
    if missing_silos:
        # For each missing silo, add its strongest partial (if any)
        for _, code in SILOS:
            if code in silos_represented:
                continue
            candidates = [r for r in partial_ranked if r["silo_code"] == code]
            if candidates:
                backfill.append(candidates[0])
                silos_represented.add(code)
    full_shortlist = shortlist + backfill

    lines = [
        "# Theme-to-Literature Crosswalk Shortlist",
        "",
        f"Generated: {datetime.now(timezone.utc).isoformat()}",
        "",
        f"Source: B2 analytical themes × C2 v2 grounding verdicts.",
        f"Rule: 2 grounded auto-included; top-{PARTIAL_CAP} partial by (supporting_paper_count, grounded_in_count); "
        f"silo-balance backfill ensures every silo has at least one representative.",
        f"Unsupported themes are NOT crosswalked; they go through disposition instead.",
        "",
        "## Global counts (v2)",
        "",
        f"- Total analytical themes: {len(rows)}",
        f"- Grounded: {len(grounded)}",
        f"- Partially grounded: {len(partial)}",
        f"- Unsupported: {len(unsupported)}",
        "",
        f"## Shortlist ({len(full_shortlist)} themes)",
        "",
        "| # | Silo | Theme ID | Verdict | Conf | Papers | DTs | Counter | Theme label |",
        "|---|------|----------|:-------:|:----:|:------:|:---:|:-------:|-------------|",
    ]
    for i, r in enumerate(full_shortlist, 1):
        tag = "🟢" if r["verdict"] == "grounded" else "🟡"
        note = r["theme_label"][:90].replace("|", "\\|") + ("…" if len(r["theme_label"]) > 90 else "")
        lines.append(
            f"| {i} | {r['silo_code']} | {r['theme_id']} | {tag} {r['verdict']} | {r['confidence']} "
            f"| {r['supporting_paper_count']} | {r['grounded_in_count']} | {r['counter_evidence_count']} | {note} |"
        )

    lines += [
        "",
        "## Grounded themes (auto-included)",
        "",
    ]
    for r in grounded:
        lines += [
            f"### {r['theme_id']} ({r['silo_code']}) 🟢",
            f"**Label**: {r['theme_label']}",
            "",
            f"**Interpretation**: {r['interpretation']}",
            "",
        ]

    lines += [
        "## Partially grounded, selected for crosswalk (top-ranked)",
        "",
    ]
    for r in partial_ranked[:PARTIAL_CAP]:
        lines += [
            f"### {r['theme_id']} ({r['silo_code']}) 🟡  papers={r['supporting_paper_count']} DTs={r['grounded_in_count']}",
            f"**Label**: {r['theme_label']}",
            "",
            f"**Interpretation**: {r['interpretation']}",
            "",
        ]

    if backfill:
        lines += [
            "## Silo-balance backfill",
            "",
        ]
        for r in backfill:
            lines += [
                f"### {r['theme_id']} ({r['silo_code']}) 🟡 (backfill for silo coverage)",
                f"**Label**: {r['theme_label']}",
                "",
                f"**Interpretation**: {r['interpretation']}",
                "",
            ]

    lines += [
        "## Unsupported themes (NOT in crosswalk)",
        "",
        "These require disposition (demote / revise / drop) before Chapter 6 prose. See `docs/C2_GROUNDING_REPORT.md`.",
        "",
    ]
    for r in unsupported:
        lines.append(f"- **{r['theme_id']}** ({r['silo_code']}): {r['theme_label']}")

    (ROOT / "docs" / "THEME_CROSSWALK_SHORTLIST.md").write_text(
        "\n".join(lines), encoding="utf-8"
    )

    # Machine-readable export for the crosswalk LLM call
    (ROOT / "s5_cross_silo" / "crosswalk_shortlist.json").write_text(
        json.dumps({
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "rule": f"2 grounded + top-{PARTIAL_CAP} partial + silo-balance backfill",
            "shortlist": full_shortlist,
            "unsupported_count": len(unsupported),
        }, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    print(f"Shortlist: {len(full_shortlist)} themes ({len(grounded)} grounded, "
          f"{min(PARTIAL_CAP, len(partial_ranked))} top-partial, {len(backfill)} backfill)")
    print(f"Silo coverage: {sorted(silos_represented)}")
    print(f"Written: docs/THEME_CROSSWALK_SHORTLIST.md")
    print(f"Written: s5_cross_silo/crosswalk_shortlist.json")


if __name__ == "__main__":
    main()
