# Triage: SP2

**Reviewers (joint):** Vincent Wallerich + Aleix Telesforo  
**Triage date:** 2026-04-25  
**Vincent verdict (first pass):** **DRIFT_MINOR**

---

## Paper

- **Title:** Impacting Financial Predictions & Security through Quantum Support Vector Machines, Quantum Approximate Optimization, and Quantum-Resistant Lattice Cryptography
- **Paper ID:** `378c2a73ea46` · **Experiment:** `exp_3` · **Silo:** `portfolio-optimization` · **Cohort algorithm family:** `other-gate-based`

**Sources to consult:**
- Paper markdown: [p2_systematic_review/output/processed/378c2a73ea46.md](p2_systematic_review/output/processed/378c2a73ea46.md)
- Circuit: [p4_experiments/experiments/silos/portfolio_optimization/378c2a73ea46__exp_3/circuit.py](p4_experiments/experiments/silos/portfolio_optimization/378c2a73ea46__exp_3/circuit.py)
- Instance: [p4_experiments/experiments/silos/portfolio_optimization/378c2a73ea46__exp_3/instance.json](p4_experiments/experiments/silos/portfolio_optimization/378c2a73ea46__exp_3/instance.json)
- Phase 3 LLM extraction (GPT 5.3 / GPT 5.4-mini, P3 s2_quantitative): [p3_thematic_synthesis/s2_quantitative/output/extractions/378c2a73ea46.json](p3_thematic_synthesis/s2_quantitative/output/extractions/378c2a73ea46.json) (experiment_id `exp_3`)
- Vincent's review: [../vincent/SP2.md](../vincent/SP2.md)

---

## Disagreement

Vincent's review (first pass) flagged this label as **DRIFT_MINOR** —
i.e. the implemented circuit does not faithfully match what the
Phase 3 LLM extraction (GPT 5.3 / GPT 5.4-mini) recorded the paper's algorithm to be.

**Vincent's verdict summary:** Acknowledged template-proxy stretch: paper exp_3 is QAOA portfolio optimization but circuit is a generic RealAmplitudes ansatz with compute-uncompute oracle; cohort family bucket is 'other-gate-based' so the proxy is methodologically permitted, but it is not algorithmically QAOA and internal labels say SP9.

## Phase 3 (LLM) extraction — values for this label

**Source:** [p3_thematic_synthesis/s2_quantitative/output/extractions/378c2a73ea46.json](p3_thematic_synthesis/s2_quantitative/output/extractions/378c2a73ea46.json) (experiment_id `exp_3`)  
**Models used (per source `extraction_metadata.models_used`):** `gpt-5.3` (synthesis) + `gpt-5.4-mini` (extraction steps).

| Field | Phase 3 value |
|---|---|
| `algorithm_family` | `other-gate-based` |
| `algorithm_variant` | `Quantum Principal Component Analysis (QPCA)` |
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
| Family-faithful | ❌ | Paper exp_3 is QAOA over an Ising portfolio Hamiltonian (H = sum J_ij sigma_z sigma_z + sum h_i sigma_z) with mixer/cost alternation. Circuit implements a generic RealAmplitudes variational ansatz (linear entanglement) with no problem-Hamiltonian evolution and no QAOA mixer. Cohort tags this as 'other-gate-based' and instance.json explicitly declares 'generic variational ansatz stretch (template proxy)' / 'ansatz_stretch' / 'does NOT implement the paper's algorithm', so the family drift is preregistered and methodology-permitted, but it is genuine drift from the paper's QAOA. |
| Scale-faithful | ✅ | Paper does not state a qubit count for exp_3 (v2 num_qubits=NOT_STATED; paper itself flags qubits/p/mixer/shots as unspecified). Reported portfolio sizes are 50/100/200 assets, which would imply 50-200 qubits for a one-qubit-per-asset QAOA encoding, far above the 12-qubit tractability cap. Circuit uses n_qubits=5, ansatz_layers=3, which is within the agreed cap and is a legitimate small-scale proxy. |
| Structurally non-trivial | ✅ | Bare circuit is RealAmplitudes(n=5, reps=3, entanglement='linear') with random fixed-seed parameters; full circuit composes the ansatz with its inverse (compute-uncompute proxy oracle) and measures all 5 qubits. Non-empty, non-trivial gate content with parameterised single-qubit rotations and CX entanglement, consistent with the 'ansatz_stretch' template proxy contract — though it has none of QAOA's cost/mixer structure. |
| Metadata-consistent | ❌ | Internal labels in circuit.py and instance.json identify this artefact as 'SP9' (register(label='SP9'), instance_id='SP9_v5_proxy_v1', label='SP9'), while the cohort and audit task identify it as label_id='SP2'. Paper_id (378c2a73ea46) and experiment_id (exp_3) match. Per the v2 operator_notes, SP1/SP2/SP3 are three label rows that all map to this single multi-experiment paper, so the SP9 label appears to be a v5 stretch artefact label that has not been reconciled with the SP2 cohort identifier. |

### Concerns raised by Vincent

- Paper exp_3 algorithm (QAOA over Ising portfolio Hamiltonian) is not implemented; a generic RealAmplitudes ansatz with compute-uncompute is used as the proxy.
- Internal label mismatch: circuit/instance use label 'SP9' while the audit cohort row is 'SP2' (same paper_id and experiment_id).
- Paper does not specify qubit count, p-depth, mixer, shots, optimizer, iter, or seed for exp_3 (v2 extraction marks all as NOT_STATED), so scale-faithfulness can only be checked against the 12-qubit tractability cap.
- v2 fidelity_assessment is 'P' and operator_notes flag SP1/SP2/SP3 as three redundant labels from the same paper requiring manual triage.

