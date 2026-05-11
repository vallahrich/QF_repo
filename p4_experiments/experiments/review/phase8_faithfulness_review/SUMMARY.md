# Phase 8 Faithfulness Review — Summary

**Cohort:** the 71 Tier-1 cohort labels (Phase 3 majority-viable subset).

## Pass 1 — Phase 3 LLM extraction (GPT 5.3 / GPT 5.4-mini)

Per-paper extraction of algorithm family, algorithm variant, quantitative
resources where reported (including `num_qubits` for 41/71 Tier-1 labels),
problem-instance details, results, classical baselines, and citations. Fields
that P3 S2 did not extract, such as `oracle_structure` and `encoding`, are
treated as Vincent-only review observations rather than Phase-3 disagreements.
Outputs live at `p3_thematic_synthesis/s2_quantitative/output/extractions/<paper_id>.json` (one file per paper; index labels by `experiment_id`).

## Pass 2 — Vincent's faithfulness review

**Reviewer:** Vincent Wallerich  
**Review date:** 2026-04-24  

For each of the 71 labels Vincent read the paper, the Phase 3 extraction,
the implemented `circuit.py`, and `instance.json`, and judged whether the
circuit is a faithful proxy for the paper's algorithm under four checks:
family-faithful, scale-faithful, structurally non-trivial, metadata-consistent.
Per-label review markdowns: `p4_experiments/experiments/review/phase8_faithfulness_review/vincent/<lid>.md`.

### Vincent verdict tally

| Verdict | Count |
|---|---:|
| CONFIRMED | 11 |
| DRIFT_MINOR | 42 |
| DRIFT_MAJOR | 18 |

## Pass 3 — Joint triage

**Reviewers:** Vincent Wallerich + Aleix Telesforo  
**Triage date:** 2026-04-25  

The real joint-triage set contains the labels where Vincent's review contradicts a value that Phase 3 S2 actually extracted (`algorithm.family`, or `num_qubits` when present). This yields 21 joint-triage cases, all now adjudicated. The remaining 39 non-confirmed labels are recorded separately as Vincent-only observations because their concerns involve fields absent from P3 S2 or internal metadata/proxy disclosure.

### Joint decision tally

| Action | Count |
|---|---:|
| reauthor_circuit | 13 |
| demote_label | 4 |
| accept_vincent | 3 |
| no_change | 1 |

### Remediation batches

- **accept_vincent / ansatz_stretch** (3): SQ13, SX5, SX6
- **demote_label / ansatz_stretch** (1): SX7
- **demote_label / classical_nqs_placeholder** (1): SD6
- **demote_label / qft_phase_proxy** (1): SD1
- **demote_label / swap_test_kernel_proxy** (1): SQ8
- **no_change / ansatz_stretch** (1): SQ12
- **reauthor_circuit / hhl_proxy** (7): SQ9, ST1, ST2, SX1, SX2, SX3, SX4
- **reauthor_circuit / lmr_distance_proxy** (1): SQ25
- **reauthor_circuit / qaoa_proxy** (2): SP1, SP2
- **reauthor_circuit / qft_phase_proxy** (1): SD5
- **reauthor_circuit / quantum_svm_kernel_proxy** (1): SQ11
- **reauthor_circuit / swap_test_kernel_proxy** (1): SQ10

Index: `p4_experiments/experiments/review/phase8_faithfulness_review/triage/TRIAGE_INDEX.md`.
Observations: `p4_experiments/experiments/review/phase8_faithfulness_review/observations/OBSERVATIONS_INDEX.md`.
