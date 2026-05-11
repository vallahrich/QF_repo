"""
QGAN-then-QAE template — generator state-prep feeding canonical QAE.

Used by SD1 (Hybrid Quantum Wasserstein GAN for option pricing). Mirrors B5's
construction so the resource cost is comparable.
"""

from __future__ import annotations

import numpy as np
from qiskit import QuantumCircuit
from qiskit.circuit.library import RealAmplitudes

from p4_experiments.core.templates.qae import canonical_qae


def generator(n_qubits: int, reps: int, seed: int = 0) -> QuantumCircuit:
    """RealAmplitudes ansatz at fixed (proxy ``trained'') parameters."""
    ansatz = RealAmplitudes(num_qubits=n_qubits, reps=reps)
    rng = np.random.default_rng(seed)
    x = rng.uniform(-np.pi, np.pi, size=ansatz.num_parameters)
    return ansatz.assign_parameters(x)


def qgan_qae(
    n_qubits: int,
    generator_reps: int,
    num_eval_qubits: int,
    seed: int = 0,
    name: str = "QGAN_QAE_full",
) -> QuantumCircuit:
    gen = generator(n_qubits=n_qubits, reps=generator_reps, seed=seed)
    return canonical_qae(state_prep=gen, num_eval_qubits=num_eval_qubits, name=name)