### Recommendations from Vincent

- Reconcile the SP9 label inside circuit.py / instance.json with the canonical SP2 label_id (or document the SP9->SP2 mapping in cohort metadata) so register() and the audit row agree.
- If exp_3 is meant to be representative of QAOA portfolio optimization, consider replacing the RealAmplitudes proxy with a small QAOA template (problem-Hamiltonian Ising layer + transverse-field mixer, p=1-2) at n_qubits<=12 to make family_faithful=true.
- Resolve the SP1/SP2/SP3 multi-label issue from the same paper as flagged in v2 operator_notes before final Phase-8 resource estimation.

---

## DECISION (joint manual review)

```yaml
label_id: SP2
paper_id: 378c2a73ea46
experiment_id: exp_3
reviewers: [Vincent Wallerich, Aleix Telesforo]
reviewed_utc: 2026-04-25

# winner: 'phase3' | 'vincent' | 'merge' | 'other'
# action:  'accept_vincent' | 'reauthor_circuit' | 'demote_label' | 'relabel_family' | 'no_change'
decision:
  winner: merge
  action: reauthor_circuit
  rationale: |
    Accept Vincent's drift finding, but treat SP2 as requiring canonical-experiment cleanup before final resource use.

    The paper is a multi-method paper. It discusses QSVM for predictive modeling, QAOA for portfolio optimization, QPCA for dimensionality reduction, QBM for time-series forecasting, and lattice cryptography for security. For the portfolio-optimization silo, the relevant paper-side algorithm is QAOA: the paper explicitly states that QAOA is applied to portfolio optimization, encodes the optimization objective as an Ising Hamiltonian with Pauli-Z terms, and describes iterative gamma/beta optimization with cost and mixer operators.

    Phase 3 lists exp_3 as QPCA, which is also present in the paper, but QPCA is described as a dimensionality-reduction/preprocessing component rather than the portfolio-optimization algorithm itself. Therefore, either the experiment mapping is wrong, or SP2 is incorrectly assigned to the portfolio-optimization silo. This should be resolved before treating SP2 as a canonical family-faithful implementation.

    The current circuit described in Vincent's review is a generic RealAmplitudes ansatz with compute-uncompute structure. It is non-empty and acceptable only as a disclosed ansatz_stretch template proxy, but it is not algorithmically faithful to QAOA and it is also not a faithful QPCA implementation. It has no Ising cost layer, no Z_i Z_j portfolio-correlation couplings, no transverse-field mixer, no gamma/beta QAOA parameterization, and no phase-estimation/covariance-eigenvalue structure for QPCA.

    The internal SP9 metadata mismatch is material. Even if the current artifact is retained as a proxy, circuit.py and instance.json must be reconciled to the canonical SP2 label, or the SP9-to-SP2 mapping must be explicitly documented.
  evidence_section: >
    PDF pages 2-4: the abstract and introduction separate QSVM, QAOA, QPCA, QBM, and lattice cryptography as distinct components; QAOA is specifically tied to portfolio optimization, while QPCA is tied to dimensionality reduction.
    PDF pages 13-14: the QAOA section states that portfolio optimization is encoded as an Ising Hamiltonian H = sum_ij sigma_i^z J_ij sigma_j^z + sum_i h_i sigma_i^z, and that QAOA uses repeated task-Hamiltonian and mixing operators with parameters gamma and beta.
    PDF page 15, Figure 2: the workflow explicitly includes "Perform Portfolio Optimization (QAOA)".
    PDF pages 16-17: QPCA is described as dimensionality reduction of financial datasets through covariance/density-matrix representation and eigenvalue extraction, not as the portfolio-optimization objective itself.
    PDF pages 23-24: Table 4 and Figure 4 report QAOA Sharpe-ratio results for 50-, 100-, and 200-asset portfolios.
  remediation:
    template: qaoa_proxy
    n_qubits: 12
    notes: |
      First resolve the canonical experiment mapping:
      - If SP2 remains in the portfolio-optimization silo, reauthor it as a QAOA proxy.
      - If exp_3 is intentionally QPCA, move/relabel SP2 out of portfolio optimization and do not use a QAOA resource interpretation.
      - Do not keep the current RealAmplitudes ansatz as family-faithful for either QAOA or QPCA.

      Recommended QAOA remediation if SP2 remains portfolio optimization:
      - Use a small Ising portfolio instance truncated to <=12 qubits from the paper's 50/100/200-asset setting.
      - Encode J_ij as Z_i Z_j cost couplings.
      - Encode h_i as single-qubit Z fields.
      - Use a transverse-field X mixer.
      - Use p=1 or p=2 QAOA layers with explicit gamma and beta parameters.
      - Measure all qubits in the computational basis to represent candidate portfolio allocations.

      Required metadata fixes:
      - Replace all SP9 labels in circuit.py and instance.json with SP2, or document SP9 as an implementation alias for SP2.
      - Align instance_id, label, function names, register_accounting labels, and docstrings with SP2.
      - Keep paper_id=378c2a73ea46 and experiment_id=exp_3 only if the experiment mapping is confirmed.
      - If the current ansatz_stretch proxy is retained temporarily, mark it as non-family-faithful and exclude it from family-faithful QAOA portfolio-optimization aggregates.
      
```
