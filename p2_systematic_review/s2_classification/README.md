# `s2_classification/` — Phase 2 extraction & classification pipeline

Production pipeline that turns Phase 2 PDFs into the structured Markdown profiles in [`../output/processed/`](../output/processed/).

## Subdirectories

| Folder | Contents |
|--------|----------|
| `scripts/` | CLI entry points (`extract_paper.py`, `run_classification.py`, `discover_tags.py`, `approve_tags.py`, etc.). See [`scripts/README.md`](scripts/README.md). |
| `prompts/` | Versioned 6-step prompt files (cached-prefix variant + canonical variant). See [`prompts/README.md`](prompts/README.md). |
| `templates/` | `paper_base.md` Markdown template used to render each per-paper profile. See [`templates/README.md`](templates/README.md). |
| `utils/` | Shared helpers (`step_runner`, `frontmatter`, `processing_log`, `validation`). See [`utils/README.md`](utils/README.md). |

## Pipeline reference

The active production pipeline is **Pipeline C — 6-step cached-prefix**, selected via [`../output/ab_test_results/`](../output/ab_test_results/). See parent [`../README.md`](../README.md) for the full step-by-step description.

## Status

Active. Frozen at the 777-paper run — re-runs require GL-01/GL-02 review.
