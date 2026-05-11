# Triage: SM5

**Reviewers (joint):** Vincent Wallerich + Aleix Telesforo  
**Triage date:** 2026-04-25  
**Vincent verdict (first pass):** **DRIFT_MINOR**

---

## Paper

- **Title:** A quantum spectral method for simulating stochastic processes, with applications to Monte Carlo
- **Paper ID:** `8f553bfb1077` · **Experiment:** `exp_1` · **Silo:** `simulation-monte-carlo` · **Cohort algorithm family:** `other-gate-based`

**Sources to consult:**
- Paper markdown: [p2_systematic_review/output/processed/8f553bfb1077.md](p2_systematic_review/output/processed/8f553bfb1077.md)
- Circuit: [p4_experiments/experiments/silos/simulation_monte_carlo/8f553bfb1077__exp_1/circuit.py](p4_experiments/experiments/silos/simulation_monte_carlo/8f553bfb1077__exp_1/circuit.py)
- Instance: [p4_experiments/experiments/silos/simulation_monte_carlo/8f553bfb1077__exp_1/instance.json](p4_experiments/experiments/silos/simulation_monte_carlo/8f553bfb1077__exp_1/instance.json)
- Phase 3 LLM extraction (GPT 5.3 / GPT 5.4-mini, P3 s2_quantitative): [p3_thematic_synthesis/s2_quantitative/output/extractions/8f553bfb1077.json](p3_thematic_synthesis/s2_quantitative/output/extractions/8f553bfb1077.json) (experiment_id `exp_1`)
- Vincent's review: [../vincent/SM5.md](../vincent/SM5.md)

---

## Disagreement

Vincent's review (first pass) flagged this label as **DRIFT_MINOR** —
i.e. the implemented circuit does not faithfully match what the
Phase 3 LLM extraction (GPT 5.3 / GPT 5.4-mini) recorded the paper's algorithm to be.

**Vincent's verdict summary:** Acknowledged generic RealAmplitudes template proxy for a theoretical spectral-MC paper; family bucket and scale defensible, but circuit/instance carry the SM15 label rather than SM5 and structure does not reflect QFT/QAE spectral pipeline.

## Phase 3 (LLM) extraction — values for this label

**Source:** [p3_thematic_synthesis/s2_quantitative/output/extractions/8f553bfb1077.json](p3_thematic_synthesis/s2_quantitative/output/extractions/8f553bfb1077.json) (experiment_id `exp_1`)  
**Models used (per source `extraction_metadata.models_used`):** `gpt-5.3` (synthesis) + `gpt-5.4-mini` (extraction steps).

| Field | Phase 3 value |
|---|---|
| `algorithm_family` | `other-gate-based` |
| `algorithm_variant` | `Quantum spectral method for Brownian motion trajectory simulation` |
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
| Family-faithful | ✅ | Cohort algorithm_family is 'other-gate-based' and the circuit registers under the same family. Paper itself is a QFT+QAE spectral method, but template proxy under the 'other-gate-based' bucket is permitted by methodology. |
| Scale-faithful | ✅ | Paper reports only asymptotic qubit bounds (NOT_STATED concretely); proxy uses n_qubits=5, well within the 12-qubit tractability cap and consistent with v5 paper_claimed=null for this experiment row. |
| Structurally non-trivial | ✅ | Bare circuit is a 5-qubit RealAmplitudes ansatz with linear entanglement and 3 reps; full variant adds an inverse compute-uncompute oracle pair plus measurement, so it is not empty/trivial. It does NOT implement QFT/Wiener-loader/QAE structure of the paper, but that is the explicit template-proxy methodology. |
| Metadata-consistent | ❌ | Task label_id is SM5 but circuit.py registers label='SM15', instance.json instance_id='SM15_v5_proxy_v1' and label='SM15'. Notes field also references SM15. This is a v5 stretch-label mismatch with the SM5 cohort entry. |

### Concerns raised by Vincent

- Circuit and instance use label 'SM15' while this audit task is label_id 'SM5' (same paper_id 8f553bfb1077, same exp_1) - label registry / cohort mapping should be reconciled.
- v2 extraction notes SM5/SM6/SM7 are 3 redundant labels for one theoretical paper; combined with SM15 stretch label, the SM-family labeling for this paper is overloaded.
- Circuit is an explicit generic ansatz proxy and does not exercise QFT, recursive RBS data loader, or QAE oracle structure that the paper's algorithm requires; resource estimates from this proxy will not reflect the paper's claimed polylog(T) + poly(eps^{-1/2H}) scaling.

### Recommendations from Vincent

- Reconcile label naming: either rename the registered circuit/instance from SM15 to SM5 (or whichever canonical label the cohort uses) or document the SM5<->SM15 mapping in the cohort registry.
- If Phase-8 needs a more faithful proxy for this paper, consider a QFT-based template (e.g., QFT + amplitude-estimation skeleton) rather than a bare RealAmplitudes ansatz, while keeping qubit count <=12.

---

## DECISION (joint manual review)

```yaml
label_id: SM5
paper_id: 8f553bfb1077
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
