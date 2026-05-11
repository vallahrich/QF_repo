"""Rønnow et al. (2014) benchmark-validity assessment.

Polices whether an advantage/speedup/supremacy claim is well-defined and
whether the classical comparator is fair.  This is the first layer in the
4-core + 1-veto design: every paper that claims "advantage", "speedup", or
"supremacy/utility" must pass Rønnow before the practicality and resource
layers are even consulted.

The assessor does NOT evaluate whether the claimed speedup is *large enough*
or whether the resources are *feasible*.  Those are downstream layers.

Usage:
    python -m p3_thematic_synthesis.s3_quantum_advantage.ronnow.assess_ronnow
    python -m p3_thematic_synthesis.s3_quantum_advantage.ronnow.assess_ronnow --silo portfolio-optimization
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

FRAMEWORK_ID = "ronnow_2014"
_MODULE_ROOT = Path(__file__).resolve().parent
THRESHOLDS_PATH = _MODULE_ROOT / "ronnow_thresholds.json"
OUTPUT_PATH = _MODULE_ROOT / "results" / "ronnow_results.json"


def load_thresholds() -> dict:
    return json.loads(THRESHOLDS_PATH.read_text(encoding="utf-8"))


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _has_speedup_claim(experiment: dict, claim_keywords: list[str]) -> tuple[bool, str]:
    """Check whether the experiment or its parent paper claims an advantage."""
    complexity = experiment.get("complexity_analysis") or {}
    algo = experiment.get("algorithm") or {}
    impl = experiment.get("implementation_details") or {}
    pi = experiment.get("problem_instance") or {}

    # Build a text blob from relevant fields
    parts = [
        str(complexity.get("speedup_type", "")),
        str(complexity.get("speedup_claimed", "")),
        str(complexity.get("advantage_claim", "")),
        str(algo.get("claimed_advantage", "")),
        str(algo.get("description", "")),
        str(impl.get("description", "")),
        str(pi.get("description", "")),
    ]
    text = " ".join(parts).lower()

    # Explicit structured speedup
    speedup_type = complexity.get("speedup_type")
    if speedup_type and speedup_type not in ("none", "none_proven", "unknown", ""):
        return True, f"Structured speedup_type='{speedup_type}'"

    # Keyword scan
    for kw in claim_keywords:
        if kw.lower() in text:
            return True, f"Keyword match: '{kw}'"

    return False, "No speedup/advantage claim detected in experiment fields"


def _check_classical_baseline(experiment: dict, weak_keywords: list[str]) -> tuple[str, str]:
    """Return (status, reasoning) for classical baseline quality.

    status: 'named' | 'weak' | 'missing'
    """
    complexity = experiment.get("complexity_analysis") or {}
    algo = experiment.get("algorithm") or {}

    baseline_fields = [
        complexity.get("classical_algorithm"),
        complexity.get("classical_baseline"),
        complexity.get("classical_method"),
        algo.get("classical_comparator"),
    ]
    baseline = next((str(b) for b in baseline_fields if b), None)

    if baseline is None:
        return "missing", "No classical baseline algorithm identified"

    baseline_lower = baseline.lower()
    for kw in weak_keywords:
        if kw.lower() in baseline_lower:
            return "weak", f"Classical baseline '{baseline}' matches weak-baseline signal '{kw}'"

    return "named", f"Classical baseline identified: '{baseline}'"


def _check_comparison_type(experiment: dict, valid_types: list[str]) -> tuple[str, str]:
    """Check whether the speedup comparison type is defined.

    Return (status, reasoning).  status: 'defined' | 'undefined'
    """
    complexity = experiment.get("complexity_analysis") or {}

    ctype = (
        complexity.get("comparison_type")
        or complexity.get("speedup_type")
        or complexity.get("advantage_type")
    )

    if ctype and str(ctype).lower() in [v.lower() for v in valid_types]:
        return "defined", f"Comparison type: '{ctype}'"

    # Infer from context
    if complexity.get("quantum_complexity") and complexity.get("classical_complexity"):
        return "defined", "Algorithmic comparison inferred (both complexities stated)"

    impl = experiment.get("implementation_details") or {}
    if complexity.get("wall_clock_quantum") or impl.get("quantum_execution_time"):
        if complexity.get("wall_clock_classical"):
            return "defined", "Empirical wall-clock comparison inferred"

    return "undefined", "Comparison type not specified or inferable"


def _check_instance_fairness(
    experiment: dict, warning_signals: list[str]
) -> tuple[bool, list[str]]:
    """Return (has_concerns, list_of_concerns)."""
    pi = experiment.get("problem_instance") or {}
    impl = experiment.get("implementation_details") or {}

    text = " ".join([
        str(pi.get("description", "")),
        str(pi.get("problem_type", "")),
        str(impl.get("description", "")),
        str(impl.get("instance_selection", "")),
    ]).lower()

    concerns: list[str] = []
    for signal in warning_signals:
        if signal.lower() in text:
            concerns.append(signal)

    # Small qubit counts as fairness concern
    qr = experiment.get("quantum_resources") or {}
    qubits = qr.get("num_qubits")
    if isinstance(qubits, (int, float)) and 0 < qubits <= 4:
        concerns.append(f"very small qubit count ({int(qubits)})")

    return len(concerns) > 0, concerns


def _check_scaling_evidence(experiment: dict, min_sizes: int) -> tuple[bool, str]:
    """Check whether multiple problem sizes were tested."""
    complexity = experiment.get("complexity_analysis") or {}
    impl = experiment.get("implementation_details") or {}

    # Look for scaling data
    sizes = (
        complexity.get("problem_sizes_tested")
        or impl.get("problem_sizes")
        or impl.get("scaling_data")
    )
    if isinstance(sizes, list) and len(sizes) >= min_sizes:
        return True, f"{len(sizes)} problem sizes tested"

    # Infer from num_assets range or dataset sizes
    pi = experiment.get("problem_instance") or {}
    if isinstance(pi.get("num_assets"), list) and len(pi["num_assets"]) >= min_sizes:
        return True, f"Multiple asset counts: {pi['num_assets']}"

    return False, "No multi-size scaling evidence found"


def _check_optimal_parameters(
    experiment: dict, warning_signals: list[str]
) -> tuple[bool, list[str]]:
    """Check for Rønnow Section IV.A concern: fixed/suboptimal parameters.

    If quantum or classical side uses fixed parameters rather than
    size-optimized ones, the comparison may fake or mask speedup.
    """
    impl = experiment.get("implementation_details") or {}
    algo = experiment.get("algorithm") or {}
    complexity = experiment.get("complexity_analysis") or {}

    text = " ".join([
        str(impl.get("description", "")),
        str(impl.get("parameter_selection", "")),
        str(algo.get("description", "")),
        str(complexity.get("methodology_notes", "")),
    ]).lower()

    concerns: list[str] = []
    for signal in warning_signals:
        if signal.lower() in text:
            concerns.append(signal)

    return len(concerns) > 0, concerns


def _check_hardware_parity(
    experiment: dict, warning_signals: list[str]
) -> tuple[bool, list[str]]:
    """Check for Rønnow Section IV.B concern: hardware resource scaling parity.

    If a quantum device using N qubits is compared against a single-core
    classical machine, a parallel speedup may be mistaken for a quantum one.
    """
    complexity = experiment.get("complexity_analysis") or {}
    impl = experiment.get("implementation_details") or {}

    text = " ".join([
        str(complexity.get("classical_baseline", "")),
        str(complexity.get("classical_algorithm", "")),
        str(impl.get("classical_hardware", "")),
        str(impl.get("description", "")),
    ]).lower()

    concerns: list[str] = []
    for signal in warning_signals:
        if signal.lower() in text:
            concerns.append(signal)

    return len(concerns) > 0, concerns


# ---------------------------------------------------------------------------
# Main assessment logic
# ---------------------------------------------------------------------------

def _assess_one(
    experiment: dict, thresholds: dict, derived: dict | None
) -> tuple[str, str, dict]:
    criteria = thresholds["validity_criteria"]

    # FIX 2026-05-02 (QA-1 open-blocker): Rønnow et al. (2014) was developed
    # as a *quantum annealing* benchmark-validity protocol. The four pitfalls
    # (optimal-annealing-time tuning, fixed-time artefacts, hardware parity,
    # instance-class fairness) are annealing-specific. Applying the framework
    # to gate-based families that have no analogue (e.g. variational
    # eigensolvers, QML classifiers, Hamiltonian-simulation primitives) is a
    # category stretch. We therefore early-return `not_applicable` for
    # families outside the gate-based set where the Rønnow taxonomy genuinely
    # transfers (QAOA / Grover / amplitude estimation / amplitude
    # amplification), and for any other family unless the extraction
    # explicitly flags the paper as a benchmark-validity study.
    _RONNOW_APPLICABLE_FAMILIES = {
        "qaoa", "grover", "amplitude-estimation", "amplitude_estimation",
        "amplitude-amplification", "amplitude_amplification",
        # Annealing-domain families that the original Rønnow paper directly addresses
        "quantum-annealing", "quantum_annealing", "qaoa-annealing",
    }
    algo = experiment.get("algorithm") or {}
    family = str(algo.get("family", "")).lower().strip()
    is_validity_study = bool(experiment.get("benchmark_validity_study", False))

    if family and family not in _RONNOW_APPLICABLE_FAMILIES and not is_validity_study:
        extras: dict = {
            "family_gate": "not_applicable",
            "algorithm_family": family,
            "applicable_families": sorted(_RONNOW_APPLICABLE_FAMILIES),
        }
        return (
            "not_applicable",
            f"Rønnow benchmark-validity: algorithm family '{family}' is outside "
            f"the framework's applicable set "
            f"{sorted(_RONNOW_APPLICABLE_FAMILIES)} and the experiment is not a "
            f"benchmark-validity study. Rønnow's four pitfalls are "
            f"annealing/QAOA/Grover-specific; applying them to '{family}' is a "
            f"category stretch (audit fix 2026-05-02, QA-1).",
            extras,
        )

    # 1. Does the experiment claim an advantage?
    has_claim, claim_reason = _has_speedup_claim(
        experiment, criteria["speedup_claim_present"]["claim_keywords"]
    )

    extras: dict = {
        "has_speedup_claim": has_claim,
        "claim_reason": claim_reason,
    }

    if not has_claim:
        return (
            "not_applicable",
            f"Rønnow benchmark-validity: {claim_reason}. "
            "No advantage claim to validate — framework does not apply.",
            extras,
        )

    # 2. Is the classical baseline identified and fair?
    baseline_status, baseline_reason = _check_classical_baseline(
        experiment, criteria["classical_baseline_identified"]["weak_baseline_keywords"]
    )
    extras["baseline_status"] = baseline_status
    extras["baseline_reason"] = baseline_reason

    # 3. Is the comparison type defined?
    type_status, type_reason = _check_comparison_type(
        experiment, criteria["comparison_type_defined"]["valid_types"]
    )
    extras["comparison_type_status"] = type_status
    extras["comparison_type_reason"] = type_reason

    # 4. Instance fairness (optional, adds caution flags)
    has_fairness_concerns, fairness_concerns = _check_instance_fairness(
        experiment, criteria["instance_fairness"]["warning_signals"]
    )
    extras["has_fairness_concerns"] = has_fairness_concerns
    extras["fairness_concerns"] = fairness_concerns

    # 5. Scaling evidence (optional)
    has_scaling, scaling_reason = _check_scaling_evidence(
        experiment, criteria["scaling_evidence"]["minimum_sizes_for_scaling"]
    )
    extras["has_scaling_evidence"] = has_scaling
    extras["scaling_reason"] = scaling_reason

    # 6. Optimal parameters (Rønnow Section IV.A)
    param_criteria = criteria.get("optimal_parameters", {})
    has_param_concerns, param_concerns = _check_optimal_parameters(
        experiment, param_criteria.get("warning_signals", [])
    )
    extras["has_parameter_concerns"] = has_param_concerns
    extras["parameter_concerns"] = param_concerns

    # 7. Hardware resource parity (Rønnow Section IV.B, Eq. 4-5)
    parity_criteria = criteria.get("hardware_resource_parity", {})
    has_parity_concerns, parity_concerns = _check_hardware_parity(
        experiment, parity_criteria.get("warning_signals", [])
    )
    extras["has_hardware_parity_concerns"] = has_parity_concerns
    extras["hardware_parity_concerns"] = parity_concerns

    # --- Collect all caution flags ---
    all_concerns: list[str] = []
    if has_fairness_concerns:
        all_concerns.extend(f"instance: {c}" for c in fairness_concerns)
    if has_param_concerns:
        all_concerns.extend(f"parameters: {c}" for c in param_concerns)
    if has_parity_concerns:
        all_concerns.extend(f"hw-parity: {c}" for c in parity_concerns)

    # --- Verdict logic ---

    # No baseline at all → fails (undefined speedup)
    if baseline_status == "missing" and type_status == "undefined":
        return (
            "fails",
            f"Rønnow: Advantage claimed ({claim_reason}) but no classical baseline "
            f"identified and comparison type undefined. Speedup claim is not well-defined.",
            extras,
        )

    # Weak baseline → conditional
    if baseline_status == "weak":
        reasoning = (
            f"Rønnow: Advantage claimed ({claim_reason}). {baseline_reason}. "
            f"Comparison type: {type_reason}."
        )
        if all_concerns:
            reasoning += f" Additional concerns: {', '.join(all_concerns)}."
        return "conditional", reasoning, extras

    # Missing baseline but type defined → conditional
    if baseline_status == "missing":
        reasoning = (
            f"Rønnow: Advantage claimed ({claim_reason}). {baseline_reason}. "
            f"Comparison type: {type_reason}."
        )
        return "conditional", reasoning, extras

    # Named baseline, type undefined → conditional
    if type_status == "undefined":
        reasoning = (
            f"Rønnow: Advantage claimed ({claim_reason}). {baseline_reason}. "
            f"But {type_reason} — unclear whether speedup is algorithmic, hardware, or implementation."
        )
        return "conditional", reasoning, extras

    # Named baseline + defined type but significant concerns → conditional
    if all_concerns:
        reasoning = (
            f"Rønnow: Well-defined claim ({claim_reason}). {baseline_reason}. "
            f"{type_reason}. BUT concerns: {', '.join(all_concerns)}."
        )
        return "conditional", reasoning, extras

    # All clear
    reasoning = (
        f"Rønnow: Well-defined advantage claim. {baseline_reason}. "
        f"{type_reason}."
    )
    if has_scaling:
        reasoning += f" {scaling_reason}."
    return "viable", reasoning, extras


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

        # Confidence: high if we can clearly determine claim + baseline status
        has_claim = extras.get("has_speedup_claim", False)
        baseline_clear = extras.get("baseline_status") in ("named", "missing")
        confidence = (
            "high" if has_claim and baseline_clear
            else "medium" if has_claim
            else "low"
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
                "methodology": "Rønnow benchmark-validity taxonomy applied to extracted experiment metadata",
                "checks": ["speedup_claim_present", "classical_baseline_quality",
                           "comparison_type_defined", "instance_fairness", "scaling_evidence"],
            },
            quantitative_margin=None,
            framework_specific=extras,
        ))

    payload = build_output_payload(FRAMEWORK_ID, verdicts)
    save_payload(payload, OUTPUT_PATH)
    return payload


def main():
    p = argparse.ArgumentParser(description="Rønnow et al. (2014) benchmark-validity assessment")
    p.add_argument("--silo", help="Filter to specific silo")
    args = p.parse_args()

    payload = run_assessment(args.silo)
    print_summary(payload)
    print(f"\nResults saved to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
