# Triage: SD4

**Reviewers (joint):** Vincent Wallerich + Aleix Telesforo  
**Triage date:** 2026-04-25  
**Vincent verdict (first pass):** **DRIFT_MINOR**

---

## Paper

- **Title:** Pricing multi-asset derivatives by variational quantum algorithms
- **Paper ID:** `1d44742c9e15` · **Experiment:** `exp_1` · **Silo:** `derivative-pricing` · **Cohort algorithm family:** `other-gate-based`

**Sources to consult:**
- Paper markdown: [p2_systematic_review/output/processed/1d44742c9e15.md](p2_systematic_review/output/processed/1d44742c9e15.md)
- Circuit: [p4_experiments/experiments/silos/derivative_pricing/1d44742c9e15/circuit.py](p4_experiments/experiments/silos/derivative_pricing/1d44742c9e15/circuit.py)
- Instance: [p4_experiments/experiments/silos/derivative_pricing/1d44742c9e15/instance.json](p4_experiments/experiments/silos/derivative_pricing/1d44742c9e15/instance.json)
- Phase 3 LLM extraction (GPT 5.3 / GPT 5.4-mini, P3 s2_quantitative): [p3_thematic_synthesis/s2_quantitative/output/extractions/1d44742c9e15.json](p3_thematic_synthesis/s2_quantitative/output/extractions/1d44742c9e15.json) (experiment_id `exp_1`)
- Vincent's review: [../vincent/SD4.md](../vincent/SD4.md)

---

## Disagreement

Vincent's review (first pass) flagged this label as **DRIFT_MINOR** —
i.e. the implemented circuit does not faithfully match what the
Phase 3 LLM extraction (GPT 5.3 / GPT 5.4-mini) recorded the paper's algorithm to be.

**Vincent's verdict summary:** RealAmplitudes (RY+CZ-style, linear entanglement) compute-uncompute proxy is a defensible variational stand-in for the paper's RY+CZ VQS ansatz at near-paper scale, but cohort family tag 'other-gate-based' and instance 'vqe' are both stale relative to the paper's actual VQS algorithm.

## Phase 3 (LLM) extraction — values for this label

**Source:** [p3_thematic_synthesis/s2_quantitative/output/extractions/1d44742c9e15.json](p3_thematic_synthesis/s2_quantitative/output/extractions/1d44742c9e15.json) (experiment_id `exp_1`)  
**Models used (per source `extraction_metadata.models_used`):** `gpt-5.3` (synthesis) + `gpt-5.4-mini` (extraction steps).

| Field | Phase 3 value |
|---|---|
| `algorithm_family` | `other-gate-based` |
| `algorithm_variant` | `variational quantum simulation (VQS) for linear ODE/PDE evolution with SWAP-test overlap estimation` |
| `num_qubits` | `6` |
| `ansatz` (free-text) | `hardware-efficient ansatz with layers of RY gates and CZ entangling layers` |
| `num_layers` | _(not extracted in P3 S2)_ |
| `circuit_depth` | _(not extracted in P3 S2)_ |
| `oracle_structure` | _(not extracted in P3 S2)_ |
| `encoding` | _(not extracted in P3 S2)_ |

_Note: P3 s2_quantitative extracts paper-level algorithm and quantum-resource fields. Circuit-level details that are not in the S2 schema (e.g. `oracle_structure`, `encoding`) appear as _(not extracted in P3 S2)_ above. Vincent's per-check notes below adjudicate those fields from direct paper + circuit reading._

### Vincent's per-check notes

| Check | Result | Note |
|---|---|---|
| Family-faithful | ✅ | Paper uses a parameterized RY+CZ ansatz inside a VQS loop; RealAmplitudes (RY rotations + CZ-like entanglers) is the canonical hardware-efficient ansatz proxy and is family-faithful as a variational template. The VQS time evolution and SWAP/Hadamard tests are not implemented, but the methodology explicitly permits a template proxy. |
| Scale-faithful | ✅ | Paper reports up to 6 qubits in VQS runs (ngr=64); circuit uses 5 qubits, well within factor 2 and below the 12-qubit cap. |
| Structurally non-trivial | ✅ | Bare circuit is RealAmplitudes(reps=3, linear entanglement) with assigned parameters; full circuit composes ansatz . ansatz_dagger compute-uncompute and measures. Non-trivial parameterized two-qubit-entangling structure consistent with a variational ansatz. |
| Metadata-consistent | ❌ | Cohort/registry tags algorithm_family='other-gate-based' while instance.json sets algorithm_family='vqe'; the paper is VQS (variational, hybrid), so the cohort 'other-gate-based' label is a stale/incorrect family tag. Also, ansatz_layers in instance (3) differs from paper's reported 4 (within proxy tolerance) and instance n_qubits=5 vs paper-claimed 6. |

### Concerns raised by Vincent

- Cohort algorithm_family='other-gate-based' contradicts instance algorithm_family='vqe' and the paper's VQS classification.
- Implementation is explicitly a generic ansatz_stretch template proxy and does not implement VQS time evolution, LCU decomposition of F/C, SWAP test, or Hadamard test.
- n_qubits=5 and ansatz_layers=3 instead of paper's 6 qubits / 4 layers, though within proxy tolerance.

### Recommendations from Vincent

- Update cohort algorithm_family for SD4 from 'other-gate-based' to 'vqe' (or 'variational') to align with the paper and instance.json.
- Optionally bump n_qubits to 6 and ansatz_layers to 4 to exactly match the paper's reported configuration since both are well under the 12-qubit cap.

---

## DECISION (joint manual review)

```yaml
label_id: SD4
paper_id: 1d44742c9e15
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
