---
aliases:
- 'Optimized Stock Price Forecasting: A Deep Learning Approach Using QCTO Based GRU
  Network'
- Optimized Stock Price Forecasting
authors:
- Maloy Kumar Dey
- Shouvik Dey
auto_detected: true
classification: ''
contradiction_flags:
- contradiction:classical-vs-quantum
doi: 10.1109/CIACON65473.2025.11189776
evaluation_type: benchmark-comparison
evidence_type: ''
has_quantitative_results: true
idea_tags:
- idea:quantum-advantage
- idea:hybrid-approach
journal_or_venue: 2025 International Conference on Computing, Intelligence, and Application
  (CIACON)
methodology_tags:
- quantum-ml
- hybrid-quantum-classical
paper_type: ''
quantum_advantage_claim: speculative
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
- topic/quantum-ml-finance
- method/quantum-ml
- method/hybrid-quantum-classical
- idea/quantum-advantage
- idea/hybrid-approach
- contradiction/classical-vs-quantum
title: 'Optimized Stock Price Forecasting: A Deep Learning Approach Using QCTO Based
  GRU Network'
topic_tags:
- quantum-ml-finance
year: '2025'
zotero_key: ''
---

## Abstract summary
The paper proposes a QCTO-GRU model that integrates Quantum Class Topper Optimization (QCTO) to optimize GRU network parameters for stock price forecasting. Evaluated on Bank of America historical data (2005–2021), the approach demonstrates improved predictive accuracy over a CNN-BiLSTM-Attention baseline, reporting MAE of 0.01271 and MSE of 0.0097568.
## Methodology
The study proposes a QCTO-GRU approach for stock price forecasting that combines a Gated Recurrent Unit (GRU) network with a quantum-inspired meta-heuristic optimizer named Quantum Class Topper Optimization (QCTO). The pipeline begins with collection of Bank of America daily stock data from Yahoo Finance (Jan 2005–Oct 2021), cleaning (forward-fill for missing values, duplicate removal), feature engineering (Open, Close, Low, High, Volume plus derived/encoded columns), Min-Max scaling to [0,1], and an 80/20 train-test split. GRU is used as the forecasting model (with standard GRU gating equations reported) and its parameters/hyperparameters are optimized by QCTO: candidate parameters are encoded as Q-bit amplitudes (α, β), decoded to real-valued parameters, evaluated by training/evaluating the GRU to produce a performance factor (PF), and then updated via QCTO phase-updates and a quantum rotation gate. QCTO iterates (up to a fixed number of examinations or until convergence) using section-best and class-best learning rules, an improvement factor schedule, and Q-bit rotation updates; final performance is reported on test data using MAE, MSE and MAPE and compared against a CNN-BiLSTM-Attention baseline.

**Algorithms used:** Gated Recurrent Unit (GRU), Quantum Class Topper Optimization (QCTO), Class Topper Optimization (CTO) — referenced/base algorithm, CNN-BiLSTM-Attention (baseline)

**Dataset:** Daily stock price data for Bank of America retrieved from Yahoo Finance covering January 2005 to October 2021. Raw dataset: 4122 samples with features Open, Close, Low, High, Volume. Preprocessed dataset reported as 4027 rows with 6 columns (engineered target/feature included).
## Experiment details
### Input
{'source': 'https://finance.yahoo.com (Bank of America historical daily prices)', 'raw_size': '4122 samples x 5 features', 'features': ['OpenPrice', 'ClosePrice', 'LowPrice', 'HighPrice', 'Volume'], 'preprocessed_size': '4027 samples x 6 features (after feature engineering/target addition)', 'train_size': '3221 samples (80%)', 'test_size': '806 samples (20%)', 'preprocessing_steps': ['Missing values filled with forward-fill', 'Duplicate rows removed', 'Feature engineering to produce additional column(s) (preprocessed -> 6 cols)', 'Min-Max scaling to range [0,1]', 'Train/test temporal split (80/20)']}

