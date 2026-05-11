# Triage: SP1

**Reviewers (joint):** Vincent Wallerich + Aleix Telesforo  
**Triage date:** 2026-04-25  
**Vincent verdict (first pass):** **DRIFT_MAJOR**

---

## Paper

- **Title:** Impacting Financial Predictions & Security through Quantum Support Vector Machines, Quantum Approximate Optimization, and Quantum-Resistant Lattice Cryptography
- **Paper ID:** `378c2a73ea46` · **Experiment:** `exp_1` · **Silo:** `portfolio-optimization` · **Cohort algorithm family:** `other-gate-based`

**Sources to consult:**
- Paper markdown: [p2_systematic_review/output/processed/378c2a73ea46.md](p2_systematic_review/output/processed/378c2a73ea46.md)
- Circuit: [p4_experiments/experiments/silos/portfolio_optimization/378c2a73ea46/circuit.py](p4_experiments/experiments/silos/portfolio_optimization/378c2a73ea46/circuit.py)
- Instance: [p4_experiments/experiments/silos/portfolio_optimization/378c2a73ea46/instance.json](p4_experiments/experiments/silos/portfolio_optimization/378c2a73ea46/instance.json)
- Phase 3 LLM extraction (GPT 5.3 / GPT 5.4-mini, P3 s2_quantitative): [p3_thematic_synthesis/s2_quantitative/output/extractions/378c2a73ea46.json](p3_thematic_synthesis/s2_quantitative/output/extractions/378c2a73ea46.json) (experiment_id `exp_1`)
- Vincent's review: [../vincent/SP1.md](../vincent/SP1.md)

---

## Disagreement

Vincent's review (first pass) flagged this label as **DRIFT_MAJOR** —
i.e. the implemented circuit does not faithfully match what the
Phase 3 LLM extraction (GPT 5.3 / GPT 5.4-mini) recorded the paper's algorithm to be.

**Vincent's verdict summary:** v2 ground truth identifies exp_1 as QAOA on a 50-asset portfolio with an Ising cost Hamiltonian, but the implemented circuit is a QSVM-style amplitude-encoding paired-inverse template proxy and is also mislabeled as SP4 with algorithm_family quantum-svm.

## Phase 3 (LLM) extraction — values for this label

**Source:** [p3_thematic_synthesis/s2_quantitative/output/extractions/378c2a73ea46.json](p3_thematic_synthesis/s2_quantitative/output/extractions/378c2a73ea46.json) (experiment_id `exp_1`)  
**Models used (per source `extraction_metadata.models_used`):** `gpt-5.3` (synthesis) + `gpt-5.4-mini` (extraction steps).

| Field | Phase 3 value |
|---|---|
| `algorithm_family` | `other-gate-based` |
| `algorithm_variant` | `Quantum Support Vector Machines (QSVM) with quantum kernel` |
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
| Family-faithful | ❌ | Paper exp_1 (per v2) = QAOA portfolio optimization with Ising H = sum_ij J_ij Z_i Z_j + sum_i h_i Z_i and parameterized (gamma, beta) layers. Circuit implements an amplitude-encoding ansatz with an encoder . encoder^dagger paired-inverse oracle (a QSVM-kernel-style template), which is a different algorithm family. Cohort tag 'other-gate-based' is broad enough to nominally cover both, but the proxy does not represent QAOA. |
| Scale-faithful | ✅ | Paper does not state qubit count (NOT_STATED). Circuit uses n_qubits=5, well within the 12-qubit tractability cap; no contradictory paper number to violate the factor-of-2 rule. |
| Structurally non-trivial | ✅ | Bare circuit composes a parameterized amplitude encoder with computational-basis measurement; full accounting registers a paired-inverse oracle (encoder . encoder^dagger). Non-trivial as a QSVM-kernel proxy, but lacks any QAOA structure (no cost-unitary exp(-i gamma H_C) and no mixer exp(-i beta H_M) layers, no Z_iZ_j couplings). |
| Metadata-consistent | ❌ | instance.json and circuit.py are labeled 'SP4' (label/instance_id/name/description), and instance algorithm_family='quantum-svm' / algorithm_variant_paper='QSVM for financial classification and regression'. Cohort entry for SP1 declares algorithm_family='other-gate-based', and v2 extraction targets QAOA portfolio optimization (exp_1). Label, family tag, and variant string all disagree with the cohort/v2 record. |

### Concerns raised by Vincent

- Algorithm-family mismatch: implemented proxy is QSVM-kernel amplitude-encoding paired-inverse, but v2 ground truth for exp_1 is QAOA portfolio optimization on the Ising Hamiltonian.
- Cross-label contamination: circuit.py and instance.json are stamped 'SP4' (label, instance_id 'SP4_v3_proxy_v1', register label='SP4', circuit name 'SP4_bare', algorithm_variant_paper QSVM), suggesting this artifact was authored for a different cohort entry and reused for SP1.
- v2 operator_notes explicitly flags substantive drift from the old SP1 (old=QSVM, v2=QAOA) and asks for manual canonical-experiment selection; the implemented proxy still tracks the old QSVM reading, not the v2-selected QAOA exp_1.
- No QAOA-specific structure present: no Z_iZ_j cost layer, no transverse-field mixer, no (gamma, beta) parameter pair, so Phase-8 resource extrapolation from this circuit will not represent QAOA cost.
- Paper does not specify qubit count, p-depth, mixer, shots, or optimizer; even a faithful QAOA proxy here would have to assume defaults, but the current proxy is the wrong family entirely.

