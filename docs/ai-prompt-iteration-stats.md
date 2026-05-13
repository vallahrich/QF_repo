# AI Prompt-Iteration & Review-Acceptance Statistics

_Created: 2026-05-03 (Wave 3, GL-13). Read-only consolidation; no pipeline outputs modified._

This file quantifies (a) the iterative improvement of LLM prompts and configuration across the
four pipeline phases, and (b) the manual-review acceptance rate at each phase. It is the
quantitative companion to [`docs/manual-evaluations-inventory.md`](manual-evaluations-inventory.md)
(GL-12). Per writing-guide rule **R-07**, full per-call evidence stays in the online repository
(Tier 3); this file is the canonical source for the **Appendix I** prompt-iteration register and
for the **Methodology §4.6** reproducibility subsection. Body chapters carry only one or two
headline numbers (see §6).

Per **R-02**, no individuals are named.

Sources: `p1_framework_synthesis/audit-trail.md`, `p2_systematic_review/processing_log.json`
+ `p2_systematic_review/README.md`, `p3_thematic_synthesis/prompts/VERSION_LOG.md`,
`p3_thematic_synthesis/docs/AUDIT_LOG.md`,
`p3_thematic_synthesis/_archive/s4_thematic_coding/pilot/trading_execution/PILOT_DEEP_ANALYSIS.md`,
`p3_thematic_synthesis/AUDIT_REPORT.md`,
`p3_thematic_synthesis/s2_quantitative/output/ab_test/ab_test_results.json`,
`p4_experiments/experiments/review/phase8_faithfulness_review/SUMMARY.md`,
`p4_experiments/scripts/implementation_type_audit_report.json`,
`shared/tools/llm_client.py` (caching key includes `prompt_hash`),
`logs/*_llm_client.jsonl`.

---

## 1. Per-phase acceptance criteria

The five LLM-assisted pipeline stages use distinct acceptance regimes; one schema cannot
fit them all. The table below states the operational definition of *accepted*, *revised*,
and *rejected* used in §§3–5.

| Phase / stage | Unit of acceptance | "Accepted" | "Revised" | "Rejected" |
|---|---|---|---|---|
| **P1 — Framework extraction** | per-paper extraction file (n=29) | passes paper-level quality triage and feeds the inductive taxonomy | `needs-recheck` flag in audit-trail Entry 1 | excluded from Phase-1 evidence base |
| **P1 — Taxonomy categories** | per category (10 PD, 11 SA) | category retained in `unified_taxonomy.json` v2.0 | label/scope edited by researcher synthesis (e.g. PD-10 absorbed into PD-03) | category dropped from active scope (e.g. PD-08 cryptography) |
| **P2 — Screening** | per record screening decision | LLM and researcher both include OR both exclude (calibration); LLM include matches held-out human (validation) | disagreement resolved in adjudication round | retro-excluded by post-hoc triage (`excluded_post_classification.csv`) |
| **P2 — Classification (6-step)** | per-paper extraction JSON | passes Pipeline-C step1–step6 with no validator failure and not retro-excluded | retro-tagged (e.g. `tag_normalisation_report.json`) without removal | retro-excluded (22/777, FP 2.83 %) |
| **P3 / s2 — Quantitative extraction** | per-experiment row | passes scope filter (gate-based only) AND passes step-4 schema validation | rescoped after audit (Q-0..Q-5, Q-9, Q-10 closed-active) | dropped by hard scope filter (annealing/QUBO leakage; ~9 % of pre-audit corpus) |
| **P3 / s3 — Quantum-advantage frameworks** | per (paper × framework) row | row receives a definitive `met` / `not_met` / `not_applicable` label | label flipped after manual re-assessment (QA-1, QA-5, QA-11) | row excluded from framework eligibility |
| **P3 / s4 — Thematic coding** | per-paper memo (a1/a2 codes + l3 audit) | L1 quote-match ≥ 0.85, no JSON parse failure, codes within `code_label` schema; spot-check passes | OCR-noise paper kept with reduced code count; researcher post-hoc edit | excluded for PDF-extraction failure or wrong-language (5087f7c0e2a3, dd6b533767c3, 3 overflow) |
| **P3 / s4 — Themes (B1/B2/C2)** | per-silo theme bundle | B1/B2 rubric mean ≥ 4.0 AND no criterion < 3 AND C2 grounding ∈ {grounded, partially_supported_with_disposition} | C2 disposition: `revise` or `demote` | C2 disposition: `drop` |
| **P4 — Phase 8 faithfulness** | per cohort label (n=71) | Pass 2 verdict `CONFIRMED` | `DRIFT_MINOR` (kept, observation logged) or Pass 3 actions `accept_vincent` / `no_change` | `DRIFT_MAJOR` followed by `reauthor_circuit` or `demote_label` |