### Process
{'pipeline_steps': ['Data collection from Yahoo Finance (Bank of America daily prices Jan 2005–Oct 2021).', 'Data cleaning: forward-fill missing values, remove duplicates.', 'Feature engineering: use Open, Close, Low, High, Volume and derive required target/extra column(s).', 'Scale features using Min-Max scaler to [0,1].', 'Split dataset into train (80%) and test (20%).', 'Initialize QCTO population: generate Q-bit phases (θ) from amplitudes (α, β).', 'Encode parameters: map α/β amplitudes to real-valued model parameters Q within bounds.', 'Evaluate each candidate: set GRU parameters from Q, train/evaluate GRU to compute a Performance Factor (PF).', 'Identify section best (SB) and class best (CB) based on PF.', 'Update phases: SBs learn from CB, normal students learn from SB using phase-update equations; update improvement factor wt.', 'Q-bit update: apply quantum rotation gate to (α, β) using phase correction ΔQ.', 'Decode parameters back to real-valued Qt+1 for next iteration.', 'Terminate when CB convergence achieved or maximum examinations reached; select best-found GRU parameters and evaluate on test set.'], 'iterations': 'QCTO run for up to 100 examinations (iterations) as reported; convergence criterion also used.', 'key_equations_referenced': ['GRU gate equations (reset, update, candidate state, hidden update)', 'Q-bit phase generation θ = atan2(β, α)', 'Q-value encoding/decoding rules', 'Phase update equations for SB and students', 'Improvement factor schedule wt = wmax - ((wmax - wmin)/E)*t', 'Quantum rotation gate update for (α, β)']}

### Output
{'metrics_reported': ['Mean Squared Error (MSE)', 'Mean Absolute Error (MAE)', 'Mean Absolute Percentage Error (MAPE)'], 'results_proposed': {'MSE': 0.0097568, 'MAE': 0.0127147, 'MAPE': 0.0249261}, 'baseline_model': 'CNN-BiLSTM-Attention (from reference [9])', 'baseline_results': {'MSE': 0.0128641, 'MAE': 0.0177637, 'MAPE': 0.0198415}, 'other_outputs': ['Convergence plots for MAE, MSE and MAPE across epochs/iterations', 'Prediction vs actual price plots for visual comparison']}

### Parameters
- QCTO: {'no_of_sections': 5, 'no_of_students_per_section': 100, 'courses_structure': '3 x 6 matrix (as reported)', 'no_of_examinations_max': 100, 'wmax': 0.5, 'wmin': 0, 'acceleration_coefficient_C': 1.2, 'ISS': 0.001, 'IST': 0.001}
- dataset_sizes: {'raw_rows': 4122, 'preprocessed_rows': 4027, 'train_rows': 3221, 'test_rows': 806}
- preprocessing: {'scaler': 'Min-Max Scaler to [0,1]', 'missing_value_strategy': 'forward fill'}
- GRU: {'architecture_details': 'Not specified (standard GRU gating equations provided); specific layer counts, units, learning rate and optimizer not reported'}

### Hardware
N/A

### Reproducibility
N/A
## Findings
- [supported] The paper proposes a hybrid QCTO-GRU model that uses Quantum Class Topper Optimization (QCTO) to optimize GRU network parameters for stock price prediction.
- [supported] On a Bank of America stock dataset (Jan 2005–Oct 2021, 4,122 samples, 5 features) with an 80/20 train/test split, the QCTO-GRU model achieved reported test performance of MSE = 0.0097568, MAE = 0.0127147, MAPE = 0.0249261.
- [supported] The QCTO-GRU model outperformed the compared benchmark (CNN-BiLSTM-Attention) on MSE and MAE (baseline CNN-BiLSTM reported MSE = 0.0128641, MAE = 0.0177637) but had a slightly higher MAPE than that baseline.
- [supported] The authors present convergence graphs (MAE, MSE, MAPE) showing steady decline during training, which the paper uses to argue for stable optimization behavior.
- [supported] The paper documents standard data preprocessing steps (cleaning with forward fill, feature engineering using Open, Close, Low, High, Volume, min-max scaling, 80/20 split) and the exact train/test sample counts (train 3,221, test 806).
- [supported] The QCTO algorithm is described as a quantum-inspired meta-heuristic (Q-bit representation, rotation gate updates, phase encoding) adapted from Class Topper Optimization (CTO) literature and prior QCTO references.
- [supported] The authors claim GRU is a suitable RNN variant for financial time series because it is simpler and computationally more efficient than LSTM while retaining predictive performance.
- [speculative] The paper claims that integrating 'quantum computing principles such as superposition and entanglement' into QCTO enables better exploration of the solution space and improves search efficiency and convergence.
- [speculative] The paper frames QCTO as an 'advanced' optimization approach that enhances the GRU's capacity for prediction through quantum-inspired mechanisms (phase encoding, rotation), though no quantum hardware or formal quantum speedup analysis is presented.
- [disputed] The paper asserts that 'the time series problem in regression is solved using Quantum computing theory,' a broad claim that overstates results—no general theoretical proof or use of actual quantum computing to 'solve' time-series regression is provided.

