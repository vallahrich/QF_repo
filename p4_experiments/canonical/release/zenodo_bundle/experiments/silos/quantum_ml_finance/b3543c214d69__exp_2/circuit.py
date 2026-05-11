"""SQ13 — Quantum-enhanced versus classical Support Vector Machine: An application to stoc.

Bare: amplitude-encoding ansatz on n_qubits.
Full: encoder(x) . encoder(y)^dagger paired inverse.
"""
from __future__ import annotations

from typing import Any, Dict

from qiskit import QuantumCircuit

from p4_experiments.core.circuit_registry import register
from p4_experiments.core.oracle_accounting import register_accounting
from p4_experiments.core.templates.amplitude_encoding import (
    encoder,
    encoding_paired_inverse,
)


@register(
    label="SQ13",
    paper_id="b3543c214d69",
    silo="quantum-ml-finance",
    algorithm_family="quantum-svm",
    description="SQ13 — amplitude-encoding paired-inverse template proxy (Quantum-enhanced versus classical Support Vector Machine: An application to stoc)",
)
def build_bare(instance: Dict[str, Any]) -> QuantumCircuit:
    p = instance["parameters"]
    enc = encoder(
        n_qubits=int(p["n_qubits"]),
        layers=int(p["encoder_layers"]),
        seed=int(p.get("random_seed", 0)),
    )
    qc = QuantumCircuit(enc.num_qubits, enc.num_qubits, name="SQ13_bare")
    qc.compose(enc, inplace=True)
    qc.measure(range(enc.num_qubits), range(enc.num_qubits))
    return qc


def _full_state_prep(instance: Dict[str, Any], bare: QuantumCircuit) -> QuantumCircuit:
    return bare


def _full_oracle(instance: Dict[str, Any], bare: QuantumCircuit) -> QuantumCircuit:
    p = instance["parameters"]
    return encoding_paired_inverse(
        n_qubits=int(p["n_qubits"]),
        layers=int(p["encoder_layers"]),
        seed=int(p.get("random_seed", 0)),
        name="SQ13_full",
    )


register_accounting(
    label="SQ13",
    state_prep=_full_state_prep,
    oracle=_full_oracle,
    oracle_variant="amplitude-encoding-paired-inverse-template-proxy",
    notes="v3 stretch: paper algorithm not implemented; uses ACAE-style template.",
)
