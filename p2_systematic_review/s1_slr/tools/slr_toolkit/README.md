# `slr_toolkit/` — SLR toolkit Python package

Reusable modules behind the SLR CLI used during search, dedup, ingest, and AI-assisted screening.

| Module | Role |
|--------|------|
| `cli.py` | Command-line entry point. |
| `api_search.py` | Database adapters (Scopus, Web of Science, IEEE, ACM, arXiv via OpenAlex). |
| `azure_client.py` | Azure OpenAI client used for LLM screening. |
| `config.py` | Toolkit configuration model. |
| `dedup.py` | Cross-database deduplication. |
| `ingest.py` | Normalise raw API records into the unified schema. |
| `llm_screening.py` | LLM-assisted title/abstract screener (drove `../../03_screening/ai_screening_decisions.csv`). |
| `import_zotero_pdfs.py` | Import full-text PDFs from a Zotero library. |
| `institutional_download.py` | Institutional-access PDF download helper. |

Tests: [`../tests/`](../tests/).
