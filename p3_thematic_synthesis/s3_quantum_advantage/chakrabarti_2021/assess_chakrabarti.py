"""Chakrabarti et al. (2021) quantum advantage assessment.

Finance-specific framework: compares each experiment's logical qubits and
T-count/T-depth against the Chakrabarti (logical_qubits, T-depth, T-count)
envelope for QAE-based derivative pricing.

Scoped: only derivative-pricing, risk-management, simulation-monte-carlo,
insurance-actuarial. Everything else → not_applicable.

Usage:
    python -m p3_thematic_synthesis.s3_quantum_advantage.chakrabarti_2021.assess_chakrabarti
    python -m p3_thematic_synthesis.s3_quantum_advantage.chakrabarti_2021.assess_chakrabarti --silo derivative-pricing
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

FRAMEWORK_ID = "chakrabarti_2021"
_MODULE_ROOT = Path(__file__).resolve().parent
THRESHOLDS_PATH = _MODULE_ROOT / "chakrabarti_thresholds.json"
OUTPUT_PATH = _MODULE_ROOT / "results" / "chakrabarti_results.json"


def load_thresholds() -> dict:
    return json.loads(THRESHOLDS_PATH.read_text(encoding="utf-8"))


def _is_applicable_silo(silo: str, applicable: list[str]) -> bool:
    return silo in applicable


def _is_qae_family(algo_family: str, applicable_families: list[str]) -> bool:
    return algo_family in applicable_families


def _read_resources(experiment: dict, derived: dict | None) -> tuple[int | None, int | None, int | None]:
    """Extract (logical_qubits, T-count, T-depth).

    T-depth is read from quantum_resources.t_depth if reported; otherwise
    falls back to quantum_resources.circuit_depth as a loose proxy (Chakrabarti
    cares about T-gate depth specifically, but circuit depth is a conservative
    upper bound when T-depth is unreported).
    """
    qr = experiment.get("quantum_resources") or {}

    qubits = qr.get("num_qubits")
    if not isinstance(qubits, (int, float)) or qubits <= 0:
        qubits = None
    else:
        qubits = int(qubits)

    t_count: int | None = None
    tc = qr.get("t_count")
    if isinstance(tc, (int, float)) and tc > 0:
        t_count = int(tc)
    else:
        oracle_M, _ = estimate_oracle_complexity(experiment, derived)
        if oracle_M is not None and oracle_M > 0:
            t_count = oracle_M

    t_depth: int | None = None
    td = qr.get("t_depth")
    if isinstance(td, (int, float)) and td > 0:
        t_depth = int(td)
    else:
        cd = qr.get("circuit_depth")
        if isinstance(cd, (int, float)) and cd > 0:
            t_depth = int(cd)  # proxy: circuit_depth upper-bounds T-depth

    return qubits, t_count, t_depth


def _assess_one(
    experiment: dict, silo: str, thresholds: dict, derived: dict | None
) -> tuple[str, str, dict]:
    applicable_silos = thresholds["applicable_silos"]
    applicable_families = thresholds["applicable_algorithm_families"]
    envelope = thresholds["advantage_envelope"]

    algo = experiment.get("algorithm") or {}
    algo_family = algo.get("family", "unknown")

    extras: dict = {
        "silo_applicable": _is_applicable_silo(silo, applicable_silos),
        "algorithm_is_qae_based": _is_qae_family(algo_family, applicable_families),
    }

    # Gate 1: silo scope
    if not extras["silo_applicable"]:
        return (
            "not_applicable",
            f"Silo '{silo}' outside Chakrabarti's scope (derivative pricing / risk / MC only).",
            extras,
        )

    qubits, t_count, t_depth = _read_resources(experiment, derived)
    extras["logical_qubits_reported"] = qubits
    extras["t_count_reported"] = t_count
    extras["t_depth_reported"] = t_depth
    extras["t_depth_source"] = (
        "t_depth" if (experiment.get("quantum_resources") or {}).get("t_depth")
        else "circuit_depth_proxy" if t_depth is not None
        else None
    )
    extras["envelope_min_qubits"] = envelope["min_logical_qubits"]
    extras["envelope_min_t_count"] = envelope["min_t_count"]
    extras["envelope_min_t_depth"] = envelope["min_t_depth"]
    extras["envelope_max_qubits"] = envelope["max_logical_qubits"]
    extras["envelope_max_t_count"] = envelope["max_t_count"]
    extras["envelope_max_t_depth"] = envelope["max_t_depth"]

    # Gate 2: algorithm family check
    if not extras["algorithm_is_qae_based"] and algo_family != "unknown":
        return (
            "conditional",
            f"Algorithm '{algo_family}' is not QAE-based. Chakrabarti's threshold analysis "
            "assumes QAE for derivative pricing; different algorithms have unknown resource profiles.",
            extras,
        )

    # Gate 3: no resources → insufficient_data
    if qubits is None and t_count is None and t_depth is None:
        return (
            "insufficient_data",
            f"No logical qubits, T-count, or T-depth reported. Chakrabarti envelope: "
            f"min {envelope['min_logical_qubits']} qubits / {envelope['min_t_count']:.1e} T-count "
            f"/ {envelope['min_t_depth']:.1e} T-depth.",
            extras,
        )

    min_q = envelope["min_logical_qubits"]
    min_t = envelope["min_t_count"]
    min_td = envelope["min_t_depth"]
    max_q = envelope["max_logical_qubits"]
    max_t = envelope["max_t_count"]
    max_td = envelope["max_t_depth"]

    extras["qubit_margin"] = (qubits / min_q) if qubits else None
    extras["t_count_margin"] = (t_count / min_t) if t_count else None
    extras["t_depth_margin"] = (t_depth / min_td) if t_depth else None

    # Assess against envelope
    def _bucket(val: int | None, lo: float, hi: float) -> str | None:
        if val is None:
            return None
        if val < lo:
            return "below"
        if val <= hi:
            return "within"
        return "above"

    q_status = _bucket(qubits, min_q, max_q)
    t_status = _bucket(t_count, min_t, max_t)
    td_status = _bucket(t_depth, min_td, max_td)

    extras["qubit_vs_envelope"] = q_status
    extras["t_count_vs_envelope"] = t_status
    extras["t_depth_vs_envelope"] = td_status

    statuses = [s for s in [q_status, t_status, td_status] if s is not None]

    # Both/all below → fails
    if all(s == "below" for s in statuses):
        return (
            "fails",
            f"Resources below Chakrabarti floor: "
            f"qubits={qubits} < {min_q}, T-count={t_count} < {min_t:.1e}, T-depth={t_depth} < {min_td:.1e}. "
            "Problem hasn't reached derivative-pricing complexity for QAE advantage.",
            extras,
        )

    # Any within, none above → potentially_viable (but downgrade if T-depth missing)
    if "within" in statuses and "above" not in statuses:
        if td_status is None:
            return (
                "conditional",
                f"Qubits/T-count within Chakrabarti envelope but T-depth not reported. "
                f"Chakrabarti envelope T-depth range: {min_td:.1e}–{max_td:.1e}. "
                f"Cannot confirm runtime feasibility under 10 MHz T-gate target.",
                extras,
            )
        return (
            "potentially_viable",
            f"Resources within Chakrabarti envelope (re-param to Riemann no-norm): "
            f"qubits={qubits}, T-count={t_count}, T-depth={t_depth}. "
            "Hardware needs 10 MHz T-gate rate (currently ~10 kHz).",
            extras,
        )

    # Above envelope (any dimension) → conditional (exceeds known-efficient methods)
    if "above" in statuses:
        return (
            "conditional",
            f"Resources exceed Chakrabarti envelope upper bound: "
            f"qubits={qubits} vs max {max_q}, T-count={t_count} vs max {max_t:.1e}, "
            f"T-depth={t_depth} vs max {max_td:.1e}. "
            "May indicate less-efficient algorithm than re-parameterization method.",
            extras,
        )

    # Mixed (one below, one within) → conditional
    if "below" in statuses and "within" in statuses:
        return (
            "conditional",
            f"Mixed resources: some below floor, some within envelope. "
            f"Qubits={qubits} ({q_status}), T-count={t_count} ({t_status}), T-depth={t_depth} ({td_status}).",
            extras,
        )

    # Only below (single-resource) → fails
    if all(s == "below" for s in statuses):
        return (
            "fails",
            f"Reported resources below Chakrabarti floor.",
            extras,
        )

    # Only one resource present and within → conditional
    if statuses == ["within"]:
        return (
            "conditional",
            "Partial resource data within Chakrabarti envelope; other resources unknown.",
            extras,
        )

    return "insufficient_data", "Unable to classify against Chakrabarti envelope.", extras


def run_assessment(silo_filter: str | None = None) -> dict:
    thresholds = load_thresholds()
    derived_lookup = load_derived_fields()
    verdicts: list[dict] = []

    for envelope_data, experiment in iter_experiments(silo_filter=silo_filter):
        paper_id = envelope_data["paper_id"]
        exp_id = experiment.get("experiment_id", "?")
        silo = envelope_data["silo"]
        derived = get_derived(derived_lookup, paper_id, exp_id)

        verdict, reasoning, extras = _assess_one(experiment, silo, thresholds, derived)
        extras["maturity_level"] = compute_maturity_level(experiment)

        has_resources = (
            extras.get("logical_qubits_reported") is not None
            or extras.get("t_count_reported") is not None
            or extras.get("t_depth_reported") is not None
        )
        confidence = (
            "high" if has_resources and extras.get("silo_applicable")
            else "medium" if extras.get("silo_applicable")
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
                "target_error": 0.002,
                "t_gate_rate_target_hz": 1e7,
                "benchmark_derivative": "autocallable / TARF",
                "method": "re-parameterization (QSP-polished QAE)",
            },
            quantitative_margin=margin,
            framework_specific=extras,
        ))

    payload = build_output_payload(FRAMEWORK_ID, verdicts)
    save_payload(payload, OUTPUT_PATH)
    return payload


def main():
    p = argparse.ArgumentParser(description="Chakrabarti et al. (2021) quantum advantage assessment")
    p.add_argument("--silo", help="Filter to specific silo")
    args = p.parse_args()

    payload = run_assessment(args.silo)
    print_summary(payload)
    print(f"\nResults saved to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
