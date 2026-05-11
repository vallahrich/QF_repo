---
aliases:
- An introduction to financial option pricing on a qudit-based quantum computer
- introduction financial option pricing
authors:
- Nicholas Bornman
auto_detected: true
classification: ''
contradiction_flags: []
doi: ''
evaluation_type: simulator
evidence_type: ''
has_quantitative_results: true
idea_tags:
- idea:quantum-advantage
- idea:near-term-feasibility
- idea:hybrid-approach
journal_or_venue: arXiv preprint (arXiv:2311.05537, quant-ph)
methodology_tags:
- amplitude-estimation
- grover-search
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
- topic/derivative-pricing
- topic/simulation-monte-carlo
- method/amplitude-estimation
- method/grover-search
- method/hybrid-quantum-classical
- idea/quantum-advantage
- idea/near-term-feasibility
- idea/hybrid-approach
title: An introduction to financial option pricing on a qudit-based quantum computer
topic_tags:
- derivative-pricing
- simulation-monte-carlo
year: '2023'
zotero_key: ''
---

## Abstract summary
The paper introduces basic financial derivative concepts and provides a detailed account of how to price a European call option on a quantum computer whose information registers are qudits rather than qubits. It develops qudit analogues of the key subroutines—probability loading, comparator and payoff encoding, and amplitude estimation using maximum-likelihood amplitude estimation (avoiding phase estimation)—and numerically simulates the full workflow, showing that modest increases in qudit dimension allow the quantum scheme to approach classical and analytic payoffs within expected error. The work highlights practical resource considerations and potential advantages of qudits (larger Hilbert-space per carrier and error-correction possibilities) for future financial quantum computing applications.
## Methodology
The paper develops and simulates a qudit-based quantum algorithm for pricing a European call option. Methodologically, the authors (1) model the underlying asset price with the Black–Scholes–Merton (BSM) log-normal distribution, truncate the continuous domain to [Smin,Smax] (typically µ±3σ) and discretize it into d^n bins (sampled at bin centers); (2) construct a unitary state-preparation operator P that loads the discretized probabilities {p_i} into an n-qudit register (they propose a Householder-based construction for P); (3) implement a quantum comparator C_k (via digitwise complements and qudit full-adders / ripple-carry adders) to mark basis states with asset price ≥ strike K; (4) encode the (shifted/scaled) payoff function into the amplitude of an ancilla payoff qubit using controlled Y-rotations (with shift s = π/4 and scale factor c ≤ π/4) to produce the overall oracle A = L_f C_k P; (5) form the Grover-type operator Q = -S_Ψ S_Ψ1 and perform amplitude estimation without phase estimation by applying Q^m to A|0⟩ for an exponential sequence m_l (m_0=0, m_l = 2^{l-1}), measuring the payoff qubit N times per m_l; (6) use the collected binomial counts {s_l} to build a joint likelihood across experiments and obtain a maximum-likelihood estimate (MLE) of the Grover angle θ_P1, map it to the amplitude P1 and from that recover the expected payoff (and discounted option price). The full algorithmic stack and subcircuits (state prep, comparator, adder, payoff rotations, Grover reflections) are numerically simulated using a custom Python package; two example parameter sets are presented (BSM parameters and different asset volatilities) and results are compared to the analytic BSM price and a finite-resource classical discretization baseline.

**Algorithms used:** Quantum Amplitude Estimation (QAE) without phase estimation (MLE-based), Grover amplitude amplification (Grover operator Q), Maximum Likelihood Estimation (MLE) for amplitude estimation, Householder-based state preparation, Quantum comparator using digit complements and qudit ripple-carry adder, Controlled Y-rotations for payoff encoding

