"""SM3 — OSDE-based QMCI (paper 623597ee0f9c)."""

from __future__ import annotations

from typing import Any, Dict

from qiskit import QuantumCircuit

from p4_experiments.core.circuit_registry import register
from p4_experiments.core.oracle_accounting import register_accounting
from p4_experiments.core.templates.qae import canonical_qae
from p4_experiments.core.templates.sim_mc_state_prep import continuous_func_state_prep


@register(
    label="SM3",
    paper_id="623597ee0f9c",
    silo="simulation-monte-carlo",
    algorithm_family="amplitude-estimation",
    description="OSDE block: state prep (n=4, L=2) + canonical QAE",
)
def build_bare(instance: Dict[str, Any]) -> QuantumCircuit:
    p = instance["parameters"]
    sp = continuous_func_state_prep(
        n_state=int(p["n_state"]),
        layers=int(p["state_prep_layers"]),
        seed=int(p.get("random_seed", 0)),
    )
    qc = QuantumCircuit(sp.num_qubits, sp.num_qubits, name="SM3_bare")
    qc.compose(sp, inplace=True)
    qc.measure(range(sp.num_qubits), range(sp.num_qubits))
    return qc


def _full_state_prep(instance: Dict[str, Any], bare: QuantumCircuit) -> QuantumCircuit:
    return bare


def _full_oracle(instance: Dict[str, Any], bare: QuantumCircuit) -> QuantumCircuit:
    p = instance["parameters"]
    sp = continuous_func_state_prep(
        n_state=int(p["n_state"]),
        layers=int(p["state_prep_layers"]),
        seed=int(p.get("random_seed", 0)),
    )
    return canonical_qae(state_prep=sp, num_eval_qubits=int(p["num_eval_qubits"]), name="SM3_full")


register_accounting(
    label="SM3",
    state_prep=_full_state_prep,
    oracle=_full_oracle,
    oracle_variant="OSDE-block-prep+canonical-QAE",
    notes="Full = OSDE block: state prep + canonical QAE. Bare = state prep only. The full algorithm chains many such blocks; tau accounting is per-block.",
)
