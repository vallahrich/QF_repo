"""B4 — VQE-style classifier (RealAmplitudes ansatz).

Bare: ansatz circuit only (what papers typically depict when reporting
circuit depth for VQE-style classifiers).
Full: feature-map encoding + ansatz + observable measurement basis change
(the per-sample forward circuit executed during training).
"""

from __future__ import annotations

from typing import Any, Dict

from qiskit import QuantumCircuit
from qiskit.circuit.library import RealAmplitudes, ZZFeatureMap

from p4_experiments.core.circuit_registry import register
from p4_experiments.core.oracle_accounting import register_accounting


def _build_ansatz(instance: Dict[str, Any]) -> QuantumCircuit:
    p = instance.get("parameters", instance)
    ansatz = RealAmplitudes(num_qubits=int(p["n_qubits"]),
                             reps=int(p["ansatz_reps"]))
    return ansatz


def _bind_random(circuit: QuantumCircuit, seed: int) -> QuantumCircuit:
    import numpy as np
    rng = np.random.default_rng(seed)
    x = rng.uniform(-1, 1, size=circuit.num_parameters)
    return circuit.assign_parameters(x)


@register(
    label="B4",
    paper_id="2fe0d0f15604",
    silo="quantum-ml-finance",
    algorithm_family="vqe",
    description="VQE-style classifier — bare = ansatz only",
)
def build_bare(instance: Dict[str, Any]) -> QuantumCircuit:
    p = instance["parameters"]
    ansatz = _bind_random(_build_ansatz(instance), int(p["random_seed"]))
    qc = QuantumCircuit(ansatz.num_qubits, ansatz.num_qubits, name="B4_bare")
    qc.compose(ansatz, inplace=True)
    qc.measure(range(ansatz.num_qubits), range(ansatz.num_qubits))
    return qc


def _full_state_prep(instance: Dict[str, Any], bare: QuantumCircuit) -> QuantumCircuit:
    """Prepend a ZZFeatureMap data-encoding stage."""
    p = instance["parameters"]
    n = int(p["n_qubits"])
    fm = ZZFeatureMap(feature_dimension=int(p["n_features"]), reps=1,
                      entanglement="linear")
    import numpy as np
    rng = np.random.default_rng(int(p["random_seed"]) + 7)
    x = rng.uniform(-1, 1, size=fm.num_parameters)
    bound = fm.assign_parameters(x)

    qc = QuantumCircuit(n, n, name="B4_full_prep")
    qc.compose(bound, inplace=True)
    # Append stripped bare (without measurement) then re-measure at end.
    stripped = bare.remove_final_measurements(inplace=False) or bare
    qc.compose(stripped, inplace=True)
    return qc


def _full_oracle(instance: Dict[str, Any], bare: QuantumCircuit) -> QuantumCircuit:
    """Append an observable basis change (simple Z->X rotation sweep) to
    represent the full per-sample forward circuit including measurement."""
    qc = bare.copy()
    # Remove any existing measurement, add Hadamard basis change, re-measure.
    qc.remove_final_measurements(inplace=True)
    for q in range(qc.num_qubits):
        qc.h(q)
    qc.measure(range(qc.num_qubits), range(qc.num_qubits))
    return qc


register_accounting(
    label="B4",
    state_prep=_full_state_prep,
    oracle=_full_oracle,
    oracle_variant="VQE-full-forward",
    notes=(
        "Full mode = feature-map encoding + ansatz + basis-change + measurement. "
        "Bare mode = ansatz only (paper-reported circuit depth)."
    ),
)