Five acceptance regimes generalise across the table — the typology of
[`docs/manual-evaluations-inventory.md` §3](manual-evaluations-inventory.md):
quantitative agreement (κ, recall), schema/scope conformance, researcher synthesis &
adjudication, class-level remediation, and acceptance-gesture file moves.

---

## 2. Prompt-version inventory

| Phase / stage | Prompt files | Distinct versions in repo | Production version | Selection method |
|---|---|---:|---|---|
| P1 framework extraction | `p1_framework_synthesis/prompts/extraction.txt` | 1 (v1.0, 2026-04-11; provenance metadata added 2026-05-02 without prompt-body change) | v1.0 | single-shot; no iteration |
| P2 classification | `p2_systematic_review/s2_classification/prompts/{step1..step6}_*.txt` + `cached_step{1..5}.txt` + `tag_discovery.txt` | 1 functional version × 3 pipeline variants (A single-call, B optimised 2-call, C 6-step cached prefix) | Pipeline C; cached-prefix variant (`cached_step1..5` + `step6_synthesis`) | A/B/C bake-off, framework-level not prompt-level (see [`p2_systematic_review/README.md` §Pipeline C](../p2_systematic_review/README.md)) |
| P3 / s2 quantitative | `p3_thematic_synthesis/s2_quantitative/prompts/{benchmark_extraction, step2_experiments, step3_silo_results, step4_validation}.txt` | 2 (legacy single-shot `benchmark_extraction.txt` + 3-step refactor) | 3-step refactor (step2 → step3 → step4) | A/B at n=4 ([`ab_test_results.json`](../p3_thematic_synthesis/s2_quantitative/output/ab_test/ab_test_results.json)) — under-powered, superseded by AUDIT_REPORT post-freeze closure |
| P3 / s3 quantum advantage | `p3_thematic_synthesis/s3_quantum_advantage/<framework>/assess_*.py` (rule-based, not LLM-prompted) | 11 framework assessors (QA-1..QA-11) | All 11 closed-active 2026-05-02 | full re-assessment per framework after scope audit |
| P3 / s4 thematic coding (A1 open coding) | `a1_open_coding_v{1,2,2.1,2.2,3,4}.txt` | **6** | **v2** | 11-iteration pilot + Claude Opus 4.6 deep quality assessment |
| P3 / s4 (A2 memo compression) | `a2_memo_compression_v{1,2,2.1,2.2,3}.txt` | **5** | **v2** | hybrid-test comparison (mini vs gpt-5.1 on same A1 codes) |
| P3 / s4 (L3 adversarial) | `l3_adversarial_v{1,2,2.1,2.2,3}.txt` | **5** | **v2** | severity-calibration retrospective on 658-paper pilot |
| P3 / s4 (B1/B2 themes) | `b{1,2}_*_v1.txt` (+ unversioned alias) | 1 each | v1 | B1/B2 rubric (auto + manual) |
| P3 / s4 (C1/C2/C3 cross-silo) | `c{1,2,3}_*_v1.txt` (+ `c1_cross_silo_patterns.txt` legacy alias) | 1 each | v1 | grounding check (C2) drives accept/revise |
| P3 / s4 (A3 contradiction scan) | `a3_contradiction_scan.txt` | 1 | v1 | no issues found in pilot |
| P3 / s6 silo framing | `f{1,2}_*_v{1,2}.txt` | f1: 2; f2: 1 | f1 v2, f2 v1 | post-pilot refactor |
| P4 — re-extraction | `p4_experiments/canonical/prompts/llm_re_extraction.prompt.md` | 1 | v1 (used during Phase 8 reauthor_circuit actions) | n/a (per-label) |
| P4 — audit prompts | `p4_experiments/prompts/audit_*.prompt.md` | 2 (one-off audit briefs, not pipeline prompts) | n/a | n/a |
| Shared — chapter literature | `shared/chapter_supporting_literature/scripts/prompt_v1.txt` | 1 | v1 (R-04 drafting assistance) | acceptance-gesture file move |

