---
aliases:
- Quantum computing for finance
- Quantum computing finance
authors:
- Dylan Herman
- Cody Googin
- Xiaoyuan Liu
- Yue Sun
- Alexey Galda
- Ilya Safro
- Marco Pistoia
- Yuri Alexeev
auto_detected: true
classification: ''
contradiction_flags:
- contradiction:classical-vs-quantum
- contradiction:scalability
doi: ''
evaluation_type: conceptual-only
evidence_type: ''
has_quantitative_results: false
idea_tags:
- idea:quantum-advantage
- idea:near-term-feasibility
- idea:hybrid-approach
journal_or_venue: arXiv preprint arXiv:2307.11230
methodology_tags:
- amplitude-estimation
- grover-search
- quantum-walks
- quantum-linear-systems
- qft-phase-estimation
- variational-nisq
- quantum-annealing-qubo
- quantum-ml
- hybrid-quantum-classical
- error-mitigation
paper_type: ''
quantum_advantage_claim: speculative
related_papers:
- 2019_Tang_Dequantization
relevance_phase1: high
relevance_phase3: high
source_type: review-article
source_type_confidence: high
step1_date: '2026-04-14T12:27:17.926971'
step1_model: gpt-5-mini
step2_date: '2026-04-14T12:27:17.926971'
step2_model: gpt-5-mini
step3_date: '2026-04-14T12:27:17.926971'
step3_model: gpt-5-mini
step4_date: '2026-04-14T12:27:17.926971'
step4_model: gpt-5-mini
step5_date: '2026-04-14T12:27:17.926971'
step5_model: gpt-5-mini
step6_date: '2026-04-14T12:27:17.926971'
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
- topic/portfolio-optimization
- topic/risk-management
- topic/quantum-ml-finance
- topic/fraud-detection
- topic/credit-lending
- topic/simulation-monte-carlo
- method/amplitude-estimation
- method/grover-search
- method/quantum-walks
- method/quantum-linear-systems
- method/qft-phase-estimation
- method/variational-nisq
- method/quantum-annealing-qubo
- method/quantum-ml
- method/hybrid-quantum-classical
- method/error-mitigation
- idea/quantum-advantage
- idea/near-term-feasibility
- idea/hybrid-approach
- contradiction/classical-vs-quantum
- contradiction/scalability
title: Quantum computing for finance
topic_tags:
- derivative-pricing
- portfolio-optimization
- risk-management
- quantum-ml-finance
- fraud-detection
- credit-lending
- simulation-monte-carlo
year: '2023'
zotero_key: ''
---

## Abstract summary
This review surveys the state of the art of quantum computing applied to financial problems, with emphasis on stochastic modeling, optimization, and machine learning. It summarizes potential algorithmic advantages (e.g., quadratic speedups for quantum Monte Carlo and gradient estimation), discusses key implementation challenges (data loading, readout, error correction, and NISQ limitations), and highlights hardware and research directions needed to realize end-to-end advantage.
## Methodology
This work is a narrative, domain-focused literature review aimed at physicists and practitioners. The authors conducted a comprehensive survey of prior academic and industry literature on quantum computing applications in finance, concentrating on three broad technical areas: stochastic modeling (pricing, risk analysis, PDE approaches), optimization (continuous convex/non-convex, discrete and mixed integer programming, dynamic programming), and machine learning (supervised, unsupervised, generative, reinforcement learning). The methodology consisted of: (1) identifying representative financial problem classes (derivative pricing, Greeks computation, portfolio optimization, risk metrics, fraud/credit detection, etc.); (2) cataloguing classical solution methods used in industry and academia (Monte Carlo, quasi-Monte Carlo, finite-difference PDE solvers, interior-point methods, branch-and-bound, boosting, k-means, spectral clustering, RL methods); (3) surveying and explaining corresponding quantum algorithmic proposals, heuristics, and subroutines (e.g., QMCI/QAE, QLSAs, variational algorithms, quantum annealing, QAOA, quantum kernel/QNN approaches); (4) discussing implementation and end-to-end considerations including state-preparation, data loading, readout, pre/post-processing, circuit depth, quantum memory, error-correction overheads, and hardware constraints; and (5) synthesizing open challenges and research directions (resource estimation, dequantization results, hardware-native gate support, coherent arithmetic, QRAM limits). The review aggregates and compares asymptotic complexities, practical caveats (e.g., QBLAS caveats, sampling/readout costs, conditioning dependence), and references application-specific resource analyses in the literature. No original empirical experiments were executed; conclusions are drawn from critical analysis of published algorithms, theoretical results, and existing resource estimates.

