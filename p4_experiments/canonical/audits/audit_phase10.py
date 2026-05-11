"""Phase 10 audit - manuscript artifacts."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
CANON = ROOT / "p4_experiments" / "canonical"
COHORT = CANON / "cohort.json"
OUTPUTS = CANON / "outputs"
OUT_DIR = OUTPUTS / "manuscript_artifacts"
REPORT = CANON / "reports" / "audit" / "audit_phase10.json"

EXPECTED_FILES = [
    "key_numbers.json",
    "table_h4_anchor.tex",
    "table_h1_summary.tex",
    "table_silo_breakdown.tex",
    "figure_oracle_tax_box.csv",
    "figure_h4_sensitivity.csv",
    "table_h1_full_matrix.tex",
    "table_h1_resource_axis_summary.tex",
    "table_h2_silo_effects.tex",
    "table_h2_mixedlm_icc.tex",
    "table_h3_profile_ordering.tex",
    "table_h3_structural_invariants.tex",
    "table_h4_scoreboard.tex",
    "table_circuit_fidelity.tex",
    "table_circuit_fidelity_summary.tex",
    "circuit_fidelity.csv",
    "circuit_fidelity.json",
    "table_h4_failure_taxonomy.tex",
    "table_claims_evidence_matrix.tex",
    "table_engine_failures.tex",
    "table_experiment_regimes.tex",
    "table_phase8d_regime_summary.tex",
    "claims_evidence_matrix.json",
    "figure_h1_heatmap.csv",
    "figure_h4_criterion_heatmap.csv",
    "figure_h4_funnel.csv",
    "figure_regime_map.csv",
    "figure_phase8d_scaling.csv",
    "results_brief.md",
    "discussion_claims.md",
    "caption_pack.md",
]

def main() -> int:
    cohort = json.loads(COHORT.read_text(encoding="utf-8"))
    results: list[dict] = []
    blockers_failed = 0

    def add(check_id: str, status: str, msg: str, blocker: bool = True) -> None:
        nonlocal blockers_failed
        if status == "FAIL" and blocker:
            blockers_failed += 1
        results.append({"id": check_id, "status": status, "blocker": blocker, "message": msg})

    p10 = (cohort.get("_phase_status") or {}).get("phase10") or {}
    add("P10.A", "PASS" if p10.get("status") == "complete" else "FAIL",
        f"cohort._phase_status.phase10.status='{p10.get('status')}'")

    missing = [f for f in EXPECTED_FILES if not (OUT_DIR / f).exists()]
    add("P10.B", "PASS" if not missing else "FAIL",
        f"All {len(EXPECTED_FILES)} artifacts present"
        if not missing else f"missing: {missing}")

    # Spot-check key_numbers.json structure.
    kn_path = OUT_DIR / "key_numbers.json"
    if kn_path.exists():
        try:
            kn = json.loads(kn_path.read_text(encoding="utf-8"))
            req = ["n_labels_total", "n_labels_faithful", "n_labels_proxy",
                     "h4_canonical_winners_count", "h4_bifurcation_holds",
                     "h1_accepted_tests_by_axis", "h2_kw_p_value",
                     "h2_mixedlm_label_icc", "h3_friedman_p_value",
                     "h3_kendalls_w", "h4_failure_taxonomy_counts",
                       "claims_evidence_count", "experiment_regime_ids",
                       "headline_regime_id", "appendix_regime_ids",
                       "phase8d_regime_by_status"]
            miss_keys = [k for k in req if k not in kn]
            add("P10.C", "PASS" if not miss_keys else "FAIL",
                f"key_numbers.json has all required keys"
                if not miss_keys else f"missing keys: {miss_keys}")
        except Exception as exc:
            add("P10.C", "FAIL", f"key_numbers.json parse error: {exc}")
    else:
        add("P10.C", "FAIL", "key_numbers.json missing")

    # Sanity-check LaTeX tables non-empty + close braces.
    bad_tex: list[str] = []
    for f in [x for x in EXPECTED_FILES if x.endswith(".tex")]:
        p = OUT_DIR / f
        if not p.exists():
            continue
        s = p.read_text(encoding="utf-8")
        if r"\begin{tabular}" not in s or r"\end{tabular}" not in s:
            bad_tex.append(f)
    add("P10.D", "PASS" if not bad_tex else "FAIL",
        f"All .tex tables well-formed"
        if not bad_tex else f"malformed: {bad_tex}")

    # CSVs have headers and at least one data row.
    bad_csv: list[str] = []
    for f in [x for x in EXPECTED_FILES if x.endswith(".csv")]:
        p = OUT_DIR / f
        if not p.exists():
            continue
        lines = [line for line in p.read_text(encoding="utf-8").splitlines() if line.strip()]
        if len(lines) < 2 or "," not in lines[0]:
            bad_csv.append(f)
    add("P10.E", "PASS" if not bad_csv else "FAIL",
        f"All .csv figure-data files have headers and rows"
        if not bad_csv else f"bad csv files: {bad_csv}")

    # Markdown briefs are non-empty and headed.
    bad_md: list[str] = []
    for f in [x for x in EXPECTED_FILES if x.endswith(".md")]:
        p = OUT_DIR / f
        if not p.exists():
            continue
        text = p.read_text(encoding="utf-8").strip()
        if len(text) < 40 or not text.startswith("#"):
            bad_md.append(f)
    add("P10.F", "PASS" if not bad_md else "FAIL",
        f"All markdown briefs are non-empty and headed"
        if not bad_md else f"bad markdown files: {bad_md}")

    rendered_fig_dir = OUTPUTS / "figures"
    rendered_figures = sorted(rendered_fig_dir.glob("*")) if rendered_fig_dir.exists() else []
    add("P10.G", "PASS" if not rendered_figures else "FAIL",
        "Rendered figure files intentionally excluded; source CSVs are present"
        if not rendered_figures else f"rendered figures should be removed: {[p.name for p in rendered_figures]}")

    n_pass = sum(1 for r in results if r["status"] == "PASS")
    n_fail = sum(1 for r in results if r["status"] == "FAIL")
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps({
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "results": results,
        "totals": {"pass": n_pass, "fail": n_fail, "blockers_failed": blockers_failed},
    }, indent=2), encoding="utf-8")
    print(f"[Phase 10 audit] {n_pass} PASS / {n_fail} FAIL; blockers_failed={blockers_failed}")
    for r in results:
        tag = "[ok]" if r["status"] == "PASS" else "[FAIL]"
        print(f"  {tag} {r['id']}: {r['message']}")
    return 0 if blockers_failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
