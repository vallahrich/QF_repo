---
aliases:
- A Survey on Quantum Computational Finance for Derivatives Pricing and VaR
- Survey Quantum Computational Finance
authors:
- Andrés Gómez
- Álvaro Leitao
- Alberto Manzano
- Daniele Musso
- María R. Nogueiras
- Gustavo Ordóñez
- Carlos Vázquez
auto_detected: true
classification: ''
contradiction_flags:
- contradiction:classical-vs-quantum
- contradiction:scalability
doi: 10.1007/s11831-022-09732-9
evaluation_type: conceptual-only
evidence_type: ''
has_quantitative_results: false
idea_tags:
- idea:quantum-advantage
- idea:near-term-feasibility
- idea:hybrid-approach
journal_or_venue: Archives of Computational Methods in Engineering
methodology_tags:
- amplitude-estimation
- grover-search
- qft-phase-estimation
- quantum-walks
- quantum-linear-systems
- variational-nisq
- quantum-ml
- quantum-annealing-qubo
- hybrid-quantum-classical
- error-mitigation
paper_type: ''
quantum_advantage_claim: theoretical
related_papers: []
relevance_phase1: high
relevance_phase3: high
source_type: review-article
source_type_confidence: high
step1_date: unknown_pre_2026-05-02
step1_model: gpt-5-mini
step2_date: unknown_pre_2026-05-02
step2_model: gpt-5-mini
step3_date: unknown_pre_2026-05-02
step3_model: gpt-5-mini
step4_date: unknown_pre_2026-05-02
step4_model: gpt-5-mini
step5_date: unknown_pre_2026-05-02
step5_model: gpt-5-mini
step6_date: unknown_pre_2026-05-02
step6_model: gpt-5-mini
steps_completed:
- 1
- 2
- 3
- 4
- 5
- 6
tags:
- topic/derivative-pricing
- topic/risk-management
- topic/simulation-monte-carlo
- topic/quantum-ml-finance
- method/amplitude-estimation
- method/grover-search
- method/qft-phase-estimation
- method/quantum-walks
- method/quantum-linear-systems
- method/variational-nisq
- method/quantum-ml
- method/quantum-annealing-qubo
- method/hybrid-quantum-classical
- method/error-mitigation
- idea/quantum-advantage
- idea/near-term-feasibility
- idea/hybrid-approach
- contradiction/classical-vs-quantum
- contradiction/scalability
title: A Survey on Quantum Computational Finance for Derivatives Pricing and VaR
topic_tags:
- derivative-pricing
- risk-management
- simulation-monte-carlo
- quantum-ml-finance
year: '2022'
zotero_key: ''
---

## Abstract summary
This review surveys the state of the art in quantum computing applied to derivative pricing and risk measures such as Value at Risk (VaR). It summarizes classical pricing and risk models and numerical methods, describes quantum algorithms (notably quantum-accelerated Monte Carlo, PDE-based and machine-learning approaches), and discusses practical challenges to achieving quantum advantage such as distribution loading and payoff evaluation.
## Methodology
This article is a narrative literature review (a state-of-the-art survey) focused on quantum computing applications to derivative pricing and Value-at-Risk (VaR). The authors organise the work in two main parts: (1) a concise review of classical models and numerical methods used in pricing and risk (Black–Scholes, Heston, Monte Carlo, PDE/finite-difference, tree methods, regression/ANN approaches, factor models and PCA), and (2) a review of quantum alternatives and recent advances covering quantum-accelerated Monte Carlo (amplitude amplification/estimation and its variants), quantum PDE approaches (Hamiltonian mappings and imaginary-time propagation), and quantum machine-learning methods (QNNs, QPCA, QGANs, etc.). The paper synthesises and compares existing proposals from the literature, explains pipelines and building blocks (state loading, payoff encoding, amplification, estimation), and discusses resource and implementation challenges (distribution/loading cost, circuit depth, qubit counts, NISQ limitations, error correction overheads). The review cites and summarises relevant primary works, highlights open problems and bottlenecks, and provides qualitative assessment and discussion rather than new experimental results. No systematic review protocol, dataset search strategy, or experimental study is reported; the methodology is therefore a structured thematic literature synthesis and critical discussion.

