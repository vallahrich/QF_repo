# `s2_classification/prompts/` — Versioned 6-step extraction prompts

Two parallel variants of the same 6-step extraction schedule.

| Step | Canonical | Cached-prefix (production) |
|------|-----------|---------------------------|
| 1 — Classification | `step1_classify.txt` | `cached_step1.txt` |
| 2 — Metadata | `step2_metadata.txt` | `cached_step2.txt` |
| 3 — Methodology | `step3_methodology.txt` | `cached_step3.txt` |
| 4 — Findings | `step4_findings.txt` | `cached_step4.txt` |
| 5 — Limitations | `step5_limitations.txt` | `cached_step5.txt` |
| 6 — Synthesis | `step6_synthesis.txt` | `cached_step6.txt` |

Tag-discovery prompt: `tag_discovery.txt`.

## Production variant

The **cached-prefix** variant was selected by the A/B comparison in [`../../output/ab_test_results/`](../../output/ab_test_results/) and is the one used by `run_classification.py`.

## Provenance

Edits change classification outputs and require GL-01/GL-02 review before re-running on the corpus.
