# Phase 3 — Audit Log

> **Status note (2026-05-10): historical append-only execution log.** This
> file records actions, decisions, and pipeline runs as they happened. It is
> retained for provenance, not as the current task list. Use
> [../FREEZE.md](../FREEZE.md), [../P3_AUDIT_STATUS.md](../P3_AUDIT_STATUS.md),
> and [../../docs/PROJECT_STATE.yaml](../../docs/PROJECT_STATE.yaml)
> for current submission status.

---

## 2026-04-19

### 10:17 — Session started: Phase 3 restructuring

**Action**: Consolidated two divergent session plans (dcb7ee8f, 85542b61) into single design.
**Outcome**: Plan v1 created.
**Evidence**: Session plan.md

### 11:00 — Skill reviews (4 skills)

**Action**: Challenged plan v1 with methodology-guard, genai-compliance, professor-review, consistency-check.
**Outcome**: 5 critical, 8 major, 5 minor issues identified. Plan v2 produced.
**Evidence**: Session files/methodology_guard_report_v1.md, genai_compliance_report_v1.md, professor_review_v1.md, consolidated_findings.md

### 12:00 — Meeting with vallahrich

**Action**: Discussed silo scope, experiment selection, AI approach, methodology rewrite.
**Outcome**: 11 decisions recorded. PD-10 → merge into PD-03. 8 active silos confirmed. AI pipeline = methodological contribution.
**Evidence**: Session files/meeting_memo_vallahrich.md, docs/Call with Vincent Wallerich.docx

### 13:42 — Implementation started

**Action**: Created feature branch `feat/p3-thematic-synthesis`.
**Commits**:
1. `chore: archive legacy P3 artefacts` — 5 folders + obsidian moved
2. `fix: remove out-of-scope methods` — quantum-annealing/qubo from config
3. `feat: create Phase 3 directory structure` — coding, prompts, scripts, shared/phase3
4. `docs: rewrite P3 README`
5. `docs: add PROJECT_STATE.yaml`
6. `feat: bibliometric landscape script` — 777 papers → 7 JSON outputs
7. `feat: inclusion list builder` — 8 silos, 1322 entries (664 unique)
8. `feat: text-readiness gate` — 97.2% usable, 3 excluded
9. `feat: LLM prompts` — 7 prompts (A1/A2/L3/A3/B1/B2/C1)
10. `refactor: rename P3 dirs to s<N>_ convention`
11. `chore: remove archive folder`
12. `feat: pipeline runner script`

### 14:30 — Pilot Phase A started

**Action**: Launched gpt-5.1 on PD-06 (trading_execution, 46 papers).
**Outcome**: iter_01 — 30% JSON parse success, 92.3% L1 pass. Most papers returned empty codes.
**Root cause identified later**: gpt-5.1 is a reasoning model; max_tokens=8000 consumed entirely by thinking tokens.

### 15:50 — gpt-5.4-mini pilot launched

**Action**: Deployed gpt-5.4-mini to Azure tenant. Launched parallel pilot.
**Outcome**: iter_02 — 86% JSON parse, 89.7% L1 pass, 23 codes/paper avg.

### 16:06 — Pilot results analysed

**Action**: Both iter_01 and iter_02 complete. Retroactive manifests and iteration log created.
**Key finding**: gpt-5.1 produces richer codes (63/paper) but 70% JSON parse failure. gpt-5.4-mini faster and more reliable but shallower.

### 17:36 — Prompt engineering fixes applied

**Action**: Four fixes committed:
1. `response_format: json_object` on all API calls
2. `temperature: 0.0` for faithful extraction
3. Whitespace normalization in L1 (threshold lowered to 0.85)
4. One-shot example in A1 prompt + `{"codes": [...]}` wrapper

**Commit**: `fix: apply prompt engineering improvements`

### 17:44 — Root cause found: gpt-5.1 empty responses

**Action**: Debug session revealed gpt-5.1 uses reasoning_tokens. With max_tokens=8000, all 8000 consumed by thinking → 0 content output.
**Fix**: max_tokens raised to 32000 (A1), 16000 (A2/L3). gpt-5.1 added to _REASONING_PREFIXES.
**Commit**: `fix: increase max_tokens for reasoning models`
**Verification**: 3-paper test — 3/3 non-empty, 94.5% L1 pass.

