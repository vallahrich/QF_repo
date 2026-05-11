"""Validate extracted benchmark JSON against schema and semantic rules.

Two validation layers:
  1. JSON Schema validation against benchmark_schema.json
  2. Semantic range checks (qubits > 0, accuracy in [0,1], etc.)

Usage:
    python -m p3_thematic_synthesis.s2_quantitative.scripts.validate_benchmarks path/to/extraction.json
"""

import argparse
import json
import sys
from pathlib import Path

from jsonschema import Draft202012Validator

_QUANT_ROOT = Path(__file__).resolve().parents[1]
_PROJECT_ROOT = Path(__file__).resolve().parents[3]

SCHEMA_PATH = _QUANT_ROOT / "config" / "benchmark_schema.json"

# Metrics where values should be in [0, 1] (or [0, 100] if percentages)
_BOUNDED_METRICS = frozenset({
    "accuracy", "precision", "recall", "f1_score", "auc_roc", "auc",
    "approximation_ratio", "feasibility_percentage", "ground_state_probability",
    "success_probability", "var_accuracy", "specificity",
})

# Metrics that must be non-negative (but are not bounded above)
_NON_NEGATIVE_METRICS = frozenset({
    "price_error", "cvar_estimation_error", "execution_time", "convergence_time",
    "num_qubits", "circuit_depth", "num_shots", "iterations_to_converge",
    "gate_count", "cnot_count", "t_count", "t_depth",
})

# Allowed units for results[].unit
_UNIT_VOCAB = frozenset({
    "seconds", "s", "ms", "us", "ns", "minutes", "hours",
    "shots", "count", "iterations", "samples",
    "ratio", "percent", "%", "pct", "percentage", "fraction",
    "unitless", "bps", "basis_points",
    "qubits", "gates", "bits",
    "usd", "dollars", "bp",
})

# Thesis scope: gate-based quantum computing only.
_SCOPE_OUT_HARDWARE_TYPES = frozenset({"quantum_annealer"})
_SCOPE_OUT_ALGORITHM_FAMILIES = frozenset({"quantum-annealing", "qubo"})


def _load_schema() -> dict:
    """Load the benchmark JSON schema from disk."""
    with open(SCHEMA_PATH, encoding="utf-8") as f:
        return json.load(f)


def validate_schema(data: dict) -> list[str]:
    """Validate data against the benchmark JSON schema.

    Returns a list of error messages. Empty list means valid.
    """
    schema = _load_schema()
    validator = Draft202012Validator(schema)
    errors: list[str] = []
    for error in sorted(validator.iter_errors(data), key=lambda e: list(e.path)):
        path = ".".join(str(p) for p in error.absolute_path) or "(root)"
        errors.append(f"Schema error at {path}: {error.message}")
    return errors


def _safe_number(val):
    """Coerce a value to a number for comparison, returning None on failure."""
    if val is None:
        return None
    if isinstance(val, (int, float)):
        return val
    if isinstance(val, str):
        try:
            return int(val)
        except ValueError:
            try:
                return float(val)
            except ValueError:
                return None
    return None


def _coerce_int_or_null(val):
    """Coerce a value to int, or None if not representable.

    Handles strings (numeric or free-text), bools (rejected),
    lists (takes max of numeric elements), and empty strings.
    """
    if val is None or isinstance(val, bool):
        return None if isinstance(val, bool) else None
    if isinstance(val, int):
        return val
    if isinstance(val, float):
        return int(val) if val == int(val) else None
    if isinstance(val, str):
        s = val.strip()
        if not s:
            return None
        # Try direct parse
        try:
            return int(s)
        except ValueError:
            pass
        try:
            f = float(s)
            return int(f) if f == int(f) else None
        except ValueError:
            pass
        # Try extracting first integer from string like "3_qubits" or "1-6"
        import re as _re
        m = _re.search(r"-?\d+", s)
        if m:
            try:
                return int(m.group(0))
            except ValueError:
                return None
        return None
    if isinstance(val, list):
        nums = [_coerce_int_or_null(v) for v in val]
        nums = [n for n in nums if n is not None]
        return max(nums) if nums else None
    return None


def _coerce_number_or_null(val):
    """Coerce to int|float or None."""
    if val is None or isinstance(val, bool):
        return None
    if isinstance(val, (int, float)):
        return val
    if isinstance(val, str):
        s = val.strip()
        if not s:
            return None
        try:
            return int(s)
        except ValueError:
            pass
        try:
            return float(s)
        except ValueError:
            pass
        import re as _re
        m = _re.search(r"-?\d+(?:\.\d+)?(?:[eE][+-]?\d+)?", s)
        if m:
            try:
                return float(m.group(0))
            except ValueError:
                return None
        return None
    if isinstance(val, list):
        nums = [_coerce_number_or_null(v) for v in val]
        nums = [n for n in nums if n is not None]
        return max(nums) if nums else None
    return None


def _coerce_bool_or_null(val):
    """Coerce to bool|None. LLMs often emit 'yes', 'no', 'likely', 'present'."""
    if val is None or isinstance(val, bool):
        return val
    if isinstance(val, (int, float)):
        return bool(val)
    if isinstance(val, str):
        s = val.strip().lower()
        if s in {"true", "yes", "y", "1", "present", "available"}:
            return True
        if s in {"false", "no", "n", "0", "absent", "unavailable", "none"}:
            return False
        if s in {"likely", "likely_true", "probable", "probable_true"}:
            return True
        if s in {"unlikely", "likely_false", "improbable"}:
            return False
        # 'not_assessed', 'insufficient_data', 'unknown', 'tbd', 'likely_significant', ''
        return None
    return None



