# Triage: SQ3

**Reviewers (joint):** Vincent Wallerich + Aleix Telesforo  
**Triage date:** 2026-04-25  
**Vincent verdict (first pass):** **DRIFT_MINOR**

---

## Paper

- **Title:** Improved Financial Forecasting via Quantum Machine Learning
- **Paper ID:** `2a0770a1a995` · **Experiment:** `exp_1` · **Silo:** `quantum-ml-finance` · **Cohort algorithm family:** `quantum-ml`

**Sources to consult:**
- Paper markdown: [p2_systematic_review/output/processed/2a0770a1a995.md](p2_systematic_review/output/processed/2a0770a1a995.md)
- Circuit: [p4_experiments/experiments/silos/quantum_ml_finance/2a0770a1a995/circuit.py](p4_experiments/experiments/silos/quantum_ml_finance/2a0770a1a995/circuit.py)
- Instance: [p4_experiments/experiments/silos/quantum_ml_finance/2a0770a1a995/instance.json](p4_experiments/experiments/silos/quantum_ml_finance/2a0770a1a995/instance.json)
- Phase 3 LLM extraction (GPT 5.3 / GPT 5.4-mini, P3 s2_quantitative): [p3_thematic_synthesis/s2_quantitative/output/extractions/2a0770a1a995.json](p3_thematic_synthesis/s2_quantitative/output/extractions/2a0770a1a995.json) (experiment_id `exp_1`)
- Vincent's review: [../vincent/SQ3.md](../vincent/SQ3.md)

---

## Disagreement

Vincent's review (first pass) flagged this label as **DRIFT_MINOR** —
i.e. the implemented circuit does not faithfully match what the
Phase 3 LLM extraction (GPT 5.3 / GPT 5.4-mini) recorded the paper's algorithm to be.

**Vincent's verdict summary:** Generic RealAmplitudes ansatz_stretch proxy is a defensible quantum-ml template at near-paper scale, but the circuit file is registered under label SQ5 (shared across SQ3/SQ4/SQ5 from the same paper) rather than SQ3, and the proxy does not reproduce the paper's RBS-Pyramid structure.

## Phase 3 (LLM) extraction — values for this label

**Source:** [p3_thematic_synthesis/s2_quantitative/output/extractions/2a0770a1a995.json](p3_thematic_synthesis/s2_quantitative/output/extractions/2a0770a1a995.json) (experiment_id `exp_1`)  
**Models used (per source `extraction_metadata.models_used`):** `gpt-5.3` (synthesis) + `gpt-5.4-mini` (extraction steps).

| Field | Phase 3 value |
|---|---|
| `algorithm_family` | `quantum-ml` |
| `algorithm_variant` | `Quantum DPP-RF hardware experiment with diagonal and semi-diagonal Clifford loaders` |
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
| Family-faithful | ✅ | Paper algorithm family is quantum-ml (QNN with RBS Pyramid orthogonal/compound layers); circuit is registered with algorithm_family='quantum-ml'. Family bucket matches. |
| Scale-faithful | ✅ | v2 num_qubits=4 (canonical reconciliation; paper hardware used 8q on ibm_hanoi); circuit n_qubits=6. Ratio 1.5x, within factor-of-2 tolerance and under the 12-qubit cap. |
| Structurally non-trivial | ✅ | Bare circuit is a parametrised RealAmplitudes ansatz with linear entanglement and 3 layers; full variant adds compute-uncompute (a . a^dagger) plus measurement. This is a non-trivial parametrised proxy, but it does NOT reproduce the paper's hamming-weight-preserving RBS Pyramid (n(n-1)/2 RBS gates, depth 2n-3, unary loader). Acceptable as a generic template_proxy under the cohort methodology, but structurally a stand-in rather than a faithful reimplementation. |
| Metadata-consistent | ❌ | circuit.py @register(label='SQ5', ...) and instance.json label='SQ5'/instance_id='SQ5_v3_proxy_v1' with algorithm_family='other-gate-based', while this audit target is SQ3. The directory is shared across SQ3/SQ4/SQ5 (all from paper 2a0770a1a995, flagged in v2 operator_notes), but the registered label and family tag do not match SQ3 (cohort.algorithm_family='quantum-ml'). |

### Concerns raised by Vincent

- Circuit file registers label='SQ5' and algorithm_family='other-gate-based' in instance.json, while the SQ3 cohort entry expects label='SQ3' and family='quantum-ml'.
- Single shared circuit at p4_experiments/experiments/silos/quantum_ml_finance/2a0770a1a995/ is reused for SQ3, SQ4, and SQ5 (three distinct cohort entries from the same paper); resource cost will be triple-counted unless deduplicated downstream.
- Generic RealAmplitudes ansatz does not preserve hamming weight and is not an RBS pyramid; depth and 2-qubit gate counts will not track paper formulas (Pyramid_depth=2n-3, gates=n(n-1)/2).
- instance.json paper_claimed.num_qubits=16 conflicts with v2 canonical num_qubits=4 and v2 instance_parameters.num_qubits=8 (ibm_hanoi hardware); scale baseline used by the proxy is ambiguous.

### Recommendations from Vincent

- Either (a) add a label='SQ3' alias registration pointing at the same build function, or (b) author SQ3-specific instance.json/circuit.py so per-label resource accounting is unambiguous.
- Reconcile algorithm_family in instance.json ('other-gate-based') with the SQ3 cohort tag ('quantum-ml').
- Reconcile paper_claimed.num_qubits across instance.json (16), v2 canonical (4), and v2 instance_parameters (8); cite which value the proxy is targeting.
- If feasible at this scale, swap the RealAmplitudes ansatz for an RBS-pyramid template (n(n-1)/2 RBS gates) so structural faithfulness improves without leaving the template-proxy methodology.

---

## DECISION (joint manual review)

```yaml
label_id: SQ3
paper_id: 2a0770a1a995
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
