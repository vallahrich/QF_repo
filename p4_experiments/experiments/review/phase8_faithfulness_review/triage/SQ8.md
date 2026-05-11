# Triage: SQ8

**Reviewers (joint):** Vincent Wallerich + Aleix Telesforo  
**Triage date:** 2026-04-25  
**Vincent verdict (first pass):** **DRIFT_MAJOR**

---

## Paper

- **Title:** Quantum machine learning for quantum anomaly detection
- **Paper ID:** `53a718c11ea8` · **Experiment:** `exp_1` · **Silo:** `quantum-ml-finance` · **Cohort algorithm family:** `other-gate-based`

**Sources to consult:**
- Paper markdown: [p2_systematic_review/output/processed/53a718c11ea8.md](p2_systematic_review/output/processed/53a718c11ea8.md)
- Circuit: [p4_experiments/experiments/silos/quantum_ml_finance/53a718c11ea8/circuit.py](p4_experiments/experiments/silos/quantum_ml_finance/53a718c11ea8/circuit.py)
- Instance: [p4_experiments/experiments/silos/quantum_ml_finance/53a718c11ea8/instance.json](p4_experiments/experiments/silos/quantum_ml_finance/53a718c11ea8/instance.json)
- Phase 3 LLM extraction (GPT 5.3 / GPT 5.4-mini, P3 s2_quantitative): [p3_thematic_synthesis/s2_quantitative/output/extractions/53a718c11ea8.json](p3_thematic_synthesis/s2_quantitative/output/extractions/53a718c11ea8.json) (experiment_id `exp_1`)
- Vincent's review: [../vincent/SQ8.md](../vincent/SQ8.md)

---

## Disagreement

Vincent's review (first pass) flagged this label as **DRIFT_MAJOR** —
i.e. the implemented circuit does not faithfully match what the
Phase 3 LLM extraction (GPT 5.3 / GPT 5.4-mini) recorded the paper's algorithm to be.

**Vincent's verdict summary:** Generic RealAmplitudes ansatz compute-uncompute proxy does not represent the paper's HHL/QPE/density-matrix-exponentiation algorithm class for quantum kernel PCA / one-class SVM anomaly detection.

## Phase 3 (LLM) extraction — values for this label

**Source:** [p3_thematic_synthesis/s2_quantitative/output/extractions/53a718c11ea8.json](p3_thematic_synthesis/s2_quantitative/output/extractions/53a718c11ea8.json) (experiment_id `exp_1`)  
**Models used (per source `extraction_metadata.models_used`):** `gpt-5.3` (synthesis) + `gpt-5.4-mini` (extraction steps).

| Field | Phase 3 value |
|---|---|
| `algorithm_family` | `other-gate-based` |
| `algorithm_variant` | `quantum kernel PCA for pure-state anomaly detection` |
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
| Family-faithful | ❌ | Paper's algorithm is HHL-style quantum linear-system inversion with density-matrix exponentiation of a quantum kernel and swap-test proximity estimation (oracle_structure=block_encoded_QSP, measurement=QPE in v2). Cohort bucket 'other-gate-based' is a catch-all, but the implemented circuit is a variational RealAmplitudes ansatz, which belongs to the VQE/ansatz family, not the QPE/HHL/quantum-kernel family the paper specifies. Circuit metadata further labels algorithm_family='quantum-svm', which is yet a third bucket and inconsistent with cohort and v2. |
| Scale-faithful | ✅ | Paper does not state a qubit count (NOT_STATED in v2 — pure-theory paper). Implemented n_qubits=5 is within the standard 12-qubit tractability cap and is a defensible default scale. |
| Structurally non-trivial | ❌ | Paper-class structure would include density-matrix exponentiation of the kernel, QPE-shaped HHL inversion, and modified swap tests. Implemented circuit is RealAmplitudes(reps=3, linear entanglement) followed by its inverse and a computational-basis measurement — no QPE register, no controlled-rotation/inverse-QPE HHL skeleton, no swap test, no ancilla-based overlap test. The compute-uncompute pair is structurally trivial (returns to |0..0> up to noise) and bears no resemblance to the paper's algorithm structure. |
| Metadata-consistent | ❌ | circuit.py module docstring, register(label=...), register_accounting(label=...), instance.label, and instance.instance_id all say 'SQ10', but this audit target is SQ8. The four labels SQ8/SQ9/SQ10/SQ11 share paper 53a718c11ea8 (per v2 operator_notes), so reuse of one proxy across labels appears intentional, but the SQ8 cohort entry points at a circuit whose own metadata identifies it as SQ10. Additionally, register(algorithm_family='quantum-svm') disagrees with cohort.algorithm_family='other-gate-based'. |

