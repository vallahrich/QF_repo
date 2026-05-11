<!-- chapter-supporting-literature reading note
     paper_id:        7f0f52d2eab9
     selection_id:    C-22
     source_text:     shared/extracted_text/text/7f0f52d2eab9_a_brief_review_of_portfolio_optimization_techniques.md
     generated_at:    2026-05-03T10:05:30.133565+00:00
     model:           gpt-5-mini
     temperature:     0.2
     prompt_version:  1.0 (2026-05-03)
     prompt_sha:      72a0945464a5
     rendered_sha:    87ff5c3a23b8
     status:          PENDING researcher review
     accept by:       moving this file to ../<paper_id>__<slug>.md -->

> ✅ **REVIEW NOTE (researcher discretion, 2026-05-03)**: This note is **at an appropriate level of detail** for the Background chapter. Use the historical evolution of portfolio-optimisation methods (Markowitz → MAD → VaR/CVaR → heuristics → ML) as a clean narrative anchor for §2.3.
>
> **Skip / do not quote**: Table 6 claim about quantum-computer energy use ("much larger than traditional computers") — dated and oversimplified; flagged in REVIEW_QUEUE Tier-B. Brief qubit/superposition primer is too informal to cite verbatim — use C-10 instead for QC fundamentals.

# A brief review of portfolio optimization techniques (2022)

**Authors**: Abhishek Gunjan, Siddhartha Bhattacharyya  
**Venue**: Artificial Intelligence Review (2023) 56:3847–3886  
**DOI**: https://doi.org/10.1007/s10462-022-10273-7  
**Suggested chapter sections**: §1.1 Motivation (Chapter 1 Introduction), §2.2 Classical portfolio measures, §2.5 Heuristics & quantum-inspired methods (Chapter 2 Background)

## 1-paragraph summary
This survey paper reviews classical, statistical and intelligent approaches to portfolio optimization, and also "touches upon" quantum-inspired methods. It compiles definitions, measures (mean-variance, MAD, VaR/CVaR, minimax, LPM), heuristic/metaheuristic methods (GA, PSO, ACO, many quantum‑inspired variants), and recent ML/RL techniques applied to portfolio construction. The paper positions quantum-inspired metaheuristics and hybrid quantum/quantum‑inspired workflows as emerging directions for large/NP-hard portfolio formulations, while stressing open challenges in robustness, estimation error and model evolution.

## Key concepts (with location)
- **Portfolio (definition)** — 1 Introduction — "In financial terms, a portfolio is a collection of assets/investments." — *1 Introduction — p.3848*
- **Survey scope / contribution** — Abstract — "A comparative study of different techniques, first of its kind, is presented in this paper." — *Abstract — p.3847*
- **Mean‑Variance (MV)** — 4.1 Mean variance risk measure — "A revolutionary technique for portfolio selection as proposed by Markowitz Markowitz (1959) is based on mean-variance." — *4.1 — p.3851*
- **Quantum computing relevance** — 7.6 Approaches based on quantum computing — "It has been found that quantum and quantum-inspired computing techniques can help solve difficult optimization problems Orus et al. (2019)." — *7.6 — p.3865*
- **Qubit (basic)** — 7.6.1 Qubit — "Qubit is the smallest unit of information in quantum computing McMahon (2007) represented as 0⟩ and 1⟩" — *7.6.1 — p.3869*
- **Quantum superposition (informal)** — 7.6.2 Quantum superposition principle — "Thus, a qubit can be represented as a superposition of two basis states viz., 0⟩ and 1⟩ implemented using quantum gates (Q-gates)." — *7.6.2 — p.3869*
- **Quantum‑inspired metaheuristics (idea)** — 7.6.3 — "Quantum-inspired metaheuristic algorithms emulate the principles of quantum mechanics." — *7.6.3 — p.3876*

