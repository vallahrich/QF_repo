---
aliases:
- Provable bounds for noise-free expectation values computed from noisy samples
- Provable bounds noise free
authors:
- Samantha V. Barron
- Daniel J. Egger
- Elijah Pelofske
- Andreas Bärtschi
- Stephan Eidenbenz
- Matthis Lehmkuehler
- Stefan Woerner
auto_detected: true
classification: ''
contradiction_flags:
- contradiction:scalability
doi: ''
evaluation_type: real-hardware
evidence_type: ''
has_quantitative_results: true
idea_tags:
- idea:near-term-feasibility
- idea:hybrid-approach
journal_or_venue: arXiv preprint
methodology_tags:
- variational-nisq
- hybrid-quantum-classical
- error-mitigation
paper_type: ''
quantum_advantage_claim: not-applicable
related_papers: []
relevance_phase1: high
relevance_phase3: high
source_type: preprint
source_type_confidence: high
step1_date: '2026-04-14T10:05:05.453444'
step1_model: gpt-5-mini
step2_date: '2026-04-14T10:05:05.453444'
step2_model: gpt-5-mini
step3_date: '2026-04-14T10:05:05.453444'
step3_model: gpt-5-mini
step4_date: '2026-04-14T10:05:05.453444'
step4_model: gpt-5-mini
step5_date: '2026-04-14T10:05:05.453444'
step5_model: gpt-5-mini
step6_date: '2026-04-14T10:05:05.453444'
step6_model: gpt-5-mini
steps_completed:
- 1
- 2
- 3
- 4
- 5
- 6
tags:
- topic/risk-management
- topic/simulation-monte-carlo
- method/variational-nisq
- method/hybrid-quantum-classical
- method/error-mitigation
- idea/near-term-feasibility
- idea/hybrid-approach
- contradiction/scalability
title: Provable bounds for noise-free expectation values computed from noisy samples
topic_tags:
- risk-management
- simulation-monte-carlo
year: '2023'
zotero_key: ''
---

## Abstract summary
This preprint quantifies how noise affects sampling from near-term quantum devices and shows that the multiplicative sampling overhead to recover noise-free samples scales with the circuit's layer fidelity (≈√γ). It proves that Conditional Value at Risk (CVaR) computed on noisy samples yields provable lower/upper bounds on noise-free expectation values, discusses implications for optimization and ML algorithms, and validates the theory with experiments up to 127 qubits.
## Methodology
The authors develop a theoretical framework and empirically validate methods to bound noise-free expectation values from noisy quantum-sampled bit strings. The theory models gate noise with a Pauli-Lindblad (Pauli) noise channel per circuit layer and introduces γ = exp(2 Σk λk) to quantify noise strength; layer fidelity (LF) is related by LFi = 1/√γi. They prove that noisy sampling probabilities are lower-bounded by the noise-free probabilities times the product of layer fidelities and that the Conditional Value-at-Risk (CVaR) computed on noisy samples provides provable lower/upper bounds for noise-free expectation values for α ≤ 1/√γ (Lemma 1). The theory is extended from diagonal Hamiltonians to non-diagonal ones by partitioning into commuting Pauli groups and rotating to diagonal bases. They also formalize filtering/post-selection using indicator functions to tighten CVaR bounds and analyze the statistical variance of CVaR estimators (scaling behavior vs α). Experimentally, they validate the theory by running QAOA circuits on IBM sherbrooke: (a) a 40-qubit MAXCUT instance (p=1,2) where optimal parameters were computed classically using light-cone simplifications and (b) 127-qubit random higher-order Ising problems (p=1..5) with parameters obtained via parameter transfer and verified by MPS simulations. Circuits were transpiled to device topology, staggered dynamical decoupling (staggered XY4) was used for error suppression, layer fidelities were measured, and samples were collected (shots). They computed empirical noisy expectation values, CVaR at levels determined by measured LFs (and calibrated α values), compared to noise-free classical simulations, and used bootstrapping to characterize CVaR estimator variance.

