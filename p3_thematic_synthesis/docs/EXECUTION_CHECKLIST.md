# Phase 3 — Step-by-Step Execution Checklist

> **Status note (2026-05-10): historical execution checklist.** This file
> preserves the 2026-04-22 working plan and should not be read as current
> submission blockers. Use [../FREEZE.md](../FREEZE.md),
> [../P3_AUDIT_STATUS.md](../P3_AUDIT_STATUS.md), and
> [../../docs/PROJECT_STATE.yaml](../../docs/PROJECT_STATE.yaml) for
> current status.
> The phase ordering below is a historical working queue. Its Phase 4/5 order
> is superseded by the canonical P3 process contract:
> **A1 -> L1 -> A2 -> L2 -> L3 -> A3 -> R1**. In the frozen submission state,
> A3 was retained/deferred and R1 was executed later as GL-10 post-freeze
> validation.
>
> Last updated: 2026-04-22

---

## Phase 0: Pre-Registration & Cleanup

- [x] **0.1** Folder cleanup (archive legacy, remove obsidian)
- [x] **0.2** Clean silo configs (remove quantum-annealing/qubo)
- [x] **0.3** Create new directory structure (s1-s5, coding, prompts, scripts)
- [x] **0.4** Update P3 README
- [x] **0.5** Create silo_inclusion.json (8 active silos)
- [x] **0.6** Update PROJECT_STATE.yaml
- [ ] **0.7** Update methodology chapter §4.5 (deferred — before submission)
- [ ] **0.8** New §4.6 Phase 4 methodology (deferred — before submission)
- [ ] **0.9** Expand §4.7 AI declaration (deferred — before submission)
- [ ] **0.10** Create Appendix H AI Use Declaration (deferred — before submission)
- [ ] **0.11** Update METHODOLOGY_DESIGN.md (deferred — before submission)
- [ ] **0.12** Frozen output acceptance record (both researchers sign FROZEN.md)

## Phase 1: Pipeline Infrastructure

- [x] **1.1** Bibliometric landscape script (Step 3.1.b) → 7 JSON outputs
- [x] **1.2** Per-silo inclusion lists (Step 3.2) → 8 silo JSONs
- [x] **1.3** Text-readiness gate (Step 3.2b) → 97.2% usable
- [x] **1.4** LLM prompt design (A1/A2/L3/A3/B1/B2/C1) → 7 prompts
- [x] **1.5** Pipeline runner script (run_thematic_pipeline.py)
- [x] **1.6** Pilot analysis script (pilot_analysis.py)
- [x] **1.7** L4 audit review generator (generate_audit_reviews.py)
- [x] **1.8** Model comparison tool (model_comparison.py)
- [x] **1.9** Production architecture documented (PRODUCTION_ARCHITECTURE.md)

## Phase 2: Pilot & Model Selection

