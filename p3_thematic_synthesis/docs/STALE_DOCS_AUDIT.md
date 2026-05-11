# Phase 3 Stale-Documents Audit

> **Status note (2026-05-10): historical cleanup audit.** This document records a 2026-04-22 archival sweep. It is not the current Phase 3 status authority. Use [../FREEZE.md](../FREEZE.md), [../README.md](../README.md), and [../../docs/PROJECT_STATE.yaml](../../docs/PROJECT_STATE.yaml) for the current active/historical boundary.

**Date**: 2026-04-22
**Purpose**: Classify every markdown document in `p3_thematic_synthesis/` by active-use status, and determine a conservative archival policy. Archive (not delete) preserves audit trail.

**Policy**: Files classified `archive` are moved to `p3_thematic_synthesis/_archive/` with original relative path preserved. Nothing is deleted in this sweep.

## Classification

### Active — keep as-is (core current pipeline)

| Path | Role |
|---|---|
| `README.md` | Current entry point. |
| `docs/PRODUCTION_ARCHITECTURE.md` | Current pipeline architecture incl. dual-LLM routing table. |
| `docs/B1_B2_QUALITY_RUBRIC.md` | Pre-committed signed rubric for B1/B2 (methodology anchor). |
| `docs/B1_B2_COALESCENCE_REPORT.md` | Silo-level coalescence report across all 8 silos. |
| `docs/B2_MANUSCRIPT_READINESS.md` | Disposition ACCEPT for all 8 silos. |
| `docs/B1_B2_RUBRIC_AUTO_SCORES.json` | Automated rubric scoring input to B2_MANUSCRIPT_READINESS.md. |
| `docs/STAGE_C_QUALITY_RUBRIC.md` | Pre-committed rubric for Stage C (signed 2026-04-22). |
| `docs/AUDIT_LOG.md` | Decision log for P3 execution. |
| `docs/AUDIT_GUIDE.md` | L4 human-audit procedure; still relevant for C2/researcher spot-checks. |
| `docs/EXECUTION_CHECKLIST.md` | Living execution checklist, last updated 2026-04-22. |
| `AUDIT_REPORT.md` | PhD-level audit (2026-04-17) of quantitative/quantum_advantage. Audit trail. |
| `prompts/VERSION_LOG.md` | Prompt version history. |
| `s1_silo_scoping/<silo>/experiments/README.md` (×8) | Per-silo scoping README stubs; referenced by the pipeline. |
| `s3_quantum_advantage/**/*.md` | **FROZEN** (2026-04-17). P4 depends on these. |
| `s4_thematic_coding/<silo>/` (×8 current silos) | Active B1/B2/memos/codes outputs. |

### Archive candidates — move to `_archive/`

| Path | Reason |
|---|---|
| `s5_cross_cutting/` (entire directory) | Pre-pipeline dashboard from 2026-04-14. Reports on P2 frontmatter tags (by_topic, by_method, by_claim) that overlap with P2 outputs. Stage C (s5_cross_silo/) replaces its cross-silo analytical role. **Contents (all README-style reports)**: `overview.md`, `missing_papers.md`, `experiment_landscape.md`, `contradictions.md`, `by_topic/`, `by_method/`, `by_claim/`. |
| `s4_thematic_coding/pilot/` (entire directory) | Pilot phase (iter_01..iter_10 trading_execution pilot). Superseded by production A1/A2/B1/B2 runs. Keep the two high-level analyses (`pilot_analysis.md`, `PILOT_DEEP_ANALYSIS.md`) as archived-but-cited methodology artefacts — they document why we picked the production prompts. Folder preserved under `_archive/` in full to retain audit traceability. |
| `docs/TUNING_GUIDE.md` | P2-style extraction-pipeline tuning guide. P3 uses a different architecture (stateless sub-agents, pre-committed prompts). Not referenced by current P3 workflow. |
| `docs/QUANTITATIVE_PIPELINE_DESIGN.md` | 2026-04-08 brainstorm document referencing a twelve-silo design that predates the eight-silo scope reduction. Superseded by the current quantitative pipeline under `s2_quantitative/` (which still evolves). Preserve as historical design record. |

### Out of scope for this audit

| Path | Rationale |
|---|---|
| `s2_quantitative/` | Owned by Vallahrich; not Phase 3 thematic synthesis. |
| `quantum_advantage/` (top-level) | Earlier sibling of s3_quantum_advantage; not touched in this audit. |
| Per-silo memos, codes, themes output directories | Execution outputs, not documentation. |

## Audit summary

- **Active docs kept**: 15 (plus per-silo README stubs and frozen s3_quantum_advantage content).
- **Docs archived**: 4 (`s5_cross_cutting/`, `s4_thematic_coding/pilot/`, `docs/TUNING_GUIDE.md`, `docs/QUANTITATIVE_PIPELINE_DESIGN.md`).
- **Files deleted**: 0 (policy: archive-only).

## Cross-references to update after archive

After archival, the following files may reference archived paths and should be spot-checked:
- `README.md` — check for links to `s5_cross_cutting/`.
- `docs/EXECUTION_CHECKLIST.md` — check for pilot references.
- `docs/PRODUCTION_ARCHITECTURE.md` — already updated to reflect production pipeline (no pilot refs).

## Reversibility

Archival is `git mv` to `_archive/...`. Reversal is trivial (`git mv` back). History preserved in git log.
