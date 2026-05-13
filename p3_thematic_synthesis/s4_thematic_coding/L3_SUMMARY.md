# s4 L3 adversarial-check summary

_Generated: 2026-04-22T18:58:59.081663+00:00_  
_Script: `p3_thematic_synthesis/scripts/aggregate_l3.py`_  
_Purpose: In-freeze full L3 adversarial-check coverage of the P2 corpus, executed before R1 stratified review._

_Freeze-boundary note: this 2026-04-22 full-coverage L3 aggregation/propagation pass extends the earlier 2026-04-22 sample (108/654) to 100% coverage. Both precede the R1 stratified review (2026-04-23 → 2026-04-25) and the B1/B2 theme generation (2026-04-26), and feed into the 2026-05-02 frozen thematic outputs._

## Headline

- **Coverage: 654/654 A2 memos = 100%** (was 108/654 = 16.5% prior to this hardening pass).
- **642** papers (98.2 %) flagged with at least one problem; **2949** total problems (avg **4.51** / paper).
- Safeguard: `gpt-5.4-mini` @ `temperature=0.0` with prompt `l3_adversarial_v3.txt` (numeric self-calibration anchor removed vs. v2).
- Methodological-comparator: 108 prior records under `papers_l3_v2_gpt51_archive/` (gpt-5.1 / prompt v2) preserved as a same-prompt-different-model sensitivity check.

## Methodology

1. **Primary safeguard (canonical):** every A2 memo in `s4_thematic_coding/papers/*.json` is reviewed by an LLM-as-adversarial-reviewer with the same prompt, model, temperature, and JSON-mode parameters across the entire 654-paper corpus.
2. **Reproducibility:** `gpt-5.4-mini` honours `temperature=0.0` (greedy decoding). The prior `gpt-5.1` reasoning-tier model in the comparator silently dropped `temperature=0.0` and was effectively run at API-mandated `temperature=1`; this is documented in the comparator block below and was a motivating reason for the model change.
3. **Prompt v3 vs v2:** v3 removes the line *"Most well-constructed memos should have 0-2 minor issues and 0 major issues"*, which acted as a numeric self-calibration anchor that suppressed problem counts. v3 retains the same six problem types, severity rubric, and "only flag genuine discrepancies" instruction, and adds explicit "do not target a particular count" wording. A 15-paper sensitivity probe (run pre-rollout, results recorded in commit history) showed v3 lifted the average problem count by ~18 % with stable category distribution — i.e. the anchor was suppressing count, not biasing categorisation.
4. **What L3 is and is not:** L3 is an LLM-adversarial review, not a researcher review. A flagged problem is a *candidate* concern. Stage B (propagation audit) lifts these candidates to AT/DT-level flags, and Stage C (assistive triage) routes flagged claims through researcher-approved actions before any manuscript edit.

## Provenance

- Raw L3 records (canonical): `s4_thematic_coding/papers/*_l3.json` (n = 654)
- Archived comparator records: `s4_thematic_coding/papers_l3_v2_gpt51_archive/*_l3.json` (n = 108)
- Driver: `p3_thematic_synthesis/scripts/run_l3_full_coverage.py` (resume-friendly, atomic per-paper writes, append-only call log at `logs/l3_calls.jsonl`)
- Aggregator: `p3_thematic_synthesis/scripts/aggregate_l3.py`
- Prompt: `p3_thematic_synthesis/prompts/l3_adversarial_v3.txt` (canonical) · `l3_adversarial_v2.txt` (comparator)
- Audit context: `p3_thematic_synthesis/GL10_AUDIT.md` gap G-03

## Primary safeguard — gpt-5.4-mini · prompt v3 (canonical)

- Model: `gpt-5.4-mini` · prompt: `v3` · temperature: `0.0`
- L3 records: **654**
- Papers with at least one flagged problem: **642** (98.2 %)
- Papers flagged clean: **12**
- Total problems flagged: **2949** (avg **4.51** / paper)
- Multi-silo papers: **362**
- Orphan papers (L3 record but no per-silo memo): **0**

### By problem type

| Type | Count |
|---|---:|
| `MISSING_LIMITATION` | 1036 |
| `SELECTIVE_QUOTE` | 818 |
| `WRONG_ATTRIBUTION` | 509 |
| `SECTION_BIAS` | 341 |
| `OVERCLAIM` | 155 |
| `HEDGING_DROPPED` | 90 |

### By severity

| Severity | Count |
|---|---:|
| `major` | 1778 |
| `minor` | 1171 |

### Per-silo distribution