**Algorithms used:** Quantum Amplitude Estimation (original QAE), Iterative/Max-Likelihood/Power-law/QoPrime variants of Amplitude Estimation, Amplitude Amplification (Grover-style), Grover's Algorithm, Quantum Fourier Transform (QFT), Quantum Phase Estimation (QPE), Quantum Coin / Quantum approximate counting, Quantum Walks, Hamiltonian simulation (including linear combination of unitaries and Trotterization), Harrow–Hassidim–Lloyd (HHL) quantum linear systems algorithm, Variational Quantum Eigensolver (VQE)-style / parameterized circuit approaches, Variational imaginary-time evolution / McLachlan variational principle, Quantum Principal Component Analysis (QPCA), Quantum Generative Adversarial Networks (QGANs), Quantum Neural Networks (QNNs), Quantum Kernel methods, Quantum annealing, Quantum-accelerated Multilevel Monte Carlo, Quantum approximate counting / Quantum counting
## Experiment details
<!-- Step 3 output — experiment replication details -->

## Findings
- [supported] Quantum Amplitude Estimation (QAE) and related amplitude-amplification techniques provide a theoretical quadratic improvement in estimation error scaling (O(1/M) versus classical O(1/sqrt(M))) for expectation-value computations.
- [supported] Recent variants of amplitude estimation (iterative QAE, maximum-likelihood QAE, power-law / QoPrime schedules, 'quantum coins') avoid the resource-intensive inverse Quantum Fourier Transform and reduce circuit depth or qubit requirements.
- [supported] The typical QAMC (quantum-accelerated Monte Carlo) pipeline requires (1) loading a probability distribution, (2) loading the integrand/payoff, (3) amplitude amplification, and (4) phase/ amplitude estimation; the loading steps are major practical bottlenecks.
- [supported] Preparing/loading arbitrary probability distributions or payoff functions into quantum states (state preparation / oracle construction) is expensive and often dominates total runtime; naive accounting of only the estimation subroutine can give misleading speedup claims.
- [speculative] If distribution/payoff loading and SDE-path generation can be implemented efficiently, end-to-end QAMC could deliver substantial runtime advantages for high-dimensional pricing and VaR problems.
- [supported] Several concrete proposals exist for distribution loading: Grover–Rudolph recursive splitting, controlled-rotation trees, variational/state‑ansatz methods (including QGANs), and tensor-network / MPS inspired encodings — each with trade-offs in accuracy, training cost and scalability.
- [supported] Generative quantum approaches (quantum walks, variational quantum simulation, trinomial/binomial tree encodings) have been proposed to directly simulate SDEs / path ensembles, but they transfer complexity from sampling to circuit depth or ansatz expressivity.
- [supported] Quantum PDE approaches map pricing PDEs to (possibly non-Hermitian) Hamiltonian evolution; two families are (a) direct propagation with an encoded Black–Scholes Hamiltonian and (b) imaginary-time (heat-equation) variational propagation.
- [speculative] Claims of exponential speedups for quantum PDE propagation subroutines exist under restrictive assumptions (e.g., diagonalization in momentum space), but overall exponential advantage is not established because of state-loading and generality limitations.
- [supported] Quantum Machine Learning (QML) techniques (QPCA, quantum regression, QNNs, quantum kernels, quantum generative models) have potential applicability to finance, but practical performance is limited by data-loading (QRAM) assumptions and instances of dequantization of some QML algorithms.
- [supported] For VaR and other risk-tail estimation tasks, comparative analyses show that quantum approaches still face strong challenges because tail probabilities require many samples and importance-sampling/rare-event methods remain necessary; quantum methods can help but do not yet eliminate sampling-cost issues.
- [supported] Resource-estimate studies (benchmarking path-dependent derivatives) find extremely large requirements for useful, error-corrected quantum advantage (example: ~7.5k logical qubits, ~4.6e7 T-gate depth, MHz clock assumptions), making near-term practical advantage unlikely.
- [supported] Realistic constraints—circuit depth limited by coherence, limited qubit counts, and large error-correction overheads—reduce chances of near-term, practical quantum advantage despite theoretical algorithmic speedups.
- [supported] Multi-level Monte Carlo has a quantum analogue (quantum multilevel Monte Carlo) and can be combined with amplitude-estimation-based subroutines to improve resource allocation across precision levels.
- [speculative] Quantum advantage claims that ignore end-to-end costs (distribution generation, payoff computation, state preparation, error-correction overhead) are incomplete; accounting for these often removes asymptotic speedups in practice.

