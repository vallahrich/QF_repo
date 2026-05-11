# Triage: SQ9

**Reviewers (joint):** Vincent Wallerich + Aleix Telesforo  
**Triage date:** 2026-04-25  
**Vincent verdict (first pass):** **DRIFT_MAJOR**

---

## Paper

- **Title:** Quantum machine learning for quantum anomaly detection
- **Paper ID:** `53a718c11ea8` · **Experiment:** `exp_2` · **Silo:** `quantum-ml-finance` · **Cohort algorithm family:** `other-gate-based`

**Sources to consult:**
- Paper markdown: [p2_systematic_review/output/processed/53a718c11ea8.md](p2_systematic_review/output/processed/53a718c11ea8.md)
- Circuit: [p4_experiments/experiments/silos/quantum_ml_finance/53a718c11ea8/circuit.py](p4_experiments/experiments/silos/quantum_ml_finance/53a718c11ea8/circuit.py)
- Instance: [p4_experiments/experiments/silos/quantum_ml_finance/53a718c11ea8/instance.json](p4_experiments/experiments/silos/quantum_ml_finance/53a718c11ea8/instance.json)
- Phase 3 LLM extraction (GPT 5.3 / GPT 5.4-mini, P3 s2_quantitative): [p3_thematic_synthesis/s2_quantitative/output/extractions/53a718c11ea8.json](p3_thematic_synthesis/s2_quantitative/output/extractions/53a718c11ea8.json) (experiment_id `exp_2`)
- Vincent's review: [../vincent/SQ9.md](../vincent/SQ9.md)

---

## Disagreement

Vincent's review (first pass) flagged this label as **DRIFT_MAJOR** —
i.e. the implemented circuit does not faithfully match what the
Phase 3 LLM extraction (GPT 5.3 / GPT 5.4-mini) recorded the paper's algorithm to be.

**Vincent's verdict summary:** Circuit is a generic RealAmplitudes ansatz template proxy with no HHL/QPE structure, while the paper's exp_2 is explicitly the HHL-based quantum one-class SVM variant; additionally the circuit/instance carry SQ10 labels and a 'quantum-svm' family tag rather than SQ9.

## Phase 3 (LLM) extraction — values for this label

**Source:** [p3_thematic_synthesis/s2_quantitative/output/extractions/53a718c11ea8.json](p3_thematic_synthesis/s2_quantitative/output/extractions/53a718c11ea8.json) (experiment_id `exp_2`)  
**Models used (per source `extraction_metadata.models_used`):** `gpt-5.3` (synthesis) + `gpt-5.4-mini` (extraction steps).

| Field | Phase 3 value |
|---|---|
| `algorithm_family` | `other-gate-based` |
| `algorithm_variant` | `quantum one-class SVM for pure-state anomaly detection` |
| `num_qubits` | _(not extracted in P3 S2)_ |
| `ansatz` (free-text) | _(not extracted in P3 S2)_ |
| `num_layers` | _(not extracted in P3 S2)_ |
| `circuit_depth` | _(not extracted in P3 S2)_ |
| `oracle_structure` | _(not extracted in P3 S2)_ |
| `encoding` | _(not extracted in P3 S2)_ |

_Note: P3 s2_quantitative extracts paper-level algorithm and quantum-resource fields. Circuit-level details that are not in the S2 schema (e.g. `oracle_structure`, `encoding`) appear as _(not extracted in P3 S2)_ above. Vincent's per-check notes below adjudicate those fields from direct paper + circuit reading._

### Vincent's per-check notes

| Check | Result | Note |
|---|---|---|
| Family-faithful | ❌ | Paper exp_2 is HHL-based quantum one-class SVM (block-encoded QSP / QPE / density-matrix exponentiation per v2 extraction). Circuit is a generic linear RealAmplitudes ansatz with no linear-system-solving structure. Cohort tag 'other-gate-based' and circuit registry tag 'quantum-svm' both fail to match the HHL/quantum-linear-systems family the paper claims for this experiment. |
| Scale-faithful | ✅ | Paper does not state qubit count (NOT_STATED). Implemented n_qubits=5 is within the <=12 tractability cap and is a reasonable small-scale proxy. |
| Structurally non-trivial | ❌ | An HHL-shaped circuit would require QPE on a controlled e^{-iKt} block plus controlled rotations and uncomputation. The implementation is only RealAmplitudes . RealAmplitudes^dagger (compute-uncompute), which has no QPE register, no controlled Hamiltonian-evolution block, and no eigenvalue-inversion rotation. It is non-trivial as a generic ansatz but not structurally representative of the HHL-class algorithm. |
| Metadata-consistent | ❌ | instance.json reports label='SQ10', experiment_id='exp_1', and algorithm_variant_paper='quantum kernel PCA for anomaly detection (pure states)'; circuit.py registers label='SQ10' with algorithm_family='quantum-svm'. None of these match the SQ9 / exp_2 (HHL one-class SVM) target. Note explicitly says 'does NOT implement the paper's algorithm'. |

### Concerns raised by Vincent

- Wrong experiment binding: SQ9 targets exp_2 (HHL variant) but the implementation files are labeled SQ10 / exp_1 (kernel PCA pure-states variant).
- Family drift: HHL/quantum-linear-systems paper algorithm represented by a generic RealAmplitudes ansatz with no QPE or matrix-inversion structure.
- Cohort algorithm_family tag 'other-gate-based' inconsistent with both paper (HHL) and circuit registry tag 'quantum-svm'.
- Self-declared in instance notes: 'The implemented circuit ... does NOT implement the paper's algorithm.'

### Recommendations from Vincent

