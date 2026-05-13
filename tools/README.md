# `tools/` — Repository-level tooling

Repo-level helper scripts that are not bound to a single phase.

| File / folder | Purpose |
|---------------|---------|
| `_print_qa_summary.py` | Print a quick QA summary across recent verifier runs. |
| `aggregate_audits.py` | Aggregate per-phase Phase 4 audit JSONs into a single report. |
| `ch7_new_figs.py`, `ch7_phase8d_table.py`, `ch7_regime_tables.py` | Generate Chapter 7 figures and tables from canonical Phase 4 outputs. |
| `regen_requirements_lock.ps1` | Regenerate the `requirements.lock` from `pyproject.toml`. |
| `verify/` | Cross-phase verifier suite (see `verify/README.md`); outputs land in `verify/reports/`. |

See parent [`../README.md`](../README.md).