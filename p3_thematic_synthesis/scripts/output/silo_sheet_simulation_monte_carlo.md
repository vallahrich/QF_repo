# Silo data sheet — simulation_monte_carlo

- total papers: **218**  (single-silo: ?, multi-silo: ?)
- DT count: 16
- AT count: 7

## Descriptive themes (DT)

### DT-SMC-001 · 8 papers
**Quantum amplitude estimation as quadratic Monte Carlo speedup**

A large majority of papers present Quantum Amplitude Estimation (QAE) as the core quantum primitive for simulation, reducing Monte Carlo sample complexity from O(1/ε²) to O(1/ε). This quadratic speedup in oracle calls is cited as the principal motivation for quantum methods in expectation-estimation tasks including derivative pricing and risk metrics.

### DT-SMC-002 · 6 papers
**State preparation and distribution loading as dominant bottleneck**

Many papers identify loading classical probability distributions into quantum states as the primary practical bottleneck that can negate theoretical QAE speedups. Generic state preparation scales exponentially in the number of qubits, motivating extensive research into structured alternatives.

### DT-SMC-003 · 6 papers
**Classical Monte Carlo as universal convergence baseline**

Nearly all papers benchmark quantum approaches against classical Monte Carlo's O(1/√M) error scaling, using its standard runtime and sample complexity as the primary comparison point. Both direct empirical comparisons and theoretical complexity analyses adopt classical MC as the reference.

### DT-SMC-004 · 12 papers
**NISQ noise and hardware limitations preclude practical quantum advantage**

Hardware noise on current NISQ devices significantly distorts quantum Monte Carlo outputs, collapsing estimates toward uninformative values and widening confidence intervals far beyond classical baselines. Multiple surveys and implementation papers confirm that no practical quantum advantage over classical MC has been demonstrated on a commercially relevant financial problem, citing noise, state-preparation costs, and error-correction overhead as key barriers.

### DT-SMC-005 · 7 papers
**VaR and CVaR tail-risk estimation as primary risk application**

A substantial subset of papers targets Value-at-Risk and Conditional Value-at-Risk estimation as the main risk-management application of quantum simulation. VaR is formulated via bisection search over threshold probabilities estimated by QAE, while CVaR is computed as the conditional tail expectation, with dedicated circuit constructions for comparator-based marking and payoff encoding.

### DT-SMC-006 · 7 papers
**Path-dependent and multi-asset derivative pricing**

Several papers extend quantum Monte Carlo pricing beyond European options to path-dependent products such as Asian, barrier, autocallable, and basket options. These are positioned as the strongest candidates for quantum advantage because classical MC cost grows with path count and time steps, and multi-step stochastic dynamics can be encoded into quantum registers.

### DT-SMC-007 · 6 papers
**Credit portfolio loss models as quantum MC use case**

Multiple papers apply quantum amplitude estimation to credit risk analysis under Gaussian conditional independence or Merton-style models. The standard pipeline loads systemic risk factors, computes per-obligor defaults, sums losses, and applies QAE for CDF and VaR estimation via bisection, with dedicated operators for uncertainty modeling, loss aggregation, and threshold comparison.

### DT-SMC-008 · 6 papers
**Fault-tolerant resource estimates reveal massive hardware requirements**

Papers providing end-to-end resource counts for quantum derivative pricing report thousands of logical qubits and tens of millions in T-depth. Concrete figures include 8k–11.5k logical qubits, T-depths of 4.5–8.2×10⁷, and clock-rate requirements of 7–10 MHz, all placing practical quantum MC advantage years away from current hardware capabilities.

### DT-SMC-009 · 9 papers
**Alternative payoff encoding via Fourier series and parameterized circuits**

Multiple papers propose replacing costly quantum arithmetic circuits for payoff computation with either truncated Fourier series decompositions or variationally trained parameterized quantum circuits. Fourier methods estimate each harmonic via separate shallow QAE calls exploiting rapid coefficient decay, while PQC-based approaches use classically pretrained circuits converted to controlled unitaries with linear overhead. Both strategies preserve the quadratic advantage with substantially reduced circuit depth.

### DT-SMC-010 · 12 papers
**Structured and learned distribution-loading methods**

