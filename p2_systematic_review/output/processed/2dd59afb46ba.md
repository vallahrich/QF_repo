---
aliases:
- Qutrit-based Quantum-inspired Optimization Model on Real-world Portfolio Optimization
- Qutrit based Quantum inspired
authors:
- Yao-Hsin Chou
- Yun-Ting Lai
- Ming-Ho Chang
- Yu-Chi Jiang
- Shu-Yu Kuo
auto_detected: true
classification: ''
contradiction_flags:
- contradiction:classical-vs-quantum
- contradiction:scalability
doi: 10.1109/QCE60285.2024.10403
evaluation_type: simulator
evidence_type: ''
has_quantitative_results: true
idea_tags:
- idea:quantum-advantage
journal_or_venue: 2024 IEEE International Conference on Quantum Computing and Engineering
  (QCE)
methodology_tags: []
paper_type: ''
quantum_advantage_claim: not-applicable
related_papers: []
relevance_phase1: high
relevance_phase3: high
source_type: conference-paper
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
- topic/portfolio-optimization
- idea/quantum-advantage
- contradiction/classical-vs-quantum
- contradiction/scalability
title: Qutrit-based Quantum-inspired Optimization Model on Real-world Portfolio Optimization
topic_tags:
- portfolio-optimization
year: '2024'
zotero_key: ''
---

## Abstract summary
The paper introduces a qutrit-inspired quantum-inspired optimization (QIO) approach that uses ternary encoding to represent long-selling, short-selling, and non-investment decisions and integrates this with a Global Best Guided Quantum-inspired Tabu Search (GQTS). Experiments on DJIA data (2013–2022) demonstrate that the hybrid qutrit-based strategy reduces portfolio risk and improves trend ratio compared with single long or short strategies, suggesting complementary benefits of combining LS and SS within a QIO framework.
## Methodology
The authors propose a qutrit-inspired quantum-inspired optimization (QIO) approach for portfolio optimization by encoding three investment actions (non-investment, long-selling (LS), short-selling (SS)) using a ternary (qutrit-like) representation. They adapt the Global Best Guided Quantum-inspired Tabu Search (GQTS) to operate with this ternary encoding (qutrit-based GQTS) and introduce an update mechanism that adjusts encoding probabilities via two partition parameters (βj1, βj2) and a small update step θ according to comparisons between the global best and local worst states for each asset (update rules summarized in Equation (2)). Portfolio performance is evaluated using the trend ratio (return per unit risk based on the regression trend line) and absolute risk metrics. Experiments are run on a classical computer simulating qutrit behavior; the dataset is the DJIA index (U.S.) covering 2013–2022 and split using a sliding-window (SW) procedure to maintain training-data freshness. The experimental protocol uses a population of candidate solutions, repeated runs per period, and comparisons against single-strategy baselines (LS and SS) implemented via EL-GNQTS. The study reports that the hybrid qutrit-inspired strategy achieves lower risk and higher trend-ratio performance relative to LS and SS baselines across the evaluated sliding windows.

**Algorithms used:** Qutrit-inspired Quantum-inspired Optimization (QIO), Global Best Guided Quantum-inspired Tabu Search (GQTS) — qutrit-based variant, EL-GNQTS (baseline comparator)

**Experimental setup:** Classical computer execution; qutrit behavior simulated in software (no quantum hardware or specific simulator named). Population-based QIO runs with population size 10, performing 10,000 iterations per run; 50 independent runs per sliding-window period.

**Dataset:** Dow Jones Industrial Average (DJIA) index data (U.S.) from 2013 to 2022, split via a sliding-window approach (13 types of sliding windows, totaling 830 periods). Initial capital for portfolio simulations: 10,000,000 USD. Reported solution space size: 330.
## Experiment details
### Input
{'source': 'DJIA index historical price data (U.S.)', 'time_range': '2013-2022', 'sliding_window': '13 types of sliding windows producing 830 periods (training/testing splits to maintain freshness of training data)', 'initial_capital': 10000000, 'solution_space_size': 330, 'preprocessing': 'Sliding-window split; normalization/standardization of portfolio fund values used in plotting; trend ratio computed by regression trend line on portfolio value time series. No additional preprocessing procedures or feature engineering explicitly detailed.'}

