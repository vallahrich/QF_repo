# Discussion Claims Evidence Matrix

## P4-COMPLETE-AUDITABLE
The canonical P4 resource-estimation grid is complete and suitable for downstream statistical reporting.

Evidence: evidence_report.json:engine_failures; audit_phase8.json; stats_report.json
Use: Methods/Results completeness paragraph and limitations disclosure

## H1-NO-ORDER-MAGNITUDE-ORACLE-TAX
The legacy Faithful cohort does not support the pre-registered claim that median full-vs-bare oracle tax exceeds 10x across the grid; the observed runtime tau range is consistent with small template/oracle overhead rather than paper-exact oracle scaling.

Evidence: table_h1_full_matrix.tex; figure_h1_heatmap.csv; stats_report.json:H1
Use: Results H1 subsection

## H2-NO-ROBUST-SILO-SEPARATION
Application silo does not explain a statistically robust separation in anchor-cell runtime oracle tax.

Evidence: table_h2_silo_effects.tex; stats_report.json:H2
Use: Results H2 subsection and Discussion methodological caveat

## H3-RUNTIME-ONLY-PROFILE-EFFECT
Hardware profile is meaningful for runtime but non-runtime logical axes are structural invariants under the estimator model.

Evidence: table_h3_profile_ordering.tex; stats_report.json:H3; figure_h3_runtime_ecdf.png
Use: Results H3 subsection and methods block on structural invariants

## H4-EMPTY-STRICT-SUBSET
No legacy Faithful label satisfies all five strict-H4 criteria. The observed bifurcation is transparent but partly structural under the current template/family-faithful implementations, so it is evidence about this cohort and implementation model rather than a field-wide no-advantage theorem.

Evidence: table_h4_scoreboard.tex; table_h4_failure_taxonomy.tex; figure_h4_funnel.csv; stats_report.json:H4
Use: Headline Results and Discussion contribution

## F-TIER-NOT-PAPER-EXACT
The legacy Faithful set is not equivalent to a paper-exact implementation set; the strict paper-faithful tier is empty under the current audit layer, and the existing H4 headline should be interpreted as a template/family-faithful result.

Evidence: stats_report.json:H4.faithfulness_tier_sensitivity; evidence_report.json:faithfulness_tiers; audit_phase4_faithfulness.json
Use: Methods faithfulness taxonomy, Results faithfulness-yield paragraph, and limitations framing

## PHASE8D-APPENDIX-ONLY
Fixed-precision QAE/HHL Phase 8d results are a separate appendix-only experiment regime and must not mutate headline H1-H4 claims.

Evidence: evidence_report.json:experiment_regimes; table_experiment_regimes.tex; table_phase8d_regime_summary.tex; key_numbers.json:phase8d_qae_hhl; audit_phase8d.json
Use: Appendix scaling and limitations after salvage sync completes
