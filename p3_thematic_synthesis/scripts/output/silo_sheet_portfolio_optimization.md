# Silo data sheet — portfolio_optimization

- total papers: **251**  (single-silo: ?, multi-silo: ?)
- DT count: 13
- AT count: 6

## Descriptive themes (DT)

### DT-PO-001 · 13 papers
**QUBO/Ising encoding of Markowitz mean-variance is the dominant portfolio formulation**

The vast majority of quantum portfolio optimization studies adopt the Markowitz mean-variance framework as their starting point, encoding expected returns, covariance-based risk, and a risk-aversion tradeoff parameter into a QUBO matrix with budget-constraint penalty terms. This QUBO is then mapped to an Ising Hamiltonian via standard binary-to-spin substitution, creating a universal interface between the financial objective and quantum hardware across both gate-based and annealing paradigms.

### DT-PO-002 · 9 papers
**QAOA is the most widely adopted gate-based algorithm for portfolio optimization**

Across the corpus, the Quantum Approximate Optimization Algorithm (QAOA) is the most frequently employed gate-based variational method for portfolio optimization. Studies apply standard QAOA, constrained-mixer variants (QAOAz), and depth-variant QAOA to portfolio QUBO instances, with classical optimizers tuning variational parameters in alternating cost-mixer circuits.

### DT-PO-003 · 7 papers
**Hybrid quantum-classical optimization loop is the standard portfolio workflow**

Nearly all implemented quantum portfolio studies employ a hybrid quantum-classical loop where quantum circuits evaluate candidate portfolios and a classical optimizer iteratively updates circuit parameters. Classical preprocessing handles data ingestion and covariance estimation while postprocessing verifies constraint satisfaction, making the quantum device one component within a classically orchestrated pipeline.

### DT-PO-004 · 8 papers
**D-Wave quantum annealing handles portfolio QUBOs at larger problem scales**

D-Wave quantum annealers and hybrid solvers are frequently used for portfolio optimization QUBOs, handling larger problem sizes than gate-based approaches by leveraging native QUBO/Ising support. Studies report optimizing portfolios with up to several hundred assets via hybrid decomposition, though solution quality varies and embedding overhead limits direct QPU capacity to approximately 25-170 assets.

### DT-PO-005 · 16 papers
**Algorithmic enhancements--CVaR objectives, warm-starting, and parameter transfer--improve variational performance**

Multiple lines of work improve variational portfolio optimization through complementary strategies: replacing standard energy expectation with CVaR-based objectives that focus on the best-sampled outcomes, initializing QAOA with states derived from classical relaxation solutions to boost low-depth approximation ratios, and applying parameter transfer and scheduling techniques that learn optimal parameters on small instances and reuse them at scale. These refinements collectively reduce the classical optimization overhead and improve solution quality within NISQ constraints.

### DT-PO-006 · 14 papers
**Constraint handling in QUBO formulations: penalty tuning challenges drive constraint-preserving mixer designs**

Studies repeatedly identify the difficulty of setting penalty coefficients that enforce budget and cardinality constraints in QUBO formulations--too-small penalties fail to ensure feasibility while too-large penalties distort the optimization landscape. This persistent challenge has driven a growing line of work replacing soft penalty terms with hard-constraint mixers (XY-type operators, Dicke-state ansatze, fermionic QAOA drivers, Hamming Weight Operators) that confine quantum evolution to the feasible subspace, avoiding penalty tuning entirely.

### DT-PO-007 · 11 papers
**Quantum portfolio experiments are confined to small scales while resource estimates reveal prohibitive costs for realistic sizes**

Quantum portfolio experiments are consistently limited to 3-20 assets because of qubit count, circuit depth, and noise constraints on current devices, with multiple papers acknowledging that tested instances are classically trivial. End-to-end resource analyses of quantum portfolio algorithms--including quantum interior-point methods and amplitude estimation--report qubit counts in the millions and gate depths far beyond current and near-term hardware, underscoring a vast gap between theoretical speedups and practical deployment.

### DT-PO-008 · 6 papers
**Hardware noise substantially degrades quantum portfolio optimizer performance**

