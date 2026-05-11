<!-- chapter-supporting-literature reading note
     paper_id:        246963801530
     selection_id:    C-19
     source_text:     shared/extracted_text/text/246963801530_a_systematic_literature_review_of_classical_and_quantum_machine_learning_approac.md
     generated_at:    2026-05-03T10:04:57.441758+00:00
     model:           gpt-5-mini
     temperature:     0.2
     prompt_version:  1.0 (2026-05-03)
     prompt_sha:      72a0945464a5
     rendered_sha:    6a147e3e7fca
     status:          PENDING researcher review
     accept by:       moving this file to ../<paper_id>__<slug>.md -->

> ✅ **REVIEW NOTE (researcher discretion, 2026-05-03)**: This note is **at an appropriate level of detail** for the Background chapter. Use the SLR-style methodology framing, the explicit NISQ definition, the NP-hard portfolio-optimisation framing, and the "hybrid is the dominant short-term technique" claim.
>
> **Skip / do not quote**: HHL, QAOA, QUBO descriptions from this paper (they are second-hand summaries of primary work that is itself out of scope for the chapter). Internal contradiction flagged: Abstract says 44 papers, Fig. 2 caption says 87 — verify or avoid citing the count.

# A Systematic Literature Review of Classical and Quantum Machine Learning Approaches for Mutual Fund Portfolio Optimization (2023)

**Authors**: Lydia Fernandes, Mugdha Kulkarni, Mandaar B. Pande  
**Venue**: 2023 IEEE Pune Section International Conference (PuneCon)  
**DOI**: 10.1109/PUNECON58714.2023.10450063  
**Suggested chapter sections**: §1.1 Motivation (Introduction), §1.2 Scope & contributions, §2.1 Quantum computing basics (NISQ, HHL, QAOA), §2.3 Portfolio optimization challenges (NP-hard, QUBO), §2.4 QML methods & benchmarks, §2.5 Research gaps

## 1-paragraph summary
This conference SLR reviews classical and quantum machine learning (QML) approaches applied to mutual fund portfolio optimization (MF PO). The authors report analyzing literature spanning 2003–2023, describe common ML and QML techniques (e.g., QUBO, quantum annealing, HHL, QAOA), summarize benchmarks and case studies (classical counterparts: genetic algorithms, simulated annealing, Gekko, exhaustive solver), and identify research gaps (NISQ limitations, applicability of quantum linear-algebra techniques, ML/DL limits for dynamic PO). The paper positions QML as a promising path for NP-hard PO problems but emphasizes current constraints and hybrid short-term solutions.

## Key concepts (with location)
- **Mutual Fund Portfolio Optimization (scope)** — Abstract (p.1) — "This review paper examines literature on classical and quantum machine learning approaches for Mutual Fund PO, analyzing 44 papers from 2003 to 2023."
- **NISQ (noisy intermediate-scale quantum computing)** — Introduction (p.1) — "The current stage of quantum technology research for devices with 50–1000 qubits that are not sufficiently advanced to produce fault-tolerant computers is known as noisy intermediate-scale quantum computing, or NISQ. [5]These processors are noisy, susceptible to quantum decoherence, and unable to do continuous quantum error correction."
- **Portfolio Optimization as NP-hard / NP-complete** — III. Literature Review / A. Classical Machine Learning Approaches for PO (p.3) — "The discrete nature of the portfolio optimization problem is NP-complete due to its strong non-linearity overpowering the continuous mean-variance portfolio optimization problem in terms of complexity levels [14]."
- **NP-hard statement (supporting)** — III. Literature Review / A. Classical Machine Learning Approaches for PO (p.3) — "PO was also examined to be a combinatorial optimization problem and research established that it was NP-hard [4], [28]."
- **HHL (quantum linear systems algorithm)** — III. Literature Review / B. Quantum Machine Learning Approaches for PO (p.3) — "A method to solve quantum linear system of equations introduced by Harrow, Hassidim and Lloyd (HHL) as an algorithm which forms the basis for several QML models. The NISQ-HHL algorithm is one such enhanced version of the former."
- **QUBO (Quadratic Unconstrained Binary Optimization) use** — III. Literature Review / B. Quantum Machine Learning Approaches for PO (p.3) — "The hybrid approach used was the Quadratic Unconstrained Binary Optimization (QUBO) technique and simulated annealing was chosen as the classical ML counterpart."
- **Quantum Annealer / QUBO as de facto standards** — IV. Discussion (p.4) — "Both the Quantum Annealer and the QUBO models are becoming the de facto standards for probing NP-complete and NP-hard issues in the context of quantum computing."
- **QAOA (Quantum Approximate Optimization Algorithm)** — IV. Discussion (p.4) — "Quantum Approximation Optimization Algorithm (QAOA) is one such quantum-based technique that offers a quick solution, with better quality solutions and answers to problems with vast parameters."