### Concerns raised by Vincent

- Circuit implements a generic variational ansatz, not the paper's HHL + density-matrix-exponentiation + swap-test pipeline; resource estimates derived from this proxy will not reflect the paper's claimed costs.
- Compute-uncompute (U then U^dagger) on |0..0> with no intervening operation is structurally trivial and produces no algorithmic content; it is not a meaningful proxy oracle for a kernel-PCA / one-class-SVM anomaly detector.
- Single shared proxy used across SQ8/SQ9/SQ10/SQ11 (all from arXiv:1710.07405) — fine in principle, but circuit/instance metadata is hard-coded to 'SQ10', not parameterised per label.
- register(algorithm_family='quantum-svm') is inconsistent with cohort.algorithm_family='other-gate-based' for SQ8.
- Paper is pure theory with no stated qubit count, depth, or gate counts (v2 fidelity_assessment='P'); any small-scale proxy is necessarily a stretch, which strengthens (not weakens) the need to flag the family/structural mismatch.

### Recommendations from Vincent

- Flag SQ8 (and the SQ9/SQ10/SQ11 siblings sharing this paper) as theoretical-paper proxies in the cohort, so downstream Phase-8 resource projections are not interpreted as faithful to the paper's HHL claims.
- If a more faithful proxy is desired, replace compute-uncompute with at minimum a QPE-shaped skeleton (QPE register + controlled-U powers + inverse QFT) over a small synthetic Hermitian K to mimic the HHL inversion stage, plus a final swap-test-style ancilla measurement.
- Reconcile circuit/instance metadata: either parameterise label/instance_id per cohort entry, or document explicitly in the cohort that SQ8/SQ9/SQ10/SQ11 share one circuit file labelled 'SQ10'.
- Reconcile algorithm_family tags: cohort says 'other-gate-based', register decorator says 'quantum-svm'; pick one and apply consistently.

---

## DECISION (joint manual review)

