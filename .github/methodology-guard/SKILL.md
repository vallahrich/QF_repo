---
name: methodology-guard
description: "Validate research design integrity across all phases. Use when: making methodological decisions, writing methodology sections, checking SLR/PRISMA compliance, verifying the abductive reasoning cycle, or reviewing LLM-assisted coding procedures. Ensures the thesis methodology is defensible under examiner questioning."
argument-hint: "Pass 'full' for complete methodology audit, 'slr' for SLR protocol check, 'abductive' for reasoning cycle validation, or a phase name for phase-specific methodology review"
---

# Methodology Guard — Research Design Integrity

Validate that the research methodology is sound, consistently applied, and defensible at the CBS oral defence. This skill acts as a methodological conscience — catching violations of the stated research design before they become vulnerabilities.

## When to Use

- Making methodological decisions for any phase
- Writing or editing the methodology chapter (Chapter 4)
- Reviewing whether LLM-assisted steps have proper audit trails
- Checking SLR protocol compliance (PRISMA, search strategy, screening)
- Verifying the abductive reasoning cycle is preserved
- Pre-defence preparation: identifying methodological weak points

## Canonical Reference

The single canonical methodology reference is: **`docs/METHODOLOGY_DESIGN.md`**

All methodology claims in the thesis, code, and documentation must be traceable to this document. If a discrepancy exists, `METHODOLOGY_DESIGN.md` is authoritative unless a documented decision overrides it.

## Methodology Architecture

This project uses a three-phase pipeline with an abductive reasoning cycle:

```
Phase 1 (INDUCTIVE)  →  Phase 2 (DEDUCTIVE)  →  Phase 3 (INDUCTIVE)
Framework Synthesis      Classification            Thematic Synthesis
                                                          ↓
                                                   Phase 4 (EMPIRICAL)
                                                   Experiment Validation
```

