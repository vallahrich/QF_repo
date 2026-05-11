# Prompt Version Log

> Tracks all prompt versions with rationale for changes.
> The pipeline loads prompts from the active version directory.
> Previous versions are preserved for reproducibility and comparison.

## Active Version: v2.2 (testing), v2.1 (previous)

## Version History

### v1 — Initial prompts (2026-04-19, commit ad6c83d)

First version. Used in pilot iterations 01-04.

**Known issues identified during pilot:**
- A1: Self-quoting bug — model quotes prompt instructions as text_spans
- A1: SECTION_ABSENT/NO_LIMITATIONS_STATED treated as verbatim quotes (L1 fails)
- A1: Field name inconsistency — model uses "label" instead of "code_label"
- A1: 40-word quote limit too long for reliable L1 matching
- A2: MISSING_LIMITATION was #1 L3 problem (86 instances) — limitations under-extracted
- A2: WRONG_ATTRIBUTION was #2 L3 problem (55 instances) — cited results attributed to paper
- A2: SECTION_BIAS was #4 problem (32 instances) — heavy on abstract, light on results
- L3: Over-flagging severity — 85% of flags rated "major" (227/266)

### v2 — Pilot-informed fixes (2026-04-19, commit f9a2c8d)

Addresses all v1 issues. Used in pilot iterations 05+.

**A1 changes:**
- Moved scope instruction ABOVE paper text (was below, causing self-quoting)
- Added explicit rule: "Do NOT quote from these instructions"
- SECTION_ABSENT/NO_LIMITATIONS_STATED now use `text_span: ""`
- Quote limit reduced 40 → 30 words
- Added explicit field name rule (MUST use code_label)
- Simplified firewall instruction

**A2 changes:**
- New rule 5: limitations are CRITICAL — must capture every limitation
- New rule 6: attribution clarity — "the authors cite [X]" not "the paper found"
- New rule 7: section balance — draw from all sections, not just abstract/intro

**L3 changes:**
- Added severity calibration guide with examples
- "Most memos should have 0-2 minor, 0 major"
- Explicit: dropped hedge word = minor, not major

**Unchanged prompts:**
- A3 (contradiction scan) — no issues found
- B1 (descriptive themes) — not yet tested
- B2 (analytical themes) — not yet tested
- C1 (cross-silo patterns) — not yet tested

### v3 — Simplified prompts for mini models (2026-04-19)

Hypothesis: mini models perform better with shorter, more direct instructions.
v2 has many rules that may confuse smaller models. v3 strips to essentials.

**A1 changes (v2 → v3):**
- Reduced from ~40 lines to ~25 lines
- Removed markdown code block example (models copy formatting)
- Consolidated 8 rules into 5 IMPORTANT bullet points
- Moved scope instruction into task description (not separate section)
- Kept all critical rules: verbatim quotes, field names, firewall, section coverage

**A2 changes (v2 → v3):**
- Reduced from ~70 lines to ~35 lines
- Flat dimension list instead of nested JSON example
- Kept critical rules: limitations emphasis, attribution, section balance

**L3 changes (v2 → v3):**
- Reduced from ~45 lines to ~25 lines
- Inline severity guide (not separate section)
- Same 6 problem types, same severity calibration

**Testing strategy:** Run v3 on mini first (fast). If it beats v2, test on gpt-5.1.
If v2 and v3 both have strengths, cherry-pick the best elements into v4.

### v2.1 — Hybrid: v2 fixes + flexible quoting (2026-04-20)

Evidence-based iteration combining best elements from v1 and v2.

**Root cause of iter_07 regression**: v2 reduced quote limit from 40 to 30 words.
gpt-5.1 (reasoning model) struggled with the tighter constraint, producing 4 empty
files and lower L1 pass (94.5% vs 95.3% on v1). Meanwhile mini was fine with 30 words.

**A1 changes (v2 → v2.1):**
- Quote limit: "max 30 words" → "typically 10-60 words, use your judgement"
  Flexible range instead of hard cap. Model picks natural span length.
- Added: "preserving all punctuation, hyphens, and special characters"
  Targets exact L1 matching improvement (most passes are fuzzy, not exact).
- Restored markdown code block example from v1 (reasoning models benefit from
  explicit format demonstration)
