# `p2_systematic_review/` — freeze record

| Field | Value |
|---|---|
| Freeze date | 2026-05-02 |
| Status | **Frozen** for code/data; manuscript-ready as a documented-limitations classification corpus. |
| Tests | `pytest p2_systematic_review/tests/` — 39 + corpus tests passing |

## Corpus state

| Metric | Value | Authority |
|---|---:|---|
| Included for coding (PRISMA flow) | **777** | [s1_slr/03_screening/included_for_coding.csv](s1_slr/03_screening/included_for_coding.csv) |
| Processed (markdown + JSON) | **777** | [output/processed/*.md](output/processed/) + `*_extraction.json` companions |
| Active downstream subset (post-hoc retro-exclusion) | **755** | 777 minus 22 confirmed off-scope (see [excluded_post_classification.csv](output/audit/excluded_post_classification.csv)) |
| Post-hoc false-positive rate | **22 / 777 ≈ 2.83 %** | [2026-05-02 amendment](s1_slr/01_protocol/amendments/2026-05-02_post_classification_triage.md) |
| Screening recall (LLM vs. 100-record human-coded subset) | **1.000** (Wilson 95 % CI [0.846, 1.000], n=22 inclusions) | [ai_validation_report.md](s1_slr/03_screening/ai_validation_report.md) |
| Screening inter-rater κ (calibration) | **0.692 → 0.849** | [calibration_log.md](s1_slr/03_screening/calibration_log.md) |
| Tag emission (`topic_tags`) | 100 % slug-canonical | [tag_normalization_report.json](output/audit/tag_normalization_report.json) |
| Tag emission (`methodology_tags`) | 99.4 % slug-canonical, 0.6 % PD/SA-code | [tag_normalization_report.json](output/audit/tag_normalization_report.json) |
| Per-step `step{N}_date` audit | 761 sentinel + 9 distinct + 7 incomplete = 777 | [step_date_backfill_report.json](output/audit/step_date_backfill_report.json) |

## What is publication-grade

- **Steps 1–4 of the SLR** (search, deduplication, screening, selection): publication-grade with documented limitations. PRISMA 2020 + PRISMA-S, thesis-supervisor search-strategy peer review (no formal information-specialist/PRESS review), calibrated κ, recall validated on a held-out subset.
- **Steps 5–6 (LLM-assisted classification / extraction)**: defensible **as input to thematic synthesis** with documented limitations (single-LLM single-pass; no inter-coder κ on extraction tags; no `response_format=json_schema` enforcement; 2.83 % off-scope FP rate handled via post-hoc retro-exclusion). Not publication-grade as a standalone classification methodology paper.

## Production vs. legacy code paths

- **Production**: [s2_classification/scripts/run_classification.py](s2_classification/scripts/run_classification.py) (Pipeline C; cached-prefix; parallel; produced all 777 outputs). Per-step `datetime.now()` per writer (fixed 2026-05-02; backfilled to sentinel).
- **Deprecated single-paper diagnostics**: [extract_paper.py](s2_classification/scripts/extract_paper.py) and [run_extraction_step.py](s2_classification/scripts/run_extraction_step.py) carry top-of-file `.. deprecated:: 2026-05-02` banners. Retained because [fetch_from_zotero.py](s2_classification/scripts/fetch_from_zotero.py) shells out to `extract_paper.py`; do not use to (re)produce the corpus.
- **Validation helpers** are now importable from [s2_classification/utils/validation.py](s2_classification/utils/validation.py) (re-exports the canonical implementations from `tests/test_schema_validation.py`).

## Test surface

- [tests/test_schema_validation.py](tests/test_schema_validation.py) — 39 tests; covers `REQUIRED_FIELDS` / `ENUM_RULES` / template integrity. Fixed import + `year` accepts `int|str|None`. `validate_tags` accepts both slug and PD/SA-code forms (case-insensitive); the tolerance is now a citable artifact (see `audit_tag_normalization.py`).
- [tests/test_processed_corpus.py](tests/test_processed_corpus.py) — parameterised over every `output/processed/*.md`. 749 pass, 22 skipped (the retro-excluded papers). Auto-discovered from repo root via the new top-level `pyproject.toml`.

## Reproduce

```powershell
# from repo root
pytest p2_systematic_review/tests/

# regenerate audit reports
python -m p2_systematic_review.s2_classification.scripts.backfill_step_dates
python -m p2_systematic_review.s2_classification.scripts.audit_tag_normalization
```

## Deferred (out of freeze; documented in the manuscript Methods/Limitations)

- **Inter-coder κ on extraction tags.** Would require a 2nd-coder pass (different model or human spot-check) on a 50-paper stratified subsample; bounded LLM cost, not in this freeze.
- **`response_format={"type":"json_schema",...}` enforcement.** Eliminates the silent-truncation failure mode but requires re-running classification over all 777 papers; not in this freeze.
- **Inferred-but-unmeasured scope FN rate.** The 22-paper post-hoc exclusion bounds the FP rate; the FN rate (in-scope papers wrongly excluded at screening) is bounded only by the ai_validation recall (1.000 on n=22) — under-powered.

## Known historical files (not authoritative)

- The root `processing_log.json` was a test artifact and has been removed. Current Phase 2 evidence is the gpt-5-mini per-paper output in `output/processed/`, the audit records in `output/audit/`, and the screening/protocol artifacts under `s1_slr/`.
- `s1_slr/03_screening/archive/` in the source archive holds the `*.bak_20260413_*` snapshots of pre-amendment screening artifacts.