### Phase 1 — Framework Synthesis
- **Movement**: Inductive
- **Method**: Qualitative content analysis (Elo & Kyngäs, 2008; Hsieh & Shannon, 2005)
- **Approach**: Exploratory scoping (Arksey & O'Malley, 2005)
- **Design principle**: LLM as analytical assistant, not authority. Researcher makes all final decisions.
- **Provenance**: Every output carries a chain back to source text with verbatim quotes and page references.

### Phase 2 — Systematic Identification & Classification
- **Movement**: Deductive
- **Method**: SLR protocol (Kitchenham & Charters, 2007)
- **Classification**: 6-step structured coding against Phase 1 framework
- **Compliance**: PRISMA guidelines for reporting
- **Scale**: 777 papers processed with LLM-assisted extraction (full corpus after PRISMA screening: 6,232 → 3,010 → 875 → 777)

### Phase 3 — Thematic Synthesis
- **Movement**: Inductive
- **Method**: Thematic synthesis (Thomas & Harden, 2008; Cruzes & Dybå, 2011)
- **Critical requirement**: Fresh coding — themes must emerge from within-silo analysis, NOT from Phase 1 labels
- **Process**: Line-by-line coding → descriptive themes → analytical themes → cross-silo comparison
- **Quantitative complement**: Benchmark extraction and quantum advantage triangulation

### Phase 4 — Experiment Replication & Validation
- **Movement**: Empirical (not part of the original abductive cycle)
- **Method**: Independent circuit replication via Qiskit + Azure QRE resource estimation
- **Design**: Pre-registered methodology on frozen P3 inputs

## Procedure

### Step 1 — Read Canonical Methodology

Read `docs/METHODOLOGY_DESIGN.md` completely. Note:
- The Research Design Onion structure (philosophy → approach → strategy → techniques)
- Phase specifications (scope, method, inputs, outputs)
- LLM integration guidelines
- Quality criteria

### Step 2 — Abductive Cycle Integrity

The most fundamental check. Verify:

1. **Phase 1 is genuinely inductive:**
   - Categories emerged from open coding, not imposed a priori
   - Evidence: `p1_framework_synthesis/audit-trail.md` documents LLM proposals and researcher decisions
   - Red flag: If Phase 1 taxonomy was copied from an existing classification scheme without modification

2. **Phase 2 is genuinely deductive:**
   - Classification uses the Phase 1 framework as a fixed scheme
   - Papers are coded against pre-existing categories, not generating new ones
   - Red flag: If new taxonomy codes were created during Phase 2 classification (they should be flagged for Phase 1 revision instead)

3. **Phase 3 is genuinely inductive:**
   - Codes are generated fresh within each silo — NOT by applying Phase 1 labels
   - Themes emerge bottom-up from line-by-line coding
   - Red flag: If silo analysis simply confirms Phase 1 categories without generating new insights
   - Verify that fresh coding actually happens — a common failure mode in inductive-after-deductive designs

4. **Phase 4 is empirically grounded:**
   - Uses pre-registered methodology on frozen P3 inputs
   - Results are independent of P3 thematic claims
   - Red flag: If P4 results are used to retroactively adjust P3 claims

### Step 3 — SLR Protocol Compliance

Check PRISMA and Kitchenham compliance:

1. **Search strategy documented?**
   - Exact search queries with database names
   - Date ranges specified
   - Location: `p2_systematic_review/s1_slr/01_protocol/`

2. **Inclusion/exclusion criteria explicit and reproducible?**
   - Criteria are binary (yes/no), not judgment-based
   - Someone else could apply them and get the same results

3. **Screening process documented?**
   - Title/abstract screening → full text screening → final selection
   - PRISMA flow diagram exists: `p2_systematic_review/s1_slr/04_figures/fig1_prisma_flow.pdf`
   - Numbers at each stage are recorded

4. **Inter-rater reliability addressed?**
   - For two-researcher projects, how was agreement measured?
   - For LLM-assisted coding, what validation was performed?

5. **Data extraction reproducible?**
   - Extraction schema documented
   - Extraction prompts version-controlled
   - Processing log maintained

### Step 4 — LLM Integration Audit

LLM-assisted research has specific methodological requirements:

1. **Audit trails present?**
   - Phase 1: `audit-trail.md` documents LLM proposals vs. researcher decisions
   - Phase 2: Processing log tracks extraction runs
   - Phase 3: Any LLM-assisted coding must have corresponding audit trails

2. **Prompt versioning?**
   - Are extraction prompts stored in version-controlled files?
   - Can someone trace which prompt version produced which output?

3. **Validation steps?**
   - Manual spot-checks of LLM outputs documented
   - Error rates estimated or acknowledged

4. **Transparency?**
   - Thesis clearly states where LLMs were used and where humans made decisions
   - No "black box" steps where LLM output was accepted without review

### Step 4b — CBS GenAI Compliance Check

CBS GenAI compliance is a dedicated responsibility — delegate the full audit to the **`genai-compliance`** skill (`.github/skills/genai-compliance/`), which owns:
- The canonical CBS rules (`genai-compliance/references/cbs_genai_rules.md`)
- The five-pillar compliance framework (declaration, role framing, audit trail, reproducibility, validation/bias)
- The per-phase compliance matrix and examiner-question readiness checklist

Within a methodology audit, perform only the high-level cross-check:
- Is GenAI use declared in the Methodology chapter (§4.7) and AI Use appendix?
- Is the researcher-vs-GenAI contribution distinguishable in every LLM-assisted step?
- Are audit trails (prompts, raw outputs, decisions) present for each phase?

If any of these fail, stop and run the full `genai-compliance` skill before approving the methodology as defensible.

### Step 5 — Produce Report

```
## Methodology Integrity Report
**Date**: [current date]
**Scope**: [full / slr / abductive / phase-specific]

### Abductive Cycle Assessment

| Phase | Expected Movement | Actual | Status |
|-------|-------------------|--------|--------|
| Phase 1 | Inductive | ... | ✅/⚠️/❌ |
| Phase 2 | Deductive | ... | ✅/⚠️/❌ |
| Phase 3 | Inductive | ... | ✅/⚠️/❌ |
| Phase 4 | Empirical | ... | ✅/⚠️/❌ |

### SLR Protocol Compliance

| Requirement | Status | Evidence |
|-------------|--------|----------|
| Search strategy documented | ✅/❌ | [file reference] |
| Inclusion/exclusion criteria | ✅/❌ | [file reference] |
| PRISMA flow diagram | ✅/❌ | [file reference] |
| Screening documented | ✅/❌ | [file reference] |
| Inter-rater reliability | ✅/⚠️/❌ | [details] |

### LLM Integration Audit

| Check | Status | Details |
|-------|--------|---------|
| Audit trails present | ✅/❌ | [per-phase details] |
| Prompt versioning | ✅/❌ | [details] |
| Manual validation | ✅/⚠️/❌ | [details] |
| Transparency | ✅/⚠️/❌ | [details] |

### CBS GenAI Compliance (delegated to `genai-compliance` skill)

| High-level check | Status | Details |
|------------------|--------|---------|
| GenAI declared in Methodology (§4.7) + Appendix | ✅/❌ | [all phases covered?] |
| Researcher vs GenAI contribution clear | ✅/⚠️/❌ | [per-phase details] |
| Audit trails present (prompts + raw outputs + decisions) | ✅/⚠️/❌ | [per-phase paths] |
| Full compliance audit run? | ✅/❌ | [link to genai-compliance report] |

### Issues

#### 🔴 Critical — [Issue]
- **Impact**: This would fail under examiner questioning
- **Evidence**: [what was found]
- **Fix**: [specific action]

#### 🟡 Major — [Issue]
...

#### 🟢 Minor — [Issue]
...

### Defence Vulnerability Assessment
[List 3–5 methodology questions an examiner would likely ask, with assessment of how well the current state can answer them. The questions below are illustrative scaffolds, not pre-determined examiner questions; the actual list is generated live from the audit findings.]

1. **Q (example)**: "How do you ensure Phase 3 themes are genuinely inductive and not just confirming Phase 1 categories?"
   **Current readiness**: [strong / adequate / weak / not yet addressable]

2. **Q (example)**: "What validation did you perform on LLM-assisted extraction?"
   **Current readiness**: ...

### Recommended Actions
1. [Highest priority methodology fix]
2. [Second priority]
3. [Third priority]
```

## Scope Options

- **`full`**: Complete methodology audit across all phases
- **`slr`**: SLR protocol and PRISMA compliance only
- **`abductive`**: Abductive reasoning cycle integrity only
- **`llm-audit`**: LLM integration audit only
- **`phase-1`** / **`phase-2`** / **`phase-3`** / **`phase-4`**: Phase-specific methodology review
- **`defence`**: Focus on methodology questions likely at the oral defence
