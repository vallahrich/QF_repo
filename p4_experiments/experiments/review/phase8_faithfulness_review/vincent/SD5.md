# Faithfulness Review: SD5

**Reviewer:** Vincent Wallerich  
**Review date:** 2026-04-24  
**Verdict:** **DRIFT_MAJOR**

---

## Paper

- **Title:** Efficient Hamiltonian Simulation for Solving Option Price Dynamics
- **Authors:** Javier Gonzalez-Conde, Ángel Rodríguez-Rozas, Enrique Solano, Mikel Sanz
- **Year:** 2024
- **Paper ID:** `349c85ac46df` · **Experiment:** `exp_1` · **Silo:** `derivative-pricing` · **Algorithm family:** `quantum-simulation`

**Sources consulted:**
- Paper markdown: [p2_systematic_review/output/processed/349c85ac46df.md](p2_systematic_review/output/processed/349c85ac46df.md)
- Circuit: [p4_experiments/experiments/silos/derivative_pricing/349c85ac46df/circuit.py](p4_experiments/experiments/silos/derivative_pricing/349c85ac46df/circuit.py)
- Instance: [p4_experiments/experiments/silos/derivative_pricing/349c85ac46df/instance.json](p4_experiments/experiments/silos/derivative_pricing/349c85ac46df/instance.json)

---

## Verdict summary

Generic RealAmplitudes ansatz with compute-uncompute pair does not implement or structurally resemble the paper's QSP/QFT/unitary-dilation Hamiltonian-simulation algorithm; also under-scaled (6 vs 9 qubits) and metadata uses wrong label 'SD8'.

## Checks

### ❌ Family-faithful

Cohort/registry tag is 'quantum-simulation' matching the paper's family, but the implemented circuit is a variational RealAmplitudes ansatz with compute-uncompute, which belongs to the variational-ansatz family rather than to gate-based Hamiltonian simulation (QSP/qubitization + QFT + unitary dilation). The instance.json itself flags algorithm_family as 'other-gate-based' and explicitly states 'does NOT implement the paper's algorithm'. This is a template-proxy mismatch in family terms.

### ✅ Scale-faithful

Paper reports 9 qubits (8 discretization + 1 dilation ancilla); circuit uses 6 qubits. 9/6 = 1.5, within the factor-of-2 tolerance, so scale is acceptable as a proxy.

- `v2_n_qubits`: `9`
- `circuit_n_qubits`: `6`

### ❌ Structurally non-trivial

Circuit is structurally trivial as a Hamiltonian-simulation proxy: it is a RealAmplitudes ansatz composed with its inverse (U U^dagger), which collapses to the identity up to parameter assignment. There is no QFT, no diagonal momentum-phase rotation, no QSP/qubitization block, no block-encoding oracle, and no ancilla-based unitary dilation / post-selection — i.e., none of the structural components a QSP-based Black–Scholes Hamiltonian-simulation paper would use.

### ❌ Metadata-consistent

Identity drift: file is for label_id SD5 (paper 349c85ac46df) but the circuit's @register label, register_accounting label, function names ('SD8_bare', 'SD8_full'), docstring, description, and instance.json's instance_id ('SD8_v3_proxy_v1') and label ('SD8') all say SD8. instance.json algorithm_family ('other-gate-based') also disagrees with the registry tag ('quantum-simulation').

## Concerns

- Label/identity mismatch throughout circuit.py and instance.json (says 'SD8', should be 'SD5').
- Algorithm_family disagreement between instance.json ('other-gate-based') and circuit registry ('quantum-simulation').
- Implemented circuit is U . U^dagger (RealAmplitudes compose inverse), which is functionally an identity proxy and carries no Hamiltonian-simulation structure.
- No QFT, no QSP/qubitization phase sequence, no block-encoding oracle, no dilation ancilla / post-selection step — all of which are central to the paper's algorithm.
- Instance is documented as a template proxy that 'does NOT implement the paper's algorithm', which is faithful documentation but means the proxy must be flagged as family/structural drift, not CONFIRMED.

## Recommendations

- Rename all 'SD8' references in circuit.py and instance.json to 'SD5' (label, instance_id, function names, docstring, description).
- Reconcile algorithm_family: either keep 'quantum-simulation' in both registry and instance.json or downgrade both to 'other-gate-based' to match the proxy nature.
- If the cohort wants a structurally meaningful proxy, replace the RealAmplitudes-compose-inverse oracle with a small QFT + diagonal phase + inverse-QFT block on n discretization qubits plus one dilation ancilla (mirroring the paper's QFT/QSP/dilation skeleton at small scale), which is tractable at n<=8.
