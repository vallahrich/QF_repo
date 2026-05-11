"""
Amplitude-encoding + Hadamard-classifier template.

Used by SQ1 (Approximate Complex Amplitude Encoding). Mirrors B3's
paired-inverse construction so kernel-style accounting transfers.

Bare: encoding ansatz applied to a single data point.
Full: encoding(x) followed by encoding(y)^dagger and measurement (the
per-kernel-entry primitive in a Hadamard-style classifier).
"""

from __future__ import annotations

import numpy as np
from qiskit import QuantumCircuit
from qiskit.circuit.library import EfficientSU2


def encoder(n_qubits: int, layers: int, seed: int = 0) -> QuantumCircuit:
    """An EfficientSU2(n, reps=layers) ansatz at fixed parameters proxies the
    paper's variationally trained amplitude-encoding circuit."""
    ansatz = EfficientSU2(num_qubits=n_qubits, reps=layers, entanglement="linear")
    rng = np.random.default_rng(seed)
    x = rng.uniform(-np.pi, np.pi, size=ansatz.num_parameters)
    return ansatz.assign_parameters(x)


def encoding_paired_inverse(
    n_qubits: int,
    layers: int,
    seed: int = 0,
    name: str = "ACAE_full",
) -> QuantumCircuit:
    enc_x = encoder(n_qubits=n_qubits, layers=layers, seed=seed)
    enc_y = encoder(n_qubits=n_qubits, layers=layers, seed=seed + 1).inverse()
    qc = QuantumCircuit(n_qubits, n_qubits, name=name)
    qc.compose(enc_x, inplace=True)
    qc.compose(enc_y, inplace=True)
    qc.measure(range(n_qubits), range(n_qubits))
    return qc
