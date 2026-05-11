# Faithfulness Review: SD6

**Reviewer:** Vincent Wallerich  
**Review date:** 2026-04-24  
**Verdict:** **DRIFT_MAJOR**

---

## Paper

- **Title:** Quantum-inspired variational algorithms for partial differential equations: Application to financial derivative pricing
- **Authors:** Tianchen Zhao, Chuhao Sun, Asaf Cohen, James Stokes, Shravan Veerapaneni
- **Year:** 2022
- **Paper ID:** `439a750eda8c` · **Experiment:** `exp_1` · **Silo:** `derivative-pricing` · **Algorithm family:** `classical-simulation`

**Sources consulted:**
- Paper markdown: [p2_systematic_review/output/processed/439a750eda8c.md](p2_systematic_review/output/processed/439a750eda8c.md)
- Circuit: [p4_experiments/experiments/silos/derivative_pricing/439a750eda8c/circuit.py](p4_experiments/experiments/silos/derivative_pricing/439a750eda8c/circuit.py)
- Instance: [p4_experiments/experiments/silos/derivative_pricing/439a750eda8c/instance.json](p4_experiments/experiments/silos/derivative_pricing/439a750eda8c/instance.json)

---

## Verdict summary

Paper is a purely classical quantum-inspired VMC/NQS PDE solver with no quantum circuit; the implemented generic RealAmplitudes ansatz proxy cannot represent that algorithm, and the circuit/instance are mislabeled SD9.

## Checks

### ❌ Family-faithful

Cohort tag and @register both say 'classical-simulation', which matches the paper's category, but the implementation is an actual quantum RealAmplitudes ansatz. The paper constructs NO quantum circuit (autoregressive MADE NQS + classical VMC + Euler TDVP step). A generic variational ansatz is not a faithful proxy for a classical NQS PDE solver; the v2 operator_notes explicitly flag this and question Tier-1 inclusion.

### ✅ Scale-faithful

Paper reports up to n=16 mesh-qubit-equivalents; circuit uses n_qubits=6, well within the 12-qubit tractability cap and within ~factor 2.7 of the paper value (acceptable under the cap rule).

- `v2_n_qubits`: `16`
- `circuit_n_qubits`: `6`

### ✅ Structurally non-trivial

RealAmplitudes(reps=3, entanglement='linear') with seeded parameters and a compute-uncompute oracle variant; non-empty and gate-rich, but structurally generic (no NQS, no autoregressive sampling, no TDVP linear-system step, no Euler update — none of which are quantum-circuit constructs anyway).

### ❌ Metadata-consistent

instance.json uses instance_id 'SD9_v3_proxy_v1' and label 'SD9'; circuit.py docstring, @register(label='SD9'), build_bare name 'SD9_bare', full circuit name 'SD9_full', and register_accounting(label='SD9') all say SD9, but the task/cohort label is SD6 (paper_id 439a750eda8c). Also instance.json algorithm_family='other-gate-based' disagrees with cohort/circuit 'classical-simulation'.

## Concerns

- Label mismatch: every artifact (instance.json, circuit.py registrations, oracle name) is tagged SD9 while the cohort row and v2 extraction are SD6.
- instance.json algorithm_family='other-gate-based' contradicts cohort and circuit registration ('classical-simulation').
- Paper has no quantum circuit at all (quantum-inspired classical VMC with MADE NQS); a RealAmplitudes proxy is not an algorithmically meaningful representation of the paper's method.
- v2 operator_notes itself flags this paper for Tier-1 review ('should this even be in tier-1?').

## Recommendations

- Either drop SD6 from the Tier-1 quantum-circuit cohort (recommended, consistent with v2 extractor's flag) or relabel/rebuild as an explicit classical-simulation placeholder with zero quantum gates rather than a misleading variational ansatz.
- If retained, fix the SD9->SD6 label mismatch across instance.json and circuit.py (label, registration, oracle name, instance_id) and reconcile algorithm_family in instance.json with the cohort ('classical-simulation').
