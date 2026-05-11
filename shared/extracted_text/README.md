# `shared/extracted_text/` — Extraction metadata and scripts

This cleanup/submission copy retains the extraction scripts and metadata, but
does not redistribute verbatim full-text Markdown extracted from source-paper
PDFs.

| Subfolder | Purpose |
|-----------|---------|
| `src/` | Extraction scripts (`extract.py`, `ocr_extract.py`). |
| `extraction_log.csv` | Extraction metadata retained so researchers with local access to the original PDFs can reproduce the extraction step. |
| `text/` | Removed from this cleanup/submission copy; contained verbatim full-text Markdown extracted from source PDFs. |
| `excluded_non_english/` | Removed from this cleanup/submission copy; contained verbatim Markdown for quarantined non-English papers. |

The removed text can be regenerated locally from the original PDFs using the
scripts under `src/` if redistribution rights and local source access permit.

See parent [`../README.md`](../README.md).