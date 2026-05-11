# Triage: SM3

**Reviewers (joint):** Vincent Wallerich + Aleix Telesforo  
**Triage date:** 2026-04-25  
**Vincent verdict (first pass):** **DRIFT_MINOR**

---

## Paper

- **Title:** Accelerated quantum Monte Carlo with mitigated error on noisy quantum computer
- **Paper ID:** `646bd6bbd935` · **Experiment:** `exp_1` · **Silo:** `simulation-monte-carlo` · **Cohort algorithm family:** `other-gate-based`

**Sources to consult:**
- Paper markdown: [p2_systematic_review/output/processed/646bd6bbd935.md](p2_systematic_review/output/processed/646bd6bbd935.md)
- Circuit: [p4_experiments/experiments/silos/simulation_monte_carlo/646bd6bbd935/circuit.py](p4_experiments/experiments/silos/simulation_monte_carlo/646bd6bbd935/circuit.py)
- Instance: [p4_experiments/experiments/silos/simulation_monte_carlo/646bd6bbd935/instance.json](p4_experiments/experiments/silos/simulation_monte_carlo/646bd6bbd935/instance.json)
- Phase 3 LLM extraction (GPT 5.3 / GPT 5.4-mini, P3 s2_quantitative): [p3_thematic_synthesis/s2_quantitative/output/extractions/646bd6bbd935.json](p3_thematic_synthesis/s2_quantitative/output/extractions/646bd6bbd935.json) (experiment_id `exp_1`)
- Vincent's review: [../vincent/SM3.md](../vincent/SM3.md)

---

## Disagreement

Vincent's review (first pass) flagged this label as **DRIFT_MINOR** —
i.e. the implemented circuit does not faithfully match what the
Phase 3 LLM extraction (GPT 5.3 / GPT 5.4-mini) recorded the paper's algorithm to be.

**Vincent's verdict summary:** Acknowledged template proxy: scale-faithful (6 qubits) and within the loose 'other-gate-based' family bucket, but the implementation is a generic RealAmplitudes ansatz with compute-uncompute and does not implement QCMC's controlled-correction / Trotter-sampling structure; instance/circuit also carry stale 'SM10' labels.

## Phase 3 (LLM) extraction — values for this label

**Source:** [p3_thematic_synthesis/s2_quantitative/output/extractions/646bd6bbd935.json](p3_thematic_synthesis/s2_quantitative/output/extractions/646bd6bbd935.json) (experiment_id `exp_1`)  
**Models used (per source `extraction_metadata.models_used`):** `gpt-5.3` (synthesis) + `gpt-5.4-mini` (extraction steps).

| Field | Phase 3 value |
|---|---|
| `algorithm_family` | `other-gate-based` |
| `algorithm_variant` | `quantum-circuit Monte Carlo (QCMC) with leading-order-rotation (LOR) and Pauli-operator-expansion (POE) summation formulas; compact and forward-backward circuits; probabilistic error cancellation a...` |
| `num_qubits` | `6` |
| `ansatz` (free-text) | _(not extracted in P3 S2)_ |
| `num_layers` | _(not extracted in P3 S2)_ |
| `circuit_depth` | _(not extracted in P3 S2)_ |
| `oracle_structure` | _(not extracted in P3 S2)_ |
| `encoding` | _(not extracted in P3 S2)_ |

_Note: P3 s2_quantitative extracts paper-level algorithm and quantum-resource fields. Circuit-level details that are not in the S2 schema (e.g. `oracle_structure`, `encoding`) appear as _(not extracted in P3 S2)_ above. Vincent's per-check notes below adjudicate those fields from direct paper + circuit reading._

### Vincent's per-check notes

| Check | Result | Note |
|---|---|---|
| Family-faithful | ✅ | Cohort tags algorithm_family='other-gate-based'; paper is QCMC (hybrid non-variational MC subroutine, neither variational nor an oracle-based primitive). A generic ansatz proxy under the 'other-gate-based' bucket is defensible per the explicit template-proxy methodology, though it is a loose fit. |
| Scale-faithful | ✅ | v2 reports 6 qubits (3-site Fermi-Hubbard, Jordan-Wigner); circuit instantiates n_qubits=6. Exact match, well within the 2x / 12-qubit cap rule. |
| Structurally non-trivial | ❌ | Circuit is a 3-layer linear-entanglement RealAmplitudes ansatz plus its inverse with measurement; it has no Trotter step, no controlled-correction operators, no ancilla-based amplitude estimation, and no forward-backward / postselection structure that would mark a QCMC implementation. Compute-uncompute on a random-parameter ansatz is a generic stretch, not QCMC-shaped. instance.notes acknowledges this explicitly ('does NOT implement the paper's algorithm'). |
| Metadata-consistent | ❌ | circuit.py and instance.json identify the cohort entry as label='SM10' (e.g. instance_id='SM10_v3_proxy_v1', register(label='SM10', ...), QuantumCircuit name 'SM10_bare'/'SM10_full'), while the canonical label_id under audit is SM3. paper_id and experiment_id match, so this appears to be a stale pre-canonicalisation label rather than a wrong-paper hookup, but the inconsistency should be resolved before Phase-8. |

### Concerns raised by Vincent

- Circuit does not implement QCMC: no Trotter / S1 product, no controlled-correction operator sampling, no ancilla amplitude-estimation circuit, no forward-backward postselection.
- Compute-uncompute of a random-parameter RealAmplitudes ansatz is a depth/2q-gate stretch, not a QCMC-shaped proxy; resulting 2q-gate count will not track the paper's ~2380 CNOT figure unless layers is tuned for that purpose.
- Stale label 'SM10' in circuit registration, instance_id, and circuit names while cohort label_id is SM3.
- Cohort family tag 'other-gate-based' is a coarse bucket for a hybrid non-variational MC algorithm; downstream Phase-8 aggregations grouped by family should treat this entry with care.

### Recommendations from Vincent

- Rename the registered label and instance_id from 'SM10' to 'SM3' (or document the alias mapping) so registry lookups match the canonical label_id.
- If a closer proxy is desired without implementing full QCMC, swap the compute-uncompute ansatz for a small Trotter step (POE-style: a few Pauli-rotation layers + nearest-neighbour CNOT staircases) repeated N times, which would be structurally more QCMC-shaped at the same 6-qubit scale.
- Optionally calibrate ansatz_layers so the proxy's two-qubit-gate count is order-of-magnitude consistent with the paper's reported ~2380 CNOTs, to avoid misleading Phase-8 cost estimates.

---

## DECISION (joint manual review)

```yaml
label_id: SM3
paper_id: 646bd6bbd935
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
