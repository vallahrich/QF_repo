"""Hoefler et al. (2023) quantum advantage assessment.

Refactored to emit the common verdict schema shared by every framework in
quantum_advantage/. The Hoefler-specific 10-verdict vocabulary is preserved
under framework_specific.original_verdict so older analysis can round-trip.

Usage:
    python -m p3_thematic_synthesis.s3_quantum_advantage.hoefler_assessment.assess_hoefler
    python -m p3_thematic_synthesis.s3_quantum_advantage.hoefler_assessment.assess_hoefler --silo portfolio-optimization
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
    infer_speedup_order,
    iter_experiments,
    load_derived_fields,
    make_verdict,
    print_summary,
    save_payload,
)

FRAMEWORK_ID = "hoefler_2023"
_MODULE_ROOT = Path(__file__).resolve().parent
THRESHOLDS_PATH = _MODULE_ROOT / "hoefler_thresholds.json"
OUTPUT_PATH = _MODULE_ROOT / "results" / "hoefler_results.json"


# Hoefler's 10 original verdicts → common 7
_VERDICT_MAP = {
    "viable": "viable",
    "likely_viable": "likely_viable",
    "potentially_viable": "potentially_viable",
    "cubic_conditional": "conditional",
    "no_proven_speedup": "fails",
    "quadratic_insufficient": "fails",
    "oracle_too_complex": "fails",
    "io_bottleneck": "fails",
    "insufficient_data": "insufficient_data",
    "runtime_advantage_demonstrated": "viable",
    "crossover_viable": "likely_viable",
}


def load_thresholds() -> dict:
    return json.loads(THRESHOLDS_PATH.read_text(encoding="utf-8"))


def _check_direct_runtime(experiment: dict, budget_seconds: int) -> tuple[str | None, str]:
    complexity = experiment.get("complexity_analysis") or {}
    impl = experiment.get("implementation_details") or {}

    def _numeric(v):
        return v if isinstance(v, (int, float)) else None

    t_q = (
        _numeric(complexity.get("wall_clock_quantum"))
        or _numeric(impl.get("quantum_execution_time"))
        or _numeric(impl.get("total_execution_time"))
    )
    t_c = _numeric(complexity.get("wall_clock_classical"))

    if t_q is not None and t_c is not None:
        if t_q < t_c:
            ratio = t_c / t_q if t_q > 0 else float("inf")
            return ("runtime_advantage",
                    f"Measured quantum time {t_q}s < classical {t_c}s (speedup {ratio:.1f}x)")
        return ("runtime_no_advantage",
                f"Measured quantum time {t_q}s >= classical {t_c}s")

    if t_q is not None and t_q > budget_seconds:
        return ("runtime_exceeds_budget",
                f"Quantum runtime {t_q}s exceeds budget {budget_seconds}s")

    crossover = complexity.get("crossover_n")
    if crossover is not None:
        try:
            cn = float(str(crossover).replace(",", ""))
            pi = experiment.get("problem_instance") or {}
            N = pi.get("num_assets") or pi.get("dataset_size")
            if isinstance(N, (int, float)) and N > 0:
                if N >= cn:
                    return ("crossover_reached",
                            f"Problem size N={N} >= crossover N*={cn}")
                return ("crossover_not_reached",
                        f"Problem size N={N} < crossover N*={cn}")
        except (ValueError, TypeError):
            pass

    return None, ""


def _check_io(experiment: dict, thresholds: dict) -> tuple[bool, str]:
    pi = experiment.get("problem_instance") or {}
    dataset_size = pi.get("dataset_size")
    num_assets = pi.get("num_assets")
    quantum_io = thresholds["table1_performance"]["future_quantum"]["io_bandwidth_gbps"]
    budget = thresholds["crossover_budget_seconds"]
    max_bits = quantum_io * 1e9 * budget

    if isinstance(dataset_size, (int, float)) and dataset_size > 0:
        data_bits = int(dataset_size * 64)
    elif isinstance(num_assets, (int, float)) and num_assets > 0:
        data_bits = int(num_assets * num_assets * 64)  # covariance
    else:
        return False, "Data size unknown — cannot assess I/O constraint"

    if data_bits > max_bits:
        return True, f"Data size {data_bits:.0e} bits exceeds I/O capacity {max_bits:.0e}"
    return False, f"Data size {data_bits:.0e} bits within I/O capacity"


def _assess_one(experiment: dict, thresholds: dict, derived: dict | None) -> tuple[str, str, dict]:
    """Return (hoefler_original_verdict, reasoning, framework_specific_extras)."""
    algo = experiment.get("algorithm") or {}
    algo_family = algo.get("family", "unknown")
    complexity = experiment.get("complexity_analysis") or {}
    mapping = thresholds.get("algorithm_speedup_mapping", {})

    speedup_order, k, speedup_reasoning = infer_speedup_order(
        algo_family, complexity, mapping, derived
    )

    # 2026-04-20 audit fix C3: amplitude-estimation, Grover, QMC, quantum-walk and
    # quantum-simulated-annealing are quadratic by published consensus (Brassard 2002;
    # Grover 1996; Szegedy 2004). Some upstream extractions report "exponential" or
    # other higher-order labels for these families; that is an extraction error.
    # Force speedup_order back to "quadratic" so Hoefler Table 2 applies correctly.
    _AE_GROVER_FAMILIES = {
        "amplitude-estimation", "amplitude_estimation",
        "quantum-amplitude-estimation", "quantum_amplitude_estimation",
        "grover", "amplitude_amplification", "amplitude-amplification",
        "quantum_monte_carlo", "quantum-monte-carlo", "qmc",
        "quantum_walk", "quantum-walk",
        "quantum_simulated_annealing", "quantum-simulated-annealing",
    }
    if (algo_family in _AE_GROVER_FAMILIES
            and speedup_order in ("exponential", "logarithmic", "cubic",
                                  "quartic", "polynomial_other")):
        speedup_reasoning = (
            f"Upstream reported speedup_order='{speedup_order}' for family '{algo_family}', "
            f"but published consensus (Brassard 2002 / Grover 1996 / Szegedy 2004) is quadratic. "
            f"Overriding to 'quadratic' (audit fix C3, 2026-04-20)."
        )
        speedup_order = "quadratic"
        k = 2

    oracle_M, op_type = estimate_oracle_complexity(experiment, derived)
    io_limited, io_reasoning = _check_io(experiment, thresholds)
    direct_verdict, direct_reasoning = _check_direct_runtime(
        experiment, thresholds["crossover_budget_seconds"]
    )

    threshold_M: int | None = None
    table2 = thresholds["table2_max_operations_per_oracle"]

    if speedup_order in ("none_proven", "none"):
        verdict = "no_proven_speedup"
        reasoning = speedup_reasoning

    elif speedup_order == "quadratic":
        verdict = "quadratic_insufficient"
        threshold_M = table2["quadratic"].get("binary", 68)
        reasoning = (f"{speedup_reasoning}. Hoefler Table 2: max {threshold_M} "
                     f"binary ops/oracle at k=2 — insufficient for non-trivial compute.")

    elif speedup_order == "cubic":
        op_key = "binary" if op_type in ("binary", "t_count", "binary_derived",
                                          "depth_times_qubits", "unknown") else op_type
        threshold_M = table2["cubic"].get(op_key, 12_500_000)
        if oracle_M is not None:
            if oracle_M <= threshold_M:
                verdict = "potentially_viable"
                reasoning = (f"{speedup_reasoning}. M={oracle_M:,} ≤ {threshold_M:,} ({op_key}).")
            else:
                verdict = "oracle_too_complex"
                reasoning = (f"{speedup_reasoning}. M={oracle_M:,} > {threshold_M:,} ({op_key}).")
        else:
            verdict = "cubic_conditional"
            reasoning = (f"{speedup_reasoning}. M unknown — viable if ≤ {threshold_M:,} {op_key}.")

    elif speedup_order in ("quartic", "polynomial_other"):
        op_key = "binary" if op_type in ("binary", "t_count", "binary_derived",
                                          "depth_times_qubits", "unknown") else op_type
        threshold_M = table2["quartic"].get(op_key, 712_000_000)
        verdict = "likely_viable"
        reasoning = f"{speedup_reasoning}. Quartic+ with threshold {threshold_M:,} {op_key}."

    elif speedup_order == "exponential":
        # 2026-04-20 audit fix C2: HHL exponential speedup requires the matrix
        # to be efficiently row-computable AND the user to need only a sample
        # from the solution (not full readout). Without explicit verification of
        # both caveats, downgrade to conditional (cannot defend a viable verdict).
        if algo_family in ("hhl", "quantum-linear-systems", "quantum_linear_systems"):
            row_computable = complexity.get("hhl_matrix_row_computable")
            readout_type = str(complexity.get("solution_readout_type", "")).lower()
            caveat_met = bool(row_computable) and readout_type in ("partial", "sampling", "expectation")
            if not caveat_met:
                verdict = "cubic_conditional"  # maps to common 'conditional'
                reasoning = (
                    f"{speedup_reasoning}. HHL caveat unverified: matrix row-computable? "
                    f"full solution readout avoided? Without both, the exponential speedup "
                    f"is not defensible (Hoefler caveat; Aaronson 2015). Downgraded to conditional."
                )
            elif io_limited:
                verdict = "io_bottleneck"
                reasoning = f"{speedup_reasoning}. Exponential BUT {io_reasoning}"
            else:
                verdict = "viable"
                reasoning = f"{speedup_reasoning}. Exponential with HHL caveats verified, I/O OK."
        elif io_limited:
            verdict = "io_bottleneck"
            reasoning = f"{speedup_reasoning}. Exponential BUT {io_reasoning}"
        else:
            verdict = "viable"
            reasoning = f"{speedup_reasoning}. Exponential, I/O OK."

    elif speedup_order == "logarithmic":
        verdict = "likely_viable"
        reasoning = f"{speedup_reasoning}. Super-polynomial speedup."

    else:
        verdict = "insufficient_data"
        reasoning = f"Speedup order unknown for '{algo_family}'"

    if direct_verdict:
        reasoning += f" | Direct runtime: {direct_reasoning}"
        # 2026-04-20 audit fix C1: a measured wall-clock advantage on a single
        # toy instance does NOT invalidate Hoefler's asymptotic Table 2. Only
        # cubic+ speedup classes are eligible for upgrade via crossover/runtime;
        # quadratic and none_proven stay at their asymptotic verdict.
        _UPGRADABLE_ORDERS = ("cubic", "quartic", "polynomial_other",
                              "exponential", "logarithmic")
        if direct_verdict == "runtime_advantage":
            if speedup_order in _UPGRADABLE_ORDERS:
                verdict = "runtime_advantage_demonstrated"
            else:
                reasoning += (" | Upgrade BLOCKED: measured advantage on a single instance "
                              "cannot override asymptotic insufficiency for quadratic/no-speedup "
                              "(audit fix C1, 2026-04-20).")
        elif direct_verdict == "crossover_reached" and verdict not in (
            "quadratic_insufficient", "no_proven_speedup"
        ):
            verdict = "crossover_viable"

    extras = {
        "original_verdict": verdict,
        "speedup_order": speedup_order,
        "speedup_k": k,
        "oracle_complexity_M": oracle_M,
        "operation_type": op_type,
        "threshold_M": threshold_M,
        "io_limited": io_limited,
        "direct_runtime_check": direct_verdict,
    }
    return verdict, reasoning, extras


def run_assessment(silo_filter: str | None = None) -> dict:
    thresholds = load_thresholds()
    derived_lookup = load_derived_fields()
    verdicts: list[dict] = []

    for envelope, experiment in iter_experiments(silo_filter=silo_filter):
        paper_id = envelope["paper_id"]
        exp_id = experiment.get("experiment_id", "?")
        silo = envelope["silo"]
        derived = get_derived(derived_lookup, paper_id, exp_id)

        original_verdict, reasoning, extras = _assess_one(experiment, thresholds, derived)
        common_verdict = _VERDICT_MAP.get(original_verdict, "insufficient_data")
        extras["maturity_level"] = compute_maturity_level(experiment)

        confidence = (
            "high" if extras["oracle_complexity_M"] is not None
                     and extras["speedup_order"] not in (None, "unknown", "none")
            else "medium" if extras["speedup_order"] not in (None, "unknown", "none")
            else "low"
        )

        verdicts.append(make_verdict(
            paper_id=paper_id,
            experiment_id=exp_id,
            silo=silo,
            algorithm_family=(experiment.get("algorithm") or {}).get("family", "unknown"),
            framework=FRAMEWORK_ID,
            verdict=common_verdict,
            confidence=confidence,
            reasoning=reasoning,
            assumptions={
                "logical_qubits": 10_000,
                "gate_time_us": 10,
                "budget_seconds": thresholds["crossover_budget_seconds"],
            },
            quantitative_margin=(
                extras["oracle_complexity_M"] / extras["threshold_M"]
                if extras["oracle_complexity_M"] and extras["threshold_M"]
                else None
            ),
            framework_specific=extras,
        ))

    payload = build_output_payload(FRAMEWORK_ID, verdicts)
    save_payload(payload, OUTPUT_PATH)
    return payload


def main():
    p = argparse.ArgumentParser(description="Hoefler et al. (2023) quantum advantage assessment")
    p.add_argument("--silo", help="Filter to specific silo")
    args = p.parse_args()

    payload = run_assessment(args.silo)
    print_summary(payload)
    print(f"\nResults saved to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
