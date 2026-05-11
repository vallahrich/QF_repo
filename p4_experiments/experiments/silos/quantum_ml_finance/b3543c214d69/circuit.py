"""B3 pilot — QSVM feature-map circuit (paper b3543c214d69, exp_1).

Builds a Havlicek-style ZZFeatureMap (n_qubits=3, reps=2) used as the
quantum kernel embedding. The *bare* circuit is the feature map applied
once to a single data point. The *full* circuit (registered in
``oracle_accounting``) is the paired kernel-estimation primitive
``U_phi(x) . U_phi(y)^dagger`` which is the actual per-kernel-entry
quantum operation executed by QSVM training.
"""

from __future__ import annotations

from typing import Any, Dict

from qiskit import QuantumCircuit
from qiskit.circuit.library import ZZFeatureMap

from p4_experiments.core.circuit_registry import register
from p4_experiments.core.oracle_accounting import register_accounting


def _build_feature_map(instance: Dict[str, Any]) -> QuantumCircuit:
    p = instance.get("parameters", instance)
    n_features = int(p["n_features"])
    reps = int(p["feature_map_reps"])
    fm = ZZFeatureMap(
        feature_dimension=n_features,
        reps=reps,
        entanglement=p.get("entanglement", "linear"),
    )
    return fm


@register(
    label="B3",
    paper_id="b3543c214d69",
    silo="quantum-ml-finance",
    algorithm_family="quantum-svm",
    description="QSVM ZZFeatureMap(3, reps=2) — pilot",
)
def build_bare(instance: Dict[str, Any]) -> QuantumCircuit:
    """Bare circuit: single feature-map application (paper-reported scale)."""
    fm = _build_feature_map(instance)
    # Bind symbolic parameters to a fixed feature vector so the circuit is
    # concrete and estimatable.
    from numpy.random import default_rng
    rng = default_rng(instance["parameters"].get("random_seed", 0))
    x = rng.uniform(-1.0, 1.0, size=fm.num_parameters)
    bound = fm.assign_parameters(x)
    qc = QuantumCircuit(fm.num_qubits, fm.num_qubits, name="B3_bare")
    qc.compose(bound, inplace=True)
    qc.measure(range(fm.num_qubits), range(fm.num_qubits))
    return qc


def _full_state_prep(instance: Dict[str, Any], bare: QuantumCircuit) -> QuantumCircuit:
    """No additional classical state-prep beyond the feature map itself."""
    return bare


def _full_oracle(instance: Dict[str, Any], bare: QuantumCircuit) -> QuantumCircuit:
    """Full accounting: append the inverse feature map on a second data point.

    This is the per-kernel-entry primitive executed in QSVM kernel
    estimation. Papers that report only the single feature-map depth
    under-count by this factor.
    """
    fm = _build_feature_map(instance)
    from numpy.random import default_rng
    rng = default_rng(instance["parameters"].get("random_seed", 0) + 1)
    y = rng.uniform(-1.0, 1.0, size=fm.num_parameters)
    bound_inv = fm.assign_parameters(y).inverse()

    qc = QuantumCircuit(fm.num_qubits, fm.num_qubits, name="B3_full")
    # Bare already has a measurement; strip it and rebuild the full pipeline.
    stripped = bare.remove_final_measurements(inplace=False) or bare
    qc.compose(stripped, inplace=True)
    qc.compose(bound_inv, inplace=True)
    qc.measure(range(fm.num_qubits), range(fm.num_qubits))
    return qc


register_accounting(
    label="B3",
    state_prep=_full_state_prep,
    oracle=_full_oracle,
    oracle_variant="qsvm-kernel-paired-inverse",
    notes=(
        "Full mode = U_phi(x) . U_phi(y)^dagger kernel-estimation primitive. "
        "Bare mode = single U_phi(x) application (paper-reported circuit)."
    ),
)