**Algorithms used:** Quantum Monte Carlo Integration (QMCI), Quantum Amplitude Estimation (QAE), Amplitude Amplification, Grover's algorithm, Grover–Rudolph state preparation, Quantum Walk Search (QWS), Quantum Linear Systems Algorithms (QLSA) / HHL-like methods, Quantum Singular Value Transformation (QSVT), Block-encoding techniques, Hamiltonian simulation, Variational Quantum Simulation (VQS), Variational Quantum Eigensolver (VQE), Quantum Approximate Optimization Algorithm (QAOA), Quantum Annealing, Quantum Interior Point Methods (quantum IPMs), Quantum Simulated Annealing, Quantum Gradient Methods, Quantum Gradient Descent / Hamiltonian Descent variants, Quantum Principal Component Analysis (qPCA), Quantum Support Vector Machine (quantum SVM / QLSA-based SVM), Quantum Nearest-Neighbor algorithms, q-means / quantum k-means, Quantum Expectation-Maximization, Quantum Generative Models (QCBM - Quantum Circuit Born Machine), Quantum Generative Adversarial Networks (QGAN), Quantum Boltzmann Machines, Quantum Bayesian Networks, Quantum-enhanced Gaussian Process Regression, Quantum Boosting (quantum AdaBoost / SmoothBoost variants), Quantum-inspired / dequantized classical algorithms
## Experiment details
<!-- Step 3 output — experiment replication details -->

## Findings
- [supported] Quantum Monte Carlo integration (QMCI) provides a provable quadratic improvement in query complexity for estimating expectations: classical MCI scales as O(σ^2/ε^2) samples while QMCI can achieve O(σ/ε) quantum samples (with constant success probability).
- [supported] Variants of quantum amplitude estimation (QAE) reduce circuit depth and can mitigate some practical resource requirements compared to original QAE.
- [supported] State preparation / data loading (including loading classical distributions into quantum states or QRAM requirements) is a major practical bottleneck that can negate theoretical speedups.
- [supported] Black-box state-preparation approaches (Grover–Rudolph, black-box L1/L2 loaders, polynomial approximations) have fill‑ratio or success‑probability dependencies that make them inefficient for sharply concentrated distributions.
- [supported] Multi-level Monte Carlo (MLMC) techniques have quantum analogues that can remove an extra O(1/ε) time-discretization overhead under certain assumptions (i.e., quantum multilevel MCI).
- [supported] Quantum linear-system algorithms (QLSAs) and related QBLAS primitives can give asymptotic dimension or spectral advantages for solving linear-algebra subroutines (and thus some PDE / finite-difference approaches), but their practical usefulness is limited by conditioning dependence, readout sampling costs, and data-access assumptions.
- [supported] Quantum interior-point-method proposals and QBLAS-based convex optimization algorithms show improved worst-case dependence on dimensions in theory, but suffer from QBLAS caveats and sampling/readout overheads that often eliminate practical advantage in realistic financial instances.
- [supported] Dequantization / quantum-inspired classical algorithms (e.g., Tang 2019 and follow-ups) have shown that many claimed quantum exponential speedups for ML/QBLAS-style problems can be matched by sublinear classical randomized algorithms under certain data-access models (low-rank / sampling-access), reducing some quantum advantage claims.
- [supported] Quantum-native machine learning models (quantum neural networks, quantum kernels, QCBMs, QGANs) are expressive but there is no convincing evidence yet that they provide a practical advantage on classical financial data; initial numerical evidence often shows no advantage.
- [supported] Variational and heuristic quantum optimization methods (VQE, VQS, QAOA, quantum annealing) are active areas of research and have shown partial empirical or numerical promise, but face practical challenges: parameter tuning, barren plateaus, training difficulty, and unclear scaling to real financial sizes.
- [supported] Quantum approaches to Greeks (derivative sensitivities) and gradient estimation can reduce sampling complexity: quantum gradient methods can provide quadratic reductions in certain settings (e.g., quantum acceleration of bump-and-reprice and gradient estimation).
- [supported] For some structured convex relaxations of nonconvex financial problems (e.g., tax-aware portfolio optimization, sparse portfolio selection), classical convex relaxations can already give near-optimal results efficiently, reducing the opportunity space for quantum advantage on these problems.
- [speculative] There is potential for quantum advantage in finance in the long term if hardware and algorithmic bottlenecks (state preparation, readout, error correction overhead, QRAM, native multi-qubit gates, coherent quantum arithmetic, and faster gate rates) are addressed.
- [speculative] Quantum annealers and near-term heuristic devices could offer practical benefits for certain constrained combinatorial finance instances, but it is unknown a priori whether problem landscapes allow beneficial quantum tunneling or other hardware-specific effects.
- [supported] End-to-end quantum advantage for realistic, commercially relevant financial problems has not yet been demonstrated and remains unproven; many algorithms give theoretical/black‑box speedups but practical resource, readout, and data-loading costs often remove the advantage.
- [supported] Hardware architectural features such as native multi-controlled/multi-qubit gates, coherent quantum floating-point arithmetic, and scalable QRAM would materially reduce algorithmic overheads for many finance-targeted quantum algorithms, but current technologies are limited.

