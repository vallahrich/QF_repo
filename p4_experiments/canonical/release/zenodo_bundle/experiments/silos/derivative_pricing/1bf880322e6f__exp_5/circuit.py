"""SD3 — Quantum Speedups for Derivative Pricing: Beyond Black-Scholes.

Bare: b-state preparation only (n_b qubits).
Full: full HHL pipeline (b-prep + QPE + controlled-rotation + inverse QPE).

Authored 2026-04-23 as part of the Tier-1 71-cohort completion (rebind);
template-proxy methodology (does NOT implement the paper's algorithm).
"""
from __future__ import annotations

from typing import Any, Dict

from qiskit import QuantumCircuit

from p4_experiments.core.circuit_registry import register
from p4_experiments.core.oracle_accounting import register_accounting
from p4_experiments.core.templates.hhl import b_state_prep, full_hhl


@register(
    label="SD3",
    paper_id="1bf880322e6f",
    silo="derivative-pricing",
    algorithm_family="hhl",
    description="SD3 — HHL template proxy (Quantum Speedups for Derivative Pricing: Beyond Black-Scholes)",
)
def build_bare(instance: Dict[str, Any]) -> QuantumCircuit:
    p = instance["parameters"]
    bp = b_state_prep(int(p["n_b"]), seed=int(p.get("random_seed", 0)))
    qc = QuantumCircuit(bp.num_qubits, bp.num_qubits, name="SD3_bare")
    qc.compose(bp, inplace=True)
    qc.measure(range(bp.num_qubits), range(bp.num_qubits))
    return qc


def _full_state_prep(instance: Dict[str, Any], bare: QuantumCircuit) -> QuantumCircuit:
    return bare


def _full_oracle(instance: Dict[str, Any], bare: QuantumCircuit) -> QuantumCircuit:
    p = instance["parameters"]
    return full_hhl(
        n_b=int(p["n_b"]),
        n_clock=int(p["n_clock"]),
        hamiltonian_simulation_steps=int(p.get("ham_sim_steps", 1)),
        seed=int(p.get("random_seed", 0)),
        name="SD3_full",
    )


register_accounting(
    label="SD3",
    state_prep=_full_state_prep,
    oracle=_full_oracle,
    oracle_variant="HHL-template-proxy",
    notes="Tier-1 rebind (2026-04-23): paper algorithm not implemented; canonical HHL pipeline at paper-scale.",
)