**Experimental setup:** Numerical simulation via a custom Python package (no external framework specified). Simulated a register of n qudits (examples use n=1) with varying local dimension d (Hilbert space size d^n). Distribution loaded by truncating BSM log-normal to Smin = max(0, µ - 3σ), Smax = µ + 3σ, dividing into d^n equal-width bins and sampling bin centers. Amplitude-estimation without phase estimation used the sequence m_l with m_0=0, m_l = 2^{l-1}, shots per m_l N=100, T=7 (example), yielding total oracle calls M = 26,200. Payoff encoding used controlled Y-rotations with shift s = π/4 and scale c chosen ≤ π/4. Two example parameter sets reported: (S0=2.0, t=1, α=0.07, σ=0.3, K=1.7) and (S0=3.0, σ=0.5, K=2.2).

**Dataset:** Synthetic data: samples drawn from the analytic Black–Scholes–Merton (BSM) log-normal distribution (no real market data). The continuous BSM distribution is truncated to [Smin,Smax] and discretized into d^n bins.
## Experiment details
### Input
{'source': 'Analytic Black–Scholes–Merton model (log-normal)', 'size_and_structure': 'Discretized into d^n points (examples use n=1 and d varied; examples show d=8 and d=10 in figures).', 'preprocessing': 'Truncate domain to Smin = max(0, µ-3σ) and Smax = µ+3σ; partition into d^n equal bins; sample bin centers s_i; compute probabilities p_i = p(s_i)/N and normalize; map integer index i to asset value via affine transform s_i = Smin + (i+1/2)ω with ω=(Smax−Smin)/d^n.'}

### Process
{'pipeline_steps': ['Truncate and discretize BSM distribution; compute normalized probabilities {p_i}.', 'Construct state-preparation unitary P (Householder transform choice) to load √p_i amplitudes into n-qudit register.', 'Compute (d−1)-complement of strike index k, add 1 to get k_c, and use qudit full-adders / ripple-carry adder circuit to add k_c to quantum index i; encode output carry into comparator ancilla qubit via comparator C_k.', 'Apply controlled Y-rotations L_f (controlled by qudit register and comparator) to encode shifted/scaled payoff into payoff ancilla amplitude (parameters s=π/4, c≤π/4).', "Form oracle A = L_f C_k P and Grover operator Q = -S_Ψ S_Ψ1 (reflections built from A and projector on ancilla '1').", "For sequence m_l (m_0=0; m_l=2^{l-1}, l=1..T), apply Q^{m_l} A |0⟩, measure payoff qubit N times per m_l and record number of 'good' outcomes s_l.", 'Multiply binomial likelihoods across l to obtain joint likelihood L(θ|{s_l}); numerically maximize L to get MLE ˆθ; map ˆθ→P1 and convert to expected payoff via the analytic relation (Eq.15); discount to option price.'], 'key_parameters_and_defaults': {'m_l_sequence': 'm_0=0; m_l=2^{l-1}', 'shots_per_setting_N': 100, 'T_cutoff': 7, 'total_oracle_calls_example_M': 26200, 'payoff_shift_s': 'π/4', 'payoff_scale_c': 'chosen ≤ π/4', 'state_preparation_method': 'Householder transform'}, 'notes': 'Amplitude estimation performed without phase estimation using MLE as described by Suzuki et al.; small-angle approximations (sin^2 expansion) used when mapping rotation angles to linear payoff.'}

### Output
{'format': 'Estimated expected payoff values (and plots) as a function of Hilbert-space dimension d^n; comparison plots versus analytic BSM expected payoff and classical finite-resource discretization.', 'metrics_reported': 'Graphical deviation from analytic payoff; qualitative convergence behavior as d and M increase; discussion of sources of error (truncation, payoff-encoding approximation, O(M^{-1}) QAE error).', 'baselines': ['Analytic closed-form Black–Scholes–Merton expected payoff', 'Classical finite-resource discretized estimator (same number of samples/bins)']}

