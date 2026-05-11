"""Babbush et al. (2021) quantum advantage assessment.

Applies Eq. (5) M > (tQ*S/tC)^(1/(d-1)) and T* = tQ * (tQ*S/tC)^(1/(d-1)) to each
experiment, under the paper's default superconducting-surface-code clock model
(tQ >= 17 ms, tC <= 33 ns) with classical parallelism S.

Usage:
    python -m p3_thematic_synthesis.s3_quantum_advantage.babbush_2021.assess_babbush
    python -m p3_thematic_synthesis.s3_quantum_advantage.babbush_2021.assess_babbush --silo derivative-pricing
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

from .._shared import (
    build_output_payload,
    compute_maturity_level,
    estimate_oracle_complexity,
    get_derived,
    infer_speedup_order,
    iter_experiments,
    load_derived_fields,
    make_verdict,
    print_summary,
    save_payload,
)

FRAMEWORK_ID = "babbush_2021"
_MODULE_ROOT = Path(__file__).resolve().parent
THRESHOLDS_PATH = _MODULE_ROOT / "babbush_thresholds.json"
OUTPUT_PATH = _MODULE_ROOT / "results" / "babbush_results.json"


def load_thresholds() -> dict:
    return json.loads(THRESHOLDS_PATH.read_text(encoding="utf-8"))


def _compute_M_min_and_Tstar(d: int, tQ: float, tC: float, S: float) -> tuple[float, float]:
    """Eq. (5): M_min = (tQ*S/tC)^(1/(d-1)); T* = tQ * M_min."""
    ratio = (tQ * S) / tC
    M_min = ratio ** (1.0 / (d - 1))
    T_star = tQ * M_min
    return M_min, T_star


def _assess_polynomial(
    d: int, M_reported: int | None, tQ: float, tC: float, S: float, budget: float
) -> tuple[str, str, float, float]:
    """Return (verdict, reasoning, M_min, T_star) for a polynomial speedup of order d."""
    M_min, T_star = _compute_M_min_and_Tstar(d, tQ, tC, S)

    # Quadratic — Babbush's central negative result
    if d == 2:
        if T_star > budget:
            return (
                "fails",
                f"Quadratic: Eq.(5) M_min={M_min:.1e} → T*={T_star:.1e}s exceeds budget {budget:.0e}s. "
                "Babbush's central claim: quadratic speedups not viable under FT + parallel classical.",
                M_min, T_star,
            )
        if M_reported is not None and M_reported >= M_min:
            return (
                "potentially_viable",
                f"Quadratic: M_reported={M_reported:.1e} ≥ M_min={M_min:.1e}, T*={T_star:.1e}s within budget. "
                "Rare case surviving Babbush's framework.",
                M_min, T_star,
            )
        return (
            "fails",
            f"Quadratic: M_min={M_min:.1e} required, M_reported={M_reported}. "
            "Under Babbush, quadratic speedup is generally infeasible.",
            M_min, T_star,
        )

    # Cubic — Babbush's borderline case
    if d == 3:
        if T_star > budget:
            return (
                "conditional",
                f"Cubic: T*={T_star:.1e}s exceeds {budget:.0e}s budget at S={S:.0e}. Viable only under lower parallelism.",
                M_min, T_star,
            )
        if M_reported is None:
            return (
                "conditional",
                f"Cubic: M_min={M_min:.1e}, T*={T_star:.1e}s fits budget. Requires M ≥ M_min (not reported).",
                M_min, T_star,
            )
        if M_reported >= M_min:
            return (
                "potentially_viable",
                f"Cubic: M_reported={M_reported:.1e} ≥ M_min={M_min:.1e}, T*={T_star:.1e}s fits budget.",
                M_min, T_star,
            )
        return (
            "fails",
            f"Cubic: M_reported={M_reported:.1e} < M_min={M_min:.1e}. Problem too small to amortize FT overhead.",
            M_min, T_star,
        )

    # Quartic+ — easy crossover
    if d >= 4:
        if T_star > budget:
            return (
                "potentially_viable",
                f"Polynomial d={d}: T*={T_star:.1e}s exceeds {budget:.0e}s but M_min={M_min:.1e} is low; viable with budget extension.",
                M_min, T_star,
            )
        return (
            "likely_viable",
            f"Polynomial d={d}: M_min={M_min:.1e}, T*={T_star:.1e}s. Babbush's preferred regime — quartic+ restores viability.",
            M_min, T_star,
        )

    return "insufficient_data", f"Unhandled polynomial order d={d}", M_min, T_star


# 2026-04-20 audit fix M2: expose Babbush's three Table-I regimes for S as a CLI
# option. Default remains S=1000 (typical_cluster) so frozen verdicts don't shift
# unless --regime is explicitly passed.
_REGIME_S = {
    "single_core": 1,
    "typical_cluster": 1000,
    "extreme_sa": 1_000_000,
}


def _assess_one(
    experiment: dict, thresholds: dict, derived: dict | None,
    *, S_override: float | None = None,
) -> tuple[str, str, dict]:
    algo = experiment.get("algorithm") or {}
    algo_family = algo.get("family", "unknown")
    complexity = experiment.get("complexity_analysis") or {}
    mapping = thresholds["algorithm_speedup_mapping"]

    speedup_order, _k, speedup_reasoning = infer_speedup_order(
        algo_family, complexity, mapping, derived
    )
    oracle_M, op_type = estimate_oracle_complexity(experiment, derived)

    tQ = thresholds["default_tQ_s"]
    tC = thresholds["default_tC_s"]
    S = S_override if S_override is not None else thresholds["default_S"]
    budget = thresholds["budget_seconds"]

    extras: dict = {
        "speedup_order": speedup_order,
        "oracle_complexity_M": oracle_M,
        "operation_type": op_type,
        "tQ_seconds": tQ,
        "tC_seconds": tC,
        "S": S,
        "budget_seconds": budget,
    }

    if speedup_order in ("none_proven", "none"):
        extras["M_min"] = None
        extras["T_star_seconds"] = None
        return (
            "fails",
            f"{speedup_reasoning}. Babbush framework requires a proven polynomial speedup.",
            extras,
        )

    if speedup_order == "exponential":
        extras["M_min"] = None
        extras["T_star_seconds"] = None
        return (
            "viable",
            f"{speedup_reasoning}. Exponential speedup escapes the polynomial-crossover penalty.",
            extras,
        )

    if speedup_order == "logarithmic":
        extras["M_min"] = None
        extras["T_star_seconds"] = None
        return (
            "likely_viable",
            f"{speedup_reasoning}. Super-polynomial speedup comparable to exponential.",
            extras,
        )

    d_map = {"quadratic": 2, "cubic": 3, "quartic": 4, "polynomial_other": 4}
    d = d_map.get(speedup_order)
    if d is None:
        extras["M_min"] = None
        extras["T_star_seconds"] = None
        return (
            "insufficient_data",
            f"{speedup_reasoning}. Speedup order '{speedup_order}' not mapped to a polynomial degree.",
            extras,
        )

    extras["d"] = d
    verdict, reasoning, M_min, T_star = _assess_polynomial(d, oracle_M, tQ, tC, S, budget)
    extras["M_min"] = M_min
    extras["T_star_seconds"] = T_star
    return verdict, f"{speedup_reasoning}. {reasoning}", extras


def run_assessment(silo_filter: str | None = None,
                   regime: str | None = None) -> dict:
    thresholds = load_thresholds()
    derived_lookup = load_derived_fields()
    verdicts: list[dict] = []

    # Resolve regime → S override (default = thresholds default_S, currently 1000)
    S_override = None
    regime_label = regime or "typical_cluster"
    if regime is not None:
        if regime not in _REGIME_S:
            raise ValueError(
                f"Unknown --regime '{regime}'. Choose from {list(_REGIME_S)} "
                "(per Babbush 2021 Table I)."
            )
        S_override = _REGIME_S[regime]

    for envelope, experiment in iter_experiments(silo_filter=silo_filter):
        paper_id = envelope["paper_id"]
        exp_id = experiment.get("experiment_id", "?")
        silo = envelope["silo"]
        derived = get_derived(derived_lookup, paper_id, exp_id)

        verdict, reasoning, extras = _assess_one(
            experiment, thresholds, derived, S_override=S_override
        )
        extras["maturity_level"] = compute_maturity_level(experiment)
        extras["regime"] = regime_label

        has_M = extras["oracle_complexity_M"] is not None
        has_d = extras["speedup_order"] not in (None, "unknown")
        confidence = "high" if (has_M and has_d) else "medium" if has_d else "low"

        margin = None
        if extras.get("M_min") and extras["oracle_complexity_M"]:
            try:
                margin = extras["oracle_complexity_M"] / extras["M_min"]
                if not math.isfinite(margin):
                    margin = None
            except (TypeError, ZeroDivisionError):
                margin = None

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
                "tQ_seconds": thresholds["default_tQ_s"],
                "tC_seconds": thresholds["default_tC_s"],
                "S": S_override if S_override is not None else thresholds["default_S"],
                "budget_seconds": thresholds["budget_seconds"],
                "regime": regime_label,
                "code_distance": thresholds["fault_tolerance_model"]["code_distance"],
            },
            quantitative_margin=margin,
            framework_specific=extras,
        ))

    payload = build_output_payload(FRAMEWORK_ID, verdicts)
    save_payload(payload, OUTPUT_PATH)
    return payload


def main():
    p = argparse.ArgumentParser(description="Babbush et al. (2021) quantum advantage assessment")
    p.add_argument("--silo", help="Filter to specific silo")
    p.add_argument(
        "--regime",
        choices=sorted(_REGIME_S.keys()),
        default=None,
        help=("Classical parallelism regime (Babbush 2021 Table I): "
              "single_core (S=1, lower bound), typical_cluster (S=1e3, default frozen), "
              "extreme_sa (S=1e6, SA-like). Default = typical_cluster."),
    )
    args = p.parse_args()

    payload = run_assessment(args.silo, regime=args.regime)
    print_summary(payload)
    print(f"\nResults saved to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
