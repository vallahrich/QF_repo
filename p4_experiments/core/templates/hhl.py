"""
HHL template — Quantum linear-systems Phase Estimation + controlled rotations.

Used by SP1, SP2, SH1.

Fidelity tier note (2026-05-02): the ``U`` and the b-prep used here are
*shared parameter-count proxies*, not paper-faithful constructions. SP1,
SP2, SH1 all share this template scaffolding; their per-paper resource
estimates differ only through extracted scale parameters. See
``THREATS_TO_VALIDITY.md`` CV-5 for the matched classical-baseline
caveat. Manuscript prose must not promote H4 results on these labels
to strict paper-faithful claims.

Bare mode: the b-state preparation circuit (what HHL papers typically depict
as their ``initial state'' figure).

Full mode: full HHL pipeline = b-prep on the work register + Hadamards on the
clock register + controlled-U^{2^k} forward QPE + a depth-proportional proxy
for the eigenvalue-inversion controlled rotations on an ancilla + inverse QPE.
The unitary U is a parametrised proxy whose resource footprint scales as
``hamiltonian_simulation_steps`` per controlled-power. We do NOT claim
finance semantics here — the resource cost (T-count, T-depth) is what tau
accounting needs; problem-specific U would only change leading constants.
"""

from __future__ import annotations

import numpy as np
from qiskit import QuantumCircuit
from qiskit.circuit.library import QFT


def b_state_prep(n_b: int, seed: int = 0) -> QuantumCircuit:
    """A non-trivial b-vector loader: depth-2 ZZ-style entangler with random
    Y-rotations, mirroring the structure of HHL preprints' b-prep figures."""
    rng = np.random.default_rng(seed)
    qc = QuantumCircuit(n_b, name="b_prep")
    angles = rng.uniform(-np.pi, np.pi, size=n_b)
    for i, a in enumerate(angles):
        qc.ry(float(a), i)
    for i in range(n_b - 1):
        qc.cx(i, i + 1)
    angles2 = rng.uniform(-np.pi, np.pi, size=n_b)
    for i, a in enumerate(angles2):
        qc.ry(float(a), i)
    return qc


def _u_proxy(n_b: int, steps: int, seed: int = 0) -> QuantumCircuit:
    """Hamiltonian-simulation proxy U = exp(-i H t).

    A depth-``steps`` Trotter-style circuit over n_b qubits that uses RZZ,
    RZ, RX gates only — same gate set as B4/B5 ansatze. Resource cost scales
    linearly in ``steps`` so controlled-U^{2^k} powers stack predictably.
    """
    rng = np.random.default_rng(seed + 17)
    qc = QuantumCircuit(n_b, name=f"U_proxy_s{steps}")
    for _ in range(steps):
        for i in range(n_b):
            qc.rz(float(rng.uniform(-np.pi, np.pi)), i)
        for i in range(n_b - 1):
            qc.rzz(float(rng.uniform(-np.pi, np.pi)), i, i + 1)
        for i in range(n_b):
            qc.rx(float(rng.uniform(-np.pi, np.pi)), i)
    return qc


def full_hhl(
    n_b: int,
    n_clock: int,
    hamiltonian_simulation_steps: int = 1,
    seed: int = 0,
    name: str = "HHL_full",
) -> QuantumCircuit:
    """Assemble the full HHL pipeline.

    Layout: [ancilla(1) | clock(n_clock) | work(n_b)].

    Includes:
      1. b-state preparation on work register
      2. Hadamards on clock register
      3. controlled-U^{2^k} for k = 0..n_clock-1 (forward QPE)
      4. inverse QFT on clock register
      5. controlled-RY(theta_j) on ancilla, controlled by each clock basis
         state (proxy: a fixed RY chain whose count scales with n_clock)
      6. forward QFT on clock register
      7. controlled-(U^{-1})^{2^k} (inverse QPE)
    """
    bp = b_state_prep(n_b, seed=seed)
    U = _u_proxy(n_b, steps=hamiltonian_simulation_steps, seed=seed)

    n_total = 1 + n_clock + n_b
    anc, clk0, wk0 = 0, 1, 1 + n_clock
    qc = QuantumCircuit(n_total, n_total, name=name)

    # 1. b-state prep on work register
    qc.compose(bp, qubits=list(range(wk0, wk0 + n_b)), inplace=True)
    # 2. Hadamards on clock
    for i in range(n_clock):
        qc.h(clk0 + i)
    # 3. Forward QPE: controlled-U^{2^k}
    for k in range(n_clock):
        power = 2 ** k
        ctrl_U = U.power(power).control(1)
        qc.compose(
            ctrl_U,
            qubits=[clk0 + k] + list(range(wk0, wk0 + n_b)),
            inplace=True,
        )
    # 4. Inverse QFT on clock
    qc.compose(QFT(n_clock, inverse=True, do_swaps=True),
               qubits=list(range(clk0, clk0 + n_clock)), inplace=True)
    # 5. Controlled-RY proxy on ancilla, one per clock qubit
    for j in range(n_clock):
        # Eigenvalue-dependent rotation; angle is a fixed proxy here.
        qc.cry(float(np.pi / (2 ** (j + 1))), clk0 + j, anc)
    # 6. Forward QFT on clock
    qc.compose(QFT(n_clock, inverse=False, do_swaps=True),
               qubits=list(range(clk0, clk0 + n_clock)), inplace=True)
    # 7. Inverse QPE: controlled-(U^-1)^{2^k}
    Uinv = U.inverse()
    for k in reversed(range(n_clock)):
        power = 2 ** k
        ctrl_Uinv = Uinv.power(power).control(1)
        qc.compose(
            ctrl_Uinv,
            qubits=[clk0 + k] + list(range(wk0, wk0 + n_b)),
            inplace=True,
        )
    qc.measure(range(n_total), range(n_total))
    return qc
