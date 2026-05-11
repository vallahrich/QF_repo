# Phase 1 — Framework Synthesis

**Status:** Complete (2026-04-11; methodology framing refreshed 2026-05-02).

**Objective:** Understand the landscape of quantum computation in financial services — which problems are being targeted and which solutions are being explored — and produce a conceptual framework (problem space taxonomy × solution space taxonomy) that structures all subsequent analysis.

**Methodological basis:** **LLM-assisted, researcher-curated framework synthesis** (Cruzes & Dybå, 2011), executed within an exploratory scoping approach (Arksey & O'Malley, 2005). The LLM produces structured extractions and candidate code labels; the researcher curates them against a vocabulary that is partly emergent from the data and partly an *a priori* normalisation list (encoded in `scripts/build_review_data_done.py::PROBLEM_CODE_MAP`). This is a **deductive normalisation step over LLM-proposed candidates**, not strict bottom-up Elo & Kyngäs (2008) inductive open coding. The narrative below describes the intended LLM-extracts/researcher-synthesizes discipline; for the divergences between the intended and executed protocol see [`audit-trail.md`](audit-trail.md) Divergence Log (D-1..D-5) and [`REVIEW_CHECKLIST.md`](REVIEW_CHECKLIST.md).

## Analytical Movement

**Predominantly inductive, with deductive normalisation.** Candidate categories emerge from LLM extraction over the 29-paper corpus; the researcher then maps the LLM-proposed code labels onto the canonical PD-01..PD-10 / SA-01..SA-11 vocabulary via `PROBLEM_CODE_MAP` / `SOLUTION_CODE_MAP` regex. No category was imposed *before* extraction, but the final code vocabulary is not strictly emergent either.

## Design Principle

**LLM extracts, researcher synthesizes.** The LLM acts as an analytical assistant (structured extraction, candidate groupings), never as an analytical authority. All final categorisation decisions are made by the researcher. The audit trail documents what the LLM proposed versus what was accepted, modified, or rejected.

**Provenance at every level.** Every output carries a chain back to the source text. Extractions include verbatim quotes with page/section references. Open codes are linked to specific chunks and source documents. Taxonomy categories list the codes and evidence passages that informed them. This ensures that the thesis can cite specific passages for every claim.

## Process

> **What was actually executed (2026-05-02 clarification).** The numbered process below describes the *intended* per-document manual-review protocol. In practice steps 3–5 were collapsed into a single deterministic Python pass in [`scripts/build_review_data_done.py`](scripts/build_review_data_done.py): paper-level inclusion/exclusion decisions are encoded as Python dictionaries (`EXCLUSIONS`, `NEEDS_RECHECK`, `HIGH_RELEVANCE`); LLM-proposed problem/solution labels are deductively normalised against the regex code-maps `PROBLEM_CODE_MAP` / `SOLUTION_CODE_MAP`. There is no per-document `_review` JSON in `s2_coding/` and no second human coder; inter-coder reliability was not measured. See [`audit-trail.md`](audit-trail.md) Divergence Log entries D-1…D-5 for full disclosure. The intended protocol below is preserved as the target for any future re-extraction.

1. **Document selection** — Curate 10–20 key academic papers, survey articles, and industry reports into a dedicated Zotero collection. Add a note per item with selection rationale.
2. **LLM-assisted extraction** — Run each document through a structured extraction prompt producing a standardised profile. For every claim, the extraction must include **verbatim supporting quotes with page/section references** — not just summaries. Each extraction entry follows the structure: `(field, extracted_value, quote, location)`.
3. **Deductive normalisation against an a priori vocabulary** — *Executed.* LLM-proposed problem/solution labels are mapped onto the canonical PD-01..PD-10 / SA-01..SA-11 vocabulary via the `PROBLEM_CODE_MAP` / `SOLUTION_CODE_MAP` regex dictionaries in `scripts/build_review_data_done.py`. Unmatched labels fall through to a slugified passthrough.
4. **Researcher-curated paper-level triage** — *Executed in code, not per-document.* Inclusions, exclusions, and `NEEDS_RECHECK` flags are encoded as Python dictionaries. The intended per-document workflow in [`REVIEW_CHECKLIST.md`](REVIEW_CHECKLIST.md) was not run.
5. **Researcher-led taxonomy construction** — The PD/SA taxonomy and the active 8×11 partition (see disclosure below) are encoded in [`scripts/build_taxonomy.py`](scripts/build_taxonomy.py); LLM aggregation was not used at this step.
6. **Framework documentation** — Produce the conceptual framework document, finalised taxonomies (with provenance), and the Phase 2 classification codebook.

### Active partition disclosure (read me before citing any matrix cell)

The corpus headline of “29 papers × 10 problem domains × 11 solution categories” **overstates effective evidence**:

- One s1 extraction (`_QUARANTINED_2026_AtharvaJain_misidentified.json`) is a misidentified PDF and is excluded — see Divergence Log D-1.
- Seven further papers are in `EXCLUSIONS` (generic QC overviews, no substantive finance content).
- Two files describe the **same** Herman survey (2022 arXiv preprint and 2023 published version); they are double-counted in every matrix cell unless explicitly deduplicated in narrative use.
- Effective independent surveys/overviews ≈ **20**, not 29.
- The active taxonomy partition is **8 problem domains × 11 solution categories**, not 10×11: PD-08 (cryptography-security) is excluded as out-of-scope (QKD-dominated) and PD-10 (insurance-actuarial) is retracted (the single PD-10 paper was the AtharvaJain misidentification) and folded into PD-03 (risk-management). Both lifecycle states are codified in [`shared/config/unified_taxonomy.json`](../shared/config/unified_taxonomy.json) and [`shared/config/silo_inclusion.json`](../shared/config/silo_inclusion.json).

Report headline counts on the **active 8×11 partition** and on the **deduplicated** Herman entry; surface the AtharvaJain retraction in the body of the chapter, not only in the audit trail.


## Expected Outputs

- Conceptual framework document.
- Problem space taxonomy with category definitions and evidence provenance.
- Solution space taxonomy with category definitions and evidence provenance.
- Classification codebook for use in Phase 2.

## Provenance Data Structure

Every extraction produces entries that propagate upward through the analysis:

```
document:  "Author_2024_Title"
chunk:     "Quantum annealing has been applied to mean-variance portfolio
            optimization, showing competitive results for up to 50 assets
            on D-Wave hardware."
location:  Section 4.2, p.15
codes:     [quantum-annealing, portfolio-optimization, hardware-benchmark]
```

Codes aggregate into categories, but each category retains pointers to its supporting chunks. When writing the thesis, you pull the chunk, verify against the PDF, and cite with full bibliographic detail.

## Folder Structure

```
p1_framework_synthesis/
├── README.md              # This file
├── s1_extractions/        # Structured LLM extraction per document
├── s2_coding/             # Reviewed extractions with manual annotations
├── s3_taxonomy/
│   ├── problem-space.md   # Evolving problem space taxonomy
│   └── solution-space.md  # Evolving solution space taxonomy
├── s4_outputs/
│   ├── conceptual-framework.md
│   └── codebook.md        # Classification codebook for Phase 2
├── prompts/               # Extraction prompt
├── scripts/               # Extraction, batch, and workbook scripts
└── audit-trail.md         # LLM proposals vs. researcher decisions
```

> **Note:** Source documents are managed in a dedicated Zotero collection (separate from the SLR and analysis collections). Selection rationale is recorded in Zotero item notes.

## Downstream Dependencies

- Phase 2 uses the taxonomy and codebook from this phase to deductively classify the full corpus.
- Phase 3 uses the problem space categories as silo boundaries for inductive thematic synthesis.

## References

- Cruzes, D.S. & Dybå, T. (2011). Recommended steps for thematic synthesis in software engineering. *Proceedings of the International Symposium on Empirical Software Engineering and Measurement (ESEM)*, 275–284. *(primary methodological basis for the executed pipeline)*
- Arksey, H. & O'Malley, L. (2005). Scoping studies: towards a methodological framework. *International Journal of Social Research Methodology*, 8(1), 19–32. *(scoping framing of corpus selection)*
- Hsieh, H.-F. & Shannon, S.E. (2005). Three approaches to qualitative content analysis. *Qualitative Health Research*, 15(9), 1277–1288. *(directed-content-analysis framing of the deductive normalisation step)*
- Elo, S. & Kyngäs, H. (2008). The qualitative content analysis process. *Journal of Advanced Nursing*, 62(1), 107–115. *(historical reference — the *intended* inductive pass described in the original protocol but **not executed**; see Divergence Log D-5)*

