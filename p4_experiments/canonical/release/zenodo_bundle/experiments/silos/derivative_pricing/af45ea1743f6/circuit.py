"""SD1 — Hybrid Quantum Wasserstein GAN for option pricing (paper af45ea1743f6).

Bare: 5-qubit RealAmplitudes generator (proxy for the trained qWGAN
generator). Full: generator-loaded state feeding canonical QAE.
"""

from __future__ import annotations

from typing import Any, Dict

from qiskit import QuantumCircuit

from p4_experiments.core.circuit_registry import register
from p4_experiments.core.oracle_accounting import register_accounting
from p4_experiments.core.templates.qgan_qae import generator, qgan_qae


@register(
    label="SD1",
    paper_id="af45ea1743f6",
    silo="derivative-pricing",
    algorithm_family="quantum-ml",
    description="qWGAN generator (5q, reps=2) + canonical QAE for option pricing",
)
def build_bare(instance: Dict[str, Any]) -> QuantumCircuit:
    p = instance["parameters"]
    gen = generator(
        n_qubits=int(p["n_qubits"]),
        reps=int(p["generator_reps"]),
        seed=int(p.get("random_seed", 0)),
    )
    qc = QuantumCircuit(gen.num_qubits, gen.num_qubits, name="SD1_bare")
    qc.compose(gen, inplace=True)
    qc.measure(range(gen.num_qubits), range(gen.num_qubits))
    return qc


def _full_state_prep(instance: Dict[str, Any], bare: QuantumCircuit) -> QuantumCircuit:
    return bare


def _full_oracle(instance: Dict[str, Any], bare: QuantumCircuit) -> QuantumCircuit:
    p = instance["parameters"]
    return qgan_qae(
        n_qubits=int(p["n_qubits"]),
        generator_reps=int(p["generator_reps"]),
        num_eval_qubits=int(p["num_eval_qubits"]),
        seed=int(p.get("random_seed", 0)),
        name="SD1_full",
    )


register_accounting(
    label="SD1",
    state_prep=_full_state_prep,
    oracle=_full_oracle,
    oracle_variant="QGAN+canonical-QAE",
    notes=(
        "Full mode = generator + controlled Grover^{2^k} over num_eval_qubits "
        "+ inverse QFT. Bare mode = generator only. Mirrors B5; resource "
        "footprint is the QAE pipeline."
    ),
)