Papers develop two complementary approaches to efficient amplitude encoding: tensor-network and MPS-based methods that exploit entanglement structure of smooth financial distributions for linear-depth circuits, and quantum generative adversarial networks that variationally learn approximate distributions with polynomial gate complexity. MPS methods achieve KL divergences as low as 10⁻⁵ for univariate cases, while qGANs produce confidence intervals close to but not necessarily containing exact values.

### DT-SMC-011 · 4 papers
**Pseudo-random number generation for qubit-efficient quantum MC**

A cluster of papers proposes generating pseudo-random numbers sequentially on a single quantum register rather than allocating one register per random variable, reducing qubit requirements from O(N) to constant. Implementations use permuted congruential generators with jump formulas, achieving T-count reductions at the cost of increased circuit depth.

### DT-SMC-012 · 6 papers
**Quantum PDE solvers as alternatives to Monte Carlo sampling**

Several papers formulate option pricing via the Black-Scholes PDE mapped to a Schrödinger-type equation, using Hamiltonian simulation, quantum signal processing, or variational imaginary-time evolution. These PDE-based approaches directly solve the pricing equation rather than sampling payoffs, claiming polynomial advantages over classical finite-difference methods especially in high dimensions.

### DT-SMC-013 · 7 papers
**Quantum frameworks for continuous-time stochastic process simulation**

Papers develop quantum algorithms for simulating stochastic differential equations under models including Black-Scholes, Heston, CIR, and fractional Brownian motion, with end-to-end complexity claims of O(poly(d)·polylog(1/ε)). This line extends to quantum multilevel Monte Carlo, which combines MLMC variance reduction with QAE’s quadratic sample-complexity improvement, requiring higher-order discretization schemes and careful handling of correlated path increments including Lévy areas.

### DT-SMC-014 · 6 papers
**Discretization and approximation errors as accuracy floor**

Multiple papers report that coarse discretization of probability distributions and payoff functions introduces systematic errors that dominate at feasible qubit counts and can exceed QAE estimation error. With only 1–3 qubits per variable, discretization errors reach 14% or more for VaR estimates, establishing a precision floor regardless of quantum speedup quality.

### DT-SMC-015 · 6 papers
**NISQ-compatible QAE variants without phase estimation**

Many papers adopt QAE variants such as iterative QAE (IQAE) and maximum-likelihood QAE (MLAE/MLQAE) that avoid quantum phase estimation to reduce circuit depth and qubit overhead. These variants achieve comparable convergence with shallower circuits suitable for near-term devices, though some lack formal convergence guarantees.

### DT-SMC-016 · 3 papers
**Modified amplitude encoding for negative payoffs**

Standard quantum Monte Carlo encoding fails for contracts with negative payoffs because naive amplitude encoding discards sign information. Papers propose direct-encoding protocols combined with modified Real Quantum Amplitude Estimation that recovers both magnitude and sign, demonstrating correct convergence on negative-price examples including cliquet options.

## Analytical themes (AT)

### AT-SMC-001 · C2=partially_grounded (medium)
**Oracle-complexity advantage collapses under end-to-end cost accounting**

_Interpretation:_ While QAE provides a genuine quadratic reduction in oracle calls, the end-to-end cost of quantum Monte Carlo is dominated by non-oracle overheads—state preparation, quantum arithmetic, and error correction—that can absorb or exceed the theoretical speedup. Papers benchmarking against classical MC consistently compare oracle counts but omit constant factors, physical clock rates, and compilation overhead, producing advantage claims that do not survive translation to wall-clock time. The resource-estimation literature makes this explicit: thousands of logical qubits and tens of millions of T-gates are required even for moderately complex pricing tasks.

_grounded_in DT:_ DT-SMC-001, DT-SMC-002, DT-SMC-003, DT-SMC-008

**B2 counter_evidence:**
- `49aaab8109ac` (boundary_condition): Fourier-series QAE achieves full quadratic advantage with minimal circuit depth per harmonic component, demonstrating that for structured payoff functions the end-to-end overhead can be substantially mitigated by avoiding quantum arithmetic entirely.

