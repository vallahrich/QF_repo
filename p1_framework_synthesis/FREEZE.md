# `p1_framework_synthesis/` — freeze record

| Field | Value |
|---|---|
| Freeze date | 2026-05-02 |
| Status | **Frozen** for code/data. All future Phase 1 changes require a re-extraction (out of freeze scope). |
| Methodology | LLM-assisted extraction + researcher-curated regex normalisation. **Cruzes & Dybå (2011)** within an **Arksey & O'Malley (2005)** scoping approach. *Not* strict Elo & Kyngäs inductive coding (see [audit-trail.md](audit-trail.md) D-5). |

## Active partition (cite this, not the headline)

| Dimension | Headline | Active / effective | Authority |
|---|---|---|---|
| Problem domains | 10 (PD-01..PD-10) | **8** active | [shared/config/unified_taxonomy.json](../shared/config/unified_taxonomy.json) + [silo_inclusion.json](../shared/config/silo_inclusion.json); enforced by `tools/verify/v2_consistency.py` |
| Solution categories | 11 (SA-01..SA-11) | 11 | unified_taxonomy.json |
| s1 extraction files on disk | 29 | — | `s1_extractions/` |
| Effective independent surveys | — | **≈ 20** | minus 1 quarantined (`_QUARANTINED_2026_AtharvaJain_misidentified.json`), minus 7 `EXCLUSIONS`, minus 1 Herman 2022/2023 duplicate (D-6) |

PD-08 = excluded (D-3); PD-10 = retracted, merged into PD-03 (D-1/D-2). Both lifecycle states codified in `unified_taxonomy.json`.

## Closed audit-trail items (D-1..D-7)

- **D-1** AtharvaJain extraction quarantined (data-integrity defect; sole PD-10 source was wrong PDF).
- **D-2** PD-10 retracted, merged_into PD-03.
- **D-3** PD-08 marked excluded (QKD-dominated, out of gate-based scope).
- **D-4** Multi-tag overlap policy added to [s4_outputs/codebook.md](s4_outputs/codebook.md) covering PD-02↔PD-09, SA-02∧SA-04, PD-08↔SA-09.
- **D-5** Methodology framing reframed across README, REVIEW_CHECKLIST, script docstring, taxonomy headers, conceptual-framework, and bibliography.
- **D-6** Herman 2022 (arXiv) → 2023 (published) deduplication codified via `SUPERSEDED` map in [scripts/build_review_data_done.py](scripts/build_review_data_done.py).
- **D-7** Khari + AtharvaJain documented as a *class* of failure (filename↔embedded-title mismatch); guard preregistered for any future re-extraction.

## Provenance

- Extraction prompt is versioned: [prompts/extraction.txt](prompts/extraction.txt) header `version: 1.0; date: 2026-04-11; model: gpt-5.1; temperature: 0.2`.
- Per-paper triage decisions live in [scripts/build_review_data_done.py](scripts/build_review_data_done.py): `EXCLUSIONS`, `NEEDS_RECHECK`, `HIGH_RELEVANCE` (now dict-with-rationales), `SUPERSEDED`.
- `s2_coding/_archive/` holds the stale `review_data.json`; the live aggregate is `review_data_done.json`. Dead `scripts/build_review_data.py` is in `scripts/_archive/`.

## Reproduce

```powershell
python p1_framework_synthesis/scripts/build_review_data_done.py
python p1_framework_synthesis/scripts/build_taxonomy.py
python p1_framework_synthesis/scripts/validate_outputs.py
```

`build_review_data_done.py` is fully deterministic (no LLM calls); both other scripts are pretty-printers over its output. The validator exits 0 if all live artifacts are present.

## Deferred (out of freeze)

- Inter-coder κ on Phase 1 extractions. Single-LLM single-pass; no second coder. Acceptable as a **scoping** synthesis; would need a 2nd-coder pass on a 30-paper subsample to support stronger empirical claims.
- Filename↔embedded-title guard in [scripts/extract_document.py](scripts/extract_document.py). Preregistered in audit-trail D-7; not implemented because no re-extraction is being run.
- LLM-aggregation step (originally step 4 of the README's "Process") was never executed. Replaced by deterministic regex normalisation, which is the actual basis of every count cited in the conceptual framework. This is a known and disclosed methodological choice.