Multiple empirical studies report that gate noise, decoherence, and measurement errors on NISQ devices substantially degrade the quality of portfolio solutions found by QAOA and VQE. Under noise, XY mixers lose their constraint-preserving advantage, QAOA convergence becomes unstable, and output distributions approach random guessing on small-gap instances.

### DT-PO-009 · 7 papers
**Classical solvers match or outperform quantum methods on all tested portfolio instances**

Benchmarking studies consistently find that state-of-the-art classical solvers (Gurobi, CPLEX, simulated annealing, problem-specific heuristics) match or outperform quantum and quantum-inspired methods on the portfolio instances that current hardware can handle. No practical quantum advantage for portfolio optimization has been demonstrated at any tested scale.

### DT-PO-010 · 12 papers
**Extended formulations incorporate transaction costs, multi-period dynamics, and multi-objective criteria**

Several studies extend static single-period portfolio models to incorporate transaction costs, rebalancing schedules, market impact, multi-period dynamics, and multi-objective criteria (return, risk, diversification entropy, ESG/solvency) within quantum-amenable QUBO or Hamiltonian representations. Scalarization with varying weight parameters generates Pareto frontiers from quantum annealing or QAOA runs, bridging the gap between academic toy models and realistic portfolio management.

### DT-PO-011 · 6 papers
**Graph-based and clustering methods reformulate portfolio diversification as combinatorial optimization**

A subset of papers formulates portfolio diversification as a graph optimization problem--Maximum Independent Set, Max-Cut, or signed-graph clustering--on correlation networks derived from asset return data, then solves these formulations on quantum or quantum-inspired hardware to select diversified asset subsets. This reformulation reframes the portfolio problem in terms native to quantum combinatorial solvers.

### DT-PO-012 · 5 papers
**Quantum-inspired metaheuristics solve portfolio selection on classical hardware**

A distinct family of papers applies quantum-inspired optimization algorithms--metaheuristics that simulate superposition, measurement, and entanglement-like concepts on classical hardware--to portfolio selection. These methods use qubit or qutrit probability vectors, quantum-style updates, and local search to explore large combinatorial portfolio spaces without requiring quantum hardware.

### DT-PO-013 · 6 papers
**Real historical market data grounds quantum portfolio benchmarks**

Many quantum portfolio studies instantiate their experiments with real historical market data from major indices (S&P 500, DJIA, NASDAQ, DAX, NSE) and commodity futures rather than purely synthetic instances. This grounds problem encoding in genuine financial data and enables evaluation via standard financial metrics such as Sharpe ratio and tracking error.

## Analytical themes (AT)

### AT-PO-001 · C2=partially_grounded (medium)
**The QUBO formulation funnel imposes a binary bottleneck on quantum portfolio expressiveness**

_Interpretation:_ The near-universal pipeline from Markowitz mean-variance to QUBO to Ising Hamiltonian creates a formulation funnel that serves as the lowest-common-denominator encoding across gate-based and annealing hardware, but at the cost of forcing continuous financial models into binary-variable discretizations. This funnel exists because it is the only representation compatible with both quantum paradigms, yet it sacrifices the rich continuous structure of modern portfolio theory and makes penalty calibration a persistent engineering burden. The constraint-handling literature is best understood as a corrective reaction to pathologies introduced by the QUBO funnel itself.

_grounded_in DT:_ DT-PO-001, DT-PO-006

**B2 counter_evidence:**
- `05a01a257cc7` (boundary_condition): Reformulates portfolio diversification as a graph-based Max-Independent-Set problem on correlation networks, bypassing the standard Markowitz-to-QUBO pipeline and demonstrating that alternative problem encodings can avoid the binary bottleneck.
- `76ee9fd77e4e` (boundary_condition): Multi-objective scalarization with Dirichlet weight sampling extends the formulation well beyond single-objective QUBO, suggesting the funnel is not the only viable quantum encoding strategy for portfolio problems.

**C2 flagged_papers:**
- `0b40a3e55edc` (misaligned_claim): The memo supports binary QUBO/Ising encoding and notes that "continuous portfolio weights require additional post-processing," but it does not show that QUBO is the only viable representation or that constraint work is mainly corrective.
- `b97e7f0690c5` (partially_grounded): This memo shows a discrete "binary selection vector" and QUBO recasting, but it does not discuss cross-paradigm necessity, penalty pathologies, or constraint-handling as a reaction to them.

