# Phase 3 - Thematic Synthesis

Phase 3 is the thesis synthesis layer. It turns the classified P2 corpus into finance-silo evidence, quantitative experiment records, quantum-advantage assessments, thematic findings, and cross-silo arguments.

For frozen counts and claim limits, use [FREEZE.md](FREEZE.md) and [P3_AUDIT_STATUS.md](P3_AUDIT_STATUS.md). For the whole repository pipeline, use [../docs/PIPELINE.md](../docs/PIPELINE.md).

## Current State

| Item | Value |
|---|---:|
| Active silos | 8 |
| Active S2 extractions | 501 files / 1,046 experiments |
| S3 filtered matrix | 936 active rows |
| S4 thematic layer | 95 descriptive themes / 45 analytical themes |
| S5 cross-silo layer | C1/C2/C3 artifacts retained with provenance note |
| S6 finance framing | 629 F1 paper outputs / 8 F2 silo briefs |

S6 (`s6_silo_framing/`) is a descriptive finance-framing sibling, not an independent semantic-validation layer.

## Stage Map

| Stage | Folder | Purpose | Main Evidence |
|---|---|---|---|
| S1 | `s1_silo_scoping/` | Defines active finance silos and inclusion boundaries. | Silo manifests and scope notes. |
| S2 | `s2_quantitative/` | Extracts quantitative benchmark and experiment records. | `output/extractions/`, `output/audit/`. |
| S3 | `s3_quantum_advantage/` | Applies the 4-core + 1-veto quantum-advantage assessment. | `combined/output/*.filtered.json`. |
| S4 | `s4_thematic_coding/` | Performs per-paper coding, memoing, review, and per-silo theme synthesis. | `papers/`, per-silo `themes/`, `production_summary.json`. |
| S5 | `s5_cross_silo/` | Builds cross-silo meta-themes and literature crosswalks. | `c1_meta_themes.json`, `c2_aggregate.json`, `c3_crosswalk.json`. |
| S6 | `s6_silo_framing/` | Adds descriptive financial-problem framing for chapter context. | `extractions/papers/`, `briefs/*/f2_silo_brief.json`. |

## What To Cite

- Cite filtered S3 outputs for active quantum-advantage claims.
- Cite S4 per-silo `b2_silo_themes.json` files for analytical themes.
- Cite S5 outputs for cross-silo patterns, with the C2 provenance caveat in `s5_cross_silo/c2_aggregate.PROVENANCE_NOTE.md`.
- Cite S6 only as descriptive finance framing.

## Historical Material

The old `_archive/` payload has been moved to the external source archive named in [../README.md](../README.md). A small `_archive/README.md` remains as the restore pointer. This keeps the hand-in tree focused on the active thesis evidence.

## Verification

From the repository root:

```powershell
pwsh .\verify.ps1
python -m pytest p3_thematic_synthesis/tests
```