### Recommendations from Vincent

- Replace the SP1 circuit with a QAOA template proxy (e.g., portfolio_optimization/qaoa_ising) using a 50-node Ising-style cost Hamiltonian truncated/mapped to <=12 qubits and a default p (e.g., p=1 or p=2) with a transverse-field mixer.
- Fix metadata: set label='SP1', algorithm_family='quantum-optimization' (or repository's QAOA bucket) and algorithm_variant_paper='QAOA on 50-asset Ising portfolio Hamiltonian'; rename instance_id and remove SP4 stamps.
- If the canonical-experiment decision is to keep the QSVM reading instead of v2's QAOA, record that decision explicitly in DECISIONS_LOG.md and re-run the v2 extraction so the cohort ground truth and the implemented proxy agree.

---

## DECISION (joint manual review)

```yaml
label_id: SP1
paper_id: 378c2a73ea46
experiment_id: exp_1
reviewers: [Vincent Wallerich, Aleix Telesforo]
reviewed_utc: 2026-04-25

# winner: 'phase3' | 'vincent' | 'merge' | 'other'
# action:  'accept_vincent' | 'reauthor_circuit' | 'demote_label' | 'relabel_family' | 'no_change'
decision:
  winner: vincent
  action: reauthor_circuit
  rationale: |
    Accept Vincent's DRIFT_MAJOR assessment for SP1.

    The paper is multi-method: it discusses QSVM for prediction/classification, QAOA for portfolio optimization, QPCA for dimensionality reduction, QBM for forecasting, and lattice cryptography for security. However, this triage label belongs to the portfolio-optimization silo. For that experimental context, the relevant paper algorithm is QAOA, not QSVM.

    The paper's portfolio-optimization section explicitly states that QAOA is used for combinatorial asset-allocation tasks. It encodes portfolio optimization as an Ising Hamiltonian with Pauli-Z terms, pairwise couplings J_ij, and asset-level fields h_i. It also describes QAOA as an iterative process with task-Hamiltonian and mixing operators parameterized by gamma and beta, followed by measurement to extract the optimal portfolio configuration.

    The implemented circuit described in Vincent's review is a QSVM-style amplitude-encoding / paired-inverse quantum-kernel proxy. That structure may loosely correspond to the paper's QSVM predictive-modeling component, but it does not represent the portfolio-optimization QAOA experiment. It lacks the central QAOA structures: no Ising cost Hamiltonian, no exp(-i gamma H_C) cost layer, no transverse-field mixer exp(-i beta H_M), no repeated p-layer gamma/beta structure, and no Z_i Z_j portfolio-correlation couplings.

    The metadata drift is also material. The pasted review indicates that circuit.py and instance.json are stamped as SP4, with algorithm_family='quantum-svm' and a QSVM variant string, while this triage label is SP1 and the relevant cohort row is portfolio optimization. This is cross-label contamination rather than a faithful implementation of SP1.

    Therefore, the paper should not be treated as a QSVM instance for this label. SP1 should be reauthored as a QAOA portfolio-optimization proxy, or otherwise demoted/excluded from family-faithful portfolio-optimization aggregates.
  evidence_section: >
    PDF pages 10-12: the paper describes QSVM as a financial predictive-modeling/classification component using quantum kernels. This explains why a QSVM reading is present in the paper, but it belongs to prediction/classification rather than portfolio optimization.
    PDF pages 13-14: the paper introduces QAOA for combinatorial portfolio optimization, defines the Sharpe-ratio objective context, encodes the portfolio task as an Ising Hamiltonian H = sum_ij sigma_i^z J_ij sigma_j^z + sum_i h_i sigma_i^z, and describes QAOA as an iterative gamma/beta optimization with task and mixing operators.
    PDF page 15, Figure 2: the workflow explicitly routes portfolio optimization through QAOA after prediction/risk-analysis steps.
    PDF pages 23-24, Table 4 and Figure 4: the comparative results report Sharpe-ratio performance for QAOA on 50-, 100-, and 200-asset portfolios, including a 50-asset portfolio Sharpe ratio of 1.45.
  remediation:
    template: qaoa_proxy
    n_qubits: 12
    notes: |
      Reauthor SP1 as a QAOA portfolio-optimization proxy.

      Recommended circuit structure:
      - Use a truncated Ising portfolio instance with up to 12 qubits, representing a tractable subset of the paper's 50-asset portfolio.
      - Encode portfolio correlations as Z_i Z_j cost terms with coefficients J_ij.
      - Encode asset-level return/risk contributions as Z_i field terms h_i.
      - Use a standard transverse-field X mixer.
      - Implement p=1 or p=2 QAOA layers with explicit gamma and beta parameters.
      - Measure in the computational basis to represent candidate portfolio selections.

      Required metadata fixes:
      - Rename all SP4 references in circuit.py and instance.json to SP1.
      - Replace algorithm_family='quantum-svm' with the repository's QAOA/quantum-optimization bucket if available; otherwise use other-gate-based with an explicit QAOA variant string.
      - Set algorithm_variant_paper to 'QAOA on Ising portfolio-optimization Hamiltonian'.
      - Remove QSVM-specific descriptions from this SP1 artifact.
      - If the project instead chooses QSVM as the canonical experiment, that must be recorded explicitly in the decisions log and the silo/cohort assignment should be changed away from portfolio optimization.
      
```