def validate_ranges(data: dict) -> list[str]:
    """Check semantic range constraints on extracted data.

    Returns a list of warning messages. These are non-fatal but
    indicate potential extraction errors.
    """
    warnings: list[str] = []

    # Paper-level checks
    year = _safe_number((data.get("paper_metadata") or {}).get("year"))
    if year is not None and not (2015 <= year <= 2027):
        warnings.append(
            f"paper_metadata.year={year} outside expected range [2015, 2027]"
        )

    for i, exp in enumerate(data.get("experiments", [])):
        prefix = f"experiments[{i}]"

        # Scope: reject annealing algorithm families (gate-based-only thesis)
        algo = exp.get("algorithm") or {}
        fam = (algo.get("family") or "").strip().lower()
        if fam in _SCOPE_OUT_ALGORITHM_FAMILIES:
            warnings.append(
                f"{prefix}.algorithm.family={fam!r} is out of scope "
                f"(gate-based thesis) — remove or reclassify as qaoa/grover/other-gate-based"
            )

        # Scope: reject annealer hardware (gate-based-only thesis)
        hw = exp.get("hardware") or {}
        hw_type = (hw.get("type") or "").strip().lower()
        if hw_type in _SCOPE_OUT_HARDWARE_TYPES:
            warnings.append(
                f"{prefix}.hardware.type={hw_type!r} is out of scope "
                f"(gate-based thesis) — paper should have been filtered upstream"
            )

        # Quantum resource checks (coerce strings to numbers defensively)
        qr = exp.get("quantum_resources") or {}
        num_qubits = _safe_number(qr.get("num_qubits"))
        if num_qubits is not None and (num_qubits < 1 or num_qubits > 100_000):
            warnings.append(
                f"{prefix}.quantum_resources.num_qubits={num_qubits} "
                f"outside expected range [1, 100000]"
            )

        depth = _safe_number(qr.get("circuit_depth"))
        if depth is not None and depth < 0:
            warnings.append(
                f"{prefix}.quantum_resources.circuit_depth={depth} "
                f"must be non-negative"
            )

        depth_t = _safe_number(qr.get("circuit_depth_transpiled"))
        if depth is not None and depth_t is not None and depth_t < depth:
            warnings.append(
                f"{prefix}.quantum_resources.circuit_depth_transpiled={depth_t} "
                f"< circuit_depth={depth} (transpiled depth should be >= logical depth)"
            )

        shots = _safe_number(qr.get("num_shots"))
        if shots is not None and shots < 1:
            warnings.append(
                f"{prefix}.quantum_resources.num_shots={shots} must be positive"
            )

        # Error-correction cross-field: physical >= logical when both present
        ec = qr.get("error_correction") or {}
        if isinstance(ec, dict):
            log_q = _safe_number(num_qubits)  # logical count proxy when qubit_type == 'logical'
            tot_phys = _safe_number(ec.get("total_physical_qubits"))
            ppl = _safe_number(ec.get("physical_qubits_per_logical"))
            if log_q is not None and tot_phys is not None and tot_phys < log_q:
                warnings.append(
                    f"{prefix}.quantum_resources.error_correction.total_physical_qubits={tot_phys} "
                    f"< num_qubits={log_q} (physical qubits must be >= logical qubits)"
                )
            if ppl is not None and ppl < 1:
                warnings.append(
                    f"{prefix}.quantum_resources.error_correction.physical_qubits_per_logical={ppl} must be >= 1"
                )

        # Result value checks
        for j, result in enumerate(exp.get("results", [])):
            name = result.get("metric_name", "")
            name_lc = name.lower()
            val = result.get("value")
            unit_raw = (result.get("unit") or "").strip()
            unit = unit_raw.lower()

            # Unit-vocabulary check (warn only; preserves freeform units)
            if unit_raw and unit not in _UNIT_VOCAB:
                warnings.append(
                    f"{prefix}.results[{j}].unit={unit_raw!r} not in standard vocabulary "
                    f"(allowed: seconds, ms, percent, ratio, unitless, ...)"
                )

            if not isinstance(val, (int, float)):
                continue

            # Non-negative metrics
            if name_lc in _NON_NEGATIVE_METRICS and val < 0:
                warnings.append(
                    f"{prefix}.results[{j}].{name}={val} must be non-negative"
                )

            if name_lc in _BOUNDED_METRICS:
                is_percent = unit in {"percent", "%", "pct", "percentage"}
                if val < 0:
                    warnings.append(
                        f"{prefix}.results[{j}].{name}={val} is negative; expected in [0,1] (fraction) or [0,100] (percent)"
                    )
                elif is_percent and val > 100:
                    warnings.append(
                        f"{prefix}.results[{j}].{name}={val}% exceeds 100"
                    )
                elif not is_percent and 1 < val <= 100:
                    warnings.append(
                        f"{prefix}.results[{j}].{name}={val} with unit={result.get('unit')!r} looks like percent but unit is not labelled — verify fraction vs percent"
                    )
                elif val > 100:
                    warnings.append(
                        f"{prefix}.results[{j}].{name}={val} exceeds 100 for a bounded metric"
                    )

    return warnings


