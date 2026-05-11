# Triage: SX1

**Reviewers (joint):** Vincent Wallerich + Aleix Telesforo  
**Triage date:** 2026-04-25  
**Vincent verdict (first pass):** **DRIFT_MAJOR**

---

## Paper

- **Title:** Demonstration of quantum linear equation solver on the IBM qiskit platform
- **Paper ID:** `7cfdb2957f6c` · **Experiment:** `exp_1` · **Silo:** `other` · **Cohort algorithm family:** `hhl`

**Sources to consult:**
- Paper markdown: [p2_systematic_review/output/processed/7cfdb2957f6c.md](p2_systematic_review/output/processed/7cfdb2957f6c.md)
- Circuit: [p4_experiments/experiments/silos/other/7cfdb2957f6c/circuit.py](p4_experiments/experiments/silos/other/7cfdb2957f6c/circuit.py)
- Instance: [p4_experiments/experiments/silos/other/7cfdb2957f6c/instance.json](p4_experiments/experiments/silos/other/7cfdb2957f6c/instance.json)
- Phase 3 LLM extraction (GPT 5.3 / GPT 5.4-mini, P3 s2_quantitative): [p3_thematic_synthesis/s2_quantitative/output/extractions/7cfdb2957f6c.json](p3_thematic_synthesis/s2_quantitative/output/extractions/7cfdb2957f6c.json) (experiment_id `exp_1`)
- Vincent's review: [../vincent/SX1.md](../vincent/SX1.md)

---

## Disagreement

Vincent's review (first pass) flagged this label as **DRIFT_MAJOR** —
i.e. the implemented circuit does not faithfully match what the
Phase 3 LLM extraction (GPT 5.3 / GPT 5.4-mini) recorded the paper's algorithm to be.

**Vincent's verdict summary:** Paper implements HHL (QPE + controlled reciprocal rotation + inverse QPE on Qiskit Aqua), but circuit.py is a generic RealAmplitudes ansatz compute-uncompute template proxy with no QPE structure; explicitly self-flagged as not implementing the paper's algorithm.

## Phase 3 (LLM) extraction — values for this label

**Source:** [p3_thematic_synthesis/s2_quantitative/output/extractions/7cfdb2957f6c.json](p3_thematic_synthesis/s2_quantitative/output/extractions/7cfdb2957f6c.json) (experiment_id `exp_1`)  
**Models used (per source `extraction_metadata.models_used`):** `gpt-5.3` (synthesis) + `gpt-5.4-mini` (extraction steps).

| Field | Phase 3 value |
|---|---|
| `algorithm_family` | `hhl` |
| `algorithm_variant` | `HHL algorithm for solving linear equations` |
| `num_qubits` | `4` |
| `ansatz` (free-text) | _(not extracted in P3 S2)_ |
| `num_layers` | _(not extracted in P3 S2)_ |
| `circuit_depth` | _(not extracted in P3 S2)_ |
| `oracle_structure` | _(not extracted in P3 S2)_ |
| `encoding` | _(not extracted in P3 S2)_ |

_Note: P3 s2_quantitative extracts paper-level algorithm and quantum-resource fields. Circuit-level details that are not in the S2 schema (e.g. `oracle_structure`, `encoding`) appear as _(not extracted in P3 S2)_ above. Vincent's per-check notes below adjudicate those fields from direct paper + circuit reading._

### Vincent's per-check notes

| Check | Result | Note |
|---|---|---|
| Family-faithful | ❌ | Cohort/@register tag declares algorithm_family='hhl' matching the paper, but the actual gates are a generic variational ansatz, not an HHL circuit. Family tag is aspirational rather than realised. |
| Scale-faithful | ✅ | Paper 2x2 case uses 1 system + 3 clock + 3 ancillae ~= 7 qubits; circuit uses 4 qubits. Within factor of 2 and under the 12-qubit cap. |
| Structurally non-trivial | ❌ | An HHL proxy must exhibit QPE-shaped structure (Hamiltonian simulation of e^{-iAt}, QFT/inverse-QFT on a clock register, controlled reciprocal rotation on an ancilla). The circuit contains only RealAmplitudes followed by its inverse and a measurement; no QPE, no controlled rotation, no clock register. |
| Metadata-consistent | ❌ | @register declares algorithm_family='hhl' but instance.json declares algorithm_family='other-gate-based' and notes 'does NOT implement the paper's algorithm'. Inconsistent family labels across registry and instance. |

### Concerns raised by Vincent

- Circuit is a generic variational ansatz proxy, not an HHL implementation; no QPE / controlled-rotation / inverse-QPE structure.
- Metadata mismatch: registry algorithm_family='hhl' vs instance.json algorithm_family='other-gate-based'.
- Instance label inside instance.json is 'SX4' (instance_id 'SX4_v3_proxy_v1', label 'SX4') even though this triple is SX1; SX1-SX4 share one paper but the instance file appears to have been authored against the SX4 slot and reused.
- Resource estimates derived from this circuit will reflect ansatz cost, not HHL cost; using them as a Phase-8 proxy for HHL resource scaling will systematically understate true HHL gate counts (no Trotterised Hamiltonian simulation, no QFT).

### Recommendations from Vincent

- Either (a) replace circuit with an HHL skeleton (state-prep on system + QPE with Trotterised e^{-iAt} on a clock register + controlled-Y reciprocal on ancilla + inverse QPE) sized at paper scale, or (b) downgrade registry algorithm_family to 'other-gate-based' / 'ansatz-proxy' so the proxy classification is honest and Phase-8 aggregation does not attribute these costs to the HHL family.
- Reconcile instance.json metadata for SX1: set label/instance_id to SX1 and align algorithm_family with the registry choice made above.
- If the proxy is retained, document in the cohort that SX1-SX4 contribute ansatz-proxy resource estimates, not HHL estimates, and exclude them from any HHL-family scaling claim.