_C2 reason:_ Papers 081dbc9360d1, 9636cfb13bd3, and f190da5cb928 clearly support a recurring binary QUBO/Ising pipeline: 081dbc9360d1 describes a "QUBO-based formulation" with "constraint penalties," 9636cfb13bd3 says standard penalty QAOA can converge to an infeasible "111" portfolio, and f190da5cb928 replaces penalty handling with a constraint-preserving mixer. 0a1f9315f6a7, 0fb65bb44954, and 3c79c53d5d90 also support the Markowitz-to-QUBO-to-Hamiltonian pattern. But the stronger claims that this is the only cross-paradigm representation and that the whole constraint-handling literature is a corrective reaction are not directly established by every memo: 0b40a3e55edc emphasizes "custom mixer Hamiltonians" and b97e7f0690c5 only reports a simplified "binary selection vector" recast as QUBO.

**C3 crosswalk entries:**
- **confirms** (high) · `1961129130d1` *Exploring the Versatility of QAOA: A Comprehensive Review*
  > "converting constrained problems (e.g., VRPTW) into QUBO often requires penalty terms and handling bilinear equality constraints that increase problem complexity"
- **extends** (medium) · `1993ad0237f3` *Quantum computing for finance: overview and prospects*
  > "Quantum annealing and QAOA map many financial combinatorial problems to QUBO/ground-state formulations and could in principle improve solution quality or runtime"
- **contradicts** (medium) · `7f0f52d2eab9` *A brief review of portfolio optimization techniques*
  > "D-Wave hybrid annealing handled very large (e.g., ~1272 fully-connected) instances and ran comparatively fast"

### AT-PO-002 · C2=partially_grounded (medium)
**Algorithmic refinement compensates for hardware inadequacy but yields diminishing returns**

_Interpretation:_ The rapid proliferation of variational improvements--CVaR objectives, warm-starting from classical relaxations, parameter transfer across problem sizes, and constraint-preserving mixers--represents the community's strategy of extracting marginal performance gains through software innovation when the underlying hardware cannot deliver on theoretical promise. This pattern mirrors the classical computing history of compiler-level optimization substituting for raw hardware gains, but in the quantum case each refinement addresses symptoms (noise, barren plateaus, penalty sensitivity) rather than root causes (insufficient qubit counts and coherence times). The cumulative effect is an increasingly complex classical-quantum software stack whose overhead may itself become the performance bottleneck.

_grounded_in DT:_ DT-PO-002, DT-PO-005, DT-PO-006

**B2 counter_evidence:**
- `3a3ba897009d` (null_result): Shows that even with algorithmic improvements, a classical MIP solver solves all tested portfolio instances optimally in seconds, suggesting that variational refinements cannot close the fundamental performance gap on small instances.

**C2 flagged_papers:**
- `3f8ab7317ca4` (misaligned_claim): The memo centers on extrapolated QAOA parameters and reports slower quantum runtime growth for the portfolio case, which does not clearly support a diminishing-returns or hardware-inadequacy reading.
- `470b798927ef` (misaligned_claim): This paper presents LR-QAOA parameter simplification and a fitted scaling advantage over the chosen baseline, not evidence that refinements merely compensate for inadequate hardware.

_C2 reason:_ Several memos document software-side refinements layered onto weak NISQ hardware: 0fb65bb44954 studies "mixer type, constraint implementation via penalty terms, parameter scaling," 25b9eceec1f2 shows that "XY mixers’ initial superiority degrades" under noise, c70ae91a70de introduces warm-start transfer, e1ab375ffe44 makes CVaR the objective, and e4bb7333aaa5 adds "symmetry-based measurement error mitigation" and fragment reuse. 1caec67a4a64 also supports the refinement pattern by reporting that CVaR-VQE outperforms standard VQE while product-state CVaR can rival entangled NISQ setups. But the memos do not consistently show diminishing returns as the field’s dominant narrative: 3f8ab7317ca4 and 470b798927ef instead report parameter-extrapolation and LR-QAOA scaling advantages over selected classical baselines, so the theme overstates a single symptom-fixing interpretation.

