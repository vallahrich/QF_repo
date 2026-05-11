---
aliases:
- Reduction of Qubits in Quantum Algorithm for Monte Carlo Simulation by Pseudo-random
  Number Generator
- Reduction Qubits Quantum Algorithm
authors:
- Koichi Miyamoto
- Kenji Shiohara
auto_detected: true
classification: ''
contradiction_flags:
- contradiction:scalability
doi: ''
evaluation_type: simulator
evidence_type: ''
has_quantitative_results: true
idea_tags:
- idea:quantum-advantage
- idea:near-term-feasibility
- idea:hybrid-approach
journal_or_venue: arXiv preprint arXiv:1911.12469
methodology_tags:
- amplitude-estimation
- hybrid-quantum-classical
paper_type: ''
quantum_advantage_claim: theoretical
related_papers: []
relevance_phase1: high
relevance_phase3: high
source_type: preprint
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
- topic/simulation-monte-carlo
- topic/risk-management
- method/amplitude-estimation
- method/hybrid-quantum-classical
- idea/quantum-advantage
- idea/near-term-feasibility
- idea/hybrid-approach
- contradiction/scalability
title: Reduction of Qubits in Quantum Algorithm for Monte Carlo Simulation by Pseudo-random
  Number Generator
topic_tags:
- simulation-monte-carlo
- risk-management
year: '2020'
zotero_key: ''
---

## Abstract summary
The paper proposes reducing qubit requirements in quantum Monte Carlo by implementing pseudo-random number generators (notably PCG) on quantum circuits to sequentially generate sample paths and then estimating the sample average with quantum amplitude estimation, retaining the quadratic speedup while using far fewer qubits. It gives concrete circuit constructions, demonstrates an integration example and an application to credit risk measurement, and discusses the trade-off between qubit savings and increased circuit depth.
## Methodology
The authors propose a quantum Monte Carlo approach that reduces qubit requirements by generating pseudo-random numbers (PRNs) sequentially on a single quantum PRN register rather than allocating one register per random variable. The method implements a pseudo-random number generator (PCG: permuted congruential generator, built on an LCG plus a permutation) as quantum gates: PPRN (advance PRN by one) and JPRN (jump-to-start-of-subsequence). For an integrand that can be computed sequentially (yn = fn(yn-1,xn)), the circuit prepares an equal superposition over Nsamp starting indices, uses JPRN to load starting PRNs, then alternates applying a calculation step fn and PPRN to progress the PRN and update a running integrand register. The final integrand values are encoded into an ancilla amplitude (via controlled rotations) and the average (Esamp) is estimated by amplitude estimation / likelihood-based amplitude estimation (following Suzuki et al.). The paper details gate constructions for modular arithmetic (multiplication, addition) required for LCG, and for permutation steps (random rotation and xorshift) implemented with controlled-SWAP (Fredkin) and CNOTs. The approach is applied conceptually to the Merton credit-loss model (circuit-level description) and demonstrated on a small toy multivariable integral using a Qiskit simulator, using a small LCG instance and amplitude-estimation-by-likelihood with multiple powers of the Grover-like operator.

**Algorithms used:** Amplitude Estimation (likelihood-based variant, Suzuki et al.), Permuted Congruential Generator (PCG) / Linear Congruential Generator (LCG), Random rotation / xorshift permutations (bitwise permutations), Modular arithmetic circuits (modular multiplication/addition), Maximum-likelihood estimation for phase/amplitude
**Frameworks:** Qiskit

**Experimental setup:** Demonstration run on the Qiskit quantum-circuit simulator. Small-scale toy experiment: evaluate a 2-variable trigonometric integral using a 5-bit LCG PRNG (a=11, c=0, m=31, seed=1), Nsamp=8 sample points (uses 16 PRN elements), amplitude estimation with M=8 and Nk=100 measurements per chosen power mk (mk = 2^k). Implementations of adders/multipliers follow referenced quantum-arithmetic circuits.
## Experiment details
### Input
{'problem': 'Toy integration of I = (1/θ^Nvar) ∫ ... ∫ sin^2(sum xi) over Nvar=2 with θ=π/6', 'PRNG': {'type': 'LCG (used for demonstration); proposed PCG for general use', 'parameters': {'a': 11, 'c': 0, 'm': 31, 'seed': 1}, 'output_bits': 5, 'period': 30}, 'sampling': {'Nsamp': 8, 'PRN_elements_used': 16}}