**Results summary:** This review surveys quantum-algorithmic methods applied to derivative pricing and Value-at-Risk (VaR). It documents that quantum amplitude-estimation based methods give a provable theoretical quadratic improvement for expectation estimation, and that a number of algorithmic variants reduce the need for costly Quantum Fourier Transforms. It highlights that the main practical obstacles are state preparation (loading probability distributions and payoffs), realistic generation of stochastic paths (SDE simulation), circuit depth and qubit-count limits, and error-correction overheads. Quantum PDE mapping and QML approaches are promising but carry restrictive assumptions (e.g., specific Hamiltonian structure, QRAM availability) that limit immediate practical benefit. Resource-estimate studies show very large hardware requirements for meaningful, error-corrected advantage, so while theoretical speedups exist, no end-to-end, practically demonstrated quantum advantage for derivatives pricing or VaR has been established.

**Performance claims:**
- Theoretical Monte Carlo convergence: classical error scales O(1/sqrt(M)); quantum amplitude-estimation error scales O(1/M) (quadratic speedup).
- Amplitude-estimation depth/total-call tradeoff: total oracle calls N = O(1/ε^{1+β}) and sequential depth D = O(1/ε^{1−β}), interpolating between full QAE (β=0) and classical Monte Carlo (β=1).
- Resource-bound example from benchmark study [19]: approximately 7.5k logical qubits and ~46 million T-gate depth needed for certain path-dependent derivative pricing examples (with assumed 10 MHz logical clock), which is far beyond current hardware (~10 kHz).
- QAMC asymptotic cost including loading: T_QAMC = O(T_P / ε), where T_P is time to implement the oracle P that loads the probability distribution and ε is target precision, implying loading cost can dominate.
- Quantum PCA/QPCA offers asymptotic improvements (potential exponential in some formulations) but requires converting covariance matrix to a density matrix, purification (costing ~N^2 pre-processing), and typically n = 2 log(N) qubits for purification, limiting practical gains.
## Quantum advantage claim
**Classification:** theoretical

