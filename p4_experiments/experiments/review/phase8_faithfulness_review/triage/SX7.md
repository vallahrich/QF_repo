# Triage: SX7

**Reviewers (joint):** Vincent Wallerich + Aleix Telesforo  
**Triage date:** 2026-04-25  
**Vincent verdict (first pass):** **DRIFT_MAJOR**

---

## Paper

- **Title:** Quantum Heavy-tailed Bandits
- **Paper ID:** `a2b747cae698` · **Experiment:** `exp_3` · **Silo:** `other` · **Cohort algorithm family:** `amplitude-estimation`

**Sources to consult:**
- Paper markdown: [p2_systematic_review/output/processed/a2b747cae698.md](p2_systematic_review/output/processed/a2b747cae698.md)
- Circuit: [p4_experiments/experiments/silos/other/a2b747cae698/circuit.py](p4_experiments/experiments/silos/other/a2b747cae698/circuit.py)
- Instance: [p4_experiments/experiments/silos/other/a2b747cae698/instance.json](p4_experiments/experiments/silos/other/a2b747cae698/instance.json)
- Phase 3 LLM extraction (GPT 5.3 / GPT 5.4-mini, P3 s2_quantitative): [p3_thematic_synthesis/s2_quantitative/output/extractions/a2b747cae698.json](p3_thematic_synthesis/s2_quantitative/output/extractions/a2b747cae698.json) (experiment_id `exp_3`)
- Vincent's review: [../vincent/SX7.md](../vincent/SX7.md)

---

## Disagreement

Vincent's review (first pass) flagged this label as **DRIFT_MAJOR** —
i.e. the implemented circuit does not faithfully match what the
Phase 3 LLM extraction (GPT 5.3 / GPT 5.4-mini) recorded the paper's algorithm to be.

**Vincent's verdict summary:** Circuit is a generic RealAmplitudes ansatz template with no amplitude-estimation structure (no Grover-style oracle, no QPE/inverse-QFT), so it does not represent the paper's AE-based QTME algorithm class; instance.json also tags the family as 'qaoa', inconsistent with the cohort and registry 'amplitude-estimation' tag.

## Phase 3 (LLM) extraction — values for this label

**Source:** [p3_thematic_synthesis/s2_quantitative/output/extractions/a2b747cae698.json](p3_thematic_synthesis/s2_quantitative/output/extractions/a2b747cae698.json) (experiment_id `exp_3`)  
**Models used (per source `extraction_metadata.models_used`):** `gpt-5.3` (synthesis) + `gpt-5.4-mini` (extraction steps).