### Process
{'pipeline_steps': ['Construct quantum circuit that prepares equal superposition over Nsamp starting indices (Hadamards).', 'Use JPRN to load the starting PRN element for each index into the PRN register.', 'For each sample sequence: sequentially apply controlled rotations (or compute integrand into a register) while advancing PRN via PPRN to accumulate the integrand contribution (sequential evaluation of fn).', 'Encode the integrand value into an ancilla qubit amplitude via controlled Ry rotations (angle proportional to integrand).', 'Construct Grover-like operator Q = -A S0 A^{-1} S_chi and apply Q^m for various m values (mk = 2^k).', 'For each chosen mk, perform Nk = 100 measurements of the ancilla; record hk successes.', 'Use likelihood maximization over θa (phase/amplitude) based on the observed counts across mk to estimate the target probability (Esamp) and thereby the integral.', 'Compare the quantum-based estimate with the exact integral and the arithmetic average over the chosen sample points.'], 'parameters_used': {'Nvar': 2, 'θ': 'π/6', 'nsamp (qubits for sample index)': 3, 'nPRN (PRN bits)': 5, 'M': 8, 'mk': '2^k for k=0..8', 'Nk': 100}}

### Output
{'format': 'scalar estimate of the integral (estimated probability to observe ancilla=1)', 'reported_values': {'exact_integral': 0.074578, 'exact_average_on_sample_points': 0.078394, 'quantum_estimate': 0.078391}, 'metrics': ['Numerical estimate of integral vs exact value', 'Comparison to arithmetic sample-average baseline'], 'baselines': ['Exact analytic value', 'Arithmetic mean over chosen sample points']}

### Parameters
- nsamp_qubits: 3
- nPRN_bits: 5
- Nsamp: 8
- PRNG_a: 11
- PRNG_c: 0
- PRNG_m: 31
- PRNG_seed: 1
- Nvar: 2
- theta: pi/6
- M_for_AE: 8
- mk_list: [1, 2, 4, 8, 16, 32, 64, 128, 256]
- Nk_shots_per_mk: 100

### Hardware
{'simulator': 'Qiskit simulator (IBM Qiskit)', 'QPU_model': None, 'cloud_provider': 'IBM (Qiskit ecosystem)'}

### Reproducibility
A small-scale proof-of-concept was run on the Qiskit simulator with parameter values reported in the paper. The authors reference specific adder/multiplier circuit constructions (citations) used to implement modular arithmetic. No code repository or implementation files are provided in the preprint; reproduction would require reimplementing the circuits in Qiskit following the described parameter settings (PRNG params, Nsamp, mk, Nk) and the referenced arithmetic constructions. The paper lists referenced implementations and parameter choices, which are sufficient to attempt reproduction but no direct code or data link is given.
## Findings
- [speculative] Quantum Monte Carlo estimation achieves quadratic convergence in sample error (error ∝ N^{-1}) compared with classical Monte Carlo (error ∝ N^{-1/2}), and this quadratic speedup is the basis for applying amplitude estimation to Monte Carlo problems.
- [supported] Previous quantum Monte Carlo proposals represent each required random number on a separate quantum register, making the required qubit count proportional to the number of random numbers (problem dimension) (citations [2–5]).
- [speculative] One can reduce the number of qubits by implementing a pseudo-random number generator (PRNG) on the quantum circuit, sequentially generating PRNs in a single register and computing the integrand step-by-step (a quantum analogue of classical Monte Carlo using PRNs).
- [speculative] Using amplitude estimation on the superposition of sampled integrand values produced by the PRNG-based method yields the same quadratic speedup in estimation error as standard quantum Monte Carlo amplitude-estimation approaches (up to the sampling/statistical error from using Nsamp PRN trajectories).
- [speculative] The reduction in qubits comes at the cost of increased circuit depth: sequential PRN generation and sequential integrand evaluation make depth scale with the number of random numbers (Nran) required per sample.
- [speculative] The permuted congruential generator (PCG) is a practical PRNG choice for quantum implementation because it composes simple LCG steps with efficient bit-permutations (which can be implemented with controlled swaps and CNOTs), balancing working-space qubit requirements and circuit depth.
- [speculative] The PCG quantum implementation requires primarily modular multiplication and addition primitives; modular multipliers dominate resource costs (ancilla qubits O(n), depth O(n^2) for n-bit words), so PRN generation typically does not dominate overall cost when integrand steps are heavier.
- [speculative] For problems whose integrand can be evaluated sequentially (y_n = f_n(y_{n-1}, x_n)), for example many Markov-process-based derivative pricing problems and credit portfolio loss computations, the PRNG-sequential approach is applicable.
- [speculative] The method can be applied to credit risk measurement under the Merton model by treating the portfolio loss as a sequential sum of obligor contributions and using a single PRN register to sample idiosyncratic variates while conditioning on a common systematic factor.
- [supported] The authors implemented a small-scale proof-of-concept simulation (Qiskit) for a two-variable trigonometric integral. Reported values: exact integral 0.074578; exact average on chosen sample points 0.078394; quantum-circuit-based estimate 0.078391 (demonstrating that the circuit produces the sample-average result).
- [speculative] Increasing Nsamp (number of sampled PRN trajectories) reduces the sampling/statistical error ∆TrSm as in classical Monte Carlo (∝ 1/√Nsamp), while amplitude-estimation error decreases with the number of oracle calls Norac (∝ 1/Norac); total error is the sum of these two contributions.
- [supported] There exists a practical trade-off parameter: choosing Nsamp (hence qubit count via nsamp = log2 Nsamp) and Norac (amplitude estimation oracle calls) allows tuning between memory (qubits) and runtime (depth/oracle calls), which may be necessary given realistic machine constraints.
- [speculative] The PRNG period and statistical quality considerations remain relevant (e.g., Nran Nsamp must be small relative to PRNG period), but widely-used PRNGs (with large period) alleviate practical concerns for typical financial sizes.
- [speculative] Partial parallelization (generating blocks of PRNs in parallel and merging partial results) is a practical compromise when full parallel memory is unavailable: this reduces required qubits by factor n at the expense of increasing circuit depth by ~n.

