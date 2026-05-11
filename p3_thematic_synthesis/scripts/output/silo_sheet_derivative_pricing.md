# Silo data sheet — derivative_pricing

- total papers: **144**  (single-silo: ?, multi-silo: ?)
- DT count: 14
- AT count: 6

## Descriptive themes (DT)

### DT-DP-001 · 17 papers
**Quantum amplitude estimation as core pricing and sensitivity estimation engine**

A large majority of derivative pricing papers adopt Quantum Amplitude Estimation (QAE) or its variants (IQAE, MLAE, power-law AE) as the core subroutine for computing expected payoffs, claiming a quadratic improvement from O(1/ε²) to O(1/ε) over classical Monte Carlo. This framework extends naturally to option sensitivities (Greeks such as Delta, Gamma, Vega) via quantum gradient estimation, parameter-shift rules, or finite-difference schemes within QAE, with an additional quadratic advantage in the number of sensitivities computed simultaneously.

### DT-DP-002 · 9 papers
**State preparation and distribution loading as dominant pipeline bottleneck**

Many papers identify the preparation of quantum states encoding probability distributions (e.g., lognormal asset prices) as the most critical bottleneck in quantum pricing pipelines. Generic state preparation scales exponentially with qubit count, and inefficient loading can negate the quadratic QAE speedup entirely, making this the prerequisite that determines practical viability.

### DT-DP-003 · 11 papers
**Approximate distribution loading via generative and tensor-network models**

Multiple papers propose quantum generative adversarial networks (qGANs), quantum circuit Born machines (QCBMs), quantum-walk generators, and tensor-train (TT) or matrix product state (MPS) representations as scalable approaches to approximately loading asset-price distributions into quantum states with polynomial gate cost. These methods avoid exponential generic loading but introduce approximation errors and training costs that propagate through the pricing pipeline.

### DT-DP-004 · 6 papers
**Black-Scholes PDE as quantum Hamiltonian simulation with non-Hermitian embedding**

Multiple papers reformulate the Black-Scholes PDE into a Schrödinger-type equation via log-price change of variables and time reversal, mapping option price dynamics to Hamiltonian evolution. The non-Hermitian nature of the resulting Hamiltonian is a central challenge, requiring unitary dilation, post-selection, or non-unitary time-evolution methods (e.g., QNUTE) to recover the desired option-price dynamics on a quantum computer.

### DT-DP-005 · 6 papers
**Variational quantum algorithms for financial PDE solving**

Several papers propose variational quantum simulation (VQS), variational quantum imaginary-time evolution (VarQITE), or variational quantum circuit (VQC) methods to solve Black-Scholes or Feynman-Kac PDEs on shallow circuits, using McLachlan's variational principle and classical parameter updates. These methods target NISQ compatibility but face ill-conditioned variational matrices, barren plateaus, and noise sensitivity.

### DT-DP-006 · 9 papers
**European vanilla options as ubiquitous quantum pricing benchmark**

European call or put options under the Black-Scholes-Merton model serve as the standard test case for quantum pricing algorithms across the literature, chosen because their analytical solutions allow direct accuracy verification. Papers note that while Europeans are a convenient testbed, real-world path-dependent derivatives are substantially more complex and represent the setting where quantum advantage would matter most.

### DT-DP-007 · 15 papers
**Complex derivative pricing: path-dependent, early-exercise, and signed-payoff extensions**

Papers extend quantum pricing beyond vanilla options to path-dependent derivatives (Asian, barrier, autocallable, TARF), early-exercise products (American, Bermudan), and contracts with negative payoffs (cliquets). Path-dependent products require sequential multi-timestep encoding and complex payoff logic; early-exercise options face a no-go theorem for amplitude-maximum operations; and signed payoffs require modified encoding protocols. These extensions represent where the largest potential quantum impact is expected but where achieving it is structurally hardest.

### DT-DP-008 · 8 papers
**Multi-asset pricing targeting the curse of dimensionality**

Numerous papers target multi-asset derivative pricing (basket, rainbow, portfolio options) where classical grid-based PDE methods suffer O(N^d) computational growth with the number of underlying assets. Quantum approaches claim polynomial or logarithmic dependence on dimension through amplitude encoding and Hamiltonian simulation, though cross-asset correlations, boundary conditions, and qubit growth introduce practical complexity.