| Field | Phase 3 value |
|---|---|
| `algorithm_family` | `amplitude-estimation` |
| `algorithm_variant` | `Heavy-QLinUCB (quantum linear UCB for heavy-tailed SLB)` |
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
| Family-faithful | ❌ | Registry @register tag is 'amplitude-estimation' (matches cohort and paper's QTME=AE-based mean estimator), but the implemented circuit is a generic variational ansatz (RealAmplitudes) with no AE-specific components. As an AE proxy this is family drift; the implementation is effectively a variational/QAOA-shaped proxy, not an AE-shaped proxy. |
| Scale-faithful | ✅ | Paper does not state a qubit count (NOT_STATED). Circuit uses n_qubits=5, which is within the <=12 tractability cap and is a reasonable small-scale proxy. |
| Structurally non-trivial | ❌ | Per the audit rubric, an amplitude-estimation circuit must have a Grover-style oracle and an inverse QFT (QPE-like structure). The full variant here is just A . A^dagger (compute-uncompute of a RealAmplitudes ansatz) followed by computational-basis measurement. There is no Grover oracle, no controlled-Q powers, and no inverse QFT, so the circuit lacks AE structure. |
| Metadata-consistent | ❌ | instance.json sets algorithm_family='qaoa' and instance_id/label='SX1' (not SX7), while the cohort/prompt and the @register decorator declare algorithm_family='amplitude-estimation' for label SX7. The registered label in circuit.py is also 'SX1', not 'SX7'. Multiple metadata inconsistencies. |

### Concerns raised by Vincent

- Implemented circuit is a generic RealAmplitudes ansatz proxy; it shares no structural resemblance to amplitude estimation (no Grover oracle, no inverse QFT, no QPE register).
- Registry decorator labels this circuit as 'SX1' with paper a2b747cae698, but this audit triple is SX7 (exp_3); appears to be a shared/reused circuit across SX5/SX6/SX7 (operator note flags redundancy).
- instance.json algorithm_family='qaoa' contradicts cohort.algorithm_family='amplitude-estimation' and the @register tag.
- Paper's circuit fields are entirely NOT_STATED, so the proxy cannot be validated against any paper-reported qubit/depth/gate counts.

### Recommendations from Vincent

- If the methodology permits a generic ansatz proxy, retag instance.json algorithm_family to match the cohort ('amplitude-estimation') and document explicitly that the proxy is an ansatz_stretch placeholder, not an AE implementation.
- Add a label-specific @register entry for SX7 (and SX5, SX6) rather than reusing the SX1 registration, so accounting and provenance are not collapsed across distinct cohort rows.
- If structural faithfulness is required for the AE family, replace the compute-uncompute pair with at minimum a controlled-Q-style oracle plus inverse-QFT QPE block at small qubit count (e.g., the Qiskit AmplitudeEstimation primitive), so the circuit is recognizably AE-shaped.

---

## DECISION (joint manual review)

```yaml
label_id: SX7
paper_id: a2b747cae698
experiment_id: exp_3
reviewers: [Vincent Wallerich, Aleix Telesforo]
reviewed_utc: 2026-04-25

# winner: 'phase3' | 'vincent' | 'merge' | 'other'
# action:  'accept_vincent' | 'reauthor_circuit' | 'demote_label' | 'relabel_family' | 'no_change'
decision:
  winner: vincent
  action: demote_label
  rationale: |
    Accept Vincent's DRIFT_MAJOR assessment for the current artifact.

    Phase 3 is faithful to the paper for exp_3. The relevant paper-side algorithm is Heavy-QLinUCB, a quantum linear UCB algorithm for heavy-tailed stochastic linear bandits. Heavy-QLinUCB uses QTME as a quantum mean-estimation subroutine, where QTME is built from QBME and the Quantum Monte Carlo Mean Estimator. The algorithm assumes quantum reward oracles and uses QTME estimates inside a weighted least-squares / Linear-UCB-style update.

    The implemented circuit described in Vincent's review is a generic RealAmplitudes ansatz followed by its inverse and measurement. This is not structurally faithful to Heavy-QLinUCB or to the amplitude-estimation / quantum-mean-estimation primitive behind it. It has no quantum reward oracle, no QTME/QBME segmented estimation structure, no amplitude-estimation or quantum Monte Carlo estimator skeleton, no Grover/amplitude-amplification iterate, no QPE or inverse-QFT-style estimation register, and no Linear-UCB / weighted least-squares wrapper.

    The paper is theoretical and oracle-model based, so the absence of a full gate-level implementation in the paper prevents exact circuit reconstruction. However, the current artifact is not merely underspecified; it is also reportedly mislabeled as SX1 and has instance.json algorithm_family='qaoa', while the cohort and paper family are amplitude-estimation. Those metadata defects make the current artifact unsafe for downstream aggregation.

    Therefore, SX7 should be demoted to a disclosed template-proxy label unless it is reauthored as a QAE/QME-shaped proxy. The paper-level family should remain amplitude-estimation / quantum-mean-estimation, but the current circuit body should not be counted as family-faithful.
  evidence_section: >
    PDF page 1, Abstract: the paper studies quantum multi-armed bandits and stochastic linear bandits with heavy-tailed rewards and proposes a new quantum mean estimator based on the Quantum Monte Carlo Mean Estimator.
    PDF pages 2-3, Contributions and Table 1: the paper states that QTME gives a quadratic improvement in estimation error and is used to obtain improved regret bounds for both quantum heavy-tailed MAB and SLB.
    PDF page 3, Section 3.1: the paper defines the quantum oracle OY and reviews the Quantum Monte Carlo Mean Estimator, which queries OY and OY^\dagger and serves as the amplitude-estimation-like primitive behind QTME.
    PDF pages 4-5, Section 4: Algorithm 1 defines QBME by segmenting the interval [0,B] and invoking QME on each segment; Algorithm 2 defines QTME by estimating positive and negative truncated components.
    PDF pages 6-7, Section 6 and Algorithm 4: the paper defines Heavy-QLinUCB for stochastic linear bandits, where each epoch runs QTME on a selected action's quantum reward oracle and then updates a weighted least-squares estimator.
    PDF page 7, Theorem 5: the paper proves the Heavy-QLinUCB regret bound and frames the algorithm as a quantum heavy-tailed SLB method, not as a gate-level variational ansatz.
    PDF page 7, Figure 1 and Experiments: the shown experiments compare regret behavior, while the paper does not provide a concrete quantum circuit implementation.
  remediation:
    template: ansatz_stretch
    n_qubits: 5
    notes: |
      Required immediate fixes:
      - Rename all SX1 references in circuit.py and instance.json to SX7.
      - Set experiment_id=exp_3 consistently.
      - Align @register(label=...), register_accounting(label=...), circuit names, function names, module docstring, instance_id, and instance label with SX7.
      - Change instance.json algorithm_family from qaoa to amplitude-estimation, or separate paper_family='amplitude-estimation' from proxy_family='ansatz_stretch/other-gate-based'.

      Faithfulness status:
      - Mark the current SX7 artifact as DRIFT_MAJOR until metadata is fixed.
      - If retained without reauthoring, demote it to template-proxy / resource-only status.
      - Do not treat the current RealAmplitudes circuit as a faithful Heavy-QLinUCB, QTME, QBME, QME, or amplitude-estimation implementation.

      Optional stronger remediation:
      - Replace ansatz_stretch with a qae_proxy / quantum-mean-estimation proxy.
      - Include a quantum reward-oracle placeholder O_s for the selected action.
      - Include amplitude-estimation-like structure: state preparation, controlled oracle calls or Grover/amplitude-amplification iterate, an estimation register, inverse QFT or iterative estimation surrogate, and measurement.
      - Add a small truncation-bin or segmented-estimation path to represent QBME/QTME.
      - Add an accounting note that Heavy-QLinUCB repeatedly invokes QTME across epochs and then performs weighted least-squares updates classically.
      - Keep n_qubits=5 unless a later implementation source provides a concrete qubit count.

      Aggregation guidance:
      - Treat the paper and SX7 label as amplitude-estimation / quantum-mean-estimation at the paper level.
      - Exclude the current circuit from family-faithful amplitude-estimation or QTME resource aggregates.
      - Deduplicate SX5/SX6/SX7 in per-paper aggregation unless each label is implemented as a distinct proxy for QTME, Heavy-QUCB, and Heavy-QLinUCB respectively.
```
