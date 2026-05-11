"""Dalzell et al. (2023) quantum advantage assessment.

Compares each experiment's reported logical qubits and T-count against the
per-silo Minimum Scale for Advantage (MSA) derived from the end-to-end
resource estimates in Dalzell's 337-page survey.

Usage:
    python -m p3_thematic_synthesis.s3_quantum_advantage.dalzell_2023.assess_dalzell
    python -m p3_thematic_synthesis.s3_quantum_advantage.dalzell_2023.assess_dalzell --silo derivative-pricing
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from .._shared import (
    build_output_payload,
    compute_maturity_level,
    estimate_oracle_complexity,
    get_derived,
    iter_experiments,
    load_derived_fields,
    make_verdict,
    print_summary,
    save_payload,
)

FRAMEWORK_ID = "dalzell_2023"
_MODULE_ROOT = Path(__file__).resolve().parent
THRESHOLDS_PATH = _MODULE_ROOT / "dalzell_thresholds.json"
OUTPUT_PATH = _MODULE_ROOT / "results" / "dalzell_results.json"


# Map extraction-file silo names → Dalzell threshold keys
_SILO_ALIASES: dict[str, str] = {
    "PD-01": "portfolio-optimization",
    "PD-02": "derivative-pricing",
    "PD-03": "risk-management",
    "PD-04": "quantum-ml-finance",
    "PD-05": "fraud-detection",
    "PD-06": "trading-execution",
    "PD-07": "credit-lending",
    "PD-08": "cryptography-security",
    "PD-09": "simulation-monte-carlo",
    "PD-10": "insurance-actuarial",
    # Pass-through for already-normalised names
    "portfolio-optimization": "portfolio-optimization",
    "derivative-pricing": "derivative-pricing",
    "risk-management": "risk-management",
    "quantum-ml-finance": "quantum-ml-finance",
    "fraud-detection": "fraud-detection",
    "trading-execution": "trading-execution",
    "credit-lending": "credit-lending",
    "cryptography-security": "cryptography-security",
    "simulation-monte-carlo": "simulation-monte-carlo",
    "insurance-actuarial": "insurance-actuarial",
}


def load_thresholds() -> dict:
    return json.loads(THRESHOLDS_PATH.read_text(encoding="utf-8"))


def _get_silo_thresholds(silo: str, thresholds: dict) -> dict | None:
    """Return per-silo thresholds or None if Dalzell has no data for this silo."""
    key = _SILO_ALIASES.get(silo, silo)
    return thresholds.get("silo_thresholds", {}).get(key)


def _read_resources(experiment: dict, derived: dict | None) -> tuple[int | None, int | None, int | None]:
    """Extract (logical_qubits, T-count, T-depth) from extraction + derived fields.

    T-depth falls back to circuit_depth as a conservative upper-bound proxy
    when the extraction reports circuit depth but not T-depth explicitly.
    """
    qr = experiment.get("quantum_resources") or {}

    # Logical qubits
    qubits = qr.get("num_qubits")
    if not isinstance(qubits, (int, float)) or qubits <= 0:
        qubits = None
    else:
        qubits = int(qubits)

    # T-count (prefer explicit; fall back to oracle_complexity_M)
    t_count: int | None = None
    tc = qr.get("t_count")
    if isinstance(tc, (int, float)) and tc > 0:
        t_count = int(tc)
    else:
        oracle_M, _op_type = estimate_oracle_complexity(experiment, derived)
        if oracle_M is not None and oracle_M > 0:
            t_count = oracle_M

    # T-depth (prefer explicit; fall back to circuit_depth proxy)
    t_depth: int | None = None
    td = qr.get("t_depth")
    if isinstance(td, (int, float)) and td > 0:
        t_depth = int(td)
    else:
        cd = qr.get("circuit_depth")
        if isinstance(cd, (int, float)) and cd > 0:
            t_depth = int(cd)

    return qubits, t_count, t_depth


def _assess_one(
    experiment: dict, silo: str, thresholds: dict, derived: dict | None
) -> tuple[str, str, dict]:
    st = _get_silo_thresholds(silo, thresholds)

    extras: dict = {
        "silo_analyzed_in_dalzell": st is not None,
    }

    if st is None:
        extras["reason"] = f"Silo '{silo}' not covered by Dalzell survey"
        return "not_applicable", extras["reason"], extras

    # Check for explicitly infeasible silo (e.g., portfolio-optimization QIPM).
    # FIX 2026-05-02 (QA-5 open-blocker): the `is_infeasible` flag in
    # dalzell_thresholds.json for portfolio-optimization is derived from
    # Dalzell's QIPM (quantum interior-point method) end-to-end estimates.
    # Previously this gate force-failed *every* portfolio-optimization
    # experiment regardless of algorithm family, which silently mis-classified
    # QAOA / Grover / amplitude-estimation portfolio papers. The gate is now
    # scoped to algorithms actually analysed by Dalzell's QIPM section.
    if st.get("is_infeasible"):
        algo = experiment.get("algorithm") or {}
        family = str(algo.get("family", "")).lower().strip()
        QIPM_FAMILIES = {"qipm", "quantum-interior-point", "quantum_interior_point",
                         "quantum-ipm", "interior-point"}
        if family in QIPM_FAMILIES:
            extras["reason"] = (
                f"Dalzell flags silo '{silo}' as infeasible under current end-to-end "
                f"QIPM estimates (min T-count ~{st.get('min_t_count', '?'):.1e}). "
                f"{st.get('notes', '')}"
            )
            extras["min_t_count"] = st.get("min_t_count")
            extras["min_logical_qubits"] = st.get("min_logical_qubits")
            return "fails", extras["reason"], extras
        # Non-QIPM portfolio algorithms: Dalzell's MSA does not cover them.
        extras["reason"] = (
            f"Dalzell's '{silo}' MSA is QIPM-specific; algorithm family "
            f"'{family or 'unknown'}' is outside Dalzell's analysed scope for this silo."
        )
        extras["dalzell_msa_scope"] = "qipm-only"
        return "not_applicable", extras["reason"], extras

    min_q = st.get("min_logical_qubits")
    min_t = st.get("min_t_count")
    min_td = st.get("min_t_depth")

    # If Dalzell gives no MSA numbers → insufficient_data from the framework side
    if min_q is None and min_t is None:
        extras["reason"] = f"Dalzell has no resource estimates for '{silo}'. {st.get('notes', '')}"
        return "not_applicable", extras["reason"], extras

    qubits, t_count, t_depth = _read_resources(experiment, derived)
    extras["logical_qubits_reported"] = qubits
    extras["t_count_reported"] = t_count
    extras["t_depth_reported"] = t_depth
    extras["t_depth_source"] = (
        "t_depth" if (experiment.get("quantum_resources") or {}).get("t_depth")
        else "circuit_depth_proxy" if t_depth is not None
        else None
    )
    extras["min_logical_qubits"] = min_q
    extras["min_t_count"] = min_t
    extras["min_t_depth"] = min_td
    extras["qubit_margin"] = (qubits / min_q) if (qubits and min_q) else None
    extras["t_count_margin"] = (t_count / min_t) if (t_count and min_t) else None
    extras["t_depth_margin"] = (t_depth / min_td) if (t_depth and min_td) else None

    # Determine resources that we can actually compare (True = at/above MSA)
    qubit_above: bool | None = None
    t_above: bool | None = None
    td_above: bool | None = None

    if qubits is not None and min_q is not None:
        qubit_above = qubits >= min_q
    if t_count is not None and min_t is not None:
        t_above = t_count >= min_t
    if t_depth is not None and min_td is not None:
        td_above = t_depth >= min_td

    comparisons = [x for x in [qubit_above, t_above, td_above] if x is not None]

    # Case 1: qubits + T-count both known (the Dalzell-core comparison)
    if qubit_above is not None and t_above is not None:
        if qubit_above and t_above:
            # Both primary resources pass; check T-depth as an extra dimension
            if td_above is False:
                return (
                    "conditional",
                    f"Qubits and T-count at/above Dalzell MSA but T-depth {t_depth:.1e} < "
                    f"MSA {min_td:.1e}. Runtime may be insufficient.",
                    extras,
                )
            if td_above is None and min_td is not None:
                return (
                    "conditional",
                    f"Qubits and T-count at/above Dalzell MSA (qubits={qubits}, T-count={t_count:.1e}) "
                    f"but T-depth not reported (MSA T-depth={min_td:.1e}). "
                    f"Cannot confirm runtime feasibility.",
                    extras,
                )
            return (
                "likely_viable",
                f"Resources at/above Dalzell MSA: {qubits} qubits ≥ {min_q}, "
                f"T-count {t_count:.1e} ≥ {min_t:.1e}"
                + (f", T-depth {t_depth:.1e} ≥ {min_td:.1e}" if td_above else "")
                + ". Problem at end-to-end advantage scale.",
                extras,
            )
        if not qubit_above and not t_above:
            # Distinguish sub-advantage-regime (toy/demo scale) from genuine fail.
            # Threshold = 10x below MSA on both dimensions (matches margin_tiers.below = 0.1).
            qm = extras.get("qubit_margin") or 0.0
            tm = extras.get("t_count_margin") or 0.0
            if qm < 0.1 and tm < 0.1:
                return (
                    "not_applicable",
                    f"Sub-MSA scale: {qubits} qubits and T-count {t_count:.1e} are >10x below "
                    f"Dalzell MSA ({min_q} qubits, {min_t:.1e} T-count). "
                    f"Experiment is not in the advantage regime Dalzell analyzes; "
                    f"verdict deferred rather than failed.",
                    extras,
                )
            return (
                "fails",
                f"Both primary resources below Dalzell MSA: {qubits} qubits < {min_q}, "
                f"T-count {t_count:.1e} < {min_t:.1e}. Problem classically trivial at this scale.",
                extras,
            )
        return (
            "conditional",
            f"Mixed resources vs Dalzell MSA: qubits {'≥' if qubit_above else '<'} {min_q}, "
            f"T-count {'≥' if t_above else '<'} {min_t:.1e}. Need refinement.",
            extras,
        )

    # Case 2: only one resource known (any of qubits / t_count / t_depth)
    if comparisons:
        known_above = all(comparisons)
        any_above = any(comparisons)
        parts = []
        if qubit_above is not None:
            parts.append(f"qubits {qubits} {'≥' if qubit_above else '<'} MSA {min_q}")
        if t_above is not None:
            parts.append(f"T-count {t_count:.1e} {'≥' if t_above else '<'} MSA {min_t:.1e}")
        if td_above is not None:
            parts.append(f"T-depth {t_depth:.1e} {'≥' if td_above else '<'} MSA {min_td:.1e}")
        if known_above:
            return (
                "conditional",
                f"Partial evidence for advantage scale: {', '.join(parts)}. Other resources unknown.",
                extras,
            )
        if not any_above:
            # Sub-advantage-regime check on whichever single dimension is reported.
            margins = [m for m in (extras.get("qubit_margin"), extras.get("t_count_margin"), extras.get("t_depth_margin")) if m is not None]
            if margins and max(margins) < 0.1:
                return (
                    "not_applicable",
                    f"Sub-MSA scale (>10x below Dalzell MSA on reported dimension): {', '.join(parts)}. "
                    f"Not in advantage regime; verdict deferred.",
                    extras,
                )
            return (
                "fails",
                f"Reported resources below Dalzell MSA: {', '.join(parts)}.",
                extras,
            )
        return (
            "conditional",
            f"Mixed partial resources: {', '.join(parts)}.",
            extras,
        )

    # Case 3: no resources reported
    return (
        "insufficient_data",
        f"No logical qubit count, T-count, or T-depth reported. Cannot compare against Dalzell MSA "
        f"(min qubits={min_q}, min T-count={min_t:.1e}, min T-depth={min_td}).",
        extras,
    )


def run_assessment(silo_filter: str | None = None) -> dict:
    thresholds = load_thresholds()
    derived_lookup = load_derived_fields()
    verdicts: list[dict] = []

    for envelope, experiment in iter_experiments(silo_filter=silo_filter):
        paper_id = envelope["paper_id"]
        exp_id = experiment.get("experiment_id", "?")
        silo = envelope["silo"]
        derived = get_derived(derived_lookup, paper_id, exp_id)

        verdict, reasoning, extras = _assess_one(experiment, silo, thresholds, derived)
        extras["maturity_level"] = compute_maturity_level(experiment)

        has_resources = (
            extras.get("logical_qubits_reported") is not None
            or extras.get("t_count_reported") is not None
            or extras.get("t_depth_reported") is not None
        )
        confidence = (
            "high" if has_resources and extras.get("silo_analyzed_in_dalzell")
            else "medium" if extras.get("silo_analyzed_in_dalzell")
            else "low"
        )

        margin = (
            extras.get("t_count_margin")
            or extras.get("t_depth_margin")
            or extras.get("qubit_margin")
        )

        verdicts.append(make_verdict(
            paper_id=paper_id,
            experiment_id=exp_id,
            silo=silo,
            algorithm_family=(experiment.get("algorithm") or {}).get("family", "unknown"),
            framework=FRAMEWORK_ID,
            verdict=verdict,
            confidence=confidence,
            reasoning=reasoning,
            assumptions={
                "source": "Dalzell et al. 2023, arXiv:2310.03011",
                "methodology": "Per-silo Minimum Scale for Advantage (MSA)",
            },
            quantitative_margin=margin,
            framework_specific=extras,
        ))

    payload = build_output_payload(FRAMEWORK_ID, verdicts)
    save_payload(payload, OUTPUT_PATH)
    return payload


def main():
    p = argparse.ArgumentParser(description="Dalzell et al. (2023) quantum advantage assessment")
    p.add_argument("--silo", help="Filter to specific silo")
    args = p.parse_args()

    payload = run_assessment(args.silo)
    print_summary(payload)
    print(f"\nResults saved to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
