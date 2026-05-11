# `output/audit/` — Phase 2 audit artifacts

Cross-paper audit reports generated after the main classification run.

| File | Purpose |
|------|---------|
| `triage_classification.json` | Post-classification quantitative triage ledger for 63 candidate-defective papers; kept here as Phase 2 audit provenance and referenced by `p4_experiments/canonical/cohort.json`. |
| `excluded_post_classification.csv` | 22 papers formally excluded by the 2026-05-02 post-classification triage amendment (see [`../../s1_slr/01_protocol/amendments/2026-05-02_post_classification_triage.md`](../../s1_slr/01_protocol/amendments/2026-05-02_post_classification_triage.md)). |
| `step_date_backfill_report.json` | Audit log of the 2026-04 backfill that filled missing per-step extraction dates in `processed/*_extraction.json`. |
| `tag_normalization_report.json` | Audit log of tag normalisation against [`shared/config/unified_taxonomy.json`](../../../shared/config/unified_taxonomy.json). |

> See [`../README.md`](../README.md) for the output namespace overview.
