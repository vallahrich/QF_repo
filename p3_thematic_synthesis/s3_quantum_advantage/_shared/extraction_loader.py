"""Walk the active P3 S2 quantitative extractions directory and yield experiments.

Every framework assessor iterates (paper, experiment) pairs from here.
Keeps the extraction-dir path in ONE place so a repo move only touches this file.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Iterator

_MODULE_ROOT = Path(__file__).resolve().parent
PROJECT_ROOT = _MODULE_ROOT.parents[2]
EXTRACTIONS_DIR = PROJECT_ROOT / "p3_thematic_synthesis" / "s2_quantitative" / "output" / "extractions"

_SCOPE_OUT_ALGORITHM_FAMILIES = {"quantum-annealing", "quantum-annealing-qubo", "qubo"}
_SCOPE_OUT_HARDWARE_TYPES = {"quantum_annealer"}


def _scope_violation(exp: dict) -> bool:
    algo = exp.get("algorithm") or {}
    hardware = exp.get("hardware") or {}
    family = str(algo.get("family") or "").strip().lower()
    hw_type = str(hardware.get("type") or "").strip().lower()
    return family in _SCOPE_OUT_ALGORITHM_FAMILIES or hw_type in _SCOPE_OUT_HARDWARE_TYPES


def load_extraction(path: Path) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _bridge_experiment(exp: dict) -> dict:
    """Add derived flat fields that assessors expect but the schema stores elsewhere.

    This is purely additive — no original fields are removed or overwritten.
    If a target field already exists and is non-null, it is left as-is.
    Works on a shallow copy to avoid mutating the original dict.

    Tracks all bridged fields in exp["provenance"] so downstream code can
    distinguish paper-reported data from bridge-generated data.
    """
    exp = {k: v for k, v in exp.items()}  # shallow copy top level
    bridged_fields: list[str] = []  # collect what we bridge

    # --- Algorithm fields expected by Rønnow ---
    algo = dict(exp.get("algorithm") or {})

    # algorithm.classical_comparator ← first classical_baselines[].method_name
    if not algo.get("classical_comparator"):
        baselines = exp.get("classical_baselines") or []
        if baselines and baselines[0].get("method_name"):
            algo["classical_comparator"] = baselines[0]["method_name"]
            bridged_fields.append("algorithm.classical_comparator←classical_baselines[0].method_name")

    # algorithm.claimed_advantage ← advantage_assessment.advantage_status
    if not algo.get("claimed_advantage"):
        adv = exp.get("advantage_assessment") or {}
        status = adv.get("advantage_status")
        if status:
            algo["claimed_advantage"] = status
            bridged_fields.append("algorithm.claimed_advantage←advantage_assessment.advantage_status")

    # algorithm.description ← top-level experiment description
    if not algo.get("description"):
        desc = exp.get("description")
        if desc:
            algo["description"] = desc
            bridged_fields.append("algorithm.description←experiment.description")

    # algorithm.name ← family + variant
    if not algo.get("name"):
        variant = algo.get("variant")
        family = algo.get("family", "")
        algo["name"] = f"{family} ({variant})" if variant else family
        bridged_fields.append("algorithm.name←family+variant")

    exp["algorithm"] = algo

    # --- complexity_analysis fields expected by Rønnow/Hoefler ---
    ca = dict(exp.get("complexity_analysis") or {})

    # complexity_analysis.speedup_type ← first speedup_claims[].type
    claims = exp.get("speedup_claims") or []
    if not ca.get("speedup_type") and claims:
        ca["speedup_type"] = claims[0].get("type")
        bridged_fields.append("complexity_analysis.speedup_type←speedup_claims[0].type")

    # complexity_analysis.speedup_claimed ← first speedup_claims[].factor
    if not ca.get("speedup_claimed") and claims:
        ca["speedup_claimed"] = claims[0].get("factor")
        bridged_fields.append("complexity_analysis.speedup_claimed←speedup_claims[0].factor")

    # complexity_analysis.advantage_claim ← advantage_assessment.advantage_status
    if not ca.get("advantage_claim"):
        adv = exp.get("advantage_assessment") or {}
        if adv.get("advantage_status"):
            ca["advantage_claim"] = adv["advantage_status"]
            bridged_fields.append("complexity_analysis.advantage_claim←advantage_assessment.advantage_status")

    # complexity_analysis.classical_baseline ← first classical_baselines[].method_name
    if not ca.get("classical_baseline"):
        baselines = exp.get("classical_baselines") or []
        if baselines:
            ca["classical_baseline"] = baselines[0].get("method_name")
            bridged_fields.append("complexity_analysis.classical_baseline←classical_baselines[0].method_name")

    # complexity_analysis.classical_algorithm ← same
    if not ca.get("classical_algorithm"):
        ca["classical_algorithm"] = ca.get("classical_baseline")
        if ca["classical_algorithm"]:
            bridged_fields.append("complexity_analysis.classical_algorithm←classical_baseline")

    # complexity_analysis.classical_method ← same
    if not ca.get("classical_method"):
        ca["classical_method"] = ca.get("classical_baseline")
        if ca["classical_method"]:
            bridged_fields.append("complexity_analysis.classical_method←classical_baseline")

    # complexity_analysis.comparison_type ← infer from speedup_claims
    if not ca.get("comparison_type") and claims:
        ca["comparison_type"] = claims[0].get("type")
        bridged_fields.append("complexity_analysis.comparison_type←speedup_claims[0].type")

    # complexity_analysis.problem_sizes_tested ← scalability_data[].problem_size
    if not ca.get("problem_sizes_tested"):
        sd = exp.get("scalability_data") or []
        sizes = [e["problem_size"] for e in sd if e.get("problem_size") is not None]
        if sizes:
            ca["problem_sizes_tested"] = sizes
            bridged_fields.append("complexity_analysis.problem_sizes_tested←scalability_data")

    # complexity_analysis.methodology_notes ← first speedup_claims[].conditions + caveats
    if not ca.get("methodology_notes") and claims:
        parts = []
        c0 = claims[0]
        if c0.get("conditions"):
            parts.append(str(c0["conditions"]))
        if c0.get("caveats"):
            parts.append(str(c0["caveats"]))
        if parts:
            ca["methodology_notes"] = "; ".join(parts)
            bridged_fields.append("complexity_analysis.methodology_notes←speedup_claims[0].conditions+caveats")

    # complexity_analysis.target_precision / target_error ← results[] metrics
    if not ca.get("target_precision") and not ca.get("target_error"):
        for r in (exp.get("results") or []):
            mn = (r.get("metric_name") or "").lower()
            if mn in ("target_precision", "target_error", "epsilon", "accuracy_target"):
                ca["target_error"] = r.get("value")
                bridged_fields.append(f"complexity_analysis.target_error←results[].{mn}")
                break

    if ca:
        exp["complexity_analysis"] = ca

    # --- noise_model: bridge new field names to legacy assessor field names ---
    nm = dict(exp.get("noise_model") or {})

    # Assessors read error_rate, two_qubit_error, gate_error_rate
    # Schema stores single_qubit_error_rate, two_qubit_error_rate
    if not nm.get("error_rate"):
        val = nm.get("two_qubit_error_rate") or nm.get("single_qubit_error_rate")
        if val:
            nm["error_rate"] = val
            bridged_fields.append("noise_model.error_rate←error_rates")
    if not nm.get("two_qubit_error"):
        if nm.get("two_qubit_error_rate"):
            nm["two_qubit_error"] = nm["two_qubit_error_rate"]
            bridged_fields.append("noise_model.two_qubit_error←two_qubit_error_rate")
    if not nm.get("gate_error_rate"):
        if nm.get("single_qubit_error_rate"):
            nm["gate_error_rate"] = nm["single_qubit_error_rate"]
            bridged_fields.append("noise_model.gate_error_rate←single_qubit_error_rate")

    if nm:
        exp["noise_model"] = nm

    # --- implementation_details: bridge algorithm.num_layers → impl fields ---
    impl = dict(exp.get("implementation_details") or {})

    if not impl.get("num_layers") and algo.get("num_layers"):
        impl["num_layers"] = algo["num_layers"]
        bridged_fields.append("implementation_details.num_layers←algorithm.num_layers")
    if not impl.get("p_rounds") and algo.get("num_layers"):
        family = algo.get("family", "")
        if family == "qaoa":
            impl["p_rounds"] = algo["num_layers"]
            bridged_fields.append("implementation_details.p_rounds←algorithm.num_layers")

    if not impl.get("hardware_name"):
        hw = exp.get("hardware") or {}
        if hw.get("device_name"):
            impl["hardware_name"] = hw["device_name"]
            bridged_fields.append("implementation_details.hardware_name←hardware.device_name")

    if impl:
        exp["implementation_details"] = impl

    # --- Write bridge provenance ---
    if bridged_fields:
        prov = dict(exp.get("provenance") or {})
        existing = prov.get("bridged_fields") or []
        prov["bridged_fields"] = existing + bridged_fields
        exp["provenance"] = prov

    return exp


def iter_experiments(
    silo_filter: str | None = None,
    require_valid: bool = True,
) -> Iterator[tuple[dict, dict]]:
    """Yield (paper_envelope, experiment) for every extracted experiment.

    paper_envelope carries paper_id, finance_domain, paper_metadata,
    and validation_passed (bool).
    experiment is one entry from paper["experiments"], enriched with
    bridged fields so downstream assessors find data where they expect it.

    Args:
        silo_filter: Only yield experiments from this silo.
        require_valid: If True, skip papers where validation_passed is False.
            Default True so framework verdicts do not consume schema-failed
            extraction files. Use False only for explicit sensitivity/audit runs.
    """
    if not EXTRACTIONS_DIR.exists():
        raise FileNotFoundError(f"Extractions directory not found: {EXTRACTIONS_DIR}")

    for f in sorted(EXTRACTIONS_DIR.glob("*.json")):
        data = load_extraction(f)
        paper_id = data.get("paper_id", f.stem)
        silo = (data.get("finance_domain") or {}).get("primary_silo", "other")
        if silo_filter and silo != silo_filter:
            continue

        em = data.get("extraction_metadata") or {}
        validation_passed = em.get("validation_passed", None)

        if require_valid and not validation_passed:
            continue

        envelope = {
            "paper_id": paper_id,
            "silo": silo,
            "paper_metadata": data.get("paper_metadata", {}),
            "finance_domain": data.get("finance_domain", {}),
            "validation_passed": validation_passed,
        }
        # Deduplicate experiment_ids within a paper: the schema does not
        # enforce uniqueness, and some extractions reuse the same id
        # (e.g. two exp_4 rows). Downstream code keys on
        # (paper_id, experiment_id), so collisions silently drop rows.
        # Suffix duplicates with __dup{n} to preserve every row.
        seen: dict[str, int] = {}
        for exp in data.get("experiments", []) or []:
            if _scope_violation(exp):
                continue
            exp_id = exp.get("experiment_id") or "unknown"
            count = seen.get(exp_id, 0)
            if count > 0:
                new_id = f"{exp_id}__dup{count}"
                exp = {**exp, "experiment_id": new_id,
                       "_original_experiment_id": exp_id}
            seen[exp_id] = count + 1
            yield envelope, _bridge_experiment(exp)