**Results summary:** The paper proposes a resource-aware variant of quantum Monte Carlo that reuses a single pseudo-random number register on a quantum circuit (implementing a PRNG such as PCG) to sequentially generate random variates and compute the integrand stepwise, thereby reducing qubit requirements relative to prior quantum Monte Carlo designs that allocate one register per random number. The approach still leverages quantum amplitude estimation to obtain a quadratic improvement in estimator convergence relative to classical Monte Carlo, but introduces a trade-off: qubit reduction is achieved at the cost of increased circuit depth proportional to the number of sequential PRN steps. The authors present circuit constructions for PRNG progression and permutation (PCG), detail application to the Merton credit-risk model, analyze complexity and error contributions (statistical sampling vs amplitude-estimation error), and validate the concept with a small Qiskit simulation for a two-variable integral, recovering the sample-average estimate accurately.

**Performance claims:**
- Simulation (Qiskit) of a 2-variable trigonometric integral: exact integral = 0.074578; exact average of integrand values on chosen sample points = 0.078394; quantum-circuit-based estimate = 0.078391.
- Asymptotic error behaviors stated: classical Monte Carlo error ∝ N^{-1/2}; quantum amplitude-estimation error ∝ N^{-1}.
- Resource scaling for implementing PCG on quantum hardware: modular multiplication dominates (ancilla qubits O(n), circuit depth O(n^2) for n-bit arithmetic).
- Sampling/statistical error term ∆TrSm ≤ c σ_f N_samp^{-1/2} (classical Monte Carlo scaling) and amplitude-estimation error ∆Est ∼ 2π d sqrt(Esamp(1-Esamp)) Norac^{-1} (leading term), so total error ≈ statistical term + amplitude-estimation term.
## Quantum advantage claim
**Classification:** theoretical

