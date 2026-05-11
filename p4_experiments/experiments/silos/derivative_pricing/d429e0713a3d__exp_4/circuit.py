"""SD15 — Quantum Computing in Option Pricing.

Bare: continuous-function state-prep proxy (n_state qubits).
Full: canonical QAE wrapping the proxy oracle.

Authored 2026-04-23 as part of the Tier-1 71-cohort completion (rebind);
template-proxy methodology (does NOT implement the paper's algorithm).
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
    label="SD15",
    paper_id="d429e0713a3d",
    silo="derivative-pricing",
    algorithm_family="amplitude-estimation",
    description="SD15 — QAE template proxy (Quantum Computing in Option Pricing)",
)
def build_bare(instance: Dict[str, Any]) -> QuantumCircuit:
    p = instance["parameters"]
    sp = _state_prep(p)
    qc = QuantumCircuit(sp.num_qubits, sp.num_qubits, name="SD15_bare")
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
        name="SD15_full",
    )


register_accounting(
    label="SD15",
    state_prep=_full_state_prep,
    oracle=_full_oracle,
    oracle_variant="QAE-template-proxy",
    notes="Tier-1 rebind (2026-04-23): paper algorithm not implemented; using QAE template at scale informed by paper_n.",
)