| Silo | Papers in L3 | Papers w/ problems | Papers clean | Total problems |
|---|---:|---:|---:|---:|
| portfolio_optimization | 249 | 242 | 7 | 1114 |
| derivative_pricing | 143 | 142 | 1 | 691 |
| risk_management | 163 | 157 | 6 | 741 |
| quantum_ml_finance | 310 | 304 | 6 | 1368 |
| fraud_detection | 104 | 101 | 3 | 445 |
| trading_execution | 43 | 43 | 0 | 209 |
| credit_lending | 63 | 63 | 0 | 302 |
| simulation_monte_carlo | 216 | 212 | 4 | 1011 |

## Archive comparator — gpt-5.1 · prompt v2 (16.5% subset, prior baseline)

- Model: `gpt-5.1` · prompt: `v2` · temperature: `0.0 requested but silently dropped by API; effective temperature=1 (reasoning model)`
- L3 records: **108**
- Papers with at least one flagged problem: **106** (98.1 %)
- Papers flagged clean: **2**
- Total problems flagged: **387** (avg **3.58** / paper)
- Multi-silo papers: **81**
- Orphan papers (L3 record but no per-silo memo): **0**

### By problem type

| Type | Count |
|---|---:|
| `OVERCLAIM` | 233 |
| `HEDGING_DROPPED` | 63 |
| `WRONG_ATTRIBUTION` | 32 |
| `SECTION_BIAS` | 31 |
| `MISSING_LIMITATION` | 19 |
| `SELECTIVE_QUOTE` | 9 |

### By severity

| Severity | Count |
|---|---:|
| `minor` | 281 |
| `major` | 106 |

### Per-silo distribution

| Silo | Papers in L3 | Papers w/ problems | Papers clean | Total problems |
|---|---:|---:|---:|---:|
| portfolio_optimization | 54 | 54 | 0 | 201 |
| derivative_pricing | 34 | 34 | 0 | 133 |
| risk_management | 45 | 44 | 1 | 178 |
| quantum_ml_finance | 67 | 65 | 2 | 254 |
| fraud_detection | 25 | 24 | 1 | 94 |
| trading_execution | 13 | 13 | 0 | 56 |
| credit_lending | 19 | 19 | 0 | 87 |
| simulation_monte_carlo | 49 | 49 | 0 | 199 |

## Side-by-side headline (canonical vs archive comparator)

| Metric | Canonical (mini+v3, n=654) | Archive (5.1+v2, n=108) |
|---|---:|---:|
| Papers with problems | 642 (98.2 %) | 106 (98.1 %) |
| Avg problems per paper | 4.51 | 3.58 |
| Total problems | 2949 | 387 |
| Multi-silo papers | 362 | 81 |
| Orphan papers | 0 | 0 |

_The two reviewers operate with different category vocabularies (gpt-5.1 collapses most flags into `OVERCLAIM`; mini distributes across `MISSING_LIMITATION`, `SELECTIVE_QUOTE`, `WRONG_ATTRIBUTION`, `SECTION_BIAS`, `OVERCLAIM`, `HEDGING_DROPPED`). Verdict-level agreement (does this memo have problems? yes/no) is high; category-level disagreement is informative, not noise — the canonical safeguard is the mini+v3 line, the archive comparator documents the methodological history._

---

## Propagation audit and triage outcomes

The L3 candidate flags above feed two downstream layers that turn LLM signal into researcher-validated verdicts.

### Stage B — relevance-aware propagation audit (commit `12d61f28`)

