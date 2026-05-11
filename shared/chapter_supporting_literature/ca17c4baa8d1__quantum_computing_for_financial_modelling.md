<!-- chapter-supporting-literature reading note
     paper_id:        ca17c4baa8d1
     selection_id:    C-12
     source_text:     shared/extracted_text/text/ca17c4baa8d1_quantum_computing_for_financial_modelling.md
     generated_at:    2026-05-03T10:03:45.076131+00:00
     model:           gpt-5-mini
     temperature:     0.2
     prompt_version:  1.0 (2026-05-03)
     prompt_sha:      72a0945464a5
     rendered_sha:    16b27816911d
     status:          PENDING researcher review
     accept by:       moving this file to ../<paper_id>__<slug>.md -->

> ✅ **REVIEW NOTE (researcher discretion, 2026-05-03)**: This note is **at an appropriate level of detail** for the Background chapter. Use the survey-style framing of QC-in-finance applications (Monte Carlo, QAE for risk and pricing, QML for credit, hybrid architectures, NISQ/qRAM limits).
>
> **Skip / do not quote**: the outdated "Google now embraces the record [for the most qubits] with 72 quantum processing qubits" claim (wrong as of 2026); the "fourfold sample-size reduction" attribution is ambiguous in the source — verify before citing. Watch for translation artefacts (e.g. "quantum width estimation" should be "amplitude estimation").

# Quantum Finance: Exploring the Implications of Quantum Computing on Financial Models (2025)

**Authors**: Jiawei Zhou  
**Venue**: Computational Economics (preprint / journal article)  
**DOI**: https://doi.org/10.1007/s10614-025-10894-4  
**Suggested chapter sections**: §1 Motivation/introduction; §2.1 Financial problems (risk, derivatives, portfolio optimization); §2.3 Quantum computing basics; §2.4 Quantum algorithms relevant to finance; §2.5 Quantum Monte Carlo & amplitude estimation; §2.6 Hardware & practical challenges

## 1-paragraph summary
This review surveys quantum computing applications in finance, emphasizing quantum Monte Carlo, quantum amplitude estimation (QAE), quantum optimization (including annealing and QAOA), and quantum machine learning. It highlights claimed efficiency gains for derivative pricing and risk measures (VaR/CVaR), discusses hardware and NISQ-era constraints, and identifies gaps such as scalability, data-quality, and hybrid quantum–classical integration. The paper frames both theoretical algorithms (Grover, HHL, QFT) and applied use cases (portfolio optimization, arbitrage, credit-scoring feature selection), and proposes future directions including hybrid systems, quantum cryptography, and blockchain intersections.

## Key concepts (with location)
- **Quantum Amplitude Estimation (QAE)** — 5 Quantum Amplitude Estimation & Monte Carlo — p.1064 — "Brassard et al. (2002) extracted their quantum width estimation (QAE) algorithm, which is a crucial component of numerous more intricate quantum algorithms. Specifically, it can be used to compute the expected value using Monte Carlo sampling and then obtain a quadratic estimate."
- **Quantum Monte Carlo speedup (Montanaro)** — 5 Quantum Amplitude Estimation & Monte Carlo — p.1064 — "Montanaro (2015) demonstrated that Monte Carlo simulations could be performed on a quantum computer with about a fourth of the samples k needed to achieve the accuracy indicated by the equation in Fig. 8 (Montanaro, 2015)."
- **Grover’s algorithm (quadratic search speedup)** — 2.4 Quantum Computing in Finance — p.1050 — "Grover’s algorithm locates a given index in an unordered database in O(√N) steps, not to be overlooked when discussing significant developments in the realm of quantum physics (Grover, 1996)."
- **HHL algorithm (quantum linear systems)** — 2.4 Quantum Computing in Finance — p.1050 — "When it comes to solving systems of linear equations, the Harrow, Hasidim, and Lloyd (HHL) algorithm exponentially outperforms the best classical selection algorithm (Harrow et al., 2009)."
- **Quantum Annealing / QUBO formulation** — 3 Quantum Optimization / 3.2 Optimal Arbitrage Opportunities — p.1054–1057 — "Consequently, the quantum unconstrained proper binary optimization (QUBO) problem is the root cause of the issue."
- **NISQ (Noisy Intermediate-Scale Quantum)** — 2.6 Challenges for Quantum Computing — p.1051 — "Many academics have resorted to techniques based on processing so-called noisy intermediate quanta (NISQ) to overcome these challenges."
- **qRAM (quantum RAM) gap** — 2.6 Challenges for Quantum Computing — p.1052 — "Currently, a quantum random access memory (qRAM) that can safely store this information for extended periods and efficiently encode it into a quantum state is not available."

