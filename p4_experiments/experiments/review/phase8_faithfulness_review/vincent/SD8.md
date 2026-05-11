# Faithfulness Review: SD8

**Reviewer:** Vincent Wallerich  
**Review date:** 2026-04-24  
**Verdict:** **CONFIRMED**

---

## Paper

- **Title:** Extracting a function encoded in amplitudes of a quantum state by tensor network and orthogonal function expansion
- **Authors:** Koichi Miyamoto, Hiroshi Ueda
- **Year:** 2023
- **Paper ID:** `871c63b61487` · **Experiment:** `exp_1` · **Silo:** `derivative-pricing` · **Algorithm family:** `other-gate-based`

**Sources consulted:**
- Paper markdown: [p2_systematic_review/output/processed/871c63b61487.md](p2_systematic_review/output/processed/871c63b61487.md)
- Circuit: [p4_experiments/experiments/silos/derivative_pricing/871c63b61487__exp_1/circuit.py](p4_experiments/experiments/silos/derivative_pricing/871c63b61487__exp_1/circuit.py)
- Instance: [p4_experiments/experiments/silos/derivative_pricing/871c63b61487__exp_1/instance.json](p4_experiments/experiments/silos/derivative_pricing/871c63b61487__exp_1/instance.json)

---

## Verdict summary

Generic RealAmplitudes ansatz_stretch proxy is a defensible template stand-in for a paper whose quantum resource counts (qubits, depth, gates) are entirely NOT_STATED, and the algorithm_family bucket 'other-gate-based' is consistent with the paper's bespoke VMPS construction.

## Checks

### ✅ Family-faithful

Paper proposes a bespoke variational MPS (VMPS) circuit plus orthogonal-basis oracle blocks V_i^OF — neither HHL/QPE/QAE/VQE nor a standard hardware-efficient ansatz. Cohort tag 'other-gate-based' is the appropriate catch-all bucket; instance.json honestly labels the proxy as 'generic variational ansatz stretch (template proxy)'.

### ✅ Scale-faithful

Paper does not state any qubit count for VMPS or V_i^OF (v2 num_qubits = NOT_STATED); n=5 was chosen because d=5 assets, which is a reasonable small-scale proxy and well within the Tier-1 cap of 12.

- `v2_n_qubits`: `None`
- `circuit_n_qubits`: `5`

### ✅ Structurally non-trivial

RealAmplitudes(n=5, reps=3, entanglement='linear') with random-parameter assignment is non-trivial; full variant is an ansatz . ansatz^dagger compute–uncompute pair followed by computational-basis measurement. This does not reproduce the paper's MPS/SVD optimization or Hadamard-test overlap estimation, but as an explicit template proxy under the documented ansatz_stretch methodology it is structurally valid for resource-estimation purposes.

### ✅ Metadata-consistent

label_id, paper_id, silo='derivative-pricing', and algorithm_family='other-gate-based' agree across instance.json, circuit.py @register/register_accounting, and the cohort entry. instance.notes and circuit docstring both transparently flag this as a non-faithful template proxy authored 2026-04-23.

## Concerns

- Circuit does NOT implement the paper's actual algorithm (no MPS block structure, no orthogonal-basis V_i^OF oracle, no Hadamard test, no SVD-based block update); it is purely a generic ansatz proxy and any Phase-8 resource estimate derived from it should be interpreted as a template-class lower bound, not as a faithful estimate of VMPS+V_i^OF.
- Qubit count n=5 is anchored to the paper's d=5 asset dimension rather than to a stated qubit count, because the paper provides none; the true qubit requirement of the proposed circuit is unknown and could be substantially larger once V_i^OF basis-state preparation and ancillae are accounted for.

## Recommendations

- Keep instance.notes and circuit.py docstring wording explicit that the proxy does not implement the paper's algorithm so downstream resource-aggregation never silently treats SD8 as a faithful VMPS/Hadamard-test cost estimate.
- If a higher-fidelity proxy is later desired, consider a scale-controlled MPS-shaped brick-wall ansatz (linear nearest-neighbor 2-qubit blocks, depth ~ d) to better reflect the paper's VMPS topology, but this is optional under the current template-proxy methodology.