**Results summary:** This review synthesizes the literature on quantum computing for finance across stochastic modeling, optimization, and machine learning. Theoretical (black‑box) quantum algorithms such as quantum Monte Carlo integration and quantum amplitude estimation provide provable quadratic (or better, under assumptions) improvements in query or spectral complexity for core subroutines used in finance (pricing, risk metrics, PDE solves, linear-system solvers). However, a consistent theme is that realistic end-to-end advantages are undermined by practical bottlenecks: classical-to-quantum data loading, output readout/sampling costs, conditioning dependence and assumptions of QBLAS/QRAM, error-correction overheads, and the impact of dequantization results producing competitive classical algorithms. Variational and heuristic quantum methods have partial empirical promise but face training and scalability issues. The review concludes that while theoretical potential exists, no demonstrated practical quantum advantage for commercially relevant financial workloads exists yet, and substantial algorithmic and hardware advances are required.

**Performance claims:**
- Quantum Monte Carlo integration (QMCI) sample complexity: O(σ/ε) quantum samples versus classical Monte Carlo O(σ^2/ε^2) samples.
- Quantum gradient estimation for computing k Greeks: quantum sampling complexity O(√k σ/ε) versus classical bump-and-reprice O(k σ^2/ε^2).
- Quantum matrix multiplicative-weights (MMW) / SDP-solving complexity (best known quantum): ~O(s √m γ^4 + s √n γ^5) gate/oracle complexity (with m constraints, n variables, s sparsity, γ related to desired error), compared to classical MMW ~O(m n s γ^4 + n s γ^7) (as reported).
- Quantum k-means single-step complexity (proposed bound): O(M √k log(k) / ε) queries for a quantum-accelerated step (M = number of data points, k = clusters, ε = error), versus a direct classical step O(k M N) (N = dimension) under common assumptions.
- Multilevel Monte Carlo (classical) removes extra O(1/ε) from time discretization in MCI; quantum versions of MLMC have been proposed with similar guarantees (quantized MLMC).
- Dequantization result (Tang 2019): classical randomized algorithms can match certain quantum recommendation-system speedups under sampling-access assumptions, undermining claimed exponential quantum advantages in some ML settings.
## Quantum advantage claim
**Classification:** speculative

