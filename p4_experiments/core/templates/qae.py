"""
QAE template — canonical Grover-based Quantum Amplitude Estimation.

Used by SM1, SM2, SM3 (sim-MC papers whose claimed advantage rests on QAE
applied to a problem-specific state preparation).

Fidelity tier note (2026-05-02): SM1, SM2, SM3 share the same
``grover_proxy`` Grover-operator scaffolding; the per-paper resource
estimates differ only through extracted scale parameters and the
state-preparation slot. These labels live at the paper-family-template
tier (PRE_REGISTRATION.md section 0a); manuscript prose must not
promote H4 results to strict paper-faithful claims.

Bare mode: state-preparation circuit only.
Full mode: ``canonical_qae(state_prep, num_eval_qubits)`` — eval register in
uniform superposition, controlled Grover^{2^k}, inverse QFT.
"""

from __future__ import annotations

from qiskit import QuantumCircuit
from qiskit.circuit.library import QFT


def grover_proxy(n: int) -> QuantumCircuit:
    """Minimal Grover operator: phase flip on |0>^n then diffusion.

    Matches B5's ``_controlled_grover_proxy`` so SM1/SM2/SM3 share the same
    QDK-resource footprint per Grover iterate as B5 does. No problem-specific
    semantics; the resource cost is what we care about for tau accounting.
    """
    qc = QuantumCircuit(n, name="Q_proxy")
    qc.x(range(n))
    qc.h(n - 1)
    if n >= 2:
        qc.mcx(list(range(n - 1)), n - 1)
    qc.h(n - 1)
    qc.x(range(n))
    qc.h(range(n))
    qc.x(range(n))
    qc.h(n - 1)
    if n >= 2:
        qc.mcx(list(range(n - 1)), n - 1)
    qc.h(n - 1)
    qc.x(range(n))
    qc.h(range(n))
    return qc


def canonical_qae(
    state_prep: QuantumCircuit,
    num_eval_qubits: int,
    name: str = "QAE_full",
) -> QuantumCircuit:
    """Assemble canonical QAE: state prep + 2^k controlled Grover + inverse QFT.

    The eval register is the high-order block; the work register receives the
    state preparation. Includes terminal measurement on all qubits.
    """
    n_work = state_prep.num_qubits
    m = num_eval_qubits
    Q = grover_proxy(n_work)

    total = m + n_work
    qc = QuantumCircuit(total, total, name=name)
    for i in range(m):
        qc.h(i)
    qc.compose(state_prep, qubits=list(range(m, m + n_work)), inplace=True)
    for k in range(m):
        power = 2 ** k
        ctrl_Q = Q.power(power).control(1)
        qc.compose(ctrl_Q, qubits=[k] + list(range(m, m + n_work)), inplace=True)
    qc.compose(QFT(m, inverse=True, do_swaps=True),
               qubits=list(range(m)), inplace=True)
    qc.measure(range(total), range(total))
    return qc