Every AT (45 across 8 silos) and DT (234) was annotated in place with two new fields: `l3_flags` (per-supporting-paper breakdown including each L3 problem's attributed memo dimension and a `relevant` bit) and `l3_unflagged_support_ratio` (four parallel views: `any`, `any_major`, `relevant`, `relevant_major`). A flag is *relevant* to a theme when its target memo dimension is one the theme actually relies on (derived by walking AT.grounded_in → DT.support_code_ids[paper] → A2-memo dimensions whose support_codes overlap). Aggregate:

| View | AT support edges flagged / 758 | DT support edges flagged / 1794 |
|---|---:|---:|
| any | 755 (99.6 %) | 1786 (99.6 %) |
| any_major | 719 (94.8 %) | 1688 (94.1 %) |
| relevant | 663 (87.5 %) | 1480 (82.5 %) |
| **relevant_major** | **487 (64.2 %)** | **1002 (55.9 %)** |

Per-theme manifests at `s4_thematic_coding/{silo}/themes/l3_propagation.json`; aggregate at [`output/l3_propagation_summary.md`](output/l3_propagation_summary.md). No retain/queue verdict is computed at this layer — the relevance-filtered base rate is still too saturated for a `> 0.5` threshold to discriminate. Verdicts are deferred to R1.

**A3/R1 contract note:** the design-time within-paper contract is A1 -> L1 -> A2 -> L2 -> L3 -> A3 -> R1. In the frozen submission state A3 remained a retained/deferred contradiction-scan prompt with no executed outputs; the R1 stratified review below was executed in-freeze (2026-04-23 → 2026-04-25, 3 working windows per day, +02:00) before B1/B2 theme generation on 2026-04-26.

### R1 stratified researcher review (commit `273c7cd5`, finalised `2026-04-25`)

**Sampling:** propagation-prioritised stratified sample drawn only from papers feeding ≥1 B1/B2 theme, with three-tier stratification by L3 max severity (A=major / B=minor / C=none) and a corpus-wide top-up for major-flagged papers feeding ≥10 themes that the per-silo draws missed. Sample n=153 = 11.85 % of the 1291 silo–paper assignments; all 8 silos at or above the 10 % floor (range 10.0 – 18.6 %); 133 from per-silo Tier-A walk + 20 corpus-wide high-propagation top-ups.

**Verdict distribution (full sample, n=153):**

| Verdict | Count | % | Outcome |
|---|---:|---:|---|
| approved | 69 | 45.1 % | memo placed at `{silo}/reviewed/{paper_id}.json` |
| approved_with_caveat | 81 | 52.9 % | memo placed with `_r1_caveat` field |
| requires_revision | 2 | 1.3 % | memo retained; per-AT attribution scope-down logged |
| flag_for_pull | 1 | 0.7 % | memo moved to `{silo}/reviewed/_pulled/`; downstream cleanup applied |

**Reconciliation (commit `f145a83f`, 2026-04-25):**

- *TE pull* — `4e492b86e6c7` / `Wu2025`: non-replicable methodology (no dataset, no annealer named, suspiciously round and identically repeated performance numbers across sections). Removed from `supporting_papers` + `support_code_ids` of 4 B1 DTs + 4 B2 DTs + 2 B2 ATs in trading_execution; `_r1_pulled_papers` audit field added; 3 surgical edits to `manuscript/03_Chapters/06_silos/trading_execution.tex` (AT-TE-002 footnote 7→6 papers, AT-TE-004 body neutralised, AT-TE-004 footnote 6→5 papers + verdict count updated). Pull disclosed inline with audit-trail path.
- *QML revise* — `0030bd185e0d` / `Pasupuleti2025` and `1312e9d3c55e` / `Shapiro2025`: not evidentiary for AT-QML-001 (NISQ ceiling) or AT-QML-005 (expressivity-trainability). No theme deletion, no manuscript edits (citations live in multi-anchor `\cite{}` clusters where AT prose survives). Per-AT `_r1_attribution_caveats` metadata added to every QML theme that lists either paper as supporting; future re-projection passes honour the scope-down without losing the original provenance.
- Manuscript build re-validated: `pdflatex` single-pass clean, PDF 2.0 MB / 223 pp.

**Net signal:** of 153 papers reviewed, 150 (98.0 %) held without follow-up; 3 (2.0 %) triggered targeted s4 metadata edits and (for the pull) 3 surgical manuscript edits. The L3 mini+v3 safeguard's high flag rate is therefore a *sensitivity setting* rather than a *prevalence estimate* — researcher review converts most candidate flags into "noted, theme stands" rather than "claim retracted".

### Audit-trail provenance

- Per-silo R1 worklists: `s4_thematic_coding/{silo}/reviewed/r1_review_worklist.jsonl`
- Per-silo R1 decision logs: `s4_thematic_coding/{silo}/reviewed/r1_review.jsonl`
- Approved memos: `s4_thematic_coding/{silo}/reviewed/{paper_id}.json`
- Pulled memos: `s4_thematic_coding/{silo}/reviewed/_pulled/{paper_id}.json`
- Per-silo dispositions (post-R1): `s4_thematic_coding/{silo}/reviewed/_disposition.json` schema `p3.s4.r1_disposition.v2`
- Corpus aggregate: `s4_thematic_coding/r1_review_summary.json`
- GL-10 closure: `p3_thematic_synthesis/GL10_AUDIT.md` row G-02 → **closed**, row G-03 → **closed** (this hardening pass)
- Vincent methodology brief: `manuscript/working/p3_methodology_handoff_for_vincent.md`