### AT-PO-003 · C2=partially_grounded (medium)
**The scalability paradox: quantum advantage is theoretically plausible only at scales that remain experimentally inaccessible**

_Interpretation:_ Quantum portfolio optimization faces a structural paradox: the regime where quantum speedups could exceed classical solvers requires problem sizes (hundreds to thousands of assets with complex constraints) that demand millions of logical qubits and gate depths far beyond any foreseeable hardware, while all experimental evidence is confined to 3-20 asset instances that classical solvers handle trivially. Hardware noise further degrades quantum performance precisely at the boundary where scaling might begin. This is not merely an engineering gap but reflects a fundamental mismatch between the polynomial or exponential resources quantum algorithms require for portfolio problems and the current state of quantum error correction.

_grounded_in DT:_ DT-PO-007, DT-PO-008, DT-PO-009

**B2 counter_evidence:**
- `73f3adac41d9` (boundary_condition): D-Wave hybrid solvers optimize portfolios with up to several hundred assets, partially bridging the scale gap and demonstrating that hybrid decomposition approaches can push beyond gate-based qubit limits, though without demonstrated advantage over classical solvers.
- `685e76bf45ae` (methodological_critique): Reports quantum-inspired digital annealing competitive on mid-scale instances, suggesting that scale alone may not determine whether quantum-native hardware is the right tool for portfolio optimization.

**C2 flagged_papers:**
- `374d8058ad85` (partially_grounded): This memo is about a quantum CVaR subgradient oracle with simulation-only evaluation; it does not directly support the theme’s claim that useful scales are experimentally inaccessible.
- `78cc9d5068f3` (misaligned_claim): The paper explicitly argues that the quantum method can deliver a "significant polynomial speedup" under favourable conditioning, which cuts against the theme’s general impossibility framing.
- `91d09b729085` (partially_grounded): Although the memo acknowledges hardware limits, it also reports 19–28 qubit backtests where quantum methods can match or slightly outperform classical ones, so it is not clean evidence for the full paradox claim.

_C2 reason:_ The paradox is strongly supported by 6ac0d0a3c55a, which estimates "about 8×10^6 logical qubits" and roughly "7×10^29 T gates" for n=100, by 1858371f4c44, whose demonstration uses "only 5 assets (5 qubits), making the instance classically trivial," and by 3a3ba897009d, where noisy QAOA degrades on 2–5 qubit cases and real-device execution was impractical. 69b8b36d8aad and 9170a0c2d3a2 also support near-term scale limits through 15-asset and small-hardware studies with explicit hardware constraints. But the memo set does not uniformly imply a fundamental dead end: 78cc9d5068f3 argues a quantum IPM "can constitute a significant polynomial speedup," 374d8058ad85 focuses on query-efficient CVaR optimization rather than inaccessible scale, and 91d09b729085 reports competitive 19–28 qubit backtests rather than a pure scalability collapse.

### AT-PO-004 · C2=partially_grounded (medium)
**The hybrid architecture positions quantum hardware as an interchangeable stochastic oracle**

_Interpretation:_ The ubiquitous hybrid quantum-classical optimization loop--where quantum circuits serve as approximate function evaluators within classically orchestrated workflows--reveals that quantum hardware in portfolio optimization currently occupies the role of a stochastic sampling subroutine, not an autonomous solver. Classical components handle problem formulation, parameter optimization, and solution verification, while the quantum device provides noisy cost-function evaluations that could in principle be replaced by any approximate oracle. D-Wave's hybrid solver architecture, where QPU time is a small fraction of total runtime with classical overhead dominating, makes this substitutability especially transparent.

_grounded_in DT:_ DT-PO-003, DT-PO-004

**B2 counter_evidence:**
- `6ac0d0a3c55a` (opposing_claim): Proposes a fully quantum interior-point method for portfolio optimization that would operate end-to-end on quantum hardware without classical optimization loops, demonstrating that non-hybrid quantum architectures are theoretically viable, though at resource costs far beyond current capabilities.