**C2 flagged_papers:**
- `1760158c7e1b` (partially_grounded): The memo supports a major loading bottleneck, but it does not state that non-oracle overheads dominate total wall-clock cost or erase the advantage claim.
- `a9fb068595f2` (partially_grounded): The memo shows that Monte Carlo is more stable than QAE under current conditions, but it does not tie that result to state preparation, error correction, or end-to-end resource accounting.
- `5beb1712456c` (misaligned_claim): This memo reports positive empirical results for QAE, including tighter uncertainty intervals than classical Monte Carlo, so it does not support a collapse-of-advantage interpretation.

_C2 reason:_ AT-SMC-001 is partly grounded because several memos explicitly foreground non-oracle overheads: 49dc03e35036 cites "Provides explicit error budgeting for the Monte Carlo-style workflow, including loader, arithmetic, and payoff errors," c46b48afaa7c says "The main Monte Carlo-style advantage is theoretical, but the practical cost is high circuit depth and limited hardware scale," and e366a47d08de notes "large qubit counts and very deep circuits." 075a4a34de90 and 75a7b04fa681 also support a loading bottleneck, but the stronger claim that benchmarked advantages fail after wall-clock translation is not established across the whole sample. 5beb1712456c is misaligned because its memo reports "tighter uncertainty intervals for the quantum estimates than for classical Monte Carlo," while 1760158c7e1b and a9fb068595f2 describe bottlenecks or current instability without directly showing end-to-end collapse.

**C3 crosswalk entries:**
- **confirms** (high) · `eedf4aad8fda` *A Survey on Quantum Computational Finance for Derivatives Pricing*
  > "Claims of a quadratic speed-up from QAMC over classical Monte Carlo lack rigorous evidence when accounting for distribution generation and loading costs"
- **confirms** (high) · `ef99551dab0f` *NExt ApplicationS of Quantum Computing — D5.1: Review of*
  > "state-loading, compilation overheads, and error-correction costs can eliminate the theoretical advantage"

### AT-SMC-002 · C2=grounded (high)
**Distribution loading transforms quantum advantage into a hardware-software co-design problem**

_Interpretation:_ The exponential cost of generic state preparation has spawned a rich ecosystem of structured workarounds—tensor networks, MPS decompositions, qGANs, and pseudo-random generators—each trading exactness for tractability. This reveals that quantum advantage in financial simulation is as much a problem of clever encoding as of raw quantum speedup: the QAE kernel is well understood, but practical viability hinges on matching the mathematical structure of financial distributions to efficient quantum representations. The co-design challenge is that each loading technique imposes constraints on the class of distributions and payoffs it can handle, fragmenting the field into problem-specific pipelines.

_grounded_in DT:_ DT-SMC-002, DT-SMC-010

**B2 counter_evidence:**
- `16d418f1da92` (boundary_condition): Hardware noise degrades QAE outputs to uninformative levels regardless of state-preparation quality, suggesting that solving the loading problem alone is insufficient for practical advantage and that noise mitigation is an equally critical co-design dimension.

_C2 reason:_ AT-SMC-002 is well grounded in memos that repeatedly frame loading as the core design problem. 075a4a34de90 names "Approximation and constructibility constraints on Monte Carlo applicability," 14ceb7e36df7 says the "MPS model is trained classically on simulated Heston paths," 59cca9744140 identifies "a class of functions and distributions that can be prepared efficiently," and c57f6422ed7b states "Approximation error limits the Monte Carlo advantage in practice." 48cd8220e3b2, 50989fdc9ad1, and c945ded90aa0 likewise describe structured loaders with scope conditions, so the interpretation that advantage depends on matching distributions to efficient encodings is directly supported.

**C3 crosswalk entries:**
- **confirms** (high) · `674c681a57d0` *NExt ApplicationS of Quantum Computing – D5.7: Update of*
  > "State preparation (loading distributions and payoffs) remains a central bottleneck; many methods exist (Grover-Rudolph, low-rank/SVD, MPS, tree-based, variational) but none meet all NISQ desiderata"
- **confirms** (high) · `eedf4aad8fda` *A Survey on Quantum Computational Finance for Derivatives Pricing*
  > "Loading probability distributions into quantum states is a major bottleneck for QAMC and can dominate overall runtime"
