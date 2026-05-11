# s2\_quantitative — Benchmark Extraction Pipeline

**Phase 3, Steps 3.2–3.4**  
**Status**: 🔒 FROZEN (2026-04-17)

## Purpose

Extracts experiment-level benchmark data from the P2 corpus: algorithms, quantum resources, speedup claims, classical baselines. Produces the structured evidence substrate that feeds the quantum-advantage triangulation in s3.

## Pipeline

| Step | Description | Model | Status |
|------|-------------|-------|--------|
| 3.2 | Per-silo inclusion lists | — | ✅ Complete |
| 3.2b | Text-readiness gate (97.2% pass) | — | ✅ Complete |
| 3.3 | Benchmark extraction (3-step LLM) | gpt-5.4-mini | 🔒 Frozen |

The 3-step extraction per paper:
1. **Identify experiments** — detect distinct experiments in full text
2. **Extract silo results** — extract resources, speedups, baselines per experiment
3. **Validate against paper** — cross-check extracted claims against source

## Configuration

- Model: `gpt-5.4-mini`, temperature 0.0, seed 42
- Schema: `benchmark_extraction_v1.0` (100% validation rate)
- Config: `config/extraction_config.json`

## Inputs

- `shared/extracted_text/text/` — 777 full-text PDFs extracted to markdown
- `shared/phase3/inclusion/` — 8 per-silo inclusion JSONs (664 unique papers)

## Outputs

- `output/extractions_preQ0_20260417_095811/` — 459 papers × 1,185 experiments (JSON)
- `output/tables/` — aggregate rollup tables (silo × algorithm family × speedup)

## Freeze Notice

⚠️ **Do not re-run extractions.** These outputs are consumed by s3\_quantum\_advantage (also frozen) and feed the Phase 4 shortlist. SHA256 fingerprints recorded in `s3_quantum_advantage/FROZEN.md`.

## Downstream Consumers

- **s3\_quantum\_advantage** — triangulates these 1,185 experiments
- **manuscript Ch6** — per-silo quantitative footprint paragraphs
- **p4\_experiments** — experiment selection via `common/p4_shortlist.json`
