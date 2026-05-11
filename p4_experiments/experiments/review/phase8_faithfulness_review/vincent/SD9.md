# Faithfulness Review: SD9

**Reviewer:** Vincent Wallerich  
**Review date:** 2026-04-24  
**Verdict:** **DRIFT_MINOR**

---

## Paper

- **Title:** Noise-Robust Quantum Generative Models for Distribution Learning and Efficient Data Loading
- **Authors:** Ankit Kumar Mandusia
- **Year:** 2025
- **Paper ID:** `872cedb13e27` · **Experiment:** `exp_1` · **Silo:** `derivative-pricing` · **Algorithm family:** `other-gate-based`

**Sources consulted:**
- Paper markdown: [p2_systematic_review/output/processed/872cedb13e27.md](p2_systematic_review/output/processed/872cedb13e27.md)
- Circuit: [p4_experiments/experiments/silos/derivative_pricing/872cedb13e27__exp_1/circuit.py](p4_experiments/experiments/silos/derivative_pricing/872cedb13e27__exp_1/circuit.py)
- Instance: [p4_experiments/experiments/silos/derivative_pricing/872cedb13e27__exp_1/instance.json](p4_experiments/experiments/silos/derivative_pricing/872cedb13e27__exp_1/instance.json)

---

## Verdict summary

Generic RealAmplitudes ansatz at the paper's 6-qubit qGAN loader scale is a defensible template proxy for the EfficientSU2 generator, but it omits the QAE oracle/QFT structure used for the pricing experiment.

## Checks

### ✅ Family-faithful

Paper uses a variational qGAN loader (EfficientSU2 reps=8) plus QAE for pricing. RealAmplitudes is a reasonable variational-ansatz proxy for the EfficientSU2 generator, and the cohort family 'other-gate-based' is consistent with a hybrid qGAN+QAE workload.

### ✅ Scale-faithful

Circuit n_qubits=6 matches v2 num_qubits=6 (qGAN loader scale; the separate QAE pricing experiment used 10 qubits but the canonical v2 field winner is 6).

- `v2_n_qubits`: `6`
- `circuit_n_qubits`: `6`

### ❌ Structurally non-trivial

Circuit is a parametrised RealAmplitudes(reps=3) plus an ansatz-inverse compute/uncompute pair. It is non-trivial as a variational ansatz, but it lacks the amplitude-estimation structure (Grover-style oracle + inverse QFT / QPE) that v2 lists as oracle_structure='amplitude_estimation' and measurement='QPE'. Acknowledged as a template proxy.

### ✅ Metadata-consistent

Cohort/instance algorithm_family='other-gate-based' matches the registered circuit; instance.notes and circuit docstring openly disclose this is an ansatz_stretch template proxy authored 2026-04-23 and does NOT implement the paper's qGAN+QAE algorithm. Random seed and parameter counts are coherent.

## Concerns

- Implementation does not reflect the paper's QAE oracle/QPE measurement structure; only the variational loader half of the pipeline is proxied.
- ansatz_layers in the circuit (reps=3) is much smaller than the paper's EfficientSU2 reps=8, so depth/parameter scaling is not representative for resource estimation.
- RealAmplitudes (RY+CX linear) differs in two-qubit-gate structure from EfficientSU2 (RY/RZ + CX full/linear), which will under-estimate 2q gate count for Phase-8 cost projection.

## Recommendations

- If a tighter proxy is desired later, swap RealAmplitudes for EfficientSU2(reps=8) to match the paper's loader, and optionally append a small QAE block (e.g., 2-3 eval qubits + inverse QFT) to capture the measurement-side cost.
- Document in the cohort that SD9's resource estimate covers the qGAN loader only, not the QAE pricing oracle, so downstream Phase-8 totals are not misread.