## Quotable claims (with location)
- Abstract (p.1) — "In principle, Quantum Computing, makes it possible to arrive at an optimal portfolio composition for a high return and low risk investment much faster than any existing supercomputer today." — *useful for: §1.1 Motivation*
- II. Research Methodology (p.2) — "The search yielded papers focusing on stocks as the underlying data rather than mutual funds data. This alone is a significant gap in the existing literature." — *useful for: §1.2 Scope & research gap*
- II. Research Methodology (p.2) — "Our statistics show an approx. 67.81% of the collection ranging in the year 2019 to 2023." — *useful for: §1.2 Literature trends*
- III. Literature Review / A. Classical Machine Learning Approaches for PO (p.3) — "Despite its positive characteristics, traditional ML approaches face time constraints, at times requiring days to run simulation-based epochs. They also have high costs due to their inability to consider risk calculations at various levels, including the curse of dimensionality, [4], [7], [10]." — *useful for: §2.3 Limitations of classical ML*
- III. Literature Review / B. Quantum Machine Learning Approaches for PO (p.3) — "Quantum Portfolio Optimization (QPO) is one application that has demonstrated experimental success, mapping the optimization work onto quantum technology [29]." — *useful for: §2.4 QML examples*
- IV. Discussion (p.4) — "Most implementations make use of hybrid techniques, which means that the algorithms combine classical and quantum computing." — *useful for: §2.5 Short-term practical approaches*
- IV. Discussion (p.4) — "PO is an area that should be researched more, based on early experimentation which has produced encouraging results." — *useful for: §1.2 Research directions*

## Limitations stated by authors
- NISQ performance / validation — Table III (p.4) — "The limited performance of NISQ technology makes it difficult to validate a quantum computer's output, prompting researchers to look for more effective ways to achieve higher quantum gate accuracy for future implementations."
- Applicability of quantum linear-algebra techniques — Table III (p.4) — "Quantum linear-algebra techniques may not always be applicable for specific linear-algebra and financial use cases due to prerequisites and constraint accommodations and may become a bottleneck to achieve quantum speedups."
- ML/DL limits for dynamic portfolio optimization — Table III (p.4) — "No dynamic portfolio optimization framework can outperform the covariance model. ML/DL approaches require more research due to the curse of dimensionality and the DL architectures inability to improve performance of sample-based portfolios."
- Practical qubit limitations & need for hybrid methods — IV. Discussion (p.4) — "Most implementations make use of hybrid techniques, which means that the algorithms combine classical and quantum computing. In the short term, this appears to be the most fruitful technique, as QCs have yet to acquire enough functional qubits to effectively optimize portfolios, unless a significant portion of the algorithm can be done on a traditional computer."

## How this paper might be used in the chapter
- §1.1 Motivation: cite the paper's claim that QC "in principle" promises faster MF PO solutions (Abstract) as part of motivation for quantum methods, with caveats from Table III.
- §2.1 Background — Quantum computing basics: use the paper's NISQ definition and discussion to introduce limitations of near-term devices.
- §2.3 Background — Portfolio optimization complexity: use the paper's NP-complete / NP-hard quotes to justify why PO invites quantum approaches.
- §2.4 QML methods: summarize concrete QML techniques the survey highlights (QUBO, quantum annealing, HHL, QAOA) and classical benchmarks (genetic algorithms, simulated annealing, Gekko) — cite relevant quotations.
- §2.5 Research gaps & future work: adopt the paper's Table III findings to motivate open problems (NISQ validation, applicability limits of quantum linear-algebra, ML/DL limitations).
- Consider citing alongside reviews such as Orús et al. (2019) and Preskill (2018) which the paper references when discussing broader QC-for-finance context.

## Researcher to verify
- [x] Verify the inconsistent counts (44 vs 87 papers) — RESOLVED-VIA-BANNER + DO-NOT-CITE the count: source-paper internal contradiction. Don't cite the number; cite the SLR-style framing only.
- [ ] Confirm page numbers used here against the PDF — ACTION REQUIRED at citation time: page numbers are LLM-assigned; verify against IEEE PuneCon proceedings pagination before citing specific pages.
- [x] Check the exact phrasing of the authors' exception note (400+ citations) — RESOLVED-VIA-BANNER: methodology details below the chapter's level of abstraction; not cited.
- [x] Verify details of benchmark methods and quantum hardware in III.B — RESOLVED-VIA-BANNER: secondhand summaries of HHL/QAOA/QUBO not cited from this paper (use primary sources directly).
