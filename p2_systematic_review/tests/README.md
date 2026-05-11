# `tests/` — Phase 2 corpus-level tests

| File | Purpose |
|------|---------|
| `test_processed_corpus.py` | Whole-corpus invariants over [`../output/processed/`](../output/processed/) (file pairing, frontmatter validity, tag coverage). |
| `test_schema_validation.py` | Per-paper `_extraction.json` schema validation. |

Run with `pytest p2_systematic_review/tests/`.