### Process
{'overview': 'Map each asset to a ternary decision (0=non-invest, 1=LS, 2=SS). Initialize a population of candidate portfolios (size 10). For each iteration, update per-asset probability parameters (βj1, βj2 and related θ adjustments) using the qutrit-based GQTS rule comparing global best and local worst states per asset (see Equation (2)). Sample or derive portfolio decisions from updated probabilities, evaluate portfolios on training window using trend ratio and risk; maintain global best. Repeat for 10,000 iterations. For each sliding-window period, perform 50 independent runs. Aggregate results across 830 SW periods and 13 SW types, and compare hybrid strategy output to LS and SS baselines implemented via EL-GNQTS.', 'key_steps': ['Encode each decision as ternary (0/1/2 mapping to non-invest/LS/SS)', 'Initialize population of candidate solutions (size 10)', 'At each iteration, compute global best (P_Gb_j) and local worst (P_Lw_j)', 'Update βj1 and βj2 by ±θ according to the qutrit-based update rules (Equation (2))', 'Construct portfolios from updated probabilities and evaluate using trend ratio and risk', 'Repeat for 10,000 iterations per run; perform 50 runs per sliding-window period', 'Compare hybrid strategy performance against LS and SS baselines (EL-GNQTS)'], 'parameters_and_counts': {'theta': 0.0003, 'population_size': 10, 'iterations_per_run': 10000, 'runs_per_period': 50, 'sliding_window_periods': 830, 'sliding_window_types': 13, 'initial_fund_usd': 10000000, 'solution_space': 330}}

### Output
{'formats': 'Time-series of portfolio fund values (plots/run charts), computed trend ratio (slope of regression trend line), and absolute risk metric(s) shown in comparisons.', 'metrics_reported': ['Trend ratio (return per unit of risk; slope of regression trend line)', 'Risk (absolute risk values shown in plots; units not fully specified)'], 'baselines': ['Long-selling (LS) portfolio via EL-GNQTS', 'Short-selling (SS) portfolio via EL-GNQTS'], 'findings_summary': 'Hybrid qutrit-inspired strategy consistently produced lower risk than LS and SS across 13 sliding-window types and delivered higher trend ratio values; visual run charts illustrated symmetric LS/SS fluctuations that produced a stabilized hybrid uptrend.'}

### Parameters
- theta: 0.0003
- population_size: 10
- iterations: 10000
- runs_per_period: 50
- sliding_window_periods: 830
- sliding_window_types: 13
- initial_fund_usd: 10000000
- solution_space_size: 330

### Hardware
N/A

### Reproducibility
N/A
## Findings
- [supported] A qutrit-inspired ternary encoding (states: non-investment, long-selling, short-selling) can be integrated into a quantum-inspired optimization (QIO) algorithm (GQTS) to represent three investment decisions.
- [supported] The proposed qutrit-based hybrid strategy (simultaneously searching for LS and SS positions) produced lower portfolio risk than single-strategy (LS-only or SS-only) portfolios across 13 sliding-window experiments on DJIA data.
- [supported] The hybrid strategy produced higher trend-ratio (return per unit risk, measured via regression trend line) than LS-only and SS-only strategies in the reported experiments.
- [supported] In selected cases, symmetric fluctuations between the LS and SS components of the hybrid portfolio produced net volatility cancellation and a more stable uptrend (illustrated for sample periods Y2M Oct 2018–Sep 2019 and Nov 2015–Oct 2016).
- [supported] Experimental setup details: solution space size 330, initial capital $10,000,000, population size 10, 50 runs per sliding-window period, each run with 10,000 iterations, θ parameter set to 0.0003, investment period 2013–2022.
- [speculative] The ternary (qutrit-inspired) encoding and update mechanism generally enable more efficient search in a larger solution space compared to binary/qubit-inspired encodings (claimed benefit for broader practical applications).
- [speculative] Qutrit-based QIO can help investors make better-informed decisions in volatile markets by encoding additional strategic information beyond buy/no-buy.
- [speculative] The authors claim novelty (they are the first to propose a qutrit-inspired hybrid strategy for real-world portfolio optimization).
- [supported] The model uses trend ratio as the evaluation metric to prefer portfolios with higher upward trend and lower deviation from the trend line.
- [supported] The qutrit-inspired GQTS update rules (θ-based updates of β parameters guided by global best and local worst states) were implemented and used to drive probability adjustments among three states.

**Results summary:** The paper proposes a qutrit-inspired ternary encoding integrated into a Global-Best-Guided Quantum-inspired Tabu Search (GQTS) to optimize portfolios over long-selling, short-selling, or no position. On DJIA historical data (2013–2022) using sliding windows, the hybrid strategy that jointly searches LS and SS allocations demonstrated empirically lower risk and higher trend-ratio than LS-only and SS-only portfolios across the reported sliding-window experiments. The authors show example periods where symmetric LS/SS fluctuations cancel volatility, producing a smoother uptrend. Experimental parameters and settings are reported, but no claim of quantum hardware usage or quantum computational speedup is made.

**Performance claims:**
- Solution space size: 330 (reported)
- Initial fund: $10,000,000 (reported)
- Population size: 10; 50 tests per sliding-window period; each test ran 10,000 iterations (reported)
- Parameter θ (update magnitude) was set to 0.0003 (reported)
- Hybrid strategy produced consistently lower risk than LS and SS in 13 sliding-window types (empirical claim across reported experiments; no absolute risk numbers provided)
- Hybrid strategy achieved higher trend ratio than LS-only and SS-only in the reported experiments (no absolute trend-ratio values provided)
## Quantum advantage claim
**Classification:** not-applicable