### Parameters
- n_qudits: 1
- d_local_dimension: varied (examples include d=8 and d=10)
- shots_per_m_l_N: 100
- T_max: 7
- m_l_definition: m_0=0; m_l=2^{l-1} for l≥1
- total_oracle_calls_example_M: 26200
- state_preparation: Householder transform (matrix P constructed to have first column = √p vector)
- payoff_encoding: {'shift_s': 'π/4', 'scale_c': '≤ π/4', 'mapping': 'c * ˜f(i) + s with ˜f(i) normalized to [-1,1]'}
- distribution_truncation: Smin = max(0, µ−3σ), Smax = µ+3σ
- BSM_example_params_case1: {'S0': 2.0, 't_years': 1.0, 'alpha_or_r': 0.07, 'sigma': 0.3, 'K': 1.7}
- BSM_example_params_case2: {'S0': 3.0, 'sigma': 0.5, 'K': 2.2}

### Hardware
N/A

### Reproducibility
The authors state that they used a custom Python package to numerically simulate the full algorithmic stack but do not provide a repository or explicit code link in the paper. All mathematical constructions (state-prep, comparator, payoff-encoding, Q operator), parameter choices, and example numerical parameters (BSM parameters, N, T, m_l sequence, truncation rules) are described, so independent reproduction is feasible in principle but would require reimplementation of the described circuits and simulator.
## Findings
- [speculative] The paper presents a qudit-native analogue of the standard qubit-based quantum Monte Carlo / amplitude-estimation approach to price European options, detailing the required subroutines (probability loading, comparator, payoff encoding, amplitude estimation).
- [supported] The author implements numerical simulations of the full qudit-based stack (distribution sampling, circuit subroutines, MLE-based amplitude estimation) for European call options and reports that the qudit-based scheme's estimated payoff approaches that obtained by a similarly-resourced classical finite-register calculation and the analytic payoff within expected error.
- [speculative] The quantum algorithm affords a quadratic asymptotic speedup in sample complexity for amplitude estimation (error scaling O(M^{-1})) compared with classical Monte Carlo (error scaling O(M^{-1/2})), and this carries over to the qudit-based version when using amplitude estimation (or amplitude estimation without phase estimation / MLE variants).
- [speculative] Amplitude estimation without phase estimation (using maximum-likelihood estimation on repeated Grover-operator applications) can preserve the quadratic scaling while forgoing costly phase-estimation / QFT subroutines, making the approach more NISQ-friendly.
- [speculative] Qudit registers provide a logarithmic increase in classical information storage per physical information carrier versus qubits; hence for a fixed number of information carriers a qudit register can represent a finer discretisation of the underlying asset distribution.
- [speculative] Qudits may offer additional potential advantages in some hardware platforms (e.g., possible increased noise robustness, alternative error-correction/mitigation strategies, bosonic encodings like cat codes) but the paper does not present experimental evidence for hardware-level advantages.
- [supported] The paper presents two comparator-circuit design trade-offs for qudits: a design using O(n) ancilla carries with O(n) depth (in single-/double-control gates) and a design using O(1) ancillas but with much larger depth (at least O(n^2) in multi-controlled gates).
- [speculative] Efficient loading of arbitrary distributions into quantum registers remains challenging; while some log-concave distributions (like the log-normal BSM) admit efficient loading, general or market-implied distributions may require classical precomputation or quantum generative techniques (e.g., QGANs) to prepare practical circuits—this is a forward-looking claim.
- [supported] The simulations demonstrate that distribution truncation (discarding tails) and finite discretisation introduce predictable errors; these errors grow for higher-volatility underlying distributions unless register size or truncation window is increased.
- [speculative] For modest increases in qudit dimension the qudit-based scheme can match the accuracy of a finite-resource classical computation of the same register size, suggesting feasibility of small-to-modest qudit registers for simple options (European calls).
- [speculative] The dominant practical bottlenecks for near-term implementations are: (i) state preparation (general unitary compilation / arbitrary state preparation costs), (ii) constructing/compiling the Grover-type operators and reflections into hardware-native gates, and (iii) phase-estimation / QFT subroutines if used; MLE-based approaches mitigate (iii).
- [speculative] The described qudit circuit constructions and decomposition strategies are technology-dependent: e.g., SNAP+displacement style controls for cavity/circuit-QED may offer different compilation/resource tradeoffs compared with linear-ion or photonic qudit gate sets.

