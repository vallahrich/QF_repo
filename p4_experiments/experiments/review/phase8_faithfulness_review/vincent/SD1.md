# Faithfulness Review: SD1

**Reviewer:** Vincent Wallerich  
**Review date:** 2026-04-24  
**Verdict:** **DRIFT_MAJOR**

---

## Paper

- **Title:** Efficient Hamiltonian Simulation for Solving Option Price Dynamics
- **Authors:** Javier Gonzalez-Conde, Ángel Rodríguez-Rozas, Enrique Solano, Mikel Sanz
- **Year:** 2024
- **Paper ID:** `0608ad48d5b8` · **Experiment:** `exp_1` · **Silo:** `derivative-pricing` · **Algorithm family:** `quantum-simulation`

**Sources consulted:**
- Paper markdown: [p2_systematic_review/output/processed/0608ad48d5b8.md](p2_systematic_review/output/processed/0608ad48d5b8.md)
- Circuit: [p4_experiments/experiments/silos/derivative_pricing/0608ad48d5b8__exp_1/circuit.py](p4_experiments/experiments/silos/derivative_pricing/0608ad48d5b8__exp_1/circuit.py)
- Instance: [p4_experiments/experiments/silos/derivative_pricing/0608ad48d5b8__exp_1/instance.json](p4_experiments/experiments/silos/derivative_pricing/0608ad48d5b8__exp_1/instance.json)

---

## Verdict summary

Circuit is a generic RealAmplitudes compute-uncompute ansatz at the paper's 9-qubit scale, which does not represent the paper's QSP/qubitization Hamiltonian-simulation algorithm class.

## Checks

### ❌ Family-faithful

Paper algorithm family is Hamiltonian simulation via Quantum Signal Processing / qubitization with unitary dilation, QFT diagonalization of the momentum operator, and post-selection on an embedding ancilla. The implemented circuit is a generic linear-entanglement RealAmplitudes variational ansatz followed by its inverse (compute-uncompute) — a variational-ansatz family, not a Hamiltonian-simulation primitive. Cohort/registry tag 'quantum-simulation' matches the paper, but the actual circuit body does not.

### ✅ Scale-faithful

Implemented n_qubits=9 matches v2_extraction.circuit.num_qubits=9 (8 spatial + 1 embedding ancilla + 1 duplication qubit collapsed into the same 9-qubit register). Exact match, well within the factor-of-2 tolerance.

- `v2_n_qubits`: `9`
- `circuit_n_qubits`: `9`

### ❌ Structurally non-trivial

A faithful Hamiltonian-simulation/QSP circuit would contain QFT (and inverse QFT) blocks for momentum diagonalization, block-encoding/qubitization or QSP-style controlled rotations, an embedding ancilla actually used for unitary dilation, and post-selection/measurement on that ancilla. The circuit contains none of these structural markers — only RealAmplitudes Ry layers with linear CX entanglement, then its inverse, then a full-register computational measurement. The compute-uncompute pair makes the bare oracle action approximately identity on the seeded parameters, providing no algorithmic content beyond the ansatz template.

### ✅ Metadata-consistent

instance.json and circuit.py both explicitly and consistently disclose the proxy status (instance notes 'does NOT implement the paper's algorithm'; circuit docstring repeats 'template-proxy methodology'; oracle_variant='ansatz-compute-uncompute-template-proxy'). n_qubits, paper_id, label, silo, and algorithm_family tags are internally consistent across cohort/instance/circuit registry.

## Concerns

- family_drift: paper is QSP/qubitization Hamiltonian simulation; proxy is a variational RealAmplitudes ansatz — different algorithmic families despite sharing the 'quantum-simulation' silo tag.
- No QFT, no block-encoding, no QSP rotation structure, and no embedding-ancilla post-selection are present, so the proxy carries none of the structural cost drivers (QSP query repetitions, controlled phase oracles) that would dominate the paper's resource profile.
- Compute-uncompute of a randomly-seeded ansatz approximates identity, so the 'full' oracle path contributes essentially no additional gate-cost-relevant structure beyond the bare ansatz.

## Recommendations

- Ensure downstream Phase-8 reporting flags SD1 as P-tier/template-proxy and excludes it from any family-faithful headline aggregate.
- If a stronger proxy is desired without re-implementing full QSP, swap the ansatz_stretch template for a QFT-based template (QFT + diagonal phase + inverse QFT on 8 spatial qubits with a single embedding ancilla) to at least preserve the paper's structural cost drivers.
