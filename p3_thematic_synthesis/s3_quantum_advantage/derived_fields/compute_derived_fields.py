"""Compute derived fields for experiments missing complexity/resource data.

Reads extraction JSONs, applies theoretical complexity formulas from
algorithm_complexity.json, and enriches experiments with computed values.
All derived values are flagged with _derived=True so they can be
distinguished from paper-reported values.

Usage:
    python -m p3_thematic_synthesis.s3_quantum_advantage.derived_fields.compute_derived_fields
    python -m p3_thematic_synthesis.s3_quantum_advantage.derived_fields.compute_derived_fields --silo portfolio-optimization
"""

import argparse
import json
import math
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent
_PROJECT_ROOT = Path(__file__).resolve().parents[3]

ALGO_COMPLEXITY_PATH = _ROOT / "algorithm_complexity.json"
P4_TAU_SUMMARY_PATH = _ROOT / "p4_tau_summary.json"
EXTRACTIONS_DIR = _PROJECT_ROOT / "p3_thematic_synthesis" / "quantitative" / "output" / "extractions"
OUTPUT_DIR = _ROOT / "enriched"


def load_algo_complexity() -> dict:
    with open(ALGO_COMPLEXITY_PATH, encoding="utf-8") as f:
        return json.load(f)


def load_p4_tau_summary() -> dict:
    """Load the per-silo P4-prime tau / oracle-share summary, if present.

    Returns a dict with keys: ``meta`` (h4_anchor, source, schema_version) and
    ``by_silo`` (silo -> compact summary row). Returns an empty dict with
    ``"available": False`` if the file is missing so downstream callers can
    keep going without it.
    """
    if not P4_TAU_SUMMARY_PATH.exists():
        return {"available": False, "by_silo": {}}
    raw = json.loads(P4_TAU_SUMMARY_PATH.read_text(encoding="utf-8"))
    by_silo = {row["silo"]: row for row in raw.get("rows", [])}
    return {
        "available": True,
        "schema_version": raw.get("schema_version"),
        "source": raw.get("source"),
        "h4_anchor": raw.get("h4_anchor"),
        "by_silo": by_silo,
    }


def get_numeric(val) -> int | float | None:
    """Extract numeric value, handling strings like '3888'."""
    if isinstance(val, (int, float)):
        return val
    if isinstance(val, str):
        # Try to parse first number from string
        import re
        m = re.search(r'(\d+(?:\.\d+)?)', val.replace(',', ''))
        if m:
            try:
                return float(m.group(1))
            except ValueError:
                pass
    return None


def compute_derived_complexity(experiment: dict, algo_db: dict) -> dict:
    """Compute complexity fields from algorithm family + problem parameters."""
    algo = experiment.get("algorithm", {})
    family = algo.get("family", "unknown")
    entry = algo_db.get(family, {})
    
    if not entry:
        return {}
    
    derived = {}
    ca = experiment.get("complexity_analysis") or {}
    
    # Fill missing complexity fields from theory
    if not ca.get("quantum_complexity") and entry.get("quantum_complexity"):
        derived["quantum_complexity"] = entry["quantum_complexity"]
        derived["quantum_complexity_derived"] = True
        derived["quantum_complexity_citation"] = entry.get("citation", "")
    
    if not ca.get("classical_complexity") and entry.get("classical_complexity"):
        derived["classical_complexity"] = entry["classical_complexity"]
        derived["classical_complexity_derived"] = True
    
    # Only fill missing speedup_order — do NOT overwrite "none" (paper-reported
    # empirical finding of no speedup) with the family's theoretical default.
    if ca.get("speedup_order") in (None, "unknown") or not ca.get("speedup_order"):
        if entry.get("speedup_order"):
            derived["speedup_order"] = entry["speedup_order"]
            derived["speedup_order_derived"] = True
            derived["speedup_k"] = entry.get("k")
    
    # Add caveats if any
    if entry.get("caveats"):
        derived["caveats"] = entry["caveats"]
    
    return derived


