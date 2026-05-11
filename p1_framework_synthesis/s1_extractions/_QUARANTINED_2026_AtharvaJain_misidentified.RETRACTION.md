# RETRACTION — `2026_AtharvaJain_Quantum_Computing_S_Role.json`

**Status:** QUARANTINED 2026-05-02. The JSON file in this directory
(`_QUARANTINED_2026_AtharvaJain_misidentified.json`) is preserved
*solely* for audit-trail completeness. **It must not be used as
extraction evidence by any downstream phase.**

## Defect

The filename refers to a paper "AtharvaJain — Quantum Computing's Role
[in Finance]". The `metadata` block inside the JSON, however, records a
*different* paper:

- **Title:** "From Bits to Qubits: The Quantum Transformation of
  Computing — A Comprehensive Analysis of Quantum Communication
  Network: State-of-the-Art, Applications and Future Prospects"
- **Authors:** Swastik Kumar Sahu, Kaushik Mazumdar
- **Venue:** Studies in Big Data 179 (Springer), 2026
- **Topic:** 5G/6G quantum communication networks and QKD — *not a
  finance paper*

The extraction was performed on the wrong PDF. All extracted
`problem_domains` and `solution_methods` therefore describe quantum
communication infrastructure, not quantum-finance applications.

## Downstream impact

This single file was the **sole evidence** for the Phase 1 problem-space
category **PD-10 Insurance and Actuarial Science**, contributing the
only `insurance-actuarial` open codes. With the source retracted, PD-10
loses its empirical grounding.

The file also contributed to PD-04, PD-05, PD-06, PD-07, PD-08, SA-04,
SA-05, SA-07, SA-09, SA-10, and SA-11; in every other case the
contribution is a small fraction of the category's evidence base, so
the categories themselves remain supported by the rest of the
29-paper Phase 1 corpus. PD-10 is the one category whose evidence base
collapses.

## Resolution

1. **Phase 1 taxonomy artefacts** (`s3_taxonomy/problem-space.md`,
   `s4_outputs/codebook.md`): mark PD-10 as **RETRACTED** with a
   pointer to this note. (Done in the same 2026-05-02 commit.)
2. **`shared/config/unified_taxonomy.json`**: PD-10 entry annotated
   `"status": "retracted"` with the retraction reason and date. (Done.)
3. **Phase 3 active baseline** is unaffected in practice: PD-10 was
   already merged into PD-03 (`silo_inclusion.json` excluded_silos
   list, dated 2026-04-19). The retraction simply makes the original
   evidence gap visible at the source layer.
4. **Re-extraction not attempted.** The corresponding paper appears
   either to never have been included in the SLR corpus or to be the
   `Sahu/Mazumdar` chapter, which is outside the gate-based
   quantum-finance scope. Either way, no replacement evidence is
   available for PD-10 from the Phase 1 corpus.

## Why preserve the file at all

Deleting the JSON would erase evidence of the defect. Quarantining it
under a `_QUARANTINED_*` prefix:
- preserves the full extraction text for any examiner who asks "show
  me the broken artefact",
- prevents accidental ingestion: the underscore-prefix excludes the
  file from `iter_extractions()`-style loaders, and the "QUARANTINED"
  marker in the filename is impossible to miss in a directory listing,
- documents the root-cause (PDF-vs-filename mismatch) so future Phase 1
  re-extractions can add a guard.

## Recommended guard for any future Phase 1 re-extraction

Add a check in `scripts/extract_document.py` that compares the
extracted `metadata.title` (or DOI, if available) against the input
filename via Levenshtein/substring similarity, and flags any
divergence above a threshold for manual review. Without that guard,
this defect class can recur silently.

---

*This file is part of the chore/remediation-2026-05 cleanup. See*
*[`p1_framework_synthesis/audit-trail.md`](../audit-trail.md) Divergence Log*
*for the broader context.*
