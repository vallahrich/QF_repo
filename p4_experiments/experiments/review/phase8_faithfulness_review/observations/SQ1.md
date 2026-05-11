# Triage: SQ1

**Reviewers (joint):** Vincent Wallerich + Aleix Telesforo  
**Triage date:** 2026-04-25  
**Vincent verdict (first pass):** **DRIFT_MAJOR**

---

## Paper

- **Title:** Quantum Algorithm for Unsupervised Anomaly Detection
- **Paper ID:** `14777484b99d` · **Experiment:** `exp_1` · **Silo:** `quantum-ml-finance` · **Cohort algorithm family:** `other-gate-based`

**Sources to consult:**
- Paper markdown: [p2_systematic_review/output/processed/14777484b99d.md](p2_systematic_review/output/processed/14777484b99d.md)
- Circuit: [p4_experiments/experiments/silos/quantum_ml_finance/14777484b99d/circuit.py](p4_experiments/experiments/silos/quantum_ml_finance/14777484b99d/circuit.py)
- Instance: [p4_experiments/experiments/silos/quantum_ml_finance/14777484b99d/instance.json](p4_experiments/experiments/silos/quantum_ml_finance/14777484b99d/instance.json)
- Phase 3 LLM extraction (GPT 5.3 / GPT 5.4-mini, P3 s2_quantitative): [p3_thematic_synthesis/s2_quantitative/output/extractions/14777484b99d.json](p3_thematic_synthesis/s2_quantitative/output/extractions/14777484b99d.json) (experiment_id `exp_1`)
- Vincent's review: [../vincent/SQ1.md](../vincent/SQ1.md)

---

## Disagreement

Vincent's review (first pass) flagged this label as **DRIFT_MAJOR** —
i.e. the implemented circuit does not faithfully match what the
Phase 3 LLM extraction (GPT 5.3 / GPT 5.4-mini) recorded the paper's algorithm to be.

**Vincent's verdict summary:** Circuit is a generic RealAmplitudes ansatz with compute-uncompute proxy; paper specifies a QRAM-based quantum LOF using amplitude estimation, Grover, quantum minimum search, and quantum arithmetic — none of these primitives are present.

## Phase 3 (LLM) extraction — values for this label

**Source:** [p3_thematic_synthesis/s2_quantitative/output/extractions/14777484b99d.json](p3_thematic_synthesis/s2_quantitative/output/extractions/14777484b99d.json) (experiment_id `exp_1`)  
**Models used (per source `extraction_metadata.models_used`):** `gpt-5.3` (synthesis) + `gpt-5.4-mini` (extraction steps).

| Field | Phase 3 value |
|---|---|
| `algorithm_family` | `other-gate-based` |
| `algorithm_variant` | `Quantum LOF algorithm for unsupervised anomaly detection` |
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
| Family-faithful | ✅ | Both cohort and circuit are tagged 'other-gate-based'; paper is amplitude-estimation/Grover-based which fits the catch-all 'other-gate-based' bucket. Family tag matches, though the specific algorithmic content does not. |
| Scale-faithful | ✅ | Paper does not state qubit count (NOT_STATED in v2 extraction); circuit uses n_qubits=5 which is within the 12-qubit tractability cap and a defensible small-scale proxy. |
| Structurally non-trivial | ❌ | Paper requires QRAM oracle access, amplitude estimation (with QFT), quantum minimum search, Grover search, quantum counting, and quantum multiply-adder. Circuit implements only a RealAmplitudes ansatz followed by its inverse (compute-uncompute), with no QPE/QFT structure, no Grover oracle/diffusion, no arithmetic registers. Structurally this is a generic VQE-style ansatz, not an HHL/QAE/Grover-shaped circuit. |
| Metadata-consistent | ❌ | Circuit file labels itself 'SQ7' throughout (label, names SQ7_bare/SQ7_full, register decorator label='SQ7') but the cohort label_id is SQ1 and instance.json also uses label='SQ7'/instance_id='SQ7_v3_proxy_v1'. Same paper_id (14777484b99d) is shared, but the SQ1 vs SQ7 label divergence is a registry inconsistency. |

### Concerns raised by Vincent

- Circuit does not implement any of the paper's named quantum primitives (amplitude estimation, Grover, quantum minimum search, quantum counting, quantum multiply-adder, QRAM oracles).
- Compute-uncompute of a RealAmplitudes ansatz is not a faithful proxy for an amplitude-estimation/Grover oracle structure; it is a generic variational template.
- Label mismatch: cohort/prompt label_id is SQ1, but circuit.py and instance.json self-identify as SQ7 (same paper_id 14777484b99d).
- v2 extraction reports oracle_structure='amplitude_estimation', yet the circuit has no QFT/inverse-QFT or controlled-unitary phase-estimation block.
- The circuit explicitly states in its notes 'paper algorithm not implemented; generic RealAmplitudes ansatz at paper-scale' — i.e., self-documented as a non-faithful proxy.

### Recommendations from Vincent

- Reconcile SQ1 vs SQ7 labeling across cohort, instance.json, and circuit.py register decorator to remove registry ambiguity.
- If treating this entry as a deliberate template proxy for resource estimation, document explicitly in the cohort that the circuit is a non-family-faithful stand-in (generic ansatz proxy, not amplitude-estimation-shaped).
- For a more family-faithful proxy, replace the ansatz-compute-uncompute with a small QAE skeleton: state-prep ansatz + Grover-style oracle reflection + inverse QFT on a small ancilla register, which would at least carry the QPE/Grover structural signature the paper's algorithm requires.

---

## DECISION (joint manual review)

```yaml
label_id: SQ1
paper_id: 14777484b99d
experiment_id: exp_1
reviewers: [Vincent Wallerich, Aleix Telesforo]
reviewed_utc: 2026-04-25

# winner: 'phase3' | 'vincent' | 'merge' | 'other'
# action:  'accept_vincent' | 'reauthor_circuit' | 'demote_label' | 'relabel_family' | 'no_change'
decision:
  winner: 
  action: 
  rationale: |
    
  evidence_section: 
  remediation:
    template:           # e.g. hhl_proxy | qae_proxy | qaoa_proxy | qft_phase_proxy | ansatz_stretch
    n_qubits:
    notes: |
      
```
