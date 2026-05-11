# Phase 1 Audit Trail

Log of LLM proposals vs. researcher decisions. Each entry records what the LLM suggested and what was accepted, modified, or rejected.

---

## Divergence Log (added 2026-05-02 — chore/remediation-2026-05)

> The historical entries below this section originally read "PENDING
> REVIEW" and were rubber-stamped to "ACCEPTED" in a single 2026-05-02
> closure pass without recording the substantive divergences that
> actually occurred between the LLM's framework proposal and the
> Phase-3 / Phase-4 active pipeline. This Divergence Log is the honest
> record. It supersedes the per-entry "ACCEPTED" annotations wherever
> they conflict.

### D-1. AtharvaJain extraction quarantined (data-integrity defect)

- **What:** [`s1_extractions/2026_AtharvaJain_Quantum_Computing_S_Role.json`](s1_extractions/_QUARANTINED_2026_AtharvaJain_misidentified.json) renamed to `_QUARANTINED_2026_AtharvaJain_misidentified.json` with a sibling [`.RETRACTION.md`](s1_extractions/_QUARANTINED_2026_AtharvaJain_misidentified.RETRACTION.md).
- **Why:** Filename refers to "AtharvaJain — Quantum Computing's Role in Finance"; embedded `metadata.title`/`authors` describe a different paper (Sahu & Mazumdar, "Quantum Communication Network", Studies in Big Data 179, 2026) about 5G/6G QKD networks — not a finance paper. The extraction was performed against the wrong PDF.
- **Downstream effect:** the file is the **sole evidence** for PD-10 Insurance and Actuarial Science (and contributes a small minority share to PD-04..PD-08, SA-04, SA-05, SA-07, SA-09, SA-10, SA-11). PD-10 loses its empirical grounding; the other categories remain supported by the rest of the 29-paper corpus.

### D-2. PD-10 (Insurance and Actuarial Science) retracted

- **What:** [`shared/config/unified_taxonomy.json`](../shared/config/unified_taxonomy.json) PD-10 entry annotated `"status": "retracted"`, `"merged_into": "PD-03"`, `"retracted_date": "2026-05-02"`. [`s3_taxonomy/problem-space.md`](s3_taxonomy/problem-space.md) PD-10 heading marked **🚫 RETRACTED**; [`s4_outputs/codebook.md`](s4_outputs/codebook.md) PD-10 heading similarly marked.
- **Why:** Direct consequence of D-1. With the AtharvaJain extraction quarantined, no Phase-1 evidence remains for PD-10.
- **Downstream effect:** the active P3 silo set (`silo_inclusion.json`, dated 2026-04-19) had already absorbed PD-10 into PD-03 as a subsection on the grounds of low evidence (1 paper). The retraction now makes that absorption defensible at the source: the "1 paper" was in fact misidentified evidence.

### D-3. PD-08 (Cryptography and Financial Security) marked excluded

- **What:** [`unified_taxonomy.json`](../shared/config/unified_taxonomy.json) PD-08 annotated `"status": "excluded"` with `"excluded_reason": "QKD-dominated; out of gate-based quantum-finance scope"` and `"excluded_date": "2026-04-19"`. P1 taxonomy markdowns marked **⚠️ EXCLUDED FROM ACTIVE PIPELINE**.
- **Why:** The PD-08 corpus is dominated by QKD/post-quantum-cryptography papers, which are out of scope for a gate-based quantum-finance thesis. The Phase-3 active silo set (`silo_inclusion.json` `excluded_silos`) recorded this on 2026-04-19; the source taxonomy did not reflect it until now.
- **Downstream effect:** none — the active pipeline has been operating without PD-08 since 2026-04-19. This entry only makes the source-of-truth taxonomy match the executed pipeline.

### D-4. MECE seams documented (carried forward to codebook)

- **What:** Three known overlap seams in the taxonomy are explicitly acknowledged for future re-coding:
  - PD-08 ↔ SA-09: cryptography appears as both a problem domain and a solution approach (definitional overlap by design; further softened by D-3).
  - PD-02 vs. PD-09: Monte Carlo for derivative pricing vs. general MC simulation — the same QAE/QMCI literature is double-counted in [`conceptual-framework.md`](s4_outputs/conceptual-framework.md) PD-02×SA-03 (17) and PD-09×SA-03 (8).
  - SA-02 vs. SA-04: variational ML hybrids (QNN, VQE-as-classifier) genuinely belong to both; the codebook currently forces a single choice.
- **Why:** These are inherent to the LLM-proposed structure and were not flagged in the original Entry 2 / Entry 3 "ACCEPTED" closures. The codebook needs a multi-tag policy for SA-02 ∧ SA-04 and a disambiguation note for PD-02 vs. PD-09.
- **Action open:** [`s4_outputs/codebook.md`](s4_outputs/codebook.md) needs a "Multi-tag and overlap policy" section. *Not done in this remediation pass.*

### D-5. Methodology framing not yet rewritten (open action)