Algorithms (notably amplitude estimation and some Hamiltonian-propagation subroutines) provide provable asymptotic speedups in isolation, but practical, end-to-end quantum advantage for pricing and VaR remains theoretical: critical bottlenecks (state preparation, SDE-path generation, payoff evaluation, and error-correction overhead) and large resource estimates mean a demonstrated, practical advantage has not been achieved.
## Limitations
- Loading probability distributions into quantum states is a major bottleneck for QAMC and can dominate overall runtime (author-stated).
- Generation/simulation of underlying stochastic processes (SDEs) prior to loading is costly and often omitted from quantum speedup claims (author-stated).
- Claims of a quadratic speed-up from QAMC over classical Monte Carlo lack rigorous evidence when accounting for distribution generation and loading costs (author-stated).
- Quantum Fourier Transform (QFT) and phase-estimation based amplitude estimation require deep and wide circuits that are impractical for NISQ devices (author-stated).
- Many quantum algorithms assume oracles (P and R) or QRAM availability; these assumptions may be unrealistic or infeasible in near-term hardware (author-stated).
- Resource requirements (logical qubits, T-gate depth, clock rates) for practically valuable quantum advantage in realistic, path-dependent derivative pricing are extremely high and currently prohibitive (author-stated).
- Error-correction and related constant overheads can negate quadratic scaling advantages, making practical advantage unclear (author-stated).
- Efficient loading of arbitrary or empirical (VaR) distributions is not solved; many loading methods scale poorly with the number of discretization points (author-stated).
- Payoff function encoding can be complicated (especially non-piecewise-linear or exotic payoffs) and may require complex comparator circuits or pointwise loading that do not scale (author-stated).
- Some PDE-based quantum mappings (e.g., mapping to Hermitian Hamiltonians) rely on model-specific transformations (Black–Scholes) that are not generally applicable to more complex models (author-stated).
- Imaginary-time propagation approaches and variational ansatz methods introduce classical subroutines and normalization issues; scaling and efficiency are not thoroughly assessed (author-stated).
- Quantum Principal Component Analysis (QPCA) and similar algorithms require expensive pre-processing (e.g., N^2 classical operations, purification) and may not yield exponential speedups in practice (author-stated).
- Variational circuit approaches (including QGANs) lack rigorous performance guarantees; training can be costly, may get stuck, and must be redone per distribution (author-stated).
- Many QML proposals assume QRAM or state-preparation resources that may not be physically realizable in the near term (author-stated).
- [inferred] The energy, monetary cost and practical deployment overhead of quantum solutions (beyond asymptotic runtime) are not analyzed and could outweigh computational benefits.
- [inferred] Hardware connectivity and specific device architectures materially affect algorithm viability, yet many papers present hardware-independent claims.
- [inferred] Hybrid quantum-classical pipelines (e.g., classical pre-/post-processing around quantum subroutines) may shift computational bottlenecks to the classical side, reducing net benefit.
- [inferred] Dequantization results for some QML algorithms imply that putative quantum advantages may disappear under fair classical comparisons.
- [inferred] Comparator and piecewise payoff circuits increase circuit depth and width in nontrivial ways, making some pricing tasks impractical on NISQ machines.
- [inferred] Quantum walk and generative (pathwise) simulation methods may be sensitive to decoherence and noise, reducing their practical advantage.
## Open questions
- How can probability distributions (especially empirical ones for VaR) be loaded into quantum registers efficiently and scalably?
- Can the full pipeline for derivative pricing (including SDE simulation, state preparation, payoff encoding and amplitude estimation) achieve a net quantum advantage in realistic settings?
- What are optimal or provably efficient unitary encodings/representations of general payoff functions suitable for quantum circuits?
- Is it possible to generalize Hamiltonian/PDE mappings (used for Black–Scholes) to richer models (stochastic volatility, path-dependent features) while retaining efficient quantum simulation?
- How large are the practical resource thresholds (logical qubits, gate depth, error-correction overhead) required for a useful quantum advantage in typical financial derivatives (e.g., autocallables)?
- To what extent do error-correction costs and fault-tolerance requirements eliminate asymptotic quantum speedups for financial workloads?
- Are there hardware-aware algorithm designs that can deliver meaningful near-term improvements (NISQ-friendly) for pricing or VaR?
- Can amplitude estimation variants that avoid QFT (iterative, ML-based, power-law, QoPrime, quantum coin) be made robust and resource-efficient for real-world finance problems?
- What are the best strategies to generate pathwise distributions (simulate SDEs) natively on quantum devices (e.g., quantum walks, variational simulation) with acceptable fidelity and cost?
- How can variational/state-preparation training procedures (e.g., QGANs) be made reliable, scalable and fast enough for routine use in finance?
- Is QRAM feasible in practice, and if not, what are realistic alternatives for accessing large classical datasets from quantum algorithms?
- Can QPCA or other quantum linear-algebra subroutines be implemented with end-to-end speedups once all preprocessing and state-preparation costs are included?
- How should quantum advantage be defined and quantified in finance beyond asymptotic time complexity (including energy, monetary cost, and latency)?
- What are the trade-offs between circuit depth and total oracle calls (N vs D) for amplitude estimation in realistic hardware, and where is the sweet spot?
- Can imaginary-time variational propagation and its linear-system subroutines be implemented fully quantum (e.g., via HHL) with practical resource requirements?