**Results summary:** The preprint develops a detailed qudit-based adaptation of the well-known quantum Monte Carlo / amplitude-estimation method for pricing a European call option. It presents explicit circuit-level subroutines (probability loading, qudit comparator, payoff encoding via controlled rotations) and advocates amplitude estimation via maximum-likelihood estimation (avoiding full phase estimation) as a NISQ-friendlier approach. Numerical simulations of the full pipeline (including MLE amplitude estimation) for example Black–Scholes–Merton parameter sets show that the qudit-based estimated payoff converges toward both a similarly-resourced classical finite-register result and the analytic expected payoff within the scheme's theoretical errors. The paper discusses resource trade-offs (ancilla count vs. circuit depth), distribution truncation errors, and practical compilation considerations for different qudit-capable hardware platforms, and argues the expected quadratic asymptotic speedup of quantum amplitude estimation (O(M^{-1})) versus classical Monte Carlo (O(M^{-1/2})), although this remains theoretical in the qudit context.

**Performance claims:**
- Error scaling: classical Monte Carlo O(M^{-1/2}) vs. quantum amplitude estimation O(M^{-1}) (asymptotic claim).
- Simulation experiment parameters reported: N = 100 single-shot measurements per m_ℓ, cutoff T = 7, resulting in total oracle calls M = 26,200 (for the example runs).
- Comparator circuit resource trade-offs: design A uses O(n) ancilla carries and O(n) depth; design B uses O(1) ancillas but at least O(n^2) depth (counting multi-controlled gates).
- Simulation shows that modest increases in qudit Hilbert-space dimension yield payoffs that approach the classical finite-register payoff and analytic payoff within theoretical errors (no single-number error bound provided).
- Distribution truncation heuristic: choose S_min = max(0, μ − 3σ) and S_max = μ + 3σ to capture ≈3σ of probability mass (practical recommendation, not a performance guarantee).
## Quantum advantage claim
**Classification:** theoretical

