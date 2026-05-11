# Phase 2 — Systematic Identification & Classification

**Objective:** Systematically identify, screen, and classify the relevant corpus of literature on quantum computation in finance using the framework developed in Phase 1.

**Methodological basis:** Systematic literature review protocol (Kitchenham & Charters, 2007; Tranfield, Denyer & Smart, 2003).

## Analytical Movement

**Deductive** — The Phase 1 framework is applied top-down to systematically classify the full corpus. Categories that were inductively derived are now treated as fixed and applied mechanically.

## Process

1. **Search**: Define search strings and execute across the four production sources (Scopus, OpenAlex, Semantic Scholar, arXiv). Web of Science was considered during protocol development and dropped after API testing; this is documented in the search peer-review log.
2. **Deduplication**: Remove duplicate records across databases.
3. **Screening**: Apply inclusion/exclusion criteria through title/abstract screening, followed by full-text screening.
4. **Selection**: Finalise the included corpus (~900 papers).
5. **Classification**: Apply structured deductive coding against the Phase 1 framework — tag each paper with problem space(s), solution space(s), and extract metadata profiles.
6. **Clustering**: Group papers into problem space silos for Phase 3 analysis.

**Status (refreshed 2026-05-02):** SLR (steps 1–4) **complete**; classification pipeline (steps 5–6) **executed** — 777 papers under [`output/processed/`](output/processed/), each as a structured Markdown + `_extraction.json` companion. A post-hoc scope triage on 2026-04 surfaced 22 confirmed-off-scope papers; these are formally excluded by [`s1_slr/01_protocol/amendments/2026-05-02_post_classification_triage.md`](s1_slr/01_protocol/amendments/2026-05-02_post_classification_triage.md) with the explicit list in [`output/audit/excluded_post_classification.csv`](output/audit/excluded_post_classification.csv). The active downstream P3 baseline already reflects these exclusions (777 → 501 extractions; see `p3_thematic_synthesis/s2_quantitative/output/audit/corpus_lineage.json`).

## Folder Structure

```
p2_systematic_review/
├── README.md                # This file
├── s1_slr/                  # Complete SLR data (inlined from quantum-finance-slr)
│   ├── 01_protocol/         # SLR protocol, amendments, PRISMA checklists
│   ├── 02_search_logs/      # Search peer review, snowball log
│   ├── 04_deduped_library/  # Deduplicated records
│   ├── 05_screening/        # Screening decisions, calibration, validation
│   ├── 06_figures/          # PRISMA flow, charts
│   ├── 07_full_texts/       # Download log, missing PDFs
│   └── tools/slr_toolkit/   # SLR CLI and modules
├── s2_classification/       # Extraction + classification (merged pipeline)
│   ├── scripts/             # extract_paper.py, run_extraction_step.py, discover_tags.py, approve_tags.py
│   ├── utils/               # step_runner, frontmatter, processing_log
│   ├── prompts/             # step1_classify.txt – step6_synthesis.txt, tag_discovery.txt
│   └── templates/           # paper_base.md template
├── output/                  # All outputs
│   ├── raw_pdfs/            # Downloaded PDFs
│   └── processed/           # One structured .md per paper
└── tests/
```

## Expected Outputs

- PRISMA flow diagram documenting the search and screening process.
- Complete classified corpus with problem/solution space tags and metadata.
- Descriptive bibliometric overview (publication trends, venue distribution).
- Document clusters (silos) defined by problem space, ready for Phase 3.

## Usage

```bash
# From the project root (quantum-finance/)

# === Production pipeline used to generate the 777 outputs (Pipeline C) ===
# Batch 6-step cached-prefix classification with parallel workers.
# This is the script that actually produced output/processed/*.md.
python -m p2_systematic_review.s2_classification.scripts.run_classification --parallel 8

# Process a single paper (Pipeline C)
python -m p2_systematic_review.s2_classification.scripts.run_classification \
    --paper-id 0067a26ce270

# === Legacy / single-paper diagnostic path (NOT used to produce the corpus) ===
# extract_paper.py and run_extraction_step.py orchestrate via
# s2_classification/utils/step_runner.py. They use the per-step prompts
# step{1..6}_*.txt rather than the cached_step{1..5}.txt + step6_synthesis.txt
# pair used by run_classification.py. Useful for re-running a single step on
# a single paper for debugging; do not use for the production corpus.
python -m p2_systematic_review.s2_classification.scripts.extract_paper \
    --pdf p2_systematic_review/output/raw_pdfs/paper.pdf \
    --name 2024_Author_Title.md
python -m p2_systematic_review.s2_classification.scripts.run_extraction_step \
    --paper 2024_Author_Title.md --step 3

# Validate the processed corpus against the schema
pytest p2_systematic_review/tests/test_schema_validation.py
pytest p2_systematic_review/tests/test_processed_corpus.py
```

