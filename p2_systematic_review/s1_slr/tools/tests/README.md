# `tools/tests/` — SLR toolkit tests

Pytest suite for [`../slr_toolkit/`](../slr_toolkit/). Run from the repo root:

```bash
pytest p2_systematic_review/s1_slr/tools/tests/
```

| Test | Subject |
|------|---------|
| `test_ai_screening.py` | LLM screening logic in `llm_screening.py`. |
| `test_dedup.py` | Cross-database dedup. |
| `test_ingest_smoke.py` | End-to-end ingest smoke test. |
| `test_institutional_download.py` | Institutional-access download flow. |
| `test_llm_screening.py` | LLM screening integration. |
| `test_no_duplicates.py` | Invariant: no duplicate IDs in the deduplicated dataset. |
| `test_query_builder.py` | Query string construction. |
| `test_search_run.py` | End-to-end search-run smoke test. |