The review reports provable theoretical/black‑box speedups (e.g., QMCI quadratic improvement, QLSA dimension advantages), but stresses that end-to-end, practical quantum advantage for realistic financial workloads has not been demonstrated. Data-loading/readout costs, conditioning and sparsity assumptions, error-correction overhead, and dequantization results substantially limit or invalidate many claimed advantages today. Thus advantage remains a plausible long-term outcome contingent on algorithmic and hardware advances, but is not demonstrated.
## Limitations
- State preparation (loading classical probability distributions / payoff distributions) is expensive and often requires costly arithmetic or has poor scaling (filling-ratio dependence, polynomial/quasilinear costs).
- Readout / extraction of classical information from quantum states requires sampling and can negate algorithmic query speedups (classical sampling cost and poor error dependence).
- Pre- and post-processing overheads (including distribution integration, classical numerical methods used in state preparation) can significantly reduce or eliminate theoretical quantum speedups.
- Current noisy intermediate-scale quantum (NISQ) hardware has low fidelity and few qubits, limiting problem sizes that can be practically solved.
- Quantum error-correction overheads (space/time) are large and could prevent realization of stated quadratic (or better) speedups for finance applications.
- Many quantum linear-algebra subroutines (QBLAS / QLSA) have caveats: dependence on matrix conditioning, need for sparse matrices or special access models, and reliance on quantum memory / QRAM assumptions.
- Variants of quantum algorithms (e.g., QAE, QLSA, quantum IPMs) often encode results in quantum states requiring further costly extraction or are only advantageous in black-box/oracular settings.
- Multistep SDE discretization / time-stepping can introduce extra complexity that removes simple speedups (additional factors of O(1/ε) unless mitigated by multilevel approaches).
- Quantum heuristics (VQE, QAOA, quantum annealing) have unclear, problem-dependent performance and face challenges in parameter tuning, barren plateaus, and training difficulty (some optimizations are NP-hard).
- Quantum annealing advantages are uncertain since tunnelling benefits depend on problem landscape and mapping constrained financial problems to unconstrained forms can be costly in qubits and overhead.
- Dequantization results show that several proposed exponential quantum speedups for ML can be matched by classical randomized algorithms under realistic data-access models.
- Variational / quantum-native ML methods lack robust training methodologies comparable to classical backpropagation (parameter-shift rule sampling cost; vanishing gradients), impairing scalability.
- Many quantum algorithms assume access to quantum memory (quantum-read classical-write QRAM) that is currently unrealized and faces fundamental practical limitations.
- Quantum PDE and Hamiltonian-simulation-based approaches often require further sampling/estimation stages (QAE / QMCI) to extract observables, adding overhead and uncertainty to end-to-end advantage.
- Problem structure matters: classical specialized algorithms (e.g., MMW, interior-point, simplex, cutting-plane) are already highly efficient for many finance SCPs and may reduce the margin for quantum advantage.
- [inferred] Integrating quantum subroutines into existing financial IT, risk, and compliance pipelines will be operationally complex and could add hidden costs.
- [inferred] Wall-clock advantages may be negated by slow gate operation rates, circuit compilation and communication overheads even when asymptotic quantum speedups exist.
- [inferred] For many practical problem sizes and precisions required in finance, constants and polynomial factors in quantum algorithms may make them less competitive than classical approaches.
- [inferred] The need for extensive classical optimization, error mitigation, and hyperparameter tuning alongside quantum runs implies significant resource and workflow complexity.
## Open questions
- Can end-to-end quantum advantage (wall-clock and economic value) be achieved for realistic, commercially relevant financial problems?
- Can state-preparation methods be developed that load payoff/path distributions with sublinear qubit scaling and without prohibitive arithmetic costs?
- How can the sampling/readout bottleneck be reduced so that exponential or quadratic algorithmic advantages translate into practical speedups?
- Is it possible to build scalable, low-cost quantum memory (QRAM) or to find alternative data-access models that enable QBLAS-style speedups in practice?
- Can quantum algorithms be designed that avoid the conditioning and sparsity caveats of current QBLAS approaches or otherwise mitigate their effects?
- Do variational quantum neural networks or other quantum-native ML models provide practical advantages for classical financial data, beyond toy or quantum-native data distributions?
- What are resource-optimal implementations (qubits, gates, depth) of QMCI / QAE variants that are viable on early fault-tolerant devices?
- Can quantum interior-point methods (or other quantum convex optimization techniques) be made competitive end-to-end (including sampling/readout and data access) with classical solvers on financial SCPs?
- Are there practical problem classes or structured financial instances where quantum-walk/search or quantum simulated annealing yield provable and realized speedups versus classical heuristics?
- How broadly do dequantization results limit potential quantum speedups in ML for finance, and which quantum algorithms remain immune to dequantization?
- Can quantum generative models (QCBMs, QGANs, quantum Boltzmann machines) provide sampling advantages for distributional tasks in finance (e.g., scenario generation, copula modeling) that lead to practical benefits?
- What are effective strategies to mitigate barren plateaus and training difficulty in variational algorithms applied to high-dimensional financial tasks?
- How much do error-correction overheads reduce the theoretical advantages of quantum Monte Carlo and linear-algebra-based methods in realistic implementations?
- Can hardware features (native multi-qubit gates, coherent quantum arithmetic, faster gate clocks) be developed that materially reduce circuit complexity for financial algorithms?
- What are the trade-offs between hybrid classical-quantum pipelines versus fully quantum approaches for end-to-end financial workflows?