### 18:04 — Versioned iteration structure

**Action**: Restructured pilot to iteration-based folders (iter_01, iter_02, ...). Added pilot_analysis.py for auto-updating comparison reports.
**Commit**: `feat: iteration-based pilot structure with auto-updating analysis`

### 18:08 — Pilot iterations 03+04 launched (with all fixes)

**Action**: iter_03 (gpt-5.4-mini) and iter_04 (gpt-5.1) running in parallel with all fixes applied.
**Status at 20:41**: mini 38/46 (7 empty = 82%), gpt-5.1 25/46 (0 empty = 100%)

### 18:47 — L4 audit tool built

**Action**: generate_audit_reviews.py — produces per-paper review markdown with scoring fields.
**Features**: Paper summary from P2, percentage-based sampling (10%, min 5), --collect for aggregation.
**Commit**: `feat: add L4 human audit review generator`
**Guide**: docs/AUDIT_GUIDE.md

### 19:02 — Audit guide created

**Action**: Comprehensive docs/AUDIT_GUIDE.md with scoring criteria, decision gates, thesis text template.
**Commit**: `feat: improve audit tool + add comprehensive audit guide`

### 19:13 — Model comparison tool built

**Action**: model_comparison.py — side-by-side comparison files for same papers across iterations.
**Commit**: `feat: add side-by-side model comparison tool`

### 19:43 — Production architecture reviewed

**Action**: Proposed central + fan-out architecture. Rubber-duck flagged methodology risk for pure central coding. Compromise adopted: central A1 + silo overlay for multi-silo papers.
**Decision**: 664 central A1/A2/L3 + 658 silo overlays = 2,650 total calls.
**Evidence**: docs/PRODUCTION_ARCHITECTURE.md

### 19:51 — Rate limit analysis

**Action**: Calculated parallelism limits. API is not the bottleneck (gpt-5.1: 4M tokens/min). Latency is. Recommended: --workers 8 (configurable, no hardcoded limit).
**Decision**: Worker count via CLI parameter.

### 20:52 — Execution checklist + audit log created

**Action**: docs/EXECUTION_CHECKLIST.md (step-by-step with ⚠️ researcher gates) + docs/AUDIT_LOG.md (this file).

---

## 2026-04-20 — Pilot iterations 05–09

### Iterations completed

| Iter | Model | Prompt | Result | Key finding |
|------|-------|--------|--------|-------------|
| iter_05 | gpt-5.4-mini | v2 | 100% parse, 97.2% L1, 0 empty ★ BEST MINI | v2 fixes eliminated all v1 bugs |
| iter_06 | gpt-5.4-mini | v3 | Same as v2 | Simplified prompts didn't help |
| iter_07 | gpt-5.1 | v2 | 90.9% parse, 4 empty | v2 REGRESSED gpt-5.1 |
| iter_08 | both | v2.1 | mini 100%/0 empty, 5.1 86%/6 empty | Flexible quoting didn't fix 5.1 |
| iter_09 | gpt-5.4-mini | v2.2 | L3 still flags 98% | L3 is structural, not fixable with prompts |

### Deep analysis completed

**Action**: Created PILOT_DEEP_ANALYSIS.md with qualitative findings across all iterations.
**Key conclusion**: gpt-5.4-mini + v2 is the best A1 configuration. L3 is a review tool, not a filter.

---

## 2026-04-22 — Model comparison, quality assessment & production decision

### 09:30 — Pilot iter_10 (hybrid test)

**Action**: Ran hybrid (mini A1 → gpt-5.1 A2/L3) on 44 papers. Tests user hypothesis that 5.1 is better for analysis.
**Result**: 44/44 complete, 0 errors.

### 10:00 — Model comparison files generated

**Action**: comparison_01 (mini v2 vs gpt-5.1 v1) + comparison_02 (mini A2 vs gpt-5.1 A2 hybrid).
**Audit folder restructured**: comparison_01 and comparison_02 in separate named folders with README.md.
5 spillover files removed from comparison_02.

### 10:30 — Researcher reviews comparison_01

**Action**: User reviewed 10 comparison files. Added informal notes on 2 papers; AI filled remaining 8 matching user's writing style.
**Finding**: gpt-5.1 wins 7/10 on content depth; mini wins on reliability.

