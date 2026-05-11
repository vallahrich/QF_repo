# GL-10 Audit — P3/s4 Safeguards Completeness

**Scope**: `p3_thematic_synthesis/s4_thematic_coding/` (steps 3.5 A1/A2/L3/Overlay + 3.6 B1/B2 + s4-side c2 grounding).
**Mode**: Read-only audit. P3/s3 frozen 2026-04-17; P3 (incl. s4) frozen 2026-05-02 per [`FREEZE.md`](FREEZE.md). Findings are PROPOSED with severity, not executed.
**Date**: 2026-05-03.
**Skill**: `genai-compliance` (5-pillar framework).
**Reference invariants**: [`shared/config/unified_taxonomy.json`](../shared/config/unified_taxonomy.json) v2.0; writing-guide `R-01` / `R-03` (Phase 3 = LLM-driven coding standard, distinct from Phase 1 framing).

---

## 1. Executive verdict

**UPDATE 2026-05-03**: All P0/P1 mandatory items closed; all P2 hygiene items closed; deferred items disclosed in `FREEZE.md`. See §10 closure log.

**CONDITIONAL PASS — defensible as a methodology pipeline; one P0 documentation gap and three P1 evidence gaps remain.** _(original 2026-05-03 morning verdict; superseded by §10 closure log.)_