- **extends** (high) · `ef99551dab0f` *NExt ApplicationS of Quantum Computing — D5.1: Review of*
  > "State-preparation/loading is identified as a major practical bottleneck; QRAM and large-scale coherent data access are not expected soon, negating some QML/QCMC proposals"

### AT-SMC-003 · C2=partially_grounded (medium)
**Computational cost structure of financial risk drives rational quantum target selection**

_Interpretation:_ The concentration of quantum simulation research on VaR/CVaR estimation, credit portfolio models, and path-dependent derivatives reflects a rational cost-benefit calculus: these are computationally expensive classical MC problems where precision requirements are high and regulatory deadlines are tight, maximizing the potential return on quantum speedup. VaR and credit risk share a common QAE pipeline structure (uncertainty model → loss aggregation → threshold comparison), enabling methodological reuse across applications. Path-dependent products add dimensionality that further favors quantum approaches. This convergence is not accidental but reveals the field’s implicit identification of financial problems where the classical MC cost-to-precision ratio is worst.

_grounded_in DT:_ DT-SMC-005, DT-SMC-006, DT-SMC-007

**B2 counter_evidence:**
- `da7ecd113b59` (boundary_condition): Resource estimates for autocallable pricing show 8k+ logical qubits and T-depths exceeding 10⁷, indicating that even the highest-value path-dependent targets require fault-tolerant hardware far from availability, undermining the ‘near-term target’ framing.

**C2 flagged_papers:**
- `270d264b98f3` (partially_grounded): The memo supports a VaR-style threshold-estimation workflow, but it does not discuss why this class of problem was selected by the field or any regulatory rationale.
- `631717352091` (partially_grounded): This memo shows path-simulation and nested-risk mechanics, yet it does not evidence a field-level target-selection logic beyond describing one expensive simulation workflow.
- `c434305b37fb` (partially_grounded): The memo is about Gaussian loading for credit-style sampling, but it does not support the theme's stronger claim about an implicit cost-benefit calculus or deadline-driven selection.

_C2 reason:_ AT-SMC-003 captures a real pattern in the memo set: 16d418f1da92 defines the targets as "expected loss, VaR, and economic capital," 288305d31b7d "Replaces classical Monte Carlo VaR estimation with QAE-based sampling and bisection," 173cd12aee6b reformulates path-dependent pricing as simulated-path probability estimation, and ed111831958f says contribution estimation is more costly than whole-portfolio risk estimation. These memos support concentration on costly VaR/credit/path-dependent problems and on reusable QAE-style pipelines. But the stronger explanation that the field chose these targets because "regulatory deadlines are tight" or via an explicit "rational cost-benefit calculus" is not directly stated in the sampled memos.

**C3 crosswalk entries:**
- **confirms** (high) · `5308fd4d7e17` *A Structured Survey of Quantum Computing for the Financial*
  > "The literature clusters finance use-cases into three methodological areas: optimization, Monte Carlo/simulation, and (less represented) machine learning"
- **extends** (medium) · `1993ad0237f3` *Quantum computing for finance: overview and prospects*
  > "Quantum Amplitude Estimation provides a quadratic sample-complexity improvement for Monte Carlo-based derivative pricing and risk metrics (VaR/CVaR) in theory"

### AT-SMC-004 · C2=partially_grounded (medium)
**NISQ and fault-tolerant paradigms offer irreconcilable advantage pathways**

_Interpretation:_ The literature reveals two fundamentally different strategies for quantum MC advantage that lack a credible interpolation path. NISQ approaches—shallow variational circuits, iterative QAE, maximum-likelihood estimation—sacrifice theoretical guarantees for hardware compatibility but produce results that hardware noise degrades below classical baselines. Fault-tolerant approaches deliver rigorous quadratic speedups but require resources (thousands of logical qubits, tens of millions in T-depth) that are orders of magnitude beyond current devices. The gap between these paradigms is not merely quantitative but structural: NISQ methods optimize for gate count while FT methods optimize for oracle complexity, and the intermediate regime lacks both the depth for exact QAE and the error tolerance for variational heuristics.

_grounded_in DT:_ DT-SMC-004, DT-SMC-008, DT-SMC-015

**B2 counter_evidence:**
- `b28e4aff9e6f` (boundary_condition): Iterative QAE achieves near-quadratic convergence with NISQ-compatible circuit depths, suggesting a partial bridge between the two paradigms for small-to-medium problem instances where circuit depth remains manageable.