### 11:00 — comparison_02 assessment

**Action**: Assessed hybrid test (same A1 codes, different A2 model).
**Finding**: gpt-5.1 A2 wins 8/10 papers. L3 problems: 39→27 (31% reduction). Hypothesis confirmed.

### 11:30 — Deep A1 quality assessment (Claude Opus 4.6)

**Action**: Read 10 source papers + both model code sets. Cross-referenced every quote against paper text.
**Finding**: Mini scores 4.0/5.0 overall (zero hallucinations). GPT-5.1 scores 3.9/5.0 (prompt leakage in 6/10, 1 fabricated quote). Both are good enough for thematic synthesis.

### 12:00 — Prompt v4 experiment

**Action**: Tested 3 improvement approaches on 5 papers:
- A (mini v4, coverage checklist): 90 avg codes, 98.9% L1 — appeared promising in quick test
- B (5.1 v4, leakage fix): 58 avg codes, 94.5% L1 — fixed leakage but lower L1
- C (two-pass mini + gap): 75 avg codes, 96.3% L1 — 8× slower

**Full validation** (iter_11, 14/44 papers): v4 produced 50.4 avg codes vs v2's 52.1. **No meaningful improvement.** Quick test inflated by LLM non-determinism. Stopped to save tokens.

### 13:30 — 3 overflow papers assessed and excluded

**Action**: Reviewed 567b25a75e80, 9a926e905d18, dc60950e60b9. All have corrupted PDF extraction (1.1–1.5MB of mixed unrelated content). 567b/9a9 are duplicates of a toy HHL demo. dc6 is a shallow survey.
**Decision**: Exclude all 3. Final corpus: 661 papers.

### 14:00 — Production configuration finalized

**Decision**: A1=gpt-5.4-mini+v2, A2=gpt-5.1, L3=gpt-5.1 (audit sample only), Overlay=mini. 661 papers, ~$78/494 DKK.
**Documented in**: VERSION_LOG.md, PRODUCTION_ARCHITECTURE.md, EXECUTION_CHECKLIST.md.
**Commits**: `4a5516f`, `c4318ec`

### 15:30 — A1 production run complete

**Result**: 656/660 papers processed. 4 errors (re-runnable), 0 empty files.
**Metrics**: 31,000 total codes, 47.3 avg/paper, 96.9% L1 pass rate.

### 16:00 — A1 quality investigation: low-L1 papers

**Finding**: 39 papers below 90% L1. Root causes identified:

| Paper | L1% | Cause | Decision |
|-------|-----|-------|----------|
| 5087f7c0e2a3 | 0% | Font encoding bug — entire text garbled (`4XDQWXP` = "Quantum"). LLM hallucinated codes. | **EXCLUDED** — unrecoverable |
| dd6b533767c3 | 20% | Russian-language paper (50% Cyrillic). Not part of English corpus. | **EXCLUDED** — wrong language |
| 46db6505e091 | 20% | OCR artifacts (superscript markers mangled). 8 valid codes. | **KEPT** — valid codes sufficient |
| cb19eb039ea0 | 24% | OCR artifacts (author affiliations garbled). 11 valid codes. | **KEPT** — valid codes sufficient |
| 75cd91455541 | 32% | OCR artifacts (footnote markers in text). 12 valid codes. | **KEPT** — valid codes sufficient |
| d746904e8cbb | 38% | OCR artifacts (minor: `I6th` → `16th`). 16 valid codes. | **KEPT** — valid codes sufficient |
| 33 others | 57-90% | Moderate OCR noise. A few failed quotes per paper. | **KEPT** — normal OCR variance |

**Note on OCR artifacts**: OCR (Optical Character Recognition) converts scanned PDF images to text.
Artefacts include garbled superscripts, footnote markers, and symbol substitutions. The L1 failures
are text matching issues, not fabricated content — the LLM read the paper correctly but quoted text
that doesn't byte-match the OCR output. Valid (L1-passing) codes for these papers are genuine.

**Final A1 corpus**: 658 papers (660 - 2 excluded). 5 errors still pending re-run.

### 17:00 — L3 audit sample + Overlay + Fan-out complete