**Algorithms used:** QAOA, VQE (discussed), Probabilistic Error Cancellation (PEC, discussed), Zero Noise Extrapolation (ZNE, discussed), CVaR (loss/estimator), QSVM (discussed), Variational Quantum Time Evolution (VarQTE, discussed), Light-cone classical simulation, Matrix Product State (MPS) simulation
**Frameworks:** IBM Quantum Platform, Qiskit (Qiskit Experiments referenced), CPLEX (for classical optimal solutions), MPS simulator (bond-dimension based simulator, referenced)

**Experimental setup:** Physical runs on ibm_sherbrooke, a 127-qubit superconducting device using echoed cross-resonance (ECR) two-qubit gates (equivalent to CNOT up to single-qubit gates). Experiments included: (1) QAOA for a 40-node 3-regular MAXCUT instance (p=1 and p=2) with circuits transpiled to a linear qubit line and light-cone optimized parameters, and (2) QAOA for 127-qubit higher-order (cubic) Ising spin-glass instances compatible with the heavy-hex hardware graph (p = 1..5) with parameters obtained by parameter transfer and verified by MPS with χ=2048. Staggered dynamical decoupling (staggered XY4) was applied. Layer fidelities were measured (per distinct non-overlapping two-qubit gate layer).
## Experiment details
### Input
Two problem instances: (A) A 3-regular MAXCUT instance on 40 nodes (taken from Ref. [11]) used for p=1 and p=2 QAOA; graphs were transpiled to a line of 40 qubits using swap networks and light-cone simplifications to permit classical evaluation of local expectations. (B) Random hardware-compatible higher-order Ising (spin-glass) problems on a 127-qubit heavy-hex topology with random coefficients {+1,-1} for linear, quadratic, and cubic terms; instances defined to be compatible with heavy-hex so circuits have limited non-overlapping CNOT layers. No external financial datasets were used.

### Process
Pipeline: (1) Problem → encode to diagonal Hamiltonian (QUBO→Z-basis for MAXCUT; higher-order Ising directly specified). (2) Determine QAOA parameters: for 40-qubit instance use classical light-cone optimization to get p=1,2 parameters; for 127-qubit use parameter transfer from smaller instances and verify with MPS (χ=2048). (3) Transpile circuits to device topology and schedule layers into minimal non-overlapping two-qubit layers; insert staggered XY4 dynamical decoupling. (4) Measure layer fidelities (LF) per layer and compute γ and α bounds (α ≤ 1/√γ). (5) Execute circuits on IBM sherbrooke: collect shots (10^5 shots for 40-qubit p=1, 10^7 shots for 40-qubit p=2; for 127-qubit experiments use 10^5 shots per circuit). (6) Post-process measurement results: compute noisy expectation values, compute CVaR at α derived from LF and also calibrated α' fitted to match noise-free expectation values from classical simulations, compute best sampled values, bootstrapping to estimate CVaR variance, and compare to classical noise-free baselines (light-cone or MPS).

### Output
Outputs and metrics: noisy expectation values (tr(eρ H)), estimated noise-free expectation values via classical simulation (tr(ρ H)) used as baselines, CVaR at specified α levels (lower/upper bounds on noise-free expectation), best sampled bitstring objective values, number of CNOT gates, measured layer fidelities, computed γ and √γ sampling overheads, calibrated effective α' and γ' inferred by matching CVaR to classical noise-free values, approximation ratios vs global optimum, and bootstrapped variances of CVaR estimators.