**C2 flagged_papers:**
- `0030bd185e0d` (partially_grounded): The memo frames quantum computing as complementing portfolio and risk simulations, but it does not directly show the quantum component acting as an interchangeable oracle inside a classical optimization loop.
- `081dbc9360d1` (unsupported): This paper focuses on a quantum-annealing formulation and benchmark comparisons, not on a hybrid loop where the quantum device is a replaceable sampling subroutine.
- `37f43983f4d2` (unsupported): The memo supports a multiperiod QUBO/annealing formulation, but not the theme’s claim that classical orchestration reduces the quantum component to an oracle role.
- `5c9fef8c2825` (unsupported): This memo describes a D-Wave index-tracking formulation with penalty handling and qubit-saving bounds, not a hybrid architecture with classical dominance over runtime or logic.

_C2 reason:_ A hybrid orchestration pattern is clearly present in 02db829631f9, where "a classical optimizer iteratively updates circuit parameters based on measurement outcomes," in 83317aae0ec0, where D-Wave "samples near-optimal portfolios" before a classical post-selection step, in 41c620c565b5’s decomposition-based QCHA, and in f4883fc328d4, where "the quantum processor evaluates states and the classical processor optimizes parameters." Those memos support the idea that quantum hardware often appears as a subroutine inside a larger classical workflow. However, the stronger claim that the hardware is merely an interchangeable stochastic oracle is not broadly evidenced: 081dbc9360d1 and 5c9fef8c2825 describe direct annealing formulations rather than oracle substitution, 37f43983f4d2 is a QUBO/annealing proof-of-concept without a hybrid evaluation loop, and none of the sampled memos directly support the specific D-Wave runtime-fraction claim.

### AT-PO-005 · C2=unsupported (high)
**Problem-space expansion toward financial realism proceeds without demonstrated quantum payoff**

_Interpretation:_ The extension of quantum portfolio formulations to encompass transaction costs, multi-period rebalancing, multi-objective Pareto frontiers, graph-based diversification, and real market data represents the field's aspiration toward financial practice relevance. However, these extensions consistently fail to demonstrate that quantum approaches handle the added complexity better than classical alternatives. Real market data lends financial credibility to experiments that remain at trivially small scales, while formulation complexity grows faster than quantum hardware capability. The pattern suggests that problem-space expansion is driven by publication differentiation rather than by evidence that quantum methods offer genuine advantages for richer financial models.

_grounded_in DT:_ DT-PO-010, DT-PO-011, DT-PO-013

**B2 counter_evidence:**
- `05a01a257cc7` (boundary_condition): Uses QAOA with circuit cutting on a 71-qubit graph-based diversification problem, pushing beyond typical toy scales and demonstrating that graph reformulations may be more naturally suited to quantum combinatorial algorithms than Markowitz extensions.
- `8e52ff85234f` (boundary_condition): Shows that quantum multi-objective optimization with stochastic Dirichlet sampling generates Pareto fronts competitive with classical multi-objective methods on small instances, indicating potential utility in the multi-objective regime.

**C2 flagged_papers:**
- `0b40a3e55edc` (unsupported): This memo directly claims better multi-objective performance than classical baselines, so it conflicts with the theme’s assertion that richer formulations fail to show quantum payoff.
- `34fc27290f18` (partially_grounded): The memo clearly adds realism through dynamic rebalancing and transaction costs, but it does not establish the theme’s stronger claim that such expansion is mostly publication differentiation without payoff.
- `57ed01f77bc6` (unsupported): This paper reports quantum results comparable to the classical baseline and explicitly claims faster runtime, which cuts against the theme’s no-payoff interpretation.
- `7bdb6593ec48` (unsupported): The memo says the QA-CQM framework achieves the highest hypervolume, lowest IGD, and the largest non-dominated set in the cross-market case, contradicting the theme.
- `8e52ff85234f` (unsupported): This memo explicitly states that the hybrid quantum-classical approach outperforms classical multi-objective algorithms on multiple Pareto metrics, so it does not support the theme.

