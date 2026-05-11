# Silo data sheet — trading_execution

- total papers: **43**  (single-silo: ?, multi-silo: ?)
- DT count: 10
- AT count: 4

## Descriptive themes (DT)

### DT-TE-001 · 7 papers
**Trading problems encoded as QUBO for quantum solvers**

Multiple papers formulate trading and execution problems — including currency arbitrage, crypto arbitrage, portfolio rebalancing schedules, energy market trading, and transaction settlement — as Quadratic Unconstrained Binary Optimization (QUBO) or equivalent Ising Hamiltonians, enabling solution via quantum annealing or QAOA. These formulations incorporate constraint penalties, log-transformed objectives, and slack-variable reformulations to map financial decision variables onto binary quantum representations.

### DT-TE-002 · 9 papers
**Hybrid quantum-classical architectures as dominant design pattern**

The overwhelming majority of empirical and proposed quantum trading systems adopt hybrid quantum-classical designs where quantum circuits handle specific subtasks — feature generation, optimization, or policy learning — while classical components manage data preprocessing, ensemble integration, and output interpretation. Pure quantum models consistently underperform hybrid designs, reinforcing that near-term quantum value lies in augmenting rather than replacing classical pipelines.

### DT-TE-003 · 5 papers
**Quantum-enhanced reinforcement learning for sequential trading decisions**

Several papers embed variational quantum circuits into reinforcement learning frameworks (A3C, DQN, PPO) for trading, replacing or augmenting classical policy and value network components with quantum layers. These systems encode financial state representations into parameterized quantum circuits and are trained via hybrid optimization, evaluated on trading tasks with transaction costs and standard risk-adjusted metrics.

### DT-TE-004 · 7 papers
**Classical baselines match or outperform quantum trading models**

Across multiple empirical comparisons, classical machine learning models and optimization baselines remain competitive with or outperform quantum approaches on trading-relevant metrics. Quantum advantages appear only in narrow regimes or not at all, with classical ensembles, SVMs, and LSTM/Transformer architectures matching hybrid quantum variants on investment returns, prediction accuracy, and optimization quality.

### DT-TE-005 · 14 papers
**NISQ hardware noise and simulation-to-hardware gap degrade quantum trading viability**

Current NISQ-era quantum devices suffer from noise, decoherence, limited qubit counts, and high gate error rates that degrade circuit fidelity and prevent scaling to production-grade financial systems. Papers testing on real quantum hardware report degraded performance, noise-induced variance, longer runtimes, and constraint violations compared to simulator results, revealing a significant gap between simulated and deployed quantum trading systems.

### DT-TE-006 · 8 papers
**Transaction cost-aware evaluation in quantum trading studies**

A growing number of quantum trading papers incorporate explicit transaction costs, bid-ask spreads, or commission rates into their models and evaluation metrics, moving beyond pure prediction accuracy toward economically meaningful assessment. Papers include transaction-cost terms in QUBO objectives, evaluate RL agents with profit-net-of-cost rewards, and warn that directional accuracy alone does not guarantee profitability once costs are included.

### DT-TE-007 · 7 papers
**Ultra-low-latency demands in high-frequency trading strain quantum viability**

Multiple papers note that high-frequency trading requires microsecond-to-millisecond decision latency, and current quantum hardware — with queue delays, circuit execution times, and communication overhead — cannot yet meet these stringent timing requirements. Classical HPC already approaches computational limits at realistic market scales, and quantum systems add rather than reduce execution overhead for time-critical trading.

### DT-TE-008 · 8 papers
**Quantum trading experiments confined to small problem instances**

Across empirical studies, quantum trading experiments are confined to small problem sizes — a handful of currencies, single assets, or short evaluation windows — raising questions about generalizability. Arbitrage experiments cover only 3-10 currencies, rebalancing is tested with limited candidate dates, and RL agents are evaluated on single indices over restricted periods.

### DT-TE-009 · 6 papers
**Quantum data encoding trade-offs constrain financial model design**