---

## DECISION (joint manual review)

```yaml
label_id: SX1
paper_id: 7cfdb2957f6c
experiment_id: exp_1
reviewers: [Vincent Wallerich, Aleix Telesforo]
reviewed_utc: 2026-04-25

# winner: 'phase3' | 'vincent' | 'merge' | 'other'
# action:  'accept_vincent' | 'reauthor_circuit' | 'demote_label' | 'relabel_family' | 'no_change'
decision:
  winner: vincent
  action: reauthor_circuit
  rationale: |
    Accept Vincent's DRIFT_MAJOR assessment.

    Phase 3 is faithful to the paper at the algorithm level. The paper is explicitly about demonstrating the HHL quantum linear equation solver on IBM Qiskit. It defines the linear-system problem Ax = b, describes the quantum form A|x> = |b>, and states that the core HHL procedure consists of state preparation, quantum phase estimation, controlled rotation / matrix inversion, and inverse quantum phase estimation.

    The implemented circuit described in Vincent's review is a generic RealAmplitudes ansatz followed by its inverse and measurement. This is a variational ansatz-stretch / compute-uncompute proxy. It lacks all defining HHL structures: no system/register separation for |b> and |x>, no clock/eigenvalue register, no QPE block, no controlled Hamiltonian simulation or EigsQPE-style evolution, no reciprocal lookup / controlled rotation ancilla, and no inverse-QPE uncomputation.

    The mismatch is major because the paper provides an actual HHL circuit-level demonstration, including a quantum circuit diagram for the second-order linear-system case and Qiskit Aqua HHL configuration details for fourth-order examples. Therefore, the paper is not merely a vague HHL reference; it gives enough structure that a generic RealAmplitudes proxy is clearly non-faithful.

    Scale alone does not repair the drift. The paper discusses 4-qubit and 7-qubit HHL demonstrations, while the proxy uses 4 qubits. The scale is acceptable, but the structure is not.

    Metadata consistency is also broken. The pasted review indicates that the circuit registry declares algorithm_family='hhl', while instance.json declares algorithm_family='other-gate-based' and labels the instance as SX4 rather than SX1. This would misstate HHL-family coverage unless corrected.
  evidence_section: >
    PDF page 1, Abstract: the paper states that it demonstrates the HHL quantum algorithm on IBM Qiskit and gives HHL circuits corresponding to 4-qubit and 7-qubit cases.
    PDF page 1, Introduction: the paper identifies HHL as an algorithm for solving linear equations and motivates its use in science, engineering, finance, economics, regression, differential equations, and large linear systems.
    PDF page 2, Section II "The HHL Algorithm": the paper defines Ax = b and A|x> = |b>, states that matrix A must be square and Hermitian or transformed into Hermitian form, and identifies the core HHL steps as phase estimation, controlled rotation, and inverse phase estimation.
    PDF page 2, Figure 1: the paper gives a schematic diagram of the HHL algorithm.
    PDF page 3, Figure 2: the paper shows the quantum circuit diagram of the HHL algorithm for second-order linear equations.
    PDF page 3, Qiskit implementation block: the paper uses Qiskit Aqua's HHL algorithm with EigsQPE, num_ancillae=3, num_time_slices=50, and a reciprocal lookup component.
    PDF pages 3-4, Results and Conclusion: the paper evaluates HHL on second-order and fourth-order matrices and reports fidelity results, confirming that the experiment is an HHL linear-system-solving demonstration rather than an ansatz-based variational method.
  remediation:
    template: hhl_proxy
    n_qubits: 4
    notes: |
      Required immediate handling:
      - Mark the current SX1 artifact as DRIFT_MAJOR.
      - Do not treat the current RealAmplitudes compute-uncompute circuit as an HHL implementation.
      - Exclude the current circuit from family-faithful HHL / quantum-linear-system resource aggregates.

      Metadata fixes:
      - Replace SX4 labels in instance.json and circuit.py with SX1 if this artifact is intended for SX1.
      - Align instance_id, label, register labels, function names, docstrings, and register_accounting labels with SX1.
      - Reconcile algorithm_family between circuit.py and instance.json.
      - If the circuit remains a generic ansatz proxy, set the registered family to other-gate-based or ansatz_proxy rather than hhl.
      - If the family remains hhl, the circuit body must be reauthored.

      Recommended HHL remediation:
      - Implement a minimal HHL skeleton at the paper's 4-qubit scale if feasible.
      - Include a system register for |b>.
      - Include a clock/eigenvalue register for QPE.
      - Add controlled Hamiltonian-simulation / controlled-U powers for a small Hermitian matrix A.
      - Add inverse-QFT / QPE uncomputation.
      - Add a reciprocal lookup or controlled rotation ancilla.
      - Measure/post-select the ancilla as in the standard HHL flow.
      - Use the paper's 2x2 example matrix A = [[1.5, 0.5], [0.5, 1.5]] and b = [sqrt(2)/2, sqrt(2)/2] if a directly paper-aligned toy instance is desired.

      Aggregation guidance:
      - Treat the paper as hhl at the paper level.
      - Treat the current implementation as non-family-faithful until reauthored.
      - If SX1-SX4 are sibling rows for the same HHL paper, deduplicate them in per-paper aggregation unless each row has a distinct and correctly labelled circuit/instance artifact.
```
