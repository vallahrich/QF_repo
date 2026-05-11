# `s2_classification/utils/` — Shared classification utilities

Pure-Python helpers shared by the scripts in [`../scripts/`](../scripts/).

| Module | Purpose |
|--------|---------|
| `step_runner.py` | Drives the 6-step extraction sequence with caching, retries, and per-step logging. |
| `frontmatter.py` | Read/write YAML frontmatter on the per-paper Markdown profiles. |
| `processing_log.py` | Append-only JSONL processing log writer. |
| `validation.py` | Schema validation helpers (paired with `tests/test_schema_validation.py`). |