**C2 flagged_papers:**
- `bf1f4204b1e6` (partially_grounded): The memo supports noise sensitivity and bottlenecks, but it does not itself show that NISQ and fault-tolerant pathways are structurally irreconcilable.
- `da7ecd113b59` (partially_grounded): This memo is about discretization-aware IQAE benchmarking on simulators; it does not establish that no useful intermediate regime exists between shallow and fully fault-tolerant approaches.
- `dfca7435a13e` (misaligned_claim): The BIQAE memo presents improved iterative-QAE variants and explicit intermediate scheduling choices, which cuts against the theme's claim that there is no credible interpolation path.

_C2 reason:_ AT-SMC-004 is partly grounded because multiple memos describe a stark split between near-term and exact approaches: 5308fd4d7e17 says "Current demonstrations are limited by hardware and problem complexity," 674c681a57d0 concludes that gains are "incremental and noise-limited" with error correction potentially pushing speedups out of reach, a9fb068595f2 reports that "Monte Carlo remains more stable than QAE under current conditions," and e366a47d08de highlights "large qubit counts and very deep circuits." Those points support a divide between noise-limited NISQ methods and resource-heavy exact methods. However, the stronger claim that the two pathways are irreconcilable and that no credible intermediate bridge exists overreaches the memos, especially where bf1f4204b1e6, da7ecd113b59, and dfca7435a13e optimize intermediate QAE variants rather than proving the bridge impossible.

**C3 crosswalk entries:**
- **confirms** (high) · `674c681a57d0` *NExt ApplicationS of Quantum Computing – D5.7: Update of*
  > "Noise and device error rates on current NISQ hardware are the dominant factors preventing realization of theoretical speedups; empirical benchmarks indicate hardware is orders of magnitude away from required thresholds"
- **extends** (medium) · `67f83161d410` *A Survey of Quantum Computing for Finance*
  > "Quantum error correction / fault-tolerant quantum computing remains far from practical; error-correction overhead could negate near-term algorithmic speedups"

### AT-SMC-005 · C2=unsupported (high)
**Classical Monte Carlo’s parallel scalability silently raises the quantum crossover threshold**

_Interpretation:_ The literature’s universal adoption of single-processor classical MC as the baseline obscures a critical competitive reality: classical Monte Carlo is embarrassingly parallel and can be distributed across thousands of CPUs or GPUs with near-linear speedup, a capability quantum computers cannot match due to their fundamentally sequential oracle-call structure. The quadratic quantum speedup must therefore compete not against one classical processor but against massively parallel classical infrastructure, raising the crossover problem size from theoretically modest to practically unreachable levels. This asymmetry in parallelism is rarely acknowledged in quantum advantage analyses, creating a systematic bias toward optimistic crossover estimates.

_grounded_in DT:_ DT-SMC-001, DT-SMC-003, DT-SMC-004

**B2 counter_evidence:**
- `8f553bfb1077` (boundary_condition): Quantum SDE simulation frameworks claim O(poly(d)·polylog(1/ε)) complexity scaling that could outpace even massively parallel classical MC for sufficiently high-dimensional problems where classical cost grows exponentially in dimension.

**C2 flagged_papers:**
- `0b549647c8e5` (unsupported): The memo discusses classical MC as a benchmark and mentions overhead bottlenecks, but it does not mention classical parallel hardware or biased crossover estimates.
- `342ce43a11d1` (unsupported): This memo compares QMC against classical MC scaling, but it does not discuss massively parallel CPUs/GPUs or the literature's omission of such baselines.
- `a64e9d084306` (unsupported): The memo covers a standard path-based MC baseline and quantum discretization constraints, not parallel classical scalability or sequential-oracle asymmetry.
- `c46b48afaa7c` (unsupported): This memo discusses circuit depth, limited hardware scale, and noise, but it does not say that classical parallelism is the hidden reason crossover thresholds rise.
- `ce2db00aac7a` (unsupported): The memo gives runtime/error comparisons at different accuracy targets, yet it is silent on distributed classical infrastructure or single-processor baselines.
- `dcc9f218d7a2` (unsupported): This memo reports a quadratic advantage versus classical MC in simulation, but it does not discuss whether the classical comparator was under-parallelized or otherwise unrealistically weak.
- `ef99551dab0f` (unsupported): The memo emphasizes state loading and resource expense, not classical MC's parallel scalability or an unacknowledged crossover-threshold effect.
- `f792c5e92b0c` (partially_grounded): The memo does imply a sequential quantum burden by saying the model and payoff must run coherently many times in series, but it still does not discuss parallel CPU/GPU baselines or literature-wide optimism bias.

