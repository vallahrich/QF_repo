# `shared/config/` — Canonical configuration

| File | Purpose |
|------|---------|
| `unified_taxonomy.json` | **Single tag registry** (PD-01..PD-09, SA-01..SA-11) used across all phases. |
| `extraction_config.json` | Per-step LLM settings for the P2 extraction pipeline. |
| `silo_inclusion.json` | Per-silo inclusion lists for Phase 3. |
| `source_types.json` | Source-type taxonomy for bibliometric reporting. |
| `tier_definitions.json` | Tier definitions for paper-level claim strength. |
| `zotero_collection_map.json` | Mapping from Zotero collection keys to taxonomy slugs. |
| `schemas/` | JSON Schemas validating each of the configs above. |
| `_archive/` | Historical config snapshots (e.g., `unified_taxonomy_v1_backup.json`). |

Modifying any of these files has cross-phase impact — see the cross-phase
guard rules in [`../../.github/copilot-instructions.md`](../../.github/copilot-instructions.md).

See parent [`../README.md`](../README.md).