**Results summary:** The study introduces QCTO-GRU, a GRU-based deep learning model whose weights/hyperparameters are optimized by a quantum-inspired Class Topper Optimization algorithm (QCTO). On Bank of America historical stock data (4,122 samples; features: Open, Close, Low, High, Volume), the model attains reported test metrics of MSE = 0.0097568, MAE = 0.0127147, and MAPE = 0.0249261, showing improved MSE and MAE relative to a CNN-BiLSTM-Attention benchmark but a slightly worse MAPE. The authors present convergence plots indicating stable training and describe QCTO's quantum-inspired mechanisms. However, the work uses a quantum-inspired optimizer rather than real quantum hardware and does not demonstrate a provable or measured quantum computational advantage.

**Performance claims:**
- MSE = 0.0097568 (QCTO-GRU, test set)
- MAE = 0.0127147 (QCTO-GRU, test set)
- MAPE = 0.0249261 (QCTO-GRU, test set)
- Baseline CNN-BiLSTM-Attention: MSE = 0.0128641, MAE = 0.0177637, MAPE = 0.0198415 (test set)
- Dataset size: 4,122 samples × 5 features (preprocessed to 4,027 × 6 with additional target column); train/test split 3,221 / 806 (80%/20%)
- QCTO optimization run parameters: number of sections = 5, number of students = 100, number of examinations (iterations) = 100, acceleration coefficient C = 1.2, weight factor wmax = 0.5, wmin = 0
## Quantum advantage claim
**Classification:** speculative