### DT-DP-009 · 6 papers
**Beyond-Black-Scholes dynamics: stochastic volatility and jump processes**

Several papers extend quantum pricing beyond constant-volatility Black-Scholes to richer stochastic models including Heston, CIR, local volatility, SABR, and Merton jump-diffusion. These works analyze whether end-to-end quantum speedups can be preserved under more realistic dynamics, finding that complexity bounds are often pessimistic and parameter-sensitive, and that quantum multi-level Monte Carlo with specialized samplers may be needed to maintain the quadratic speedup.

### DT-DP-010 · 6 papers
**Payoff encoding circuit optimization via QSP and parameterized methods**

Several papers focus on reducing quantum resources for implementing derivative payoff functions, proposing QSP-based amplitude loading, conditional parameterized quantum circuits (CPQCs), and intermediate-qutrit arithmetic. These optimizations achieve significant reductions (e.g., 16x fewer T-gates, elimination of T-gates via qutrits, linear vs. O(n log n) gate scaling) and treat the payoff operator as the key bottleneck inside amplitude-estimation pricing pipelines.

### DT-DP-011 · 14 papers
**NISQ hardware noise and fault-tolerant resource gaps block practical advantage**

Current NISQ devices lack the qubit counts, gate fidelities, coherence times, and circuit depths for pricing at practically advantageous scales, with consistent advantage requiring error rates around 10⁻⁶ to 10⁻⁷ versus current 10⁻² to 10⁻³. Fault-tolerant resource estimates report requirements of thousands of logical qubits, tens of millions of T-gates, and MHz logical clock rates — orders of magnitude beyond current capabilities. Together, these findings establish that quantum pricing advantage is contingent on hardware advances far beyond the current generation.

### DT-DP-012 · 7 papers
**Discretization and approximation errors dominate pricing accuracy budgets**

Papers consistently identify discretization of the probability distribution, truncation of the domain, and payoff approximation (sine-squared, piecewise-linear, gearbox-based) as the dominant sources of pricing error at feasible qubit counts, often exceeding QAE estimation error. Estimates suggest 12 or more qubits are needed for 1% pricing accuracy, and error budgets must jointly track discretization, truncation, and function-approximation components.

### DT-DP-013 · 4 papers
**End-to-end market-data-to-quantum-price pipelines using real data**

A small number of papers construct complete pipelines that calibrate to real option quotes, recover risk-neutral distributions, and perform quantum-accelerated pricing rather than working only with synthetic data. These include NIG-copula calibration from equity markets, regime-switching models using NBER business-cycle data, and swaption surface prediction from daily market quotes, reporting favorable comparisons against classical benchmarks.

### DT-DP-014 · 3 papers
**Quantum walk models of option price dynamics**

A subset of papers models asset price evolution using discrete-time quantum walks with Hadamard coins and translation operators, interpreting position basis states as log prices. When calibrated to match classical variance, quantum-walk option prices agree closely with binomial/random-walk prices while additionally producing volatility smiles, time-to-maturity effects, and bimodal distributions through interference — features requiring no extra parameters.

## Analytical themes (AT)

### AT-DP-001 · C2=partially_grounded (medium)
**The conditional speedup paradox: quadratic advantage requires components that negate it**

_Interpretation:_ QAE's quadratic speedup for derivative pricing is mathematically established, yet it presupposes efficient state preparation and sufficiently precise payoff encoding — both of which remain unsolved at practical scales. Generic state preparation costs exponentially and discretization errors dominate at feasible qubit counts, creating a paradox where the oracle-model advantage is real but the oracle itself is the bottleneck. This explains why the field invests heavily in subroutine optimization rather than end-to-end advantage demonstrations: the theoretical speedup is a ceiling that the actual pipeline cannot yet approach.

_grounded_in DT:_ DT-DP-001, DT-DP-002, DT-DP-012