## Quotable claims (with location)
- Abstract — "Quantum Monte Carlo algorithms provide substantial efficiency gains, reducing sample size requirements by up to fourfold compared to classical methods." — *useful for: §2.5 Quantum Monte Carlo; Chapter 2 background on algorithmic speedups*
- 5 Quantum Amplitude Estimation & Monte Carlo — p.1064 — "Brassard et al. (2002) developed a quantum amplification algorithm (QAA) by extending Grover’s search method (Grover, 1996)." — *useful for: §2.4 Algorithms background; technical note on QAE provenance*
- 5 Quantum Amplitude Estimation & Monte Carlo — p.1064 — "Specifically, p can be assessed in an M-oracle call with an error ϵ = 2π(1 − p)/M + π2/M, a measure with success probability ≥ 8/π2, which is the case if the probability interval |Ψ⟩ equals p." — *useful for: §2.5 QAE technical detail / limitations*
- 5 Quantum Amplitude Estimation & Monte Carlo — p.1064 — "Montanaro (2015) demonstrated that Monte Carlo simulations could be performed on a quantum computer with about a fourth of the samples k needed to achieve the accuracy indicated by the equation in Fig. 8 (Montanaro, 2015)." — *useful for: §2.5 Monte Carlo speedups*
- 5.2 Risk Analysis — p.1065 — "they were able to compute CVaR and VaR four times faster and with greater accuracy utilizing the QAE technique, which makes use of an Oracle custom function." — *useful for: §2.5 Risk measurement and case examples*
- 2.6 Challenges for Quantum Computing — p.1051 — "It is imperative to note that creating a quantum computer that performs better than a classical computer is a tremendously challenging endeavor and may rank among the century’s biggest challenges." — *useful for: §2.6 Hardware & practical constraints*
- 2.6 Challenges for Quantum Computing — p.1051 — "one of the most significant issues is context, or the uncontrolled interaction between a system and its environment." — *useful for: §2.6 Decoherence / error correction discussion*
- 2.5 Existing Quantum Hardware — p.1051 — "With 72 quantum processing qubits, Google now embraces the record for the most qubits within the architecture of a gate." — *useful for: §2.5 Current hardware landscape*
- 6 Conclusion and Future Work — p.1065 — "The review’s prominent contributions include an extensive discussion of modern quantum algorithms applied to finance, including quantum annealing and quantum machine learning." — *useful for: §1 Introduction (scope) and §2 Literature synthesis*

## Limitations stated by authors
- Scalability, integration, data quality, regulatory constraints — 5.3 Limitations of Monte Carlo Methods — p.1065–1066 — "However, questioning scalability is one of the problems with quantum Monte Carlo methods (Adegbola et al., 2024). As for quantum computing applications, real-time applications, including high-frequency trading or dynamic portfolio rebalancing, require extremely fast computation and low latency, which are not yet available in quantum computing hardware."
- Error correction and qubit overhead — 2.6 Challenges for Quantum Computing — p.1051 — "The most considerable challenge is that many physical qubits may be required for a single fault-tolerant qubit to function."
- Data quality and sample size requirements for Monte Carlo — 5.3 Limitations of Monte Carlo Methods — p.1065 — "A significant limitation is the need for large and high-quality data with high computational costs (Matsakos & Nield, 2023)."
- Absence of production-ready qRAM — 2.6 Challenges for Quantum Computing — p.1052 — "Currently, a quantum random access memory (qRAM) that can safely store this information for extended periods and efficiently encode it into a quantum state is not available."

## How this paper might be used in the chapter
- §1 (Introduction): Use the Abstract quote and conclusion sentences to motivate potential efficiency gains and open research directions ("Quantum Monte Carlo algorithms provide substantial efficiency gains..." — Abstract) as framing for why quantum computing matters for financial services.
- §2 (Background — Quantum algorithms): Cite Grover, HHL and QAE descriptions and the Brassard et al. provenance for QAE when defining algorithmic primitives and expected asymptotic improvements.
- §2 (Background — Monte Carlo & risk): Use the Montanaro and Woerner & Egger claims to discuss quantum speedups in derivative pricing and VaR/CVaR estimation, while pairing with the paper’s limitations section to present caveats.
- §2 (Background — Hardware & constraints): Use the NISQ, qRAM, and error-correction quotes to justify a subsection on practical hardware limits and the need for hybrid quantum–classical solutions.
- §2 (Background — Research gaps): Use Table 5 summary and explicit listed research gaps as a compact literature-gap map to motivate the thesis research questions (hybrid frameworks, scaling QAE, regulatory integration).

## Researcher to verify
- [ ] Verify the claim in the Introduction that the paper "introduces a new algorithm for quantum computers in derivative pricing" — ACTION REQUIRED at citation time: confirm whether this is a review or contains a novel algorithm before describing the paper to readers.
- [ ] Confirm the numerical claim "reducing sample size requirements by up to fourfold" attribution — ACTION REQUIRED at citation time: trace attribution between Montanaro (2015) and Woerner & Egger (2019) in the source PDF before citing the number; otherwise prefer the primary Montanaro 2015 paper.
- [x] Check the exact page locations and any figure references (Fig. 8 / Chebyshev expression) — RESOLVED-VIA-BANNER: equation/figure technical details below the chapter's level of abstraction; not cited.
- [x] Validate the hardware statement "With 72 quantum processing qubits, Google now embraces the record..." — RESOLVED-VIA-BANNER + DO-NOT-CITE: outdated as of 2026 (IBM has surpassed 1000+ since 2023). Use a current source for hardware milestones.