def validate_extraction(data: dict) -> tuple[list[str], list[str]]:
    """Run full validation on an extraction result.

    Returns:
        (errors, warnings) — errors are schema violations (fatal),
        warnings are semantic range issues (non-fatal).
    """
    errors = validate_schema(data)
    warnings = validate_ranges(data)
    return errors, warnings


# ---------------------------------------------------------------------------
# Metric name normalization
# ---------------------------------------------------------------------------

# Maps common LLM-generated variations to canonical metric names.
# Keys are lowercase patterns; values are the canonical name.
_METRIC_ALIASES: dict[str, str] = {
    "expected_return_percentage": "expected_return",
    "expected_return_pct": "expected_return",
    "return_percentage": "expected_return",
    "risk_variance": "variance",
    "portfolio_variance": "variance",
    "convergence_time_seconds": "convergence_time",
    "convergence_time_s": "convergence_time",
    "execution_time_seconds": "execution_time",
    "execution_time_s": "execution_time",
    "runtime_seconds": "execution_time",
    "wall_clock_time": "execution_time",
    "f1": "f1_score",
    "f1score": "f1_score",
    "auc": "auc_roc",
    "auroc": "auc_roc",
    "num_qubits_total": "num_qubits",
    "total_qubits": "num_qubits",
    "qubit_count": "num_qubits",
    "circuit_depth_total": "circuit_depth",
    "total_depth": "circuit_depth",
    "price_error_absolute": "price_error",
    "price_error_relative": "price_error",
    "option_price_error": "price_error",
    "pricing_error": "price_error",
    "sharpe": "sharpe_ratio",
    "ground_state_prob": "ground_state_probability",
    "success_probability_postselection": "success_probability",
    "expected_success_probability_postselection": "success_probability",
    "default_prediction_accuracy": "accuracy",
    "classification_accuracy": "accuracy",
}


def normalize_metric_name(name: str) -> str:
    """Normalize a metric name to its canonical form.

    Returns the canonical name if a known alias exists,
    otherwise returns the original lowercased name.
    """
    lower = name.lower().strip()
    return _METRIC_ALIASES.get(lower, lower)