def compute_derived_resources(experiment: dict, algo_db: dict) -> dict:
    """Compute circuit resources from algorithm + problem size."""
    algo = experiment.get("algorithm", {})
    family = algo.get("family", "unknown")
    entry = algo_db.get(family, {})
    circuit = entry.get("circuit", {})
    
    if not circuit:
        return {}
    
    qr = experiment.get("quantum_resources") or {}
    pi = experiment.get("problem_instance") or {}
    pf = experiment.get("problem_formulation") or {}
    
    derived = {}
    
    # Get N (problem size)
    N = None
    num_assets = get_numeric(pi.get("num_assets"))
    num_binary = get_numeric(pf.get("num_binary_variables"))
    dataset_size = get_numeric(pi.get("dataset_size"))
    num_qubits_reported = get_numeric(qr.get("num_qubits"))
    
    # Determine N based on algorithm
    if family in ("qaoa", "vqe", "quantum-annealing", "qubo"):
        N = num_binary or num_assets
    elif family in ("grover", "quantum-walk"):
        N = dataset_size or num_assets
    elif family in ("amplitude-estimation",):
        N = None  # N is precision-based, not problem size
    elif family in ("hhl",):
        N = num_assets  # System size
    elif family in ("quantum-simulation",):
        N = num_assets or num_qubits_reported
    else:
        N = num_assets or num_binary
    
    if N is None or N <= 0:
        return {}
    
    N = int(N)
    
    # Get algorithm-specific params
    p = get_numeric(algo.get("num_layers"))  # QAOA depth / VQE layers
    
    # Compute qubits if missing
    if not num_qubits_reported:
        formula = circuit.get("qubits_formula")
        if formula == "N":
            derived["num_qubits"] = N
            derived["num_qubits_derived"] = True
            derived["num_qubits_formula"] = f"{family}: 1 qubit per variable, N={N}"
        elif family == "grover" and N > 0:
            derived["num_qubits"] = math.ceil(math.log2(N)) + 1
            derived["num_qubits_derived"] = True
            derived["num_qubits_formula"] = f"ceil(log2({N})) + 1 ancilla"
    
    # Compute depth if missing
    if not qr.get("circuit_depth"):
        if family == "qaoa" and p and N:
            d = int(2 * p * N)
            derived["circuit_depth"] = d
            derived["circuit_depth_derived"] = True
            derived["circuit_depth_formula"] = f"2 * p * N = 2 * {p} * {N} = {d}"
        elif family == "vqe" and p and N:
            d = int(p * N * 2)
            derived["circuit_depth"] = d
            derived["circuit_depth_derived"] = True
            derived["circuit_depth_formula"] = f"d * N * 2 = {p} * {N} * 2 = {d}"
    
    # Compute total gates if missing
    if not qr.get("gate_count_total"):
        if family == "qaoa" and p and N:
            # Rough: p * (N single-qubit + edges two-qubit)
            # For complete graph: edges = N*(N-1)/2
            edges = N * (N - 1) // 2
            gates = int(p * (N + edges))
            derived["gate_count_total"] = gates
            derived["gate_count_total_derived"] = True
            derived["gate_count_total_formula"] = f"p * (N + edges) = {p} * ({N} + {edges}) = {gates}"
    
    # Compute variational params if missing
    if not qr.get("num_variational_params"):
        if family == "qaoa" and p:
            derived["num_variational_params"] = int(2 * p)
            derived["num_variational_params_derived"] = True
        elif family == "vqe" and p and N:
            params = int(p * N * 2)
            derived["num_variational_params"] = params
            derived["num_variational_params_derived"] = True
    
    # Compute oracle complexity M (for Hoefler)
    total_gates = get_numeric(qr.get("gate_count_total")) or derived.get("gate_count_total")
    depth = get_numeric(qr.get("circuit_depth")) or derived.get("circuit_depth")
    qubits = num_qubits_reported or derived.get("num_qubits")
    
    if total_gates:
        derived["oracle_complexity_M"] = int(total_gates)
        derived["oracle_complexity_M_source"] = "gate_count_total"
        derived["oracle_complexity_M_derived"] = not bool(qr.get("gate_count_total"))
    elif depth and qubits:
        d_val = get_numeric(depth)
        q_val = get_numeric(qubits)
        if d_val and q_val:
            derived["oracle_complexity_M"] = int(d_val * q_val)
            derived["oracle_complexity_M_source"] = "depth * qubits"
            derived["oracle_complexity_M_derived"] = True
    
    return derived


def enrich_experiment(experiment: dict, algo_db: dict) -> dict:
    """Enrich a single experiment with derived fields.

    Returns a dict with complexity_derived, resources_derived, and
    derived_field_list (names of all fields that were computed from theory).
    """
    complexity_derived = compute_derived_complexity(experiment, algo_db)
    resource_derived = compute_derived_resources(experiment, algo_db)

    # Collect names of all derived fields for provenance tracking
    derived_names = []
    for d in (complexity_derived, resource_derived):
        for k, v in d.items():
            if k.endswith("_derived") and v is True:
                derived_names.append(k.removesuffix("_derived"))

    return {
        "complexity_derived": complexity_derived if complexity_derived else None,
        "resources_derived": resource_derived if resource_derived else None,
        "derived_field_list": derived_names if derived_names else None,
    }


