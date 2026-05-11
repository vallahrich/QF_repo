# Conceptual Framework: Quantum Computing in Financial Services

_Phase 1 output — Framework Synthesis (LLM-assisted, researcher-curated)_
_Date: 2026-04-11; reframed and corrected 2026-05-02 (pre-freeze)_
_Method: Cruzes & Dybå (2011) within an Arksey & O'Malley (2005) scoping approach. **Not** strict bottom-up Elo & Kyngäs inductive coding — see [`audit-trail.md`](../audit-trail.md) D-5._

## Overview

This conceptual framework organises the landscape of quantum computing in finance along two orthogonal dimensions:

1. **Problem space** — the financial problems being targeted
2. **Solution space** — the quantum / hybrid approaches being applied

The framework was constructed from an exploratory corpus of 29 academic papers, surveys, and industry reports. LLM-assisted extraction produced verbatim-quoted candidate labels per paper; the researcher then deductively normalised those labels onto an a-priori `PD-01..PD-10` / `SA-01..SA-11` vocabulary encoded in [`scripts/build_review_data_done.py`](../scripts/build_review_data_done.py). Phase 2 uses this framework as the deductive coding scheme for the 777-paper SLR; Phase 3 uses the **active** problem-space partition as silo boundaries.

## Active partition (read me before citing any matrix cell)

The headline "10 problem domains × 11 solution categories × 29 papers" overstates effective evidence. The corrected counts are:

| Metric | Headline | Active / effective | Reason |
|---|---|---|---|
| Problem domains | 10 (PD-01..PD-10) | **8** active | PD-08 (Cryptography) **excluded** (QKD-dominated, out of gate-based scope; D-3); PD-10 (Insurance) **retracted** (sole evidence file misidentified; D-1, D-2) and folded into PD-03 |
| Solution categories | 11 (SA-01..SA-11) | 11 active | No SA-level retractions; PD-08↔SA-09 disambiguation rule in [`codebook.md`](codebook.md) |
| Independent surveys / overviews in s1 corpus | 29 files | **≈ 20** | Minus 1 quarantined (AtharvaJain, D-1), minus 7 EXCLUSIONS (generic QC overviews), minus 1 Herman duplicate (2022 arXiv preprint superseded by 2023 published version; D-6) |

Both lifecycle states are codified in [`shared/config/unified_taxonomy.json`](../../shared/config/unified_taxonomy.json) (`status: excluded` for PD-08; `status: retracted, merged_into: PD-03` for PD-10) and enforced by [`tools/verify/v2_consistency.py`](../../tools/verify/v2_consistency.py).

## Problem-space taxonomy

| Code | Category | s1 papers (raw) | s1 papers (effective) | Status |
|------|----------|----------------:|----------------------:|--------|
| PD-01 | Portfolio Optimisation and Asset Allocation | 19 | 18 | active |
| PD-02 | Derivative Pricing and Valuation | 17 | 16 | active |
| PD-03 | Risk Management and Assessment | 18 | 17 | active (absorbs retracted PD-10) |
| PD-04 | Machine Learning and Pattern Recognition in Finance | 17 | 16 | active |
| PD-05 | Fraud Detection and Anomaly Detection | 12 | 11 | active |
| PD-06 | Trading and Market Microstructure | 7 | 6 | active |
| PD-07 | Credit Scoring and Lending | 11 | 10 | active |
| PD-08 | Cryptography and Financial Security | 9 | — | **excluded 2026-04-19** (QKD-dominated; D-3) |
| PD-09 | Simulation and Monte Carlo Methods | 14 | 13 | active |
| PD-10 | Insurance and Actuarial Science | 1 | — | **retracted 2026-05-02** (sole evidence misidentified; D-1/D-2; merged into PD-03) |

"Effective" columns subtract the one Herman duplicate from each row that contained both 2022 and 2023 entries. PD-08 / PD-10 effective counts are intentionally blank — those rows must not be cited as active evidence.

## Solution-space taxonomy

| Code | Category | s1 papers (raw) | s1 papers (effective) | Status |
|------|----------|----------------:|----------------------:|--------|
| SA-01 | Quantum Annealing and QUBO Formulations | 17 | 16 | active |
| SA-02 | Variational and NISQ Algorithms | 17 | 16 | active |
| SA-03 | Quantum Amplitude Estimation and Monte Carlo Integration | 16 | 15 | active |
| SA-04 | Quantum Machine Learning | 17 | 16 | active |
| SA-05 | Grover's Search and Variants | 11 | 10 | active |
| SA-06 | Quantum Linear Systems (HHL and Extensions) | 9 | 8 | active |
| SA-07 | Quantum Walks | 8 | 7 | active |
| SA-08 | Hybrid Quantum-Classical Approaches | 13 | 12 | active |
| SA-09 | Quantum Cryptography and Post-Quantum Security | 9 | 8 | active (cite the PD-08↔SA-09 overlap rule when used) |
| SA-10 | Quantum Fourier Transform and Phase Estimation | 5 | 4 | active |
| SA-11 | Error Mitigation and Fault Tolerance | 6 | 5 | active |

