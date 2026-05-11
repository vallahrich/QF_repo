# P3 S2 Corpus Lineage

Generated UTC: `2026-04-28T18:44:06.899050+00:00`

## Current Active Corpus

- P2 processed records: 777
- Current exclusion rows: 276
- Active S2 extraction files: 501
- Active S2 experiments: 1046
- Lineage equation: 777 P2 records - 276 current exclusions = 501 active extraction files
- Validation files: {'False': 36, 'True': 465}
- Validation experiments: {'False': 84, 'True': 962}

## Current Exclusion Reasons

| Reason | Papers |
|---|---:|
| no_quantitative_results | 130 |
| scope_out | 146 |

## Historical Checkpoints

| Checkpoint | Papers | Experiments | Interpretation | Source |
|---|---:|---:|---|---|
| pre_q0_audit_historical | 643 | 1957 | Historical pre-repair audit state; includes annealing/QUBO leakage and is not the active corpus. | p3_thematic_synthesis/AUDIT_REPORT.md |
| s3_freeze_2026_04_17_historical | 459 | 1185 | Historical S3 freeze state from 2026-04-17; superseded by the active S2 directory. | p3_thematic_synthesis/s3_quantum_advantage/FROZEN.md |
| current_active_s2_2026_04_28 | 501 | 1046 | Current active S2 quantitative extraction corpus. | p3_thematic_synthesis/s2_quantitative/output/extractions/ |

## Previous Exclusion CSV Before Regeneration

- Rows in active exclusion CSV before this run: 276
- Reason counts in active exclusion CSV before this run: {'no_quantitative_results': 130, 'scope_out': 146}
- Historical archive rows: 318
- Historical archive reason counts: {'no_quantitative_results': 130, 'scope_out': 146, 'scope_out_no_quantum': 1, 'scope_out_non_finance': 16, 'scope_out_physics': 9, 'scope_out_position_paper': 6, 'scope_out_quantum_inspired': 2, 'scope_out_survey': 8}
- Historical archive implied active papers: 459
- Previous-excluded IDs now active: 42
- Historical archive: p3_thematic_synthesis/s2_quantitative/output/audit/excluded_papers_historical_2026-04-17.csv

## Consistency Checks

- Expected active set matches extraction directory: True
- Active extractions missing from P2: 0
- P2 records missing extracted text: 0
- Extracted text records missing P2: 0
- Scope-audit hard violations: 0
- Scope-audit validation-failed files: 36

Current claim boundary: the 643-paper and 459-paper counts are historical checkpoints, not the active S2 quantitative corpus. The active corpus is the 501-file extraction directory summarized above.