```yaml
label_id: SQ8
paper_id: 53a718c11ea8
experiment_id: exp_1
reviewers: [Vincent Wallerich, Aleix Telesforo]
reviewed_utc: 2026-04-25

# winner: 'phase3' | 'vincent' | 'merge' | 'other'
# action:  'accept_vincent' | 'reauthor_circuit' | 'demote_label' | 'relabel_family' | 'no_change'
decision:
  winner: merge
  action: demote_label
  rationale: |
    Accept Vincent's DRIFT_MAJOR assessment, with a correction to the algorithm-specific wording.

    Phase 3 is faithful to the paper for exp_1: the relevant paper-side algorithm is quantum kernel PCA for pure-state anomaly detection. The paper proposes quantum anomaly-detection algorithms based on kernel PCA and one-class SVM, but SQ8 / exp_1 corresponds to the pure-state kernel-PCA branch. That branch defines centroid and centered quantum states, constructs a covariance/density-matrix representation from the centered training states, and computes the anomaly proximity measure through inner-product estimation using modified swap tests or a standard swap test on the centered-data density matrix.

    The relevant SQ8 structure is therefore a quantum-kernel / kernel-PCA / swap-test-style proximity-estimation pipeline, not an HHL/QPE quantum linear-system pipeline. HHL, QPE, controlled kernel evolution, and eigenvalue inversion belong to the pure-state one-class SVM branch, i.e. SQ9 / exp_2, not SQ8 / exp_1.

    The implemented circuit described in Vincent's review is a generic RealAmplitudes ansatz followed by its inverse and then computational-basis measurement. That is a variational ansatz-stretch / compute-uncompute proxy. It lacks the defining structures of the SQ8 paper branch: no training-state superposition, no centroid or centered-state preparation, no covariance/density-matrix construction, no swap-test or modified-swap-test ancilla, and no kernel-PCA proximity-measure computation.

    The current proxy is therefore not family-faithful and not structurally faithful. The broad cohort bucket ('other-gate-based') does not repair the mismatch, because the operative SQ8 algorithm is a quantum kernel-PCA anomaly-detection method, not an ansatz-based variational circuit.

    Metadata consistency is also broken. The pasted review indicates that circuit.py and instance.json are hard-coded as SQ10 while this audit item is SQ8. Because SQ8/SQ9/SQ10/SQ11 share the same paper, a shared proxy may be acceptable only if the mapping is explicit and parameterized; otherwise the current artifact is cross-label contaminated.

    Therefore SQ8 should be demoted to theoretical-paper/template-proxy status and excluded from family-faithful quantum-kernel / kernel-PCA / anomaly-detection resource aggregates unless the circuit is reauthored.
  evidence_section: >
    PDF page 1, Abstract and Introduction: the paper states that it develops quantum algorithms for anomaly detection in quantum states using kernel PCA and one-class SVM, with resources logarithmic in the quantum-state dimension and, for pure states, logarithmic in the number of training states.
    PDF pages 3-4, Section III.A "Quantum kernel PCA (pure state)": the pure-state quantum kernel-PCA algorithm defines centroid and centered quantum states, constructs a covariance/density-matrix representation, and computes the anomaly proximity measure using inner products and modified swap tests.
    PDF page 4, Section III.A.2: the paper gives an alternative protocol for pure-state kernel PCA using a superposition of centered data and a standard swap test to estimate the proximity measure from the centered-data density matrix.
    PDF pages 4-6, Section III.B: the paper separately describes the quantum one-class SVM branch, including HHL-style quantum matrix inversion, kernel-matrix exponentiation, and overlap estimation. This supports keeping HHL/QPE language for SQ9, not SQ8.
    PDF pages 6-7, Section IV and Discussion: the mixed-state extensions continue to rely on kernel/fidelity measures, swap-test-style procedures, and proximity estimation, reinforcing that these anomaly-detection methods are not variational-ansatz templates.
  remediation:
    template: swap_test_kernel_proxy
    n_qubits: 5
    notes: |
      Recommended immediate handling:
      - Mark SQ8 as DRIFT_MAJOR and P-tier/theoretical-paper proxy.
      - Exclude the current RealAmplitudes compute-uncompute circuit from family-faithful quantum-kernel, kernel-PCA, or anomaly-detection resource aggregates.
      - Keep paper_id=53a718c11ea8 and experiment_id=exp_1, but do not treat the current circuit as an implementation of the paper's algorithm.

      Metadata fixes:
      - Replace hard-coded SQ10 labels in circuit.py and instance.json with SQ8, or explicitly document SQ10 as a shared proxy alias for SQ8/SQ9/SQ10/SQ11.
      - Align instance_id, label, register labels, function names, docstrings, and register_accounting labels with SQ8 if this remains a separate cohort row.
      - Reconcile algorithm_family tags: either consistently use other-gate-based as the broad cohort bucket, or introduce a more specific quantum-kernel / kernel-PCA / quantum-ml-anomaly category if available.

      Recommended reauthoring if a stronger proxy is needed:
      - Replace the RealAmplitudes compute-uncompute circuit with a small pure-state quantum-kernel-PCA proxy.
      - Include a training-state/index register and a system register for small synthetic training states.
      - Add a centroid or centered-state preparation proxy, or explicitly account for this as a state-preparation block.
      - Include a swap-test or modified-swap-test ancilla to estimate the required overlaps between centered states and the test state.
      - Use the overlap-estimation path as the accounting proxy for the kernel-PCA proximity measure.
      - Do not use an HHL/QPE-shaped template for SQ8; reserve that for SQ9 / exp_2, the pure-state one-class SVM branch.
      - n_qubits=5 may remain acceptable as a tractable proxy because the paper does not state a concrete qubit count, but the structural template must change.
```