### Parameters
- 40_qubit_MAXCUT: {'qubits': 40, 'depth_p': [1, 2], 'shots': {'p=1': 100000, 'p=2': 10000000}, 'CNOT_count': {'p=1': 461, 'p=2': 922}, 'measured_layer_fidelities': [0.7686, 0.7444], 'derived_FCX': 0.9858, 'derived_gamma_per_CX': 1.029, 'alpha_from_LF': {'p=1': 0.001361, 'p=2': 1.851e-06}, 'optimized_parameters': 'classical light-cone optimization (γ,β values provided in Appendix E)'}
- 127_qubit_higher_order_Ising: {'qubits': 127, 'depth_p': [1, 2, 3, 4, 5], 'shots_per_run': 100000, 'CNOT_count_per_p': {'p=1': 288, 'p=2': 576, 'p=3': 864, 'p=4': 1152, 'p=5': 1440}, 'measured_layer_fidelities': [0.056926, 0.02963, 0.167959], 'derived_FCX': 0.94485, 'EPLG': 0.05515, 'parameter_generation': 'parameter transfer (angles from smaller instances) validated with MPS (bond dimension χ=2048)', 'dynamic_decoupling': 'staggered XY4'}
- misc: {'CVaR_level_rule': 'α ≤ 1/√γ (from measured layer fidelities)', 'CVaR_estimation_notes': 'Monte Carlo sampling; variance scales roughly O(1/α) in the normal/Bernoulli regimes considered; bootstrapping used to estimate variance'}

### Hardware
{'qpu_model': 'ibm_sherbrooke (127-qubit superconducting, heavy-hex topology)', 'two_qubit_gate': 'Echoed cross-resonance (ECR) gate (equivalent to CNOT up to single-qubit gates)', 'cloud_provider': 'IBM Quantum Platform', 'tools_and_simulators': ['Qiskit (Qiskit Experiments referenced for LF measurement)', 'Light-cone classical simulator (for 40-qubit local expectations)', 'MPS simulator (bond dimension χ=2048 for 127-qubit verification)', 'IBM ILOG CPLEX for optimal classical solutions']}