- [x] **2.1** Pilot iter_01: gpt-5.1, pre-fix prompts (30% parse, baseline)
- [x] **2.2** Pilot iter_02: gpt-5.4-mini, pre-fix prompts (86% parse, baseline)
- [x] **2.3** Pilot iter_03: gpt-5.4-mini, v1+json fix (84% parse, 96.8% L1)
- [x] **2.4** Pilot iter_04: gpt-5.1, v1+token fix (100% parse, 95.3% L1, 0 empty)
- [x] **2.5** Pilot iter_05: gpt-5.4-mini, v2 prompts (100% parse, 97.2% L1, 0 empty) ★ BEST MINI
- [x] **2.6** Pilot iter_06: gpt-5.4-mini, v3 prompts (same as v2 — v3 didn't help)
- [x] **2.7** Pilot iter_07: gpt-5.1, v2 prompts (90.9% parse — v2 regressed 5.1)
- [x] **2.8** Pilot iter_08: both models, v2.1 prompts (mini 100%/0 empty, 5.1 86%/6 empty)
- [x] **2.9** Pilot iter_09: gpt-5.4-mini, v2.2 L3 materiality (L3 still flags 98% — structural)
- [x] **2.10** Run pilot_analysis.py → 10 iterations compared
- [x] **2.11** Deep analysis (PILOT_DEEP_ANALYSIS.md) — mini v2 wins production
- [x] **2.12** Preliminary model decision: gpt-5.4-mini with v2 prompts (A1/A2), L3 as review tool not filter
- [x] **2.13** Run model_comparison.py → comparison_01 (mini v2 vs gpt-5.1 v1) + comparison_02 (hybrid A2 test)
- [x] **2.14** Pilot iter_10: hybrid (mini A1 → gpt-5.1 A2/L3) — 44/44, 0 errors
- [x] **2.15** Deep A1 quality assessment (Claude Opus 4.6, 10 papers vs source text): mini 4.0/5, 5.1 3.9/5
- [x] **2.16** Prompt v4 experiment: tested 3 approaches (A/B/C) on 5 papers → no improvement in pipeline
- [x] **2.17** iter_11 (mini v4): 14/44 papers completed, confirmed no improvement — stopped to save tokens
- [x] **2.18** ⚠️ Researcher reviewed comparison_01 (notes on 10 papers) + comparison_02 (assessed)
- [x] **2.19** Final production config confirmed (2026-04-22):
  - A1: gpt-5.4-mini + v2 prompt (97.4% L1, 0 hallucinations, 4.0/5.0 quality)
  - A2/L3: gpt-5.1 hybrid (wins 8/10 depth, 31% fewer L3 problems)
  - 3 papers excluded (corrupted extraction): 567b25a75e80, 9a926e905d18, dc60950e60b9
  - Final corpus: 661 papers, ~2,631 API calls

## Phase 3: Production Run

- [ ] **3.1** Build production pipeline (central + silo overlay architecture)
- [ ] **3.2** Create global paper manifest (661 papers, deterministic batching)
- [ ] **3.3** Strip topic_tags from A2 enrichment input (inductiveness safeguard)
- [ ] **3.4** ~~Text chunking~~ Not needed — 3 overflow papers excluded (corrupted extraction)
- [ ] **3.5** Run central A1 (661 papers, gpt-5.4-mini, v2 prompt, --workers 8)
- [ ] **3.6** Run central A2+L3 (661 papers, gpt-5.1 hybrid, v2 prompt, --workers 8)
- [ ] **3.7** Run silo overlay memos (~648 calls, gpt-5.1)
- [ ] **3.8** Run fan-out (project central outputs → silo directories)
- [ ] **3.9** Verify: campaign manifest + batch manifests + projection manifests
- [ ] **3.10** ⚠️ L4 AUDIT: Generate 10% sample per silo, review, collect scores
- [ ] **3.11** Check decision gates (L1 <10% fail, JSON >90%)

## Phase 4: Researcher Review (R1)

- [ ] **4.1** Tier A papers: full memo review + spot-check codes
- [ ] **4.2** Tier B papers: skim memo, review L3 flags only
- [ ] **4.3** Set disposition per paper: approved / approved_with_edits / manual_read / excluded
- [ ] **4.4** Write REVIEW_LOG.md per silo
- [ ] **4.5** ⚠️ GATE: Only approved/approved_with_edits memos proceed to B1/B2

## Phase 5: Theme Generation (B1/B2)

- [ ] **5.1** Run B1 batch descriptive themes per silo (batches of 20-30 memos)
- [ ] **5.2** Run B2 silo-level theme merge + analytical themes
- [ ] **5.3** ⚠️ RESEARCHER GATE: Review B2 themes, accept/reject/restructure
- [ ] **5.4** Log theme decisions in REVIEW_LOG.md
- [ ] **5.5** Run A3 contradiction scan per silo (rolling at 50% + final at 100%)

## Phase 6: Chapter Writing (R2)

- [ ] **6.1** Per-silo chapters (8 × `manuscript/03_Chapters/06_silos/<silo>.tex`)
- [ ] **6.2** Each chapter follows template: landscape → methods → results → verdicts → white spots → P4 link
- [ ] **6.3** ⚠️ NO VERBATIM AI TEXT in chapters (CBS rule)

## Phase 7: Cross-Silo Synthesis (C1/C2/C3)

- [ ] **7.1** Run C1 cross-silo pattern assembly
- [ ] **7.2** Construct white-spot matrix (PD × SA co-occurrence gaps)
- [ ] **7.3** ⚠️ C2 RESEARCHER: Adjudicate patterns, select white spots, back-justify P4
- [ ] **7.4** Write cross-silo chapter (06_Phase3_Synthesis.tex)
- [ ] **7.5** Write DECISION_LOG.md in cross_silo/

## Final Checks

- [ ] **F.1** All REVIEW_LOG.md files complete
- [ ] **F.2** All audit_results.json files collected
- [ ] **F.3** iteration_log.jsonl complete with all runs
- [ ] **F.4** Methodology chapter §4.5/4.6/4.7 matches actual process
- [ ] **F.5** Appendix H (AI Use Declaration) complete and signed
- [ ] **F.6** METHODOLOGY_DESIGN.md updated
- [ ] **F.7** PROJECT_STATE.yaml reflects final status
- [ ] **F.8** Professor meeting: confirm AI disclosure approach

---

## ⚠️ Symbols

- [x] = completed
- [ ] = pending
- ⚠️ = requires researcher action (cannot be automated)
