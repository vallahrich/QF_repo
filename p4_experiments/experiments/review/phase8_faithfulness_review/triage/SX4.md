# Triage: SX4

**Reviewers (joint):** Vincent Wallerich + Aleix Telesforo  
**Triage date:** 2026-04-25  
**Vincent verdict (first pass):** **DRIFT_MAJOR**

---

## Paper

- **Title:** Demonstration of quantum linear equation solver on the IBM qiskit platform
- **Paper ID:** `7cfdb2957f6c` · **Experiment:** `exp_4` · **Silo:** `other` · **Cohort algorithm family:** `hhl`

**Sources to consult:**
- Paper markdown: [p2_systematic_review/output/processed/7cfdb2957f6c.md](p2_systematic_review/output/processed/7cfdb2957f6c.md)
- Circuit: [p4_experiments/experiments/silos/other/7cfdb2957f6c/circuit.py](p4_experiments/experiments/silos/other/7cfdb2957f6c/circuit.py)
- Instance: [p4_experiments/experiments/silos/other/7cfdb2957f6c/instance.json](p4_experiments/experiments/silos/other/7cfdb2957f6c/instance.json)
- Phase 3 LLM extraction (GPT 5.3 / GPT 5.4-mini, P3 s2_quantitative): [p3_thematic_synthesis/s2_quantitative/output/extractions/7cfdb2957f6c.json](p3_thematic_synthesis/s2_quantitative/output/extractions/7cfdb2957f6c.json) (experiment_id `exp_4`)
- Vincent's review: [../vincent/SX4.md](../vincent/SX4.md)

---

## Disagreement

Vincent's review (first pass) flagged this label as **DRIFT_MAJOR** —
i.e. the implemented circuit does not faithfully match what the
Phase 3 LLM extraction (GPT 5.3 / GPT 5.4-mini) recorded the paper's algorithm to be.

**Vincent's verdict summary:** Circuit is a generic RealAmplitudes ansatz compute-uncompute proxy with no QPE/controlled-rotation/inverse-QPE structure, so it does not represent the HHL algorithm class the paper implements.

## Phase 3 (LLM) extraction — values for this label

**Source:** [p3_thematic_synthesis/s2_quantitative/output/extractions/7cfdb2957f6c.json](p3_thematic_synthesis/s2_quantitative/output/extractions/7cfdb2957f6c.json) (experiment_id `exp_4`)  
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
| Family-faithful | ❌ | Cohort/registry tag is hhl, but the implementation is a variational ansatz stretch (instance.json algorithm_family='other-gate-based', task='generic variational ansatz stretch (template proxy)'). Variational ansatz is not in the HHL family. |
| Scale-faithful | ✅ | Paper system register is 4 qubits for the 4x4 dense symmetric case (plus 3 clock + 3 ancillae); circuit uses n_qubits=4, matching the system-register scale within the factor-of-2 / cap-12 rule. |
| Structurally non-trivial | ❌ | HHL requires QPE (Suzuki Hamiltonian simulation) + controlled reciprocal rotation (Lookup) + inverse QPE. The circuit contains only a RealAmplitudes ansatz and its inverse with measurement; no QPE shape, no controlled rotations on an ancilla register, no inverse-QPE uncomputation. |
| Metadata-consistent | ❌ | Inconsistencies: instance.json experiment_id='exp_1' but cohort/prompt experiment_id='exp_4'; instance.json algorithm_family='other-gate-based' while @register declares algorithm_family='hhl'; description string says 'generic variational ansatz stretch' which contradicts the hhl family tag. |

### Concerns raised by Vincent

- Implementation is explicitly a template proxy that does not implement HHL (state_prep, QPE, controlled rotation, inverse QPE all absent).
- algorithm_family mismatch between registry decorator ('hhl') and instance.json ('other-gate-based').
- experiment_id mismatch: instance.json says exp_1 but this cohort entry is exp_4 (4x4 dense symmetric matrix).
- Resource estimates from this circuit will reflect a RealAmplitudes ansatz, not an HHL circuit, so Phase-8 cost extrapolation for the HHL family will be biased downward.

### Recommendations from Vincent

- Either (a) replace circuit with an HHL-shaped proxy (QPE block + controlled rotation on ancilla + inverse QPE) sized to 4 system + 3 clock + 1 ancilla qubits, or (b) reclassify SX4 cohort algorithm_family to 'other-gate-based / variational-proxy' and document that HHL family resource estimates are not derived from SX1-SX4.
- Fix instance.json experiment_id from 'exp_1' to 'exp_4' and align algorithm_family with the registry decorator.
- Note in cohort that SX1-SX4 are flagged redundant in v2 extraction; consolidate or explicitly differentiate the four matrix instances.

---

## DECISION (joint manual review)