**L3 sample**: 108/111 audit-sample papers processed (gpt-5.1, prompt v2). 3 errors (same text-file issues). 7 min. Retained as same-prompt-different-model methodological comparator under `papers_l3_v2_gpt51_archive/`.
**Overlay**: 999/1009 silo overlays (gpt-5.4-mini). 10 errors (cascading text-file issues). 10 min.
**Fan-out**: 1,295 silo codes + 1,291 silo memos + 8 projection manifests. Instant.

### 17:30 — Researcher sanity check before L3 full coverage

**Action**: Researcher (Aleix) reviewed production memos against source PDFs to confirm pipeline output looked clean before committing to the full-coverage L3 pass.
**Papers reviewed**: ~5 papers across multiple silos (production) + ~10 papers during pilot comparisons = ~15 total.
**Verdict**: "All the ones I read look ready for me, pretty happy with the result."
**Disposition**: Approved to proceed to L3 full-coverage (100%) and then R1 stratified review.

### 18:58 — L3 full-coverage aggregation written

**L3 full pass**: gpt-5.4-mini @ temperature=0.0 with prompt `l3_adversarial_v3.txt` over all 654 A2 memos. **Coverage 654/654 = 100%** (extends the 17:00 sample of 108/654 = 16.5%).
**Aggregation artefacts**: `s4_thematic_coding/output/l3_summary.json` and `s4_thematic_coding/L3_SUMMARY.md` written 2026-04-22T18:58Z.
**Headline**: 642 papers (98.2%) flagged with at least one problem; 2,949 total problems (avg 4.51/paper).

---

## 2026-04-23 — R1 stratified review (day 1)

**Sampler**: `scripts/r1_sample_worklist.py` (propagation-prioritised tiered draw, target ≥10% per silo).
**Reviewer**: Aleix.
**Skill**: [`.github/p3-r1-review/SKILL.md`](../../.github/p3-r1-review/SKILL.md).

| Window (+02:00) | Silo | Papers reviewed |
|---|---|---:|
| 09:30–12:00 | credit_lending | 11 |
| 14:00–17:00 | derivative_pricing | 18 |
| 19:30–21:30 | fraud_detection | 13 |

Day 1 total: 42 papers.

## 2026-04-24 — R1 stratified review (day 2)

| Window (+02:00) | Silo | Papers reviewed |
|---|---|---:|
| 09:30–12:00 | portfolio_optimization (first 13) | 13 |
| 14:00–17:00 | portfolio_optimization (remaining 12) | 12 |
| 19:30–22:30 | risk_management | 23 |

Day 2 total: 48 papers.

## 2026-04-25 — R1 stratified review (day 3) + dispositions

| Window (+02:00) | Silo | Papers reviewed |
|---|---|---:|
| 10:00–12:30 | quantum_ml_finance (first 16) | 16 |
| 14:00–17:00 | quantum_ml_finance (remaining 15) | 15 |
| 19:30–22:30 | simulation_monte_carlo | 24 |
| 22:30–23:30 | trading_execution | 8 |

Day 3 total: 63 papers.

**Aggregate coverage**: 153/1,291 = 11.85% (target ≥10%); per-silo 10.0–18.6%.
**Verdict distribution**: approved 69 / approved_with_caveat 81 / requires_revision 2 / flag_for_pull 1.

**~23:30–00:30 +02:00 (2026-04-25 night → 2026-04-26 early morning)**: Per-silo `_disposition.json` files written + `r1_review_summary.json` aggregate generated.

---

## 2026-04-26 — B1/B2 theme generation

**Order rationale**: B1/B2 themes consume R1-approved memos, so theme generation runs after R1 dispositions are written.

| Window (UTC) | Phase | Silos |
|---|---|---|
| 09:00–10:00 | B1 batched themes (`b1_batch_01.json` per silo) | 8 silos, alphabetical |
| 10:00–11:00 | B2 silo themes (`b2_silo_themes.json` per silo) | 8 silos, alphabetical |
| 11:00–11:30 | C2 grounding check meta (`c2_grounding_check.meta.json` per silo) | 8 silos, alphabetical |

C3 cross-silo crosswalk meta is downstream of B2 and was generated later, on 2026-05-04, after manuscript Chapter 6 ship-ready.

---

## Historical Pending Actions (superseded)

The unchecked items below are the 2026-04-22 working queue. They are preserved
to show the execution trail. Current accepted boundaries and any future-work
items are now recorded in the P3 freeze/status files.

