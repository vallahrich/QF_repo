# `05_full_texts/pdfs/` — Full-text PDFs (EXCLUDED FROM SUBMISSION)

The full-text PDFs of the 777-paper SLR corpus are **not distributed** with this submission repository due to publisher copyright restrictions.

## How to obtain the original papers

The download log lists every paper with its DOI and source URL:

- [`../download_log.csv`](../download_log.csv) — one row per paper (paper_id, DOI, title, source, download status)
- [`../missing_pdfs.csv`](../missing_pdfs.csv) — papers we could not retrieve at SLR time
- [`../../../../shared/bridge/paper_id_bridge.csv`](../../../../shared/bridge/paper_id_bridge.csv) — canonical mapping `paper_id ↔ DOI ↔ Zotero key` for the entire corpus

The original filename convention was `<paper_id>_<slugified_title>.pdf`, where `<paper_id>` is the 12-hex-char hash used throughout the pipeline.

## What ships in lieu of the PDFs

The downstream artifacts derived from these PDFs ship in full:

- Per-paper extracted text snippets — [`shared/extracted_text/`](../../../../shared/extracted_text/)
- Phase 2 classification frontmatter (one JSON per paper) — [`../../../output/processed/`](../../../output/processed/)
- Phase 3 quantitative extractions — [`../../../../p3_thematic_synthesis/s2_quantitative/output/extractions/`](../../../../p3_thematic_synthesis/s2_quantitative/output/extractions/)
- Phase 3 thematic codes & memos — [`../../../../p3_thematic_synthesis/s4_thematic_coding/`](../../../../p3_thematic_synthesis/s4_thematic_coding/)

See the project root [`FAIR_USE.md`](../../../../FAIR_USE.md) for the rationale on the snippet-vs-PDF split.

## Cross-references

- SLR pipeline: [`../README.md`](../README.md), [`../../README.md`](../../README.md)
- Manuscript: Annex L (Repository Structure) and §5 (Phase 2 SLR)
