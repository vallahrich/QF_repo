# L4 Human Audit Guide

> **Status note (2026-05-11): historical L4/R1 guide.** This guide explains
> the intended researcher validation layer for the P3 thematic pipeline. The
> canonical within-paper contract is **A1 -> L1 -> A2 -> L2 -> L3 -> A3 -> R1**.
> In the frozen submission state A3 was retained as a deferred contradiction-scan
> prompt; R1 stratified review was executed in-freeze (2026-04-23 → 2026-04-25,
> 3 working windows per day, +02:00). Use [../FREEZE.md](../FREEZE.md) and
> [../GL10_AUDIT.md](../GL10_AUDIT.md) for current authority.

## Purpose

The L4 audit is the **researcher validation layer** of the 5-layer safeguard architecture. It provides the evidence that LLM-generated codes and memos are accurate — the key defence for examiner questions about AI reliability.

Layers L1-L3 run automatically. L4 is where the researcher confirms the automated layers are working.

## When to Run

- **Pilot phase**: After each pilot iteration — validates pipeline quality before committing to production
- **Production phase**: After each silo's A1/A2/L3 pipeline completes — 10% stratified sample
- **Pre-submission**: Final spot-check before thesis defence

## Sampling Strategy

| Context | Sample size | Rationale |
|---------|------------|-----------|
| **Pilot** | All papers or --sample N | Full coverage during calibration |
| **Production** | 10% per silo, minimum 5 papers | Statistically meaningful, reproducible (fixed seed) |
| **Cross-silo** | 10% per silo, stratified by source_type + tier | Ensures diversity across paper types |

The sample is drawn with a fixed random seed (default: 42) for reproducibility. Another researcher using the same seed gets the same sample.

## How to Use

### Step 1: Generate review files

```bash
# Pilot: review all papers in an iteration
python -m p3_thematic_synthesis.scripts.generate_audit_reviews \
    --iteration iter_04_gpt-5_1_vd5b5e8c \
    --silo trading_execution \
    --all

# Production: 10% sample (default)
python -m p3_thematic_synthesis.scripts.generate_audit_reviews \
    --iteration run_20260420_... \
    --silo portfolio_optimization

# Custom percentage
python -m p3_thematic_synthesis.scripts.generate_audit_reviews \
    --iteration run_20260420_... \
    --silo portfolio_optimization \
    --pct 15
```

This creates `audit/review_<paper_id>.md` files inside the iteration folder.

### Step 2: Review each paper

Open each review file in VS Code. For each paper:

1. **Read the summary** at the top — understand what the paper is about
2. **Skim the A1 codes** — do the labels and quotes look reasonable?
3. **Spot-check 3-5 quotes** against the source paper:
   - Open `shared/extracted_text/text/<paper_id>*.md`
   - Search for the quoted text
   - Is it real? Is it taken in context?
   - Focus on ❌ L1-fail codes and 🟡 fuzzy-match codes
4. **Read the A2 memo** — does it faithfully represent the paper?
   - Check each dimension: is the text supported by the cited codes?
   - Look for `model_inference` support types — these are LLM interpretations
5. **Review L3 flags** — are the adversarial findings real problems?
6. **Fill in the scoring section** at the bottom

### Step 3: Scoring guide

#### Memo Accuracy
| Score | When to use |
|-------|------------|
| **Accurate** | The memo faithfully represents the paper. No significant overclaims, omissions, or misinterpretations. You would trust this memo for thematic synthesis. |
| **Minor issues** | Small overclaims or omissions that don't change the overall picture. For example: a hedging word dropped, a minor result omitted, a slight overstatement of findings. Acceptable for synthesis with caveats. |
| **Major issues** | The memo misrepresents the paper in ways that matter. Fabricated claims, wrong attribution of results, missing critical limitations, or fundamental misunderstanding of the method. This memo should NOT feed thematic synthesis without correction. |

#### Code Coverage
| Score | When to use |
|-------|------------|
| **Good** | All major claims, methods, results, and limitations from the paper are captured in the codes. You can't think of significant content that was missed. |
| **Partial** | The codes capture the main points but miss some significant claims or entire sections. For example: results covered but limitations section ignored. |
| **Poor** | Many important claims are missing. The codes only capture surface-level content (abstract/intro) and miss the substance (methods/results/discussion). |

#### L3 Assessment
| Score | When to use |
|-------|------------|
| **L3 flags are valid** | The adversarial pass correctly identified real problems (overclaims, hedging dropped, etc.) |
| **L3 flags are false positives** | The flagged issues are not actually problems — the memo is fine |
| **L3 missed issues** | You found problems that L3 didn't catch. Note what was missed in the Researcher Notes field. |

#### Disposition
| Score | Effect | When to use |
|-------|--------|------------|
| **approved** | Memo enters thematic synthesis pipeline (B1/B2) | Accurate or minor issues only |
| **approved_with_edits** | Memo enters after you correct the noted issues | Minor issues that you've fixed in the notes |
| **requires_manual_read** | Paper needs full manual reading before coding | Major memo issues but paper is important enough to keep |
| **excluded** | Paper dropped from thematic claims | Unreliable memo AND paper isn't critical to the silo narrative |

### Step 4: Collect results

```bash
python -m p3_thematic_synthesis.scripts.generate_audit_reviews \
    --iteration iter_04_gpt-5_1_vd5b5e8c \
    --silo trading_execution \
    --collect
```

This parses all completed review files and produces `audit/audit_results.json` with:
- Per-paper scores
- Aggregate accuracy rate
- Disposition distribution

## Decision Gates

| Metric | Threshold | Action if failed |
|--------|-----------|-----------------|
| Memo accuracy "accurate" rate | ≥ 80% | Pass — proceed to B1/B2 |
| Memo accuracy "accurate" rate | 60-80% | Warning — review prompts, consider revision |
| Memo accuracy "accurate" rate | < 60% | Fail — revise prompts and re-run pipeline |
| "Major issues" rate | < 10% | Pass |
| "Major issues" rate | ≥ 10% | Fail — investigate which papers and why |
| "Excluded" dispositions | < 5% | Pass |

## What to Report in the Thesis

In §4.7 (AI-Assisted Research Methods):

> "We validated the LLM-assisted coding pipeline through a stratified human audit
> of [N] papers ([X]% of the corpus), randomly sampled across [N] silos. Two
> researchers independently reviewed LLM-generated codes and memos against the
> source papers. Memo accuracy was rated as: accurate [X]%, minor issues [X]%,
> major issues [X]%. [X]% of memos were approved for thematic synthesis without
> modification. The L3 adversarial pass correctly identified [X] issues that the
> researcher confirmed as valid."

## File Locations

```
<iteration>/
└── audit/
    ├── review_<paper_id>.md    — one per sampled paper (researcher fills in)
    └── audit_results.json      — aggregated scores (generated by --collect)
```