**Future work:**
- Develop efficient (ideally optimal) algorithms and representations to load probability distributions into quantum states, particularly for empirical VaR data.
- Design efficient unitary encodings or compact quantum representations of common and exotic payoff functions to reduce circuit complexity.
- Study end-to-end quantum pipelines that include SDE generation/simulation, state preparation, payoff encoding and estimation to obtain realistic resource estimates and scaling.
- Investigate quantum algorithms for PDE-based pricing (including generalizations beyond Black–Scholes) and rigorously assess whether they can outperform classical PDE solvers.
- Advance amplitude estimation methods that avoid deep QFT circuits (iterative, ML/post-processing, power-law and QoPrime) and benchmark their resource/accuracy trade-offs on financial tasks.
- Explore tensor-network-based and variational circuit techniques for efficient state preparation and their applicability to finance distributions.
- Research quantum generative/simulation methods (quantum walks, variational simulation, trinomial trees) for native pathwise generation of stochastic processes.
- Assess the feasibility and design alternatives to QRAM for QML and quantum data access in finance.
- Quantify practical quantum advantage metrics for finance that include error-correction overhead, energy and monetary costs, and not just asymptotic runtime.
- Develop hybrid quantum-classical approaches and hardware-aware algorithm designs tailored to NISQ constraints and realistic device connectivity.
- Investigate robustness of QML methods (e.g., projected quantum kernels, QNNs, QGANs) on noisy hardware and their potential for PDE-solving and regression in finance.
- Provide detailed resource and architectural studies (qubits, gate counts, clock rates) for benchmark, path-dependent derivative pricing problems to identify realistic milestones toward advantage.
- Study dequantization risks and rigorously compare quantum proposals to best classical alternatives (including quantum-inspired classical algorithms).
## Key ideas
- #idea:quantum-advantage — Quantum Amplitude Estimation (QAE) offers a theoretical quadratic improvement for expectation estimation (O(1/M) vs O(1/sqrt(M))).
- #idea:quantum-advantage — Variants of QAE (iterative, ML, power-law, 'quantum coins') reduce circuit depth and qubit costs compared to original QFT-based QAE.
- #idea:near-term-feasibility — End-to-end speedups are threatened by state-preparation and payoff-loading costs; naive accounting of only the estimation subroutine overstates advantage.
- #idea:near-term-feasibility — Resource estimates for realistic derivatives (logical qubits, T-gate depths) are extremely large, making error-corrected advantage unlikely in the near term.
- #idea:hybrid-approach — Hybrid/variational methods, QGANs and classical preprocessing are proposed to mitigate data-loading and reduce qubit requirements.
- #idea:quantum-advantage — Quantum PDE approaches and quantum multilevel Monte Carlo are promising subroutines but exponential or end-to-end speedups require restrictive assumptions.
- #idea:near-term-feasibility — QML methods have potential but suffer from QRAM/data-loading assumptions and dequantization results that erode some claimed quantum benefits.
- #idea:hybrid-approach — Combining amplitude-estimation subroutines with classical importance-sampling and multilevel strategies can optimize resource allocation.
## Contradictions
- Paper argues many optimistic quantum-superiority claims are contradicted by end-to-end cost accounting: distribution/payoff loading and path generation often dominate runtime and eliminate the apparent algorithmic speedup.
- Resource-estimate studies summarized in the review contradict near-term scaling claims by showing extremely large qubit counts and gate depths (e.g., thousands of logical qubits and tens of millions of T gates) required for practical advantage.
- The review highlights that several QML proposals rely on QRAM or other strong data-access assumptions; dequantization results for some QML algorithms further contradict claims of inherent quantum superiority in finance.
## Notable quotes
<!-- Researcher-added — verbatim quotes with page references -->

## Researcher notes
<!-- Researcher-added — not LLM generated -->
