# Fair Use, Copyright, and Excluded Materials

This document explains which materials were excluded from the supplementary repository, why, and how an examiner can obtain originals.

## Posture

This repository accompanies an MSc thesis at Copenhagen Business School (CBS), Denmark. It ships the analytical artifacts (codes, themes, classifications, extracted benchmark data, audit trails, configurations, prompts, and reproduction scripts) that the thesis derives from a corpus of academic papers identified by a systematic literature review.

The repository **does not redistribute copyrighted source materials**. It instead ships:

- **DOI / arXiv identifiers** for every paper in the corpus (see [`shared/bridge/paper_id_bridge.csv`](shared/bridge/paper_id_bridge.csv)),
- **Researcher-derived analytical artifacts** that summarise, classify, code, or extract structured information from those papers, and
- **Short verbatim snippets** (titles, metric names, brief descriptive phrases) embedded inside derived JSON records, which we treat as fair use for academic research under Danish copyright law and the EU InfoSoc Directive (2001/29/EC) research-and-teaching exception.

If you are a rights holder and believe a specific snippet exceeds fair use, please contact the authors and we will redact it.

## Excluded materials

### Source PDFs of the SLR corpus

- **777 papers** identified by the Phase 2 SLR are not redistributed.
- The directory [`p2_systematic_review/s1_slr/05_full_texts/pdfs/`](p2_systematic_review/s1_slr/05_full_texts/pdfs/) is intentionally empty (its `README.md` documents the exclusion).
- Use [`p2_systematic_review/s1_slr/05_full_texts/download_log.csv`](p2_systematic_review/s1_slr/05_full_texts/download_log.csv) and the canonical bridge file [`shared/bridge/paper_id_bridge.csv`](shared/bridge/paper_id_bridge.csv) to obtain originals via DOI from your institution.

### Full-text Markdown transcripts

- The plain-text transcripts of corpus papers (one Markdown file per paper, generated for internal LLM ingestion) are not redistributed. The Markdown carries the same copyright posture as the PDF.
- The transcript pipeline scripts and the per-paper extraction log do ship at [`shared/extracted_text/`](shared/extracted_text/), so the procedure is reproducible.

### Phase 1 source PDFs

- The 29 papers used in the Phase 1 inductive framework synthesis are not redistributed.
- The directory [`p1_framework_synthesis/s1_extractions/pdfs/`](p1_framework_synthesis/s1_extractions/pdfs/) is empty (its `README.md` documents the exclusion).
- Per-paper structured extractions (JSON) ship in the parent folder.

### Reference PDFs of the Phase 3 quantum-advantage frameworks

- Source PDFs and full-text Markdown of the seven assessment-framework papers (Rønnow 2014, Babbush 2021, Stilck França 2021, Chakrabarti 2021, Beverland 2022, Dalzell 2023, Hoefler 2023) are not redistributed.
- See [`p3_thematic_synthesis/s3_quantum_advantage/REFERENCE_PDFS_EXCLUDED.md`](p3_thematic_synthesis/s3_quantum_advantage/REFERENCE_PDFS_EXCLUDED.md) for the full citation list.
- The `assess_*.py` scripts that operationalise each framework are shipped in full.

### Other excluded materials (not copyright-related)

- **The thesis manuscript itself** — submitted as the primary deliverable on Digital Exam, not as part of this supplementary archive.
- **Personal review notes, work-in-progress audits, internal review matrices, and design-iteration scaffolding** — not part of the validation surface.
- **Operational caches and bytecode** (`__pycache__/`, vector stores, API response caches) — regenerable from code and configuration.
- **Pre-remediation snapshots and unfiltered raw S3 outputs** — superseded by the canonical `*.filtered.json` outputs in the same folders; the [Artifact Claim Ledger](docs/ARTIFACT_CLAIM_LEDGER.md) explicitly says "do not cite" the unfiltered versions.

## What the repository does ship

| Type | Where | Notes |
|------|-------|-------|
| Per-paper structured extractions | `p1_framework_synthesis/s1_extractions/`, `p2_systematic_review/output/processed/`, `p3_thematic_synthesis/s2_quantitative/output/extractions/` | Researcher-derived classification, frontmatter, and quantitative extraction JSONs. Short text fields (titles, metric names, brief descriptions) appear verbatim. |
| Per-silo thematic codes and memos | `p3_thematic_synthesis/s4_thematic_coding/<silo>/{codes,memos,themes}/` | Researcher-authored codes, paper-level memos, and aggregated themes (B1/B2/C2/C3 stage outputs). |
| Per-silo descriptive briefs | `p3_thematic_synthesis/s6_silo_framing/briefs/<silo>/` | F2 finance-framing brief per silo. |
| Cross-silo synthesis | `p3_thematic_synthesis/s5_cross_silo/` | C1/C2/C3 cross-silo aggregation. |
| Phase 4 experiment cohort and results | `p4_experiments/canonical/`, `p4_experiments/common/output/` | 71-label cohort, 2,556 Phase-8 records, manuscript artefact CSVs and figures. |
| LLM call logs (raw audit trail) | `audit/logs/`, `p3_thematic_synthesis/s6_silo_framing/logs/`, plus stage-local `*.raw_response.txt`, `*.meta.json`, `*_calls.jsonl` | Both researchers' execution sessions, merged where non-overlapping. |
| Prompts (every version) | `p1_framework_synthesis/prompts/`, `p2_systematic_review/s2_classification/prompts/`, `p3_thematic_synthesis/prompts/`, `p4_experiments/prompts/`, `p3_thematic_synthesis/s6_silo_framing/prompts/` | Includes `_v1.txt`, `_v2.txt`, ... and `VERSION_LOG.md` to document iteration. |
| Configurations and taxonomies | `shared/config/`, `shared/bridge/` | Canonical taxonomy v2.0, tier definitions, paper-id bridge. |
| Verifier scripts and dated reports | `tools/verify/` and `tools/verify/reports/` | V1–V9 verifiers + dated drift reports + `known_drift_2026-05.md`. |

## Contact

For questions about included or excluded materials, or to request takedown of a specific snippet, contact the authors via the channels listed on the thesis title page.