_C2 reason:_ Some memos support the first half of the theme: 7a47e22ecc89 expands to realistic dynamic rebalancing with "transaction costs and short selling" and explicitly reports that digital methods dominate quantum and quantum-inspired solvers, while 822dbee7acfe’s 71-qubit diversification workflow is "outperformed by a classical evolutionary algorithm baseline." 37f43983f4d2 also shows realism expansion via multiperiod rebalancing and market impact, albeit at proof-of-concept scale. But the full interpretation is not recoverable from the sample because multiple papers directly claim quantum payoff: 0b40a3e55edc reports "3.2% higher hypervolume than NSGA-II," 57ed01f77bc6 says the quantum methods were faster than the Monte Carlo baseline, 7bdb6593ec48 reports the "highest hypervolume" and "lowest IGD," and 8e52ff85234f says the hybrid method attains higher hypervolume and lower GD/IGD than classical baselines.

### AT-PO-006 · C2=partially_grounded (medium)
**Quantum-inspired methods serve as an implicit control group that challenges hardware necessity**

_Interpretation:_ Quantum-inspired metaheuristics--classical algorithms that borrow superposition and entanglement metaphors--achieve competitive portfolio selection performance without any quantum hardware, implicitly functioning as a control group for quantum advantage claims. When combined with the consistent finding that commercial classical solvers dominate quantum and quantum-inspired methods on tested instances, this body of evidence challenges the premise that quantum hardware is necessary for exploiting the combinatorial structure of portfolio optimization. The competitive performance of purely classical approaches that mimic quantum dynamics suggests the computational advantage, if any, lies in the algorithmic structure rather than in quantum physical resources.

_grounded_in DT:_ DT-PO-012, DT-PO-009

**B2 counter_evidence:**
- `41c620c565b5` (opposing_claim): Reports that D-Wave quantum annealing solves portfolio instances at scales and speeds that challenge classical simulated annealing in specific parameter regimes, suggesting quantum hardware may offer advantages inaccessible to quantum-inspired classical methods at sufficient scale.

**C2 flagged_papers:**
- `24ca4814e7f2` (misaligned_claim): This is a broad review arguing that practical quantum advantage is unproven, but it is not evidence that portfolio-specific quantum-inspired methods themselves act as the decisive control group.
- `685e76bf45ae` (misaligned_claim): The memo compares QAOA variants with a classical solver and says classical time-to-solution still scales better, but it is not about quantum-inspired portfolio metaheuristics.
- `91d09b729085` (misaligned_claim): This paper studies hardware-based quantum algorithms and reports that they can match or slightly outperform classical methods in some backtests, which weakens the theme’s stronger necessity claim.
- `c65b93ca030a` (partially_grounded): QJA is clearly quantum-inspired and hardware-free, but it is benchmarked only against other quantum-inspired methods, so it does not directly support the theme’s comparison with standard classical or quantum hardware approaches.

_C2 reason:_ The sample does support the idea that hardware-free, quantum-inspired methods function as an implicit comparator: 2dd59afb46ba is a "fully classical algorithm that simulates quantum superposition," 3fb78ea9b31b reports QBAS outperforming PSO/GA/BAS, and 40e4c7fdd4ac shows a quantum-inspired tensor-network optimizer scaling to 1272 variables while "Gekko ... occasionally exceed[s] the quantum methods." 20c7e1972b0b also uses a quantum-inspired evolutionary search for near-optimal allocations without any quantum hardware. But the stronger inference that classical solvers consistently dominate both quantum and quantum-inspired methods, and therefore that any edge lies purely in algorithmic structure, is not uniformly supported: 91d09b729085 says quantum methods can "match or slightly outperform" classical ones, 685e76bf45ae is about QAOA vs classical scaling rather than quantum-inspired methods, and c65b93ca030a only benchmarks against other quantum-inspired algorithms.

## C2 silo summary

- **themes_checked**: 6
- **grounded**: 0
- **partially_grounded**: 5
- **unsupported**: 1
- **overall_note**: The PO analytical layer captures several real patterns, especially the prevalence of QUBO encodings, hybrid workflows, and NISQ-era refinement strategies, but most themes over-extend beyond what the memos directly say. The main systematic issue is analytic inflation: stronger causal or field-level claims are often built from mixed evidence, and one theme (AT-PO-005) is directly contradicted by several supporting memos that claim quantum payoff.