**B2 counter_evidence:**
- `872cedb13e27` (boundary_condition): Demonstrates that a qGAN can approximately load lognormal distributions with sub-0.01 Wasserstein distance and achieve European call pricing errors below 1% with 100x fewer shots, partially resolving the state preparation bottleneck for simple distributions.
- `75a7b04fa681` (boundary_condition): Reports that the TT-cross algorithm achieves high-accuracy distribution encoding with training time scaling logarithmically with discretization points and linear circuit depth in qubits, suggesting tractable exact-style loading for structured distributions.

**C2 flagged_papers:**
- `12a26364b038` (partially_grounded): The memo supports practical accuracy-resource limits and diminishing returns, but it does not clearly claim that state preparation or payoff encoding negates the quadratic advantage end to end.
- `270d264b98f3` (partially_grounded): The memo shows that distribution loading and payoff encoding are necessary pricing inputs, but it does not frame them as the oracle bottleneck that explains the field's broader research behavior.
- `75a7b04fa681` (misaligned_claim): This memo addresses the loading bottleneck, but it reports logarithmic training behavior and linear depth growth, which weakens the theme's blanket claim that the bottleneck remains practically unresolved.
- `a64e9d084306` (unsupported): The memo emphasizes comparable pricing and a runtime reduction, not a failure mode where state preparation or encoding erases the promised speedup.

_C2 reason:_ AT-DP-001 is partially grounded. 3f4c5ad6749d explicitly says "the main practical limitation for derivative pricing is the linear qubit cost and the dependence on efficient distribution loading," bf1f4204b1e6 says "state preparation and function application are the main bottlenecks," and ef99551dab0f notes that "state loading and circuit depth can dominate any theoretical speedup." But a64e9d084306 mainly reports a "comparable option value and more than 60% runtime reduction," and 75a7b04fa681 presents TT-cross as reducing depth growth from exponential to linear, so the stronger paradox and field-level explanation are not fully recovered from the sampled memos.

### AT-DP-002 · C2=partially_grounded (medium)
**State preparation as a proxy war for quantum pricing viability**

_Interpretation:_ The proliferation of competing distribution loading paradigms — qGANs, QCBMs, MPS/tensor-train, quantum walks, variational circuits — signals communal recognition that state preparation, not estimation, determines quantum pricing viability. No single approach dominates: each introduces its own accuracy-depth tradeoff that propagates through the entire pricing pipeline. This diversity is characteristic of a pre-convergence research phase where the community explores a broad design space rather than optimizing a settled architecture. The pattern reveals that quantum derivative pricing is not one problem but two — representation and estimation — with the representation layer upstream absorbing most of the unsolved complexity.

_grounded_in DT:_ DT-DP-002, DT-DP-003

**B2 counter_evidence:**
- `75a7b04fa681` (boundary_condition): The TT-cross algorithm achieves logarithmic training scaling and linear circuit depth without iterative training, suggesting that for structured financial distributions the state preparation problem may already have a near-optimal solution, undermining the framing of an unresolved proxy war.

**C2 flagged_papers:**
- `871c63b61487` (partially_grounded): The memo is about MPS compression of a pricing function and low-error approximation; it supports representation as a major issue but not the broader claim about competing distribution-loading camps.
- `ce2db00aac7a` (partially_grounded): The memo supports a two-step workflow of state preparation plus amplitude estimation, but it does not clearly support the claim that the field lacks a settled architecture or is engaged in a proxy war.

_C2 reason:_ AT-DP-002 captures a real memo pattern: 872cedb13e27 says "qGAN-based approximate loading is positioned as the enabling step," c57f6422ed7b calls approximate loading "the central enabler for quantum option pricing," and eedf4aad8fda warns that pricing speedups "depend on an efficient distribution oracle and may be dominated by loading costs." The overreach is the stronger sociology claim that this diversity proves a field-wide "pre-convergence" phase, because memos such as 871c63b61487 and ce2db00aac7a describe specific architectures and tradeoffs but do not themselves diagnose communal non-convergence.

**C3 crosswalk entries:**
- **confirms** (high) · `eedf4aad8fda` *A Survey on Quantum Computational Finance for Derivatives Pricing*
  > "End-to-end speedups are threatened by state-preparation and payoff-loading costs; naive accounting of only the estimation subroutine overstates advantage"