The paper claims the method preserves the known quadratic error-scaling advantage of quantum amplitude estimation (error ∝ 1/Norac) compared to classical Monte Carlo (∝ 1/√Nsamp), but this is presented as a theoretical result based on combining PRNG-based sampling with amplitude estimation; the paper provides a small simulator proof-of-concept for circuit correctness, not a large-scale empirical demonstration of practical quantum advantage.
## Limitations
- Trade-off between qubit number and circuit depth: reducing qubits by sequentially generating PRNs increases circuit depth proportionally to the number of required random numbers; full qubit reduction may be impractical for deep circuits (author-stated).
- Method assumes the integrand can be computed sequentially in Nran steps using one random number per step; not all target integrands satisfy this form (author-stated).
- The approach relies on converting uniform PRNs into desired distributions (e.g., normal) on-circuit; the paper assumes such conversion gates (Box–Muller, trig, log, etc.) are available/efficient (author-stated).
- Requires construction of two PRNG-related quantum gates (PPRN and JPRN) for the chosen PRNG; implementing JPRN may require modular exponentiation/multiplication/division circuits (author-stated).
- PRNG arithmetic (especially modular multiplication) dominates resource costs: typical implementations need O(n) ancilla qubits and O(n^2) depth for n-bit operands (author-stated).
- Statistical concerns when using subsequences of PRNGs in high dimensions (homogeneity of tuples of consecutive PRNs) — may affect estimator quality; mitigation argued but not fully resolved (author-stated).
- Dependence on PRNG period: Nran * Nsamp must be smaller than the PRNG period to avoid repetition; although typical PRNGs may suffice, this is a constraint (author-stated).
- Deep circuits required by the sequential method are not feasible on near-term noisy hardware without quantum error correction; even with error correction, long runtime of fault-tolerant gates can be problematic (author-stated).
- Small-scale demonstration limitations: the simulator experiment used a tiny LCG (5-bit) and only 8 samples, so statistical validity and scalability to realistic financial problems are not demonstrated (author-stated).
- LCG (and simple PRNGs) have known statistical flaws that must be addressed by permutation (PCG) at added implementation cost; permutation overheads (g and g^{-1}) are nonzero (author-stated).
- [inferred] Practical near-term applicability is limited: current quantum hardware qubit counts and coherence times make the proposed deep, sequential circuits unlikely to run at scale in the near term.
- [inferred] Implementing efficient, high-precision conversion routines (e.g., Box–Muller, inverse CDF, trig, log) in-place and with low depth/qubit overhead may be costly and could negate some resource gains.
- [inferred] The error bounds and resource estimates assume idealized amplitude estimation; the impact of noise, gate errors, and decoherence on amplitude estimation and overall error is not analyzed.
- [inferred] JPRN's jump-ahead operations (exponentiation / ak computations) may become a computational bottleneck when large jumps or many jump-targets are needed, increasing depth substantially.
- [inferred] Optimal choice of nsamp (number of samples / qubit budget split) given specific hardware constraints is nontrivial and not solved in the paper.
- [inferred] The choice of PRNG parameters (LCG/PCG seed, modulus, multiplier, permutation) that are both statistically sound and resource-efficient on a quantum circuit is not fully characterized.
## Open questions
- What is the practical frontier (machine specs, qubit count, coherence time) at which the proposed sequential-PRN method becomes advantageous over fully parallel quantum Monte Carlo or classical Monte Carlo?
- How to optimally balance the qubit-depth trade-off (choose Nsamp / nsamp) for a given target error ϵ and real hardware constraints (available qubits, maximum feasible circuit depth, and noise profile)?
- How to design and implement efficient, low-depth quantum circuits for converting uniform PRNs into target non-uniform distributions (e.g., Box–Muller, inverse CDF) suitable for financial applications?
- How do realistic noise models and gate errors affect amplitude estimation accuracy in the sequential-PRN approach, and what error mitigation or fault-tolerant overheads are required?
- What are the resource (qubit, depth, time) estimates for end-to-end, large-scale financial tasks (e.g., credit portfolios with O(10^6) obligors) using this method, including necessary error correction overheads?
- How do PRNG statistical properties (period, correlation structure, high-dimensional homogeneity) of quantum-implemented PRNGs affect Monte Carlo estimator bias and variance in high-dimensional financial problems (VaR/CVaR)?
- Which PRNG families (beyond PCG) are best-suited for quantum implementation, balancing statistical quality, period, and implementability (in-place update, easy jump-ahead) on quantum hardware?
- How to efficiently implement JPRN (jump-ahead to xiNran+1) for large i and large Nran without prohibitive cost on depth and qubits?
- Can partial-parallel strategies (generate and process blocks of PRNs in parallel then merge results) be systematically optimized, and how do they perform compared to fully parallel and fully sequential schemes?
- How to implement the required arithmetic primitives (in-place modular multiplication, addition, exponentiation, transcendental functions) with minimized ancilla and depth tailored to this application?
- What are the impacts on financial risk measures (VaR, CVaR) when using PRN-based quantum Monte Carlo vs. exact quantum expectation estimation, in terms of regulatory or practical acceptability?
- To what extent can the sequential-PRN approach be adapted for other Monte Carlo-dependent finance applications, such as derivative pricing for non-Markovian or path-dependent payoffs?

