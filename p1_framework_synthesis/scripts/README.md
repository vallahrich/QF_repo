# `scripts/` — Phase 1 pipeline scripts

Python entry points for the Phase 1 LLM-assisted extraction and deductive-normalisation pipeline.

## Contents

| Script | Purpose |
|--------|---------|
| `extract_document.py` | Run the LLM extraction prompt over a single PDF → `s1_extractions/<stem>.json`. |
| `build_review_data_done.py` | Apply `PROBLEM_CODE_MAP` / `SOLUTION_CODE_MAP` regex normalisation + `EXCLUSIONS` / `NEEDS_RECHECK` / `HIGH_RELEVANCE` paper-level decisions → `s2_coding/review_data_done.json`. **The active per-paper triage authority for Phase 1.** |
| `build_review_workbook.py` | Render `review_data_done.json` → `s2_coding/review_dashboard.html` for human inspection. |
| `build_taxonomy.py` | Aggregate normalised codes → taxonomy artifacts in `s3_taxonomy/`. |
| `build_references.py` | Generate BibTeX entries for the Phase 1 corpus. |

## Status

Frozen as a pipeline. Edits to the regex maps inside `build_review_data_done.py` re-shape Phase 1 outputs and require GL-01 review.

> See parent [`../README.md`](../README.md) for the controlling methodology and divergence log.