**Future work:**
- Reduce resource requirements for key components: state preparation (distribution loading), coherent quantum arithmetic, and output readout to make QMCI and QLSA-based methods practical.
- Develop hardware-aware quantum algorithms and circuit designs that exploit native multi-qubit gates and available device connectivities to lower depth and qubit counts.
- Design and prototype quantum memory architectures or practical QRAM alternatives and study their impact on algorithm feasibility.
- Advance quantum error correction and fault-tolerant architectures to reduce overheads that currently negate algorithmic speedups.
- Create and benchmark end-to-end resource analyses and wall-clock runtime studies (including pre/post-processing and sampling) for representative financial applications (pricing, VaR, portfolio optimization, etc.).
- Investigate alternative unitary procedures for payoff distribution loading that avoid heavy arithmetic and scale sublinearly with time steps.
- Explore and exploit problem structure in financial models (sparsity, low effective dimension, symmetries) to obtain targeted quantum speedups.
- Further study and empirically evaluate quantum heuristics (QAOA, VQE, quantum annealing) on realistic constrained financial optimization problems and incorporate domain-aware mixers/ansätze.
- Develop improved training methods for variational quantum models (combat barren plateaus, reduce sampling cost, hybrid optimization strategies).
- Investigate applicability and limits of quantum generative models for scenario generation, copula modeling, and other sampling-heavy financial tasks.
- Assess the implications of dequantized classical algorithms and develop quantum algorithms that remain robust to dequantization approaches.
- Explore quantum algorithm variants with reduced circuit depth (e.g., low-depth amplitude estimation) suitable for early fault-tolerant devices.
- Integrate quantum-walk based search methods with practical heuristic pruning and subproblem solvers used in industry branch-and-bound frameworks.
- Pursue cross-disciplinary work to address operational, explainability, and regulatory aspects of deploying quantum models in finance (feature extraction interpretability, model validation).
- Perform more application-specific resource estimations and prototyping to determine realistic near-term use-cases for quantum advantage in finance.
## Key ideas
- #idea:quantum-advantage — Quantum Monte Carlo integration / amplitude estimation offers a provable quadratic sample-complexity advantage for expectation estimation (QMCI: O(σ/ε) vs classical O(σ^2/ε^2) under idealized assumptions).
- #idea:quantum-advantage — Quantum linear-system algorithms and QBLAS primitives give asymptotic dimension/spectral advantages for some linear-algebra subroutines relevant to PDEs and pricing, in theory.
- #limitation:data-encoding — State-preparation and data-loading (QRAM) are major bottlenecks; black-box loaders and polynomial approximations have success-probability/fill-ratio issues that can erase theoretical speedups.
- #limitation:qubit-count — End-to-end resource estimates highlight very large qubit and coherence requirements (plus error-correction overhead) for many provable advantages, limiting near-term practicality.
- #limitation:noise — NISQ-era noise, circuit depth limits, and the need for error mitigation / fault tolerance undermine direct implementation of many ideal algorithms.
- #idea:near-term-feasibility — Variational/heuristic methods (QAOA, VQE, quantum annealing) show numerical/empirical promise on small instances but face barren plateaus, parameter tuning, and unclear scaling.
- #idea:hybrid-approach — Hybrid quantum-classical workflows, classical pre/post-processing, and reduced-depth QAE variants are identified as the most plausible near-to-medium-term paths to practical advantage.
- #contradiction:classical-vs-quantum — Dequantization and quantum-inspired classical algorithms (e.g., Tang 2019 and follow-ups) reduce or remove some claimed exponential quantum advantages in ML/QBLAS settings under realistic data-access models.
- #contradiction:scalability — Readout/sampling costs, conditioning dependence for QLSAs, and state-prep overhead often negate asymptotic improvements in realistic financial instances; theoretical favorable scalings rarely translate directly to end-to-end speedups.
- #limitation:no-empirical-validation — The review finds little convincing empirical evidence that quantum-native ML models (QNNs, QGANs, quantum kernels) outperform classical methods on real financial datasets to date.
## Contradictions
- Dequantization results (e.g., Tang 2019) show that many claimed exponential quantum speedups for ML/QBLAS-style problems can be matched by classical randomized algorithms under realistic data-access models, challenging claims of quantum superiority.
- Asymptotic advantages of QAE/QLSA/QBLAS are frequently contradicted by practical considerations—state-preparation/QRAM costs, readout/sampling overhead, and conditioning dependence—so scalability claims do not hold for many realistic financial instances without strong additional assumptions.
## Notable quotes
<!-- Researcher-added — verbatim quotes with page references -->

## Researcher notes
<!-- Researcher-added — not LLM generated -->