- **confirms** (high) · `ef99551dab0f` *NExt ApplicationS of Quantum Computing — D5.1: Review of*
  > "Many algorithmic speedups are concentrated in subroutines; overall end-to-end quantum advantage can vanish once loading/preprocessing is accounted for"
- **extends** (high) · `674c681a57d0` *NExt ApplicationS of Quantum Computing – D5.7: Update of*
  > "State preparation (initialization of probability distributions and payoffs) remains a central bottleneck"

### AT-DP-003 · C2=partially_grounded (medium)
**Paradigm fragmentation: three quantum pricing routes compete without convergence**

_Interpretation:_ Three fundamentally different quantum pricing paradigms coexist: QAE-based Monte Carlo (targeting sample complexity), Hamiltonian simulation of PDEs (targeting grid resolution), and variational PDE solvers (targeting NISQ compatibility), plus the more speculative quantum walk models. Each addresses structurally different bottlenecks — the Monte Carlo route faces state preparation costs, the PDE route faces non-Hermitian embedding and dimensionality costs, and variational methods face barren plateaus and scalability barriers. This fragmentation is unusual for a field claiming proximity to practical advantage and suggests that the community has not yet identified which computational pathway will first achieve deployment-relevant performance.

_grounded_in DT:_ DT-DP-001, DT-DP-004, DT-DP-005, DT-DP-014

**B2 counter_evidence:**
- `96baad0b46a9` (boundary_condition): The overwhelming majority of derivative pricing papers in this silo adopt QAE-based Monte Carlo, suggesting the community has already implicitly converged on this paradigm despite the formal existence of alternatives.

**C2 flagged_papers:**
- `4ceae3900931` (partially_grounded): The memo supports VQS as a distinct PDE route, but it does not support the specific barrier language in the theme and presents a more optimistic near-term feasibility framing.
- `4d07c1a00ccf` (partially_grounded): This memo shows a variational PDE solver on shallow circuits, yet its stated limitations are ill-conditioning and ansatz fit rather than the barren-plateau/scalability barrier asserted in the theme.
- `a19de5d705c8` (partially_grounded): The memo supports a quantum-walk alternative, but it is a conceptual pricing model and does not itself evidence field-wide competition over deployment-relevant paradigms.

_C2 reason:_ AT-DP-003 is supported at the level of paradigm diversity: 96baad0b46a9 "Proposes a quantum Monte Carlo pricing pipeline," 0608ad48d5b8 "Maps the pricing PDE into a Black-Scholes Hamiltonian," and 4d07c1a00ccf uses "quantum imaginary-time evolution" as a shallow-circuit PDE alternative; a19de5d705c8 and b94d98f5a637 add quantum-walk models. What is not clearly grounded is the stronger interpretation that these routes compete "without convergence" and that variational methods are blocked specifically by barren plateaus; 4ceae3900931 instead highlights potential "feasibility on small-scale quantum hardware."

### AT-DP-004 · C2=unsupported (high)
**Benchmarking monoculture conceals the complexity cliff between validation and deployment**

_Interpretation:_ The field's overwhelming reliance on European vanilla options as test cases creates a misleading maturity signal, because the transition to real derivative books involves a steep complexity cliff. Path-dependent products require sequential multi-timestep encoding, early-exercise options face no-go theorems, multi-asset pricing reintroduces correlation complexity, and stochastic volatility models multiply circuit depth. The few papers constructing end-to-end market-data pipelines expose how far algorithm demonstrations are from financial deployment workflows. This benchmarking monoculture exists because European options provide clean validation against analytical solutions, but it systematically obscures the gap between proof-of-concept and production readiness.

_grounded_in DT:_ DT-DP-006, DT-DP-007, DT-DP-008, DT-DP-009, DT-DP-013

**B2 counter_evidence:**
- `dcc9f218d7a2` (boundary_condition): Constructs a full market-data-to-quantum-price pipeline calibrating NIG marginals from real French equity option quotes with copula-based joint distributions, demonstrating that deployment-oriented end-to-end research does exist even if rare.
- `49dc03e35036` (boundary_condition): Provides end-to-end resource estimates for realistic structured products (autocallables, TARFs) rather than European options, showing that some groups are already benchmarking against production-relevant instruments.

