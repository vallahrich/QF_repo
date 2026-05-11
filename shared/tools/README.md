# `shared/tools/` — Cross-phase Python utilities

| File | Purpose |
|------|---------|
| `_paths.py` | Repo-relative path helpers. |
| `env_loader.py` | `.env` loader for Azure OpenAI credentials. |
| `llm_client.py` | Azure OpenAI client wrapper used by all LLM-driven scripts. |
| `logger.py` | JSONL structured logger (writes to `logs/`). |
| `openalex_client.py` | OpenAlex API client used for bibliometric enrichment. |
| `paper_selector.py` | Cross-phase paper selection helpers. |
| `text_chunker.py` | Text chunking utility for LLM input preparation. |

See parent [`../README.md`](../README.md).