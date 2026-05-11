"""SM* — generic continuous-function state-prep proxy for sim-MC AE papers.

Used by SM1, SM2, SM3 (none of which give explicit circuit constructions in
the P3 extraction). The proxy mirrors templates.hhl.b_state_prep but with
configurable layer count, since the QAE work-register cost is what dominates
the resource estimate.
"""

from __future__ import annotations

import numpy as np
from qiskit import QuantumCircuit


def continuous_func_state_prep(
    n_state: int,
    layers: int,
    seed: int = 0,
) -> QuantumCircuit:
    """Parametrised RY-then-CNOT-chain state-prep proxy."""
    rng = np.random.default_rng(seed)
    qc = QuantumCircuit(n_state, name=f"sm_prep_{n_state}q_{layers}L")
    for _ in range(layers):
        for i in range(n_state):
            qc.ry(float(rng.uniform(-np.pi, np.pi)), i)
        for i in range(n_state - 1):
            qc.cx(i, i + 1)
    for i in range(n_state):
        qc.ry(float(rng.uniform(-np.pi, np.pi)), i)
    return qc
