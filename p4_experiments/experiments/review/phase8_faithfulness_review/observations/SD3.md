# Triage: SD3

**Reviewers (joint):** Vincent Wallerich + Aleix Telesforo  
**Triage date:** 2026-04-25  
**Vincent verdict (first pass):** **DRIFT_MINOR**

---

## Paper

- **Title:** Quantum Speedups for Derivative Pricing: Beyond Black-Scholes
- **Paper ID:** `1bf880322e6f` · **Experiment:** `exp_5` · **Silo:** `derivative-pricing` · **Cohort algorithm family:** `hhl`

**Sources to consult:**
- Paper markdown: [p2_systematic_review/output/processed/1bf880322e6f.md](p2_systematic_review/output/processed/1bf880322e6f.md)
- Circuit: [p4_experiments/experiments/silos/derivative_pricing/1bf880322e6f__exp_5/circuit.py](p4_experiments/experiments/silos/derivative_pricing/1bf880322e6f__exp_5/circuit.py)
- Instance: [p4_experiments/experiments/silos/derivative_pricing/1bf880322e6f__exp_5/instance.json](p4_experiments/experiments/silos/derivative_pricing/1bf880322e6f__exp_5/instance.json)
- Phase 3 LLM extraction (GPT 5.3 / GPT 5.4-mini, P3 s2_quantitative): [p3_thematic_synthesis/s2_quantitative/output/extractions/1bf880322e6f.json](p3_thematic_synthesis/s2_quantitative/output/extractions/1bf880322e6f.json) (experiment_id `exp_5`)
- Vincent's review: [../vincent/SD3.md](../vincent/SD3.md)

---

## Disagreement

Vincent's review (first pass) flagged this label as **DRIFT_MINOR** —
i.e. the implemented circuit does not faithfully match what the
Phase 3 LLM extraction (GPT 5.3 / GPT 5.4-mini) recorded the paper's algorithm to be.

**Vincent's verdict summary:** HHL template proxy matches the cohort family tag and is structurally non-trivial, but the paper's primary primitive is QMCI/QAE with QET/QSVT loaders; HHL appears mainly as a discussed barrier, so the proxy represents the cohort's hhl tag rather than the paper's actual dominant algorithm.

## Phase 3 (LLM) extraction — values for this label

**Source:** [p3_thematic_synthesis/s2_quantitative/output/extractions/1bf880322e6f.json](p3_thematic_synthesis/s2_quantitative/output/extractions/1bf880322e6f.json) (experiment_id `exp_5`)  
**Models used (per source `extraction_metadata.models_used`):** `gpt-5.3` (synthesis) + `gpt-5.4-mini` (extraction steps).

| Field | Phase 3 value |
|---|---|
| `algorithm_family` | `hhl` |
| `algorithm_variant` | `quantum linear-systems / Fokker-Planck PDE solver for state preparation` |
| `num_qubits` | _(not extracted in P3 S2)_ |
| `ansatz` (free-text) | _(not extracted in P3 S2)_ |
| `num_layers` | _(not extracted in P3 S2)_ |
| `circuit_depth` | `1` |
| `oracle_structure` | _(not extracted in P3 S2)_ |
| `encoding` | _(not extracted in P3 S2)_ |

_Note: P3 s2_quantitative extracts paper-level algorithm and quantum-resource fields. Circuit-level details that are not in the S2 schema (e.g. `oracle_structure`, `encoding`) appear as _(not extracted in P3 S2)_ above. Vincent's per-check notes below adjudicate those fields from direct paper + circuit reading._

### Vincent's per-check notes

| Check | Result | Note |
|---|---|---|
| Family-faithful | ✅ | cohort.algorithm_family=hhl matches circuit registration algorithm_family=hhl and the authoring template (hhl). The paper does discuss HHL-type quantum linear-system / Fokker-Planck PDE solvers (Section on PDE-solver barriers), so an HHL proxy is within the family tag, even though the paper's headline contribution is QMCI/QAE-based pricing. |
| Scale-faithful | ✅ | v2 reports num_qubits=NOT_STATED (theoretical paper, no concrete instance). Circuit uses n_b=5 + n_clock=3 + 1 HHL ancilla = 9 qubits in the full pipeline (bare = 5). This is within the Tier-1 tractability cap (<=12) and is a reasonable default when the paper does not state a size. |
| Structurally non-trivial | ✅ | build_bare composes b_state_prep on n_b qubits with measurement; full pipeline calls full_hhl(n_b, n_clock, ham_sim_steps), which is the canonical HHL template (b-prep + QPE + controlled rotation + inverse QPE). This has the QPE-shaped structure expected of an HHL-family circuit. |
| Metadata-consistent | ✅ | instance.json algorithm_family=hhl, label/paper_id/experiment_id agree across instance.json, circuit.py @register decorator, and the v2 extraction. instance.notes explicitly flags this as a template proxy that does NOT implement the paper's algorithm, which is consistent with the v2 operator_notes. |

### Concerns raised by Vincent

- Paper's primary algorithmic contribution is QMCI/QAE with QET/QSVT distribution loading and a quantum Milstein/Levy-area sampler; HHL is discussed mainly as a barrier (Fokker-Planck PDE solver subsection). An HHL template proxy therefore captures a secondary, negatively-discussed thread of the paper rather than its main result.
- v2 extraction gives no num_qubits, depth, T-count, or two-qubit gate count (theoretical paper, NOT_STATED across the board), so scale-faithfulness can only be asserted in the weak sense of 'within tractability cap'.
- Cohort algorithm_family=hhl appears to follow the paper's methodology tag 'quantum-linear-systems' rather than the dominant primitive (amplitude-estimation); a QAE/QMCI template proxy would arguably be more representative of the paper's main claim.

### Recommendations from Vincent

- Consider rebinding SD3 cohort.algorithm_family to qae (or amplitude_estimation) and re-authoring against a QAE template to better reflect the paper's headline QMCI/QAE quadratic-speedup result; retain the hhl proxy only if the cohort is intentionally probing the PDE-solver barrier discussion.
- If keeping the hhl proxy, document in instance.notes that the proxy targets the paper's HHL/Fokker-Planck barrier discussion rather than its primary QMCI contribution, to avoid misinterpreting Phase-8 resource estimates as estimates of the paper's main algorithm.

---

## DECISION (joint manual review)

```yaml
label_id: SD3
paper_id: 1bf880322e6f
experiment_id: exp_5
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
