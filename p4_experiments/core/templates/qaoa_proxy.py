"""
QAOA proxy template — p-layer Quantum Approximate Optimization Ansatz.

Used by SP1 (and any other 'qaoa' / Ising-cost-Hamiltonian flagged paper that
needs a structurally faithful proxy rather than a generic RealAmplitudes
stretch).

Bare mode: a single layer of cost (RZZ on linear chain + RZ singles) and
mixer (RX), with random Ising weights and parametric (gamma, beta) bound to
seeded values. Resource cost scales as O(p * n) two-qubit gates.

This is a structurally faithful QAOA proxy: it has the right gate set
(RZZ cost layer, RX mixer), the right repetition pattern (alternating
cost/mixer), and the right qubit count, but the Ising weights are
random rather than derived from a specific portfolio covariance matrix.
That is the same fidelity contract as ansatz_stretch, but family-correct.
"""
from __future__ import annotations

import numpy as np
from qiskit import QuantumCircuit


def qaoa_proxy(
    n_qubits: int,
    p_layers: int = 2,
    seed: int = 0,
    name: str = "qaoa_proxy",
) -> QuantumCircuit:
    """Build a p-layer QAOA circuit on a linear-coupling Ising cost.

    Layout: H^{⊗n} initial state → for each layer ℓ: cost(γ_ℓ) + mixer(β_ℓ).
    Includes terminal measurement on all qubits.
    """
    rng = np.random.default_rng(seed)
    # Random Ising weights (linear chain)
    h = rng.uniform(-1.0, 1.0, size=n_qubits)
    J = rng.uniform(-1.0, 1.0, size=max(n_qubits - 1, 0))
    # Random (γ, β) per layer, mimicking optimised parameters
    gammas = rng.uniform(0.0, 2.0 * np.pi, size=p_layers)
    betas = rng.uniform(0.0, np.pi, size=p_layers)

    qc = QuantumCircuit(n_qubits, n_qubits, name=name)
    # |+>^n initial state
    for q in range(n_qubits):
        qc.h(q)

    for ell in range(p_layers):
        gamma = float(gammas[ell])
        beta = float(betas[ell])
        # Cost layer: ZZ couplings + Z singles
        for i in range(n_qubits - 1):
            qc.rzz(2.0 * gamma * float(J[i]), i, i + 1)
        for i in range(n_qubits):
            qc.rz(2.0 * gamma * float(h[i]), i)
        # Mixer layer: X rotations
        for i in range(n_qubits):
            qc.rx(2.0 * beta, i)

    qc.measure(range(n_qubits), range(n_qubits))
    return qc
