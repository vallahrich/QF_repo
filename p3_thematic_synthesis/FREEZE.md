# `p3_thematic_synthesis/` — freeze record

| Field | Value |
|---|---|
| Freeze date | 2026-05-02 |
| Status | **Frozen** for code/data. Any further changes require LLM reruns (out of freeze). |
| Tests | `pytest p3_thematic_synthesis/tests/` — 4/4 passing (silo consistency + 3 release invariants) |

## Active partition (cite this, not the historical README tables)

| Dimension | Value | Authority |
|---|---:|---|
| Active silos | **8** (PD-01..PD-09 minus PD-08) | [shared/config/silo_inclusion.json](../shared/config/silo_inclusion.json) |
| `problems/` directories on disk | 9 (8 active + `cryptography_security/` excluded marker) | enforced by `tools/verify/v2_consistency.py:C2`/`C3` |
| Active S2 extractions | **501 files / 1046 experiments** | [s2_quantitative/output/audit/corpus_lineage.json](s2_quantitative/output/audit/corpus_lineage.json) |
| S3 rows after active-silo filter | **936** consensus/matrix rows; **46** disagreement cases | [combined/output/*.filtered.json](s3_quantum_advantage/combined/output/) |
| Stage status | s1 ✅ s2 ✅ s3 ✅ s4 ✅ s5 ✅ (c2 provenance gap disclosed) **s6 ✅ descriptive framing complete as scoped** | see status doc |

## What is the canonical artifact

For any S3 claim cited in the manuscript, **use the `*.filtered.json` files**:

- [combined/output/consensus_summary.filtered.json](s3_quantum_advantage/combined/output/consensus_summary.filtered.json) — 936-row active-silo rollup, 8 active silos
- [combined/output/triangulation_matrix.filtered.json](s3_quantum_advantage/combined/output/triangulation_matrix.filtered.json) — 936 per-experiment rows (110 dropped: 89 "other" + 18 cryptography-security + 3 insurance-actuarial)
- [combined/output/disagreement_cases.filtered.json](s3_quantum_advantage/combined/output/disagreement_cases.filtered.json) — 46 disagreement cases (4 dropped: "other")

The unfiltered files (`consensus_summary.json`, `triangulation_matrix.json`, `disagreement_cases.json`) are kept for provenance but **must not be cited** as active evidence — they predate the 2026-04-19 silo-set reduction.

## Closed audit-trail items (P3_AUDIT_STATUS.md)

| ID | Was | Now | Where |
|---|---|---|---|
| QA-1 | open-blocker (Rønnow gate-based) | **closed-active** | [assess_ronnow.py:_assess_one](s3_quantum_advantage/ronnow/assess_ronnow.py) `_RONNOW_APPLICABLE_FAMILIES` — non-applicable families now return `not_applicable`. |
| QA-5 | open-blocker (Dalzell QIPM blanket) | **closed-active** | [assess_dalzell.py:121-153](s3_quantum_advantage/dalzell_2023/assess_dalzell.py) — QIPM `is_infeasible` scoped to QIPM-tagged experiments. |
| QA-11 | open-blocker (Beverland fidelity) | **accepted-risk** | [assess_beverland.py](s3_quantum_advantage/beverland_2022/assess_beverland.py) `FRAMEWORK_ID="beverland_inspired_2022"` + module-docstring caveat. |

## Architectural points to remember

- **5 active analytical/descriptive stages + s6 sibling framing.** s1 silo scoping → s2 quantitative → s3 quantum advantage → s4 thematic coding → s5 cross-silo; s6 is a descriptive sibling framing layer with 629 F1 paper outputs and 8 F2 silo briefs. It is not independent semantic validation.
- **s5/c2 lineage gap.** `c2_aggregate.json` lacks the prompt + raw response + meta provenance siblings that `c1` and `c3` carry. Disclosed in [s5_cross_silo/c2_aggregate.PROVENANCE_NOTE.md](s5_cross_silo/c2_aggregate.PROVENANCE_NOTE.md). Cite the per-silo `c2_grounding_check.json` files (which have provenance) instead of `c2_aggregate.json`.
- **AUDIT_REPORT.md is historical.** Controlling status doc is [P3_AUDIT_STATUS.md](P3_AUDIT_STATUS.md). README banner is now consistent with both.

## Test surface

- [tests/test_silo_consistency.py](tests/test_silo_consistency.py) — `consensus_summary.filtered.json` references no inactive silos.
- [tests/test_release_invariants.py](tests/test_release_invariants.py) — (a) s6 status banner present in s6/README + top-level README, (b) no active code imports from `_archive/`, (c) filtered consensus post-dates raw consensus.

## Reproduce

```powershell
# from repo root
python p3_thematic_synthesis/s3_quantum_advantage/scripts/filter_consensus.py
pytest p3_thematic_synthesis/tests/
```

## Deferred (out of freeze)

- **Q-6** stratified n≥30 reliability κ on extraction. Bounded LLM cost (~30 papers × 3-step extraction) but not in this freeze; disclosed as a limitation.
- **Q-8** legacy `extract_benchmarks.py` script archival. Carries deprecation banner; consumed by `run_batch.py` / `run_batch_api.py`. Not removed because removal would break those scripts.
- **s5/c2 regeneration with provenance siblings.** One Opus 4.6/4.7 call against the same inputs; deferred.
- **`triangulate.py` re-run** that consumes the relabelled per-paper Rønnow / Dalzell / Beverland verdicts. The post-hoc filter is sufficient for the freeze; a full re-aggregation would also recompute the `consensus_verdict` field per row, which the post-hoc filter does not.

### GL-10 — s4 reproducibility caveats (added 2026-05-03)

- **LLM-call seed not set.** `s4_thematic_coding/campaign_manifest.json` `parameters_used.llm_call_seed = null`. The Azure OpenAI `seed` parameter was not passed to A1/A2/L3/Overlay/B1/B2 calls, so outputs are subject to Azure non-determinism even at `temperature=0`. Sampling within `run_production.py` is deterministic (`random.Random(42)`). To be acknowledged in the methodology limitations section.
- **A3 contradiction scan retained but not executed.** [`prompts/a3_contradiction_scan.txt`](prompts/a3_contradiction_scan.txt) is preserved in the prompt set for traceability; no `a3_*.json` outputs were produced in the v2026-05-02 freeze. Disclosed as a deferred validation step. The canonical design order remains A1 -> L1 -> A2 -> L2 -> L3 -> A3 -> R1, but the frozen artefact set must not be described as having executed the full A3 -> R1 chain.
- **L3 / R1 timing.** The 2026-04-22 spot-check (~15 papers, free-text approval, [`docs/AUDIT_LOG.md`](docs/AUDIT_LOG.md) 17:30) plus L3 adversarial sample (108/654 = 16.5 %) plus c2 grounding check per silo are the in-freeze Pillar 5 evidence. The later full-coverage L3 aggregation/propagation pass and R1 stratified review were executed as GL-10 post-freeze validation hardening and should be cited as such, not as inputs to the 2026-05-02 freeze.
- **Single-coder design.** No inter-rater Cohen's κ was computed between the two researchers. Bias-mitigation substitute is the LLM-adversarial L3 layer plus the c2 grounding check. To be stated explicitly in the methodology.

## Known historical files (kept for provenance, not authoritative)

- `s3_quantum_advantage/combined/output/_pre_remediation_snapshot_2026-05-02/` — pre-filter snapshot.
- `cross_cutting/by_topic/`, `by_method/`, `by_claim/`, `openalex_cache/` — referenced by `shared/scripts/build_citation_graph.py`. Not removed.
- `_archive/` — `obsidian_pre_2026-05-02/` plus 4 `problems_*` directories that were never PDs or were absorbed/excluded.
