# `tools/` — Repository-level tooling

Repo-level helper scripts that are not bound to a single phase.

| File / folder | Purpose |
|---------------|---------|
| `_print_qa_summary.py` | Print a quick QA summary across recent verifier runs. |
| `aggregate_audits.py` | Aggregate per-phase audit JSONs into a single report. |
| `regen_requirements_lock.ps1` | Regenerate the `requirements.lock` from `pyproject.toml`. |
| `rag/` | Lightweight RAG index over thesis assets (see `rag/README.md`). |
| `verify/` | Cross-phase verifier suite (see `verify/README.md`); outputs land in `verify/reports/`. |

See parent [`../README.md`](../README.md).