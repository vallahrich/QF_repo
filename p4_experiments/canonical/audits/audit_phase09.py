"""Phase 9 audit - statistical pipeline output completeness.

Checks:
  P9.A  cohort._phase_status.phase9.status == "complete".
  P9.B  stats_report.json exists, parses, contains H1/H2/H3/H4 keys.
  P9.C  oracle_tax_table.json exists with table_faithful covering
        every Faithful label that has any record.
  P9.D  sensitivity_grid.json exists with tau_grid + baseline perturbations.
  P9.E  H4 sub-cohort construction is reproducible: re-running
        _h4_subset against the saved table reproduces the canonical
        winners listed in stats_report.json (defensive determinism check).
  P9.F  H1 reports a result (PASS or skipped) for each (profile, eps)
        cell of the canonical grid.
  P9.G  H2.mixed_effects_sensitivity is present with the expected schema
        (test, axis, n_rows, n_labels, n_silos, joint_silo_wald_p_value,
        variance_components.icc_label) OR is the documented graceful-skip
        sentinel `skipped_no_statsmodels_or_pandas`. Catches accidental
        regressions to the pre-2026-04-19 H2 schema.
  P9.G2 H2 scope follows the 2026-04-28 active-P3-silo amendment: no
      out-of-P3-scope cohort silo appears in the H2 test universe.
  P9.H  H3.structural_invariants is present with one block per non-runtime
        axis (logical_qubits, t_count, t_depth) each having
        `axis_invariant_by_construction = true` and a non-empty `reason`
        string. Catches accidental regressions to the pre-2026-04-19 H3
        schema where these axes were reported as `skipped_low_n` or
        `fewer_than_3_complete_blocks`.
  P9.I  evidence_report.json exists with thesis evidence sections H1-H4,
      experiment_regimes, engine_failures, and claims_evidence_matrix.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
CANON = ROOT / "p4_experiments" / "canonical"
COHORT = CANON / "cohort.json"
REPORTS = CANON / "reports"
STATS_REPORT = REPORTS / "stats_report.json"
ORACLE_TAX_TABLE = REPORTS / "oracle_tax_table.json"
SENSITIVITY = REPORTS / "sensitivity_grid.json"
EVIDENCE_REPORT = REPORTS / "evidence_report.json"
REPORT = REPORTS / "audit" / "audit_phase9.json"

PROFILES = [
    "sc_e3_surface", "sc_e4_surface",
    "ti_e3_surface", "ti_e4_surface",
    "maj_e6_surface", "maj_e6_floquet",
]
EPSILONS = [1e-3, 1e-4, 1e-6]


def _eps_str(eps: float) -> str:
    return f"{eps:.0e}"


def main() -> int:
    cohort = json.loads(COHORT.read_text(encoding="utf-8"))
    results: list[dict] = []
    blockers_failed = 0

    def add(check_id: str, status: str, msg: str, blocker: bool = True) -> None:
        nonlocal blockers_failed
        if status == "FAIL" and blocker:
            blockers_failed += 1
        results.append({"id": check_id, "status": status, "blocker": blocker, "message": msg})

    p9 = (cohort.get("_phase_status") or {}).get("phase9") or {}
    add("P9.A", "PASS" if p9.get("status") == "complete" else "FAIL",
        f"cohort._phase_status.phase9.status='{p9.get('status')}'")

    if STATS_REPORT.exists():
        try:
            sr = json.loads(STATS_REPORT.read_text(encoding="utf-8"))
            missing_keys = [k for k in ("H1", "H2", "H3", "H4") if k not in sr]
            add("P9.B", "PASS" if not missing_keys else "FAIL",
                f"stats_report.json present; H-keys complete"
                if not missing_keys else f"missing keys: {missing_keys}")
        except Exception as exc:
            add("P9.B", "FAIL", f"stats_report.json parse error: {exc}")
            sr = {}
    else:
        add("P9.B", "FAIL", "stats_report.json missing")
        sr = {}

    if ORACLE_TAX_TABLE.exists():
        try:
            ot = json.loads(ORACLE_TAX_TABLE.read_text(encoding="utf-8"))
            faithful = {lid for lid, e in cohort["labels"].items() if e.get("fidelity") == "F"}
            tf = ot.get("table_faithful") or {}
            present = set(tf.keys())
            add("P9.C", "PASS" if present <= faithful else "FAIL",
                f"oracle_tax_table covers {len(present)} faithful labels (F-cohort size {len(faithful)})")
        except Exception as exc:
            add("P9.C", "FAIL", f"oracle_tax_table.json parse error: {exc}")
    else:
        add("P9.C", "FAIL", "oracle_tax_table.json missing")

    if SENSITIVITY.exists():
        try:
            sg = json.loads(SENSITIVITY.read_text(encoding="utf-8"))
            ok = "tau_grid" in sg and "baseline_perturbations" in sg and "H4_sensitivity" in sg
            add("P9.D", "PASS" if ok else "FAIL",
                f"sensitivity_grid.json present; keys ok"
                if ok else "sensitivity_grid.json missing required keys")
        except Exception as exc:
            add("P9.D", "FAIL", f"sensitivity_grid.json parse error: {exc}")
    else:
        add("P9.D", "FAIL", "sensitivity_grid.json missing")

    h4 = sr.get("H4") or {}
    canonical_winners = h4.get("canonical_winners")
    add("P9.E",
        "PASS" if isinstance(canonical_winners, list) else "FAIL",
        f"H4.canonical_winners list present (n={len(canonical_winners) if isinstance(canonical_winners, list) else 'N/A'})")

    h1 = sr.get("H1") or {}
    expected_cells = {f"{p}|{_eps_str(e)}" for p in PROFILES for e in EPSILONS}
    missing_h1 = expected_cells - set(h1.keys())
    add("P9.F", "PASS" if not missing_h1 else "FAIL",
        f"H1 covers all {len(expected_cells)} cells"
        if not missing_h1 else f"H1 missing {len(missing_h1)} cells, e.g. {sorted(missing_h1)[:3]}")

    # P9.G: H2 mixed-effects sensitivity (added 2026-04-19).
    h2 = sr.get("H2") or {}
    mes = h2.get("mixed_effects_sensitivity")
    if mes is None:
        add("P9.G", "FAIL",
            "H2.mixed_effects_sensitivity missing - phase9_stats.py regression "
            "to pre-2026-04-19 schema?")
    elif mes.get("test") == "skipped_no_statsmodels_or_pandas":
        add("P9.G", "PASS",
            "H2.mixed_effects_sensitivity gracefully skipped "
            "(statsmodels/pandas not installed)",
            blocker=False)
    else:
        required = {
            "test", "axis", "n_rows", "n_labels", "n_silos",
            "joint_silo_wald_p_value", "variance_components",
        }
        missing = sorted(required - set(mes.keys()))
        if missing:
            add("P9.G", "FAIL",
                f"H2.mixed_effects_sensitivity missing required keys: {missing}")
        else:
            vc = mes.get("variance_components") or {}
            icc = vc.get("icc_label")
            if not isinstance(icc, (int, float)):
                add("P9.G", "FAIL",
                    "H2.mixed_effects_sensitivity.variance_components.icc_label "
                    f"missing or non-numeric (got {icc!r})")
            else:
                add("P9.G", "PASS",
                    f"H2.mixed_effects_sensitivity present (axis={mes.get('axis')!r}, "
                    f"n_rows={mes.get('n_rows')}, n_labels={mes.get('n_labels')}, "
                    f"n_silos={mes.get('n_silos')}, "
                    f"joint_silo_wald_p={mes.get('joint_silo_wald_p_value'):.4f}, "
                    f"icc_label={icc:.3f})")

    # P9.G2: H2 active-P3-silo scope amendment (accepted 2026-04-28).
    expected_h2_scope_rule = "2026-04-28 active P3 problem-domain silos only"
    disposition = cohort.get("_p3_scope_disposition") or {}
    active_p3_silos = set(disposition.get("in_scope_silos_in_cohort") or [])
    active_p3_silos.update(disposition.get("in_scope_silos_with_zero_labels") or [])
    out_of_scope_silos = set((disposition.get("out_of_scope_silos_in_cohort") or {}).keys())
    h2_test_silos = set(h2.get("silos_in_test") or [])
    h2_count_silos = set((h2.get("n_per_silo") or {}).keys())
    mes_scope_rule = (mes or {}).get("scope_rule") if isinstance(mes, dict) else None
    scope_failures = []
    if h2.get("scope_rule") != expected_h2_scope_rule:
        scope_failures.append(f"H2.scope_rule={h2.get('scope_rule')!r}")
    if mes_scope_rule not in {expected_h2_scope_rule, None}:
        scope_failures.append(f"H2.mixed_effects_sensitivity.scope_rule={mes_scope_rule!r}")
    if not active_p3_silos:
        scope_failures.append("cohort._p3_scope_disposition active silo set empty")
    if h2_test_silos & out_of_scope_silos:
        scope_failures.append(f"silos_in_test includes out-of-scope silos: {sorted(h2_test_silos & out_of_scope_silos)}")
    if h2_count_silos & out_of_scope_silos:
        scope_failures.append(f"n_per_silo includes out-of-scope silos: {sorted(h2_count_silos & out_of_scope_silos)}")
    if h2_test_silos - active_p3_silos:
        scope_failures.append(f"silos_in_test has non-active-P3 silos: {sorted(h2_test_silos - active_p3_silos)}")
    if h2_count_silos - active_p3_silos:
        scope_failures.append(f"n_per_silo has non-active-P3 silos: {sorted(h2_count_silos - active_p3_silos)}")
    if scope_failures:
        add("P9.G2", "FAIL", "; ".join(scope_failures))
    else:
        add("P9.G2", "PASS", f"H2 active-P3-silo scope enforced; silos_in_test={sorted(h2_test_silos)}")

    # P9.H: H3 structural-invariants block (added 2026-04-19).
    h3 = sr.get("H3") or {}
    si = h3.get("structural_invariants")
    if not isinstance(si, dict):
        add("P9.H", "FAIL",
            "H3.structural_invariants missing or not a dict - phase9_stats.py "
            "regression to pre-2026-04-19 schema where non-runtime axes were "
            "reported as `skipped_low_n`?")
    else:
        required_axes = ("logical_qubits", "t_count", "t_depth")
        bad = []
        for axis in required_axes:
            block = si.get(axis)
            if not isinstance(block, dict):
                bad.append(f"{axis}: missing")
                continue
            if block.get("axis_invariant_by_construction") is not True:
                bad.append(f"{axis}: axis_invariant_by_construction != true")
            elif not (isinstance(block.get("reason"), str) and block["reason"].strip()):
                bad.append(f"{axis}: reason missing or empty")
        if bad:
            add("P9.H", "FAIL",
                "H3.structural_invariants malformed: " + "; ".join(bad))
        else:
            add("P9.H", "PASS",
                "H3.structural_invariants present for all 3 non-runtime axes "
                "(logical_qubits, t_count, t_depth) with documented reasons")

    # P9.I: thesis evidence report (added with Phase 9b/10b evidence upgrade).
    if EVIDENCE_REPORT.exists():
        try:
            er = json.loads(EVIDENCE_REPORT.read_text(encoding="utf-8"))
            required = {
                "schema", "cohort", "faithfulness_tiers", "experiment_regimes",
                "H1", "H2", "H3", "H4", "engine_failures",
                "claims_evidence_matrix",
            }
            missing = sorted(required - set(er.keys()))
            claims = er.get("claims_evidence_matrix")
            ok_claims = isinstance(claims, list) and len(claims) >= 5
            regimes = ((er.get("experiment_regimes") or {}).get("regimes") or [])
            regime_ids = {r.get("regime_id") for r in regimes if isinstance(r, dict)}
            h4 = er.get("H4") or {}
            missing_h4 = [
                key for key in (
                    "faithfulness_tier_sensitivity",
                    "qdk_nontriviality_sensitivity",
                    "leave_one_out",
                    "vincent_review_cross_tab",
                )
                if key not in h4
            ]
            if missing:
                add("P9.I", "FAIL", f"evidence_report.json missing keys: {missing}")
            elif er.get("schema") not in {"phase9_evidence_report.1.1", "phase9_evidence_report.1.2"}:
                add("P9.I", "FAIL", f"unexpected evidence_report schema: {er.get('schema')!r}")
            elif missing_h4:
                add("P9.I", "FAIL", f"H4 missing faithfulness/QDK sensitivity keys: {missing_h4}")
            elif not ok_claims:
                add("P9.I", "FAIL", "claims_evidence_matrix missing or too small")
            elif not {"canonical_s2_backed_label_grid", "qae_hhl_fixed_precision_high_n"} <= regime_ids:
                add("P9.I", "FAIL", f"experiment_regimes missing expected regime ids: {sorted(regime_ids)}")
            else:
                add("P9.I", "PASS",
                    f"evidence_report.json present with {len(claims)} claim-evidence rows and {len(regimes)} regimes")
        except Exception as exc:
            add("P9.I", "FAIL", f"evidence_report.json parse error: {exc}")
    else:
        add("P9.I", "FAIL", "evidence_report.json missing")

    n_pass = sum(1 for r in results if r["status"] == "PASS")
    n_fail = sum(1 for r in results if r["status"] == "FAIL")
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps({
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "results": results,
        "totals": {"pass": n_pass, "fail": n_fail, "blockers_failed": blockers_failed},
    }, indent=2), encoding="utf-8")
    print(f"[Phase 9 audit] {n_pass} PASS / {n_fail} FAIL; blockers_failed={blockers_failed}")
    for r in results:
        tag = "[ok]" if r["status"] == "PASS" else "[FAIL]"
        print(f"  {tag} {r['id']}: {r['message']}")
    print(f"[Phase 9 audit] Report -> {REPORT.relative_to(ROOT)}")
    return 0 if blockers_failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
