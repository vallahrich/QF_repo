# Triage: SX2

**Reviewers (joint):** Vincent Wallerich + Aleix Telesforo  
**Triage date:** 2026-04-25  
**Vincent verdict (first pass):** **DRIFT_MAJOR**

---

## Paper

- **Title:** Demonstration of quantum linear equation solver on the IBM qiskit platform
- **Paper ID:** `7cfdb2957f6c` · **Experiment:** `exp_2` · **Silo:** `other` · **Cohort algorithm family:** `hhl`

**Sources to consult:**
- Paper markdown: [p2_systematic_review/output/processed/7cfdb2957f6c.md](p2_systematic_review/output/processed/7cfdb2957f6c.md)
- Circuit: [p4_experiments/experiments/silos/other/7cfdb2957f6c__exp_2/circuit.py](p4_experiments/experiments/silos/other/7cfdb2957f6c__exp_2/circuit.py)
- Instance: [p4_experiments/experiments/silos/other/7cfdb2957f6c__exp_2/instance.json](p4_experiments/experiments/silos/other/7cfdb2957f6c__exp_2/instance.json)
- Phase 3 LLM extraction (GPT 5.3 / GPT 5.4-mini, P3 s2_quantitative): [p3_thematic_synthesis/s2_quantitative/output/extractions/7cfdb2957f6c.json](p3_thematic_synthesis/s2_quantitative/output/extractions/7cfdb2957f6c.json) (experiment_id `exp_2`)
- Vincent's review: [../vincent/SX2.md](../vincent/SX2.md)

---

## Disagreement

Vincent's review (first pass) flagged this label as **DRIFT_MAJOR** —
i.e. the implemented circuit does not faithfully match what the
Phase 3 LLM extraction (GPT 5.3 / GPT 5.4-mini) recorded the paper's algorithm to be.

**Vincent's verdict summary:** Circuit is a generic RealAmplitudes ansatz compute-uncompute template; the paper implements HHL (QPE + Lookup reciprocal + inverse QPE) on a 4x4 diagonal system, so the proxy does not represent the paper's algorithm class.

## Phase 3 (LLM) extraction — values for this label

**Source:** [p3_thematic_synthesis/s2_quantitative/output/extractions/7cfdb2957f6c.json](p3_thematic_synthesis/s2_quantitative/output/extractions/7cfdb2957f6c.json) (experiment_id `exp_2`)  
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
| Family-faithful | ❌ | Paper algorithm is HHL (QPE-based linear-systems solver). Circuit is a variational RealAmplitudes ansatz with an ansatz-inverse compute-uncompute pair; no QPE, no eigenvalue-reciprocal rotation, no inverse QPE. instance.json explicitly tags algorithm_family='other-gate-based' while the circuit register decorator and cohort tag say 'hhl' — internal inconsistency, and neither matches the paper's HHL structure structurally. |
| Scale-faithful | ✅ | Paper reports 7 qubits for this 4x4 instance (2 state + 3 clock + ancillae). Circuit uses 6 qubits, within a factor of 2 and below the 12-qubit tractability cap. |
| Structurally non-trivial | ❌ | Circuit is structurally a generic variational ansatz (RealAmplitudes, linear entanglement, 3 reps) followed by its inverse. It lacks every distinguishing HHL component: no Hamiltonian-simulation block, no QPE clock register, no controlled-reciprocal rotation on an ancilla, no inverse QPE. Compute-uncompute of a parametrised ansatz with measurement at the end yields a near-trivial bit-string distribution and is not HHL-shaped. |
| Metadata-consistent | ❌ | instance.json algorithm_family='other-gate-based' and label='SX5' / instance_id='SX5_v5_proxy_v1', but cohort label_id is SX2 and circuit register tag is algorithm_family='hhl' with label='SX5'. Notes also state 'covered v2/v3/v4 label corresponds to a DIFFERENT experiment row of the same paper', confirming this row was not authored as a faithful HHL implementation. |

### Concerns raised by Vincent

- Family drift: HHL paper proxied by a generic variational ansatz; no QPE / reciprocal / inverse-QPE structure.
- Label mismatch: cohort label_id=SX2 but instance.json label=SX5 and circuit register label='SX5' (paper-level reuse across SX1-SX4 noted in v2 operator_notes).
- Algorithm-family tag inconsistency between instance.json ('other-gate-based') and circuit @register decorator ('hhl').
- Compute-uncompute of an ansatz with measurement is a near-identity proxy that under-represents HHL's true gate cost (Hamiltonian simulation, controlled rotations) for Phase-8 resource estimation.

### Recommendations from Vincent

- Either (a) replace circuit with a small HHL skeleton at n=6-7 qubits (mock QPE on a 2-qubit state register with 3 clock qubits + 1 reciprocal ancilla), or (b) explicitly down-classify this row as a non-faithful template stretch and exclude it from family-level HHL aggregates.
- Reconcile the SX2 vs SX5 labelling and the algorithm_family tag between instance.json and circuit.py before any Phase-8 reporting that groups by family.

