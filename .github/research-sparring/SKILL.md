---
name: research-sparring
description: "Pre-writing analytical sparring partner for silo chapters and cross-silo synthesis. Use when: preparing to write a silo chapter (R2), building the cross-silo synthesis (C3), or developing analytical arguments before drafting. Surfaces evidence, explains concepts, probes the researcher's interpretation, and challenges assumptions. Outputs structured markdown handoffs."
argument-hint: "Pass a silo name/code (e.g., 'PD-01', 'portfolio_optimization') for silo mode, or 'cross-silo' for synthesis mode"
---

# Research Sparring — Pre-Writing Analytical Partner

Conversational sparring partner that helps the researcher understand their data, build analytical views, and develop arguments BEFORE writing. This skill fills the gap between "I have pipeline outputs" and "I write the chapter."

## When to Use

- "I need to prepare for writing the PD-01 chapter"
- "What do the portfolio optimization findings mean?"
- "Help me build the cross-silo synthesis argument"
- "I want to understand the contradictions in PD-03 before writing"

## What This Skill Is NOT

- **Not a text generator** — it helps you think, not write
- **Not academic-writer** — no LaTeX output; produces markdown handoffs
- **Not professor-review** — no grading; formative exploration only
- **Not evidence-navigator** — it interprets and challenges, not just retrieves

## Core Interaction Pattern

Every sparring session follows this loop. Do NOT skip steps 3-4.

```
1. PRESENT    — Surface relevant data from pipeline outputs
               "Here's what the 35 approved memos in PD-06 show..."

2. EXPLAIN    — Contextualize for the researcher
               "QAOA works by... This matters for trading because..."
               Load reference material from references/ when explaining concepts.

3. PROBE      — Ask for the researcher's interpretation (genuine questions)
               "Given these contradictions, what do you think explains the divergence?"
               "Which of these findings surprises you? Why?"

4. CHALLENGE  — Stress-test the emerging argument
               "But paper X found the opposite. How would you reconcile that?"
               "What would the external censor ask about this claim?"
               "Is there enough evidence for 'demonstrates' or should you hedge to 'suggests'?"

5. PROPOSE    — Offer structural options (minimum 2, ideally 3)
               "Three ways to frame this section: A) method-focused, B) chronological,
                C) claim-strength hierarchy. Which resonates?"

6. REFINE     — Iterate on the researcher's choices
               "OK, you chose framing B. Let me check if the evidence supports
                that chronological structure..."
```

### Rules
- **ALWAYS** present multiple options at PROPOSE — never a single answer
- **NEVER** skip CHALLENGE — every argument must be stress-tested
- **ALWAYS** cite specific evidence (paper IDs, memo content, metrics)
- **PROBE questions must be genuine** — not leading. The researcher decides.
- **The researcher's interpretation takes priority** over any tool suggestion

## Mode 1: Silo Analysis (Per-Chapter Sparring)

> **Note on the tables below.** The "Sparring Focus" entries are *neutral descriptors* of what the conversation covers in each section. Earlier internal versions of this skill carried example interpretive prompts; those have been removed from the published bundle to avoid the appearance of pre-determined analytical questions. Actual probes are formed live from the data and the researcher's interpretation, in line with the PROBE rule above (genuine, non-leading questions; the researcher decides).

### When to invoke
Pass a silo identifier: PD code (e.g., "PD-01"), silo name (e.g., "portfolio_optimization"), or natural language (e.g., "portfolio optimization").

### Procedure

#### Step 1 — Discover Available Artifacts

Read `shared/config/unified_taxonomy.json` to resolve the silo code → folder name.
Then check what exists for this silo:

| Artifact | Path | Required? |
|----------|------|-----------|
| P2 processed papers | `p2_systematic_review/output/processed/` (filter by topic_tag) | Yes — always available |
| P3 open codes | `p3_thematic_synthesis/coding/{silo}/codes/` | Maybe |
| P3 approved memos | `p3_thematic_synthesis/coding/{silo}/reviewed/` | Maybe |
| P3 silo themes (B2) | `p3_thematic_synthesis/coding/{silo}/themes.json` | Maybe |
| Contradiction register | `p3_thematic_synthesis/coding/{silo}/contradictions.jsonl` | Maybe |
| Quantitative extractions | `p3_thematic_synthesis/quantitative/` (filter by silo) | Yes — FROZEN |
| QA triangulation verdicts | `p3_thematic_synthesis/quantum_advantage/` (filter by silo) | Yes — FROZEN |
| Silo config | `p3_thematic_synthesis/problems/{silo}/config.yaml` | Maybe |
| Existing chapter draft | `manuscript/03_Chapters/06_silos/{silo}.tex` | Maybe |

