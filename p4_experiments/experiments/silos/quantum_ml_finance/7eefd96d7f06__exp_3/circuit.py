"""SQ15 — Quantum algorithms for hedging and the learning of Ising models.

Bare: parametrised RealAmplitudes ansatz, fixed seed.
Full: ansatz . ansatz^dagger compute-uncompute pair (proxy oracle).
"""
from __future__ import annotations

from typing import Any, Dict

from qiskit import QuantumCircuit

from p4_experiments.core.circuit_registry import register
from p4_experiments.core.oracle_accounting import register_accounting
from p4_experiments.core.templates.ansatz_stretch import ansatz_stretch
from qiskit.circuit.library import RealAmplitudes
import numpy as np


def _ansatz_only(p: Dict[str, Any]) -> QuantumCircuit:
    n = int(p["n_qubits"])
    layers = int(p["ansatz_layers"])
    a = RealAmplitudes(num_qubits=n, reps=layers, entanglement="linear")
    rng = np.random.default_rng(int(p.get("random_seed", 0)))
    return a.assign_parameters(rng.uniform(-np.pi, np.pi, size=a.num_parameters))


@register(
    label="SQ15",
    paper_id="7eefd96d7f06",
    silo="quantum-ml-finance",
    algorithm_family="other-gate-based",
    description="SQ15 — generic variational ansatz stretch (Quantum algorithms for hedging and the learning of Ising models)",
)
def build_bare(instance: Dict[str, Any]) -> QuantumCircuit:
    p = instance["parameters"]
    return ansatz_stretch(
        n_qubits=int(p["n_qubits"]),
        layers=int(p["ansatz_layers"]),
        seed=int(p.get("random_seed", 0)),
        name="SQ15_bare",
    )


def _full_state_prep(instance: Dict[str, Any], bare: QuantumCircuit) -> QuantumCircuit:
    return bare


def _full_oracle(instance: Dict[str, Any], bare: QuantumCircuit) -> QuantumCircuit:
    p = instance["parameters"]
    n = int(p["n_qubits"])
    a = _ansatz_only(p)
    qc = QuantumCircuit(n, n, name="SQ15_full")
    qc.compose(a, inplace=True)
    qc.compose(a.inverse(), inplace=True)
    qc.measure(range(n), range(n))
    return qc


register_accounting(
    label="SQ15",
    state_prep=_full_state_prep,
    oracle=_full_oracle,
    oracle_variant="ansatz-compute-uncompute-template-proxy",
    notes="v3 stretch: paper algorithm not implemented; generic RealAmplitudes ansatz at paper-scale.",
)
