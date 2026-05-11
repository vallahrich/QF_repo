# `output/` — Phase 2 corpus outputs

All generated outputs from the Phase 2 SLR + classification pipeline.

## Subdirectories

| Folder | Contents |
|--------|----------|
| `processed/` | Final per-paper artifacts (777 papers): one `<paper_id>.md` Markdown profile + `<paper_id>_extraction.json` companion. The canonical Phase 2 deliverable consumed downstream by Phase 3. See [`processed/README.md`](processed/README.md). |
| `audit/` | Cross-paper audit artifacts (post-classification triage exclusions, step-date backfill report, tag normalisation report). See [`audit/README.md`](audit/README.md). |
| `ab_test_results/` | A/B comparisons used to select the production extraction pipeline (Pipeline C — 6-step cached-prefix). See [`ab_test_results/README.md`](ab_test_results/README.md). |

## Status

Active. The 777 baseline minus 22 post-classification exclusions = effective 755 papers, formalised in [`s1_slr/01_protocol/amendments/2026-05-02_post_classification_triage.md`](../s1_slr/01_protocol/amendments/2026-05-02_post_classification_triage.md).

> See parent [`../README.md`](../README.md) for the controlling pipeline description.
