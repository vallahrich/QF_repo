# Phase 10 Results Brief

- Cohort: 71 labels across 8 silos: 0 strict-tier estimator labels, 13 family/template labels, 58 proxy labels.
- Faithfulness tiers: {'paper-faithful-strict': 0, 'paper-family-template': 13, 'proxy': 58}. Four strict code specimens exist outside the active estimator grid and have 0 Phase-8 Resource Estimator records.
- H1: accepted triple-condition tests by axis: {'logical_qubits': 0, 't_count': 0, 't_depth': 0, 'runtime_seconds': 0}. Runtime median tau range: {'min': 1.9382716049382713, 'max': 2.0297029702970297}; interpret as template/full-vs-bare overhead, not paper-exact oracle scaling.
- H2: active-P3-silo Kruskal-Wallis p=0.680; MixedLM joint silo p=0.704; label ICC=0.993.
- H3: Friedman p=0.096, Kendall W=0.11; non-runtime axes are structural invariants under the estimator model.
- H4: canonical winners=0 in the family/template implementation cohort; bifurcation holds=True; failure classes={'classical_baseline_too_small_and_not_beaten': 1, 'trivial_oracle_or_no_non_clifford_depth': 12}; QDK-aware nontriviality sensitivity winners=0. Strict-tier H4 statistics are N/A because strict-tier estimator records=0.
- Engine failures: 37 of 2556 canonical Phase 8 records.
- Regimes: headline H1-H4 uses only `canonical_s2_backed_label_grid`; `qae_hhl_fixed_precision_high_n` is appendix-only fixed-precision HHL/QAE scaling evidence.
