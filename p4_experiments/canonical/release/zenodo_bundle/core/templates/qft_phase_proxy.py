"""
QFT-phase Hamiltonian-simulation proxy template.

Used for SD1, SD5 — papers whose claimed algorithm is QSP / qubitization /
QFT-diagonalised Hamiltonian simulation (Black–Scholes / option-price PDE
dynamics). The full QSP/qubitization stack is too large to author per-paper
at Tier-1 scale, so we use a structurally faithful QFT-based proxy:

    QFT  →  diagonal-phase evolution (RZ chain + RZZ couplings, parameterised
            by simulation-step count)  →  inverse QFT  →  embedding-ancilla
            controlled rotation (post-selection proxy)

This carries the right structural cost drivers (Hadamard cascade, controlled
phase shifts in QFT, RZ/RZZ phase evolution, inverse QFT, ancilla controlled
rotation) — i.e. the same primitives a real QSP/qubitization proxy would
expose to the QDK Resource Estimator. Resource cost scales as O(n²) for QFT
plus O(steps · n) for the phase block.
"""
from __future__ import annotations

import numpy as np
from qiskit import QuantumCircuit
from qiskit.circuit.library import QFT


def qft_phase_proxy(
    n_qubits: int,
    sim_steps: int = 2,
    use_ancilla: bool = True,
    seed: int = 0,
    name: str = "qft_phase_proxy",
) -> QuantumCircuit:
    """QFT + diagonal-phase + iQFT + post-selection-ancilla proxy.

    Layout: [ancilla(0..1)] + [work(n_qubits)]. If ``use_ancilla`` is True,
    one extra qubit is appended for a controlled-RY post-selection proxy.

    Includes terminal measurement on all qubits.
    """
    n_anc = 1 if use_ancilla else 0
    n_total = n_qubits + n_anc
    rng = np.random.default_rng(seed)

    qc = QuantumCircuit(n_total, n_total, name=name)
    work = list(range(n_qubits))
    anc = n_qubits if use_ancilla else None

    # 1. Forward QFT on the work register (momentum-basis diagonalisation)
    qc.compose(QFT(n_qubits, inverse=False, do_swaps=True),
               qubits=work, inplace=True)

    # 2. Diagonal phase evolution (RZ singles + RZZ couplings, sim_steps reps)
    for _ in range(sim_steps):
        for i in range(n_qubits):
            qc.rz(float(rng.uniform(-np.pi, np.pi)), i)
        for i in range(n_qubits - 1):
            qc.rzz(float(rng.uniform(-np.pi, np.pi)), i, i + 1)

    # 3. Inverse QFT (back to position basis)
    qc.compose(QFT(n_qubits, inverse=True, do_swaps=True),
               qubits=work, inplace=True)

    # 4. Embedding-ancilla controlled rotation (post-selection proxy).
    # One CRY per work qubit so cost scales linearly in n.
    if use_ancilla:
        for i in range(n_qubits):
            qc.cry(float(np.pi / (2 ** (i + 1))), i, anc)

    qc.measure(range(n_total), range(n_total))
    return qc
