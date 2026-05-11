# Methodology Design: Quantum Computation for Financial Services

> **Status note (refreshed 2026-05-10): historical design scaffold, not a current methodology authority.** This file is retained to show how the methodology design evolved. Do not cite the body below as the final executed method without checking the freeze records. Current repository-truth is controlled by [../FREEZE.md](../FREEZE.md), [PROJECT_STATE.yaml](PROJECT_STATE.yaml), and the phase freeze records: [p1_framework_synthesis/FREEZE.md](../p1_framework_synthesis/FREEZE.md), [p2_systematic_review/FREEZE.md](../p2_systematic_review/FREEZE.md), [p3_thematic_synthesis/FREEZE.md](../p3_thematic_synthesis/FREEZE.md), and [p4_experiments/FREEZE.md](../p4_experiments/FREEZE.md). Known stale elements below include the three-phase-only design, strict Elo/Kyngas Phase 1 framing, interview/mixed-methods assumptions, and pre-Phase-4 tier assumptions.

## Current Method Snapshot

The submitted repository evidence follows a four-part pipeline:

| Phase | Current executed role | Current status authority |
|---|---|---|
| Phase 1 | Scoping/framework synthesis with LLM-assisted extraction and researcher-curated taxonomy normalization | [../p1_framework_synthesis/FREEZE.md](../p1_framework_synthesis/FREEZE.md) |
| Phase 2 | Systematic review and 6-step LLM-assisted classification/extraction of 777 included papers, with 755 active downstream after 22 retro-exclusions | [../p2_systematic_review/FREEZE.md](../p2_systematic_review/FREEZE.md) |
| Phase 3 | Thematic synthesis, quantitative extraction, filtered quantum-advantage triangulation, and descriptive finance framing across 8 active silos | [../p3_thematic_synthesis/FREEZE.md](../p3_thematic_synthesis/FREEZE.md) |
| Phase 4 | Canonical resource-estimation experiment layer over a 71-label cohort: 0 strict estimator labels, 13 family-template labels, 58 proxy labels | [../p4_experiments/FREEZE.md](../p4_experiments/FREEZE.md) |

The sections below remain useful for design provenance, terminology, and rationale, but they are not a promise that every early design element was executed.

## Systematic Literature Review — Research Design Documentation

---

## 1. Research Design Onion

This section documents the epistemological and methodological choices underpinning the study, following the Research Design Onion framework (Saunders, Lewis & Thornhill, 2019). Each layer justifies a design decision that constrains and informs the next.

### 1.1 Research Philosophy: Pragmatism

**Choice**: Pragmatism

**Justification**: This study sits at the intersection of computer science (algorithmic performance, computational complexity) and business (financial decision-making, operational improvement). A purely positivist lens would capture quantitative benchmarks but miss the contextual reasoning behind methodological choices in the literature. A purely interpretivist lens would capture thematic richness but struggle with the empirical, performance-oriented nature of quantum computing research.

Pragmatism allows us to treat the research question as the primary determinant of method. It supports the use of both quantitative evidence synthesis (benchmarking results across papers) and qualitative thematic analysis (understanding why certain approaches are favoured, where limitations persist, and what trajectories are emerging) without epistemological contradiction.

**Key implication**: The study does not commit to a single ontological position. It treats algorithmic performance results as objective and comparable, while treating research trends, motivations, and limitations as socially constructed within the research community.

### 1.2 Research Approach: Abductive

**Choice**: Abductive reasoning

**Justification**: The study follows neither a purely deductive nor purely inductive logic. Instead, it operates abductively — moving iteratively between framework and data through three phases:

- **Inductive movement** (Phase 1): The conceptual framework is constructed bottom-up from exploratory reading of academic and industry literature. Categories emerge from observed patterns in the literature — they are not imposed a priori.
- **Deductive movement** (Phase 2): The framework produced by Phase 1 is then applied top-down to systematically classify the full corpus. Categories that were inductively derived are now treated as fixed and applied mechanically.
- **Inductive movement** (Phase 3): Within each classified silo, thematic synthesis generates new analytical themes from the literature itself — themes that were not predetermined by the framework.