**Future work:**
- Study and quantify the memory (qubit) versus speed (circuit depth/runtime) trade-off and develop guidelines for choosing nsamp/Nsamp given specific machine specifications.
- Optimize PCG (or other PRNG) implementations on quantum circuits: minimize ancilla usage, reduce modular-multiplication depth, and tune permutation schemes for statistical quality versus cost.
- Develop and benchmark efficient quantum circuits for conversion from uniform PRNs to target distributions (e.g., Box–Muller, inverse CDF) with resource analyses.
- Produce detailed resource and runtime estimates (including fault-tolerant/error-correction overhead) for large-scale financial Monte Carlo tasks, such as credit risk with O(10^6) obligors.
- Investigate partial-parallel computation strategies (divide work into blocks of size n) to maximize feasible parallelism under limited qubit budgets and characterize their performance.
- Assess the statistical impact of PRNG subsequence usage at scale (homogeneity in high dimensions) and, if needed, design quantum-friendly PRNGs with provable high-dimensional properties.
- Demonstrate larger-scale proofs-of-concept on real quantum hardware (or high-fidelity simulators) using more realistic PRNG settings (e.g., 32-bit outputs, 64-bit states) and more samples.
- Analyze robustness of amplitude-estimation procedures under realistic noisy conditions and develop error mitigation techniques appropriate for the sequential-PRN workflow.
- Investigate algorithmic improvements to make JPRN (jump-ahead) and modular exponentiation cheaper (depth/qubit) for wide-range index selection.
- Extend the approach to other Monte Carlo problems in finance (e.g., derivative pricing with Markov or path-dependent dynamics) and characterize applicability limits.
## Key ideas
- #idea:quantum-advantage — Demonstrates that amplitude estimation can be combined with a quantum-implemented pseudo-random number generator (PCG/LCG) to retain the theoretical quadratic Monte Carlo speedup while drastically reducing qubit count compared to per-random-variable register approaches.
- #idea:hybrid-approach — Uses a quantum circuit for PRN generation and integrand evaluation together with classical maximum-likelihood postprocessing for amplitude/phase estimation (likelihood-based AE), i.e., a quantum-classical hybrid workflow.
- #idea:near-term-feasibility — Proposes a practical qubit-saving design (sequential PRN register with PPRN/JPRN operations) intended to make quantum Monte Carlo more feasible on limited-qubit devices, trading qubits for circuit depth.
- #limitation:simulation-only — All experiments are performed on a Qiskit simulator (no real-QPU runs); the demonstration uses a tiny 5-bit LCG and Nsamp=8, so results are proof-of-concept only.
- #limitation:no-empirical-validation — No hardware experiments or noise analyses are provided; claims about scaling and retained quadratic speedup are not validated on noisy devices.
- #limitation:qubit-count — The method addresses qubit-count bottlenecks by sequential PRN generation but does not eliminate potentially large qubit needs for realistic problems (ancilla, arithmetic, integrand registers remain substantial).
- #limitation:noise — The approach increases circuit depth (many modular-arithmetic and permutation gates), making it sensitive to noise and error accumulation on NISQ devices.
- #limitation:data-encoding — Encoding integrand values into ancilla amplitudes via controlled rotations and performing modular arithmetic for PRNGs adds nontrivial encoding and gate-complexity overheads that may offset qubit savings in practice.
- #idea:quantum-advantage — Provides concrete quantum-circuit constructions (modular adders/multipliers, controlled-SWAP/xorshift) and a worked toy example (2-variable integral and conceptual Merton credit-loss mapping) that produce simulator estimates matching the sample-average baseline.
## Contradictions
- #contradiction:scalability — The paper claims that using a sequential quantum PRNG preserves amplitude-estimation quadratic speedup while reducing qubit requirements, but also shows that this comes at the cost of substantially increased circuit depth and arithmetic complexity; this trade-off undercuts optimistic claims that quantum Monte Carlo can be scaled to practical, noisy hardware without prohibitive resource costs.
- #contradiction:scalability — Results are demonstrated only on a tiny simulator instance (5-bit LCG, Nsamp=8). The retained quadratic advantage is asserted but not empirically shown for realistic problem sizes or under realistic noise models, creating a tension between theoretical speedup claims and practical feasibility.
## Notable quotes
<!-- Researcher-added — verbatim quotes with page references -->

## Researcher notes
<!-- Researcher-added — not LLM generated -->
