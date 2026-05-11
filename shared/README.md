# `shared/` — Cross-phase shared assets

Code and configuration shared across all four phases of the thesis pipeline.
Treat this folder as the single canonical source for taxonomy, paper IDs, LLM
plumbing, and per-phase derived inputs.

| Subfolder | Purpose |
|-----------|---------|
| `bridge/` | `paper_id_bridge.csv` — canonical mapping between SLR paper_id hashes, DOIs, and Zotero item keys. |
| `chapter_supporting_literature/` | Researcher-curated supporting literature notes used by manuscript chapters. |
| `config/` | Taxonomy, tier definitions, extraction config (and JSON schemas). **The single source of taxonomy codes (PD-/SA-).** |
| `extracted_text/` | Per-paper extracted text used as input to P2/P3/P4 LLM steps. |
| `phase3/` | P3-derived shared assets (bibliometric summaries, inclusion lists, text-readiness reports). |
| `tests/` | Tests for shared utilities. |
| `tools/` | Cross-phase Python tools (LLM client, env loader, logger, paper selector, text chunker, OpenAlex client). |
| `validate_taxonomy.py` | Validator for `config/unified_taxonomy.json`. |
| `FREEZE.md` | Freeze status of shared assets. |

> Authoritative status lives in [`../docs/PROJECT_STATE.yaml`](../docs/PROJECT_STATE.yaml);
> repository structure narrative in [`../docs/ARCHITECTURE.md`](../docs/ARCHITECTURE.md).