Papers report that encoding classical financial data into quantum states is a critical bottleneck. Angle encoding is practical but limited in expressiveness, amplitude encoding is theoretically richer but prohibitively expensive on NISQ hardware, and aggressive dimensionality reduction is required to fit within available qubit budgets. These trade-offs necessitate feature selection techniques that may discard financially meaningful information.

### DT-TE-010 · 6 papers
**Quantum trading model performance varies across market regimes**

Several studies report that quantum or hybrid trading models show regime-dependent performance, with advantages concentrated in specific market states such as high volatility or crisis periods while degrading or underperforming in others. QLSTM strategies outperform only during GFC and pre-COVID periods, hybrid ensemble accuracy peaks in high-volatility regimes, and quantum-enhanced RL shows variable reward-performance gaps across market conditions.

## Analytical themes (AT)

### AT-TE-001 · C2=grounded (high)
**The hybridization imperative: quantum as component, not system**

_Interpretation:_ The convergence on hybrid quantum-classical architectures across trading applications is not merely a pragmatic NISQ-era concession but reveals a structural insight: quantum computing's value in trading lies in enhancing specific computational bottlenecks within classical pipelines rather than replacing end-to-end systems. Quantum circuits consistently serve as pluggable modules for feature generation, policy optimization, or combinatorial subroutines, while classical infrastructure handles data ingestion, risk management, and execution. The persistent competitiveness of classical baselines further indicates that quantum contributions must demonstrably exceed the overhead of integration to justify hybrid complexity.

_grounded_in DT:_ DT-TE-002, DT-TE-003, DT-TE-004

**B2 counter_evidence:**
- `5081ec6b6068` (null_result): Classical Random Forest and Gradient Boosting ensembles match or beat hybrid quantum models on AMM trading returns, demonstrating that hybridization alone does not guarantee advantage over well-tuned classical alternatives.
- `4ee4d5f63858` (null_result): QSVM shows no improvement over classical SVM on stock prediction tasks even within a hybrid pipeline, suggesting the quantum component adds noise rather than value for certain problem types.

**C2 flagged_papers:**
- `48fad011ea47` (partially_grounded): The memo supports execution-oriented policy learning with costs and backtesting, but it does not clearly show the theme's stronger claim that quantum is only a modular component inside a larger classical pipeline.

_C2 reason:_ Six of seven memos support the claim that quantum is used as a module inside broader classical workflows rather than as a full replacement. Paper 5081ec6b6068 says "Hybrid models are the strongest candidates for execution-oriented decision support because they deliver the best return-risk tradeoff," while the same memo adds that "Classical ensembles remain highly competitive," and 9be7c1fe15c2 says "The hybrid pipeline converts market features into a trading signal through quantum processing and a dense output layer." Papers 4ee4d5f63858 and dca63675e36a further anchor the modular reading via upstream feature-selection / signal-generation roles, but 48fad011ea47 focuses on a learned trading agent and costs without clearly showing quantum as only a pluggable subsystem.

**C3 crosswalk entries:**
- **confirms** (high) · `67f83161d410` *A Survey of Quantum Computing for Finance*
  > "Variational hybrid algorithms (VQA/QAOA/VQE) and hybrid QPU-CPU workflows are emphasized as the practical near-term path for optimization and ML tasks in finance"
- **confirms** (high) · `1993ad0237f3` *Quantum computing for finance: overview and prospects*
  > "Practical near-term deployments likely require hybrid quantum-classical workflows (classical pre/post-processing, classical optimizers tuning variational circuits, QUBO embeddings)"
- **extends** (medium) · `f3998e794c14` *A Review on High-Frequency Trading Forecasting Methods: Opportunity*
  > "hybrid quantum-classical models (variational layers within RNNs, quantum-classical GANs) as the primary practical path toward integrating quantum methods in HFT forecasting"

### AT-TE-002 · C2=partially_grounded (medium)
**The formulation-scalability paradox in quantum trading optimization**

