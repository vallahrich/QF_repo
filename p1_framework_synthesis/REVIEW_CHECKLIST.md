# Phase 1 — Manual Review & Open Coding Checklist

> ⚠️ **Intended-protocol document, partially executed** (banner added 2026-05-02).
>
> This checklist describes the *intended* per-document manual-review workflow.
> In practice the manual review was carried out as a single programmatic pass
> in [`scripts/build_review_data_done.py`](scripts/build_review_data_done.py)
> with paper-level inclusion/exclusion decisions encoded as Python
> dictionaries rather than as per-document JSON files in `s2_coding/`. The
> per-document `_review`-flag workflow described below was therefore not
> executed; `s2_coding/` contains only the aggregate `review_data*.json`
> files. Treat this checklist as the *intended* protocol that future Phase-1
> re-extractions should follow, not as a record of what happened. See
> [`audit-trail.md`](audit-trail.md) Divergence Log entry D-5 for context.

Use this checklist for each extraction JSON in `p1_framework_synthesis/s1_extractions/`. Open the PDF alongside the JSON and work through each section. Record corrections and codes in a copy saved to `p1_framework_synthesis/s2_coding/`.

---

## Per-Document Workflow

### 0. Setup

- [ ] Open the source PDF (from Zotero)
- [ ] Open the extraction JSON (`p1_framework_synthesis/s1_extractions/<name>.json`)
- [ ] Copy JSON to `p1_framework_synthesis/s2_coding/<name>.json` — all edits go in the coding copy
- [ ] Check `_extraction_quality` field: `valid`, `reason`, `failed_chunks`

### 1. Metadata Verification

- [ ] Title matches the PDF
- [ ] Authors are correct and complete
- [ ] Year is correct
- [ ] Venue is correct (journal, conference, preprint server)
- [ ] `document_type` is accurate (academic-paper / survey / industry-report / whitepaper / other)

### 2. Problem Domains Review

For **each** entry in `problem_domains`:

- [ ] **Quote accuracy** — Is the quote verbatim? Fix any OCR artefacts or truncation
- [ ] **Location accuracy** — Does the page/section reference match where the quote appears?
- [ ] **Label quality** — Does the `problem` label accurately capture what the document describes?
- [ ] **Confidence check** — Agree with the confidence rating? Adjust if needed
- [ ] **Duplicates** — Flag or merge entries that describe the same problem with different wording
- [ ] **Missing problems** — Scan the PDF for financial problems the LLM missed. Add them manually with `"source": "manual"` tag

**Open coding** — For each verified problem, assign one or more initial codes:
```json
"codes": ["portfolio-optimization", "combinatorial", "NP-hard"]
```
Use the document's own terminology. Do not force labels into pre-existing categories.

### 3. Solution Approaches Review

For **each** entry in `solution_approaches`:

- [ ] **Quote accuracy** — Verbatim check
- [ ] **Location accuracy** — Page/section check
- [ ] **Label quality** — Does the label match what the document actually describes?
- [ ] **Specificity** — Is the approach named concretely (e.g. "QAOA" not just "quantum algorithm")? Sharpen if possible
- [ ] **Duplicates** — Merge entries referring to the same approach
- [ ] **Missing approaches** — Scan the PDF for quantum solutions the LLM missed

**Open coding:**
```json
"codes": ["QAOA", "variational", "gate-based", "near-term"]
```

### 4. Problem–Solution Mappings Review

For **each** entry in `problem_solution_mappings`:

- [ ] **Mapping valid** — Does the document actually connect this problem to this solution?
- [ ] **Quote supports the link** — Does the quote show the connection, not just mention both?
- [ ] **Missing mappings** — Are there problem–solution pairs in the PDF that weren't captured?
- [ ] **Spurious mappings** — Remove any that are inferred but not stated in the document

### 5. Key Claims Review

For **each** entry in `key_claims`:

- [ ] **Claim accuracy** — Does the claim faithfully represent what the document says?
- [ ] **Claim type** — Is the tag correct? (advantage / limitation / gap / trend / comparison)
- [ ] **Quote supports the claim** — Does the verbatim text actually say this?
- [ ] **Overstated claims** — Flag claims where the LLM overstated what the document asserts
- [ ] **Missing claims** — Add important claims from the conclusion, abstract, or discussion sections

### 6. Maturity Indicators Review

- [ ] **Indicator correct** — theoretical-only / simulation / real-hardware / production / not-stated
- [ ] **Quote supports the indicator** — Does the text show this maturity level?
- [ ] **Multiple levels** — If the paper covers both simulation and real hardware, are both captured?

### 7. Open Questions Review

- [ ] **Accuracy** — Are these actually stated as open questions or future work in the document?
- [ ] **Completeness** — Check the "Future Work" and "Conclusion" sections for missed items

---

## Quality Flags

Add these flags to the coding copy's root level as needed:

```json
"_review": {
  "reviewer": "your initials",
  "date": "2026-04-XX",
  "status": "verified | needs-recheck | exclude",
  "notes": "free-text observations",
  "relevance": "high | medium | low",
  "exclusion_reason": null
}
```

- **`exclude`** — Document is too general / off-topic for Phase 1 framework building. Record reason.
- **`needs-recheck`** — Extraction had issues; should be re-extracted or re-reviewed.
- **`relevance`** — How useful is this document for building the problem/solution taxonomy?

---

## Open Coding Conventions

1. **Use lowercase, hyphenated labels** — `portfolio-optimization`, not `Portfolio Optimization`
2. **Be specific** — `quantum-annealing` not `quantum-method`
3. **Use the document's terminology first** — If the paper says "mean-variance optimization", code it as `mean-variance-optimization`
4. **One code per concept** — Don't pack multiple ideas into one code
5. **Record new codes as they emerge** — There is no fixed code list; codes are created inductively
6. **Note cross-document patterns** — If you see the same concept in multiple papers, use the same code label

---

## After Reviewing All Documents

- [ ] Compile a list of all unique codes across all coded documents
- [ ] Note which codes appear in multiple documents (frequency)
- [ ] Flag codes that seem synonymous (candidates for merging in step 1.6)
- [ ] Identify any documents that should be excluded from the taxonomy
- [ ] Update `p1_framework_synthesis/audit-trail.md` with any corrections or decisions made
