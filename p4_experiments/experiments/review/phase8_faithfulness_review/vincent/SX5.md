# Faithfulness Review: SX5

**Reviewer:** Vincent Wallerich  
**Review date:** 2026-04-24  
**Verdict:** **DRIFT_MINOR**

---

## Paper

- **Title:** Quantum Heavy-tailed Bandits
- **Authors:** Yulian Wu, Chaowen Guan, Vaneet Aggarwal, Di Wang
- **Year:** 2023
- **Paper ID:** `a2b747cae698` · **Experiment:** `exp_1` · **Silo:** `other` · **Algorithm family:** `amplitude-estimation`

**Sources consulted:**
- Paper markdown: [p2_systematic_review/output/processed/a2b747cae698.md](p2_systematic_review/output/processed/a2b747cae698.md)
- Circuit: [p4_experiments/experiments/silos/other/a2b747cae698/circuit.py](p4_experiments/experiments/silos/other/a2b747cae698/circuit.py)
- Instance: [p4_experiments/experiments/silos/other/a2b747cae698/instance.json](p4_experiments/experiments/silos/other/a2b747cae698/instance.json)

---

## Verdict summary

Acknowledged template proxy (RealAmplitudes ansatz + inverse) for a purely theoretical heavy-tailed bandits paper with no implemented circuit; family tag aligns with cohort but circuit lacks AE structure, and metadata is internally inconsistent (registered label 'SX1' instead of SX5; instance.json algorithm_family='qaoa' contradicts cohort 'amplitude-estimation').

## Checks

### ❌ Family-faithful

Cohort family is amplitude-estimation and the @register decorator tags the circuit as amplitude-estimation, but the implementation is a generic RealAmplitudes ansatz with a compute-uncompute pair, not an AE/QPE/Grover-style structure. The paper itself only simulates AE outputs classically (no implementable AE circuit is described), so a generic ansatz proxy is acceptable per methodology, but it is not family-faithful in a structural sense.

### ✅ Scale-faithful

v2 extraction reports num_qubits as NOT_STATED (paper has no implemented circuit, only theoretical / classically-simulated AE oracles), so no paper-side scale to drift from. Implemented n_qubits=5 is well within the <=12 tractability cap.

- `v2_n_qubits`: `None`
- `circuit_n_qubits`: `5`

### ✅ Structurally non-trivial

Bare circuit is RealAmplitudes(n=5, reps=3, linear) and full circuit is ansatz . ansatz^dagger with measurement; non-trivial parameter count and entanglement, even though it does not encode AE-specific subcomponents (no QFT, no Grover oracle).

### ❌ Metadata-consistent

Multiple metadata defects: (1) the @register decorator and register_accounting both label this circuit 'SX1' rather than 'SX5', and the docstring/circuit names use 'SX1'; (2) instance.json sets instance_id='SX1_v3_proxy_v1', label='SX1', and algorithm_family='qaoa', which contradicts both the cohort algorithm_family='amplitude-estimation' and the @register algorithm_family='amplitude-estimation'; (3) algorithm_variant_paper in instance.json correctly names QTME/Heavy-QUCB but the family bucket disagrees.

## Concerns

- Circuit and instance files are tagged with label 'SX1' instead of 'SX5'; appears to be a copy-paste artifact across the SX cohort.
- instance.json algorithm_family='qaoa' is inconsistent with the cohort's 'amplitude-estimation' family and with the circuit registry tag.
- Implementation is a generic RealAmplitudes ansatz proxy and does not contain any amplitude-estimation structure (no QPE, no Grover oracle, no inverse QFT); resource estimates from this circuit will not reflect QTME/AE costs.
- Paper provides no concrete circuit (purely theoretical with classical simulation of AE output distribution), so any Phase-8 cost extrapolation from this proxy must be flagged as not paper-derived.

## Recommendations

- Rename register/register_accounting label and instance_id/label fields from 'SX1' to 'SX5' to match the cohort identifier.
- Set instance.json algorithm_family to 'amplitude-estimation' to match the cohort and the @register tag.
- If a more faithful AE proxy is desired, replace the RealAmplitudes compute-uncompute with a Montanaro-style amplitude-estimation template (state prep + Grover operator + inverse QFT) at small qubit count; otherwise keep the explicit 'template_proxy' note in downstream Phase-8 reporting.