def normalize_extraction_metrics(data: dict) -> dict:
    """Normalize all metric names in an extraction to canonical forms.

    Also sanitizes LLM output quirks:
    - Fixes data_source values like "text/figure" → "text"
    - Converts array/dict values to string representations
    - Fixes silo name underscores to hyphens

    Modifies and returns the data dict in-place.
    """
    _VALID_DATA_SOURCES = {"table", "figure", "text", "computed"}

    # Map invalid algorithm.family values back to the schema's closed vocabulary.
    # LLMs sometimes emit Phase-2 taxonomy codes (SA-01..SA-11 from
    # shared/config/unified_taxonomy.json, methodology_tags), which is a coarser
    # vocabulary than benchmark_schema.json's gate-based families. Annealing
    # families are out of scope and are mapped to "other" so the scope check
    # in validate_ranges() flags them. Canonical mapping:
    #   SA-01 quantum-annealing-qubo  → other        (out of scope — gate-based thesis)
    #   SA-02 variational-nisq        → vqe          (QAOA papers are re-labelled
    #                                                  qaoa upstream by the prompt;
    #                                                  vqe is the safe catch-all)
    #   SA-03 amplitude-estimation    → amplitude-estimation (identical)
    #   SA-04 quantum-ml              → quantum-ml (identical)
    #   SA-05 grover-search           → grover
    #   SA-06 quantum-linear-systems  → hhl
    #   SA-07 quantum-walks           → quantum-walk
    #   SA-08 hybrid-quantum-classical → hybrid
    #   SA-09 quantum-cryptography    → other-gate-based (Shor, QKD, etc.)
    #   SA-10 qft-phase-estimation    → amplitude-estimation (QPE underpins QAE)
    #   SA-11 error-mitigation        → other (not an algorithm per se)
    _FAMILY_FIX = {
        "quantum-annealing-qubo": "other",
        "quantum-annealing": "other",
        "qubo": "other",
        "variational-nisq": "vqe",
        "grover-search": "grover",
        "quantum-linear-systems": "hhl",
        "quantum-walks": "quantum-walk",
        "hybrid-quantum-classical": "hybrid",
        "quantum-cryptography": "other-gate-based",
        "qft-phase-estimation": "amplitude-estimation",
        "error-mitigation": "other",
    }
    _VALID_FAMILIES = {
        "qaoa", "vqe", "amplitude-estimation", "quantum-ml", "quantum-walk",
        "hhl", "hybrid", "grover", "quantum-svm",
        "quantum-simulation", "classical-simulation", "other-gate-based", "other",
    }

    # hardware.type canonical vocabulary + free-form aliases from LLM output
    _VALID_HW_TYPES = {
        "simulator_statevector", "simulator_noisy", "simulator_other",
        "real_qpu_superconducting", "real_qpu_trapped_ion",
        "real_qpu_photonic", "real_qpu_neutral_atom", "not_specified",
    }
    _HW_TYPE_FIX = {
        # superconducting QPU variants
        "ibm_qpu_superconducting": "real_qpu_superconducting",
        "qpu_ibm": "real_qpu_superconducting",
        "gate-based_qpu_superconducting": "real_qpu_superconducting",
        "gate_based_qpu": "real_qpu_superconducting",
        # trapped-ion variants
        "ionq_trapped_ion_qpu": "real_qpu_trapped_ion",
        # photonic
        "photonic_qpu": "real_qpu_photonic",
        "photonic_gate_based_experiment": "real_qpu_photonic",
        # simulator flavours
        "simulator_gate_based": "simulator_statevector",
        "simulator_qiskit": "simulator_statevector",
        "simulator_ibm_qiskit": "simulator_statevector",
        "simulator_qiskit_aer": "simulator_statevector",
        "simulator_aer": "simulator_statevector",
        "simulator_qasm": "simulator_statevector",
        "simulator_ibm_qasm": "simulator_statevector",
        "simulator_cirq": "simulator_statevector",
        "simulator_pennylane": "simulator_statevector",
        "simulator_cuda_q": "simulator_statevector",
        "simulator_neutral_atom": "simulator_statevector",
        "simulator_mps": "simulator_other",
        "simulator_lindblad": "simulator_noisy",
        "simulator_classical": "classical-simulation-placeholder",  # drop below
        "simulator_classical_cpu": "classical-simulation-placeholder",
        "classical_cpu": "classical-simulation-placeholder",
        # generic unknown
        "qpu": "real_qpu_superconducting",
        "quantum_device": "not_specified",
        "quantum_processor": "not_specified",
        "mixed_simulator_and_qpu": "simulator_other",
    }

    # feasibility_horizon canonical enum + aliases
    _VALID_HORIZONS = {
        "current_nisq", "near_term_2_5_years", "medium_term_5_10_years",
        "far_future_10_plus_years", "requires_fault_tolerance",
    }
    _HORIZON_FIX = {
        "near_term": "near_term_2_5_years",
        "near-term": "near_term_2_5_years",
        "near term": "near_term_2_5_years",
        "medium_term": "medium_term_5_10_years",
        "long_term": "far_future_10_plus_years",
        "far_future": "far_future_10_plus_years",
        "requires_ft": "requires_fault_tolerance",
        "fault_tolerant": "requires_fault_tolerance",
        "not_near_term": "far_future_10_plus_years",
        "not_assessed": None,
        "not_applicable": None,
        "unknown": None,
        "tbd": None,
        "theoretical_only": "requires_fault_tolerance",
        "theoretical only": "requires_fault_tolerance",
    }

    # maturity_level canonical enum + aliases
    _VALID_MATURITY = {
        "L0_theory", "L1_noiseless_sim", "L2_noisy_sim",
        "L3_qpu_small", "L4_qpu_scale", "L5_production",
    }
    _MATURITY_FIX = {
        "l0": "L0_theory",
        "l0_theory": "L0_theory",
        "l1": "L1_noiseless_sim",
        "l1_noiseless_sim": "L1_noiseless_sim",
        "l2": "L2_noisy_sim",
        "l2_noisy_sim": "L2_noisy_sim",
        "l2_noiseless_sim": "L1_noiseless_sim",  # common LLM confusion
        "l3": "L3_qpu_small",
        "l3_qpu_small": "L3_qpu_small",
        "l4": "L4_qpu_scale",
        "l4_qpu_scale": "L4_qpu_scale",
        "l5": "L5_production",
        "l5_production": "L5_production",
    }

    # paper_metadata.year: coerce string → int, empty → None
    pm = data.get("paper_metadata") or {}
    y = pm.get("year")
    if isinstance(y, str):
        y_clean = y.strip().split("-")[0].split("/")[0]
        if not y_clean:
            pm["year"] = None
        else:
            coerced = _safe_number(y_clean)
            pm["year"] = int(coerced) if coerced is not None else None
    elif isinstance(y, float):
        pm["year"] = int(y)

    for exp in data.get("experiments", []):
        # Normalize algorithm.family
        algo = exp.get("algorithm") or {}
        fam = algo.get("family", "")
        if fam:
            normalized = fam.replace("_", "-").lower().strip()
            if normalized in _VALID_FAMILIES:
                algo["family"] = normalized
            elif normalized in _FAMILY_FIX:
                algo["family"] = _FAMILY_FIX[normalized]
            elif fam not in _VALID_FAMILIES:
                algo["family"] = "other"

        # Fix string dataset_specification → wrap in object
        pi = exp.get("problem_instance")
        if pi:
            ds = pi.get("dataset_specification")
            if isinstance(ds, str):
                pi["dataset_specification"] = {"description": ds}

        # Coerce string-typed numeric fields in quantum_resources
        qr = exp.get("quantum_resources")
        if qr:
            _INT_QR_FIELDS = (
                "num_qubits", "circuit_depth", "circuit_depth_transpiled",
                "num_shots", "t_count", "t_depth", "gate_count_total",
                "cnot_count", "num_variational_params",
            )
            for nf in _INT_QR_FIELDS:
                qr[nf] = _coerce_int_or_null(qr.get(nf))
            # error_correction nested. Schema requires an object; LLMs often emit
            # ``null`` when the paper does not discuss QEC. Promote ``null`` to an
            # empty object so the schema validator stops flagging this in 631/643
            # otherwise-clean files.
            ec = qr.get("error_correction")
            if ec is None:
                qr["error_correction"] = {}
                ec = qr["error_correction"]
            if isinstance(ec, dict):
                for nf in ("code_distance", "physical_qubits_per_logical", "total_physical_qubits"):
                    ec[nf] = _coerce_int_or_null(ec.get(nf))
                for nf in ("logical_error_rate", "physical_error_rate_assumed"):
                    ec[nf] = _coerce_number_or_null(ec.get(nf))

        # Coerce algorithm.num_layers
        if algo:
            algo["num_layers"] = _coerce_int_or_null(algo.get("num_layers"))

        # Coerce string-typed numeric fields in problem_instance
        if pi:
            for nf in ("num_assets", "time_steps", "num_features", "dataset_size"):
                pi[nf] = _coerce_int_or_null(pi.get(nf))
            # dataset_name: LLM sometimes returns a list, coerce to string
            dn = pi.get("dataset_name")
            if isinstance(dn, list):
                pi["dataset_name"] = ", ".join(str(x) for x in dn) if dn else None
            elif isinstance(dn, dict):
                pi["dataset_name"] = str(dn)
            # data_type: enum
            dt = pi.get("data_type")
            if isinstance(dt, str):
                dt_lc = dt.strip().lower().replace(" ", "_").replace("-", "_")
                _VALID_DT = {"synthetic", "real_market", "proprietary", "public_benchmark"}
                if dt_lc in _VALID_DT:
                    pi["data_type"] = dt_lc
                elif "synth" in dt_lc:
                    pi["data_type"] = "synthetic"
                elif "market" in dt_lc or "real" in dt_lc:
                    pi["data_type"] = "real_market"
                elif "benchmark" in dt_lc or "public" in dt_lc:
                    pi["data_type"] = "public_benchmark"
                elif "propriet" in dt_lc:
                    pi["data_type"] = "proprietary"
                else:
                    pi["data_type"] = None

        # Coerce problem_formulation.num_binary_variables
        pf = exp.get("problem_formulation")
        if isinstance(pf, dict):
            pf["num_binary_variables"] = _coerce_int_or_null(pf.get("num_binary_variables"))

        # Coerce variance_across_runs + other numeric fields in convergence_data
        impl = exp.get("implementation_details") or {}
        cd = impl.get("convergence_data") if isinstance(impl, dict) else None
        if isinstance(cd, dict):
            cd["variance_across_runs"] = _coerce_number_or_null(cd.get("variance_across_runs"))
            cd["iterations_to_converge"] = _coerce_int_or_null(cd.get("iterations_to_converge"))
            cd["num_independent_runs"] = _coerce_int_or_null(cd.get("num_independent_runs"))
            cd["final_loss_value"] = _coerce_number_or_null(cd.get("final_loss_value"))

        # Coerce code_available to bool|None
        if isinstance(impl, dict):
            impl["code_available"] = _coerce_bool_or_null(impl.get("code_available"))
            # numeric-ish fields often emitted as strings
            for nf in ("classical_mc_samples", "num_layers", "ansatz_depth", "p_rounds"):
                impl[nf] = _coerce_int_or_null(impl.get(nf))

        # Coerce scalability_data numeric fields
        for sd in (exp.get("scalability_data") or []):
            if not isinstance(sd, dict):
                continue
            sd["problem_size"] = _coerce_number_or_null(sd.get("problem_size"))
            sd["metric_value"] = _coerce_number_or_null(sd.get("metric_value"))
            sd["num_qubits"] = _coerce_int_or_null(sd.get("num_qubits"))

        # Coerce advantage_assessment booleans + free-text
        aa_ref = exp.get("advantage_assessment")
        if isinstance(aa_ref, dict):
            aa_ref["data_loading_bottleneck"] = _coerce_bool_or_null(
                aa_ref.get("data_loading_bottleneck")
            )
            # advantage_status: enum coercion
            st = aa_ref.get("advantage_status")
            if isinstance(st, str):
                _VALID_ST = {
                    "advantage_demonstrated", "advantage_claimed_not_demonstrated",
                    "parity_with_classical", "classical_still_better",
                    "theoretical_only", "not_assessed",
                }
                st_lc = st.strip().lower().replace(" ", "_").replace("-", "_")
                aa_ref["advantage_status"] = st_lc if st_lc in _VALID_ST else "not_assessed"

            # feasibility_horizon: enum
            fh = aa_ref.get("feasibility_horizon")
            if isinstance(fh, str) and fh:
                fh_lc = fh.strip().lower().replace(" ", "_")
                if fh_lc in _VALID_HORIZONS:
                    aa_ref["feasibility_horizon"] = fh_lc
                elif fh_lc in _HORIZON_FIX:
                    aa_ref["feasibility_horizon"] = _HORIZON_FIX[fh_lc]
                else:
                    t = fh.lower()
                    if "fault" in t:
                        aa_ref["feasibility_horizon"] = "requires_fault_tolerance"
                    elif "far" in t or "long" in t or "decade" in t or "not_near" in t or "10+" in t:
                        aa_ref["feasibility_horizon"] = "far_future_10_plus_years"
                    elif "medium" in t or "5-10" in t or "5_10" in t:
                        aa_ref["feasibility_horizon"] = "medium_term_5_10_years"
                    elif "near" in t or "2-5" in t or "2_5" in t:
                        aa_ref["feasibility_horizon"] = "near_term_2_5_years"
                    elif "nisq" in t or "current" in t:
                        aa_ref["feasibility_horizon"] = "current_nisq"
                    else:
                        aa_ref["feasibility_horizon"] = None

            # maturity_level: enum
            ml = aa_ref.get("maturity_level")
            if isinstance(ml, str) and ml:
                ml_lc = ml.strip().lower()
                if ml in _VALID_MATURITY:
                    pass
                elif ml_lc in _MATURITY_FIX:
                    aa_ref["maturity_level"] = _MATURITY_FIX[ml_lc]
                elif ml_lc.startswith("l") and len(ml_lc) >= 2 and ml_lc[1].isdigit():
                    aa_ref["maturity_level"] = _MATURITY_FIX.get(ml_lc[:2], None)
                else:
                    aa_ref["maturity_level"] = None

        # Normalize hardware.type to schema enum
        hw = exp.get("hardware")
        if isinstance(hw, dict):
            ht = hw.get("type", "")
            if isinstance(ht, str) and ht:
                ht_lc = ht.strip().lower().replace(" ", "_")
                if ht_lc in _VALID_HW_TYPES:
                    hw["type"] = ht_lc
                elif ht_lc in _HW_TYPE_FIX:
                    fixed = _HW_TYPE_FIX[ht_lc]
                    hw["type"] = "simulator_other" if fixed == "classical-simulation-placeholder" else fixed
                elif ht_lc.startswith("simulator"):
                    hw["type"] = "simulator_other"
                elif "qpu" in ht_lc or "quantum" in ht_lc:
                    hw["type"] = "not_specified"
                else:
                    hw["type"] = "not_specified"

        # Normalize provenance enums. Each field has its own allowed set per
        # benchmark_schema.json → provenance. Generic 'paper_not_reported' and
        # empty string → null.
        prov = exp.get("provenance")
        if prov is None:
            exp.pop("provenance", None)
        elif isinstance(prov, dict):
            _PROV_ENUMS = {
                "hardware_type":        {"paper_reported", "paper_inferred"},
                "advantage_status":     {"paper_reported", "paper_inferred"},
                "num_qubits":           {"paper_reported", "paper_inferred", "derived"},
                "circuit_depth":        {"paper_reported", "paper_inferred", "derived"},
                "speedup_order":        {"paper_reported", "paper_inferred", "derived"},
                "quantum_complexity":   {"paper_reported", "derived"},
                "classical_complexity": {"paper_reported", "derived"},
            }
            _NULL_SENTINELS = {"paper_not_reported", "not_reported", "missing",
                               "unknown", "tbd", "n/a", "na", "none", "null", ""}
            for k, v in list(prov.items()):
                if k == "notes":
                    continue
                if not isinstance(v, str):
                    continue
                v_lc = v.strip().lower().replace(" ", "_").replace("-", "_")
                allowed = _PROV_ENUMS.get(k)
                if v_lc in _NULL_SENTINELS:
                    prov[k] = None
                elif allowed is None:
                    # Unknown provenance field — leave null-safe
                    prov[k] = None if v_lc in {""} else v_lc
                elif v_lc in allowed:
                    prov[k] = v_lc
                elif v_lc == "paper_inferred" and "paper_inferred" not in allowed:
                    # For {quantum_complexity, classical_complexity}: map to 'derived'
                    prov[k] = "derived"
                elif v_lc in {"derived", "computed"} and "derived" not in allowed:
                    # For {hardware_type, advantage_status}: map 'derived' → 'paper_inferred'
                    prov[k] = "paper_inferred"
                elif v_lc in {"figure_estimated", "bridged", "inferred"}:
                    prov[k] = "paper_inferred" if "paper_inferred" in allowed else "derived"
                else:
                    prov[k] = None

        # Coerce noise_model list-type fields to strings, is_noisy to bool
        nm = exp.get("noise_model")
        if isinstance(nm, dict):
            for k in ("noise_type", "error_mitigation_method"):
                v = nm.get(k)
                if isinstance(v, list):
                    nm[k] = ", ".join(str(x) for x in v) if v else None
                elif isinstance(v, dict):
                    nm[k] = str(v)
            nm["is_noisy"] = _coerce_bool_or_null(nm.get("is_noisy"))

        # Coerce hardware.device_name list → joined string
        if hw:
            dn = hw.get("device_name")
            if isinstance(dn, list):
                hw["device_name"] = ", ".join(str(x) for x in dn) if dn else None
            elif isinstance(dn, dict):
                hw["device_name"] = str(dn)

        # Flatten list-valued string fields inside problem_instance + dataset_spec
        if pi:
            # data_type came in as list → pick first valid
            dt = pi.get("data_type")
            if isinstance(dt, list):
                pi["data_type"] = dt[0] if dt else None
                # re-run the data_type enum coercion
                dt2 = pi["data_type"]
                if isinstance(dt2, str):
                    dt2_lc = dt2.strip().lower().replace(" ", "_").replace("-", "_")
                    _VALID_DT2 = {"synthetic", "real_market", "proprietary", "public_benchmark"}
                    pi["data_type"] = dt2_lc if dt2_lc in _VALID_DT2 else None

            ds_spec = pi.get("dataset_specification")
            if isinstance(ds_spec, dict):
                for k in ("benchmark_name", "date_range"):
                    v = ds_spec.get(k)
                    if isinstance(v, list):
                        ds_spec[k] = ", ".join(str(x) for x in v) if v else None
                    elif isinstance(v, dict):
                        # e.g. {'train': '2016-...', 'test': '...'} → serialize
                        ds_spec[k] = "; ".join(f"{kk}: {vv}" for kk, vv in v.items())
                # ticker_symbols: schema expects array, LLM may emit string
                ts = ds_spec.get("ticker_symbols")
                if isinstance(ts, str):
                    ds_spec["ticker_symbols"] = [ts] if ts.strip() else None

        # Flatten problem_formulation.encoding_method list → first
        if isinstance(pf, dict):
            em_v = pf.get("encoding_method")
            if isinstance(em_v, list):
                pf["encoding_method"] = em_v[0] if em_v else None
            elif isinstance(em_v, dict):
                pf["encoding_method"] = str(em_v)

        # Flatten implementation_details list/dict-valued string fields
        if isinstance(impl, dict):
            fv = impl.get("framework_version")
            if isinstance(fv, dict):
                impl["framework_version"] = "; ".join(f"{k}={v}" for k, v in fv.items())
            elif isinstance(fv, list):
                impl["framework_version"] = ", ".join(str(x) for x in fv) if fv else None
            cu = impl.get("code_url")
            if isinstance(cu, list):
                impl["code_url"] = cu[0] if cu else None
            # framework
            fk = impl.get("framework")
            if isinstance(fk, list):
                impl["framework"] = ", ".join(str(x) for x in fk) if fk else None

        # speedup_claims.type: map 'speculative' and other extras to 'projected'
        for sc in (exp.get("speedup_claims") or []):
            if not isinstance(sc, dict):
                continue
            t = sc.get("type")
            if isinstance(t, str):
                _VALID_SC = {"asymptotic", "empirical", "theoretical", "projected", "none"}
                t_lc = t.strip().lower()
                if t_lc in _VALID_SC:
                    sc["type"] = t_lc
                elif t_lc in {"speculative", "hypothetical", "estimated", "inferred"}:
                    sc["type"] = "projected"
                elif t_lc in {"empirical_projected", "empirical/projected"}:
                    sc["type"] = "empirical"
                else:
                    sc["type"] = "none"

        # Flatten other list/dict-valued string fields across the schema
        # (hardware.framework, algorithm.ansatz, implementation_details
        # execution-time fields, dataset_specification.train_test_split).
        if isinstance(hw, dict):
            fwk = hw.get("framework")
            if isinstance(fwk, list):
                hw["framework"] = ", ".join(str(x) for x in fwk) if fwk else None
            elif isinstance(fwk, dict):
                hw["framework"] = "; ".join(f"{k}={v}" for k, v in fwk.items())
        if algo:
            ans = algo.get("ansatz")
            if isinstance(ans, list):
                algo["ansatz"] = ", ".join(str(x) for x in ans) if ans else None
            elif isinstance(ans, dict):
                algo["ansatz"] = str(ans)
        if isinstance(impl, dict):
            for k in ("quantum_execution_time", "total_execution_time",
                      "classical_execution_time", "preprocessing_time"):
                v = impl.get(k)
                if isinstance(v, dict):
                    # Try to extract a single number
                    num = v.get("value") if isinstance(v.get("value"), (int, float)) else None
                    impl[k] = num if num is not None else "; ".join(f"{kk}={vv}" for kk, vv in v.items())
                elif isinstance(v, list):
                    nums = [x for x in v if isinstance(x, (int, float))]
                    impl[k] = nums[0] if nums else ", ".join(str(x) for x in v) if v else None
        if pi:
            ds_spec = pi.get("dataset_specification")
            if isinstance(ds_spec, dict):
                tts = ds_spec.get("train_test_split")
                if isinstance(tts, dict):
                    ds_spec["train_test_split"] = "; ".join(f"{k}: {v}" for k, v in tts.items())
                elif isinstance(tts, list):
                    ds_spec["train_test_split"] = ", ".join(str(x) for x in tts) if tts else None

        # complexity_analysis.speedup_order: map free-form to enum
        ca = exp.get("complexity_analysis")
        if isinstance(ca, dict):
            so = ca.get("speedup_order")
            if isinstance(so, str):
                so_lc = so.strip().lower().replace(" ", "_").replace("-", "_")
                _VALID_SO = {"exponential", "cubic", "quadratic", "polynomial_other",
                             "logarithmic", "constant", "none", "none_proven"}
                if so_lc in _VALID_SO:
                    ca["speedup_order"] = so_lc
                elif so_lc in {"polynomial", "super_polynomial", "sub_exponential", "sub_exponential_polylog"}:
                    ca["speedup_order"] = "polynomial_other"
                elif so_lc in {"linear"}:
                    ca["speedup_order"] = "polynomial_other"
                elif "exp" in so_lc:
                    ca["speedup_order"] = "exponential"
                elif "quad" in so_lc:
                    ca["speedup_order"] = "quadratic"
                elif "cubic" in so_lc:
                    ca["speedup_order"] = "cubic"
                elif "log" in so_lc:
                    ca["speedup_order"] = "logarithmic"
                elif so_lc in {"", "unknown", "tbd", "not_assessed", "not_specified"}:
                    ca["speedup_order"] = None
                else:
                    ca["speedup_order"] = None

        for result in exp.get("results", []):
            # Fix compound data_source values
            ds = result.get("data_source")
            if isinstance(ds, str) and ds not in _VALID_DATA_SOURCES and ds:
                result["data_source"] = ds.split("/")[0] if "/" in ds else "text"
            # Convert non-scalar values to strings
            val = result.get("value")
            if isinstance(val, (list, dict)):
                result["value"] = str(val)
        for baseline in exp.get("classical_baselines", []):
            if "metric_name" in baseline:
                baseline["metric_name"] = normalize_metric_name(baseline["metric_name"])
            val = baseline.get("value")
            if isinstance(val, (list, dict)):
                baseline["value"] = str(val)
        for sd in exp.get("scalability_data", []):
            if sd.get("metric_name"):
                sd["metric_name"] = normalize_metric_name(sd["metric_name"])
    return data


