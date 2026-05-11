# `s2_classification/scripts/` — Phase 2 classification CLI

| Script | Purpose |
|--------|---------|
| `extract_paper.py` | Per-paper extraction driver (single-paper mode). |
| `run_classification.py` | Batch driver that runs `extract_paper.py` over the corpus with the 6-step cached-prefix prompt schedule. **Production entry point.** |
| `extract_pdf_text.py` | PDF → plain text extraction helper used upstream of the LLM calls. |
| `discover_tags.py` | Surface candidate new tags from a batch of extractions for human review. |
| `approve_tags.py` | Promote approved candidate tags into [`shared/config/unified_taxonomy.json`](../../../shared/config/unified_taxonomy.json). |
| `audit_tag_normalization.py` | Generate `output/audit/tag_normalization_report.json`. |
| `backfill_step_dates.py` | One-off retro-fill of missing per-step extraction dates. |
| `fetch_from_zotero.py` / `push_tags_to_zotero.py` | Sync helpers between the corpus and the Zotero library. |

> See parent [`../README.md`](../README.md) for the controlling pipeline definition.