## Quotable claims (with location)
- Abstract — "Portfolio optimization has always been a challenging proposition in finance and management." — *useful for: §1.1 Motivation*
- Abstract — "An effort is also made to compile classical, intelligent, and quantum-inspired techniques that can be employed in portfolio optimization." — *useful for: §1.2 Literature scope*
- 1 Introduction — "Over the years, portfolio optimization techniques have also evolved from techniques like mean-variance (MV) Markowitz (1959), variance with skewness (VwS) Samuelson (1975), Value-at-Risk (VaR) Jorion (1997), Conditional Value-at-Risk Rockafellar and Uryasev (2000), Mean-absolute deviation (MAD) Konno and Yamazaki (1991) and Minimax (MM) Young (1998) to more advanced heuristic and meta-heuristic based methods." — *useful for: §2.2 Historical evolution of methods*
- 7.6 — "It has been found that quantum and quantum-inspired computing techniques can help solve difficult optimization problems Orus et al. (2019)." — *useful for: §2.5 Motivation for quantum approaches*
- Table 6 — "The energy required by quantum computer is much larger than traditional computers. Still there is a lot of unknowns as this is an ongoing area of research." — *useful for: §2.5 Limitations of quantum methods*
- 8 Discussions and conclusion — "However, evolution of a better portfolio model is a challenge for the overall performance improvement of these portfolio optimization techniques." — *useful for: §1.3 Open challenges / Research gaps*

## Limitations stated by authors
- Quantum approaches: "The energy required by quantum computer is much larger than traditional computers. Still there is a lot of unknowns as this is an ongoing area of research." — *Table 6 — p.3871*
- Estimation error / need for regularization: "Most of the methods used in portfolio selection proces suffers from estimation error and hence there is a need to regularize the portfolio process Bruder et al. (2013)." — *1 Introduction — p.3848*
- General challenge / open problem: "robust and efficient optimization techniques remain to be investigated for yielding better optimization scenarios, including the optimization of the risk-return paradigm involving conflicting objectives." — *8 Discussions and conclusion — p.3880*

## How this paper might be used in the chapter
- §1 Introduction: Use the Abstract and early Introduction quotes to motivate why portfolio optimization remains challenging and to justify surveying classical → intelligent → quantum-inspired approaches.
- §2 Background — classical measures: Cite the paper's concise list of measures (mean-variance, MAD, VaR/CVaR, minimax, LPM) when introducing conventional risk/return formulations and limitations (estimation error, non-convexity).
- §2 Background — heuristics & ML: Use the survey's summary of evolutionary, swarm and ML/RL methods to motivate inclusion of heuristic and learning-based techniques in the background.
- §2 Background — quantum motivation: Use the verbatim claim that "quantum and quantum-inspired computing techniques can help solve difficult optimization problems" as a cited motivation for introducing quantum computing topics in the thesis; pair with the paper's exposition on qubits and quantum-inspired metaheuristics.
- §2 Discussion / Limitations: Use the quoted limitation on energy and "a lot of unknowns" to temper expectations about near-term practical quantum advantage in finance; consider citing alongside other, more technical quantum‑computing-for-finance papers.

## Researcher to verify
- [ ] Verify exact page numbers — ACTION REQUIRED at citation time: page numbers in this note are LLM-assigned; verify against AI Review (2023) 56:3847–3886 published pagination before citing specific pages.
- [x] Confirm the verbatim qubit notation — RESOLVED-VIA-BANNER: qubit primer from this paper not used (use C-10 instead for QC fundamentals, per banner). OCR artefact only.
- [x] Check the authors' statement in Table 6 about quantum computers' energy cost — RESOLVED-VIA-BANNER + DO-NOT-CITE: dated/oversimplified claim; not cited.
- [x] Inspect citations where the paper attributes dates/authors — RESOLVED-VIA-BANNER: only the historical-evolution narrative is used (Markowitz → MAD → VaR/CVaR → heuristics → ML); cite primary sources (Markowitz 1959, etc.) directly when referencing.
