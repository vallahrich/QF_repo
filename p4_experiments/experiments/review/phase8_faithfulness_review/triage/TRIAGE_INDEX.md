# Triage Index — Completed Joint Decisions

**Joint reviewers:** Vincent Wallerich + Aleix Telesforo  
**Triage date:** 2026-04-25  

Scope: the 71 Tier-1 cohort labels.

A label enters joint triage only if Vincent's review contradicts a value Phase 3 S2 actually extracted: `algorithm.family`, or `num_qubits` when S2 recorded it. Labels whose concerns are only about fields absent from S2 remain in `observations/`.

**Joint-triage cases completed:** 21 of 21
**Vincent-only observations:** 39 of 71
**CONFIRMED (no review work needed):** 11 of 71

## Decision Tally

| Action | Count |
|---|---:|
| reauthor_circuit | 13 |
| demote_label | 4 |
| accept_vincent | 3 |
| no_change | 1 |

| Winner | Count |
|---|---:|
| vincent | 17 |
| merge | 4 |

## Completed Joint-Triage Worksheets

| # | Label | Winner | Action | Template | n_qubits | Paper | Exp | Silo | Worksheet |
|---:|---|---|---|---|---|---|---|---|---|
| 1 | **SD1** | vincent | demote_label | qft_phase_proxy | 9 | `0608ad48d5b8` | exp_1 | derivative-pricing | [SD1.md](SD1.md) |
| 2 | **SD6** | vincent | demote_label | classical_nqs_placeholder | NOT_APPLICABLE | `439a750eda8c` | exp_1 | derivative-pricing | [SD6.md](SD6.md) |
| 3 | **SQ8** | merge | demote_label | swap_test_kernel_proxy | 5 | `53a718c11ea8` | exp_1 | quantum-ml-finance | [SQ8.md](SQ8.md) |
| 4 | **SX7** | vincent | demote_label | ansatz_stretch | 5 | `a2b747cae698` | exp_3 | other | [SX7.md](SX7.md) |
| 5 | **SD5** | vincent | reauthor_circuit | qft_phase_proxy | 9 | `349c85ac46df` | exp_1 | derivative-pricing | [SD5.md](SD5.md) |
| 6 | **SP1** | vincent | reauthor_circuit | qaoa_proxy | 12 | `378c2a73ea46` | exp_1 | portfolio-optimization | [SP1.md](SP1.md) |
| 7 | **SP2** | merge | reauthor_circuit | qaoa_proxy | 12 | `378c2a73ea46` | exp_3 | portfolio-optimization | [SP2.md](SP2.md) |
| 8 | **SQ10** | merge | reauthor_circuit | swap_test_kernel_proxy | 5 | `53a718c11ea8` | exp_3 | quantum-ml-finance | [SQ10.md](SQ10.md) |
| 9 | **SQ11** | merge | reauthor_circuit | quantum_svm_kernel_proxy | 5 | `53a718c11ea8` | exp_4 | quantum-ml-finance | [SQ11.md](SQ11.md) |
| 10 | **SQ25** | vincent | reauthor_circuit | lmr_distance_proxy | 2 | `c99a158445ec` | exp_1 | quantum-ml-finance | [SQ25.md](SQ25.md) |
| 11 | **SQ9** | vincent | reauthor_circuit | hhl_proxy | 5 | `53a718c11ea8` | exp_2 | quantum-ml-finance | [SQ9.md](SQ9.md) |
| 12 | **ST1** | vincent | reauthor_circuit | hhl_proxy | 6 | `3adb18321a79` | exp_1 | trading-execution | [ST1.md](ST1.md) |
| 13 | **ST2** | vincent | reauthor_circuit | hhl_proxy | 6 | `3adb18321a79` | exp_2 | trading-execution | [ST2.md](ST2.md) |
| 14 | **SX1** | vincent | reauthor_circuit | hhl_proxy | 4 | `7cfdb2957f6c` | exp_1 | other | [SX1.md](SX1.md) |
| 15 | **SX2** | vincent | reauthor_circuit | hhl_proxy | 7 | `7cfdb2957f6c` | exp_2 | other | [SX2.md](SX2.md) |
| 16 | **SX3** | vincent | reauthor_circuit | hhl_proxy | 7 | `7cfdb2957f6c` | exp_3 | other | [SX3.md](SX3.md) |
| 17 | **SX4** | vincent | reauthor_circuit | hhl_proxy | 7 | `7cfdb2957f6c` | exp_4 | other | [SX4.md](SX4.md) |
| 18 | **SQ13** | vincent | accept_vincent | ansatz_stretch | 5 | `59cca9744140` | exp_1 | quantum-ml-finance | [SQ13.md](SQ13.md) |
| 19 | **SX5** | vincent | accept_vincent | ansatz_stretch | 5 | `a2b747cae698` | exp_1 | other | [SX5.md](SX5.md) |
| 20 | **SX6** | vincent | accept_vincent | ansatz_stretch | 5 | `a2b747cae698` | exp_2 | other | [SX6.md](SX6.md) |
| 21 | **SQ12** | vincent | no_change | ansatz_stretch | 5 | `5413b7728054` | exp_1 | quantum-ml-finance | [SQ12.md](SQ12.md) |

## Remediation Batches

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
