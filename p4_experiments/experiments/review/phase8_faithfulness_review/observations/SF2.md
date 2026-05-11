# Triage: SF2

**Reviewers (joint):** Vincent Wallerich + Aleix Telesforo  
**Triage date:** 2026-04-25  
**Vincent verdict (first pass):** **DRIFT_MINOR**

---

## Paper

- **Title:** Q-DTN: A Quantum-Enhanced Framework for Secure Financial Risk Management
- **Paper ID:** `8fec8d839e47` · **Experiment:** `exp_1` · **Silo:** `fraud-detection` · **Cohort algorithm family:** `other-gate-based`

**Sources to consult:**
- Paper markdown: [p2_systematic_review/output/processed/8fec8d839e47.md](p2_systematic_review/output/processed/8fec8d839e47.md)
- Circuit: [p4_experiments/experiments/silos/fraud_detection/8fec8d839e47/circuit.py](p4_experiments/experiments/silos/fraud_detection/8fec8d839e47/circuit.py)
- Instance: [p4_experiments/experiments/silos/fraud_detection/8fec8d839e47/instance.json](p4_experiments/experiments/silos/fraud_detection/8fec8d839e47/instance.json)
- Phase 3 LLM extraction (GPT 5.3 / GPT 5.4-mini, P3 s2_quantitative): [p3_thematic_synthesis/s2_quantitative/output/extractions/8fec8d839e47.json](p3_thematic_synthesis/s2_quantitative/output/extractions/8fec8d839e47.json) (experiment_id `exp_1`)
- Vincent's review: [../vincent/SF2.md](../vincent/SF2.md)

---

## Disagreement

Vincent's review (first pass) flagged this label as **DRIFT_MINOR** —
i.e. the implemented circuit does not faithfully match what the
Phase 3 LLM extraction (GPT 5.3 / GPT 5.4-mini) recorded the paper's algorithm to be.

**Vincent's verdict summary:** RealAmplitudes proxy at correct 5-qubit scale faithfully represents the paper's variational Ry/Rz+CNOT ansatz family, with minor deviations (Ry-only vs Ry/Rz, 3 vs 4 layers, stale 'other-gate-based' family tag).

## Phase 3 (LLM) extraction — values for this label

**Source:** [p3_thematic_synthesis/s2_quantitative/output/extractions/8fec8d839e47.json](p3_thematic_synthesis/s2_quantitative/output/extractions/8fec8d839e47.json) (experiment_id `exp_1`)  
**Models used (per source `extraction_metadata.models_used`):** `gpt-5.3` (synthesis) + `gpt-5.4-mini` (extraction steps).

| Field | Phase 3 value |
|---|---|
| `algorithm_family` | `other-gate-based` |
| `algorithm_variant` | `Quantum-Enhanced Risk Classifier (QERC) combining QSVM and VQC elements` |
| `num_qubits` | `5` |
| `ansatz` (free-text) | _(not extracted in P3 S2)_ |
| `num_layers` | `4` |
| `circuit_depth` | `4` |
| `oracle_structure` | _(not extracted in P3 S2)_ |
| `encoding` | _(not extracted in P3 S2)_ |

_Note: P3 s2_quantitative extracts paper-level algorithm and quantum-resource fields. Circuit-level details that are not in the S2 schema (e.g. `oracle_structure`, `encoding`) appear as _(not extracted in P3 S2)_ above. Vincent's per-check notes below adjudicate those fields from direct paper + circuit reading._

### Vincent's per-check notes

| Check | Result | Note |
|---|---|---|
| Family-faithful | ✅ | Paper describes a hybrid QSVM+VQC (QERC) with a parameterised variational circuit using alternating Ry/Rz single-qubit rotations and CNOT entanglers. RealAmplitudes(reps, entanglement='linear') is a standard variational ansatz with Ry rotations + CNOT entanglement — same family (variational-nisq / VQC). The cohort tag 'other-gate-based' is loose but not contradictory. |
| Scale-faithful | ✅ | Paper reports n_qubits_used=5; circuit instantiates n_qubits=5. Exact match (well within factor of 2 and below 12-qubit cap). |
| Structurally non-trivial | ✅ | build_bare uses ansatz_stretch (RealAmplitudes-style parameterised ansatz with random angles); _full_oracle composes ansatz . ansatz^dagger (compute-uncompute) followed by computational-basis measurement. Non-trivial parameterised entangling structure consistent with a VQC proxy. |
| Metadata-consistent | ❌ | Two minor inconsistencies: (1) instance.parameters.ansatz_layers=3 but paper-reported optimal depth is 4 layers (also recorded in instance.paper_claimed.circuit_depth=4 and v2 ansatz_layers=4); (2) algorithm_family tag is 'other-gate-based' whereas the paper is clearly variational-nisq / VQC. Both are documented as a template-proxy stretch and do not invalidate the proxy. |

### Concerns raised by Vincent

- ansatz_layers mismatch: instance uses 3 layers, paper reports optimal 4 layers (v2 extraction also says 4)
- RealAmplitudes uses Ry rotations only; paper specifies alternating Ry/Rz rotations (proxy approximation)
- algorithm_family tag 'other-gate-based' understates that this is a VQC/variational-nisq cohort entry
- Paper algorithm (hybrid QSVM+VQC with hinge loss, COBYLA, parameter-shift training) is not implemented — only the variational ansatz at paper scale is exercised, as openly disclosed in instance.notes

### Recommendations from Vincent

- Bump instance.parameters.ansatz_layers from 3 to 4 to match paper's reported optimal circuit_depth_layers=4
- Consider re-tagging algorithm_family as 'variational-nisq' (or adding a sub-tag) for downstream Phase-8 cohort analysis
- Optionally extend the proxy to interleave Rz layers between Ry layers to better mirror the paper's alternating Ry/Rz structure

---

## DECISION (joint manual review)

```yaml
label_id: SF2
paper_id: 8fec8d839e47
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