The paper uses a quantum-inspired optimization algorithm (QCTO) that adopts quantum-like representations (Q-bits, rotation gates) but does not employ real quantum hardware nor provides empirical or theoretical evidence of quantum computational speedup or advantage. Claims that quantum principles (superposition/entanglement) improve exploration are presented without demonstration on quantum devices or formal complexity/benchmarks, so any asserted 'quantum advantage' remains speculative.
## Limitations
- The proposed QCTO-GRU model achieves lower MAE and MSE but a slightly higher MAPE compared to the benchmark, indicating less consistent percentage error (author-stated).
- [inferred] Evaluation is limited to a single asset (Bank of America stock) and a single dataset (2005–2021); generalizability across other stocks, indices, sectors or markets is not demonstrated.
- [inferred] Comparisons are made against only one benchmark model (CNN-BiLSTM-Attention); there is no comprehensive baseline set (e.g., plain GRU/LSTM without QCTO, classical optimizers, or statistical models) to isolate the benefit of QCTO.
- [inferred] No ablation study or analysis is provided to quantify the individual contribution of QCTO optimization versus the GRU architecture or other preprocessing choices.
- [inferred] The paper does not specify whether the 'quantum' aspects of QCTO are executed on actual quantum hardware or simulated classically, leaving ambiguity about practical quantum advantage.
- [inferred] The computational cost, runtime, and resource requirements of training the QCTO-GRU (including QCTO optimization) are not reported, so scalability and real-time applicability are unclear.
- [inferred] The methodology uses basic OHLCV features only; no exogenous data (e.g., macroeconomic indicators, news/sentiment, implied volatility) are included, potentially limiting predictive power.
- [inferred] Missing-data handling is limited to forward fill and duplicate removal; potential impacts of this choice on model bias or performance are not analyzed.
- [inferred] No time-series cross-validation or walk-forward testing details are provided; the use of a simple 80/20 split may inflate performance estimates or fail to assess temporal robustness.
- [inferred] No statistical significance tests or confidence intervals are reported for the performance differences versus the baseline, so it is unclear whether improvements are robust.
- [inferred] The study does not analyze economic or trading performance metrics (e.g., Sharpe ratio, returns after transaction costs), so practical usefulness for trading/investment is not assessed.
- [inferred] Interpretability and explainability of the QCTO-GRU predictions are not addressed; the model remains a black box without feature importance or attributions.
- [inferred] Robustness to market regime shifts, sudden shocks, or non-stationarity is not evaluated.
## Open questions
- Does the QCTO algorithm run on actual quantum hardware or is it a quantum-inspired/simulated algorithm executed classically?
- How does QCTO compare, in performance and computational cost, with standard hyperparameter/weight optimization methods (e.g., Bayesian optimization, grid/random search, genetic algorithms, PSO) when applied to GRU?
- What is the contribution of QCTO to the model improvement versus the GRU architecture itself (i.e., would a GRU tuned by a classical optimizer achieve similar gains)?
- How well does the QCTO-GRU generalize to other stocks, indices, asset classes, time periods, or higher-frequency (intraday) data?
- How sensitive are the results to different feature sets, preprocessing choices (e.g., scaling, missing-value imputation), and train-test splitting strategies (e.g., walk-forward validation)?
- What are the computational resource requirements (CPU/GPU time, memory) and convergence behavior of QCTO in larger-scale problems?
- Can integrating additional data sources (sentiment, macroeconomic indicators, VIX/implied volatility) further improve predictive performance, and how should these be incorporated?
- Is the observed improvement in MAE/MSE economically significant when translated into a trading strategy after accounting for transaction costs and slippage?
- How stable are the optimized parameters found by QCTO across re-training runs, and is there risk of overfitting to the chosen time window?
- How interpretable and explainable are the model’s predictions, and can feature importance or attention-like mechanisms be combined with QCTO-GRU to improve transparency?
- How robust is the QCTO-GRU approach to regime changes, extreme events, and non-stationarity in financial time series?

**Future work:**
- Explore integration of additional financial indicators and alternative deep learning architectures to further enhance forecasting performance (author-stated).
## Key ideas
- #idea:hybrid-approach — The paper proposes a hybrid pipeline combining a classical GRU forecasting model with a quantum-inspired meta-heuristic optimizer (QCTO) to tune GRU hyperparameters/weights.
- #idea:quantum-advantage — The authors claim the QCTO-GRU yields improved forecasting accuracy versus a CNN-BiLSTM-Attention baseline (better MSE and MAE on the Bank of America dataset).
- #idea:hybrid-approach — QCTO encodes candidate parameters as Q-bit amplitudes (α, β), computes phase θ, applies phase-update/quantum-rotation rules, decodes to real-valued parameters, and iterates with section-best / class-best learning rules.
- #idea:quantum-advantage — Reported test metrics: MSE=0.0097568, MAE=0.0127147, MAPE=0.0249261 (baseline reported MSE=0.0128641, MAE=0.0177637).
- #idea:hybrid-approach — Experimental pipeline and convergence plots provided (data preprocessing, train/test split, QCTO iterations up to 100), but GRU architectural details (layer counts, units, optimizer) are not specified.
- #idea:quantum-advantage — The quantum component is quantum-inspired (algorithmic Q-bit representation) rather than execution on quantum hardware; all results stem from classical implementation/experiments.
## Contradictions
- contradiction:classical-vs-quantum — Although the paper claims the QCTO-GRU outperforms the CNN-BiLSTM-Attention baseline, the QCTO-GRU has a higher MAPE (0.0249261) than the baseline (0.0198415), indicating mixed performance and weakening a blanket superiority claim.
- contradiction:classical-vs-quantum — The term 'quantum' is used for a quantum-inspired optimizer (QCTO) executed classically; there is no empirical evidence from quantum hardware to substantiate claims about quantum computational advantage.
## Notable quotes
<!-- Researcher-added — verbatim quotes with page references -->

## Researcher notes
<!-- Researcher-added — not LLM generated -->