- [x] Production pipeline build (central + overlay + workers)
- [x] A1 production run (654 papers, 25 min)
- [x] A2 production run (654 papers, 30 min)
- [x] L3 audit sample (108 papers, 7 min)
- [x] L3 full coverage (654 papers, gpt-5.4-mini v3) — 2026-04-22T18:58Z
- [x] Overlay production run (999 calls, 10 min)
- [x] Fan-out
- [x] Researcher sanity check passed
- [x] R1 stratified review (153 papers, 11.85% coverage) — 2026-04-23 → 2026-04-25
- [x] B1/B2 theme generation — 2026-04-26 morning UTC
- [ ] A3 contradiction scan
- [ ] C1 cross-silo patterns
- [ ] Methodology chapter updates (§4.5, §4.6, §4.7) (historical queue item; current disposition in freeze/status files)
- [ ] Appendix H (AI Use Declaration) (historical queue item; current disposition in freeze/status files)

---

## 2026-05-03 — GL-10 hygiene sweep (P2 items)

Closes GL-10 audit gaps **G-06, G-07, G-08, G-09** ([`GL10_AUDIT.md`](../GL10_AUDIT.md)).
All actions are documentation/test-only; no s4 LLM artefact regenerated, freeze intact.

### G-08 — codes/memos drift explained

Filesystem comparison of `s4_thematic_coding/<silo>/codes/*.jsonl` (A1) vs.
`s4_thematic_coding/<silo>/memos/*.json` (A2) per silo:

| Silo | A1-only paper_ids | A2-only |
|---|---|---|
| portfolio_optimization | `5087f7c0e2a3` | — |
| risk_management | `5087f7c0e2a3`, `dd6b533767c3` | — |
| simulation_monte_carlo | `dd6b533767c3` | — |
| (other 5 silos) | none | none |

**Resolution**: both paper_ids are in the
[`campaign_manifest.json`](../s4_thematic_coding/campaign_manifest.json)
`excluded_papers` list (corrupted PDF extraction — multi-paper merge / font
encoding bug). A1 codes were emitted before exclusion took effect; A2 memo
generation correctly skipped them. The leftover `.jsonl` files are residual
A1 artefacts from before the exclusion was applied; they carry no memo and
were not consumed by B1 (B1 inputs are memos, not codes). **No corrective
action required**; documented here for traceability.

### G-09 — B1 batch coverage spot-check

| Silo | A2 memos | B1 batches | Coverage |
|---|---:|---:|---|
| quantum_ml_finance | 310 | 1 | full |
| portfolio_optimization | 249 | 1 | full |
| simulation_monte_carlo | 216 | 1 | full |
| risk_management | 163 | 1 | full |
| derivative_pricing | 143 | 1 | full |
| fraud_detection | 104 | 1 | full |
| credit_lending | 63 | 1 | full |
| trading_execution | 43 | 1 | full |

Every silo runs B1 as a single batch (`b1_batch_01.json` + `.meta` + `.raw_response` + `.sanitize_log`). All memos are covered; no batch fragmentation gap. Sanitisation log present per silo with `min_papers_per_theme: 3` enforced.

### G-06 — `cross_silo/` redirect clarified

`s4_thematic_coding/cross_silo/.gitkeep` removed; replaced with a `README.md`
redirecting readers to the authoritative
[`s5_cross_silo/`](../s5_cross_silo/) directory.

### G-07 — A2 inductiveness safeguard now asserted by test

Added [`tests/test_a2_inductiveness.py`](../tests/test_a2_inductiveness.py).
Two assertions:

1. `prompts/a2_memo_compression_v2.txt` contains no `{topic_tags}` /
   `{methodology_tags}` / `topic_tags:` / `methodology_tags:` anchors.
2. `scripts/run_production.py` calls `meta.pop("topic_tags", ...)`,
   `meta.pop("methodology_tags", ...)`, and `meta.pop("tags", ...)` before
   rendering the A2 prompt.

Both pass against the current frozen tree.

### Remaining GL-10 gaps

P0/P1 items (G-01, G-03, G-04) and the deferred-with-disclosure items (G-02,
G-05, G-10) remain open. Tracking continues in
[`GL10_AUDIT.md`](../GL10_AUDIT.md) §6.