The work is quantum-inspired and simulated on classical hardware (no quantum device or quantum speedup demonstrated). Claims relate to using quantum concepts (qutrit-like ternary encoding) to enrich the solution representation; however, no empirical or theoretical claim of quantum computational advantage (speedup or asymptotic improvement) is presented or demonstrated.
## Limitations
- [inferred] The approach is qutrit-inspired and simulated on a classical computer rather than demonstrated on actual quantum (qutrit) hardware, so real quantum advantages are untested.
- [inferred] Experiments are performed only on the DJIA universe (U.S. market) — generalizability to other markets or asset classes is not demonstrated.
- [inferred] The evaluation relies on the trend ratio as the primary metric; standard finance metrics (e.g., Sharpe ratio, drawdown, VaR) and multi-objective trade-offs between return and risk are not fully addressed.
- [inferred] Practical market frictions are not modeled: transaction costs, bid-ask spread, short-selling constraints, margin requirements, and market impact are not considered.
- [inferred] Scalability and computational cost for much larger universes than the tested solution space (size 330) are not reported.
- [inferred] Sensitivity analysis and robustness to hyperparameters (e.g., θ, population size) are not provided, leaving uncertainty about parameter tuning and stability.
- [inferred] Benchmarks are limited — comparisons appear restricted to LS, SS and EL-GNQTS variants; broader benchmarking against other classical and quantum-inspired portfolio optimization methods is missing.
- [inferred] Operational feasibility of simultaneously carrying symmetric LS and SS positions (regulatory, capital, execution complexity) is not discussed.
## Open questions
- Can the qutrit-inspired encoding and GQTS updates be implemented on real qutrit quantum hardware, and would that yield practical advantages over the classical simulation?
- How does the hybrid LS+SS strategy perform when transaction costs, borrowing costs for shorting, and other market frictions are included?
- How robust are results to different hyperparameter settings (θ, population size, number of iterations) and to different sliding-window configurations?
- Does the hybrid strategy maintain its risk-reduction and trend-improvement properties across other markets, asset classes, and during extreme market events (e.g., crises)?
- How does the approach compare against a wider set of baselines, including modern classical portfolio optimizers, other quantum-inspired algorithms, and machine-learning approaches?
- Can the trend ratio objective be extended or replaced to directly optimize multi-objective criteria (risk vs return) and produce Pareto-optimal portfolios?
- What are the scalability limits (runtime, memory) of the qutrit-based GQTS for much larger universes (thousands of assets)?
- How sensitive is the hybrid portfolio composition to liquidity constraints and the practical ability to short specific securities?
- Does the symmetric cancellation effect between LS and SS observed in simulations hold in live trading given asynchronous executions and differing costs?
- How interpretable and stable are the resulting portfolios over time — e.g., how frequently do holdings flip between LS/SS/non-investment?
- Can constraints commonly used in practice (sector limits, turnover constraints, cardinality constraints) be incorporated into the ternary qutrit-inspired encoding and GQTS update rules?
- What is the theoretical justification (convergence, optimality guarantees) of the proposed qutrit-based update mechanism compared to existing QIO algorithms?

**Future work:**
- Expand the model to consider multiple objectives, such as jointly optimizing both risk and return.
- Include investments across various stock markets (extend beyond the DJIA / U.S. market).
## Key ideas
- #idea:quantum-advantage — A qutrit-inspired ternary encoding (non-invest/long/short) integrated into a quantum-inspired tabu search (qutrit-GQTS) yields lower measured portfolio risk and higher trend-ratio versus single-strategy baselines on DJIA historical data (2013-2022).
- #limitation:simulation-only — All experiments were executed on a classical computer simulating qutrit behaviour; no quantum hardware or QPU experiments were performed.
- #limitation:scalability — Reported problem size is small (solution space = 330, population size 10); paper does not demonstrate scaling to larger asset universes or higher-dimensional portfolios.
- #limitation:data-encoding — The work uses ternary encoding for three decision states, but does not address costs or complexity of mapping larger real-world decision spaces into qutrit-like representations.
- #idea:quantum-advantage — The hybrid (LS+SS) search strategy stabilises symmetric fluctuations between long and short components in some periods, producing volatility cancellation and a more stable uptrend in sample windows.
- #limitation:no-empirical-validation — While numerical comparisons to LS and SS baselines are provided, there is no validation on quantum hardware nor comparison to a broader set of classical state-of-the-art optimizers.
## Contradictions
- contradiction:classical-vs-quantum — The paper is framed as 'qutrit-based' yet presents results from purely classical simulations of quantum-inspired mechanisms; claims of quantum-related advantage are not supported by experiments on quantum hardware and may conflate quantum-inspired heuristics with genuine quantum speedup or hardware advantage.
- contradiction:scalability — The positive results are reported on a small solution space (330) and compact population/iteration settings; the paper does not provide evidence that the approach scales to realistic large-asset portfolios, raising tension between reported benefits and practical scalability.
## Notable quotes
<!-- Researcher-added — verbatim quotes with page references -->

## Researcher notes
<!-- Researcher-added — not LLM generated -->
