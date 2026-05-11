"""Stilck França & García-Patrón (2021) NISQ noise-bound assessment.

Scoped: any non-fault-tolerant noisy circuit. Includes variational families
(QAOA, VQE, QA, QNN, QGAN, QCBM, hybrid, quantum-ml, qsvm) AND non-variational
optimization/estimation circuits run on NISQ hardware (amplitude-estimation,
Grover, quantum-walk, quantum-monte-carlo). Per the paper, the p×L bound
applies to any noisy circuit, not just variational ones (audit fix M1, 2026-04-20).
Checks whether noise_rate × circuit_depth exceeds the Stilck França bound,
beyond which the circuit's output is indistinguishable from random.

Usage:
    python -m p3_thematic_synthesis.s3_quantum_advantage.stilck_franca_2021.assess_stilck_franca
    python -m p3_thematic_synthesis.s3_quantum_advantage.stilck_franca_2021.assess_stilck_franca --silo portfolio-optimization
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from .._shared import (
    build_output_payload,
    compute_maturity_level,
    get_derived,
    iter_experiments,
    load_derived_fields,
    make_verdict,
    print_summary,
    save_payload,
)

FRAMEWORK_ID = "stilck_franca_2021"
_MODULE_ROOT = Path(__file__).resolve().parent
THRESHOLDS_PATH = _MODULE_ROOT / "stilck_franca_thresholds.json"
OUTPUT_PATH = _MODULE_ROOT / "results" / "stilck_franca_results.json"


def load_thresholds() -> dict:
    return json.loads(THRESHOLDS_PATH.read_text(encoding="utf-8"))


def _infer_noise_rate(experiment: dict) -> tuple[float | None, str]:
    """Try to extract or infer a per-gate error rate.

    Sources (in order of preference):
      1. Explicit numeric entry in noise_model (error_rate, two_qubit_error, ...)
      2. Hardware name matched against known device families
      3. Hardware.platform / noise_model.platform string
      4. Maturity level L3/L4 (real QPU) -> superconducting default
      5. Explicit is_noisy=true flag -> conservative default
    """
    noise = experiment.get("noise_model") or {}
    hw = experiment.get("hardware") or {}
    impl = experiment.get("implementation_details") or {}

    # 1. Explicit error rate (check numeric fields in both noise_model and hardware)
    for src in (noise, hw):
        for key in ("error_rate", "two_qubit_error", "two_qubit_error_rate",
                     "gate_error_rate", "single_qubit_error_rate"):
            rate = src.get(key)
            if isinstance(rate, (int, float)) and rate > 0:
                return float(rate), "explicit"

    # 2. Infer from hardware_name string
    hw_name = str(impl.get("hardware_name") or hw.get("device_name") or "").lower()
    platform = str(hw.get("platform") or noise.get("platform") or "").lower()
    hay = f"{hw_name} {platform}"
    if any(k in hay for k in ("ibm", "eagle", "heron", "sycamore", "google",
                                "rigetti", "aspen", "superconducting")):
        return 0.005, "inferred_superconducting_2023"
    if any(k in hay for k in ("ionq", "aria", "quantinuum", "h1", "h2",
                                "ion-trap", "ion_trap", "trapped-ion", "trapped_ion")):
        return 0.003, "inferred_ion_trap_2023"
    if any(k in hay for k in ("d-wave", "dwave", "advantage", "annealer")):
        return 0.01, "inferred_quantum_annealer"

    # 3. Infer from maturity level (real QPU runs are noisy even if not reported)
    from .._shared import compute_maturity_level
    maturity = compute_maturity_level(experiment)
    if maturity in ("L3_qpu_small", "L4_qpu_scale"):
        return 0.005, "inferred_from_maturity_qpu"
    if maturity == "L2_noisy_sim":
        return 0.005, "inferred_from_maturity_noisy_sim"

    # 4. Explicit is_noisy flag without a specific value
    if noise.get("is_noisy") is True:
        return 0.01, "default_noisy"

    return None, "unknown"


def _get_circuit_depth(experiment: dict) -> int | None:
    qr = experiment.get("quantum_resources") or {}
    depth = qr.get("circuit_depth")
    if isinstance(depth, (int, float)) and depth > 0:
        return int(depth)

    # Infer from layers/rounds for variational
    impl = experiment.get("implementation_details") or {}
    algo = experiment.get("algorithm") or {}
    layers = (impl.get("num_layers") or impl.get("ansatz_depth")
              or impl.get("p_rounds") or algo.get("num_layers"))
    if isinstance(layers, (int, float)) and layers > 0:
        return int(layers) * 2  # rough: 2 gate layers per variational layer

    # Last resort: gate count / qubit count ≈ effective depth
    gate_count = qr.get("gate_count_total") or qr.get("two_qubit_gate_count")
    n_qubits = qr.get("num_qubits")
    if (isinstance(gate_count, (int, float)) and gate_count > 0
            and isinstance(n_qubits, (int, float)) and n_qubits > 0):
        est = int(gate_count / max(n_qubits, 1))
        if est > 0:
            return est

    return None


def _assess_one(
    experiment: dict, thresholds: dict, derived: dict | None
) -> tuple[str, str, dict]:
    applicable_families = thresholds["applicable_algorithm_families"]
    algo = experiment.get("algorithm") or {}
    algo_family = algo.get("family", "unknown")

    extras: dict = {
        "algorithm_family": algo_family,
        "is_variational": algo_family in applicable_families,
    }

    if not extras["is_variational"]:
        return (
            "not_applicable",
            f"Algorithm '{algo_family}' is not variational/NISQ. "
            "Stilck França bound only constrains noisy variational circuits.",
            extras,
        )

    error_rate, rate_source = _infer_noise_rate(experiment)
    circuit_depth = _get_circuit_depth(experiment)

    extras["error_rate"] = error_rate
    extras["error_rate_source"] = rate_source
    extras["circuit_depth"] = circuit_depth

    practical_threshold = thresholds["noise_bound"]["practical_threshold"]
    critical_threshold = thresholds["noise_bound"]["critical_pL_product"]

    if error_rate is None:
        # Check if it's a simulator (noiseless)
        noise = experiment.get("noise_model") or {}
        if noise.get("is_noisy") is False or noise.get("type") == "noiseless":
            extras["pL_product"] = 0
            return (
                "not_applicable",
                "Noiseless simulation — Stilck França bound does not apply (no physical noise).",
                extras,
            )
        return (
            "insufficient_data",
            "No noise rate available. Cannot compute p×L product for Stilck França bound.",
            extras,
        )

    if circuit_depth is None:
        return (
            "insufficient_data",
            f"Noise rate p={error_rate} ({rate_source}) but no circuit depth. "
            "Cannot compute p×L.",
            extras,
        )

    pL = error_rate * circuit_depth
    extras["pL_product"] = pL

    if pL > critical_threshold:
        return (
            "fails",
            f"Stilck França: p×L = {error_rate}×{circuit_depth} = {pL:.2f} > {critical_threshold}. "
            "Circuit output indistinguishable from random — no advantage possible.",
            extras,
        )

    if pL > practical_threshold:
        return (
            "conditional",
            f"Stilck França: p×L = {pL:.2f} in danger zone ({practical_threshold} < p×L ≤ {critical_threshold}). "
            "Severely limited approximation quality.",
            extras,
        )

    return (
        "potentially_viable",
        f"Stilck França: p×L = {pL:.4f} ≤ {practical_threshold}. "
        "Below noise threshold — variational circuit may retain useful signal.",
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

        verdict, reasoning, extras = _assess_one(experiment, thresholds, derived)
        extras["maturity_level"] = compute_maturity_level(experiment)

        has_pL = extras.get("pL_product") is not None
        confidence = (
            "high" if has_pL and extras.get("error_rate_source") == "explicit"
            else "medium" if has_pL
            else "low"
        )

        verdicts.append(make_verdict(
            paper_id=paper_id,
            experiment_id=exp_id,
            silo=silo,
            algorithm_family=algo_family if (algo_family := (experiment.get("algorithm") or {}).get("family", "unknown")) else "unknown",
            framework=FRAMEWORK_ID,
            verdict=verdict,
            confidence=confidence,
            reasoning=reasoning,
            assumptions={
                "practical_pL_threshold": thresholds["noise_bound"]["practical_threshold"],
                "critical_pL_threshold": thresholds["noise_bound"]["critical_pL_product"],
            },
            quantitative_margin=extras.get("pL_product"),
            framework_specific=extras,
        ))

    payload = build_output_payload(FRAMEWORK_ID, verdicts)
    save_payload(payload, OUTPUT_PATH)
    return payload


def main():
    p = argparse.ArgumentParser(description="Stilck França & García-Patrón (2021) NISQ noise-bound assessment")
    p.add_argument("--silo", help="Filter to specific silo")
    args = p.parse_args()

    payload = run_assessment(args.silo)
    print_summary(payload)
    print(f"\nResults saved to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