def run_enrichment(silo_filter: str | None = None) -> dict:
    """Enrich all experiments and save results."""
    algo_db = load_algo_complexity()
    p4_tau = load_p4_tau_summary()
    p4_by_silo = p4_tau.get("by_silo", {})

    stats = {
        "total_experiments": 0,
        "enriched_complexity": 0,
        "enriched_resources": 0,
        "enriched_oracle_M": 0,
        "enriched_with_p4_silo_summary": 0,
    }
    all_enriched = []
    
    for f in sorted(EXTRACTIONS_DIR.glob("*.json")):
        data = json.loads(f.read_text("utf-8"))
        paper_id = data.get("paper_id", f.stem)
        silo = data.get("finance_domain", {}).get("primary_silo", "other")
        
        if silo_filter and silo != silo_filter:
            continue
        
        seen_exp_ids: dict[str, int] = {}
        for exp in data.get("experiments", []):
            stats["total_experiments"] += 1
            # Deduplicate experiment_ids within paper (mirrors extraction_loader)
            raw_exp_id = exp.get("experiment_id", "?")
            count = seen_exp_ids.get(raw_exp_id, 0)
            exp_id = f"{raw_exp_id}__dup{count}" if count > 0 else raw_exp_id
            seen_exp_ids[raw_exp_id] = count + 1

            enrichment = enrich_experiment(exp, algo_db)

            entry = {
                "paper_id": paper_id,
                "experiment_id": exp_id,
                "silo": silo,
                "algorithm_family": exp.get("algorithm", {}).get("family", "?"),
            }
            
            if enrichment["complexity_derived"]:
                stats["enriched_complexity"] += 1
                entry["complexity_derived"] = enrichment["complexity_derived"]
            
            if enrichment["resources_derived"]:
                stats["enriched_resources"] += 1
                entry["resources_derived"] = enrichment["resources_derived"]
                if enrichment["resources_derived"].get("oracle_complexity_M"):
                    stats["enriched_oracle_M"] += 1
            
            # Attach P4-prime per-silo tau summary as a derived field when available.
            # This is silo-level, not experiment-level, so it is shared across all
            # experiments in the same silo. Marked _derived=True for provenance.
            p4_row = p4_by_silo.get(silo)
            if p4_row is not None:
                entry["p4_silo_summary_derived"] = {
                    "silo": p4_row["silo"],
                    "regime": p4_row.get("regime"),
                    "median_tau_runtime_vs_bare": p4_row.get("median_tau_runtime_vs_bare"),
                    "median_oracle_share": p4_row.get("median_oracle_share"),
                    "n_labels_in_silo": p4_row.get("n_labels"),
                    "_derived": True,
                    "_source": "p3_thematic_synthesis/s3_quantum_advantage/derived_fields/p4_tau_summary.json",
                }
                stats["enriched_with_p4_silo_summary"] += 1

            if (
                enrichment["complexity_derived"]
                or enrichment["resources_derived"]
                or "p4_silo_summary_derived" in entry
            ):
                all_enriched.append(entry)

    # Save enriched data
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    output = {
        "stats": stats,
        "p4_tau_summary": {
            "available": p4_tau.get("available", False),
            "schema_version": p4_tau.get("schema_version"),
            "source": p4_tau.get("source"),
            "h4_anchor": p4_tau.get("h4_anchor"),
            "by_silo": p4_by_silo,
        },
        "enriched_experiments": all_enriched,
    }
    
    out_path = OUTPUT_DIR / "derived_fields.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False, default=str)
    
    return output


def main():
    parser = argparse.ArgumentParser(
        description="Compute derived complexity and resource fields from theory")
    parser.add_argument("--silo", help="Filter to specific silo")
    args = parser.parse_args()
    
    output = run_enrichment(args.silo)
    stats = output["stats"]
    
    print(f"\n{'='*50}")
    print("DERIVED FIELDS COMPUTATION")
    print(f"{'='*50}")
    print(f"\nTotal experiments: {stats['total_experiments']}")
    print(f"Enriched with complexity: {stats['enriched_complexity']} "
          f"({round(stats['enriched_complexity']/max(stats['total_experiments'],1)*100,1)}%)")
    print(f"Enriched with resources: {stats['enriched_resources']} "
          f"({round(stats['enriched_resources']/max(stats['total_experiments'],1)*100,1)}%)")
    print(f"Enriched oracle M: {stats['enriched_oracle_M']} "
          f"({round(stats['enriched_oracle_M']/max(stats['total_experiments'],1)*100,1)}%)")
    print(f"\nSaved to {OUTPUT_DIR / 'derived_fields.json'}")


if __name__ == "__main__":
    main()
