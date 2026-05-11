---
aliases:
- 'Quantum Machine Learning for Secure Financial Forecasting: Mitigating Data Breaches
  and Adversarial Exploits'
- Quantum Machine Learning Secure
authors:
- Olufisayo Juliana Tiwo
auto_detected: true
classification: ''
contradiction_flags:
- contradiction:scalability
- contradiction:classical-vs-quantum
doi: https://doi.org/10.9734/ajrcos/2025/v18i4613
evaluation_type: simulator
evidence_type: ''
has_quantitative_results: true
idea_tags:
- idea:quantum-advantage
- idea:near-term-feasibility
journal_or_venue: Asian Journal of Research in Computer Science
methodology_tags:
- quantum-ml
- quantum-cryptography
paper_type: ''
quantum_advantage_claim: demonstrated
related_papers: []
relevance_phase1: high
relevance_phase3: high
source_type: peer-reviewed-empirical
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
- topic/cryptography-security
- method/quantum-ml
- method/quantum-cryptography
- idea/quantum-advantage
- idea/near-term-feasibility
- contradiction/scalability
- contradiction/classical-vs-quantum
title: 'Quantum Machine Learning for Secure Financial Forecasting: Mitigating Data
  Breaches and Adversarial Exploits'
topic_tags:
- quantum-ml-finance
- cryptography-security
year: '2025'
zotero_key: ''
---

