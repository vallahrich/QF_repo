"""T3 \u2014 Quantum reservoir computing transplant for fraud-stream classification.

Bare: a single feature-injection + one reservoir Hamiltonian-evolution
timestep on a 4-qubit transverse-field Ising reservoir. This is the depth
a reservoir-computing paper would typically headline: "our reservoir has
depth 3" or similar.

Full: the full streaming rollout \u2014 T feature-injection blocks
interleaved with T reservoir timesteps. This is the per-sample cost that
actually has to be paid to classify one streaming transaction. Papers
reporting reservoir-computing results rarely multiply the per-step depth
by the number of timesteps; T3 exhibits that gap.
"""

from __future__ import annotations

from typing import Any, Dict

import numpy as np
from qiskit import QuantumCircuit

from p4_experiments.core.circuit_registry import register
from p4_experiments.core.oracle_accounting import register_accounting


def _feature_vector(instance: Dict[str, Any]) -> np.ndarray:
    p = instance.get("parameters", instance)
    rng = np.random.default_rng(int(p.get("random_seed", 0)))
    return rng.uniform(-1.0, 1.0, size=int(p["n_features"]))


def _feature_injection(n: int, features: np.ndarray, reps: int) -> QuantumCircuit:
    qc = QuantumCircuit(n, name="feature_inject")
    for _ in range(reps):
        for q in range(n):
            qc.ry(np.pi * float(features[q % len(features)]), q)
        for q in range(n - 1):
            qc.cx(q, q + 1)
    return qc


def _reservoir_step(n: int, trotter_steps: int, seed: int) -> QuantumCircuit:
    """Single Trotterised timestep of a transverse-field Ising reservoir."""
    rng = np.random.default_rng(seed + 101)
    Js = rng.uniform(0.5, 1.5, size=n - 1)
    hs = rng.uniform(0.5, 1.5, size=n)
    dt = 1.0 / max(trotter_steps, 1)

    qc = QuantumCircuit(n, name="reservoir_step")
    for _ in range(trotter_steps):
        # ZZ interactions
        for i, J in enumerate(Js):
            qc.rzz(2.0 * float(J) * dt, i, i + 1)
        # Transverse field
        for i, h in enumerate(hs):
            qc.rx(2.0 * float(h) * dt, i)
    return qc


@register(
    label="T3",
    paper_id="transplant-T3",
    silo="fraud-detection",
    algorithm_family="quantum-reservoir-computing",
    description="Reservoir-computing transplant \u2014 fraud stream",
)
def build_bare(instance: Dict[str, Any]) -> QuantumCircuit:
    p = instance["parameters"]
    n = int(p["n_qubits"])
    reps = int(p["feature_injection_reps"])
    trotter = int(p["reservoir_trotter_steps"])
    seed = int(p["random_seed"])
    features = _feature_vector(instance)

    qc = QuantumCircuit(n, n, name="T3_bare")
    qc.compose(_feature_injection(n, features, reps), qubits=range(n), inplace=True)
    qc.compose(_reservoir_step(n, trotter, seed), qubits=range(n), inplace=True)
    qc.measure(range(n), range(n))
    return qc


def _full_state_prep(instance: Dict[str, Any], bare: QuantumCircuit) -> QuantumCircuit:
    return bare


def _full_oracle(instance: Dict[str, Any], bare: QuantumCircuit) -> QuantumCircuit:
    """Extend the single-step bare circuit to the full streaming rollout."""
    p = instance["parameters"]
    n = int(p["n_qubits"])
    reps = int(p["feature_injection_reps"])
    trotter = int(p["reservoir_trotter_steps"])
    timesteps = int(p["n_reservoir_timesteps"])
    seed = int(p["random_seed"])
    features = _feature_vector(instance)

    qc = QuantumCircuit(n, n, name=f"T3_full_T{timesteps}")
    # One reservoir step is already part of "bare"; the full rollout has
    # n_reservoir_timesteps feature-injection + evolution blocks in total.
    for t in range(timesteps):
        qc.compose(_feature_injection(n, features, reps), qubits=range(n), inplace=True)
        qc.compose(_reservoir_step(n, trotter, seed + t), qubits=range(n), inplace=True)
    qc.measure(range(n), range(n))
    return qc


register_accounting(
    label="T3",
    state_prep=_full_state_prep,
    oracle=_full_oracle,
    oracle_variant="reservoir-full-streaming-rollout",
    notes=(
        "Full mode = T feature-injection + reservoir-evolution blocks where "
        "T = n_reservoir_timesteps. Bare mode = a single such block."
    ),
)
