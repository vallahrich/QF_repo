# Vincent-only observations

**Reviewer:** Vincent Wallerich  
**Date:** 2026-04-25  

These are labels where Vincent's review flagged a concern, but the failing
checks concern fields the Phase 3 S2 quantitative extraction did not record
(`oracle_structure`, `encoding`, internal cohort/instance metadata consistency,
or `num_qubits` where Phase 3 S2 left it blank). There is no Phase 3 value to
adjudicate against — these are Vincent's structural observations from reading
the paper and circuit directly, recorded for the audit trail without joint
triage.

**Total observations:** 39 of 71

| # | Label | Vincent verdict | Failing checks | Paper | Exp | Silo |
|---:|---|---|---|---|---|---|
| 1 | **SP3** | DRIFT_MAJOR | structure; metadata | `de580e8c085e` | exp_1 | portfolio-optimization |
| 2 | **SQ1** | DRIFT_MAJOR | structure; metadata | `14777484b99d` | exp_1 | quantum-ml-finance |
| 3 | **SD12** | DRIFT_MINOR | metadata | `cb8d976cb90c` | exp_1 | derivative-pricing |
| 4 | **SD13** | DRIFT_MINOR | metadata | `cb8d976cb90c` | exp_2 | derivative-pricing |
| 5 | **SD14** | DRIFT_MINOR | metadata | `d429e0713a3d` | exp_3 | derivative-pricing |
| 6 | **SD2** | DRIFT_MINOR | structure; metadata | `081132e62980` | exp_1 | derivative-pricing |
| 7 | **SD3** | DRIFT_MINOR |  | `1bf880322e6f` | exp_5 | derivative-pricing |
| 8 | **SD4** | DRIFT_MINOR | metadata | `1d44742c9e15` | exp_1 | derivative-pricing |
| 9 | **SD7** | DRIFT_MINOR | scale (P3 silent on n_qubits: True); metadata | `439a750eda8c` | exp_2 | derivative-pricing |
| 10 | **SD9** | DRIFT_MINOR | structure | `872cedb13e27` | exp_1 | derivative-pricing |
| 11 | **SF2** | DRIFT_MINOR | metadata | `8fec8d839e47` | exp_1 | fraud-detection |
| 12 | **SM1** | DRIFT_MINOR | metadata | `48cd8220e3b2` | exp_1 | simulation-monte-carlo |
| 13 | **SM2** | DRIFT_MINOR | metadata | `623597ee0f9c` | exp_1 | simulation-monte-carlo |
| 14 | **SM3** | DRIFT_MINOR | structure; metadata | `646bd6bbd935` | exp_1 | simulation-monte-carlo |
| 15 | **SM4** | DRIFT_MINOR | metadata | `75a7b04fa681` | exp_3 | simulation-monte-carlo |
| 16 | **SM5** | DRIFT_MINOR | metadata | `8f553bfb1077` | exp_1 | simulation-monte-carlo |
| 17 | **SM6** | DRIFT_MINOR | metadata | `8f553bfb1077` | exp_2 | simulation-monte-carlo |
| 18 | **SM7** | DRIFT_MINOR | metadata | `8f553bfb1077` | exp_3 | simulation-monte-carlo |
| 19 | **SM8** | DRIFT_MINOR | metadata | `e922f913e80b` | exp_1 | simulation-monte-carlo |
| 20 | **SQ15** | DRIFT_MINOR | metadata | `75eee58caf3a` | exp_4 | quantum-ml-finance |
| 21 | **SQ16** | DRIFT_MINOR | structure; metadata | `7eefd96d7f06` | exp_3 | quantum-ml-finance |
| 22 | **SQ17** | DRIFT_MINOR | metadata | `7eefd96d7f06` | exp_4 | quantum-ml-finance |
| 23 | **SQ18** | DRIFT_MINOR | metadata | `86891f250a78` | exp_2 | quantum-ml-finance |
| 24 | **SQ2** | DRIFT_MINOR | metadata | `26d9ab80fc82` | exp_1 | quantum-ml-finance |
| 25 | **SQ20** | DRIFT_MINOR | metadata | `b3543c214d69` | exp_2 | quantum-ml-finance |
| 26 | **SQ21** | DRIFT_MINOR | structure | `c48c60134357` | exp_1 | quantum-ml-finance |
| 27 | **SQ22** | DRIFT_MINOR | structure | `c48c60134357` | exp_2 | quantum-ml-finance |
| 28 | **SQ23** | DRIFT_MINOR | metadata | `c48c60134357` | exp_3 | quantum-ml-finance |
| 29 | **SQ26** | DRIFT_MINOR | metadata | `f94276561f48` | exp_1 | quantum-ml-finance |
| 30 | **SQ27** | DRIFT_MINOR | metadata | `f94276561f48` | exp_2 | quantum-ml-finance |
| 31 | **SQ29** | DRIFT_MINOR |  | `f94276561f48` | exp_4 | quantum-ml-finance |
| 32 | **SQ3** | DRIFT_MINOR | metadata | `2a0770a1a995` | exp_1 | quantum-ml-finance |
| 33 | **SQ30** | DRIFT_MINOR | metadata | `f94276561f48` | exp_5 | quantum-ml-finance |
| 34 | **SQ32** | DRIFT_MINOR | metadata | `f94276561f48` | exp_7 | quantum-ml-finance |
| 35 | **SQ4** | DRIFT_MINOR | metadata | `2a0770a1a995` | exp_2 | quantum-ml-finance |
| 36 | **SQ5** | DRIFT_MINOR | metadata | `2a0770a1a995` | exp_3 | quantum-ml-finance |
| 37 | **SQ6** | DRIFT_MINOR | structure; metadata | `2a9cd8a96604` | exp_1 | quantum-ml-finance |
| 38 | **SQ7** | DRIFT_MINOR | metadata | `2fe0d0f15604` | exp_1 | quantum-ml-finance |
| 39 | **SX8** | DRIFT_MINOR |  | `cd9329dc38ef` | exp_3 | cryptography-security |
