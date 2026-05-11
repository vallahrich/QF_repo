"""SF1 — Quantum Principal Component Analysis for Financial Fraud Detection.

Bare: continuous-function state-prep proxy (n_state qubits).
Full: canonical QAE wrapping the proxy oracle.
"""
from __future__ import annotations

from typing import Any, Dict

from qiskit import QuantumCircuit

from p4_experiments.core.circuit_registry import register
from p4_experiments.core.oracle_accounting import register_accounting
from p4_experiments.core.templates.qae import canonical_qae
from p4_experiments.core.templates.sim_mc_state_prep import (
    continuous_func_state_prep,
)


def _state_prep(p: Dict[str, Any]) -> QuantumCircuit:
    return continuous_func_state_prep(
        n_state=int(p["n_state"]),
        layers=int(p["state_prep_layers"]),
        seed=int(p.get("random_seed", 0)),
    )


@register(
    label="SF1",
    paper_id="76a87207ec32",
    silo="fraud-detection",
    algorithm_family="amplitude-estimation",
    description="SF1 — QAE template proxy (Quantum Principal Component Analysis for Financial Fraud Detection)",
)
def build_bare(instance: Dict[str, Any]) -> QuantumCircuit:
    p = instance["parameters"]
    sp = _state_prep(p)
    qc = QuantumCircuit(sp.num_qubits, sp.num_qubits, name="SF1_bare")
    qc.compose(sp, inplace=True)
    qc.measure(range(sp.num_qubits), range(sp.num_qubits))
    return qc


def _full_state_prep(instance: Dict[str, Any], bare: QuantumCircuit) -> QuantumCircuit:
    return bare


def _full_oracle(instance: Dict[str, Any], bare: QuantumCircuit) -> QuantumCircuit:
    p = instance["parameters"]
    return canonical_qae(
        state_prep=_state_prep(p),
        num_eval_qubits=int(p["num_eval_qubits"]),
        name="SF1_full",
    )


register_accounting(
    label="SF1",
    state_prep=_full_state_prep,
    oracle=_full_oracle,
    oracle_variant="QAE-template-proxy",
    notes="v3 stretch: paper algorithm not implemented; using QAE template at scale informed by paper_n.",
)
