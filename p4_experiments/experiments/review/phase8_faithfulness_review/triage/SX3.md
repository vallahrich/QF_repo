# Triage: SX3

**Reviewers (joint):** Vincent Wallerich + Aleix Telesforo  
**Triage date:** 2026-04-25  
**Vincent verdict (first pass):** **DRIFT_MAJOR**

---

## Paper

- **Title:** Demonstration of quantum linear equation solver on the IBM qiskit platform
- **Paper ID:** `7cfdb2957f6c` · **Experiment:** `exp_3` · **Silo:** `other` · **Cohort algorithm family:** `hhl`

**Sources to consult:**
- Paper markdown: [p2_systematic_review/output/processed/7cfdb2957f6c.md](p2_systematic_review/output/processed/7cfdb2957f6c.md)
- Circuit: [p4_experiments/experiments/silos/other/7cfdb2957f6c/circuit.py](p4_experiments/experiments/silos/other/7cfdb2957f6c/circuit.py)
- Instance: [p4_experiments/experiments/silos/other/7cfdb2957f6c/instance.json](p4_experiments/experiments/silos/other/7cfdb2957f6c/instance.json)
- Phase 3 LLM extraction (GPT 5.3 / GPT 5.4-mini, P3 s2_quantitative): [p3_thematic_synthesis/s2_quantitative/output/extractions/7cfdb2957f6c.json](p3_thematic_synthesis/s2_quantitative/output/extractions/7cfdb2957f6c.json) (experiment_id `exp_3`)
- Vincent's review: [../vincent/SX3.md](../vincent/SX3.md)

---

## Disagreement

Vincent's review (first pass) flagged this label as **DRIFT_MAJOR** —
i.e. the implemented circuit does not faithfully match what the
Phase 3 LLM extraction (GPT 5.3 / GPT 5.4-mini) recorded the paper's algorithm to be.

**Vincent's verdict summary:** Circuit is a generic RealAmplitudes ansatz compute-uncompute proxy with no QPE/controlled-reciprocal/inverse-QPE structure, so it does not represent the paper's HHL algorithm class; instance.json metadata is also for a different label (SX4/exp_1).

## Phase 3 (LLM) extraction — values for this label

**Source:** [p3_thematic_synthesis/s2_quantitative/output/extractions/7cfdb2957f6c.json](p3_thematic_synthesis/s2_quantitative/output/extractions/7cfdb2957f6c.json) (experiment_id `exp_3`)  
**Models used (per source `extraction_metadata.models_used`):** `gpt-5.3` (synthesis) + `gpt-5.4-mini` (extraction steps).

| Field | Phase 3 value |
|---|---|
| `algorithm_family` | `hhl` |
| `algorithm_variant` | `HHL algorithm for solving linear equations` |
| `num_qubits` | `7` |
| `ansatz` (free-text) | _(not extracted in P3 S2)_ |
| `num_layers` | _(not extracted in P3 S2)_ |
| `circuit_depth` | _(not extracted in P3 S2)_ |
| `oracle_structure` | _(not extracted in P3 S2)_ |
| `encoding` | _(not extracted in P3 S2)_ |

_Note: P3 s2_quantitative extracts paper-level algorithm and quantum-resource fields. Circuit-level details that are not in the S2 schema (e.g. `oracle_structure`, `encoding`) appear as _(not extracted in P3 S2)_ above. Vincent's per-check notes below adjudicate those fields from direct paper + circuit reading._

### Vincent's per-check notes

| Check | Result | Note |
|---|---|---|
| Family-faithful | ❌ | Paper algorithm family is HHL (QPE + Lookup reciprocal + inverse QPE). The circuit uses a generic variational RealAmplitudes ansatz (template proxy) with no HHL-specific structure; @register tag says 'hhl' but the implementation is not in the HHL family. |
| Scale-faithful | ✅ | Paper reports 7 qubits for the full HHL register (2 state-prep + 3 clock + 3 ancilla per v2; 4 system-side for the 4x4 instance). Circuit uses 4 qubits, within a factor of 2 of the paper's 7-qubit count and matching the 4x4 system size. |
| Structurally non-trivial | ❌ | Full circuit is just RealAmplitudes . RealAmplitudes^dagger (compute-uncompute), which approximates the identity and contains none of the HHL building blocks (no QPE/Hamiltonian simulation, no controlled rotation implementing 1/lambda, no inverse QPE). Not structurally representative of HHL. |
| Metadata-consistent | ❌ | instance.json has label='SX4', experiment_id='exp_1', algorithm_family='other-gate-based', and notes='paper algorithm not implemented'. Task is SX3/exp_3 with cohort algorithm_family='hhl'. The @register decorator tags the circuit as label='SX4' algorithm_family='hhl', so label_id, experiment_id, and family tags disagree across cohort, instance, and circuit. |

### Concerns raised by Vincent

- Generic ansatz proxy does not implement HHL (no QPE, no controlled reciprocal, no inverse QPE).
- instance.json is labelled SX4/exp_1 but is being used for SX3/exp_3.
- circuit.py @register uses label='SX4' while the cohort entry is SX3.
- instance.json algorithm_family='other-gate-based' contradicts cohort/registry algorithm_family='hhl'.
- Compute-uncompute pair approximates the identity, providing no algorithmically meaningful proxy oracle for HHL cost estimation.

### Recommendations from Vincent

- Re-author the SX3 instance.json and circuit.py with correct label_id='SX3' and experiment_id='exp_3'.
- Either implement an HHL-shaped proxy (QPE + controlled rotation + inverse QPE) at small scale, or downgrade cohort algorithm_family to reflect that the implementation is a generic ansatz.
- Reconcile algorithm_family tags across cohort, instance.json, and the @register decorator.