## Problem × Solution mapping matrix (active partition)

The matrix below shows the density of explicit problem–solution mappings in the **active 8 × 11 partition** with PD-08 and PD-10 rows omitted. Cells are counts of LLM-extracted mappings that survive the regex normalisation in `scripts/build_review_data_done.py`.

> **Caveat (D-4 overlap policy):** the same QAE / QMCI literature is double-counted under PD-02 × SA-03 and PD-09 × SA-03. The disambiguation rule in [`codebook.md`](codebook.md) ("Multi-tag and overlap policy") fires at Phase 2 classification time; for the Phase 1 matrix below the cells are not deduplicated. Treat the matrix as a *density indicator*, not a paper count.

| | SA-01 | SA-02 | SA-03 | SA-04 | SA-05 | SA-06 | SA-07 | SA-08 | SA-09 | SA-10 | SA-11 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| **PD-01** | 26 | 15 | 1 | 3 | 3 | 5 | · | 1 | · | · | · |
| **PD-02** | · | 3 | 17 | 2 | · | · | · | · | · | · | · |
| **PD-03** | 3 | 2 | 16 | 3 | 1 | 1 | 2 | 1 | · | 2 | · |
| **PD-04** | 1 | 1 | 1 | 8 | · | 2 | 1 | 2 | · | 1 | · |
| **PD-05** | 1 | 1 | 1 | 4 | 1 | · | · | 1 | · | · | · |
| **PD-06** | · | 1 | · | 5 | · | · | · | · | · | · | · |
| **PD-07** | 2 | · | 1 | 1 | · | · | · | 1 | · | · | · |
| **PD-09** | · | · | 8 | · | · | · | · | · | · | 1 | · |

**Retracted / excluded rows (do not cite as active evidence):**

| | SA-01..SA-11 | Note |
|---|---|---|
| ~~**PD-08**~~ | (was 0/0/0/0/0/0/0/0/13/0/2) | excluded 2026-04-19; QKD-dominated |
| ~~**PD-10**~~ | (was 0/0/1/0/0/0/0/0/0/0/0) | retracted 2026-05-02; sole evidence misidentified |

The pattern recovered in the matrix matches the well-known structure of the literature (annealing-heavy on portfolios; QAE-heavy on derivatives, risk, and Monte Carlo; QML cluster across PD-04/05/06/07). This is a positive sanity check on the LLM-assisted extraction, not an empirical novelty claim.

## Downstream dependencies

- **Phase 2** uses the active 8 × 11 partition as the deductive coding scheme. The codebook ([`codebook.md`](codebook.md)) operationalises the taxonomy and resolves the three known overlap seams (PD-02↔PD-09; SA-02∧SA-04; PD-08↔SA-09).
- **Phase 3** uses the active 8 problem domains as silo boundaries. Silo definitions are mirrored in [`shared/config/silo_inclusion.json`](../../shared/config/silo_inclusion.json) and verified by `tools/verify/v2_consistency.py`.
- **Background chapter** (Chapter 2) presents this framework narratively. The retraction of PD-10 and the exclusion of PD-08 should be surfaced in the chapter body, not only in the audit trail.

## Provenance

- **Method:** LLM-assisted extraction (verbatim quotes + locations + confidence) → researcher-curated regex normalisation against an a-priori PD/SA vocabulary → human-curated paper-level triage encoded in `EXCLUSIONS`, `NEEDS_RECHECK`, `HIGH_RELEVANCE` dictionaries (and `SUPERSEDED` for the Herman duplicate, D-6).
- **Audit:** divergence log entries D-1..D-7 in [`audit-trail.md`](../audit-trail.md). Quarantine / retraction artefacts in [`s1_extractions/_QUARANTINED_2026_AtharvaJain_misidentified.RETRACTION.md`](../s1_extractions/_QUARANTINED_2026_AtharvaJain_misidentified.RETRACTION.md).
- **Reproducibility:** rerun `python p1_framework_synthesis/scripts/build_review_data_done.py` then `python p1_framework_synthesis/scripts/build_taxonomy.py` from a clean checkout. Extraction prompt is versioned ([`prompts/extraction.txt`](../prompts/extraction.txt) header `version: 1.0`).
- **Limitation (out of freeze scope):** single-LLM single-pass extraction; no second coder; no inter-coder κ. Disclosed in [`README.md`](../README.md) §Methods and recorded as a deferred future-work item in `FREEZE.md`.