# ---------------------------------------------------------------------------
# Extraction quality scoring
# ---------------------------------------------------------------------------

def compute_quality_score(data: dict) -> dict:
    """Compute a quality score for an extraction.

    Returns a dict with:
        score: float 0-1 (overall quality)
        completeness: float 0-1 (how many fields are populated)
        details: dict with per-dimension scores
    """
    if not data.get("has_quantitative_results") or not data.get("experiments"):
        return {
            "score": 0.0,
            "completeness": 0.0,
            "details": {"reason": "no_quantitative_results"},
        }

    scores: list[float] = []
    exp_details: list[dict] = []

    for exp in data["experiments"]:
        detail: dict[str, float] = {}

        # 1. Algorithm completeness (family + at least one of variant/ansatz/optimizer)
        algo = exp.get("algorithm") or {}
        has_family = bool(algo.get("family") and algo["family"] != "other")
        has_detail = bool(algo.get("variant") or algo.get("ansatz") or algo.get("optimizer"))
        detail["algorithm"] = 1.0 if has_family and has_detail else 0.5 if has_family else 0.0

        # 2. Quantum resources (at least qubits or depth)
        qr = exp.get("quantum_resources") or {}
        qr_fields = ["num_qubits", "circuit_depth", "num_shots", "gate_count_total"]
        qr_filled = sum(1 for f in qr_fields if qr.get(f) is not None)
        detail["quantum_resources"] = min(1.0, qr_filled / 2)  # 2+ fields = full score

        # 3. Hardware specificity
        hw = exp.get("hardware") or {}
        hw_type = hw.get("type") or ""
        has_specific_hw = hw_type not in ("", "not_specified", "simulator_other")
        has_provider = bool(hw.get("provider"))
        detail["hardware"] = 1.0 if has_specific_hw and has_provider else 0.5 if has_specific_hw or has_provider else 0.0

        # 4. Results with numeric values
        results = exp.get("results", [])
        numeric_results = sum(1 for r in results if isinstance(r.get("value"), (int, float)))
        detail["results"] = min(1.0, numeric_results / 2) if results else 0.0

        # 5. Classical baselines present
        baselines = exp.get("classical_baselines", [])
        numeric_baselines = sum(1 for b in baselines if isinstance(b.get("value"), (int, float)))
        detail["baselines"] = min(1.0, numeric_baselines / 1) if baselines else 0.0

        # 6. Problem instance description
        pi = exp.get("problem_instance") or {}
        pi_fields = ["num_assets", "dataset_size", "num_features", "time_steps"]
        pi_filled = sum(1 for f in pi_fields if pi.get(f) is not None)
        has_desc = bool(pi.get("description"))
        detail["problem_instance"] = min(1.0, (pi_filled + (0.5 if has_desc else 0)) / 1.5)

        # Weighted average
        weights = {
            "algorithm": 0.15,
            "quantum_resources": 0.20,
            "hardware": 0.10,
            "results": 0.30,
            "baselines": 0.15,
            "problem_instance": 0.10,
        }
        exp_score = sum(detail[k] * weights[k] for k in weights)
        scores.append(exp_score)
        exp_details.append(detail)

    overall = sum(scores) / len(scores) if scores else 0.0
    completeness = overall  # alias for readability

    return {
        "score": round(overall, 3),
        "completeness": round(completeness, 3),
        "num_experiments": len(scores),
        "experiment_scores": [round(s, 3) for s in scores],
        "details": exp_details,
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Validate a benchmark extraction JSON file."
    )
    parser.add_argument("json_path", help="Path to the extraction JSON file.")
    args = parser.parse_args()

    path = Path(args.json_path)
    if not path.is_file():
        print(f"ERROR: File not found: {path}", file=sys.stderr)
        sys.exit(1)

    with open(path, encoding="utf-8") as f:
        data = json.load(f)

    errors, warnings = validate_extraction(data)

    if errors:
        print(f"ERRORS ({len(errors)}):")
        for e in errors:
            print(f"  ✗ {e}")
    if warnings:
        print(f"WARNINGS ({len(warnings)}):")
        for w in warnings:
            print(f"  ⚠ {w}")
    if not errors and not warnings:
        print("PASS — no issues found.")

    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main()
