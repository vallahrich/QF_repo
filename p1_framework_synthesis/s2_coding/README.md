# `s2_coding/` — Phase 1 deductive normalisation outputs

Researcher-curated paper-level review data, built from [`../s1_extractions/`](../s1_extractions/) by [`../scripts/build_review_data_done.py`](../scripts/build_review_data_done.py).

## Contents

| File | Purpose |
|------|---------|
| `review_data_done.json` | Authoritative per-paper review record (inclusion/exclusion, normalised PD/SA codes via `PROBLEM_CODE_MAP` / `SOLUTION_CODE_MAP`). |
| `review_dashboard.html` | Human-browseable rendering of `review_data_done.json` for inspection during Phase 1 review. |
| `_archive/` | Pre-normalisation snapshot — see [`_archive/README.md`](_archive/README.md). |

## Divergence note

Per Divergence Log D-2/D-3 in [`../audit-trail.md`](../audit-trail.md), the intended per-document `_review.json` workflow described in [`../REVIEW_CHECKLIST.md`](../REVIEW_CHECKLIST.md) was collapsed into the single Python pass that produces `review_data_done.json`. There is no per-document JSON in this folder.

## Downstream

Feeds [`../scripts/build_taxonomy.py`](../scripts/build_taxonomy.py) → [`../s3_taxonomy/`](../s3_taxonomy/) and [`../s4_outputs/`](../s4_outputs/).

> See parent [`../README.md`](../README.md) for the active partition disclosure.
