# Chapter Supporting Literature

**Purpose**: A curated set of additional sources used as **reading material**
for drafting Chapters 1 (Introduction) and 2 (Background). These are NOT
Phase 1 inputs and do NOT modify the PD/SA taxonomy. They are cited in the
chapters like any other reading.

**Scope**: 10 papers selected from the Phase 2 SLR corpus (see
`docs/manual-review-pipeline.md` GL-03) under "Profile B" criteria
(foundational + landmark technical works that ground Background and
Introduction prose).

## Layout

```
shared/chapter_supporting_literature/
├── README.md                 # this file
├── _selection.md             # the 10 papers + rationale (mirror of GL-03)
├── _index_by_section.md      # which note informs which §
├── _pending/                 # LLM-produced notes awaiting researcher review
│   └── <paper_id>__<slug>.md
├── <paper_id>__<slug>.md     # researcher-accepted notes (moved from _pending/)
└── scripts/
    ├── prompt_v1.txt         # versioned LLM prompt
    └── make_notes.py         # one-shot note generator
```

## Workflow (per paper)

1. `python -m shared.chapter_supporting_literature.scripts.make_notes <paper_id>`
   writes `_pending/<paper_id>__<slug>.md`.
2. Researcher reviews the note: verifies quotes against the source PDF,
   ticks the "Researcher to verify" checklist, edits as needed.
3. Researcher moves the note from `_pending/` to the parent folder.
   The file move IS the acceptance gesture (audit trail).
4. Researcher updates `_index_by_section.md` if the paper informs sections
   beyond the suggested ones.

## Compliance

- This use of GenAI is **drafting assistance**, not analytical extraction.
  Output is a researcher reading aid; chapter prose is written by the
  researchers from the source PDFs.
- Declared in `manuscript/04_Appendix/H_AI_Use_Declaration.tex` under
  "Drafting assistance — chapter supporting literature".
- See `docs/writing-guide.md` §R-04 for the canonical protocol.
- See `docs/manual-review-pipeline.md` GL-15 for the full decision trail.

## What goes here vs. Phase 1

| Phase 1 (`p1_framework_synthesis/`) | Chapter supporting literature (here) |
|---|---|
| Closed, frozen | Open — sources may be added during drafting |
| 29 papers | 10 papers (initially) |
| LLM-assisted open coding | LLM-assisted reading-note drafting |
| Output feeds the PD/SA taxonomy | Output feeds chapter prose only |
| Researcher curates emergent codes | Researcher reviews summaries + quotes |
| Audit trail = `audit-trail.md` | Audit trail = `_pending/` flow + Appendix H |