## Abstract summary
This empirical study evaluates Quantum Machine Learning (QML) for financial forecasting, comparing a Quantum LSTM (QLSTM) to classical LSTM and ARIMA on Yahoo Finance data and reporting superior predictive performance for QLSTM (RMSE 1.82, MAE 1.45, MSE 3.31). It further finds quantum methods (QSVM) more robust to adversarial attacks and that Quantum Key Distribution (QKD) offers substantial security advantages over classical cryptography, while noting challenges including high computational cost, hardware limitations, and integration complexity.
## Methodology
This study used a quantitative experimental approach to evaluate Quantum Machine Learning (QML) for financial forecasting and security. Forecasting experiments compared a Quantum LSTM (QLSTM) model against a classical LSTM and ARIMA using Yahoo Finance time-series data (daily closing prices, volumes, volatility indices over a 10-year period). Forecast performance was assessed with RMSE, MAE and MSE and statistical significance tested via paired t-tests. Adversarial robustness was evaluated using the IEEE DataPort 'Adversarial Attacks on AI in Finance' dataset; Random Forest, classical SVM and LSTM models were compared to a Quantum SVM (QSVM) under FGSM and PGD attacks (adversarial perturbation x' = x + ε·sign(∇xJ(θ,x,y))). Robustness impact was measured as relative accuracy drop ΔA = (A_clean − A_adv)/A_clean × 100%. Quantum security mechanisms were assessed with QKD data from NIST, computing Secure Key Rate (SKR = R_raw·(1 − H(E))) and Shannon entropy of keys and comparing QKD metrics to classical cryptosystems (RSA-4096, AES-256). The broader impact of QML adoption was analyzed via multiple linear regression using World Bank FinTech/AI-in-Finance data, with forecasting accuracy as the dependent variable and QML adoption rate, quantum infrastructure investment, and AI integration as predictors; significance was evaluated by p-values and adjusted R².

**Algorithms used:** Quantum LSTM (QLSTM), Classical LSTM, ARIMA, Random Forest, Support Vector Machine (SVM), Quantum SVM (QSVM), Fast Gradient Sign Method (FGSM) [attack], Projected Gradient Descent (PGD) [attack], Quantum Key Distribution (QKD) [security mechanism], Multiple Linear Regression

**Dataset:** Yahoo Finance daily market data (daily closing prices, trading volumes, volatility indices over 10 years); IEEE DataPort 'Adversarial Attacks on AI in Finance' dataset for adversarial tests; NIST QKD data for secure key analysis; World Bank FinTech and AI in Finance dataset for adoption/regression analysis.
## Experiment details
### Input
{'forecasting_dataset': {'source': 'Yahoo Finance', 'description': 'Daily closing prices, trading volumes, volatility indices', 'timeframe': '10 years (daily)', 'size': 'Not explicitly reported (daily time series over 10 years)', 'preprocessing': 'Not specified in manuscript'}, 'adversarial_dataset': {'source': 'IEEE DataPort - Adversarial Attacks on AI in Finance', 'description': 'Adversarial examples for finance-related AI models', 'size': 'Not specified', 'preprocessing': 'Not specified'}, 'qkd_dataset': {'source': 'NIST QKD data', 'description': 'Raw key rates and error rates for QKD systems', 'size': 'Not specified', 'preprocessing': 'Not specified'}, 'adoption_dataset': {'source': 'World Bank FinTech and AI in Finance dataset', 'description': 'Metrics on QML adoption rate, quantum infrastructure investment, AI integration', 'size': 'Not specified', 'preprocessing': 'Not specified'}}

### Process
{'forecasting_pipeline': ['Train QLSTM, classical LSTM, and ARIMA on Yahoo Finance time series', 'Compute predictions and evaluate using RMSE, MAE, MSE', 'Perform paired t-test to assess statistical significance of forecasting improvements'], 'adversarial_pipeline': ['Train baseline models (Random Forest, SVM, LSTM) and QSVM on relevant finance dataset', 'Generate adversarial examples using FGSM and PGD (perturbation formula provided)', 'Measure accuracy before and after attacks and compute relative accuracy drop ΔA'], 'qkd_evaluation': ['Compute Secure Key Rate SKR = R_raw·(1 − H(E)) using NIST QKD data', 'Compute Shannon entropy of generated keys', 'Compare SKR, entropy and estimated resistance years against RSA-4096 and AES-256'], 'adoption_analysis': ['Fit multiple linear regression Y = β0 + β1X1 + β2X2 + β3X3 + ε', 'Where Y = forecasting accuracy, X1 = QML adoption rate, X2 = quantum infrastructure investment, X3 = AI integration', 'Report coefficients, p-values, and Adjusted R²'], 'parameters_reported': 'No model hyperparameters (e.g., learning rates, epochs), adversarial ε values, quantum circuit parameters (qubits, depth, shots), or hardware details were reported.'}

### Output
{'forecasting_metrics': [{'model': 'Quantum LSTM (QLSTM)', 'RMSE': 1.82, 'MAE': 1.45, 'MSE': 3.31}, {'model': 'Classical LSTM', 'RMSE': 4.79, 'MAE': 3.7, 'MSE': 22.98}, {'model': 'ARIMA', 'RMSE': 6.52, 'MAE': 5.3, 'MSE': 42.49}], 'adversarial_results': {'baseline_models': {'Random Forest': {'accuracy_before': 88.75, 'after_FGSM': 77.19, 'after_PGD': 67.73}, 'SVM': {'accuracy_before': 89.51, 'after_FGSM': 75.95, 'after_PGD': 64.43}, 'LSTM': {'accuracy_before': 82.32, 'after_FGSM': 66.74, 'after_PGD': 62.11}}, 'QSVM': {'accuracy_before': 94.79, 'after_FGSM': 83.73, 'after_PGD': 79.99}, 'robustness_drop_percent': {'QSVM_FGSM': 11.67, 'QSVM_PGD': 15.6, 'SVM_PGD': 28.02, 'LSTM_PGD': 24.55}}, 'qkd_comparison': [{'method': 'QKD', 'SKR_bps': 5.87, 'shannon_entropy': 0.99, 'estimated_resistance_years': 102.9}, {'method': 'RSA-4096', 'SKR_bps': 1.45, 'shannon_entropy': 0.77, 'estimated_resistance_years': 1.8}, {'method': 'AES-256', 'SKR_bps': 2.1, 'shannon_entropy': 0.82, 'estimated_resistance_years': 6.01}], 'regression_output': {'Intercept': {'coefficient': 50.23, 'p_value': 0.0}, 'QML_Adoption_Rate': {'coefficient': 0.5, 'p_value': 0.002}, 'Quantum_Infrastructure_Investment': {'coefficient': 0.3, 'p_value': 0.015}, 'AI_Integration': {'coefficient': 0.2, 'p_value': 0.043}, 'Adjusted_R_squared': 0.85}, 'baselines': {'forecasting': ['Classical LSTM', 'ARIMA'], 'adversarial': ['Random Forest', 'SVM', 'Classical LSTM'], 'cryptography': ['RSA-4096', 'AES-256']}}

### Parameters
N/A

### Hardware
N/A

### Reproducibility
Datasets referenced are public (Yahoo Finance, IEEE DataPort adversarial dataset, NIST QKD data, World Bank FinTech dataset). The manuscript does not provide code, model hyperparameters, training details (epochs, batch sizes, learning rates), adversarial ε values, quantum circuit/circuit-implementation details, or hardware/simulator identifiers, which limits direct reproducibility.
## Findings
- [supported] Quantum LSTM (QLSTM) outperformed classical LSTM and ARIMA on the study's Yahoo Finance dataset, achieving lower RMSE (1.82), MAE (1.45) and MSE (3.31).
- [supported] Paired t-test reported for QLSTM (p = 0.98) and for classical LSTM (p = 0.67) and ARIMA (p = 0.41); the paper interprets QLSTM forecasts as statistically consistent with actual prices.
- [supported] Quantum SVM (QSVM) exhibited increased adversarial robustness in experiments: accuracy degradation of 11.67% under FGSM and 15.60% under PGD, lower than the classical models tested.
- [supported] Classical models tested (Random Forest, SVM, LSTM) experienced larger accuracy drops under adversarial attacks (e.g., SVM PGD drop 28.02%, LSTM PGD drop 24.55%) per the paper's adversarial experiments (IEEE DataPort dataset).
- [supported] QSVM had the highest baseline (clean) accuracy reported in the experiments (94.79%).
- [supported] QKD (using NIST data in the paper) achieved a Secure Key Rate (SKR) = 5.87 bps and Shannon entropy = 0.99, and was presented as superior on those metrics compared to RSA-4096 and AES-256 in the paper's analysis.
- [speculative] The paper states QKD would provide more than 100 years of resistance to quantum attacks (presented as an estimated longevity metric derived by the authors).
- [disputed] The paper states RSA-4096 has an estimated resistance to quantum attacks of only 1.8 years — a claim that conflicts with mainstream assessments that no near-term fault-tolerant quantum hardware exists to break large RSA keys in such short timeframes.
- [supported] Multiple linear regression linking QML adoption, quantum infrastructure investment, and AI integration to forecasting accuracy: model Adjusted R^2 = 0.85; QML adoption coefficient = 0.50 (p = 0.002), infrastructure investment coefficient = 0.30 (p = 0.015), AI integration coefficient = 0.20 (p = 0.043).
- [speculative] The paper argues that broad industry QML adoption will yield competitive advantages for financial firms and become foundational to next-generation financial analytics — presented as projection and recommendation rather than direct empirical evidence within the study.
- [speculative] The paper lists adoption barriers (high computational cost, qubit instability, hardware limitations, integration complexity, regulatory needs) — claims supported by cited literature but not experimentally quantified in this study.
- [supported] The paper summarizes prior-cited empirical and industry examples (Itaú Unibanco, HSBC/Quantinuum, Accenture, BBVA, IBM) where quantum techniques or pilots have been applied to financial problems (cited sources are used to support these statements).
- [speculative] Statements that quantum-enhanced cryptography (QKD) and PQC will become regulatory necessities for finance are forward-looking and framed as recommendations rather than empirically established outcomes in this study.

**Results summary:** The paper reports experimental evidence that quantum-enhanced models outperform classical counterparts on the employed datasets: a QLSTM reduced forecast errors (RMSE=1.82, MAE=1.45, MSE=3.31) compared with classical LSTM and ARIMA, and a QSVM preserved higher accuracy under adversarial FGSM/PGD attacks than Random Forest, SVM and LSTM. The authors further compare cryptographic approaches using NIST QKD data and report a higher secure key rate and near-maximal entropy for QKD versus RSA-4096 and AES-256, and present a regression associating higher QML adoption and quantum infrastructure investment with better forecasting accuracy (Adjusted R^2=0.85). The paper notes important limits — cost, hardware scalability, and integration complexity — and offers policy and investment recommendations. Some longevity and cryptanalytic timespan claims (e.g., RSA-4096 breakability in ~1.8 years; QKD >100 years resistance) are asserted by the authors but rest on extrapolations and assumptions and therefore are flagged as speculative or disputed.

**Performance claims:**
- QLSTM: RMSE = 1.82, MAE = 1.45, MSE = 3.31 (vs Classical LSTM: RMSE 4.79, MAE 3.70, MSE 22.98; ARIMA: RMSE 6.52, MAE 5.30, MSE 42.49).
- QLSTM paired t-test p-value = 0.98; Classical LSTM p = 0.67; ARIMA p = 0.41 (as reported).
- QSVM clean accuracy = 94.79%; after FGSM = 83.73% (drop 11.67%); after PGD = 79.99% (drop 15.60%).
- Random Forest accuracy: clean 88.75%, FGSM 77.19% (drop 13.03%), PGD 67.73% (drop 23.68%).
- SVM accuracy: clean 89.51%, FGSM 75.95% (drop 15.15%), PGD 64.43% (drop 28.02%).
- LSTM accuracy: clean 82.32%, FGSM 66.74% (drop 18.93%), PGD 62.11% (drop 24.55%).
- QKD (NIST data per paper): Secure Key Rate (SKR) = 5.87 bps; Shannon Entropy (key randomness) = 0.99; estimated resistance to quantum attacks = 102.90 years (authors' estimate).
- RSA-4096 (paper's comparison): SKR = 1.45 bps; Shannon Entropy = 0.77; estimated resistance to quantum attacks = 1.80 years (authors' estimate).
- AES-256 (paper's comparison): SKR = 2.10 bps; Shannon Entropy = 0.82; estimated resistance to quantum attacks = 6.01 years (authors' estimate).
- Regression: QML adoption rate coefficient = 0.50 (p = 0.002); Quantum infrastructure investment coefficient = 0.30 (p = 0.015); AI integration coefficient = 0.20 (p = 0.043); Adjusted R^2 = 0.85.
## Quantum advantage claim
**Classification:** demonstrated

Within the experiments reported in the paper, quantum-enhanced models (QLSTM and QSVM) delivered better forecasting metrics and increased adversarial robustness compared to the classical baselines tested, and QKD outperformed classical algorithms on SKR and entropy measures. These empirical results in the manuscript are presented as evidence of a quantum advantage for the studied tasks, though some extrapolated security longevity and cryptanalysis timeframe claims rely on assumptions and should be interpreted with caution.
## Limitations
- High computational costs for QML models and training (author-stated)
- Quantum hardware limitations: qubit stability, high error rates, limited scalable quantum processors (author-stated)
- Integration complexity: difficulty integrating quantum solutions and quantum security mechanisms into legacy financial systems (author-stated)
- Significant infrastructure investment required for quantum security frameworks such as QKD to ensure scalability and reliability (author-stated)
- QKD practical constraints: distance limitations and specialized infrastructure requirements (author-stated)
- Need for algorithmic refinement: existing QML algorithms require further development and tailoring for large-scale financial applications (author-stated)
- Model interpretability concerns: many QML models act as 'black boxes,' complicating regulatory compliance and trust (author-stated)
- Regulatory and compliance barriers, including adaptation of frameworks and export restrictions on quantum technologies (author-stated)
- Limited availability and access to production-grade quantum hardware; much progress remains experimental (author-stated)
- Security of classical cryptography against future quantum attacks—necessitates transition to PQC/QKD (author-stated)
- [inferred] Experimental/implementation details are insufficiently reported for reproducibility (e.g., hardware vs. simulator used, hyperparameters, dataset splits, training epochs)
- [inferred] Evaluation limited to a narrow set of adversarial attacks (FGSM and PGD); other attack types (poisoning, backdoor, adaptive attacks) were not assessed
- [inferred] Use of public datasets (Yahoo Finance, IEEE DataPort, NIST) may limit generalizability to proprietary institutional datasets and live trading settings
- [inferred] Comparison baselines are limited (ARIMA, LSTM, SVM, Random Forest); broader classical baselines and ensemble/hybrid baselines were not explored
- [inferred] Claims about long-term QKD resistance (e.g., >100 years) are based on theoretical/estimated metrics rather than demonstrated, real-world long-horizon evidence
- [inferred] Economic and operational costs/benefit analysis of adopting QML and QKD in financial institutions is not provided
- [inferred] Robustness of QML models across different market regimes, asset classes, and time horizons is not evaluated
## Open questions
- How can QML algorithms be further developed and tailored specifically for diverse, large-scale financial forecasting tasks?
- What concrete roadmap (technical and economic) will make production-scale quantum hardware accessible and affordable to financial institutions?
- How can interpretability and explainability of QML models be improved to meet regulatory and governance requirements in finance?
- What are the most effective hybrid quantum-classical architectures for balancing quantum advantage with practical cost and availability constraints?
- How can QKD be scaled for long-distance, high-throughput financial communications while remaining cost-effective?
- What regulatory standards and compliance frameworks are needed to govern QML and quantum security deployment in financial services?
- To what extent do QML benefits demonstrated on public datasets and simulators translate to real-world proprietary datasets and live trading conditions?
- How resilient are quantum-enhanced models to a broader spectrum of adversarial attacks (including poisoning, adaptive, and black-box attacks)?
- What are the trade-offs between Post-Quantum Cryptography (PQC) and QKD for financial institutions in terms of deployability, cost, and long-term security?
- How should financial institutions prioritize investments (R&D, infrastructure, talent) to maximize the operational and security gains from QML?
- What performance and robustness guarantees can be provided for QML models under volatile market regimes and structural breaks?
- How can reproducibility and benchmarking standards be established for QML research in finance (datasets, metrics, hardware descriptions)?

**Future work:**
- Refine and develop QML algorithms specifically tailored to financial forecasting needs
- Advance quantum hardware and error-correction methods to improve qubit stability, scalability, and practical usability
- Investigate hybrid quantum-classical model architectures to reduce computational cost while leveraging quantum advantages
- Expand adversarial robustness studies to include a wider range of attack types (poisoning, adaptive, black-box) and develop quantum-aware defenses
- Research scalable and cost-effective deployment strategies for QKD in financial communications, addressing distance and infrastructure constraints
- Develop methods to improve interpretability and transparency of QML models for regulatory compliance
- Conduct empirical validation of QML methods on production-grade quantum hardware and on proprietary institutional datasets
- Perform economic cost–benefit analyses for adopting QML and quantum security mechanisms in financial institutions
- Collaborate with regulatory bodies to establish standardized guidelines and compliance frameworks for quantum technologies in finance
- Invest in R&D and cross-sector collaborations to address implementation bottlenecks and operationalize quantum-enhanced financial analytics
## Key ideas
- #idea:quantum-advantage — QLSTM reports substantially better forecasting metrics than classical LSTM and ARIMA on Yahoo Finance data (RMSE 1.82 vs 4.79/6.52; MAE 1.45 vs 3.7/5.3), and QSVM shows smaller accuracy drops under FGSM/PGD attacks (QSVM_PGD drop 15.6% vs SVM_PGD 28.02%), indicating claimed predictive and adversarial-robustness advantages.
- #idea:quantum-advantage — QKD is presented as offering superior security metrics (SKR_bps 5.87, Shannon entropy 0.99, estimated resistance years 102.9) compared to classical RSA-4096 and AES-256 in the authors' analysis.
- #idea:near-term-feasibility — Multiple regression links higher QML adoption and quantum infrastructure investment to improved forecasting accuracy (Adjusted R^2=0.85; QML adoption p=0.002), suggesting possible real-world benefits if adoption and investment increase.
- #limitation:qubit-count — The paper does not report quantum circuit or hardware details (qubit count, circuit depth, shots) or model hyperparameters, undermining reproducibility and raising questions about resource requirements.
- #limitation:simulation-only — No hardware provenance is provided for the QML experiments (no QPU vs simulator declaration); absence of hardware details implies results were likely produced in simulation rather than on real quantum devices.
- #limitation:noise — Hardware noise, error rates and any mitigation strategies are not evaluated experimentally despite being cited as a challenge, so the effect of realistic noise on reported gains is unknown.
- #limitation:data-encoding — The manuscript omits data preprocessing and quantum data-encoding details for QLSTM/QSVM, leaving the computational cost and feasibility of encoding financial time series unaddressed.
- #contradiction:scalability — The manuscript simultaneously claims strong empirical benefits and emphasizes hardware limitations and high computational cost, creating tension about whether these gains can scale to real-world, hardware-constrained deployments.
- #contradiction:classical-vs-quantum — Large reported advantages lack supporting methodological detail (missing adversarial epsilon values, hyperparameters, training/validation splits), which contradicts the strength of the superiority claims and limits verifiable comparison to classical baselines.
## Contradictions
- The paper reports large quantum-model advantages but omits critical methodological and hardware details (no qubit counts, circuit depths, shots, hyperparameters, adversarial epsilon values). This absence undermines the validity of comparative claims and reproducibility.
- While presenting QKD metrics (SKR, entropy, estimated resistance years) as superior to RSA-4096 and AES-256, the comparison mixes fundamentally different primitives (quantum key distribution metrics vs classical cipher key lifetimes), which is a methodologically inconsistent comparison.
- The authors claim practical impact and link adoption/investment to better forecasting (high Adjusted R^2), yet simultaneously acknowledge hardware limitations and high costs — a contradiction about near-term deployability and scalability.
- Adversarial robustness claims are undermined by missing experimental details (e.g., epsilon values for FGSM/PGD, training regimes), making it unclear whether robustness gains stem from model architecture, training differences, or experimental choices.
## Notable quotes
<!-- Researcher-added — verbatim quotes with page references -->

## Researcher notes
<!-- Researcher-added — not LLM generated -->