- **What:** [`README.md`](README.md) and the Phase-1 taxonomy markdown headers describe the methodology as **inductive open coding (Elo & Kyngäs 2008)**. The actual implementation (`scripts/build_review_data_done.py` `PROBLEM_CODE_MAP`) is **deductive normalisation against a hard-coded a priori vocabulary**. The 339-unique-codes claim is a count of regex-normalised slugs.
- **Why:** Method-execution mismatch — the easiest examiner attack on Phase 1.
- **Action:** rewrite as "LLM-assisted, researcher-curated framework synthesis (Cruzes & Dybå 2011)" in README + taxonomy headers + `scripts/build_review_data_done.py` module docstring. **Closed 2026-05-02 freeze:** README, REVIEW_CHECKLIST banner, script docstring, codebook PD-08/PD-10 banners, taxonomy markdown headers, and `s4_outputs/conceptual-framework.md` all reframed; bibliography demotes Elo & Kyngäs to historical/unexecuted.

### D-6. Herman 2022 / 2023 deduplication (closed 2026-05-02 freeze)

- **What:** The corpus contains two extraction files for the same Herman et al. survey — `2022_DylanHerman_Survey_Quantum_Computing_Finance` (arXiv preprint) and `2023_Herman_Quantum_Computing_Finance` (published version). Both were treated as independent in every per-category count of [`s4_outputs/conceptual-framework.md`](s4_outputs/conceptual-framework.md), inflating the 29-paper headline.
- **Why:** Same paper, two venues; double-counting it in PD-01×SA-01 (and every other cell) overstates evidence density.
- **Action:** A `SUPERSEDED = {"2022_DylanHerman_Survey_Quantum_Computing_Finance": "2023_Herman_Quantum_Computing_Finance"}` map is now defined in [`scripts/build_review_data_done.py`](scripts/build_review_data_done.py); the per-paper `_review` block of the 2022 entry carries `superseded_by` so downstream aggregators can collapse the pair. Both files remain on disk for provenance. Effective independent surveys are now ~20.

### D-7. Systemic misidentification class (closed-as-class 2026-05-02 freeze)

- **What:** Two of the 29 s1 extractions are now confirmed to have run against the wrong PDF: `2022_Khari_Quantum_Computing` (extraction is actually CryptoQNet, narrow crypto-only) and `2026_AtharvaJain_Quantum_Computing_S_Role` (extraction is actually Sahu & Mazumdar 5G/6G QKD). Khari is in `EXCLUSIONS` (D-1 / Entry 1); AtharvaJain is quarantined (D-1 / D-2). They were treated as two isolated incidents; they are in fact one class of failure: the LLM extraction was performed against a PDF whose embedded `metadata.title` does not match the filename slug.
- **Why:** Calling out the *class* rather than the *cases* makes the failure mode preventable, not just retroactively documentable.
- **Action:** Two-part remediation logged at the source:
    1. The Phase-1 extraction prompt now carries a versioned header (`version: 1.0`, `date: 2026-04-11`, `model: gpt-5.1`, `temperature: 0.2`) so the inputs to any future re-extraction are pinned (not the failure-detection mechanism, but a precondition for it).
    2. A future Phase-1 re-extraction MUST add a one-line guard in [`scripts/extract_document.py`](scripts/extract_document.py) that flags when the LLM-returned `metadata.title` does not partially match the filename slug. This is **not** in the current freeze (no re-extraction is being run); it is recorded here as a preregistered deferred action so any future re-run inherits the requirement.

---

## Entry 1: Paper-Level Quality Triage (2026-04-11)

**Action:** LLM-assisted assessment of 29 extraction files for inclusion in the Phase 1 framework synthesis corpus.

**LLM proposal:**
- 19 papers marked as `verified` (taxonomy building quality)
- 3 papers marked as `needs-recheck` (limited depth or off-topic elements)
- 7 papers marked as `exclude` (generic QC intros, toy models, no finance substance)

**Excluded papers and reasons:**
- `2022_Khari_Quantum_Computing`: Misidentified paper (CryptoQNet); narrow crypto-only scope
- `2024_Pasupuleti_Advancements_Quantum_Computing_Information`: Generic QC overview, no finance content
- `2024_Singh_Challenges_Opportunities_Quantum_Computing`: Multi-sector overview, finance superficial
- `2024_VenkataRamana_Fundamentals_Quantum_Computing_Principles`: Introductory QC fundamentals only
- `2025_Chawla_Quantum_Computing_Underlying_Principle`: Beginner QC overview, no finance analysis
- `2026_Dumba_Quantum_Thinking_Finance`: Quantum-inspired metaphor, not actual QC algorithms
- `2026_RejinaPV_Quantum_Computing_Beginner_S`: Beginner's guide, no finance-specific content

**Researcher decision:** ACCEPTED (closed 2026-05-02) — exclusion list reviewed; all 7 papers confirmed out-of-scope (no finance substance or quantum-inspired metaphors only). No re-inclusions.

---

## Entry 2: Problem-Space Taxonomy Construction (2026-04-11)

**Action:** LLM proposed 10 problem-space categories from aggregated open codes.