## Methods & limitations (read this before citing any classification number)

- **Screening** is publication-grade with documented limitations: PRISMA 2020 + PRISMA-S checklists; thesis-supervisor search-strategy peer review (no formal information-specialist/PRESS review); calibrated
  inter-rater reliability **κ = 0.692 → 0.849** ([s1_slr/03_screening/calibration_log.md](s1_slr/03_screening/calibration_log.md));
  LLM-assisted screening validated against a 100-record human-coded held-out subset
  ([s1_slr/03_screening/ai_validation_report.md](s1_slr/03_screening/ai_validation_report.md)) at
  **recall = 1.000, Wilson 95% CI [0.846, 1.000]** (n=22 inclusions; CI lower bound from k=n=22, z=1.96).
- **Classification (steps 1–6)** is a **single-LLM, single-pass deductive coding** by `gpt-5-mini` via
  [s2_classification/scripts/run_classification.py](s2_classification/scripts/run_classification.py).
  There is **no inter-coder κ** on extraction tags, no second-coder validation, and no structured-output
  schema enforcement (only `"respond ONLY with valid JSON"` in prompts).
- **Post-hoc false-positive rate.** A scope triage in 2026-04 surfaced **≥ 22 of 777 confirmed off-scope
  inclusions (≈ 2.83 %)**; these are formally excluded by the
  [2026-05-02 amendment](s1_slr/01_protocol/amendments/2026-05-02_post_classification_triage.md) and
  enumerated in [output/audit/excluded_post_classification.csv](output/audit/excluded_post_classification.csv).
  Downstream consumers (P3 / P4) operate on the 755-paper active subset.
- **Audit trail caveat (2026-05-02 fix).** Earlier runs of `run_classification.py` wrote a single shared
  `now` timestamp to all six `step{N}_date` frontmatter fields, so per-step dates in pre-2026-05-02
  outputs are **not granular**. The backfill script reclassified every paper into one of five buckets
  and wrote them to a sentinel where appropriate; **761 papers** had identical synthetic timestamps
  rewritten to `unknown_pre_2026-05-02`, **9** papers had genuinely distinct per-step timestamps
  (post-fix runs) and were left untouched, **7** papers have incomplete `step{N}_date` frontmatter
  (extraction did not complete all six steps). Total: 761 + 9 + 7 = 777. See
  [output/audit/step_date_backfill_report.json](output/audit/step_date_backfill_report.json).
- **Tag-emission tolerance.** The corpus contains tags emitted in two forms: slug
  ("portfolio-optimization") and PD-/SA- code ("PD-01" / "sa-03"), case-insensitive. The validators
  in `tests/` accept both because the mapping is unambiguous; the audit script
  [s2_classification/scripts/audit_tag_normalization.py](s2_classification/scripts/audit_tag_normalization.py)
  counts how many tags use each form and writes the result to
  [output/audit/tag_normalization_report.json](output/audit/tag_normalization_report.json) so
  downstream consumers (and the manuscript methods chapter) can cite an explicit number rather than
  relying on implicit validator behaviour.


## Dependencies

- `shared/tools/llm_client.py` — Azure OpenAI calls
- `shared/tools/env_loader.py` — .env loading
- `shared/config/extraction_config.json` — per-step LLM settings
- `shared/config/unified_taxonomy.json` — tag definitions

## Handoff to Phase 3

Phase 3 reads:
- `output/processed/*.md` — structured paper markdown
- Tier/topic classification data
- Problem space silo assignments