The resulting pattern — inductive → deductive → inductive — is characteristic of abductive reasoning. The study builds theory from observation (Phase 1), applies that theory to organise data (Phase 2), then generates new theory from within the organised data (Phase 3). This abductive cycle is well-established in systematic literature reviews in information systems and computing (Paré et al., 2015), where the research contribution lies in synthesising existing knowledge into novel thematic structures rather than testing hypotheses or generating grounded theory.

**Key implication**: The study produces both descriptive outputs (what is being researched, with what methods) and analytical outputs (why certain patterns exist, what they mean for the field's trajectory).

### 1.3 Methodological Choice: Multi-Method Study

**Choice**: Multi-method study combining qualitative thematic synthesis with quantitative benchmark comparison

**Justification**: The study employs two core analytical methods, each addressing a distinct dimension of the research questions:

1. **Thematic synthesis** (qualitative): The primary analytical engine. Applied in Phase 3 to generate descriptive and analytical themes about research patterns, methodological choices, computational challenges, limitations, and trajectories within each problem space silo.
2. **Quantitative benchmark comparison** (quantitative): Structured extraction and comparison of reported experimental results — problem sizes, performance metrics, classical vs. quantum comparisons, hardware platforms, and scalability assessments — within each problem space silo.

These two methods operate on the same silo structure in Phase 3 but answer different questions: thematic synthesis asks *what patterns and themes emerge from the literature*, while benchmarking asks *how do the reported results compare empirically*. They complement each other within each silo, with thematic findings providing interpretive context for benchmark data and benchmarks grounding thematic claims in empirical evidence.

Descriptive trend analysis (e.g., publication volume across problem or solution spaces over time) may be included where relevant to contextualise findings, but is not a core analytical commitment.

**Key implication**: The study is not a meta-analysis (no statistical pooling of effect sizes) nor a purely bibliometric study. It is a thematic synthesis enriched by structured quantitative comparison of reported results.

### 1.4 Research Strategy: Systematic Literature Review

**Choice**: Systematic Literature Review (SLR)

**Justification**: An SLR is the appropriate strategy when the research objective is to comprehensively map, classify, and synthesise a body of knowledge on a well-defined topic (Kitchenham & Charters, 2007; Tranfield, Denyer & Smart, 2003). The field of quantum computation for finance is:

- **Rapidly growing**: publication volume has increased significantly in recent years, making an ad hoc narrative review insufficient.
- **Interdisciplinary**: papers span computer science, physics, financial engineering, and operations research — requiring systematic cross-database search.
- **Fragmented**: findings are distributed across venues with different standards, terminologies, and evaluation approaches — requiring structured synthesis.

The SLR follows established guidelines from Kitchenham & Charters (2007) for the systematic process and adopts thematic synthesis (Thomas & Harden, 2008; Cruzes & Dybå, 2011) as the analytical method within the review.

### 1.5 Time Horizon: Cross-Sectional

**Choice**: Cross-sectional

**Justification**: The study captures the state of the field at a defined point in time (the search and screening cut-off date). While temporal trends are analysed descriptively (e.g., growth in publications, shifts in dominant methods), the thematic analysis itself represents a snapshot synthesis rather than a longitudinal tracking of the field's evolution.

### 1.6 Techniques and Procedures

**Choice**: Hybrid deductive-inductive thematic analysis (Fereday & Muir-Cochrane, 2006)

**Justification**: Documented in full in Section 3 below. The hybrid approach resolves the tension between the need for systematic organisation (deductive framework) and the need for discovery (inductive coding). This is operationalised through three distinct analytical phases, each with its own methodological grounding.

---

## 2. Project Structure: Three-Phase Design

The study is structured as a three-phase pipeline. Each phase has a distinct methodological identity, produces defined outputs, and feeds into the subsequent phase.

```
┌─────────────────────────────────────────────────────────────────────┐
│                     PHASE 1                                         │
│                Framework Synthesis                                  │
│    (Elo & Kyngäs, 2008; Hsieh & Shannon, 2005;                     │
│     Arksey & O'Malley, 2005)                                        │
│                                                                     │
│  Input:  Academic papers + industry reports (exploratory corpus)     │
│  Method: Inductive qualitative content analysis / scoping approach   │
│  Output: Conceptual framework                                       │
│          ├── Problem space taxonomy                                  │
│          └── Solution space taxonomy                                 │
└──────────────────────────┬──────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────────┐
│                     PHASE 2                                         │
│         Systematic Identification & Classification                  │
│              (Kitchenham & Charters, 2007)                          │
│                                                                     │
│  Input:  Phase 1 taxonomy + database search results                 │
│  Method: SLR protocol + structured deductive classification         │
│  Sub-steps:                                                         │
│          1. Database search & document fetching                     │
│          2. Deduplication                                           │
│          3. Manual screening (title/abstract → full text)           │
│          4. Final selection (n ≈ 900 papers)                        │
│          5. Structured coding against Phase 1 framework             │
│  Output: Classified corpus                                          │
│          ├── Papers tagged by problem space(s)                      │
│          ├── Papers tagged by solution space(s)                     │
│          ├── Metadata profiles per paper                            │
│          └── Clustered document sets (silos) for Phase 3            │
└──────────────────────────┬──────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────────┐
│                     PHASE 3                                         │
│                 Thematic Synthesis                                   │
│      (Thomas & Harden, 2008; Cruzes & Dybå, 2011)                  │
│                                                                     │
│  Input:  Clustered document sets from Phase 2                       │
│  Method: Inductive thematic synthesis (within-silo)                 │
│  Sub-steps:                                                         │
│          1. Line-by-line coding (fresh, per silo)                   │
│          2. Organisation into descriptive themes                    │
│          3. Generation of analytical themes                         │
│          4. Cross-silo comparison                                   │
│  Output: Thematic findings                                          │
│          ├── Within-silo analytical themes                          │
│          ├── Cross-silo patterns and gaps                           │
│          ├── Quantitative benchmark comparison                      │
│          └── Proposed experiments                                   │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 3. Phase Specifications

### 3.1 Phase 1 — Framework Synthesis

**Objective**: To understand the landscape of quantum computation in financial services — which problems are being targeted and which solutions are being explored — and to produce a conceptual framework (problem space taxonomy × solution space taxonomy) that structures all subsequent analysis.

**Methodological basis**: Inductive qualitative content analysis (Elo & Kyngäs, 2008; Hsieh & Shannon, 2005), applied within an exploratory scoping approach (Arksey & O'Malley, 2005).

**Scope**: Exploratory and self-contained. This phase reviews a purposively selected set of 10–20 academic papers and industry reports. It does not aim for exhaustive coverage (that is Phase 2's role) but for conceptual saturation — sufficient breadth to identify the major dimensions of the field.

**Design principle**: The LLM acts as an analytical assistant (structured extraction, candidate groupings), not an analytical authority. All final categorisation decisions are made by the researcher. The audit trail documents what the LLM proposed versus what was accepted, modified, or rejected.

**Provenance principle**: Every output carries a chain back to the source text. Extractions include verbatim quotes with page/section references. Open codes are linked to specific text chunks and source documents. Taxonomy categories list the codes and evidence passages that informed them. This ensures that the thesis can cite specific passages for every claim derived from Phase 1.

**Process**:

1. **Document selection**: Curate 10–20 key academic papers, survey articles, and industry reports into a dedicated Zotero collection. Add a note per item with selection rationale.
2. **LLM-assisted extraction**: Run each document through a structured extraction prompt producing a standardised profile. For every claim, the extraction must include **verbatim supporting quotes with page/section references** — not just summaries. Each extraction entry follows the structure: `(field, extracted_value, quote, location)`.
3. **Manual review and open coding**: Verify each extraction against the source. Correct errors, add missing information, annotate with initial open codes. Each code entry records: `(code_label, source_document, text_chunk, location)` to preserve the link from code to evidence.
4. **LLM-assisted code aggregation**: Feed all codes across all documents to the LLM. It proposes candidate groupings and category structures for both problem and solution spaces. The aggregation output must carry forward the source codes and their evidence chunks for each proposed category.
5. **Researcher-led taxonomy construction**: Review LLM proposals. Accept, modify, merge, split, or reject categories. Define names, working definitions, scope boundaries, and assign example papers. Each final category includes an **evidence column** listing the supporting codes, source documents, and text passages. Document decisions in audit trail.
6. **Framework documentation**: Produce the conceptual framework document, finalised taxonomies (with provenance), and the Phase 2 classification codebook.

**Outputs**:

- Conceptual framework document (self-contained, publishable as a standalone overview section of the thesis).
- Problem space taxonomy with category definitions and evidence provenance (codes → chunks → source documents).
- Solution space taxonomy with category definitions and evidence provenance.
- Classification codebook for use in Phase 2.
- Audit trail documenting LLM proposals vs. researcher decisions.

**Design rationale**: Inductive qualitative content analysis is appropriate here because the goal is to derive classification categories directly from the data through open coding, without predetermined categories. This matches Elo & Kyngäs' (2008) three-phase inductive process: open coding → creating categories → abstraction. The output is a categorisation scheme — a taxonomy and codebook — not themes or theory. Framework synthesis (Dixon-Woods, 2011) was considered but rejected because it assumes an existing or a priori framework to organise data into; here the framework must be constructed from scratch.

### 3.2 Phase 2 — Systematic Identification and Classification

**Objective**: To systematically identify, screen, and classify the relevant corpus of literature on quantum computation in finance using the framework developed in Phase 1.

**Methodological basis**: Systematic literature review protocol (Kitchenham & Charters, 2007; Tranfield, Denyer & Smart, 2003).

**Process**:

1. **Search**: Define search strings and execute across multiple academic databases (e.g., Scopus, Web of Science, IEEE Xplore, ACM Digital Library, arXiv).
2. **Deduplication**: Remove duplicate records across databases.
3. **Screening**: Apply inclusion/exclusion criteria through title/abstract screening, followed by full-text screening.
4. **Selection**: Finalise the included corpus (approximately 900 papers).
5. **Classification**: Apply structured deductive coding against the Phase 1 framework:
   - Tag each paper with one or more problem space categories.
   - Tag each paper with one or more solution space categories.
   - Extract metadata profile (year, venue, methodology type, dataset/benchmark used, quantum hardware vs. simulation, etc.).
6. **Clustering**: Group papers into problem space silos for Phase 3 analysis.

**Outputs**:

- PRISMA flow diagram documenting the search and screening process.
- Complete classified corpus with problem/solution space tags and metadata.
- Descriptive bibliometric overview (publication trends, venue distribution, geographic patterns).
- Document clusters (silos) defined by problem space, ready for Phase 3.

**Design rationale**: This phase is methodological infrastructure, not analytical interpretation. The classification applies the Phase 1 framework mechanically — no interpretive judgement about theme generation occurs here. This separation is important because it ensures that Phase 3's inductive coding is not contaminated by premature analytical decisions made during classification. The classification codebook provides reproducibility: another researcher using the same codebook should arrive at substantially similar classifications.

**Note on automation**: Parts of this phase (document fetching, deduplication, metadata extraction, structured tagging) may be supported by automated tooling. Any automated classification is subject to manual validation and correction. The methodology chapter should document the automation pipeline, validation procedures, and inter-rater reliability measures where applicable.

### 3.3 Phase 3 — Thematic Synthesis

**Objective**: To conduct in-depth, inductive analysis within each problem space silo, generating analytical themes about the state of research, computational challenges, methodological patterns, empirical results, limitations, and future directions.

**Methodological basis**: Thematic synthesis (Thomas & Harden, 2008), adapted for computing/IS literature reviews (Cruzes & Dybå, 2011).

**Process (per silo)**:

Each problem space silo is analysed independently using the following procedure:

1. **Line-by-line coding**: Read each paper within the silo and generate codes from scratch. Codes capture: research objectives, problem formulations, algorithmic choices, experimental setups, reported results, stated limitations, and future work directions. This coding is inductive — it is not constrained by the Phase 1 framework beyond the silo boundary itself.

2. **Descriptive theme organisation**: Group related codes into descriptive themes. These themes describe what the literature says about the problem space: which approaches dominate, which are emerging, how problems are typically formulated, what benchmarks are used, etc.

3. **Analytical theme generation**: Develop higher-order themes that go beyond description to interpretation. These analytical themes represent the study's contribution: identifying why certain approaches are favoured, where fundamental computational barriers exist, what contradictions appear in reported results, where the field is converging or diverging, and what opportunities remain unexplored.

4. **Quantitative benchmark comparison**: Structured extraction and comparison of reported experimental results within the silo. This includes: problem sizes tested, classical vs. quantum performance comparisons, hardware platforms used, noise/error characteristics, and scalability assessments. *(Note: this component is developed by a separate team member.)*

5. **Cross-silo comparison**: After within-silo analysis is complete across all silos, compare analytical themes across problem spaces to identify: shared computational challenges, solution methods that transfer across domains, and problem-specific vs. general patterns.

**Analytical template (consistent across silos)**:

Each silo analysis should address the following dimensions to ensure cross-silo comparability:

- **Problem characterisation**: How is the problem defined and formulated for quantum computation? What is the computational complexity class? What makes it a candidate for quantum advantage?
- **Solution landscape**: Which quantum and hybrid methods are applied? What is the distribution of approaches? What is the trajectory over time?
- **Empirical evidence**: What results are reported? At what scale? On what hardware or simulators? How do they compare to classical baselines?
- **Limitations and barriers**: What are the stated limitations? Where do hardware constraints, noise, qubit counts, or algorithmic scalability pose challenges?
- **Research gaps and opportunities**: What questions remain open? Where do the authors themselves identify future work? What gaps emerge from the synthesis that individual papers do not address?

**Outputs**:

- Within-silo thematic maps (visual representations of theme hierarchies).
- Analytical theme narratives per silo.
- Cross-silo comparison matrix.
- Quantitative benchmark tables and comparisons.
- Synthesised research agenda identifying gaps and opportunities.

**Design rationale**: The decision to code from scratch within each silo (rather than carrying forward Phase 2 codes) is deliberate. Phase 2 classification answers "what is this paper about?" at a categorical level. Phase 3 coding answers "what does this paper contribute to our understanding of this problem space?" at an analytical level. These are different questions requiring different levels of engagement with the text. Fresh coding prevents the silo labels from anchoring the analysis and allows unexpected themes to emerge.

---

## 4. Overarching Methodological Framing

### 4.1 Hybrid Deductive-Inductive Approach

The study's analytical logic is framed as a hybrid deductive-inductive approach following Fereday & Muir-Cochrane (2006):

| Analytical Movement | Phase | Description |
|---|---|---|
| Inductive | Phase 1 | Classification categories are derived bottom-up through open coding of a curated exploratory corpus, using inductive content analysis. |
| Deductive | Phase 2 | The Phase 1 framework is applied top-down to systematically classify the full corpus. |
| Inductive | Phase 3 | Themes are generated bottom-up from within-silo coding, unconstrained by the classification framework. |

The abductive character of the study emerges from this inductive → deductive → inductive cycle: observation builds the framework, the framework organises the data, and fresh observation within the organised data generates new insight. The framework channels attention without dictating conclusions.

### 4.2 Quality and Rigour

The following measures ensure methodological rigour across all phases:

- **Transparency**: Full documentation of search strings, inclusion/exclusion criteria, screening decisions, and coding procedures.
- **Reproducibility**: Classification codebook (Phase 1 output) enables independent replication of Phase 2 tagging.
- **Audit trail**: All coding decisions in Phase 3 are documented and traceable from raw text to descriptive theme to analytical theme.
- **Reflexivity**: Researcher positionality and potential biases are acknowledged, particularly regarding prior assumptions about quantum advantage.
- **PRISMA compliance**: The systematic search and screening process follows PRISMA 2020 reporting guidelines (Page et al., 2021).

### 4.3 Scope Boundaries

- The study analyses published academic literature and industry reports. It does not include primary data collection (interviews, experiments) as part of its core methodology, though proposed experiments are an output of Phase 3.
- The study does not perform statistical meta-analysis. Quantitative comparisons are descriptive and structured, not pooled statistically.
- The classification system acknowledges that papers may span multiple problem and solution spaces. Multi-tagging is permitted and documented.

---

## 5. Key Methodological References

| Reference | Role in this study |
|---|---|
| Saunders, Lewis & Thornhill (2019) | Research design onion framework |
| Elo & Kyngäs (2008) | Inductive qualitative content analysis (Phase 1) |
| Hsieh & Shannon (2005) | Qualitative content analysis approaches (Phase 1) |
| Arksey & O'Malley (2005) | Scoping review principles (Phase 1) |
| Kitchenham & Charters (2007) | SLR protocol guidelines (Phase 2) |
| Tranfield, Denyer & Smart (2003) | SLR methodology in management research |
| Thomas & Harden (2008) | Thematic synthesis methodology (Phase 3) |
| Cruzes & Dybå (2011) | Thematic synthesis in software engineering |
| Fereday & Muir-Cochrane (2006) | Hybrid deductive-inductive coding |
| Braun & Clarke (2006) | Thematic analysis foundations (referenced, not adopted) |
| Paré et al. (2015) | SLR typology in information systems |
| Page et al. (2021) | PRISMA 2020 reporting guidelines |

---

## 6. Design Decision Log

This section records key design decisions and their rationale for future reference.

| Decision | Rationale |
|---|---|
| Pragmatist philosophy over positivism or interpretivism | Study combines quantitative benchmarking with qualitative thematic analysis; pragmatism supports methodological pluralism without epistemological contradiction. |
| Inductive content analysis for Phase 1 rather than framework synthesis | Phase 1 derives categories bottom-up through open coding — no a priori framework exists. Framework synthesis (Dixon-Woods, 2011) assumes an existing framework; inductive content analysis (Elo & Kyngäs, 2008) is designed for constructing categories from data. The output is a categorisation scheme (taxonomy + codebook), not themes or theory. |
| Phase 1 recognised as inductive, not deductive | The framework is constructed bottom-up from literature, not imposed a priori. It only becomes deductive when applied in Phase 2. The full cycle (inductive → deductive → inductive) is what makes the study abductive. |
| LLM as analytical assistant, not authority (Phase 1) | LLM performs structured extraction and proposes candidate groupings; researcher makes all final categorisation decisions. Audit trail documents proposals vs. accepted/modified/rejected decisions to ensure methodological defensibility. |
| Multi-method study rather than multi-method qualitative | The quantitative benchmark comparison is a core analytical component, not a subordinate descriptive element. Thematic synthesis and benchmarking are co-equal methods operating on the same silo structure. |
| Bibliometric profiling downscaled to optional descriptive reporting | Trend analysis may contextualise findings but is not a methodological commitment. The real quantitative contribution is the benchmark comparison. |
| Merging search/screening and classification into a single phase | Classification is the terminal step of the systematic search process, not a separate analytical activity. Cleaner narrative. |
| Fresh inductive coding in Phase 3 rather than extending Phase 2 codes | Different analytical questions require different levels of engagement. Prevents classification labels from anchoring thematic discovery. |
| Consistent analytical template across silos | Enables cross-silo comparison while preserving within-silo inductive freedom. |
| Hybrid deductive-inductive framing | Resolves the apparent tension between pre-defined framework and emergent themes. Well-established in IS/computing SLR literature. |
| Thematic synthesis (Thomas & Harden) over reflexive TA (Braun & Clarke) | Reflexive TA designed for primary qualitative data; thematic synthesis designed for systematic reviews of published literature. |

---

*Document version: 1.2*
*Last updated: April 2026*
*Status: Methodology design — pre-implementation*