"""Beverland et al. (2022) parameter-swept quantum advantage assessment.

FIDELITY CAVEAT (audit 2026-04-20): this module is NOT a faithful implementation
of the Beverland 2022 resource-estimation methodology (which became the Azure
Quantum Resource Estimator). It applies Babbush 2021 Eq. (5) — a polynomial
crossover formula — across the 6 hardware-scenario *names* introduced by
Beverland 2022. It does NOT perform end-to-end QEC code-distance selection,
T-factory scheduling, or physical-qubit / runtime estimation. Treat this layer
as a "parameter-swept Babbush across Beverland's scenario points" screening
tool, not as a Beverland-faithful resource estimator. See BEVERLAND_CAVEAT.md
for the full discussion. A future revision should call qsharp.estimator
(Azure QRE) to implement the actual Beverland methodology.

Instead of a single threshold, sweeps a grid of hardware scenarios (qubit
count, gate time, error rate, code distance). For each (experiment × scenario)
cell, applies the Babbush Eq. (5) crossover formula with that scenario's
Toffoli time. Produces a per-experiment Pareto surface of verdicts.

Usage:
    python -m p3_thematic_synthesis.s3_quantum_advantage.beverland_2022.assess_beverland
    python -m p3_thematic_synthesis.s3_quantum_advantage.beverland_2022.assess_beverland --silo derivative-pricing
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

FRAMEWORK_ID = "beverland_inspired_2022"  # honest relabel 2026-05-02 (was "beverland_2022");
                                          # see module docstring "FIDELITY CAVEAT" and BEVERLAND_CAVEAT.md.
_MODULE_ROOT = Path(__file__).resolve().parent
SCENARIOS_PATH = _MODULE_ROOT / "beverland_scenarios.json"
OUTPUT_PATH = _MODULE_ROOT / "results" / "beverland_results.json"

# Verdict ordering for best/worst aggregation
_VERDICT_RANK = {
    "viable": 6,
    "likely_viable": 5,
    "potentially_viable": 4,
    "conditional": 3,
    "insufficient_data": 2,
    "not_applicable": 1,
    "fails": 0,
}


def load_scenarios() -> dict:
    return json.loads(SCENARIOS_PATH.read_text(encoding="utf-8"))


def _compute_crossover(d: int, tQ_s: float, tC_s: float, S: float) -> tuple[float, float]:
    """Babbush Eq. (5): M_min = (tQ*S/tC)^(1/(d-1)), T* = tQ * M_min."""
    ratio = (tQ_s * S) / tC_s
    M_min = ratio ** (1.0 / (d - 1))
    T_star = tQ_s * M_min
    return M_min, T_star


def _assess_scenario(
    d: int | None,
    speedup_order: str,
    oracle_M: int | None,
    scenario: dict,
    tC_s: float,
    S: float,
    budget: float,
) -> tuple[str, str]:
    """Return (verdict, reasoning) for one scenario."""
    if speedup_order in ("none_proven", "none"):
        return "fails", "No proven speedup"

    if speedup_order in ("exponential", "logarithmic"):
        return "viable", f"Super-polynomial speedup under {scenario['label']}"

    if d is None:
        return "insufficient_data", "Polynomial degree unknown"

    tQ_s = scenario["toffoli_time_us"] * 1e-6
    M_min, T_star = _compute_crossover(d, tQ_s, tC_s, S)

    if d == 2:
        if T_star > budget:
            return "fails", f"Quadratic T*={T_star:.1e}s > budget under {scenario['label']}"
        if oracle_M is not None and oracle_M >= M_min:
            return "potentially_viable", f"Quadratic M={oracle_M:.1e} >= M_min={M_min:.1e} under {scenario['label']}"
        return "fails", f"Quadratic M_min={M_min:.1e} under {scenario['label']}"

    if d == 3:
        if T_star > budget:
            return "conditional", f"Cubic T*={T_star:.1e}s > budget under {scenario['label']}"
        if oracle_M is not None and oracle_M >= M_min:
            return "potentially_viable", f"Cubic crossover met under {scenario['label']}"
        if oracle_M is None:
            return "conditional", f"Cubic M_min={M_min:.1e}, M unknown under {scenario['label']}"
        return "fails", f"Cubic M < M_min under {scenario['label']}"

    # d >= 4
    if T_star > budget:
        return "potentially_viable", f"Polynomial d={d} T*={T_star:.1e}s > budget under {scenario['label']}"
    return "likely_viable", f"Polynomial d={d} crossover easy under {scenario['label']}"


def _assess_one(
    experiment: dict, scenarios_config: dict, derived: dict | None
) -> tuple[str, str, dict]:
    algo = experiment.get("algorithm") or {}
    algo_family = algo.get("family", "unknown")
    complexity = experiment.get("complexity_analysis") or {}
    mapping = scenarios_config["algorithm_speedup_mapping"]

    speedup_order, _k, speedup_reasoning = infer_speedup_order(
        algo_family, complexity, mapping, derived
    )
    oracle_M, op_type = estimate_oracle_complexity(experiment, derived)

    d_map = {"quadratic": 2, "cubic": 3, "quartic": 4, "polynomial_other": 4}
    d = d_map.get(speedup_order)

    tC_s = scenarios_config["classical_primitive_time_ns"] * 1e-9
    S = scenarios_config["classical_parallelism_S"]

    scenario_verdicts: dict[str, dict] = {}
    for name, scenario in scenarios_config["named_scenarios"].items():
        budget = scenario["budget_seconds"]
        v, r = _assess_scenario(d, speedup_order, oracle_M, scenario, tC_s, S, budget)
        tQ_s = scenario["toffoli_time_us"] * 1e-6
        M_min, T_star = (None, None)
        if d is not None and d >= 2:
            M_min, T_star = _compute_crossover(d, tQ_s, tC_s, S)
        scenario_verdicts[name] = {
            "verdict": v,
            "reasoning": r,
            "toffoli_time_us": scenario["toffoli_time_us"],
            "M_min": M_min,
            "T_star_seconds": T_star,
        }

    # Aggregate: best, worst, median
    sorted_verdicts = sorted(
        scenario_verdicts.items(),
        key=lambda kv: _VERDICT_RANK.get(kv[1]["verdict"], 0),
    )
    worst_name, worst = sorted_verdicts[0]
    best_name, best = sorted_verdicts[-1]
    # Median by verdict rank (lower-median for even counts)
    median_idx = (len(sorted_verdicts) - 1) // 2
    median_name, median = sorted_verdicts[median_idx]

    # Top-level verdict determined by configured aggregation_policy
    policy = scenarios_config.get("aggregation_policy", "balanced")
    if policy == "conservative":
        chosen_name, chosen = worst_name, worst
    elif policy == "optimistic":
        chosen_name, chosen = best_name, best
    else:  # balanced (default)
        chosen_name, chosen = median_name, median

    top_verdict = chosen["verdict"]
    top_reasoning = (
        f"{speedup_reasoning}. "
        f"Aggregation policy='{policy}' -> {chosen_name}: {chosen['reasoning']}. "
        f"[Best={best_name}:{best['verdict']}, Median={median_name}:{median['verdict']}, Worst={worst_name}:{worst['verdict']}]"
    )

    extras = {
        "speedup_order": speedup_order,
        "oracle_complexity_M": oracle_M,
        "operation_type": op_type,
        "scenario_verdicts": scenario_verdicts,
        "aggregation_policy": policy,
        "best_scenario": best_name,
        "worst_scenario": worst_name,
        "median_scenario": median_name,
        "best_verdict": best["verdict"],
        "worst_verdict": worst["verdict"],
        "median_verdict": median["verdict"],
    }
    return top_verdict, top_reasoning, extras


def run_assessment(silo_filter: str | None = None) -> dict:
    scenarios_config = load_scenarios()
    derived_lookup = load_derived_fields()
    verdicts: list[dict] = []

    for envelope, experiment in iter_experiments(silo_filter=silo_filter):
        paper_id = envelope["paper_id"]
        exp_id = experiment.get("experiment_id", "?")
        silo = envelope["silo"]
        derived = get_derived(derived_lookup, paper_id, exp_id)

        verdict, reasoning, extras = _assess_one(experiment, scenarios_config, derived)
        extras["maturity_level"] = compute_maturity_level(experiment)

        has_M = extras["oracle_complexity_M"] is not None
        has_d = extras["speedup_order"] not in (None, "unknown")
        confidence = "high" if (has_M and has_d) else "medium" if has_d else "low"

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
                "methodology": "Parameter-swept Babbush Eq.(5) across 6 hardware scenarios",
                "fidelity_caveat": (
                    "NOT a faithful Beverland 2022 resource estimator. Uses Babbush polynomial-"
                    "crossover formula across Beverland's scenario *names*; no QEC code-distance "
                    "selection, no T-factory modelling, no physical-qubit/runtime estimation. "
                    "See BEVERLAND_CAVEAT.md (audit 2026-04-20)."
                ),
                "scenarios": list(scenarios_config["named_scenarios"].keys()),
                "classical_parallelism_S": scenarios_config["classical_parallelism_S"],
                "aggregation_policy": scenarios_config.get("aggregation_policy", "balanced"),
                "verdict_is": f"scenario selected by aggregation_policy='{scenarios_config.get('aggregation_policy', 'balanced')}'",
            },
            quantitative_margin=None,
            framework_specific=extras,
        ))

    payload = build_output_payload(FRAMEWORK_ID, verdicts)
    save_payload(payload, OUTPUT_PATH)
    return payload


def main():
    p = argparse.ArgumentParser(description="Beverland et al. (2022) parameter-swept assessment")
    p.add_argument("--silo", help="Filter to specific silo")
    args = p.parse_args()

    payload = run_assessment(args.silo)
    print_summary(payload)
    print(f"\nResults saved to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
