# P4 Shortlist Summary

> Status: legacy precursor artifact. This shortlist explains the P3-to-P4
> selection stage, but it is not the active Phase 8-10 canonical cohort. The
> current source of truth is `p4_experiments/canonical/cohort.json`: 71 labels,
> 0 strict-tier estimator labels, 13 family/template labels, 58 proxy-declared
> labels, 8 silos. Current Phase 8-10 results are in
> `p4_experiments/canonical/reports/evidence_report.json` and
> `p4_experiments/canonical/outputs/manuscript_artifacts/key_numbers.json`.

Generated from the frozen P3 triangulation matrix (1046 rows).

## Tier counts

| Tier | Count |
|------|------:|
| `tier_1_majority_viable_full_coverage` | 71 |
| `tier_1_unanimous_viable` | 1 |
| `tier_2_low_coverage_viable` | 3 |
| `tier_3_high_disagreement` | 41 |
| **Total** | **116** |

## By silo

| Silo | tier_1_majority_viable_full_coverage | tier_1_unanimous_viable | tier_2_low_coverage_viable | tier_3_high_disagreement | Total |
|---|---:|---:|---:|---:|---:|
| cryptography-security | 1 | 0 | 0 | 0 | **1** |
| derivative-pricing | 16 | 0 | 0 | 18 | **34** |
| fraud-detection | 2 | 0 | 0 | 0 | **2** |
| other | 7 | 0 | 0 | 5 | **12** |
| portfolio-optimization | 3 | 0 | 0 | 10 | **13** |
| quantum-ml-finance | 32 | 1 | 3 | 0 | **36** |
| risk-management | 0 | 0 | 0 | 1 | **1** |
| simulation-monte-carlo | 8 | 0 | 0 | 7 | **15** |
| trading-execution | 2 | 0 | 0 | 0 | **2** |

## By algorithm family

| Algorithm | tier_1_majority_viable_full_coverage | tier_1_unanimous_viable | tier_2_low_coverage_viable | tier_3_high_disagreement | Total |
|---|---:|---:|---:|---:|---:|
| amplitude-estimation | 8 | 0 | 0 | 4 | **12** |
| classical-simulation | 2 | 0 | 0 | 1 | **3** |
| grover | 0 | 0 | 0 | 3 | **3** |
| hhl | 7 | 0 | 0 | 6 | **13** |
| hybrid | 1 | 0 | 0 | 1 | **2** |
| other-gate-based | 29 | 1 | 2 | 20 | **52** |
| quantum-ml | 17 | 0 | 1 | 1 | **19** |
| quantum-simulation | 2 | 0 | 0 | 2 | **4** |
| quantum-svm | 4 | 0 | 0 | 0 | **4** |
| quantum-walk | 0 | 0 | 0 | 1 | **1** |
| vqe | 1 | 0 | 0 | 2 | **3** |

## Replication readiness

- Real-QPU experiments: **16/116**
- With circuit parameters (qubits + depth/layers): **25/116**
- With fault-tolerant resource estimate (T-count/T-depth): **4/116**

## Suggested P4 approach

1. **Tier 1** (`tier_1_*`): attempt independent replication via Qiskit simulation and Azure Quantum Resource Estimator. These are the strongest-evidence rows.
2. **Tier 2** (`tier_2_*`): resource-estimate only, no full replication; report hardware requirements under Beverland scenarios.
3. **Tier 3** (`tier_3_high_disagreement`): qualitative case studies — why do frameworks disagree on these specific experiments?