- If a structural proxy is required, switch to an HHL-shaped template (QPE register + controlled-U evolution block + ancilla rotation + inverse QPE) sized to the n_qubits cap.
- Otherwise reclassify SQ9 as an explicit ansatz_stretch resource-only proxy and update cohort algorithm_family to a generic-ansatz bucket so the family tag, circuit registry tag, and v2 extraction all agree.
- Re-author SQ9-specific instance.json and circuit.py (or alias to SQ10's files intentionally) so label_id/experiment_id metadata match the SQ9/exp_2 target instead of SQ10/exp_1.

---

## DECISION (joint manual review)

```yaml
label_id: SQ9
paper_id: 53a718c11ea8
experiment_id: exp_2
reviewers: [Vincent Wallerich, Aleix Telesforo]
reviewed_utc: 2026-04-25

# winner: 'phase3' | 'vincent' | 'merge' | 'other'
# action:  'accept_vincent' | 'reauthor_circuit' | 'demote_label' | 'relabel_family' | 'no_change'
decision:
  winner: vincent
  action: reauthor_circuit
  rationale: |
    Accept Vincent's DRIFT_MAJOR assessment.

    Phase 3 is faithful to the paper for exp_2. The paper's quantum one-class SVM algorithm is not a generic variational circuit. It defines a kernel matrix over quantum states, solves a one-class SVM linear system, and then proposes an efficient quantum implementation using HHL-style quantum matrix inversion. The paper explicitly states that the quantum matrix inversion algorithm requires phase estimation and controlled operations generated by the kernel matrix. It then explains how to exponentiate the kernel matrix through a density-matrix-exponentiation / quantum-PCA-style construction.

    The implemented circuit described in Vincent's review is a RealAmplitudes ansatz composed with its inverse. This is not family-faithful to the paper's HHL / quantum-linear-system / quantum-kernel algorithm. It has no QPE register, no controlled exp(-iKt) evolution, no eigenvalue inversion rotation, no uncomputed HHL skeleton, no kernel-density-matrix exponentiation, and no modified swap-test proximity measurement. As a compute-uncompute template, it is also structurally trivial for the algorithmic purpose of exp_2.

    The artifact metadata is additionally inconsistent. The pasted review indicates that the circuit and instance are labelled SQ10 / exp_1 and describe the pure-state kernel-PCA variant, while this audit target is SQ9 / exp_2, the quantum one-class SVM variant. This is a wrong-experiment binding, not only a weak proxy.

    Therefore, SQ9 should not be accepted as currently implemented. If SQ9 remains in the cohort, the circuit should be reauthored as an HHL-shaped quantum one-class SVM proxy. If reauthoring is not feasible, SQ9 must be demoted to a theoretical-paper/template-proxy label and excluded from family-faithful resource aggregates.
  evidence_section: >
    PDF page 1, Abstract and Introduction: the paper states that it develops quantum algorithms for anomaly detection using kernel PCA and one-class SVM, with logarithmic resource scaling in the quantum-state dimension and, for pure states, also in the number of training states.
    PDF page 3, Section II.B: the classical one-class SVM formulation is reduced to a kernel linear-system problem involving the matrix K and the coefficients alpha.
    PDF pages 4-5, Section III.B "Quantum one-class SVM (pure state)": the paper defines the quantum kernel matrix K = sum_ij |<psi_i|psi_j>|^2 |i><j| and states that matrix inversion is required before computing the proximity measure.
    PDF page 5, Section III.B.2.a: the paper explicitly converts the SVM system into (K + PT I)|alpha> = |e> and states that the HHL quantum matrix inversion algorithm is used to obtain |alpha>, relying on phase estimation and controlled operations.
    PDF pages 5-6, Sections III.B.2.b and III.B.2.c: the paper describes exponentiating the kernel matrix via a quantum-PCA/density-matrix-exponentiation construction and computing the proximity measure through constructed states |phi_1>, |phi_2> and modified swap-test-style overlap estimation.
    PDF page 6, Figure 1: the displayed circuits for generating |phi_1> and |phi_2> are structurally based on controlled state preparation and overlap estimation, not on a RealAmplitudes variational ansatz.
  remediation:
    template: hhl_proxy
    n_qubits: 5
    notes: |
      Reauthor SQ9 as an HHL-shaped proxy for the quantum one-class SVM experiment.

      Minimum structural proxy:
      - Use a small synthetic Hermitian positive semidefinite kernel matrix K.
      - Add a QPE/eigenvalue register.
      - Implement controlled powers of exp(-iKt), or a mocked controlled-U block with the same accounting structure.
      - Apply inverse-QFT / QPE structure.
      - Add a controlled rotation representing eigenvalue inversion.
      - Uncompute the QPE register.
      - Add a final overlap/proximity-estimation path, preferably a modified swap-test-style ancilla.

      Metadata fixes:
      - Replace SQ10 labels with SQ9 in circuit.py and instance.json, or explicitly document a shared SQ10 proxy alias for SQ8/SQ9/SQ10/SQ11.
      - Correct experiment_id from exp_1 to exp_2 for the SQ9 artifact.
      - Change algorithm_variant_paper from kernel PCA to quantum one-class SVM / HHL quantum matrix inversion.
      - Reconcile algorithm_family tags. The broad cohort tag other-gate-based is acceptable only as a catch-all, but the implementation notes should explicitly identify the method as an HHL / quantum-linear-system / quantum-kernel proxy rather than quantum-svm generic ansatz.

      If this reauthoring is not performed:
      - Mark SQ9 as DRIFT_MAJOR and P-tier/theoretical-paper proxy.
      - Exclude it from family-faithful HHL, quantum-linear-system, quantum-kernel, and anomaly-detection resource aggregates.
```