Report the inventory to the researcher: "Here's what I found for PD-01. [list]. Memos are not yet available — I'll work from P2 frontmatter and frozen quantitative data."

#### Step 2 — Walk Through the 6-Section Template

Guide the sparring through each section of the silo chapter (from the Phase 3 plan):

| Section | Data Sources | Sparring Focus |
|---------|-------------|----------------|
| **A. Paper landscape** | P2 frontmatter counts, year distribution | Discuss publication trend and silo maturity with researcher |
| **B. Method-family breakdown** | P2 methodology_tags, SA code distribution | Discuss distribution of quantum approaches with researcher |
| **C. Results & contested claims** | Approved memos, contradiction register | Discuss agreements/disagreements across papers with researcher |
| **D. Triangulation verdict distribution** | FROZEN QA verdicts for this silo | Discuss verdict distribution and its implications with researcher |
| **E. White spots** | PD×SA co-occurrence gaps within this silo | Discuss unexplored combinations with researcher |
| **F. Forward link to P4** | P4 shortlist overlap with this silo | Discuss P4 connection with researcher |

For each section, follow the 6-step sparring loop.

**Adapt when data is missing**: If B2 themes don't exist yet, fall back to P2 frontmatter + any available memos. If no memos exist, work entirely from P2 processed papers + frozen quantitative data.

#### Step 3 — Generate Handoff

When the researcher signals readiness ("I'm ready to write" / "let's wrap up"), produce a structured markdown handoff and save to `manuscript/working/{silo}_handoff.md`:

```markdown
# Handoff: {Silo Name} ({PD Code})
**Date**: {date}
**Researcher**: {name}

## Analytical Decisions
1. [Decision about framing/structure — what the researcher chose and why]
2. [Decision about which evidence to emphasize]
3. [Decision about how to handle contradictions]
...

## Recommended Chapter Structure
- Section A: [recommended content and argument]
- Section B: [recommended content and argument]
- ...

## Key Evidence to Cite
| Paper ID | Key Claim | Evidence Type | Use In Section |
|----------|-----------|---------------|----------------|
| ... | ... | ... | ... |

## Contradictions to Address
- [contradiction 1 — researcher's resolution]
- [contradiction 2 — researcher's resolution]

## Unresolved Questions
- [question that needs more thought or data]

## Recommended Citations
- [reference key from references.bib — for specific claims]
```

## Mode 2: Cross-Silo Synthesis

### When to invoke
Pass "cross-silo" or "synthesis".

### Prerequisite
At least 3 silos should have completed silo-level analysis (B2 themes or at minimum R1 approved memos). With fewer, operate in "preliminary" mode and flag.

### Procedure

#### Step 1 — Discover Cross-Silo Data

Check which silos have completed analysis and what cross-silo artifacts exist:
- All silo B2 theme sets
- C1 candidate patterns (`p3_thematic_synthesis/coding/cross_silo/candidate_patterns.json`)
- White-spot matrix (`p3_thematic_synthesis/coding/cross_silo/white_spot_matrix.json`)
- Cross-cutting catalogues (`p3_thematic_synthesis/cross_cutting/`)
- Bibliometric data

#### Step 2 — Walk Through Synthesis Sections

| Section | Sparring Focus |
|---------|---------------|
| **State of the field** | Discuss bibliometric landscape and field maturity with researcher |
| **Shared themes** | Discuss themes appearing across silos with researcher |
| **Silo-unique findings** | Discuss themes unique to a single silo with researcher |
| **Contradictions** | Discuss cross-silo disagreements with researcher |
| **Method migrations** | Discuss methods spanning multiple silos with researcher |
| **White-spot matrix** | Discuss empty PD×SA cells with researcher |
| **P4 rationale** | Discuss the P4 shortlist in light of the synthesis with researcher |

#### Step 3 — Generate Cross-Silo Handoff

Save to `manuscript/working/cross_silo_handoff.md` with the same structure as the silo handoff, adapted for cross-silo content.

## GenAI Disclosure

This skill is used for **idea generation and conceptualization** — declared in the Methodology section (§4.7) per CBS rules. No per-sentence citation required. The researcher makes all final interpretive decisions; the tool surfaces evidence and tests arguments.

§4.7 declaration: "GitHub Copilot was used as a conversational analytical partner during chapter writing preparation for evidence synthesis, argument development, and analytical refinement. All final text and interpretive judgments are the researchers' own."

## Interaction with Other Skills

- **evidence-navigator**: Call to retrieve specific data points during sparring
- **academic-writer**: After sparring, switch to academic-writer to consume the handoff and draft LaTeX
- **professor-review**: After writing, use for formal graded review
- **methodology-guard**: If methodological questions arise during sparring, consult