_Interpretation:_ The ease with which diverse trading problems — arbitrage detection, rebalancing, settlement — can be cast as QUBO instances creates an illusion of broad quantum applicability. However, a paradox emerges: as problem formulations incorporate realistic constraints such as transaction costs, multi-asset coverage, and market frictions, the required qubit counts and penalty terms grow rapidly, confining successful demonstrations to toy-scale instances. This formulation-scalability tension means that the most practically relevant problems are precisely those least amenable to current quantum solution, because realistic financial constraints inflate QUBO dimensionality beyond hardware capacity.

_grounded_in DT:_ DT-TE-001, DT-TE-006, DT-TE-008

**B2 counter_evidence:**
- `e71143fc75ea` (boundary_condition): Energy-market trading QUBO formulation successfully incorporates transaction costs, flow-conservation constraints, and cycle constraints, suggesting that structured domains with natural binary variables may scale more gracefully than open-ended trading problems.

**C2 flagged_papers:**
- `0e18f027f93b` (partially_grounded): The memo supports a small, cost-aware binary scheduling formulation, but it does not explicitly tie realistic constraints to qubit or penalty growth beyond hardware capacity.
- `4e492b86e6c7` (partially_grounded): The memo supports constraint-aware optimization and a deployment scalability caveat, but it does not clearly show the theme's stronger claim that realism itself drives QUBO dimensionality past hardware limits.
- `d3bf87c97dee` (misaligned_claim): This memo reports qubit-efficient compression that solves settlement instances with up to 128 transactions using fewer than 20 qubits, so it complicates the theme's claim that realistic constrained formulations are simply pushed beyond hardware capacity.

_C2 reason:_ The memos clearly support the broad formulation-versus-scale tension, but not every sampled paper grounds the full paradox as stated. 00c17032f4af frames arbitrage as a QUBO with transaction costs and constraints yet reports that "arbitrage cannot be generated ... for cycle sizes beyond ten," 2322e385b8e7 expands from 9 to 25 qubits but larger hardware runs are stopped before convergence, 25a848404367 says performance worsened as the number of currencies increased, and e71143fc75ea says bid-ask modeling increases complexity and the qubit count "scales quadratically with the number of currencies." However, 0e18f027f93b and 4e492b86e6c7 mostly show small proof-of-concept optimization setups rather than explicit constraint-driven dimensional blowup, and d3bf87c97dee partly cuts against the theme by reporting up to 128 transactions on fewer than 20 qubits via qubit-efficient encoding, even though feasibility still needs classical post-processing.

### AT-TE-003 · C2=unsupported (medium)
**Compounding deployment barriers from data encoding to execution latency**

_Interpretation:_ The barriers to quantum trading deployment — lossy data encoding, hardware noise, and execution latency — are not independent obstacles but form a compounding chain that widens the gap between theoretical promise and operational reality. Financial data must be aggressively compressed to fit qubit budgets, losing potentially critical market information; noisy NISQ hardware then degrades already-approximate computations with decoherence and gate errors; and the round-trip latency of quantum execution far exceeds the microsecond-scale requirements of time-critical trading. Each stage amplifies the losses of preceding stages, creating a multiplicative deployment readiness gap significantly wider than any single barrier suggests when considered in isolation.

_grounded_in DT:_ DT-TE-005, DT-TE-007, DT-TE-009

**B2 counter_evidence:**
- `6377e377053e` (boundary_condition): Limit order book modeling circuits function on real hardware with acceptable fidelity for shallow circuits, suggesting that specific low-depth applications with minimal encoding overhead may partially bypass the compounding barrier chain.
- `88e7d870aeb0` (boundary_condition): Quantum RL agent achieves positive returns under simulated noise models, indicating that noise-resilient circuit designs and error-aware training may partially mitigate the hardware degradation stage of the barrier chain.

