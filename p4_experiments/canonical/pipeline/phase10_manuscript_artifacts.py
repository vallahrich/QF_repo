"""Phase 10 - Manuscript artifact generator.

Reads canonical/cohort.json plus canonical/reports/stats_report.json,
canonical/reports/oracle_tax_table.json,
canonical/reports/sensitivity_grid.json, and produces:

    outputs/manuscript_artifacts/
    key_numbers.json               # single source of truth for prose
    table_h4_anchor.tex            # LaTeX table: H4 strict-subset across
                                   # tau-thresholds, Faithful sub-cohort
    table_h1_summary.tex           # LaTeX table: median tau per (profile, eps)
                                   # + Wilcoxon p-value
    table_silo_breakdown.tex       # LaTeX: per-silo cohort + completion stats
    figure_oracle_tax_box.csv      # data for box-plot of log10(tau) at
                                   # H4 anchor, by hardware profile
    figure_h4_sensitivity.csv      # data for tau_threshold sweep panel
    circuit_fidelity.csv/json      # row-level implementation fidelity ledger
    table_circuit_fidelity.tex     # compact label-level claim-boundary table
    evidence-driven H1/H2/H3/H4 tables, figure CSVs, and prose briefs

Caller: invoked by run_pipeline.py as Phase 10 (after Phase 9). All
outputs are deterministic given the inputs - rerun is idempotent.

Note: figures are emitted as CSV + matplotlib-friendly format (no PNG
generation here to keep dependencies minimal in the pipeline image).
The thesis build pulls them via pgfplots / TikZ.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
CANON = ROOT / "p4_experiments" / "canonical"
OUTPUTS = CANON / "outputs"
COHORT = CANON / "cohort.json"
REPORTS = CANON / "reports"
STATS = REPORTS / "stats_report.json"
ORACLE = REPORTS / "oracle_tax_table.json"
SENSITIVITY = REPORTS / "sensitivity_grid.json"
EVIDENCE = REPORTS / "evidence_report.json"
OUT_DIR = OUTPUTS / "manuscript_artifacts"

PROFILES = [
    "sc_e3_surface", "sc_e4_surface",
    "ti_e3_surface", "ti_e4_surface",
    "maj_e6_surface", "maj_e6_floquet",
]
EPSILONS = [1e-3, 1e-4, 1e-6]


def _eps_str(eps: float) -> str:
    return f"{eps:.0e}"


def _profile_pretty(p: str) -> str:
    return {
        "sc_e3_surface": r"SC $10^{-3}$ + surface",
        "sc_e4_surface": r"SC $10^{-4}$ + surface",
        "ti_e3_surface": r"TI $10^{-3}$ + surface",
        "ti_e4_surface": r"TI $10^{-4}$ + surface",
        "maj_e6_surface": r"Maj $10^{-6}$ + surface",
        "maj_e6_floquet": r"Maj $10^{-6}$ + floquet",
    }.get(p, p)


def _tex_escape(value: object) -> str:
    text = "" if value is None else str(value)
    replacements = {
        "\\": r"\textbackslash{}",
        "&": r"\&",
        "%": r"\%",
        "$": r"\$",
        "#": r"\#",
        "_": r"\_",
        "{": r"\{",
        "}": r"\}",
        "~": r"\textasciitilde{}",
        "^": r"\textasciicircum{}",
    }
    return "".join(replacements.get(ch, ch) for ch in text)


def _fmt_num(value: object, digits: int = 3) -> str:
    if isinstance(value, bool):
        return "yes" if value else "no"
    if isinstance(value, int):
        return str(value)
    if isinstance(value, float):
        if value == 0:
            return "0"
        if abs(value) < 0.001 or abs(value) >= 10000:
            return f"{value:.{digits}e}"
        return f"{value:.{digits}g}"
    return "--" if value is None else str(value)


def _fmt_p(value: object) -> str:
    if not isinstance(value, (int, float)):
        return "--"
    return f"{value:.3e}" if value < 0.001 else f"{value:.3f}"


def _csv_field(value: object) -> str:
    text = "" if value is None else str(value)
    if any(ch in text for ch in [",", '"', "\n"]):
        return '"' + text.replace('"', '""') + '"'
    return text


def _csv(rows: list[dict], columns: list[str]) -> str:
    lines = [",".join(columns)]
    for row in rows:
        lines.append(",".join(_csv_field(row.get(col)) for col in columns))
    return "\n".join(lines) + "\n"


def _tex_table(headers: list[str], body: list[list[object]], align: str) -> str:
    rows = [rf"\begin{{tabular}}{{{align}}}", r"\toprule"]
    rows.append(" & ".join(headers) + r" \\")
    rows.append(r"\midrule")
    for row in body:
        rows.append(" & ".join(_tex_escape(value) for value in row) + r" \\")
    rows.append(r"\bottomrule")
    rows.append(r"\end{tabular}")
    return "\n".join(rows) + "\n"


def _read(p: Path) -> dict:
    if not p.exists():
        raise SystemExit(f"required input missing: {p.relative_to(ROOT)}; run earlier phases first")
    return json.loads(p.read_text(encoding="utf-8"))


def _write(p: Path, content: str) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")
    print(f"  wrote {p.relative_to(ROOT)}")


def _table_h4_anchor(stats: dict) -> str:
    """LaTeX table: H4 strict-subset count per tau threshold + baseline scale."""
    h4 = stats.get("H4") or {}
    canonical = h4.get("canonical_winners_count", "N/A")
    sens_tau = h4.get("sensitivity_tau_winners") or {}
    sens_base = h4.get("sensitivity_baseline_winners") or {}
    rows = []
    rows.append(r"\begin{tabular}{lr}")
    rows.append(r"\toprule")
    rows.append(r"Configuration & Strict-H4 winners (of Faithful labels) \\")
    rows.append(r"\midrule")
    rows.append(rf"Canonical ($\tau=10$, baseline$\times 1$) & \textbf{{{canonical}}} \\")
    rows.append(r"\midrule")
    for k in sorted(sens_tau.keys()):
        rows.append(rf"Sensitivity {k.replace('=', '=$') + '$'} & {sens_tau[k]} \\")
    rows.append(r"\midrule")
    for k in sorted(sens_base.keys()):
        k_esc = k.replace('_', r'\_')
        rows.append(rf"Sensitivity {k_esc} & {sens_base[k]} \\")
    rows.append(r"\bottomrule")
    rows.append(r"\end{tabular}")
    return "\n".join(rows) + "\n"


def _table_h1_summary(stats: dict) -> str:
    """LaTeX table: per-(profile, eps) median tau + Wilcoxon p + Cliff's delta.

    Phase 9 (academic-rigor pass 2026-04-19) renamed the raw Wilcoxon
    p-value to ``p_one_sided_greater_raw`` and added a Holm-Bonferroni
    family-corrected ``p_one_sided_greater_holm``. Cliff's delta and the
    triple-condition acceptance flag are also exposed; we display the
    raw p (concise) and the delta (effect size) so the table mirrors
    the pre-registered acceptance criterion. Skip the
    ``_family_summary`` meta-key when iterating cells.
    """
    h1 = stats.get("H1") or {}
    rows = []
    rows.append(r"\begin{tabular}{lrrrr}")
    rows.append(r"\toprule")
    rows.append(
        r"Profile & $\varepsilon$ & median $\tau_{\text{runtime}}$ "
        r"& Wilcoxon $p_{\text{raw}}$ ($\log_{10}\tau>1$) & Cliff's $\delta$ \\"
    )
    rows.append(r"\midrule")
    for prof in PROFILES:
        for eps in EPSILONS:
            cell_key = f"{prof}|{_eps_str(eps)}"
            if cell_key.startswith("_"):
                continue
            cell = h1.get(cell_key) or {}
            rt = cell.get("runtime_seconds") or {}
            med = rt.get("median_tau")
            # Prefer raw, fall back to legacy field name if a stale report
            # is consumed (defensive backward compat for the pre-2026-04-19
            # schema).
            p = rt.get("p_one_sided_greater_raw")
            if p is None:
                p = rt.get("p_one_sided_greater")
            delta = rt.get("cliffs_delta_log10_tau_vs_1")
            med_s = f"{med:.2g}" if isinstance(med, (int, float)) else "--"
            p_s = f"{p:.2e}" if isinstance(p, (int, float)) else "--"
            d_s = f"{delta:.2f}" if isinstance(delta, (int, float)) else "--"
            rows.append(
                rf"{_profile_pretty(prof)} & ${_eps_str(eps)}$ "
                rf"& {med_s} & {p_s} & {d_s} \\"
            )
    rows.append(r"\bottomrule")
    rows.append(r"\end{tabular}")
    return "\n".join(rows) + "\n"


def _table_silo_breakdown(cohort: dict) -> str:
    """LaTeX table: per-silo N_total, N_F, N_P."""
    silos: dict[str, dict[str, int]] = {}
    for lid, e in cohort["labels"].items():
        s = e.get("silo", "unknown")
        d = silos.setdefault(s, {"N": 0, "F": 0, "P": 0})
        d["N"] += 1
        d[e.get("fidelity", "P")] += 1
    rows = []
    rows.append(r"\begin{tabular}{lrrr}")
    rows.append(r"\toprule")
    rows.append(r"Silo & $N$ & Faithful & Proxy \\")
    rows.append(r"\midrule")
    for silo in sorted(silos.keys()):
        d = silos[silo]
        silo_esc = silo.replace('_', r'\_')
        rows.append(rf"{silo_esc} & {d['N']} & {d['F']} & {d['P']} \\")
    rows.append(r"\midrule")
    tot = {"N": sum(d["N"] for d in silos.values()),
           "F": sum(d["F"] for d in silos.values()),
           "P": sum(d["P"] for d in silos.values())}
    rows.append(rf"Total & {tot['N']} & {tot['F']} & {tot['P']} \\")
    rows.append(r"\bottomrule")
    rows.append(r"\end{tabular}")
    return "\n".join(rows) + "\n"


def _figure_oracle_tax_box_csv(oracle: dict, cohort: dict) -> str:
    """CSV for box-plot of log10(tau_runtime) at H4 anchor cell, by profile."""
    import math
    table = oracle.get("table_faithful") or {}
    lines = ["profile,label,silo,log10_tau_runtime"]
    anchor_eps = "1e-04"
    for lid, by_cell in table.items():
        silo = (cohort["labels"].get(lid) or {}).get("silo", "unknown")
        for prof in PROFILES:
            v = (by_cell.get(f"{prof}|{anchor_eps}") or {}).get("runtime_seconds")
            if isinstance(v, (int, float)) and v > 0:
                lines.append(f"{prof},{lid},{silo},{math.log10(v):.6f}")
    return "\n".join(lines) + "\n"


def _figure_h4_sensitivity_csv(stats: dict) -> str:
    h4 = stats.get("H4") or {}
    sens = h4.get("sensitivity_tau_winners") or {}
    lines = ["tau_threshold,strict_H4_winners"]
    for k, v in sorted(sens.items(), key=lambda kv: float(kv[0].split("=")[1])):
        lines.append(f"{k.split('=')[1]},{v}")
    return "\n".join(lines) + "\n"


def _table_h1_full_matrix(evidence: dict) -> str:
    rows = []
    for row in (evidence.get("H1") or {}).get("rows") or []:
        rows.append([
            _profile_pretty(row.get("profile")),
            row.get("epsilon"),
            row.get("axis"),
            row.get("n"),
            _fmt_num(row.get("median_tau")),
            _fmt_num(row.get("median_log10_tau")),
            _fmt_p(row.get("p_one_sided_greater_holm")),
            _fmt_num(row.get("cliffs_delta_log10_tau_vs_1")),
            "yes" if row.get("accept_h1_triple") else "no",
        ])
    return _tex_table(
        [
            "Profile", r"$\varepsilon$", "Axis", r"$n$", r"median $\tau$",
            r"median $\log_{10}\tau$", r"Holm $p$", r"Cliff $\delta$", "H1 pass",
        ],
        rows,
        "lllrrrrrl",
    )


def _table_h1_resource_axis_summary(evidence: dict) -> str:
    h1 = evidence.get("H1") or {}
    accepted = h1.get("accepted_tests_by_axis") or {}
    tested = h1.get("tests_by_axis") or {}
    rows = [[axis, tested.get(axis), accepted.get(axis), "tau > 10 triple condition"] for axis in sorted(tested)]
    return _tex_table(["Resource axis", "Tests", "Accepted", "Acceptance rule"], rows, "lrrl")


def _table_h2_silo_effects(evidence: dict) -> str:
    rows = []
    for row in (evidence.get("H2") or {}).get("rows") or []:
        log_summary = row.get("log10_tau_runtime_summary") or {}
        rows.append([
            row.get("silo"),
            row.get("p3_scope"),
            row.get("n_labels_total"),
            row.get("n_faithful"),
            row.get("n_proxy"),
            row.get("n_anchor_observations"),
            _fmt_num(log_summary.get("median")),
            _fmt_num(log_summary.get("q1")),
            _fmt_num(log_summary.get("q3")),
            "yes" if row.get("included_in_kw") else "no",
        ])
    return _tex_table(
        ["Silo", "P3 scope", "$N$", "F", "P", "$n$ anchor", r"median $\log_{10}\tau$", "Q1", "Q3", "KW"],
        rows,
        "llrrrrrrrl",
    )


def _table_h2_mixedlm_icc(evidence: dict) -> str:
    h2 = evidence.get("H2") or {}
    kw = h2.get("kruskal_wallis") or {}
    mixed = h2.get("mixed_effects_sensitivity") or {}
    kw_n = kw.get("n_per_silo")
    included_silos = {
        row.get("silo")
        for row in (h2.get("rows") or [])
        if row.get("included_in_kw") and row.get("silo")
    }
    if isinstance(kw_n, dict) and included_silos:
        kw_n = {silo: kw_n[silo] for silo in sorted(included_silos) if silo in kw_n}
    rows = [
        ["Kruskal-Wallis", kw_n, _fmt_num(kw.get("kw_stat")), _fmt_p(kw.get("kw_p_value")), kw.get("accept_h2_overall")],
        ["MixedLM joint silo", mixed.get("n_rows"), "--", _fmt_p(mixed.get("joint_silo_wald_p_value")), mixed.get("reject_joint_at_0_05")],
        ["MixedLM label ICC", mixed.get("n_labels"), _fmt_num(mixed.get("icc_label")), "--", "sensitivity"],
    ]
    return _tex_table(["Analysis", "Effective N", "Statistic", "$p$", "Decision"], rows, "lllll")


def _table_h3_profile_ordering(evidence: dict) -> str:
    rows = [rf"\begin{{tabular}}{{lrrrr}}", r"\toprule"]
    rows.append(r"Profile & $n$ & median $\log_{10}\tau$ & Q1 & Q3 \\")
    rows.append(r"\midrule")
    for row in (evidence.get("H3") or {}).get("rows") or []:
        log_summary = row.get("log10_tau_runtime_summary") or {}
        rows.append(
            rf"{_profile_pretty(row.get('profile'))} & "
            rf"{_tex_escape(row.get('n_labels'))} & "
            rf"{_tex_escape(_fmt_num(log_summary.get('median')))} & "
            rf"{_tex_escape(_fmt_num(log_summary.get('q1')))} & "
            rf"{_tex_escape(_fmt_num(log_summary.get('q3')))} \\"
        )
    rows.append(r"\bottomrule")
    rows.append(r"\end{tabular}")
    return "\n".join(rows) + "\n"


def _table_h3_structural_invariants(evidence: dict) -> str:
    rows = []
    for axis, block in sorted(((evidence.get("H3") or {}).get("structural_invariants") or {}).items()):
        rows.append([axis, block.get("axis_invariant_by_construction"), block.get("reason")])
    return _tex_table(["Axis", "Invariant", "Reason"], rows, "lll")


def _table_h4_scoreboard(evidence: dict) -> str:
    rows = []
    for row in (evidence.get("H4") or {}).get("rows") or []:
        metrics = row.get("metrics") or {}
        rows.append([
            row.get("label"),
            row.get("silo"),
            row.get("faithfulness_tier"),
            row.get("n_criteria_passed"),
            "; ".join(row.get("failed_criteria") or []) or "none",
            row.get("failure_class"),
            _fmt_num(metrics.get("tau_runtime")),
            _fmt_num(metrics.get("full_t_count")),
            _fmt_num(metrics.get("tau_t_depth")),
        ])
    return _tex_table(
        ["Label", "Silo", "Tier", "Pass", "Failed criteria", "Class", r"$\tau_t$", "$T$ count", r"$\tau_{T_d}$"],
        rows,
        "lllrlllll",
    )


def _table_faithfulness_tiers(evidence: dict) -> str:
    tiers = evidence.get("faithfulness_tiers") or {}
    counts = tiers.get("counts") or {}
    labels_by_tier = tiers.get("labels_by_tier") or {}
    rows = []
    for tier in sorted(counts):
        rows.append([tier, counts.get(tier), ", ".join(labels_by_tier.get(tier) or [])])
    return _tex_table(["Tier", "$n$", "Labels"], rows, "lrl")


def _table_h4_qdk_nontriviality(evidence: dict) -> str:
    sens = ((evidence.get("H4") or {}).get("qdk_nontriviality_sensitivity") or {})
    rows = []
    for label, payload in sorted((sens.get("per_label") or {}).items()):
        metrics = (payload.get("metrics") or {}).get("qdk_magic") or {}
        rows.append([
            label,
            payload.get("passes_all"),
            "; ".join(payload.get("failed_criteria") or []) or "none",
            _fmt_num(metrics.get("delta_rotation_count")),
            _fmt_num(metrics.get("delta_rotation_depth")),
            _fmt_num(metrics.get("delta_num_tstates")),
        ])
    return _tex_table(
        ["Label", "Passes QDK-H4", "Failed criteria", r"$\Delta$ rotations", r"$\Delta$ rotation depth", r"$\Delta$ T states"],
        rows,
        "llllll",
    )


def _table_h4_failure_taxonomy(evidence: dict) -> str:
    h4 = evidence.get("H4") or {}
    taxonomy = h4.get("failure_taxonomy_counts") or {}
    criteria = h4.get("per_criterion_failure_counts") or {}
    rows = [["failure_class", key, value] for key, value in sorted(taxonomy.items())]
    rows.extend(["criterion_failure", key, value] for key, value in sorted(criteria.items()))
    return _tex_table(["Type", "Name", "Count"], rows, "llr")


def _h4_rows_by_label(evidence: dict) -> dict[str, dict]:
    return {
        row.get("label"): row
        for row in ((evidence.get("H4") or {}).get("rows") or [])
        if row.get("label")
    }


def _paper_exact_eligible(tier: object) -> bool:
    return tier == "paper-faithful-strict"


def _claim_scope(tier: object) -> str:
    if tier == "paper-faithful-strict":
        return "paper-exact implementation claims allowed"
    if tier == "paper-family-template":
        return "template/family-faithful only; not paper-exact"
    if tier == "proxy":
        return "proxy coverage/sensitivity only"
    return "unknown tier; do not use for paper-exact claims"


def _first_present(*values: object) -> object:
    for value in values:
        if value is not None:
            return value
    return None


def _circuit_fidelity_rows(cohort: dict, evidence: dict) -> list[dict]:
    h4_by_label = _h4_rows_by_label(evidence)
    rows = []
    for label, entry in sorted((cohort.get("labels") or {}).items()):
        tier = entry.get("faithfulness_tier")
        h4_row = h4_by_label.get(label)
        metrics = (h4_row or {}).get("metrics") or {}
        baseline = entry.get("classical_baseline") or {}
        baseline_provenance = baseline.get("_phase8b_provenance") or {}
        rows.append({
            "label": label,
            "paper_id": entry.get("paper_id"),
            "experiment_id": entry.get("experiment_id"),
            "silo": entry.get("silo"),
            "algorithm_family": entry.get("algorithm_family"),
            "fidelity": entry.get("fidelity"),
            "paper_fidelity": entry.get("paper_fidelity"),
            "faithfulness_tier": tier,
            "paper_exact_claim_eligible": _paper_exact_eligible(tier),
            "claim_scope": _claim_scope(tier),
            "phase8_runnable": entry.get("phase8_runnable"),
            "circuit_path": entry.get("circuit_path"),
            "circuit_sha256": entry.get("circuit_sha256"),
            "proxy_template": entry.get("proxy_template"),
            "proxy_justification_path": entry.get("proxy_justification_path"),
            "h4_evaluated": h4_row is not None,
            "h4_passes_all": (h4_row or {}).get("passes_all"),
            "h4_failure_class": (h4_row or {}).get("failure_class"),
            "h4_failed_criteria": ";".join((h4_row or {}).get("failed_criteria") or []),
            "h4_tau_runtime": metrics.get("tau_runtime"),
            "h4_full_t_count": metrics.get("full_t_count"),
            "h4_tau_t_depth": metrics.get("tau_t_depth"),
            "classical_baseline_scale_type": baseline.get("baseline_scale_type") or baseline_provenance.get("baseline_scale_type"),
            "headline_h4_baseline_eligible": _first_present(baseline.get("headline_h4_eligible"), baseline_provenance.get("headline_h4_eligible")),
        })
    return rows


def _table_circuit_fidelity(rows: list[dict]) -> str:
    body = []
    for row in rows:
        body.append([
            row.get("label"),
            row.get("silo"),
            row.get("fidelity"),
            row.get("faithfulness_tier"),
            "yes" if row.get("paper_exact_claim_eligible") else "no",
            "yes" if row.get("h4_evaluated") else "no",
            "yes" if row.get("h4_passes_all") else "no" if row.get("h4_evaluated") else "--",
        ])
    return _tex_table(["Label", "Silo", "F/P", "Tier", "Paper exact", "H4 row", "H4 pass"], body, "lllllll")


def _table_circuit_fidelity_summary(rows: list[dict]) -> str:
    tiers = sorted({row.get("faithfulness_tier") or "unknown" for row in rows})
    body = []
    for tier in tiers:
        tier_rows = [row for row in rows if (row.get("faithfulness_tier") or "unknown") == tier]
        body.append([
            tier,
            len(tier_rows),
            sum(1 for row in tier_rows if row.get("paper_exact_claim_eligible")),
            sum(1 for row in tier_rows if row.get("h4_evaluated")),
            sum(1 for row in tier_rows if row.get("h4_passes_all")),
            _claim_scope(tier),
        ])
    return _tex_table(["Tier", "$n$", "Paper exact", "H4 rows", "H4 pass", "Claim scope"], body, "lrrrrl")


def _circuit_fidelity_json(rows: list[dict]) -> str:
    counts = {
        "faithfulness_tier": {},
        "fidelity": {},
        "paper_exact_claim_eligible": {},
        "h4_evaluated": {},
        "h4_passes_all": {},
    }
    for row in rows:
        for key in counts:
            value = row.get(key)
            text = str(value)
            counts[key][text] = counts[key].get(text, 0) + 1
    payload = {
        "schema": "phase10_circuit_fidelity.1.0",
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "claim_boundary": {
            "paper_faithful_strict": "Required for paper-exact implementation claims; current count is zero.",
            "paper_family_template": "May support template/family-level methodology claims, not paper-exact literature benchmarking claims.",
            "proxy": "Coverage and sensitivity only; not H4 headline evidence.",
        },
        "counts": {key: dict(sorted(value.items())) for key, value in counts.items()},
        "rows": rows,
    }
    return json.dumps(payload, indent=2) + "\n"


def _table_claims_evidence_matrix(evidence: dict) -> str:
    rows = []
    for claim in evidence.get("claims_evidence_matrix") or []:
        rows.append([
            claim.get("claim_id"),
            claim.get("claim"),
            "; ".join(claim.get("primary_evidence") or []),
            claim.get("manuscript_use"),
        ])
    return _tex_table(["Claim ID", "Claim", "Primary evidence", "Manuscript use"], rows, "llll")


def _table_engine_failures(evidence: dict) -> str:
    failures = evidence.get("engine_failures") or {}
    rows = []
    for profile, counts in (failures.get("by_profile") or {}).items():
        rows.append([
            profile,
            counts.get("total"),
            counts.get("ok"),
            counts.get("engine_failure"),
            counts.get("other"),
        ])
    return _tex_table(["Profile", "Total", "OK", "Engine failure", "Other"], rows, "lrrrr")


def _table_experiment_regimes(evidence: dict) -> str:
    rows = []
    for regime in ((evidence.get("experiment_regimes") or {}).get("regimes") or []):
        rows.append([
            regime.get("regime_id"),
            regime.get("name"),
            regime.get("role"),
            "yes" if regime.get("included_in_headline_h1_h4") else "no",
            "yes" if regime.get("appendix_only") else "no",
            regime.get("separation_rule"),
        ])
    return _tex_table(
        ["Regime ID", "Name", "Role", "Headline H1-H4", "Appendix", "Boundary rule"],
        rows,
        "llllll",
    )


def _phase8d_regime(evidence: dict) -> dict:
    for regime in ((evidence.get("experiment_regimes") or {}).get("regimes") or []):
        if regime.get("regime_id") == "qae_hhl_fixed_precision_high_n":
            return regime
    return {}


def _table_phase8d_regime_summary(evidence: dict) -> str:
    phase8d = _phase8d_regime(evidence)
    rows = []
    for family in phase8d.get("families") or []:
        runtime = family.get("runtime_seconds_ok_summary") or {}
        physical = family.get("physical_qubits_ok_summary") or {}
        t_depth = family.get("t_depth_ok_summary") or {}
        rows.append([
            family.get("family"),
            family.get("n_records"),
            (family.get("by_status") or {}).get("ok", 0),
            (family.get("by_status") or {}).get("engine_failure", 0),
            ", ".join(str(v) for v in family.get("n_values") or []),
            ", ".join(str(v) for v in family.get("m_precision_qubits") or []),
            _fmt_num(runtime.get("median")),
            _fmt_num(physical.get("median")),
            _fmt_num(t_depth.get("median")),
        ])
    if not rows:
        rows.append(["not present", 0, 0, 0, "--", "--", "--", "--", "--"])
    return _tex_table(
        [
            "Family", "Records", "OK", "Engine fail", "$N$ values", "$m$ values",
            "Median runtime", "Median physical qubits", "Median T-depth",
        ],
        rows,
        "lrrrlllll",
    )


def _figure_h1_heatmap_csv(evidence: dict) -> str:
    rows = []
    for row in (evidence.get("H1") or {}).get("rows") or []:
        rows.append({
            "profile": row.get("profile"),
            "epsilon": row.get("epsilon"),
            "axis": row.get("axis"),
            "median_tau": row.get("median_tau"),
            "median_log10_tau": row.get("median_log10_tau"),
            "accept_h1_triple": row.get("accept_h1_triple"),
        })
    return _csv(rows, ["profile", "epsilon", "axis", "median_tau", "median_log10_tau", "accept_h1_triple"])


def _figure_h4_criterion_heatmap_csv(evidence: dict) -> str:
    rows = []
    for row in (evidence.get("H4") or {}).get("rows") or []:
        for criterion, passed in (row.get("criteria") or {}).items():
            rows.append({
                "label": row.get("label"),
                "silo": row.get("silo"),
                "criterion": criterion,
                "passed": int(bool(passed)),
                "failure_class": row.get("failure_class"),
            })
    return _csv(rows, ["label", "silo", "criterion", "passed", "failure_class"])


def _figure_h4_funnel_csv(evidence: dict) -> str:
    rows = []
    for index, row in enumerate((evidence.get("H4") or {}).get("criteria_funnel") or [], start=1):
        rows.append({
            "step": index,
            "criterion": row.get("criterion"),
            "n_remaining": row.get("n_remaining"),
            "labels_remaining": ";".join(row.get("labels_remaining") or []),
        })
    return _csv(rows, ["step", "criterion", "n_remaining", "labels_remaining"])


def _figure_h4_qdk_nontriviality_csv(evidence: dict) -> str:
    rows = []
    sens = ((evidence.get("H4") or {}).get("qdk_nontriviality_sensitivity") or {})
    for label, payload in sorted((sens.get("per_label") or {}).items()):
        metrics = (payload.get("metrics") or {}).get("qdk_magic") or {}
        rows.append({
            "label": label,
            "passes_qdk_h4": payload.get("passes_all"),
            "failed_criteria": ";".join(payload.get("failed_criteria") or []),
            "delta_t_count": metrics.get("delta_t_count"),
            "delta_rotation_count": metrics.get("delta_rotation_count"),
            "delta_rotation_depth": metrics.get("delta_rotation_depth"),
            "delta_num_tstates": metrics.get("delta_num_tstates"),
        })
    return _csv(
        rows,
        [
            "label", "passes_qdk_h4", "failed_criteria", "delta_t_count",
            "delta_rotation_count", "delta_rotation_depth", "delta_num_tstates",
        ],
    )


def _figure_regime_map_csv(evidence: dict) -> str:
    rows = []
    for regime in ((evidence.get("experiment_regimes") or {}).get("regimes") or []):
        rows.append({
            "regime_id": regime.get("regime_id"),
            "role": regime.get("role"),
            "included_in_headline_h1_h4": regime.get("included_in_headline_h1_h4"),
            "appendix_only": regime.get("appendix_only"),
            "source_phase": regime.get("source_phase"),
        })
    return _csv(rows, ["regime_id", "role", "included_in_headline_h1_h4", "appendix_only", "source_phase"])


def _figure_phase8d_scaling_csv(evidence: dict) -> str:
    phase8d = _phase8d_regime(evidence)
    rows = []
    for row in phase8d.get("scaling_rows") or []:
        rows.append({
            "family": row.get("family"),
            "entity_id": row.get("entity_id"),
            "n_value": row.get("n_value"),
            "m_precision_qubits": row.get("m_precision_qubits"),
            "hardware_profile": row.get("hardware_profile"),
            "epsilon": row.get("epsilon"),
            "status": row.get("status"),
            "runtime_seconds": row.get("runtime_seconds"),
            "physical_qubits": row.get("physical_qubits"),
            "t_depth": row.get("t_depth"),
            "t_count": row.get("t_count"),
            "reason": row.get("reason"),
        })
    return _csv(
        rows,
        [
            "family", "entity_id", "n_value", "m_precision_qubits", "hardware_profile",
            "epsilon", "status", "runtime_seconds", "physical_qubits", "t_depth",
            "t_count", "reason",
        ],
    )


def _results_brief(evidence: dict) -> str:
    h1 = evidence.get("H1") or {}
    h2 = evidence.get("H2") or {}
    h3 = evidence.get("H3") or {}
    h4 = evidence.get("H4") or {}
    failures = evidence.get("engine_failures") or {}
    kw = h2.get("kruskal_wallis") or {}
    mixed = h2.get("mixed_effects_sensitivity") or {}
    h3_test = h3.get("test_summary") or {}
    lines = [
        "# Phase 10 Results Brief",
        "",
        f"- Cohort: {evidence.get('cohort', {}).get('n_labels_total')} labels, "
        f"{evidence.get('cohort', {}).get('n_labels_faithful')} Faithful, "
        f"{evidence.get('cohort', {}).get('n_labels_proxy')} Proxy across "
        f"{evidence.get('cohort', {}).get('n_silos')} silos.",
        f"- Faithfulness tiers: {evidence.get('faithfulness_tiers', {}).get('counts')}. "
        "The legacy Faithful set is retained for preregistered continuity, but strict paper-faithful implementation evidence is reported separately.",
        f"- H1: accepted triple-condition tests by axis: {h1.get('accepted_tests_by_axis')}. "
        f"Runtime median tau range: {h1.get('runtime_median_tau_range')}; interpret as template/full-vs-bare overhead, not paper-exact oracle scaling.",
        f"- H2: active-P3-silo Kruskal-Wallis p={_fmt_p(kw.get('kw_p_value'))}; "
        f"MixedLM joint silo p={_fmt_p(mixed.get('joint_silo_wald_p_value'))}; "
        f"label ICC={_fmt_num(mixed.get('icc_label'))}.",
        f"- H3: Friedman p={_fmt_p(h3_test.get('friedman_p_value'))}, "
        f"Kendall W={_fmt_num(h3_test.get('kendalls_w'))}; "
        "non-runtime axes are structural invariants under the estimator model.",
        f"- H4: strict winners={h4.get('canonical_winners_count')}; "
        f"bifurcation holds={h4.get('bifurcation_holds')}; "
        f"failure classes={h4.get('failure_taxonomy_counts')}; "
        f"QDK-aware nontriviality sensitivity winners={((h4.get('qdk_nontriviality_sensitivity') or {}).get('canonical_winners_count'))}.",
        f"- Engine failures: {(failures.get('status_counts') or {}).get('engine_failure')} "
        f"of {failures.get('total_records')} canonical Phase 8 records.",
        "- Regimes: headline H1-H4 uses only `canonical_s2_backed_label_grid`; "
        "`qae_hhl_fixed_precision_high_n` is appendix-only fixed-precision HHL/QAE scaling evidence.",
    ]
    return "\n".join(lines) + "\n"


def _discussion_claims(evidence: dict) -> str:
    lines = ["# Discussion Claims Evidence Matrix", ""]
    for claim in evidence.get("claims_evidence_matrix") or []:
        lines.append(f"## {claim.get('claim_id')}")
        lines.append(str(claim.get("claim")))
        lines.append("")
        lines.append("Evidence: " + "; ".join(claim.get("primary_evidence") or []))
        lines.append("Use: " + str(claim.get("manuscript_use")))
        lines.append("")
    return "\n".join(lines)


def _caption_pack(evidence: dict) -> str:
    captions = [
        ("table_experiment_regimes.tex", "Boundary table separating the headline canonical H1-H4 grid from the appendix-only HHL/QAE fixed-precision scout."),
        ("table_phase8d_regime_summary.tex", "Family-level HHL/QAE fixed-precision scout summary by status and resource scale."),
        ("table_circuit_fidelity.tex", "Label-level implementation-fidelity ledger separating paper-exact, template/family, and proxy claim scopes."),
        ("table_circuit_fidelity_summary.tex", "Faithfulness-tier summary showing that the current strict paper-exact tier is empty."),
        ("table_faithfulness_tiers.tex", "Faithfulness tier counts separating strict paper-faithful from family/template-faithful evidence."),
        ("table_h1_full_matrix.tex", "Full H1 test matrix by hardware profile, synthesis epsilon, and resource axis."),
        ("table_h2_silo_effects.tex", "Anchor-cell silo comparison with explicit Faithful effective sample sizes."),
        ("table_h3_profile_ordering.tex", "Runtime oracle-tax ordering across hardware profiles at epsilon=1e-4."),
        ("table_h4_scoreboard.tex", "Per-label strict-H4 criteria scoreboard at the canonical anchor cell."),
        ("table_h4_qdk_nontriviality.tex", "Sensitivity table replacing H4 C3 logical T-count with a QDK-aware magic-state delta check."),
        ("figure_h1_heatmap.csv", "Heatmap source data for H1 median log10 oracle tax."),
        ("figure_h4_funnel.csv", "Sequential strict-H4 criterion funnel showing how the Faithful cohort empties."),
        ("figure_phase8d_scaling.csv", "Source data for appendix plots of fixed-precision HHL/QAE resource scaling."),
    ]
    lines = ["# Caption Pack", ""]
    for name, caption in captions:
        lines.append(f"- `{name}`: {caption}")
    lines.append("")
    lines.append(f"Generated from evidence schema `{evidence.get('schema')}`.")
    return "\n".join(lines) + "\n"


def _key_numbers(cohort: dict, stats: dict, evidence: dict) -> dict:
    h4 = stats.get("H4") or {}
    p1 = (cohort.get("_phase_status") or {}).get("phase1") or {}
    p3 = (cohort.get("_phase_status") or {}).get("phase3") or {}
    p4 = (cohort.get("_phase_status") or {}).get("phase4") or {}
    p8 = (cohort.get("_phase_status") or {}).get("phase8") or {}
    fidelity_counts: dict[str, int] = {}
    silo_counts: dict[str, int] = {}
    for e in cohort["labels"].values():
        fidelity_counts[e.get("fidelity", "?")] = fidelity_counts.get(e.get("fidelity", "?"), 0) + 1
        silo_counts[e.get("silo", "?")] = silo_counts.get(e.get("silo", "?"), 0) + 1
    h1_e = evidence.get("H1") or {}
    h2_e = evidence.get("H2") or {}
    h3_e = evidence.get("H3") or {}
    h4_e = evidence.get("H4") or {}
    failure_e = evidence.get("engine_failures") or {}
    regimes = evidence.get("experiment_regimes") or {}
    circuit_fidelity_rows = _circuit_fidelity_rows(cohort, evidence)
    return {
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "n_labels_total": len(cohort["labels"]),
        "n_labels_faithful": fidelity_counts.get("F", 0),
        "n_labels_proxy": fidelity_counts.get("P", 0),
        "faithfulness_tier_counts": (evidence.get("faithfulness_tiers") or {}).get("counts"),
        "faithfulness_tier_labels": (evidence.get("faithfulness_tiers") or {}).get("labels_by_tier"),
        "circuit_fidelity_counts": {
            "paper_exact_claim_eligible": sum(1 for row in circuit_fidelity_rows if row.get("paper_exact_claim_eligible")),
            "h4_evaluated": sum(1 for row in circuit_fidelity_rows if row.get("h4_evaluated")),
            "h4_passes_all": sum(1 for row in circuit_fidelity_rows if row.get("h4_passes_all")),
        },
        "n_silos": len(silo_counts),
        "silo_counts": silo_counts,
        "n_records_phase8": (p8.get("results_breakdown") or {}).get("total_records"),
        "n_engine_failures_phase8": (p8.get("results_breakdown") or {}).get("engine_failure"),
        "h4_canonical_winners_count": h4.get("canonical_winners_count"),
        "h4_canonical_winners": h4.get("canonical_winners"),
        "h4_bifurcation_holds": h4.get("bifurcation_holds"),
        "h4_qdk_nontriviality_winners_count": ((h4.get("qdk_nontriviality_sensitivity") or {}).get("canonical_winners_count")),
        "h4_faithfulness_tier_sensitivity": h4.get("faithfulness_tier_sensitivity"),
        "h1_accepted_tests_by_axis": h1_e.get("accepted_tests_by_axis"),
        "h1_runtime_median_tau_range": h1_e.get("runtime_median_tau_range"),
        "h2_kw_p_value": ((h2_e.get("kruskal_wallis") or {}).get("kw_p_value")),
        "h2_scope_rule": ((h2_e.get("kruskal_wallis") or {}).get("scope_rule")),
        "h2_silos_in_test": ((h2_e.get("kruskal_wallis") or {}).get("silos_in_test")),
        "h2_n_excluded_out_of_p3_scope": ((h2_e.get("kruskal_wallis") or {}).get("n_excluded_out_of_p3_scope")),
        "h2_mixedlm_joint_silo_p_value": ((h2_e.get("mixed_effects_sensitivity") or {}).get("joint_silo_wald_p_value")),
        "h2_mixedlm_label_icc": ((h2_e.get("mixed_effects_sensitivity") or {}).get("icc_label")),
        "h3_friedman_p_value": ((h3_e.get("test_summary") or {}).get("friedman_p_value")),
        "h3_kendalls_w": ((h3_e.get("test_summary") or {}).get("kendalls_w")),
        "h3_profile_order_by_median_log10_tau": h3_e.get("profile_order_by_median_log10_tau"),
        "h4_failure_taxonomy_counts": h4_e.get("failure_taxonomy_counts"),
        "h4_per_criterion_failure_counts": h4_e.get("per_criterion_failure_counts"),
        "phase8_engine_failure_status_counts": failure_e.get("status_counts"),
        "claims_evidence_count": len(evidence.get("claims_evidence_matrix") or []),
        "experiment_regime_ids": [r.get("regime_id") for r in regimes.get("regimes") or []],
        "headline_regime_id": regimes.get("headline_regime_id"),
        "appendix_regime_ids": regimes.get("appendix_regime_ids"),
        "phase8d_regime_by_status": (_phase8d_regime(evidence).get("by_status") or {}),
    }


def main() -> int:
    cohort = _read(COHORT)
    stats = _read(STATS)
    oracle = _read(ORACLE)
    _ = _read(SENSITIVITY)  # presence-only check
    evidence = _read(EVIDENCE)
    circuit_fidelity_rows = _circuit_fidelity_rows(cohort, evidence)

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    print(f"[Phase 10] generating manuscript artifacts in {OUT_DIR.relative_to(ROOT)}/")

    _write(OUT_DIR / "key_numbers.json", json.dumps(_key_numbers(cohort, stats, evidence), indent=2))
    _write(OUT_DIR / "table_h4_anchor.tex", _table_h4_anchor(stats))
    _write(OUT_DIR / "table_h1_summary.tex", _table_h1_summary(stats))
    _write(OUT_DIR / "table_silo_breakdown.tex", _table_silo_breakdown(cohort))
    _write(OUT_DIR / "figure_oracle_tax_box.csv", _figure_oracle_tax_box_csv(oracle, cohort))
    _write(OUT_DIR / "figure_h4_sensitivity.csv", _figure_h4_sensitivity_csv(stats))
    _write(OUT_DIR / "table_h1_full_matrix.tex", _table_h1_full_matrix(evidence))
    _write(OUT_DIR / "table_h1_resource_axis_summary.tex", _table_h1_resource_axis_summary(evidence))
    _write(OUT_DIR / "table_h2_silo_effects.tex", _table_h2_silo_effects(evidence))
    _write(OUT_DIR / "table_h2_mixedlm_icc.tex", _table_h2_mixedlm_icc(evidence))
    _write(OUT_DIR / "table_h3_profile_ordering.tex", _table_h3_profile_ordering(evidence))
    _write(OUT_DIR / "table_h3_structural_invariants.tex", _table_h3_structural_invariants(evidence))
    _write(OUT_DIR / "table_faithfulness_tiers.tex", _table_faithfulness_tiers(evidence))
    _write(OUT_DIR / "table_h4_scoreboard.tex", _table_h4_scoreboard(evidence))
    _write(OUT_DIR / "table_circuit_fidelity.tex", _table_circuit_fidelity(circuit_fidelity_rows))
    _write(OUT_DIR / "table_circuit_fidelity_summary.tex", _table_circuit_fidelity_summary(circuit_fidelity_rows))
    _write(OUT_DIR / "circuit_fidelity.csv", _csv(circuit_fidelity_rows, [
        "label", "paper_id", "experiment_id", "silo", "algorithm_family", "fidelity",
        "paper_fidelity", "faithfulness_tier", "paper_exact_claim_eligible", "claim_scope",
        "phase8_runnable", "h4_evaluated", "h4_passes_all", "h4_failure_class",
        "h4_failed_criteria", "h4_tau_runtime", "h4_full_t_count", "h4_tau_t_depth",
        "classical_baseline_scale_type", "headline_h4_baseline_eligible",
        "proxy_template", "circuit_path", "proxy_justification_path", "circuit_sha256",
    ]))
    _write(OUT_DIR / "circuit_fidelity.json", _circuit_fidelity_json(circuit_fidelity_rows))
    _write(OUT_DIR / "table_h4_qdk_nontriviality.tex", _table_h4_qdk_nontriviality(evidence))
    _write(OUT_DIR / "table_h4_failure_taxonomy.tex", _table_h4_failure_taxonomy(evidence))
    _write(OUT_DIR / "table_claims_evidence_matrix.tex", _table_claims_evidence_matrix(evidence))
    _write(OUT_DIR / "table_engine_failures.tex", _table_engine_failures(evidence))
    _write(OUT_DIR / "table_experiment_regimes.tex", _table_experiment_regimes(evidence))
    _write(OUT_DIR / "table_phase8d_regime_summary.tex", _table_phase8d_regime_summary(evidence))
    _write(OUT_DIR / "claims_evidence_matrix.json", json.dumps(evidence.get("claims_evidence_matrix") or [], indent=2))
    _write(OUT_DIR / "figure_h1_heatmap.csv", _figure_h1_heatmap_csv(evidence))
    _write(OUT_DIR / "figure_h4_criterion_heatmap.csv", _figure_h4_criterion_heatmap_csv(evidence))
    _write(OUT_DIR / "figure_h4_funnel.csv", _figure_h4_funnel_csv(evidence))
    _write(OUT_DIR / "figure_h4_qdk_nontriviality.csv", _figure_h4_qdk_nontriviality_csv(evidence))
    _write(OUT_DIR / "figure_regime_map.csv", _figure_regime_map_csv(evidence))
    _write(OUT_DIR / "figure_phase8d_scaling.csv", _figure_phase8d_scaling_csv(evidence))
    _write(OUT_DIR / "results_brief.md", _results_brief(evidence))
    _write(OUT_DIR / "discussion_claims.md", _discussion_claims(evidence))
    _write(OUT_DIR / "caption_pack.md", _caption_pack(evidence))

    print("[Phase 10] rendered figure files are excluded from the P4 handoff; "
          "figure source data remain in manuscript_artifacts/*.csv")

    ps = cohort.get("_phase_status") or {}
    ps["phase10"] = {
        "status": "complete",
        "completed_utc": datetime.now(timezone.utc).isoformat(),
        "artifacts_dir": str(OUT_DIR.relative_to(ROOT)).replace("\\", "/"),
    }
    cohort["_phase_status"] = ps
    COHORT.write_text(json.dumps(cohort, indent=2), encoding="utf-8")

    _emit_phase8d_block_if_ready()
    return 0


def _emit_phase8d_block_if_ready() -> None:
    """If Phase 8d ran, additively merge scout numbers into key_numbers.json.

    Idempotent and additive: never mutates existing key_numbers entries.
    Headline excludes Phase 8d (appendix-only).
    """
    scout_dir = OUTPUTS / "phase08d_qae_hhl_scout"
    summary_path = scout_dir / "summary.json"
    status_path = scout_dir / "phase8d_status.json"
    if not summary_path.exists():
        print("[phase10] Phase 8d QAE/HHL scout not present yet; skipping Phase 8d wiring.")
        return
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    status = json.loads(status_path.read_text(encoding="utf-8")) if status_path.exists() else {}
    rows = summary.get("rows") or []
    profiles = sorted({r.get("hardware_profile") for r in rows if r.get("hardware_profile")})
    n_values = sorted({r.get("n_value") for r in rows if isinstance(r.get("n_value"), int)})
    m_values = sorted({r.get("m_precision_qubits") for r in rows if isinstance(r.get("m_precision_qubits"), int)})
    families = sorted({r.get("family") for r in rows if r.get("family")})
    kn_path = OUT_DIR / "key_numbers.json"
    kn = json.loads(kn_path.read_text(encoding="utf-8")) if kn_path.exists() else {}
    kn["phase8d_qae_hhl"] = {
        "appendix_only": True,
        "headline_excludes_phase8d": True,
        "track": "qae_hhl_fixed_precision_high_n",
        "stage": status.get("stage"),
        "n_records": summary.get("n_records"),
        "expected_records": status.get("expected_records"),
        "by_status": summary.get("by_status") or {},
        "n_values": n_values,
        "m_precision_qubits": m_values,
        "hardware_profiles": profiles,
        "families": families,
        "problem_size_decoupled_from_precision": True,
    }
    kn_path.write_text(json.dumps(kn, indent=2), encoding="utf-8")
    print("[phase10] Phase 8d QAE/HHL scout numbers merged into key_numbers.json")


if __name__ == "__main__":
    raise SystemExit(main())