### Reproducibility
The paper references publicly available tools and code patterns (e.g., Qiskit Experiments, a GitHub repo for circuit generation best practices). Problem instances: the 40-node MAXCUT instance is from Ref. [11]; higher-order Ising instances are standard random coefficient constructions compatible with heavy-hex. Parameter-generation techniques (light-cone optimization, parameter transfer) and classical verification (MPS, CPLEX) are described; however, full experiment scripts, exact random seeds for instances, and raw measurement data are not provided inline. Layer-fidelity measurement capability is noted as being implemented in Qiskit Experiments; reproducing hardware runs requires access to ibm_sherbrooke or similar device and the same calibration epoch. Overall: partial reproducibility is possible using the described methods and referenced codebases, but full replication of the exact numerical outputs would require the authors' raw data or access to their precise device-calibration snapshot.
## Findings
- [speculative] The Conditional Value at Risk (CVaR) computed on noisy measurement samples provides provable lower and upper bounds on the noise-free expectation value for diagonal observables (and, via decomposition into commuting subsets and local rotations, for general Hamiltonians).
- [speculative] The sampling overhead required to guarantee that a noisy device produces a given noise-free sampling probability scales multiplicatively as √γ (equivalently as the product of layer fidelities), where γ characterizes the device noise; by contrast, probabilistic error cancellation (PEC) for unbiased expectation-value estimation incurs overhead scaling as γ^2.
- [speculative] For target α = 1/√γ (choice motivated by the sampling-overhead bound), the variance of the CVaR estimator scales like O(√γ) in important distributional cases (Normal, Bernoulli), which is significantly better than the O(γ^2) variance amplification of PEC.
- [speculative] Layer Fidelity (LF) is an efficient, low-cost metric to estimate the sampling overhead for a given circuit; the relationship used is LF_i = 1/√γ_i for layer i, yielding an overall sampling bound via the product of LFs across layers.
- [speculative] Known noise-free worst-case performance guarantees for short-depth QAOA (e.g., MAXCUT on 3-regular graphs for p ≤ 3) can be recovered on noisy hardware provided one accepts the √γ sampling overhead (i.e., the same approximation ratios hold in the noisy setting if you increase sampling accordingly).
- [supported] Experiments on IBM's 'ibm sherbrooke' quantum processor (40-qubit and 127-qubit circuits) show close empirical agreement with the theoretical predictions regarding CVaR bounds and the relation to layer fidelities.
- [supported] For a 40-qubit MAXCUT instance executed on hardware, CVaR computed from noisy samples provided an upper bound that exceeded the classical noise-free expectation by small margins (reported: 3.9% for p = 1 and 7.1% for p = 2 in the paper's experiments).
- [supported] On 127-qubit hardware-compatible higher-order Ising QAOA circuits, the authors observed that noisy expectation values improved up to p = 4 (then degraded at p = 5), and that an empirically fitted effective γ (γ') affecting the observable of interest can be substantially smaller than the device γ derived from layer fidelities—suggesting observable-dependent sensitivity to errors.
- [speculative] Applying PEC and then treating the resulting mixed-state sampling distribution leads to a measurement-probability lower bound px/γ (worse than px/√γ), i.e., PEC amplifies the sampling-overhead if one only cares about sampling probabilities (appendix derivation).
- [supported] Practical circuit-level techniques used in experiments—staggered dynamical decoupling and tailored scheduling into a small number (three) of non-overlapping CNOT layers—allowed realization of low-CNOT-depth QAOA-like circuits (CNOT depth 6p) on the 127-qubit device.
- [supported] The authors observed that Pauli-twirling (randomized Pauli insertions) did not substantially change the empirical output distributions for the tested 127-qubit circuits (appendix comparison).

**Results summary:** This preprint presents a theoretical derivation and experimental validation (on IBM's 40- and 127-qubit devices) of (i) a sampling-overhead relation for noisy quantum circuits: to preserve the noise-free sampling probability of a bitstring x one needs roughly a √γ multiplicative increase in samples (product of per-layer layer-fidelities), and (ii) provable bounds on noise-free expectation values obtained from noisy samples via the Conditional Value at Risk (CVaR) statistic, valid up to α ≤ 1/√γ. The authors prove the CVaR bounds, analyze estimator variance (finding favorable scaling relative to PEC in key cases), connect the bounds to layer-fidelity metrics, and demonstrate the theory experimentally with QAOA-style circuits (40-qubit MAXCUT and 127-qubit higher-order Ising instances). Empirical data show good agreement with the theory, modest gaps between noisy CVaR and noise-free expectations in the 40-qubit case, and observable-dependent effective noise parameters in the 127-qubit experiments.

**Performance claims:**
- 40-qubit MAXCUT (p=1): measured layer fidelities LF1 = 0.7686, LF2 = 0.7444, derived per-CNOT fidelity FCX = 0.9858, overall √γ for circuit ≈ 735.0; CVaR upper bound exceeded noise-free expectation by 3.9%.
- 40-qubit MAXCUT (p=2): same layer fidelities, overall √γ for circuit ≈ 540,276; CVaR upper bound exceeded noise-free expectation by 7.1%.
- 40-qubit MAXCUT: number of CNOTs: 461 (p=1) and 922 (p=2); shots used: 1e5 (p=1) and 1e7 (p=2) respectively (after sorting and keeping α fraction only 137 and 19 samples remained for CVaR in the two cases).
- 127-qubit higher-order Ising QAOA experiments (p=1..5): measured three layer fidelities LF1 = 0.056926, LF2 = 0.029630, LF3 = 0.167959; per-CNOT fidelity FCX = 0.94485 (from geometric averaging), γ_CX = 1.120146; circuits used 288, 576, 864, 1152, 1440 CNOTs for p = 1..5 respectively, each experiment used 1e5 shots.
- 127-qubit experiments: observed effective α' (fitted to match classical noise-free expectation) values much larger than the conservative α = 1/√γ predictions (e.g., α' ≈ 0.4602 for p=1 vs α ≈ 8.03e-8 from LF-based √γ), implying empirical γ' much smaller than γ derived from LFs for these observables.
- Analytic/variance claims: For Normal and Bernoulli distributions, CVaR estimator variance scales O(1/α) (so at α = 1/√γ variance ∼ O(√γ)), significantly better than PEC variance amplification of O(γ^2).
## Quantum advantage claim
**Classification:** not-applicable

The paper does not claim or demonstrate quantum computational advantage over classical methods. Instead it focuses on provable bounds for extracting noise-free expectation values and sampling-quality from noisy quantum devices, and provides theoretical and experimental evidence that CVaR and layer-fidelity-based sampling estimates can deliver meaningful, bounded results on NISQ hardware.
## Limitations
- The analysis assumes a Pauli-Lindblad (Pauli) noise model and uses Pauli twirling arguments; real device noise can deviate from this idealization and the theoretical guarantees may not hold exactly for non-Pauli noise.
- The work assumes a layered circuit structure with primarily two-qubit gate noise and treats single-qubit gates as effectively noise-free; this approximation may not hold for all hardware or gate sets.
- The provable CVaR bounds apply only for α ≤ 1/√γ (or α ≤ 1/C in the general lemma). Choosing larger α (e.g., via empirical calibration) violates the formal guarantees.
- CVaR provides deterministic lower/upper bounds on the noise-free expectation value rather than unbiased estimators; therefore it does not replace unbiased error-mitigation methods such as PEC.
- Variance of CVaR estimators grows as α → 0; in realistic settings (α = 1/√γ) this can mean variance scales like O(√γ) (or worse for heavy-tailed distributions), leading to high sampling cost.
- Although sampling overhead to recover good samples scales as √γ (much better than PEC's γ2 for expectation values), √γ can still be exponentially large in circuit depth/size, making the sampling overhead impractical for some circuits.
- Experimental demonstration on 127 qubits showed required sampling levels (per strict analytic bounds) that are currently impractical, highlighting limits for very large/deep circuits.
- The approach focuses on sampling and diagonal (or decomposed commuting) observables; for general non-diagonal Hamiltonians the bounds are weaker and may not tightly constrain ground-state energies or fidelities.
- State preparation and measurement (SPAM) errors were mostly excluded from the main theoretical development; SPAM can alter sampling statistics and may require additional mitigation or sampling overhead.
- Twirling was not applied in the main experiments; while comparisons suggest small differences in the demonstrated cases, the general impact of (non-)twirled noise on bounds is not fully characterized.
- PEC combined with sampling (dropping the QPD signs) yields a different mixed-state sampling distribution and introduces a poorer sampling lower bound (px/γ rather than px/√γ), highlighting trade-offs between unbiased mitigation and sampling efficiency.
- [inferred] The layer-fidelity-based bounds assume independent/local error structure and that the product of layer fidelities yields a meaningful lower bound on per-bitstring probabilities; correlated or non-local noise could break this relation.
- [inferred] The theoretical bounds rely on being able to decompose non-diagonal Hamiltonians into commuting subsets and perform post-rotations; this decomposition can increase circuit overhead and complexity in practice.
- [inferred] The method's practical usefulness depends on observable-specific effective γ (empirically smaller than global γ in experiments), but that effective reduction is instance- and observable-dependent and not theoretically characterized.
## Open questions
- How robust are the provable CVaR bounds under realistic non-Pauli noise models and correlated errors (i.e., when Pauli-twirled approximations are imperfect)?
- What is the full impact of SPAM (state preparation and measurement) errors on the sampling bounds and on CVaR-based guarantees, and how can these be best mitigated with minimal sampling overhead?
- Can one systematically calibrate α (the CVaR fraction) per application or observable to reduce sampling overhead while retaining useful guarantees, and if so, how to do this safely without invalidating bounds?
- Why do experimentally inferred effective γ values for particular observables sometimes appear much smaller than the γ predicted by layer fidelities, and can this effect be predicted or exploited systematically?
- What are trade-offs in practice between CVaR-based bounded estimates and unbiased, high-variance methods like PEC for different applications (optimization, kernels, time evolution), and how to choose between them?
- How does the variance scaling of the CVaR estimator behave across realistic/noisy quantum output distributions beyond the Normal and Bernoulli examples (especially for heavy-tailed or multimodal outputs)?
- To what extent can problem-specific filters (e.g., particle-number preservation, constraint satisfaction) improve CVaR bounds in practice, and how to design such filters without introducing unacceptable classical overhead or bias?
- What are the precise hardware (layer fidelity, EPLG) thresholds and scaling relationships required for sample-based algorithms (like QAOA at various p) to be competitive with brute-force classical search?
- How does the approach extend to different ansatz families and circuit topologies where layered non-overlapping two-qubit layers are not present or where SWAP networks differ?
- What are the effects of twirling vs not twirling in varied hardware regimes and for different observables—when is twirling beneficial vs when does it introduce prohibitive circuit overhead or alter relevant statistics?
- Can CVaR-based bounds be integrated with other mitigation approaches (e.g., readout calibration, selective PEC on small subcircuits) to get hybrid guarantees with favorable sampling costs?
- [inferred] For non-diagonal Hamiltonians requiring partition into commuting groups, what is the compounded sampling and compilation overhead and its effect on the practical tightness of CVaR-derived bounds?

**Future work:**
- A systematic study of state preparation and measurement (SPAM) errors to determine sampling overheads and mitigation strategies (explicitly mentioned as an interesting direction for future research).
- Investigate adapting the presented methodologies to account for SPAM errors, including combining CVaR bounds with statistical readout error mitigation and evaluating calibration circuit costs.
- Study the effect and validity of the Pauli-twirling assumption in more depth and characterize the gap between twirled and untwirled circuits under realistic noise models.
- Develop empirical calibration procedures for α (the CVaR fraction) for specific applications/observables (e.g., via circuits with known noise-free results) to reduce sampling overhead where possible, while understanding loss of formal guarantees.
- Explore leveraging problem structure (filter functions) systematically to improve CVaR bounds—formulating filters for common domains (optimization constraints, particle-number conservation, etc.).
- Analyze variance scaling and sampling complexity of CVaR estimators across a broader class of output distributions and noisy device behaviors, including heavy-tailed cases.
- Quantify hardware requirements (layer fidelity, EPLG) and scaling for QAOA and related algorithms to outperform brute-force search, deriving practical thresholds for different p and problem sizes.
- Integrate CVaR-based bounds with other algorithms and domains (e.g., quantum chemistry, quantum kernels, variational time evolution) and experimentally benchmark their practical utility.
- Investigate hybrid mitigation strategies combining CVaR bounds with partial PEC or other localized error cancellation techniques to balance bias, variance, and sampling cost.
- Extend experimental studies to larger classes of circuits and topologies (beyond the considered heavy-hex and linear mappings) to validate generality and limitations of the layer-fidelity sampling bounds.
## Key ideas
- #idea:near-term-feasibility — Provides provable bounds showing that recovering noise-free expectation values from noisy samples requires a multiplicative sampling overhead that scales with the circuit's layer-fidelity (roughly as √γ), and validates these bounds experimentally up to 127 qubits on IBM hardware.
- #idea:hybrid-approach — Demonstrates a practical hybrid workflow: classical light-cone optimization and parameter-transfer (from smaller instances) to obtain QAOA parameters, MPS/light-cone classical simulation for verification, and classical postprocessing (CVaR and calibrated α) to produce provable bounds on noise-free expectations from noisy samples.
- #limitation:noise — Empirical layer fidelities are low for larger/deeper circuits (reported LFs produce extremely small α values), leading to very large sampling overheads and high variance in CVaR estimators; noise is the dominant practical limitation.
- #limitation:simulation-only — While the work includes extensive real-hardware experiments, several validations (parameter verification, some baselines) rely on MPS and light-cone classical simulations for large instances, indicating hybrid reliance on classical simulation for verification at scale.
## Contradictions
- Scalability contradiction — The derived bounds imply α ≤ 1/√γ and measured layer fidelities give extremely small α for deeper/more connected circuits, which entails prohibitively large sampling overheads; this undermines optimistic claims that NISQ-era variational algorithms (e.g., QAOA) can straightforwardly scale to practically useful problem sizes without substantial error reduction or new techniques.
## Notable quotes
<!-- Researcher-added — verbatim quotes with page references -->

## Researcher notes
<!-- Researcher-added — not LLM generated -->