_C2 reason:_ AT-SMC-005 is not recoverable from the sampled memos. Several papers do compare QAE to classical MC—e.g., 0b549647c8e5 says "Classical Monte Carlo baseline is explicitly used as the comparison target" and dcc9f218d7a2 reports a "consistent quadratic advantage"—but the memos are largely silent on distributed CPU/GPU baselines, near-linear classical parallel scaling, or a systematic bias from using single-processor MC. Only f792c5e92b0c even hints at the asymmetry by noting that standard QMC is "circuit-intensive because the market model and payoff must be run coherently many times in series," which is not enough to ground the full interpretation.

### AT-SMC-006 · C2=partially_grounded (medium)
**Methodological proliferation signals exploratory-phase maturity without paradigm convergence**

_Interpretation:_ The diversity of quantum approaches to financial simulation—Fourier payoff encoding, parameterized circuit approximators, pseudo-random generators, PDE solvers, SDE frameworks, multilevel Monte Carlo, sign-corrected amplitude encoding, and NISQ QAE variants—reveals a field in vigorous exploration but without a dominant paradigm. Each method addresses a specific bottleneck (depth, qubit count, sign handling, loading cost) but introduces its own trade-offs and assumptions. Unlike classical MC, which serves as a well-understood universal default, no single quantum approach has emerged as clearly superior across problem types. This fragmentation, while scientifically productive, delays the standardization needed for industrial adoption.

_grounded_in DT:_ DT-SMC-009, DT-SMC-011, DT-SMC-012, DT-SMC-013, DT-SMC-016

**B2 counter_evidence:**
- `5308fd4d7e17` (methodological_critique): Surveys argue that the proliferation of approaches without standardized benchmarks or reproducible comparisons makes it impossible to determine which methods genuinely advance toward practical advantage, suggesting diversification may mask lack of cumulative progress.

**C2 flagged_papers:**
- `0608ad48d5b8` (partially_grounded): The memo is adjacent to Monte Carlo workflows, but it is framed more as a benchmark/sampling interface than direct evidence about field-wide methodological fragmentation.
- `49aaab8109ac` (partially_grounded): This memo supports another distinct method, but it emphasizes retaining full quadratic speedup for one structured class rather than explicitly evidencing lack of paradigm convergence across the field.
- `82475e54c193` (partially_grounded): The memo adds a continuous-time compressed-path variant, yet it does not speak to industrial standardization, adoption delay, or whether one paradigm is emerging as dominant.

_C2 reason:_ AT-SMC-006 is partly grounded because the memos clearly show method diversity: 29cfef5a271e reports a payoff-encoding approach with "about 16x fewer T-gates," 2b4dc3c2ba75 claims polylog scaling for SDE-based Monte Carlo tasks, 4de005c12725 uses CPQCs to cut function-implementation cost, 82475e54c193 compresses continuous-time paths, and 8908fea924fc uses amplitude-level arithmetic plus spin-echo optimization. That evidence supports the theme's claim that the field is exploring many bottleneck-specific routes rather than converging on one standard method. But the further inference that this fragmentation already delays industrial standardization/adoption is not directly stated in the sampled memos.

**C3 crosswalk entries:**
- **confirms** (high) · `674c681a57d0` *NExt ApplicationS of Quantum Computing – D5.7: Update of*
  > "Multiple AE variants (MLAE, IQAE, RQAE, QoPrime, FAE, AdaptQAE, etc.) present different trade-offs between query complexity, circuit depth, and NISQ suitability"
- **extends** (high) · `eedf4aad8fda` *A Survey on Quantum Computational Finance for Derivatives Pricing*
  > "Variants of QAE (iterative, ML, power-law, 'quantum coins') reduce circuit depth and qubit costs compared to original QFT-based QAE"