**LLM proposal:**
- **PD-01: Portfolio Optimisation and Asset Allocation** — 19 papers, 9 codes
- **PD-02: Derivative Pricing and Valuation** — 17 papers, 12 codes
- **PD-03: Risk Management and Assessment** — 18 papers, 12 codes
- **PD-04: Machine Learning and Pattern Recognition in Finance** — 17 papers, 7 codes
- **PD-05: Fraud Detection and Anomaly Detection** — 12 papers, 4 codes
- **PD-06: Trading and Market Microstructure** — 7 papers, 5 codes
- **PD-07: Credit Scoring and Lending** — 11 papers, 3 codes
- **PD-08: Cryptography and Financial Security** — 9 papers, 4 codes
- **PD-09: Simulation and Monte Carlo Methods** — 14 papers, 5 codes
- **PD-10: Insurance and Actuarial Science** — 1 papers, 1 codes

**Key design decisions:**
- Separated portfolio optimisation (PD-01) from trading execution (PD-06) to reflect distinct computational structures (static allocation vs. dynamic execution).
- Separated derivative pricing (PD-02) from general simulation/MC (PD-09) to align with financial domain boundaries rather than algorithmic similarity.
- Risk management (PD-03) excludes credit scoring (PD-07) — credit scoring is treated as a classification problem, while risk management covers aggregate measures.
- Cryptography (PD-08) included as a problem domain because the literature treats quantum threats to financial infrastructure as a distinct research area.
- Insurance/actuarial (PD-10) retained despite low paper count because it is a distinct financial domain with specific modelling requirements.

**Researcher decision:** ACCEPTED with modifications (closed 2026-05-02) — PD-01..PD-10 retained as the v2.0 taxonomy registry. For the active P3/P4 pipeline, PD-10 (Insurance) is absorbed into PD-03 (Risk Management) as a subsection given low evidence (1 paper at framework time), and PD-08 (Cryptography) is excluded as out-of-scope (QKD-dominated, not gate-based finance). See `p3_thematic_synthesis/P3_AUDIT_STATUS.md` for the active 8-silo set.

---

## Entry 3: Solution-Space Taxonomy Construction (2026-04-11)

**Action:** LLM proposed 11 solution-space categories from aggregated open codes.

**LLM proposal:**
- **SA-01: Quantum Annealing and QUBO Formulations** — 17 papers, 6 codes
- **SA-02: Variational and NISQ Algorithms** — 17 papers, 5 codes
- **SA-03: Quantum Amplitude Estimation and Monte Carlo Integration** — 16 papers, 5 codes
- **SA-04: Quantum Machine Learning** — 17 papers, 13 codes
- **SA-05: Grover's Search and Variants** — 11 papers, 2 codes
- **SA-06: Quantum Linear Systems (HHL and Extensions)** — 9 papers, 3 codes
- **SA-07: Quantum Walks** — 8 papers, 1 codes
- **SA-08: Hybrid Quantum-Classical Approaches** — 13 papers, 1 codes
- **SA-09: Quantum Cryptography and Post-Quantum Security** — 9 papers, 3 codes
- **SA-10: Quantum Fourier Transform and Phase Estimation** — 5 papers, 2 codes
- **SA-11: Error Mitigation and Fault Tolerance** — 6 papers, 2 codes

**Key design decisions:**
- Separated quantum annealing (SA-01) from gate-based variational (SA-02) to reflect fundamentally different hardware paradigms.
- QAE/QMCI (SA-03) given its own category rather than being subsumed under amplitude amplification because it is the dominant approach for pricing and risk.
- QML (SA-04) covers all ML-adjacent quantum algorithms; variational algorithms used for optimisation go under SA-02.
- Hybrid quantum-classical (SA-08) is an integration pattern that cross-cuts other categories — it captures architectural choices rather than specific algorithms.
- Error mitigation/fault tolerance (SA-11) included because several papers focus specifically on making financial computations viable under noise constraints.
- QFT/QPE (SA-10) included as a separate category because some papers discuss their direct financial applications beyond being subroutines.

**Researcher decision:** ACCEPTED as v2.0 (closed 2026-05-02) — SA-01..SA-11 retained as the canonical solution-space registry in `shared/config/unified_taxonomy.json`. SA-07 (Quantum Walks) and SA-10 (QFT/QPE) kept distinct; downstream evidence-density questions are tracked in P3 thematic outputs rather than as a Phase 1 blocker.

---

## Entry 4: Open Coding Scheme (2026-04-11)

**Action:** LLM applied regex-based inductive coding to all accepted entries.

**Unique problem codes generated:** 339
**Unique solution codes generated:** 401
**Unique claim codes generated:** 23

**Coding methodology:**
- Codes were assigned by matching entry labels and descriptions against a vocabulary of domain-specific patterns.
- Where no pattern matched, the entry label was normalised to a code.
- Consistent codes were applied across papers for the same concept.

**Researcher decision:** ACCEPTED as recorded (closed 2026-05-02) — open-code assignments accepted as the Phase 1 baseline; subsequent merging/splitting handled inside Phase 3 thematic coding (`s4_thematic_coding/`) rather than retroactively in the Phase 1 audit trail.

---

_End of current audit trail entries._