"""
Generic variational-ansatz stretch template.

Used for v3 picks tagged ``other-gate-based``, ``vqe``, ``qaoa``, or
``hybrid`` whose actual algorithm is not implemented from the paper.
The bare circuit is a ``RealAmplitudes(n, reps=layers)`` parametrised
ansatz at fixed RNG-seeded parameters; the full oracle wrapping is
applied by ``run_unit`` per the standard accounting (no oracle for
state-prep-only labels — matches B3/SQ1 pattern).

This template is intentionally honest about its stretch: every τ-row
emitted under this template should be read as "an FT-cost estimate for
a representative parametrised circuit at this scale and depth", NOT
"an FT-cost estimate of the paper's algorithm". The ``notes.md`` file
in each scaffolded directory records that disclaimer per-pick.
"""

from __future__ import annotations

import numpy as np
from qiskit import QuantumCircuit
from qiskit.circuit.library import RealAmplitudes


def ansatz_stretch(
    n_qubits: int,
    layers: int,
    seed: int = 0,
    name: str = "ansatz_stretch",
) -> QuantumCircuit:
    ansatz = RealAmplitudes(
        num_qubits=n_qubits, reps=layers, entanglement="linear"
    )
    rng = np.random.default_rng(seed)
    x = rng.uniform(-np.pi, np.pi, size=ansatz.num_parameters)
    bound = ansatz.assign_parameters(x)
    qc = QuantumCircuit(n_qubits, n_qubits, name=name)
    qc.compose(bound, inplace=True)
    qc.measure(range(n_qubits), range(n_qubits))
    return qc