**C2 flagged_papers:**
- `075a4a34de90` (misaligned_claim): This memo is centered on multi-asset pricing state preparation rather than vanilla-option benchmarking, so it does not support the monoculture claim.
- `14ceb7e36df7` (partially_grounded): The memo supports a complexity cliff for path-dependent products, but it is itself a non-vanilla benchmark and therefore weakens the claim that the field overwhelmingly stays with European vanilla options.
- `1bf880322e6f` (misaligned_claim): The memo focuses on end-to-end speedups for CIR and Heston-style models rather than showing that the literature mostly validates on analytically convenient European vanilla cases.
- `2b4dc3c2ba75` (misaligned_claim): This memo is about high-dimensional basket and stochastic-volatility pricing, so it supports complexity growth but not the claimed benchmarking monoculture.
- `413125f4264b` (unsupported): The memo covers regime-switching pricing and hardware MSE results; it does not discuss European-vanilla validation as the dominant benchmarking practice.
- `96baad0b46a9` (partially_grounded): The memo spans both European and arithmetic Asian options, so it supports a gap between simple and path-dependent products but not an overwhelming vanilla-only benchmarking pattern.

_C2 reason:_ AT-DP-004 is not recoverable from this sampled memo set. Some papers do use vanilla benchmarks — 0b549647c8e5 gives an "End-to-end QAE option-pricing workflow ... for European derivatives" and 3f4c5ad6749d targets a "single-asset European-style option" — but multiple others focus on non-vanilla settings such as 14ceb7e36df7 on "path-dependent option pricing," 1bf880322e6f on CIR/Heston, 2b4dc3c2ba75 on a "Basket-option case study," and 413125f4264b on regime-switching pricing. That mixed evidence can support a complexity cliff, but not the stronger claim of an overwhelming European-vanilla benchmarking monoculture.

### AT-DP-005 · C2=unsupported (high)
**The hardware-theory gap defines a decade-scale timeline for pricing advantage**

_Interpretation:_ Convergent evidence from NISQ experiments and fault-tolerant resource estimates establishes that quantum derivative pricing advantage requires hardware capabilities — thousands of logical qubits, tens of millions of T-gates, MHz logical clock rates, and error rates of 10⁻⁶ to 10⁻⁷ — that lie orders of magnitude beyond current technology. Circuit optimization techniques achieve impressive constant-factor reductions (e.g., 16x fewer T-gates via QSP payoff encoding) but do not bridge this exponential gap. The field's simultaneous investment in NISQ heuristics and fault-tolerant resource analysis reveals a dual-track hedging strategy against uncertainty about the error-correction timeline, rather than a clear path to near-term advantage.

_grounded_in DT:_ DT-DP-011, DT-DP-010, DT-DP-012

**B2 counter_evidence:**
- `4ceae3900931` (boundary_condition): Proposes variational quantum simulation on shallow NISQ circuits for option pricing PDEs, suggesting a potential near-term pathway that partially circumvents fault-tolerant resource requirements, though scalability to financially relevant problem sizes remains undemonstrated.
- `136790c5fbc5` (boundary_condition): Reports that independent catalyst towers can reduce measurement depth and spacetime volume at small to medium code distances, suggesting architectural innovations could accelerate the fault-tolerant timeline beyond simple extrapolation of current error rates.

**C2 flagged_papers:**
- `12a26364b038` (partially_grounded): The memo supports near-term accuracy-resource limits, but it does not provide the fault-tolerant hardware thresholds or timeline asserted by the theme.
- `1b554a506320` (unsupported): This memo is about mapping pricing to amplitude estimation and asymptotic scaling; it does not discuss hardware requirements beyond the generic algorithmic claim.
- `3f4c5ad6749d` (partially_grounded): The memo supports distribution-loading constraints and a near-term hardware-friendly encoding, but not a decade-scale fault-tolerance gap with explicit logical-qubit and clock-rate thresholds.
- `66f43397ba83` (partially_grounded): The memo supports constant-factor circuit optimization, yet it does not establish that such gains still leave the field orders of magnitude away from practical advantage.
- `a64e9d084306` (unsupported): The memo reports a current-runtime comparison and comparable option values rather than fault-tolerant resource estimates or long-horizon hardware constraints.
- `a9fb068595f2` (unsupported): This memo compares QAE pricing to Monte Carlo and Black-Scholes, but it is silent on the specific hardware thresholds and error-correction timeline asserted in the theme.
- `da7ecd113b59` (partially_grounded): The memo supports depth reduction for a complex payoff, but it does not connect that improvement to the broader claim about a dual-track NISQ versus fault-tolerant hedging strategy.