---

## DECISION (joint manual review)

```yaml
label_id: SX2
paper_id: 7cfdb2957f6c
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

    Phase 3 is faithful to the paper for exp_2. The paper demonstrates the HHL algorithm for solving systems of linear equations on IBM Qiskit. For this experiment, the relevant paper-side case is the fourth-order / 4x4 linear-system implementation, where the authors use Qiskit Aqua's HHL algorithm with EigsQPE, three ancillae, Suzuki expansion, time slicing, and a reciprocal Lookup component.

    The paper-side algorithm is therefore explicitly HHL: it requires state preparation for |b>, quantum phase estimation to decompose |b> in the eigenbasis of A, reciprocal/eigenvalue inversion through a controlled rotation or lookup-style reciprocal step, and inverse phase estimation to uncompute the eigenvalue register.

    The implemented circuit described in Vincent's review is a generic RealAmplitudes ansatz followed by its inverse and then measurement. That compute-uncompute proxy is not HHL-shaped. It has no system/eigenvalue/ancilla register structure, no QPE clock register, no controlled Hamiltonian simulation or EigsQPE-style block, no reciprocal Lookup or controlled rotation, and no inverse-QPE uncomputation.

    The mismatch is major because the paper does not merely mention HHL abstractly; it reports an actual Qiskit HHL setup and fourth-order matrix experiments. A generic ansatz proxy would therefore misrepresent the resource profile of the HHL family.

    Scale is acceptable but not sufficient. The paper reports a 7-qubit HHL setting for the fourth-order case, while the proxy uses 6 qubits, which is within factor-of-2 and below the 12-qubit cap. However, the structural HHL components are absent.

    Metadata consistency is also broken. The pasted review indicates that the implementation is labelled SX5 rather than SX2 and that instance.json uses algorithm_family='other-gate-based' while the circuit register declares algorithm_family='hhl'. This must be reconciled before Phase-8 aggregation.
  evidence_section: >
    PDF page 1, Abstract: the paper states that it gives HHL quantum circuits corresponding to 4-qubit and 7-qubit cases and verifies them on IBM Qiskit.
    PDF page 2, Section II "The HHL Algorithm": the paper defines Ax = b and A|x> = |b>, requires A to be square and Hermitian or transformed into Hermitian form, and identifies the core HHL components as phase estimation, controlled rotation, and inverse phase estimation.
    PDF page 2, Figure 1: the paper provides a schematic diagram of the HHL algorithm.
    PDF page 3, Qiskit implementation block: the fourth-order HHL implementation uses Qiskit Aqua with algorithm name 'HHL', EigsQPE, Suzuki expansion, num_ancillae=3, num_time_slices=50, and reciprocal Lookup.
    PDF page 3, fourth-order diagonal-matrix experiment: the paper evaluates HHL on a 4x4 diagonal matrix with b=[1,1,1,1]^T and reports fidelity 0.999353.
    PDF pages 3-4, further fourth-order experiments: the paper evaluates additional 4x4 matrices and reports fidelity values, confirming that exp_2 is an HHL linear-system-solving experiment rather than a variational ansatz experiment.
  remediation:
    template: hhl_proxy
    n_qubits: 7
    notes: |
      Required immediate handling:
      - Mark the current SX2 artifact as DRIFT_MAJOR.
      - Do not treat the current RealAmplitudes compute-uncompute circuit as an HHL implementation.
      - Exclude the current circuit from family-faithful HHL / quantum-linear-system resource aggregates until reauthored.

      Metadata fixes:
      - Replace SX5 labels in circuit.py and instance.json with SX2 if this artifact is intended for SX2.
      - Set experiment_id=exp_2 consistently.
      - Align instance_id, label, register labels, function names, docstrings, and register_accounting labels with SX2.
      - Reconcile algorithm_family between circuit.py and instance.json.
      - If the implementation remains a generic ansatz proxy, set the registered family to other-gate-based or ansatz_proxy rather than hhl.
      - If the family remains hhl, the circuit body must be replaced by an HHL-shaped proxy.

      Recommended HHL remediation:
      - Implement a small HHL skeleton at the paper's 7-qubit scale.
      - Use a 2-qubit system register for the 4x4 linear system.
      - Use a 3-qubit QPE/eigenvalue register, matching the paper's num_ancillae=3 / EigsQPE configuration.
      - Include controlled Hamiltonian-simulation or mocked controlled-U powers for the diagonal 4x4 matrix.
      - Add reciprocal Lookup or controlled reciprocal-rotation logic.
      - Add inverse-QPE uncomputation.
      - Use the paper's diagonal 4x4 example A=diag(2,1,3,2), b=[1,1,1,1]^T as the canonical SX2 toy instance.

      Aggregation guidance:
      - Treat the paper and SX2 label as hhl at the paper level.
      - Treat the current implementation as non-family-faithful until reauthored.
      - Deduplicate SX1-SX4/SX5-style sibling rows in per-paper aggregation unless each row has a distinct, correctly labelled, and structurally faithful circuit.
```