The paper claims the standard asymptotic quadratic sample-complexity advantage of quantum amplitude estimation (O(M^{-1}) vs. classical O(M^{-1/2})), and argues that this carries to the qudit-based implementation. These claims are theoretical (based on known amplitude-estimation results and cited literature) and supported in the manuscript by numerical simulations of the full algorithm stack for small examples, but there is no experimental demonstration on hardware; practical bottlenecks (state preparation, compilation, phase-estimation costs) are acknowledged and mitigated via MLE-based amplitude estimation in the proposal.
## Limitations
- State preparation (loading arbitrary probability distributions via unitary ˆP) can require exponentially many gates in general; arbitrary unitary compilation is prohibitive for large n (stated).
- Efficient loading is only known for certain classes of distributions (e.g., log-concave / analytically integrable); more general or market-implied distributions may not be efficiently encodable without additional techniques (stated).
- Truncation of the asset-price domain [Smin, Smax] and discretisation discard tail events and introduces modelling error; this is especially problematic for fat-tailed or high-volatility distributions (stated).
- Payoff encoding into ancilla amplitudes is approximate (uses sin^2 mapping and low-order approximation); this introduces constant errors unless higher-order encodings are used at the cost of deeper circuits (stated).
- Phase-estimation and inverse QFT subroutines are bottlenecks for experimental implementations; the paper therefore uses amplitude estimation variants that avoid phase estimation (stated).
- The comparator subroutine ˆCk has trade-offs: one design uses O(n) ancillas with O(n) depth, another uses O(1) ancillas but incurs much greater depth (O(n^2) with multi-control gates); resource choice depends on hardware (stated).
- Decomposition of multi-controlled qudit operations into hardware-native single- and two-body gates (and the cost thereof) is unclear; compilation resources for qudit primitives are not well characterised (stated).
- Practical construction/decomposition of certain logical operators used (e.g., ˆS0 reflection about the ground state) into hardware-native gates is not addressed and may be nontrivial (stated).
- The presented simulations do not model device-level noise, decoherence, or compilation errors; real NISQ hardware will introduce additional errors and resource constraints (stated).
- Quantum advantage for the simple, path-independent European option is limited in practice — classical methods already efficient; expected advantage mostly for path-dependent, higher-dimensional problems (stated).
- [inferred] The logarithmic information-density advantage of qudits may be outweighed by experimental complexity of building and controlling higher-d qudits in the NISQ era.
- [inferred] Use of ansatz-based or ML-based state loaders (e.g., quantum GANs) shifts complexity into training/optimisation; their practicality and resource costs on qudit hardware remain uncertain.
- [inferred] The constant and algorithmic errors (payoff-encoding approximation + QAE error) may require deeper circuits or more shots to reach acceptable financial tolerances, potentially limiting near-term applicability.
- [inferred] The mapping from measurement-derived θ estimates to risk-sensitive, regulator-compliant option prices in production settings (including tail-risk considerations) remains to be validated.
- [inferred] The paper focuses on single-asset examples (n small); scaling behaviour and resource estimates for multi-asset / path-dependent derivatives on qudit hardware are not quantified and may be prohibitive.
## Open questions
- How to efficiently and reliably compile the high-level operators (ˆP, ˆA, ˆQ, ˆS0, etc.) into the native gate sets of various qudit hardware platforms?
- Which qudit-native fundamental gate sets and control paradigms (e.g., SNAP+displacements, multimode cavity controls, photonic multiports, ion-trap gates) yield the best resource and fidelity trade-offs for option-pricing workflows?
- What are the resource requirements (qudit count, dimension d, gate depth, ancilla counts) for realistically-sized, path-dependent derivatives (barrier, Asian, basket options) on qudit hardware?
- How to encode heavy-tailed or market-implied distributions (with significant tail probability) without excessive truncation error or prohibitive resource costs?
- What are the optimal strategies for payoff encoding that balance approximation error and circuit depth (including higher-order encodings)?
- How do qudit-specific noise channels and error mechanisms affect the accuracy of amplitude-estimation-based pricing, and what mitigation/error-correction schemes are best suited to qudits?
- Can generative models (quantum or classical-quantum hybrid) be made practical and resource-efficient to load realistic market distributions into qudit registers?
- How to best choose truncation bounds Smin and Smax and discretisation granularity ω for given risk tolerances and hardware constraints?
- What are the empirical benefits (if any) of qudit-based implementations over qubit-based ones on near-term hardware, beyond the theoretical logarithmic encoding advantage?
- How to decompose and implement multi-controlled qudit operations efficiently (in particular, whether multi-control gates can be compiled into feasible two-body interactions without large overhead)?
- What are practical schemes for constructing ˆS0 (ground-state reflection) and other global reflections used in amplitude amplification on qudit platforms?
- How robust is the maximum-likelihood amplitude-estimation variant (no phase estimation) to realistic noise, and what are optimal choices of m_l, N, T in practice?
- What are the end-to-end error budgets (from truncation, discretisation, state preparation, payoff encoding, QAE, and hardware noise) required to meet financial-industry accuracy demands?
- How feasible is it to implement bosonic encodings (cat codes, bosonic modes) and use their error-correction advantages for financial workloads?
- How to extend, benchmark, and resource-estimate the qudit option-pricing pipeline for multi-asset portfolios and realistic risk-management tasks?

