"""B5 — QGAN-trained distribution loader feeding canonical QAE.

Bare: generator circuit only (RealAmplitudes ansatz at trained-parameters
proxy). Full: generator + canonical QAE pipeline — eval register in
uniform superposition, controlled Grover powers, inverse QFT. The ``amplitude
estimation on QGAN-loaded state'' claim's oracle tax lies entirely in the
QAE pipeline, not in the generator.
"""

from __future__ import annotations

from typing import Any, Dict

import numpy as np
from qiskit import QuantumCircuit
from qiskit.circuit.library import RealAmplitudes, QFT

from p4_experiments.core.circuit_registry import register
from p4_experiments.core.oracle_accounting import register_accounting


def _generator(instance: Dict[str, Any]) -> QuantumCircuit:
    p = instance.get("parameters", instance)
    n = int(p["n_qubits"])
    ansatz = RealAmplitudes(num_qubits=n, reps=int(p["generator_reps"]))
    rng = np.random.default_rng(int(p.get("random_seed", 0)))
    x = rng.uniform(-np.pi, np.pi, size=ansatz.num_parameters)
    return ansatz.assign_parameters(x)


@register(
    label="B5",
    paper_id="c57f6422ed7b",
    silo="quantum-ml-finance",
    algorithm_family="quantum-ml",
    description="QGAN-loaded AE — bare = generator only",
)
def build_bare(instance: Dict[str, Any]) -> QuantumCircuit:
    gen = _generator(instance)
    qc = QuantumCircuit(gen.num_qubits, gen.num_qubits, name="B5_bare")
    qc.compose(gen, inplace=True)
    qc.measure(range(gen.num_qubits), range(gen.num_qubits))
    return qc


def _controlled_grover_proxy(n: int) -> QuantumCircuit:
    """A minimal Grover-operator proxy over n work qubits: phase flip on |0>^n
    reflection (marked state) followed by a reflection about the mean using the
    diffusion operator. Sufficient to surface the controlled-Grover-power cost
    under the QDK Resource Estimator; no finance semantics asserted.
    """
    qc = QuantumCircuit(n, name="Q_proxy")
    # Oracle: flip phase of |0...0>
    qc.x(range(n))
    qc.h(n - 1)
    qc.mcx(list(range(n - 1)), n - 1)
    qc.h(n - 1)
    qc.x(range(n))
    # Diffusion
    qc.h(range(n))
    qc.x(range(n))
    qc.h(n - 1)
    qc.mcx(list(range(n - 1)), n - 1)
    qc.h(n - 1)
    qc.x(range(n))
    qc.h(range(n))
    return qc


def _full_state_prep(instance: Dict[str, Any], bare: QuantumCircuit) -> QuantumCircuit:
    return bare  # generator is the state prep


def _full_oracle(instance: Dict[str, Any], bare: QuantumCircuit) -> QuantumCircuit:
    p = instance["parameters"]
    m = int(p["num_eval_qubits"])
    gen = _generator(instance)
    n_work = gen.num_qubits
    Q = _controlled_grover_proxy(n_work)

    total = m + n_work
    qc = QuantumCircuit(total, total, name="B5_full_QAE")
    for i in range(m):
        qc.h(i)
    qc.compose(gen, qubits=list(range(m, m + n_work)), inplace=True)
    for k in range(m):
        power = 2 ** k
        ctrl_Q = Q.power(power).control(1)
        qc.compose(ctrl_Q, qubits=[k] + list(range(m, m + n_work)), inplace=True)
    qc.compose(QFT(m, inverse=True, do_swaps=True),
               qubits=list(range(m)), inplace=True)
    qc.measure(range(total), range(total))
    return qc


register_accounting(
    label="B5",
    state_prep=_full_state_prep,
    oracle=_full_oracle,
    oracle_variant="QGAN+canonical-QAE",
    notes=(
        "Full mode = generator + controlled Grover^{2^k} over num_eval_qubits "
        "+ inverse QFT. Bare mode = generator only (paper-reported depth)."
    ),
)