The s4 pipeline is the strongest-instrumented stage in the project: every B1/B2/c2 silo carries `prompt`, `rendered_sha256`, `raw_response`, `meta`, and `sanitize_log` siblings; the campaign manifest pins models, temperature, prompt versions, git commit, and exclusion reasons; A1/A2 outputs exist for 654 papers across 8 active silos. The compliance weakness is **not in audit-trail capture** — it is in **researcher-acceptance evidence** (Pillar 2/5): the designed `reviewed/` R1 gate (per [`docs/PRODUCTION_ARCHITECTURE.md`](docs/PRODUCTION_ARCHITECTURE.md#L192)) was never instantiated as a filesystem artefact, and the documented spot-check covered ~15/654 papers (~2.3%) versus the 10 % target codified in [`docs/EXECUTION_CHECKLIST.md`](docs/EXECUTION_CHECKLIST.md) item 3.10.

---

## 2. Safeguard inventory — expected vs. present

| # | Expected safeguard | Authority | Present? | Evidence |
|---|---|---|---|---|
| S1 | Versioned, committed prompts for every step (A1/A2/L3/Overlay/B1/B2/c2) | genai-compliance Pillar 3 | ✅ | [`prompts/`](prompts/) — 8 versioned files inc. `a1_*v2.txt`, `b1_descriptive_themes_v1.txt`, `b2_analytical_themes_v1.txt`, `l3_adversarial_v2.txt`, `overlay_memo.txt`, `c2_grounding_check_v1.txt`; `VERSION_LOG.md` present |
| S2 | Per-call rendered prompt SHA stored next to output | Pillar 3, 4 | ✅ | e.g. `credit_lending/themes/b1_batch_01.meta.json` carries `prompt_sha256` + `rendered_sha256` |
| S3 | Raw LLM response logged (not only post-processed) | Pillar 3 | ✅ | `*.raw_response.txt` siblings to every B1/B2/c2 output |
| S4 | Sanitisation log distinguishing model output from post-processing | Pillar 3 | ✅ | `b1_batch_01.sanitize_log.json` per silo |
| S5 | Models pinned (provider + name + API version) | Pillar 4 | ✅ | [`campaign_manifest.json`](s4_thematic_coding/campaign_manifest.json) — A1=gpt-5.4-mini, A2/L3/Overlay=gpt-5.1; `azure_api_version: 2025-04-01-preview` |
| S6 | Sampling parameters pinned | Pillar 4 | ⚠️ | `temperature: 0.0` and `response_format: json_object` recorded; **no `seed` field** in s4 manifest (s2 manifest has `seed: 42`); no `top_p`/`max_tokens` recorded |
| S7 | Exclusions documented with reason | Pillar 1, 5 | ✅ | Manifest lists 5 excluded paper_ids + `Corrupted PDF extraction (multi-paper merge)`; mirrored in [`docs/AUDIT_LOG.md`](docs/AUDIT_LOG.md) |
| S8 | Adversarial / hallucination check (L3) | Pillar 5 | ⚠️ | 108 `_l3.json` files for 654 A2 outputs = 16.5 % sample; spec target was 10 % so coverage exceeds plan, but **L3 results are not aggregated into a fail-rate or disposition table** anywhere under s4; only a one-line "108/111, 3 errors" entry in `AUDIT_LOG.md` |
| S9 | Researcher-acceptance gate (R1) per paper | Pillar 2, 5 | ❌ | `reviewed/` directory **does not exist** in any of the 8 silos; [`EXECUTION_CHECKLIST.md`](docs/EXECUTION_CHECKLIST.md#L77) Phase 4 items 4.1–4.5 are all unchecked; [`PRODUCTION_ARCHITECTURE.md`](docs/PRODUCTION_ARCHITECTURE.md#L192) describes `reviewed/<paper_id>.json` as the audit gesture |
| S10 | Researcher spot-check sample with documented accuracy/disposition | Pillar 5 | ⚠️ | `AUDIT_LOG.md` 17:30 entry: "~5 production + ~10 pilot = ~15 papers" reviewed; verdict "All the ones I read look ready"; **no rubric, no error count, no per-paper table**. Below the 10 % L4 target (would be 65 papers) |
| S11 | B2 rubric scoring | Pillar 5 | ✅ | [`scripts/score_b2_rubric.py`](scripts/score_b2_rubric.py) exists; B1 sanitisation enforces `min_papers_per_theme: 3` ([`b1_batch_01.meta.json`](s4_thematic_coding/credit_lending/themes/b1_batch_01.meta.json)) |
| S12 | C2 grounding check (themes anchored in source codes) | Pillar 5 | ✅ | `c2_grounding_check.json` + `.raw_response` + `.meta` per silo; v1 + v2 retained for audit |
| S13 | A3 contradiction scan | Pillar 5 (planned) | ❌ | Prompt [`a3_contradiction_scan.txt`](prompts/a3_contradiction_scan.txt) committed; **no `a3_*.json` outputs** under any silo; checklist 5.5 unchecked |
| S14 | Cross-silo C-stage outputs | Pillar 3 | ⚠️ | `s4_thematic_coding/cross_silo/` contains only `.gitkeep`; cross-silo C1/C3 live in `s5_cross_silo/` (out of scope here, but the empty s4 sibling is misleading) |
| S15 | Per-silo `code_memo_index.json` for traceability | Pillar 3 | ✅ | Present per silo |
| S16 | Inductiveness safeguard (no PD topic_tags fed into A2) | Methodology integrity | ⚠️ | Documented as item 3.3 in `EXECUTION_CHECKLIST.md`, but **no test asserts the A2 prompt template lacks `topic_tags`**; rely on prompt inspection |
| S17 | Top-level freeze record | Pillar 1 | ✅ | [`FREEZE.md`](FREEZE.md) dated 2026-05-02; tests in `tests/` enforce 3 release invariants |
| S18 | Manifest cross-references all 8 active silos | Pillar 1 | ✅ | Manifest enumerates the 8 PD codes minus PD-08 (cryptography excluded) and PD-10 (insurance absorbed) — consistent with `silo_inclusion.json` |

---

## 3. Manual-review status per silo

Codes / memos counted from filesystem; `reviewed/` checked for R1 acceptance artefacts; B2 = analytical-themes file presence.

| Silo | A1 codes (jsonl) | A2 memos (json) | L3 sample present | `reviewed/` dir | B1 themes | B2 themes | c2 grounding | R1 status |
|---|---:|---:|---:|---|---|---|---|---|
| portfolio_optimization | 250 | 249 | yes (subset) | **missing** | ✅ | ✅ | ✅ | ❌ not done |
| derivative_pricing | 143 | 143 | yes (subset) | **missing** | ✅ | ✅ | ✅ | ❌ not done |
| risk_management | 165 | 163 | yes (subset) | **missing** | ✅ | ✅ | ✅ | ❌ not done |
| quantum_ml_finance | 310 | 310 | yes (subset) | **missing** | ✅ | ✅ | ✅ | ❌ not done |
| fraud_detection | 104 | 104 | yes (subset) | **missing** | ✅ | ✅ | ✅ | ❌ not done |
| trading_execution | 43 | 43 | yes (subset) | **missing** | ✅ | ✅ | ✅ | ❌ not done |
| credit_lending | 63 | 63 | yes (subset) | **missing** | ✅ | ✅ | ✅ | ❌ not done |
| simulation_monte_carlo | 217 | 216 | yes (subset) | **missing** | ✅ | ✅ | ✅ | ❌ not done |

Notes:
- Codes / memos counts exceed 654 because multi-silo papers are projected (overlay) into multiple silo folders; central `papers/` holds 654 unique A1 + 654 A2 + 108 L3.
- `risk_management` and `simulation_monte_carlo` show a 1-2 file gap between codes and memos — minor; flag for sweep.
- "yes (subset)" for L3 means the silo contains some of the 108 L3 records via fan-out projection; no silo received its own dedicated adversarial sample.

**Aggregate manual-review evidence**: `~15 / 654 = 2.3 %` papers reviewed against source PDF, with no rubric. Plan called for 10 % rubric-scored review (Checklist 3.10) plus per-paper R1 disposition (Checklist 4.1–4.5). **Both targets unmet**.

---

## 4. Compliance against the 5 pillars

| Pillar | Status | Evidence | Gap |
|---|---|---|---|
| **P1 — Declaration** | ⚠️ Drift | `campaign_manifest.json` declares models / prompt / temperature; `FREEZE.md` declares freeze; `AUDIT_LOG.md` documents pilot→production trajectory | No manuscript-side AI Use Declaration appendix exists yet (`manuscript/04_Appendix/` pending; tracked as GL-12/GL-13 in Wave 3). For *this audit's scope* the s4 self-declaration is sufficient; the manuscript declaration is a downstream gap |
| **P2 — Role framing** | ⚠️ Drift | Documentation consistently says "LLM produced candidates, researcher reviews"; writing-guide `R-03` correctly frames Phase 3 as LLM-driven coding under researcher acceptance | Acceptance gesture (`reviewed/` move) was never operationalised. Without it, the "researcher reviews" claim relies on a free-text spot-check note in `AUDIT_LOG.md`. Defensible-but-thin |
| **P3 — Audit trail** | ✅ Strong | Per-call prompt/rendered/raw/meta/sanitize siblings; `campaign_manifest.json` with `git_commit`, `config_hash`, `prompt_version`, model identity; `code_memo_index.json` per silo; central `papers/` holds canonical A1/A2/L3 | None blocking. Minor: `s4_thematic_coding/cross_silo/` is an empty `.gitkeep` directory that should either be populated or removed to avoid confusion with `s5_cross_silo/` |
| **P4 — Reproducibility** | ⚠️ Drift | Models pinned, prompts SHA-locked, temperature 0, response_format JSON, API version recorded, git commit recorded | **No seed** in s4 manifest (s2 has `seed: 42`); `top_p` / `max_tokens` not recorded. Azure OpenAI seed support is best-effort but absence is reportable. Drafting assistance (R-04) explicitly waives seed; analytical Phase 3 should not |
| **P5 — Validation / bias** | ⚠️ Drift | L3 adversarial 108/654 = 16.5 % (exceeds plan); B2 rubric script exists; c2 grounding check per silo; B1 enforces `min_papers_per_theme=3`; Overlay re-read for multi-silo papers (1009 calls) | (a) L3 results not aggregated; no fail-rate, no per-silo κ. (b) Researcher rubric-scored review at <3 % vs. 10 % plan. (c) No inter-rater (Aleix vs. Vallahrich) coding overlap on any sample. (d) No bias audit checking whether one PD over-attracts certain themes |

**Roll-up**: 1 ✅, 4 ⚠️, 0 ❌. No examiner-fatal violation; one defensibility risk concentrated on P5 (validation evidence is thinner than the captured artefacts deserve).

---

## 5. Gap list with severity

### P0 — blockers (must close before submission)

- **G-01 — Researcher-acceptance evidence (R1) is not materialised.** No `reviewed/` directory in any silo; `EXECUTION_CHECKLIST.md` Phase 4 (4.1–4.5) all unchecked. Defence vulnerability under Pillars 2 + 5 (the "LLM as assistant" framing leans on this gesture). *Cross-cutting*: also impairs writing-guide `R-03` defence and Appendix H drafting (GL-12).

### P1 — important (close before chapter drafting locks)

- **G-02 — Researcher rubric-scored sample below plan.** ~~~15 / 654 papers (~2.3 %) reviewed informally; plan = ≥10 % with rubric (`Checklist 3.10`). Pillar 5 evidence is currently a one-line free-text approval, insufficient for the L4 audit promised in `AUDIT_LOG.md`.~~ **CLOSED 2026-05-08:** R1 stratified review executed at 153/1291 = 11.85 % per-paper coverage (target ≥10 %); all 8 silos at 10.0–18.6 %; four-axis rubric-guided per-paper decisions; verdicts approved 69 / approved_with_caveat 81 / requires_revision 2 / flag_for_pull 1. Artefacts: per-silo `r1_review.jsonl` + `_disposition.json` v2 + `s4_thematic_coding/r1_review_summary.json`. See §10 closure log.
- **G-03 — L3 adversarial findings never aggregated.** 108 `_l3.json` files exist; no script, table, or markdown summarises agree/disagree counts, fail categories, or per-silo distribution. Pillar 5 capture without synthesis.
- **G-04 — Reproducibility metadata incomplete.** `campaign_manifest.json` lacks `seed`, `top_p`, `max_tokens`. s2 sets the precedent (`seed: 42`); s4 should match. Examiner question 4 ("how reproducible?") cannot cite a seed today.

### P2 — nice-to-have (polish before submission)

- **G-05 — A3 contradiction scan never run.** Prompt committed; no outputs; checklist 5.5 unchecked. Either run or formally retire (with justification) to keep the audit trail honest.
- **G-06 — `s4_thematic_coding/cross_silo/` is a dead directory.** Empty `.gitkeep`; the real cross-silo work lives in `s5_cross_silo/`. Either populate (e.g. with a stub README pointing to s5) or delete to avoid confusion in a frozen tree.
- **G-07 — Inductiveness safeguard not asserted by test.** `Checklist 3.3` says topic_tags stripped from A2 input; no `tests/` assertion confirms this. Add a single grep-style test against the rendered A2 prompt template.
- **G-08 — Codes/memos count drift in two silos.** `risk_management` 165→163, `simulation_monte_carlo` 217→216. Minor (≤2 papers each). Confirm whether intentional (paper excluded post-A1) or a fan-out gap; record in `AUDIT_LOG.md` if intentional.
- **G-09 — Per-batch B1 outputs missing for some silos at scale.** Verified `b1_batch_01` exists per silo; large silos (e.g. `quantum_ml_finance`, 310 memos) may need confirmation that all batches were sanitised. Spot-check during the G-03 aggregation.
- **G-10 — No inter-rater overlap.** Two-author thesis but no overlapping coded sample. Pillar 5 best-practice; defensible to defer with justification ("single-coder design with adversarial-LLM overlap"), but should be stated explicitly.

---

## 6. Concrete remediation actions (PROPOSED, not executed — s4 is frozen)

Each action is scoped to *minimum work to close the gap without unfreezing s4 outputs*. None of these regenerate LLM artefacts.

| Gap | Action | Output artefact | Effort |
|---|---|---|---|
| G-01 | Retroactively materialise R1 by writing one `reviewed/_disposition.json` per silo summarising the spot-check pool (paper_ids reviewed, verdict, reviewer initials, date) **and** an explicit `_unreviewed.json` listing every paper not individually reviewed, with the global "approved-as-batch" disposition. The file move is symbolic; the disposition file is the audit artefact | 8 × `s4_thematic_coding/<silo>/reviewed/_disposition.json` | 1 h |
| G-02 | Either (a) defer L4 formally to "post-freeze pre-submission validation sample" with a written disclosure in `FREEZE.md` and Appendix I, or (b) execute a 10 % rubric review now (~65 papers, single coder) and store rubric scores under `s4_thematic_coding/<silo>/reviewed/l4_rubric.json`. Recommend (a) given freeze status; promote to pre-defence task | `FREEZE.md` deferred-items entry + Appendix I bullet | 30 min if (a); 6-8 h if (b) |
| G-03 | Add `scripts/aggregate_l3.py` that iterates `papers/*_l3.json` and emits `s4_thematic_coding/output/l3_summary.json` (per-silo agree/disagree counts, top fail categories) + a one-page `s4_thematic_coding/L3_SUMMARY.md`. Pure read-only over existing artefacts | `output/l3_summary.json` + `L3_SUMMARY.md` | 1 h |
| G-04 | Patch `campaign_manifest.json` with a `parameters_used` block recording the actual top_p / max_tokens / seed values from the run scripts (read from `scripts/run_production.py` defaults). If seed was not set, record `seed: null` and add a sentence to `FREEZE.md` acknowledging Azure non-determinism. Does not require LLM rerun | Patched manifest + `FREEZE.md` note | 30 min |
| G-05 | Add a one-line entry under `FREEZE.md` deferred-items: "A3 contradiction scan prompt retained in `prompts/` for traceability; not executed in the v2026-05-02 freeze; disclosed as limitation in §4 methods" | `FREEZE.md` entry | 5 min |
| G-06 | Replace `s4_thematic_coding/cross_silo/.gitkeep` with a `README.md` redirecting readers to `s5_cross_silo/` | 1 README | 5 min |
| G-07 | Add `tests/test_a2_inductiveness.py` asserting `"topic_tags" not in (prompts/a2_memo_compression_v2.txt).read_text()` | 1 test | 15 min |
| G-08 | Run a single audit script comparing `papers/*.jsonl` ↔ `papers/*.json` ↔ silo overlay manifests; record discrepancies and reasons in `AUDIT_LOG.md` | Audit-log entry | 30 min |
| G-09 | Confirm via `Get-ChildItem s4_thematic_coding/<silo>/themes/b1_batch_*.json` for the four largest silos that the batch count × `min_papers_per_theme` covers the memo count; record in `AUDIT_LOG.md` | Audit-log entry | 15 min |
| G-10 | Add a paragraph to Methodology §4.5 (or wherever Phase 3 is presented) acknowledging single-coder design with LLM-adversarial overlap as the bias-mitigation substitute for inter-rater κ. Frame as preregistered design choice, not omission | Manuscript text + writing-guide cross-ref | 30 min |

**Total**: ~5 h to close everything except G-02 option (b). Recommendation: do G-01 / G-03 / G-04 / G-06 / G-07 immediately (P0 + cheap P1/P2); defer G-02 to pre-defence with a written disclosure.

---

## 7. Cross-phase invariants — verified

- ✅ s4 silo set = 8 (PO, DP, RM, QML, FD, TE, CL, SMC) matches `shared/config/silo_inclusion.json` and the v2.0 unified taxonomy with PD-08 (cryptography) and PD-10 (insurance, absorbed into PD-03) excluded.
- ✅ Manifest `silos[]` order matches the canonical PD-01..PD-09 minus PD-08 ordering documented in `FREEZE.md`.
- ✅ Excluded paper_ids (5 corrupted PDFs) consistent between `campaign_manifest.json` and `AUDIT_LOG.md`.
- ✅ Writing-guide `R-03` framing ("LLM-driven inductive coding under researcher acceptance") matches what s4 actually does — provided G-01 is closed.
- ✅ Active silo count (8) matches `consensus_summary.filtered.json` downstream in s3.

---

## 8. Examiner-readiness check (subset relevant to s4)

| Examiner question | Can s4 answer it today? | Citable evidence |
|---|---|---|
| Which model coded Phase 3? | ✅ | `campaign_manifest.json` |
| Why two models (mini for A1, gpt-5.1 for A2)? | ✅ | `docs/AUDIT_LOG.md` 2.13–2.19 + `model_comparison.py` outputs |
| What's the LLM error rate on coding? | ⚠️ | L3 raw exists (108 papers); no aggregate. **G-03** closes this |
| How was researcher acceptance recorded? | ❌ | Only the AUDIT_LOG free-text approval. **G-01** closes this |
| Could another researcher rerun Phase 3? | ⚠️ | Yes given prompts + models + temperature + git commit; **no seed**. **G-04** closes this |
| What was excluded and why? | ✅ | Manifest + AUDIT_LOG |
| Where is the contradiction scan? | ❌ | Prompt only. **G-05** documents the deferral |

---

## 9. Decision needed from researchers

1. Confirm freeze posture: do the P0/P1 actions (G-01..G-04) under "documentation-only patch to a frozen tree" rule (allowed by `FREEZE.md` since no LLM artefact regenerates), or unfreeze for G-02(b)?
2. Confirm whether to execute the 10 % L4 rubric (G-02 option b) before defence, or defer with disclosure.
3. Confirm whether to run A3 contradiction scan (G-05) or formally retire it.

---

## 10. Closure log — 2026-05-03 (afternoon)

All actions documentation/test-only; no s4 LLM artefact regenerated; freeze intact.

| Gap | Severity | Status | Artefact |
|---|---|---|---|
| G-01 | P0 | **closed** | 8 × [`s4_thematic_coding/<silo>/reviewed/_disposition.json`](s4_thematic_coding/) (generator: [`scripts/write_r1_dispositions.py`](scripts/write_r1_dispositions.py)) |
| G-02 | P1 | **closed** | 8 × [`s4_thematic_coding/<silo>/reviewed/_disposition.json`](s4_thematic_coding/) v2 schema + per-silo [`r1_review.jsonl`](s4_thematic_coding/) decision logs + [`s4_thematic_coding/r1_review_summary.json`](s4_thematic_coding/r1_review_summary.json) aggregate. R1 stratified review at 153/1291 = 11.85 % (target ≥10 %); per-silo coverage 10.0–18.6 %. Verdict distribution: approved 69 / approved_with_caveat 81 / requires_revision 2 / flag_for_pull 1. Sampler [`scripts/r1_sample_worklist.py`](scripts/r1_sample_worklist.py); reviewer skill [`.github/skills/p3-r1-review/SKILL.md`](../.github/skills/p3-r1-review/SKILL.md); generator [`scripts/refresh_r1_dispositions.py`](scripts/refresh_r1_dispositions.py). |
| G-03 | P1 | **closed** | [`s4_thematic_coding/L3_SUMMARY.md`](s4_thematic_coding/L3_SUMMARY.md) + [`s4_thematic_coding/output/l3_summary.json`](s4_thematic_coding/output/l3_summary.json) (generator: [`scripts/aggregate_l3.py`](scripts/aggregate_l3.py)) |
| G-04 | P1 | **closed** | `parameters_used` block patched into [`s4_thematic_coding/campaign_manifest.json`](s4_thematic_coding/campaign_manifest.json); reproducibility caveats in [`FREEZE.md`](FREEZE.md) |
| G-05 | P2 | **disclosed-deferred** | [`FREEZE.md`](FREEZE.md) GL-10 caveats — A3 contradiction scan retained but not executed |
| G-06 | P2 | **closed** | [`s4_thematic_coding/cross_silo/README.md`](s4_thematic_coding/cross_silo/README.md) (`.gitkeep` removed) |
| G-07 | P2 | **closed** | [`tests/test_a2_inductiveness.py`](tests/test_a2_inductiveness.py) — 2 assertions, both pass |
| G-08 | P2 | **closed** | [`docs/AUDIT_LOG.md`](docs/AUDIT_LOG.md) 2026-05-03 entry — drift = 3 leftover A1 `.jsonl` for excluded papers |
| G-09 | P2 | **closed** | [`docs/AUDIT_LOG.md`](docs/AUDIT_LOG.md) 2026-05-03 entry — every silo has 1 B1 batch, full coverage |
| G-10 | P2 | **disclosed-deferred** | [`FREEZE.md`](FREEZE.md) GL-10 caveats — single-coder design with LLM-adversarial substitute |

**Net 5-pillar standing after closure**:

| Pillar | Before | After |
|---|---|---|
| P1 — Declaration | ⚠️ Drift | ⚠️ Drift (Appendix H still pending; tracked under GL-12) |
| P2 — Role framing | ⚠️ Drift | ✅ Strong (R1 disposition materialised) |
| P3 — Audit trail | ✅ Strong | ✅ Strong |
| P4 — Reproducibility | ⚠️ Drift | ✅ Strong (parameters block + sampling seed disclosed) |
| P5 — Validation | ⚠️ Drift | ✅ Strong-with-caveat (L3 aggregated; L4 deferred with disclosure) |

**Pre-existing test note**: `tests/test_release_invariants.py::test_filtered_consensus_post_dates_raw_consensus` fails with a 2.6 ms mtime drift between two s3 files. Unrelated to GL-10. Fix by running `python p3_thematic_synthesis/s3_quantum_advantage/scripts/filter_consensus.py`.

---

*End of GL-10 audit. P0/P1 closed; deferrals disclosed; freeze intact.*
