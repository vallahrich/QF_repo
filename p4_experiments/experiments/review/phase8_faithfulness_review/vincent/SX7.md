# Faithfulness Review: SX7

**Reviewer:** Vincent Wallerich  
**Review date:** 2026-04-24  
**Verdict:** **DRIFT_MAJOR**

---

## Paper

- **Title:** Quantum Heavy-tailed Bandits
- **Authors:** Yulian Wu, Chaowen Guan, Vaneet Aggarwal, Di Wang
- **Year:** 2023
- **Paper ID:** `a2b747cae698` · **Experiment:** `exp_3` · **Silo:** `other` · **Algorithm family:** `amplitude-estimation`

**Sources consulted:**
- Paper markdown: [p2_systematic_review/output/processed/a2b747cae698.md](p2_systematic_review/output/processed/a2b747cae698.md)
- Circuit: [p4_experiments/experiments/silos/other/a2b747cae698/circuit.py](p4_experiments/experiments/silos/other/a2b747cae698/circuit.py)
- Instance: [p4_experiments/experiments/silos/other/a2b747cae698/instance.json](p4_experiments/experiments/silos/other/a2b747cae698/instance.json)

---

## Verdict summary

Circuit is a generic RealAmplitudes ansatz template with no amplitude-estimation structure (no Grover-style oracle, no QPE/inverse-QFT), so it does not represent the paper's AE-based QTME algorithm class; instance.json also tags the family as 'qaoa', inconsistent with the cohort and registry 'amplitude-estimation' tag.

## Checks

### ❌ Family-faithful

Registry @register tag is 'amplitude-estimation' (matches cohort and paper's QTME=AE-based mean estimator), but the implemented circuit is a generic variational ansatz (RealAmplitudes) with no AE-specific components. As an AE proxy this is family drift; the implementation is effectively a variational/QAOA-shaped proxy, not an AE-shaped proxy.

### ✅ Scale-faithful

Paper does not state a qubit count (NOT_STATED). Circuit uses n_qubits=5, which is within the <=12 tractability cap and is a reasonable small-scale proxy.

- `v2_n_qubits`: `None`
- `circuit_n_qubits`: `5`

### ❌ Structurally non-trivial

Per the audit rubric, an amplitude-estimation circuit must have a Grover-style oracle and an inverse QFT (QPE-like structure). The full variant here is just A . A^dagger (compute-uncompute of a RealAmplitudes ansatz) followed by computational-basis measurement. There is no Grover oracle, no controlled-Q powers, and no inverse QFT, so the circuit lacks AE structure.

### ❌ Metadata-consistent

instance.json sets algorithm_family='qaoa' and instance_id/label='SX1' (not SX7), while the cohort/prompt and the @register decorator declare algorithm_family='amplitude-estimation' for label SX7. The registered label in circuit.py is also 'SX1', not 'SX7'. Multiple metadata inconsistencies.

## Concerns

- Implemented circuit is a generic RealAmplitudes ansatz proxy; it shares no structural resemblance to amplitude estimation (no Grover oracle, no inverse QFT, no QPE register).
- Registry decorator labels this circuit as 'SX1' with paper a2b747cae698, but this audit triple is SX7 (exp_3); appears to be a shared/reused circuit across SX5/SX6/SX7 (operator note flags redundancy).
- instance.json algorithm_family='qaoa' contradicts cohort.algorithm_family='amplitude-estimation' and the @register tag.
- Paper's circuit fields are entirely NOT_STATED, so the proxy cannot be validated against any paper-reported qubit/depth/gate counts.

## Recommendations

- If the methodology permits a generic ansatz proxy, retag instance.json algorithm_family to match the cohort ('amplitude-estimation') and document explicitly that the proxy is an ansatz_stretch placeholder, not an AE implementation.
- Add a label-specific @register entry for SX7 (and SX5, SX6) rather than reusing the SX1 registration, so accounting and provenance are not collapsed across distinct cohort rows.
- If structural faithfulness is required for the AE family, replace the compute-uncompute pair with at minimum a controlled-Q-style oracle plus inverse-QFT QPE block at small qubit count (e.g., the Qiskit AmplitudeEstimation primitive), so the circuit is recognizably AE-shaped.