```yaml
label_id: SX4
paper_id: 7cfdb2957f6c
experiment_id: exp_4
reviewers: [Vincent Wallerich, Aleix Telesforo]
reviewed_utc: 2026-04-25

# winner: 'phase3' | 'vincent' | 'merge' | 'other'
# action:  'accept_vincent' | 'reauthor_circuit' | 'demote_label' | 'relabel_family' | 'no_change'
decision:
  winner: vincent
  action: reauthor_circuit
  rationale: |
    Accept Vincent's DRIFT_MAJOR assessment.

    Phase 3 is faithful to the paper for exp_4. The paper demonstrates the HHL algorithm for solving systems of linear equations on IBM Qiskit. For this experiment, the relevant paper-side case is the fourth-order / 4x4 dense real symmetric matrix example, where the paper reports substantially lower fidelity than for the diagonal and sparse cases.

    The paper-side algorithm is explicitly HHL: it requires state preparation for |b>, quantum phase estimation to decompose |b> in the eigenbasis of A, reciprocal/eigenvalue inversion through a controlled rotation or lookup-style reciprocal step, and inverse phase estimation to uncompute the eigenvalue register.

    The implemented circuit described in Vincent's review is a generic RealAmplitudes ansatz followed by its inverse and then measurement. That compute-uncompute proxy is not HHL-shaped. It has no system/eigenvalue/ancilla register separation, no QPE clock register, no controlled Hamiltonian simulation or EigsQPE-style block, no reciprocal Lookup or controlled rotation, and no inverse-QPE uncomputation.

    The mismatch is major because the paper provides an actual HHL demonstration and reports concrete Qiskit HHL settings. A generic variational ansatz proxy cannot be counted as a family-faithful implementation of the HHL algorithm.

    Scale is acceptable but not sufficient. The paper reports a 7-qubit HHL setting for the fourth-order experiments, while the proxy uses 4 qubits, matching the system-register scale and remaining within the factor-of-2 / 12-qubit cap rule. However, the structural HHL components are absent.

    Metadata consistency is also broken. The pasted review indicates that instance.json uses experiment_id='exp_1' while this audit item is SX4 / exp_4, and that instance.json uses algorithm_family='other-gate-based' while the circuit registry declares algorithm_family='hhl'. This must be reconciled before Phase-8 aggregation.
  evidence_section: >
    PDF page 1, Abstract: the paper states that it gives HHL quantum circuits corresponding to 4-qubit and 7-qubit cases and verifies them on IBM Qiskit.
    PDF page 2, Section II "The HHL Algorithm": the paper defines Ax = b and A|x> = |b>, requires A to be square and Hermitian or transformed into Hermitian form, and identifies the core HHL components as phase estimation, controlled rotation, and inverse phase estimation.
    PDF page 2, Figure 1: the paper provides a schematic diagram of the HHL algorithm.
    PDF page 3, Qiskit implementation block: the fourth-order HHL implementation uses Qiskit Aqua with algorithm name 'HHL', EigsQPE, Suzuki expansion, num_ancillae=3, num_time_slices=50, and reciprocal Lookup.
    PDF page 4, dense real symmetric 4x4 experiment: the paper evaluates A=[[3,2,1,0],[2,6,4,3],[1,4,2,5],[0,3,5,4]] with b=[1,0,0,1]^T and reports fidelity 0.653278, identifying this as the weakest fourth-order HHL case.
    PDF page 4, Conclusion: the paper concludes that HHL performs well for sparse linear systems but degrades for weakly sparse / dense matrices, confirming that exp_4 is still an HHL linear-system experiment rather than a variational ansatz experiment.
  remediation:
    template: hhl_proxy
    n_qubits: 7
    notes: |
      Required immediate handling:
      - Mark the current SX4 artifact as DRIFT_MAJOR.
      - Do not treat the current RealAmplitudes compute-uncompute circuit as an HHL implementation.
      - Exclude the current circuit from family-faithful HHL / quantum-linear-system resource aggregates until reauthored.

      Metadata fixes:
      - Set experiment_id=exp_4 consistently in instance.json and circuit metadata.
      - Align instance_id, label, register labels, function names, docstrings, and register_accounting labels with SX4.
      - Reconcile algorithm_family between circuit.py and instance.json.
      - If the implementation remains a generic ansatz proxy, set the registered family to other-gate-based or ansatz_proxy rather than hhl.
      - If the family remains hhl, the circuit body must be replaced by an HHL-shaped proxy.

      Recommended HHL remediation:
      - Implement a small HHL skeleton at the paper's 7-qubit scale.
      - Use a 2-qubit system register for the 4x4 linear system.
      - Use a 3-qubit QPE/eigenvalue register, matching the paper's EigsQPE / num_ancillae=3 setting.
      - Include controlled Hamiltonian-simulation or mocked controlled-U powers for the dense 4x4 Hermitian matrix.
      - Add reciprocal Lookup or controlled reciprocal-rotation logic.
      - Add inverse-QPE uncomputation.
      - Use the paper's dense symmetric 4x4 example A=[[3,2,1,0],[2,6,4,3],[1,4,2,5],[0,3,5,4]], b=[1,0,0,1]^T as the canonical SX4 toy instance.

      Aggregation guidance:
      - Treat the paper and SX4 label as hhl at the paper level.
      - Treat the current implementation as non-family-faithful until reauthored.
      - Deduplicate SX1-SX4/SX5-style sibling rows in per-paper aggregation unless each row has a distinct, correctly labelled, and structurally faithful circuit.
```