---

## DECISION (joint manual review)

```yaml
label_id: SX3
paper_id: 7cfdb2957f6c
experiment_id: exp_3
reviewers: [Vincent Wallerich, Aleix Telesforo]
reviewed_utc: 2026-04-25

# winner: 'phase3' | 'vincent' | 'merge' | 'other'
# action:  'accept_vincent' | 'reauthor_circuit' | 'demote_label' | 'relabel_family' | 'no_change'
decision:
  winner: vincent
  action: reauthor_circuit
  rationale: |
    Accept Vincent's DRIFT_MAJOR assessment.

    Phase 3 is faithful to the paper for exp_3. The paper demonstrates the HHL algorithm for solving systems of linear equations on IBM Qiskit. The relevant experiment belongs to the fourth-order / 4x4 HHL test set, where the paper evaluates HHL on different 4x4 matrices and reports fidelity outcomes.

    The paper-side algorithm is explicitly HHL: it requires state preparation for |b>, quantum phase estimation to decompose |b> in the eigenbasis of A, reciprocal/eigenvalue inversion through a controlled rotation or lookup-style reciprocal step, and inverse phase estimation to uncompute the eigenvalue register.

    The implemented circuit described in Vincent's review is a generic RealAmplitudes ansatz followed by its inverse and then measurement. That compute-uncompute proxy is not HHL-shaped. It has no system/eigenvalue/ancilla register separation, no QPE clock register, no controlled Hamiltonian simulation or EigsQPE-style block, no reciprocal Lookup or controlled rotation, and no inverse-QPE uncomputation.

    The mismatch is major because the paper provides an actual HHL demonstration and circuit-level structure. A generic variational ansatz proxy cannot be counted as a family-faithful implementation of the HHL algorithm.

    Scale is acceptable but not sufficient. The paper reports a 7-qubit HHL setting for the fourth-order experiments, while the proxy uses 4 qubits, which is within factor-of-2 and below the 12-qubit tractability cap. However, the structural HHL components are absent.

    Metadata consistency is also broken. The pasted review indicates that instance.json and circuit.py identify the artifact as SX4 / exp_1, while this audit item is SX3 / exp_3. The instance family also reportedly says other-gate-based while the cohort and registry say hhl. This must be reconciled before Phase-8 aggregation.
  evidence_section: >
    PDF page 1, Abstract: the paper states that it gives HHL quantum circuits corresponding to 4-qubit and 7-qubit cases and verifies them on IBM Qiskit.
    PDF page 2, Section II "The HHL Algorithm": the paper defines Ax = b and A|x> = |b>, requires A to be square and Hermitian or transformed into Hermitian form, and identifies the core HHL components as phase estimation, controlled rotation, and inverse phase estimation.
    PDF page 2, Figure 1: the paper provides a schematic diagram of the HHL algorithm.
    PDF page 3, Figure 2: the paper shows the quantum circuit diagram of the HHL algorithm for the second-order case, illustrating that the paper is circuit-level HHL rather than a generic ansatz study.
    PDF page 3, Qiskit implementation block: the fourth-order HHL implementation uses Qiskit Aqua with algorithm name 'HHL', EigsQPE, Suzuki expansion, num_ancillae=3, num_time_slices=50, and reciprocal Lookup.
    PDF pages 3-4, fourth-order experiments: the paper evaluates HHL on multiple 4x4 matrices, including a strongly sparse non-diagonal matrix and a less sparse real symmetric matrix, and reports fidelity values for the HHL results.
  remediation:
    template: hhl_proxy
    n_qubits: 7
    notes: |
      Required immediate handling:
      - Mark the current SX3 artifact as DRIFT_MAJOR.
      - Do not treat the current RealAmplitudes compute-uncompute circuit as an HHL implementation.
      - Exclude the current circuit from family-faithful HHL / quantum-linear-system resource aggregates until reauthored.

      Metadata fixes:
      - Replace SX4 labels in circuit.py and instance.json with SX3 if this artifact is intended for SX3.
      - Set experiment_id=exp_3 consistently.
      - Align instance_id, label, register labels, function names, docstrings, and register_accounting labels with SX3.
      - Reconcile algorithm_family between circuit.py and instance.json.
      - If the implementation remains a generic ansatz proxy, set the registered family to other-gate-based or ansatz_proxy rather than hhl.
      - If the family remains hhl, the circuit body must be replaced by an HHL-shaped proxy.

      Recommended HHL remediation:
      - Implement a small HHL skeleton at the paper's 7-qubit scale.
      - Use a 2-qubit system register for the 4x4 linear system.
      - Use a 3-qubit QPE/eigenvalue register, matching the paper's EigsQPE / num_ancillae=3 setting.
      - Include controlled Hamiltonian-simulation or mocked controlled-U powers for a 4x4 Hermitian matrix.
      - Add reciprocal Lookup or controlled reciprocal-rotation logic.
      - Add inverse-QPE uncomputation.
      - Use one of the paper's 4x4 examples as the canonical SX3 toy instance, preferably the sparse non-diagonal matrix if exp_3 corresponds to that row.

      Aggregation guidance:
      - Treat the paper and SX3 label as hhl at the paper level.
      - Treat the current implementation as non-family-faithful until reauthored.
      - Deduplicate SX1-SX4/SX5-style sibling rows in per-paper aggregation unless each row has a distinct, correctly labelled, and structurally faithful circuit.
```
