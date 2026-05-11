# s4\_thematic\_coding — Per-Paper and Per-Silo Thematic Analysis

**Phase 3, Steps 3.5–3.6**  
**Status**: ✅ B1/B2 Complete (8 silos, 95 descriptive + 45 analytical themes)

## Purpose

Performs inductive thematic coding on the full P2 corpus: per-paper open coding and memo writing (3.5), then per-silo theme synthesis (3.6). Produces the descriptive and analytical themes that form the backbone of Chapter 6.

## Pipeline

| Step | Description | Model | Status |
|------|-------------|-------|--------|
| 3.5 A1 | Open coding (inductive, silo-blind) | gpt-5.4-mini | ✅ Complete |
| 3.5 A2 | Analytical memos | gpt-5.1 | ✅ Complete |
| 3.5 L3 | Adversarial review (~10% sample) | gpt-5.1 | ✅ Complete |
| 3.5 Overlay | Silo-specific re-read (multi-silo papers) | gpt-5.4-mini | ✅ Complete |
| 3.6 B1 | Descriptive themes (per-silo batches) | gpt-5.1 | ✅ Complete |
| 3.6 B2 | Analytical themes (silo-level synthesis) | gpt-5.1 | ✅ Complete |

## Folder Structure

```
s4_thematic_coding/
├── papers/                    # Central A1/A2/L3 outputs (661 papers)
│   ├── {paper_id}.jsonl       # A1 inductive codes
│   ├── {paper_id}.json        # A2 analytical memo
│   └── {paper_id}_l3.json     # L3 adversarial check (sample)
├── {silo}/                    # Per-silo folders (×8)
│   ├── codes/                 # A1 codes (per paper_id)
│   ├── memos/                 # A2 memos + L3 + silo overlays
│   ├── reviewed/              # Post-R1 researcher-approved memos
│   └── themes/                # B1/B2 theme outputs
│       ├── b1_batch_*.json    # B1 descriptive themes
│       └── b2_silo_themes.json # B2 analytical themes
├── cross_silo/                # Reserved for Stage C
├── campaign_manifest.json     # Production run metadata
└── production_summary.json    # Fanout phase status
```

## Theme Naming

- **DT-XX-NNN**: Descriptive themes (e.g., DT-RM-001)
- **AT-XX-NNN**: Analytical themes (e.g., AT-RM-001)

Where XX = silo abbreviation (PO, DP, RM, QML, FD, TE, CL, SMC).

## Inputs

- `shared/extracted_text/text/` — 661 full-text extracts
- `shared/phase3/inclusion/` — 8 per-silo paper lists
- `p3_thematic_synthesis/prompts/` — A1/A2/L3/overlay/B1/B2 prompts (v2)

## Outputs

- 661 central A1/A2 records in `papers/`
- 8 × `themes/b2_silo_themes.json` — analytical themes (45 total across 8 silos)
- 8 × `themes/b1_batch_*.json` — descriptive themes (95 total)
- `campaign_manifest.json` — 658 papers processed, 5 excluded (corrupted PDF)

## Downstream Consumers

- **s5\_cross\_silo** — consumes B2 analytical themes for meta-theme synthesis
- **manuscript Ch6** — each silo section is built from B2 themes
- **manuscript Ch6 propositions** — AT themes anchor the per-silo propositions
