# Triage: SM1

**Reviewers (joint):** Vincent Wallerich + Aleix Telesforo  
**Triage date:** 2026-04-25  
**Vincent verdict (first pass):** **DRIFT_MINOR**

---

## Paper

- **Title:** Entanglement scaling in matrix product state representation of smooth functions and their shallow quantum circuit approximations
- **Paper ID:** `48cd8220e3b2` · **Experiment:** `exp_1` · **Silo:** `simulation-monte-carlo` · **Cohort algorithm family:** `other-gate-based`

**Sources to consult:**
- Paper markdown: [p2_systematic_review/output/processed/48cd8220e3b2.md](p2_systematic_review/output/processed/48cd8220e3b2.md)
- Circuit: [p4_experiments/experiments/silos/simulation_monte_carlo/48cd8220e3b2/circuit.py](p4_experiments/experiments/silos/simulation_monte_carlo/48cd8220e3b2/circuit.py)
- Instance: [p4_experiments/experiments/silos/simulation_monte_carlo/48cd8220e3b2/instance.json](p4_experiments/experiments/silos/simulation_monte_carlo/48cd8220e3b2/instance.json)
- Phase 3 LLM extraction (GPT 5.3 / GPT 5.4-mini, P3 s2_quantitative): [p3_thematic_synthesis/s2_quantitative/output/extractions/48cd8220e3b2.json](p3_thematic_synthesis/s2_quantitative/output/extractions/48cd8220e3b2.json) (experiment_id `exp_1`)
- Vincent's review: [../vincent/SM1.md](../vincent/SM1.md)

---

## Disagreement

Vincent's review (first pass) flagged this label as **DRIFT_MINOR** —
i.e. the implemented circuit does not faithfully match what the
Phase 3 LLM extraction (GPT 5.3 / GPT 5.4-mini) recorded the paper's algorithm to be.

**Vincent's verdict summary:** Generic RealAmplitudes template proxy at N=6 is a defensible scale/family-faithful stand-in for the paper's MPS V-layer state-prep algorithm, but circuit.py and instance.json carry a stale 'SM8' label instead of 'SM1'.

## Phase 3 (LLM) extraction — values for this label

**Source:** [p3_thematic_synthesis/s2_quantitative/output/extractions/48cd8220e3b2.json](p3_thematic_synthesis/s2_quantitative/output/extractions/48cd8220e3b2.json) (experiment_id `exp_1`)  
**Models used (per source `extraction_metadata.models_used`):** `gpt-5.3` (synthesis) + `gpt-5.4-mini` (extraction steps).

| Field | Phase 3 value |
|---|---|
| `algorithm_family` | `other-gate-based` |
| `algorithm_variant` | `MPS-based shallow state-preparation / function-encoding circuits with iterative disentangling V-layers` |
| `num_qubits` | `64` |
| `ansatz` (free-text) | `V-layers / staircase and double-staircase isometry-based circuit decomposition` |
| `num_layers` | `1` |
| `circuit_depth` | `1` |
| `oracle_structure` | _(not extracted in P3 S2)_ |
| `encoding` | _(not extracted in P3 S2)_ |

_Note: P3 s2_quantitative extracts paper-level algorithm and quantum-resource fields. Circuit-level details that are not in the S2 schema (e.g. `oracle_structure`, `encoding`) appear as _(not extracted in P3 S2)_ above. Vincent's per-check notes below adjudicate those fields from direct paper + circuit reading._

### Vincent's per-check notes

| Check | Result | Note |
|---|---|---|
| Family-faithful | ✅ | Paper algorithm (MPS-to-circuit V-layer isometry state preparation) and the RealAmplitudes proxy both fall within the cohort 'other-gate-based' bucket; v2 ansatz_type='custom' and the proxy is explicitly acknowledged as a template stretch. |
| Scale-faithful | ✅ | Paper sweeps N in {6,10,15,18,20,25,27,40,50,64}; circuit uses n_qubits=6, exactly the smallest paper-tested value and within the 12-qubit tractability cap. |
| Structurally non-trivial | ✅ | Bare circuit is RealAmplitudes(reps=3, linear entanglement) with assigned random parameters; full variant adds compute-uncompute and measurement. Uses RY+CNOT (subset of paper's RX/RY/RZ/CNOT gate set). It is not a V-layer double-staircase nor isometry-synthesised, so it does not implement the paper's specific construction — but it is a non-trivial parametrised state-prep proxy as the cohort methodology permits. |
| Metadata-consistent | ❌ | circuit.py @register(label='SM8'), register_accounting(label='SM8'), and instance.json {instance_id:'SM8_v3_proxy_v1', label:'SM8'} all tag this artifact as SM8, but the cohort task and paper_id 48cd8220e3b2 are assigned to label_id SM1. Paper_id and silo are correct; only the label string is stale. |

### Concerns raised by Vincent

- Label mismatch: artifact files self-identify as 'SM8' while the cohort entry is 'SM1' (paper_id 48cd8220e3b2 is correct in both).
- Proxy does not reproduce the paper's V-layer (double-staircase) isometry-synthesised structure; it is a generic RealAmplitudes ansatz.
- instance_parameters.algorithm_variant_paper mentions 'TCI + isometry compilation' which is not what the proxy implements; flagged as expected for a stretch template proxy.

### Recommendations from Vincent

- Rename the @register/register_accounting label from 'SM8' to 'SM1' and update instance.json instance_id/label fields to match the canonical label_id.
- If a tighter proxy is wanted, replace the linear-entanglement RealAmplitudes with a brick-wall / staircase 2-qubit-block ansatz to better mimic the V-layer pattern; otherwise document explicitly that the cohort accepts ansatz_stretch for this paper.

---

## DECISION (joint manual review)

```yaml
label_id: SM1
paper_id: 48cd8220e3b2
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
