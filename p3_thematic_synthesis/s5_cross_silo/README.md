# s5\_cross\_silo — Cross-Silo Synthesis

**Phase 3, Step 3.7**  
**Status**: ⏳ Draft C1 complete; C2/C3 pending redesign

## Purpose

Synthesises the 8 silo-level thematic analyses (from s4 B2) into corpus-wide meta-themes. Maps findings to published frameworks and generates the cross-silo chapter of the manuscript.

## Pipeline

| Step | Description | Status |
|------|-------------|--------|
| C1 | Meta-theme identification (cross-cutting patterns) | ✅ Draft (10 themes, Opus 4.6) |
| C2 | Grounding check (verify claims against silo evidence) | ⏳ Minimal draft |
| C3 | Literature crosswalk (map to Rønnow, Beverland, etc.) | ⏳ Draft |

## Outputs

- `c1_meta_themes.json` — 10 corpus-wide meta-themes (e.g., MT-001 "end-to-end advantage mirage")
- `c2_aggregate.json` — grounding validation (currently minimal)
- `c3_crosswalk.json` — theme-to-literature crosswalk
- `crosswalk_shortlist.json` — canonical literature references per theme

## Inputs

- `s4_thematic_coding/{silo}/themes/b2_silo_themes.json` — per-silo analytical themes
- `shared/config/unified_taxonomy.json` — taxonomy anchoring
- Published QA frameworks (Rønnow 2014, Beverland 2022, etc.)

## Redesign Note

Stage C needs redesign to align with the new Ch6 per-silo structure (thematic + quantitative + QA + propositions). The current C1/C2/C3 outputs were generated before the decision to integrate quantitative and QA evidence into each silo section. Redesign scope to be decided after WS-3 (per-silo revision pass) produces the propositions register.

## Downstream Consumers

- **manuscript `_cross_silo.tex`** — §6.11 cross-silo meta-argument
- **manuscript Ch8 Discussion** — corpus-wide patterns feed the two-studies convergence