**Future work:**
- Tailor the qudit-based algorithm to more complex and realistic financial derivatives (path-dependent options, barrier options, Asian options, basket options) and study resource scaling.
- Investigate and develop efficient state-preparation methods for general (market-implied) distributions, including hybrid classical-quantum strategies and quantum generative models (quantum GANs) for distribution loading.
- Explore amplitude estimation variants that avoid phase estimation (e.g., maximum-likelihood, iterative QAE) on qudit hardware and study their noise resilience and empirical performance.
- Study the choice of comparator implementations (ancilla-rich shallow vs ancilla-poor deep circuits) for different hardware regimes and quantify trade-offs.
- Develop compilation and optimal-control methods to map logical operators (ˆP, ˆA, ˆQ, ˆS0, etc.) into hardware-native gates for specific qudit platforms (cavity QED, trapped ions, photonics, etc.).
- Analyse bosonic/qudit encodings (e.g., cat codes) and their error-correction/error-mitigation benefits for finance workloads, including how they affect state-preparation and payoff-encoding costs.
- Perform noise-aware simulations and experiments (including realistic decoherence, gate errors, and compilation overhead) to benchmark the end-to-end algorithm on current and near-term hardware.
- Produce detailed resource estimates (qudits, dimension d, gate counts, depth, ancillas) for multi-asset and path-dependent derivative pricing on qudit architectures.
- Examine methods to better capture tail events (alternative truncation strategies, adaptive discretisation, importance-sampling-like quantum methods) to reduce truncation-induced pricing errors.
- Investigate training and deployment of parameterised ansatz circuits for distribution loading on qudit systems, including practical training workflows and convergence guarantees.
## Key ideas
- #idea:quantum-advantage — Qudit-based encoding (increasing local dimension d) increases Hilbert-space per physical carrier and, in simulations, allows the scheme to approach analytic BSM payoffs with modest d, suggesting potential resource advantages over qubit-only encodings.
- #idea:hybrid-approach — The paper uses MLE-based amplitude estimation (QAE without phase estimation) combined with classical post-processing to estimate the Grover angle, avoiding phase-estimation and making the workflow more NISQ-friendly.
- #idea:near-term-feasibility — Numerical demonstrations with n=1 qudit and d up to ~10, using an exponential sequence of Grover iterations (total oracle calls M≈26,200 and N=100 shots per setting), show convergence toward analytic option prices, indicating feasibility of small proof-of-concept experiments.
- #idea:quantum-advantage — The algorithm applies Grover-type amplification and amplitude estimation (theoretically offering improved Monte Carlo scaling), and implements full subroutines (state prep via Householder, qudit comparator, ripple-carry adders, controlled Y-rotations) to realize end-to-end option pricing on qudits.
- #limitation:simulation-only — All results are from noise-free numerical simulation using a custom Python package; no noisy-device simulation or real-QPU experiments were performed.
- #limitation:no-empirical-validation — There is no experimental validation on hardware; effects of realistic gate errors, decoherence, or readout noise are not assessed.
- #limitation:qubit-count — Examples use only a single qudit register (n=1); scalability to multiple qudits (large d^n) and realistic problem sizes is not demonstrated and resource growth is not fully evaluated.
- #limitation:data-encoding — The method requires truncation/discretization of the continuous BSM distribution into d^n bins and a potentially costly Householder state-preparation unitary to load sqrt(p_i) amplitudes, posing encoding overheads that may limit practical use.
- #limitation:noise — While the paper notes error-correction possibilities for qudits, it does not model noise or employ error mitigation, so the impact of noisy implementations of comparators, adders, and payoff rotations remains unknown.
- #idea:quantum-advantage — The paper provides explicit resource accounting for the simulated examples (m_l schedule, shots per setting, total oracle calls) and shows qualitative convergence behavior vs analytic and classical discretized baselines, but does not empirically demonstrate asymptotic quantum speedup at scale.
## Contradictions
<!-- Step 6 output — where this paper contradicts others -->

## Notable quotes
<!-- Researcher-added — verbatim quotes with page references -->

## Researcher notes
<!-- Researcher-added — not LLM generated -->