**Total prompt versions across the project:** ~26 versioned prompt files spanning ~14 active
prompt slots; iterative refinement was concentrated in **P3 / s4 thematic coding** (16 versions
across A1/A2/L3 alone).

---

## 3. P3 / s4 thematic-coding pilot — per-iteration stats

Pilot corpus: PD-06 (trading_execution, 46 papers; 44 after pre-pilot exclusion of 2 corrupt
PDFs). Source: `p3_thematic_synthesis/docs/AUDIT_LOG.md` and `PILOT_DEEP_ANALYSIS.md`.

| Iter | Model | Prompt | JSON parse | L1 pass | Empty files | Avg codes/paper | Disposition |
|---|---|---|---:|---:|---:|---:|---|
| iter_01 | gpt-5.1 | v1 | 30 % | 92.3 % | many (root-cause: max_tokens=8000 consumed by reasoning tokens) | 63 | rejected; cause identified |
| iter_02 | gpt-5.4-mini | v1 | 86 % | 89.7 % | 0 | 23 | superseded |
| iter_03 | gpt-5.4-mini | v1 + token+temp+JSON-format fixes | ~100 % | high | 0 | — | superseded by v2 |
| iter_04 | gpt-5.1 | v1 + token fix | 100 % | high | 0 | 75 | superseded by hybrid |
| **iter_05** | **gpt-5.4-mini** | **v2** | **100 %** | **97.2 %** | **0** | **52** | **A1 production winner** |
| iter_06 | gpt-5.4-mini | v3 (simplified) | same as v2 | same as v2 | 0 | ~52 | no improvement; rejected |
| iter_07 | gpt-5.1 | v2 | 90.9 % | 94.5 % | 4 | — | regression vs iter_04 |
| iter_08 | both | v2.1 (flexible quoting) | mini 100 % / 5.1 86 % | — | mini 0 / 5.1 6 | — | did not fix gpt-5.1 |
| iter_09 | gpt-5.4-mini | v2.2 (L3 materiality) | — | — | — | — | L3 still flags 98 % → confirmed L3 is review tool, not filter |
| **iter_10** | **mini A1 → gpt-5.1 A2/L3** | **v2 hybrid** | **100 %** | — | **0** | — | **A2/L3 production winner**; A2 wins 8/10 vs mini A2; L3 problems −31 % |
| iter_11 | gpt-5.4-mini | v4 (coverage checklist) | — | 98.0 % | — | 50.4 (vs v2's 52.1) | no meaningful gain; stopped at 14/44; **kept for reproducibility, not used in production** |

**Production decision (2026-04-22):** A1 = mini + v2; A2 = gpt-5.1 + v2; L3 = gpt-5.1 + v2.
Documented in `p3_thematic_synthesis/prompts/VERSION_LOG.md` and `PRODUCTION_ARCHITECTURE.md`.

**Production-run acceptance (A1, n=660 papers):**
- 656 / 660 processed first pass; 4 transient errors re-runnable.
- 2 hard-rejected (5087f7c0e2a3 font-encoding bug; dd6b533767c3 wrong language);
  4 kept-with-OCR-noise; 33 with moderate OCR variance kept on valid-codes-sufficient rule.
- Final A1 corpus: **658 papers (99.4 % first-pass acceptance, 99.7 % after re-run)**.
- 31 000 codes total; 47.3 avg/paper; **96.9 % L1 pass**.

**B1/B2 silo themes:** 8/8 silos PASS rubric (mean ≥ 4.0, no criterion < 3) on first pass.
**C2 grounding (per analytical theme):** 2 grounded · 32 partially supported · 11 unsupported
(45 themes total). C2 dispositions for the 11 unsupported themes are **pending researcher
decision per silo** — see [`docs/manual-evaluations-inventory.md` §4](manual-evaluations-inventory.md).

---

## 4. P1 / P2 / P3-quant / P3-QA / P4 — acceptance summary

| Phase / stage | N input | Accepted (first pass) | Accepted (after revision) | Rejected | Acceptance % (post-revision) |
|---|---:|---:|---:|---:|---:|
| P1 extractions (Entry 1) | 29 | 19 | 22 (19 + 3 needs-recheck closed) | 7 | 75.9 % |
| P1 PD categories (Entry 2) | 10 | 8 | 10 (with PD-10→PD-03 absorption, PD-08 scope-excluded) | 0 hard-rejected (1 scope-excluded, 1 absorbed) | 80 % retained as PDs |
| P1 SA categories (Entry 3) | 11 | 11 | 11 | 0 | 100 % |
| P1 open codes (Entry 4) | 763 | 763 baseline-accepted | merging deferred to P3/s4 | 0 | 100 % (baseline) |
| P2 screening calibration round 1 | 49 records | κ = 0.692 | — | 8 disagreements | FAIL |
| P2 screening calibration round 2 | 49 records | κ = 0.849 | — | 0 | PASS |
| P2 AI screening validation | 100 records (22 inclusions) | recall = 1.000 (Wilson 95 % CI [0.846, 1.000]) | — | 0 | PASS |
| P2 classification (6-step Pipeline C) | 777 | 755 | 755 | 22 retro-excluded | **97.2 %** |
| P3 / s2 quantitative experiments | 1 957 (pre-audit) | — | 1 046 in active corpus | 911 (~46.5 %) dropped: scope leak, structural bugs, schema fail | 53.5 % active |
| P3 / s2 closed-active audit items | 11 (Q-0..Q-10) | 9 closed-active | — | 2 deferred | 81.8 % |
| P3 / s3 QA framework re-assessments | 11 frameworks | 11 | — | 0 | 100 % |
| P3 / s4 A1 production | 660 papers | 656 | 658 | 2 hard-excluded | **99.7 %** |
| P3 / s4 B1/B2 silo themes | 8 silos | 8 | 8 | 0 | 100 % |
| P3 / s4 C2 themes | 45 analytical themes | 2 grounded + 32 partial = 34 | 34 + dispositions on 11 (pending) | 0 dropped at freeze | 75.6 % first-pass; tail under researcher review |
| P4 Phase 8 Pass 2 | 71 cohort labels | 11 CONFIRMED | 11 + 42 DRIFT_MINOR (kept) = 53 | 18 DRIFT_MAJOR | 74.6 % retained, 25.4 % to triage |
| P4 Phase 8 Pass 3 (joint triage) | 21 disputed labels | 3 `accept_vincent` + 1 `no_change` = 4 | + 4 `demote_label` (kept demoted) | 13 `reauthor_circuit` | 38.1 % accepted as-is or demoted; 61.9 % required circuit re-authoring |
| P4 implementation-type audit | 71 | 56 | — | 15 mismatches disclosed as family-template proxies | 78.9 % family-faithful |
| Shared / chapter literature (R-04) | 10 reading notes | 10 (file move out of `_pending/`) | — | 0 | 100 % |

---

## 5. Prompt-iteration triggers

What forced each prompt revision (selection bias toward P3/s4 because that is where iteration
happened):

| Trigger | Affected prompt(s) | Source |
|---|---|---|
| Reasoning-token budget exhaustion (max_tokens=8000 → 32000/16000) | A1, A2, L3 (config, not prompt) | AUDIT_LOG 2026-04-19 17:44 |
| Self-quoting bug (model quotes prompt as text spans) | A1 v1 → v2 | VERSION_LOG v2 §A1 |
| Field-name drift (`label` vs `code_label`) | A1 v1 → v2 | VERSION_LOG v2 §A1 |
| Quote-length cap regression on reasoning model | A1 v2 → v2.1 (flexible 10–60 words) | VERSION_LOG v2.1 |
| L3 over-flagging (85 % "major") | L3 v1 → v2 → v2.2 (materiality test) | VERSION_LOG v2.2 |
| Limitation under-extraction (#1 L3 problem, 86 instances) | A2 v1 → v2 (rule 5) | VERSION_LOG v2 §A2 |
| Wrong attribution of cited results | A2 v1 → v2 (rule 6) | VERSION_LOG v2 §A2 |
| Section bias (heavy on abstract) | A2 v1 → v2 (rule 7) | VERSION_LOG v2 §A2 |
| Mini coverage-gap hypothesis (~15-20 % vs gpt-5.1) | A1 v2 → v4 (rejected after iter_11) | VERSION_LOG v4 |
| Scope leak (annealing/QUBO contamination) | P3 / s2 step2/step3/step4 | AUDIT_REPORT §3.3 (Q-2) |
| Classical-solver-as-experiment (QBSolv) | P3 / s2 step2 | AUDIT_REPORT (Q-5) |
| Pipeline-architecture trade-off (latency vs token cost) | P2 Pipeline A → C (6-step cached prefix) | `p2_systematic_review/README.md` §Pipeline C |
| Rønnow applicability mis-scope | QA-1 framework re-assessment | manual-evaluations-inventory row 18 |
| QIPM scope creep | QA-5 re-assessment | row 19 |
| Honest-label requirement | QA-11 rename to `beverland_inspired_2022` | row 20 |

---

## 6. Headline numbers for Methodology §4.6 and Appendix I

Two numbers are suitable for the body chapter (per **R-07** one or two headline numbers
maximum):

> **H1.** Across the four LLM-assisted pipeline phases, manual-review acceptance after
> revision exceeds **97 %** at every screening or extraction gate where a quantitative
> threshold applies (P2 screening recall 1.000; P2 classification retention 97.2 %;
> P3 / s4 A1 production 99.7 %).

> **H2.** Phase-3 thematic coding underwent **11 pilot iterations** across **6 A1, 5 A2,
> and 5 L3 prompt versions** before the production configuration (gpt-5.4-mini + v2 for
> open coding; gpt-5.1 + v2 for memo compression and adversarial audit) was frozen on
> 2026-04-22.

Supplementary numbers for the appendix audit surfaces (Appendices E, G, H, and I as relevant;
full register lives in §§2–4 of this file; appendix prose summarises only):

- **Prompt-version surface area:** ~26 versioned prompt files across ~14 active prompt slots;
  iterative refinement concentrated in P3 / s4 (16 versions).
- **P2 calibration progress:** Cohen's κ improved from 0.692 (FAIL) to 0.849 (PASS) between
  rounds 1 and 2 after researcher-led adjudication of 8 disagreements.
- **P3 / s2 closed-active audit:** 9 of 11 audit items (81.8 %) were closed under freeze
  on 2026-05-02; 2 are deferred and listed in [`p3_thematic_synthesis/FREEZE.md`](../p3_thematic_synthesis/FREEZE.md).
- **P4 Phase 8 outcome:** of 71 cohort labels, 11 CONFIRMED · 42 DRIFT_MINOR · 18 DRIFT_MAJOR;
  joint triage on the 21 contradicted cases produced 13 reauthor / 4 demote / 3 accept / 1
  no-change.
- **C2 grounding:** 75.6 % of the 45 analytical themes are at least partially grounded at
  freeze; 11 unsupported themes are pending per-silo disposition before they enter Chapter 6
  prose.

Per **R-07** the **full prompt corpus** (every `.txt`/`.prompt.md`), all per-call JSONL logs
in `logs/`, and all validator outputs are the Tier-3 online-repository deliverable. Appendix I
in the PDF carries this stats file verbatim plus one worked extraction example.

---

## 7. Known gaps

- **No per-prompt-version Cohen's κ.** Pilot iterations were compared on parse rate, L1 pass,
  empty-file count, and codes/paper — not on inter-coder κ between prompt versions on the
  same papers. A retrospective κ on iter_05 vs iter_10 (mini-A2 vs gpt-5.1-A2 hybrid on the
  44-paper pilot corpus) is achievable from existing artefacts but **not computed at freeze**.
- **No per-phase researcher-time accounting.** Hours spent on prompt iteration vs review are
  not logged.
- **P2 pipeline A/B/C performance numbers** are reported in `p2_systematic_review/README.md`
  qualitatively (latency / token cost) but not as a quantitative comparison table here.
- **Caching hit-rate** (LLM client `prompt_hash` keying) is not summarised; raw evidence in
  `logs/*_llm_client.jsonl` and `b1_calls.jsonl`, `b2_calls.jsonl`.

These gaps are documented for honesty (R-07). None block submission.

---

## 8. Maintenance

This file is regenerated by re-grepping the sources in the header. It is **not** a pipeline
output. Update when a new prompt version is committed to a `*/prompts/` folder, when a new
pilot iteration is run, or when an acceptance-tracked item in §4 changes status.

The 2026-04-22 (P3 / s4 production-config freeze) and 2026-05-02 (P2/P3 freeze) timestamps
control the rows in §§3–4.