**C2 flagged_papers:**
- `0d70169cb87f` (partially_grounded): The memo supports low-latency hybrid design and resource accounting, but it does not show the theme's full chain from lossy encoding through hardware noise to execution-latency failure.
- `2ae3455aa47b` (partially_grounded): This survey memo lists deployment blockers, but it treats them as separate constraints rather than explicitly claiming they compound into a single multiplicative readiness gap.
- `c7b77a40d1ea` (partially_grounded): The memo supports compact modeling and hardware/noise limits, but it does not connect those points to the ultra-low-latency execution barrier claimed by the theme.
- `ca17c4baa8d1` (partially_grounded): The memo clearly says current hardware is not yet fast enough for real-time trading and that hybrid integration is difficult, but it does not anchor the stronger compounding-chain interpretation.

_C2 reason:_ The sampled memos do support separate deployment obstacles, but they do not clearly support the stronger claim that these barriers form a single compounding chain. For example, 7ea4faff382d says "Latency is explicitly decomposed into quantum, classical, and network components," 9be7c1fe15c2 highlights that the framework is "explicitly designed to improve HFT trade execution speed and latency," and 2ae3455aa47b lists "shallow-circuit limits, repeated-measurement overhead, and gate-error constraints." Yet the memos do not trace a consistent causal sequence from lossy encoding to noise to latency, so the multiplicative deployment-gap interpretation goes beyond what the sampled notes explicitly state.

### AT-TE-004 · C2=unsupported (medium)
**Regime-conditional quantum utility as niche complement rather than paradigm shift**

_Interpretation:_ The evidence consistently shows that quantum and hybrid trading models exhibit regime-dependent performance, with advantages concentrated in high-volatility or crisis periods while underperforming or merely matching classical models in normal market conditions. Combined with the persistent competitiveness of classical baselines across regimes, this pattern suggests quantum computing in trading is unlikely to deliver a paradigm shift but may instead serve as a conditional complement — activated during market states where classical models' distributional assumptions break down or where the combinatorial explosion of crisis-period dynamics favors quantum exploration of solution spaces.

_grounded_in DT:_ DT-TE-004, DT-TE-010

**B2 counter_evidence:**
- `4e492b86e6c7` (opposing_claim): QA-optimized PPO reports performance gains across diverse market regimes including both stable and volatile periods, suggesting quantum advantage may not be confined to crisis conditions alone — though this claim is verified only in a single limited study.

**C2 flagged_papers:**
- `32f6aa86e556` (partially_grounded): The memo links adaptive qubits to volatile, high-frequency conditions, but it does not show that quantum utility is concentrated in crises relative to normal regimes or that it remains only a niche complement.
- `4e492b86e6c7` (misaligned_claim): This memo supports real-time adaptation and execution improvements, but it does not provide the theme's key claim that any quantum advantage is mainly crisis-conditional; it therefore does not anchor the narrowing interpretation.
- `8a2ce0575ff1` (partially_grounded): The memo supports classical competitiveness and warns about reward-performance gaps, but it is silent on regime-conditional advantage concentrated in high-volatility periods.
- `dca63675e36a` (partially_grounded): The memo mentions volatility and crash detection, yet it does not establish the stronger claim that quantum models help mainly in crisis regimes while merely matching or underperforming in normal conditions.

_C2 reason:_ Only two memos clearly anchor regime-conditional quantum utility. 1f628b8e78f9 explicitly says "Regime dependence is important for execution because the QLSTM advantage appears only in specific market states, especially crisis and pre-COVID periods," and ff62c3dd3f66 says performance "peaks in high volatility and degrades in extreme volatility." The broader claim that quantum is generally a niche complement rather than a paradigm shift is only partly supported by papers like 8a2ce0575ff1, where classical baselines beat quantum models on realized metrics, while 4e492b86e6c7 does not ground the crisis-only framing from its memo.

## C2 silo summary

- **themes_checked**: 4
- **grounded**: 1
- **partially_grounded**: 1
- **unsupported**: 2
- **overall_note**: The TE analytical layer is partly well grounded: the sampled memos robustly support a hybrid-modular pattern and reasonably support a formulation-versus-scale tension in optimization. However, the weaker themes systematically overextend by combining separately documented barriers into a stronger causal chain and by generalizing regime-conditional utility from too few directly supporting memos. The main concern is not fabrication of underlying observations, but analytical overreach in how broadly those observations are synthesized.