- **extends** (high) · `ef99551dab0f` *NExt ApplicationS of Quantum Computing — D5.1: Review of*
  > "Variants of amplitude estimation (iterative, maximum-likelihood, power-law/QoPrime, Quantum Coin) reduce some resource demands and aim to make QAE more NISQ-compatible"

### AT-SMC-007 · C2=partially_grounded (medium)
**Finite-register discretization imposes a precision ceiling that redefines advantage thresholds**

_Interpretation:_ At feasible qubit counts, discretization error from encoding continuous distributions and payoffs into finite quantum registers dominates QAE estimation error, creating a precision ceiling that no amount of quantum speedup can breach without adding more qubits. This fundamentally redefines the advantage question: the relevant comparison is not ‘quantum vs. classical at equal precision’ but ‘quantum at achievable precision vs. classical at arbitrary precision.’ Since classical MC can refine precision simply by drawing more samples at negligible per-sample cost, the quantum approach must simultaneously solve the qubit-count problem and the oracle-complexity problem—a compound challenge that is harder than either alone.

_grounded_in DT:_ DT-SMC-014, DT-SMC-001, DT-SMC-004

**B2 counter_evidence:**
- `75a7b04fa681` (boundary_condition): MPS-based state preparation achieves KL divergences as low as 10⁻⁵ for smooth univariate distributions, demonstrating that for well-structured problems the discretization floor can be pushed far below practically relevant error thresholds with modest qubit counts.

**C2 flagged_papers:**
- `1760158c7e1b` (partially_grounded): The memo supports loading and payoff-encoding bottlenecks, but it does not specifically argue that finite-register discretization is the dominant precision ceiling.
- `674c681a57d0` (partially_grounded): This review discusses loading, schedule choice, and noise, yet it does not isolate discretization as the primary error source that redefines advantage thresholds.
- `c46b48afaa7c` (partially_grounded): The memo highlights realistic-size accuracy limits and noise, but it does not make the stronger claim that discretization dominates all other practical error terms.
- `ef99551dab0f` (partially_grounded): The memo points to loading and resource costs as the main obstacle; it does not directly support the theme's stronger precision-ceiling framing.

_C2 reason:_ AT-SMC-007 is partly grounded because several memos directly foreground discretization limits: 0b549647c8e5 states "Discretization error is the dominant accuracy bottleneck in the simulation pipeline," 12a26364b038 says "1–2 uncertainty qubits causes large errors," 413125f4264b describes encoding choices that trade qubit count against circuit complexity, and ce2db00aac7a decomposes total error into discretization and quantum-circuit components. Together these memos support a real precision ceiling imposed by finite registers. But the stronger claim that discretization generally dominates QAE estimation error at feasible sizes, and that classical MC effectively enjoys arbitrary precision at negligible incremental cost, is not stated across the full sample; 1760158c7e1b, 674c681a57d0, c46b48afaa7c, and ef99551dab0f emphasize broader loading, noise, and resource bottlenecks instead.

**C3 crosswalk entries:**
- **extends** (medium) · `674c681a57d0` *NExt ApplicationS of Quantum Computing – D5.7: Update of*
  > "Accounting for all practical error sources (discretization, state-preparation error, AE algorithm error, readout) can negate the ideal quadratic advantage of QAMC in realistic settings"
- **extends** (medium) · `eedf4aad8fda` *A Survey on Quantum Computational Finance for Derivatives Pricing*
  > "Resource requirements (logical qubits, T-gate depth, clock rates) for practically valuable quantum advantage in realistic, path-dependent derivative pricing are extremely high and currently prohibitive"

## C2 silo summary

- **themes_checked**: 7
- **grounded**: 1
- **partially_grounded**: 5
- **unsupported**: 1
- **overall_note**: The SMC analytical layer is mostly grounded at the level of recurring bottlenecks: loading cost, discretization, noise sensitivity, and resource overhead all recur across the memos. The main systematic weakness is over-interpretation at the analytical layer, where several themes add stronger field-level explanations—wall-clock collapse, rational target selection, irreconcilable paradigms, industrial-adoption delay, or hidden classical-parallelism bias—that the sampled memos only partly support or do not support at all.