- Kept all v2 fixes: self-quote prevention, field name rule, firewall, section coverage

**A2 and L3**: Unchanged from v2 (issues were in A1 only).

**Expected impact**: gpt-5.1 recovers to 0 empty (like iter_04) while keeping
v2's limitation/attribution improvements. Higher L1 exact pass rate from
verbatim instruction.

### v2.2 — L3 materiality threshold (2026-04-20)

All iterations show ~100% L3 problem rate — L3 flags every single paper.
Analysis shows L3 catches micro-issues (slightly weakened hedge words) that
don't materially affect understanding. This makes the metric useless for
comparison and creates unnecessary noise for researcher review.

**L3 changes (v2.1 → v2.2):**
- Added MATERIALITY TEST: "Would a researcher form a meaningfully different
  understanding?" If no, don't flag.
- Added EXPECTED OUTCOMES: "Most papers should be CLEAN. 0-2 problems typical."
- Stronger severity distinction: minor = fair overall representation;
  major = reader would form incorrect understanding
- Only flag SUBSTANTIVE hedges dropped, not every qualifier
- Only flag PRIMARY limitations omitted, not every shortcoming

**A1 and A2**: Unchanged from v2.1.

**Evidence**: iter_03 L3 had 227 major / 39 minor (85% major, 1 clean paper).
iter_07 L3 v2 improved to 49 major / 109 minor (31% major, 3 clean).
v2.2 targets ~50-70% clean papers with only material issues flagged.

### v4 — Enhanced coverage checklist (2026-04-22, TESTED — NOT ADOPTED)

Hypothesis: mini's coverage gap (~15-20% vs gpt-5.1) can be closed with
explicit coverage guidance and deduplication instructions.

**A1 changes (v2 → v4):**
- Raised code range from 15-40 to 25-60
- Added 10-item coverage checklist (problem formulation, quantum specifics,
  classical baselines, quantitative results, hardware, limitations, related work,
  reproducibility)
- Added dedup rule: "one code per concept, from most detailed occurrence"
- Removed SECTION_ABSENT instruction (skip missing sections instead)
- Moved scope instruction after paper text to prevent prompt leakage

**Also tested:** a1_gap_check.txt — two-pass extraction where a second LLM call
reviews existing codes and adds 5-15 missed concepts.

**Quick test (5 papers, Approach A/B/C):**
- A (mini v4): 90 avg codes, 98.9% L1 — appeared promising
- B (5.1 v4): 58 avg codes, 94.5% L1, 0 leakage (fixed!)
- C (mini v2 + gap): 75 avg codes, 96.3% L1, 8× slower

**Full pilot validation (14/44 papers completed as iter_11):**
- iter_11 (mini v4): avg 50.4 codes, 98.0% L1, 14 total fails
- iter_05 (mini v2): avg 52.1 codes, 97.4% L1, 19 total fails
- **Conclusion: No meaningful improvement.** Quick test inflated code counts
  due to LLM non-determinism. In the actual pipeline, v4 produces nearly
  identical output to v2. Iteration stopped at 14/44 to save tokens.
- **v4 retained in prompts/ for reproducibility but NOT used in production.**

**Key finding from v4 testing: gpt-5.1 prompt leakage (C-001 coding thesis
instructions) is fixed by moving scope instruction after paper text.** This
finding is incorporated into v4 but irrelevant for production since mini
is used for A1 (mini never exhibited this bug).

## Production Configuration Decision (2026-04-22)

Based on 11 pilot iterations + deep quality assessment (Claude Opus 4.6
reviewing 10 papers against source text):

- **A1 (open coding):** gpt-5.4-mini with v2 prompt
  - 97.4% L1, 0 hallucinations, 0 prompt leakage
  - ~52 codes/paper avg, 4.0/5.0 overall quality
- **A2 (memo compression):** gpt-5.1 (hybrid — receives mini's A1 codes)
  - Wins 8/10 papers on content depth vs mini A2
  - 31% fewer L3 problems than mini A2
  - Adds interpretive connections and operational specifics
- **L3 (adversarial):** gpt-5.1 (same model as A2)
- **Prompt version:** v2 for A1, v2 for A2/L3