_C2 reason:_ AT-DP-005 exceeds the memo evidence. 49dc03e35036 does support a hardware-gap reading by giving "Resource estimates for the payoff circuits and total algorithms," and 66f43397ba83 shows only a constant-factor improvement by making the pricing circuit "zero T-cost and zero T-depth." But most sampled memos — including 1b554a506320, a64e9d084306, and a9fb068595f2 — discuss pricing accuracy, asymptotic scaling, or modest runtime comparisons, not the specific claims about thousands of logical qubits, MHz clocks, 10^-6 to 10^-7 error rates, or a decade-scale fault-tolerance timeline.

### AT-DP-006 · C2=partially_grounded (medium)
**High-dimensional and complex products as quantum pricing's structurally strongest value proposition**

_Interpretation:_ Multi-asset and path-dependent derivative pricing represents quantum computing's most compelling value proposition because classical PDE methods scale as O(N^d) with dimension while quantum approaches claim polynomial or logarithmic dependence. Unlike the QAE quadratic speedup on simple products — which is a constant-factor improvement in samples — the dimensionality advantage represents a potential complexity-class separation, the type of structural advantage most likely to justify quantum hardware investment. However, this is precisely where quantum implementations face their hardest challenges: no-go theorems for early-exercise products, exponential error growth with exercise dates, correlation-handling costs, and compounding circuit depth for multi-timestep encoding create a paradox where the products with the largest quantum value gap are those where achieving advantage is structurally hardest.

_grounded_in DT:_ DT-DP-008, DT-DP-007

**B2 counter_evidence:**
- `2b4dc3c2ba75` (boundary_condition): Reports that cross-asset correlations and boundary conditions introduce practical complexity that partially restores classical-like scaling in multi-asset quantum pricing, moderating the theoretical dimensionality advantage.
- `0067a26ce270` (opposing_claim): Proves a linear sample lower bound for the amplitude-maximum operation needed for American option pricing, establishing that quantum advantage for some of the most financially valuable complex products faces fundamental theoretical barriers, not merely engineering ones.

**C2 flagged_papers:**
- `173cd12aee6b` (partially_grounded): The memo supports multi-step Asian-option complexity and approximation error, but it does not clearly elevate complex derivatives as the field's strongest overarching value proposition.
- `6684e6c1b57f` (misaligned_claim): This memo offers a constructive quantum-LSM route for American options, so it does not align with the theme's generalized framing that early-exercise products are mainly evidence of structural blockage.
- `da48095bcac8` (partially_grounded): The memo supports complex-derivative pricing and explicit constraints, but it does not clearly support the stronger interpretive language about complexity-class separation and being the field's dominant value proposition.

_C2 reason:_ AT-DP-006 is partly supported. 081132e62980 says the complexity claims matter where pricing suffers from "grid and dimensionality blowup," 2b4dc3c2ba75 provides a "Basket-option case study" and Heston result, and 49dc03e35036 focuses on "realistic structured derivatives" that are harder than plain vanilla options. The memos are weaker on the stronger claims about this being the field's singular strongest value proposition or a clean complexity-class separation, and 6684e6c1b57f actually presents a positive American-option route rather than the generalized barrier framing used in the theme.

## C2 silo summary

- **themes_checked**: 6
- **grounded**: 0
- **partially_grounded**: 4
- **unsupported**: 2
- **overall_note**: The derivative-pricing analytical layer is mixed: the memos consistently support themes about state preparation pressure, paradigm diversity, and the appeal of high-dimensional or path-dependent use cases, but several themes overextend from technical observations to stronger field-level or causal narratives. The weakest themes are the benchmarking-monoculture and decade-scale hardware-timeline claims, which are not recoverable from the sampled memos without broader corpus evidence.