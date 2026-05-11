---
aliases:
- LLM-Guided Ans¨atze Design for Quantum Circuit Born Machines in Financial Generative
  Modeling
- LLM Guided Ans atze
authors:
- Yaswitha Gujju
- Romain Harang
- Tetsuo Shibuya
auto_detected: true
classification: ''
contradiction_flags:
- contradiction:classical-vs-quantum
doi: ''
evaluation_type: real-hardware
evidence_type: ''
has_quantitative_results: true
idea_tags:
- idea:quantum-advantage
- idea:near-term-feasibility
- idea:hybrid-approach
journal_or_venue: arXiv preprint (quant-ph)
methodology_tags:
- variational-nisq
- quantum-ml
- hybrid-quantum-classical
- error-mitigation
paper_type: ''
quantum_advantage_claim: speculative
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
- topic/quantum-ml-finance
- method/variational-nisq
- method/quantum-ml
- method/hybrid-quantum-classical
- method/error-mitigation
- idea/quantum-advantage
- idea/near-term-feasibility
- idea/hybrid-approach
- contradiction/classical-vs-quantum
title: LLM-Guided Ans¨atze Design for Quantum Circuit Born Machines in Financial Generative
  Modeling
topic_tags:
- quantum-ml-finance
year: '2025'
zotero_key: ''
---

## Abstract summary
This preprint presents a prompt-based framework that leverages large language models to generate hardware-aware quantum circuit Born machine (QCBM) ansätze, conditioned on qubit connectivity, gate error rates, and topology, with iterative feedback using KL divergence, circuit depth, and validity. Evaluated on a generative task for Japanese Government Bond interest rates and run on a 12-qubit IBM device, the LLM-generated circuits are substantially shallower and show improved noise robustness and generative performance compared to a standard TwoLocal baseline, while noting limitations around occasional invalid outputs and hardware noise.
## Methodology
The authors propose a prompt-driven framework that uses a large language model (GPT-4.1) to generate hardware-aware quantum circuit Born machine (QCBM) ansatzes and iteratively refine them using empirical performance feedback. Prompts encode device-specific information (qubit count, connectivity, error rates, native basis gates) and constraints (maximum allowable depth, validity flag). The LLM proposes a candidate circuit which is trained as a QCBM on a noiseless Qiskit aer_simulator backend using the MMD loss (Gaussian kernel, bandwidth σ=3). Gradients are estimated via the parameter-shift rule and training uses the Adam optimizer (learning rate 0.1) with stochastic mini-batch updates (batch size 1,000) over 30 epochs (with extensions reported up to 50–100 epochs for convergence analysis). Each candidate circuit is evaluated by metrics including reverse KL divergence (DKL(Q||P)), circuit depth, and validity; these metrics are provided back to the LLM which decides to prune or extend the architecture. Trained circuits are then executed on a 12-qubit IBM device (ibm_fez) using Qiskit Sampler, with optional measurement error mitigation via the Mthree package and optional post-selection on valid bitstrings. A TwoLocal ansatz (alternating RX/RZ rotation layers and CZ entanglement with 18 repetitions, depth ≈85) serves as the baseline for comparison against the LLM-generated, shallower ansatz (depth 28). Evaluation reports MMD convergence on simulator and KL divergence on simulator and real hardware (with and without error mitigation).

**Algorithms used:** Quantum Circuit Born Machine (QCBM), Maximum Mean Discrepancy (MMD) loss, Reverse Kullback–Leibler divergence (DKL(Q||P)), Adam optimizer, Parameter-shift gradient rule, TwoLocal ansatz (baseline), LLM-guided architecture search (GPT-4.1 prompt engineering), Measurement error mitigation (Mthree), Post-selection
**Frameworks:** Qiskit (including aer_simulator and Sampler primitive), Mthree (measurement error mitigation), OpenAI GPT-4.1 (LLM used for ansatz generation)

**Experimental setup:** Training on Qiskit aer_simulator (noiseless) with 10,000 measurement shots per circuit evaluation; trained circuits executed on a 12-qubit IBM quantum processor (ibm_fez) via Qiskit Sampler. Measurement error mitigation applied with Mthree. Prompts to LLM included hardware connectivity, gate errors, and maximum depth constraints.

**Dataset:** Daily Japanese Government Bond (JGB) interest rates for three maturities (5, 10, 20 years) from the Ministry of Finance Japan covering January 4, 2000 to February 28, 2025. The dataset contains 6,164 samples and is publicly available from the Ministry of Finance Japan.
## Experiment details
### Input
Source: Ministry of Finance Japan public dataset of daily interest rates for 5-, 10-, and 20-year JGB maturities (2000-01-04 to 2025-02-28). Size: 6,164 samples. Preprocessing: uniform quantization (binary encoding) mapping each real-valued input to an n-bit binary representation; experiments allocate 4 qubits per maturity (total 12 qubits), using the mapping (x)_2 = round((2^n - 1) * (x - xmin) / (xmax - xmin)) and inverse mapping described in the paper.

### Process
1) Encode real-valued JGB rates to binary strings (4 qubits per maturity, 12 qubits total). 2) Use GPT-4.1 prompts containing hardware profile (connectivity, error rates, native gates) to synthesize a candidate QCBM ansatz or select baseline TwoLocal. 3) Train the QCBM on Qiskit aer_simulator: compute MMD loss (Gaussian kernel, σ=3), estimate gradients via parameter-shift, update parameters with Adam (lr=0.1) using mini-batches of size 1,000; typical training reported for 30 epochs (with extended runs up to 50–100 epochs for analysis). 4) Evaluate trained model on simulator (MMD, KL) and then execute the trained circuit on ibm_fez (10,000 shots) via Qiskit Sampler. 5) Apply measurement error mitigation (Mthree) and optional post-selection; compute reverse KL divergence DKL(Q||P) and compare to TwoLocal baseline. 6) Provide performance metrics (KL, depth, validity) back to the LLM for iterative ansatz refinement (prune/append layers) in subsequent rounds.

### Output
Reported metrics include MMD loss trajectories during training and reverse KL divergence values on both simulator and real hardware. Baseline: TwoLocal ansatz (depth ≈85, 18 repetitions). LLM-generated ansatz: depth 28. Table I examples: simulator KL — LLM 3.67 vs TwoLocal 3.10; real hardware KL (no EM) — LLM 7.37 ± 0.11 vs TwoLocal 9.32 ± 0.06; with EM — LLM 6.91 ± 0.13 vs TwoLocal 8.92 ± 0.07. Post-selection results show KL reductions to ~0.78 (LLM) and ~0.68 (TwoLocal). Outputs also include probability distribution plots comparing true data and model outputs.

### Parameters
- qubits: 12
- qubits_per_maturity: 4
- llm_generated_depth: 28
- baseline_depth: 85
- baseline_repetitions: 18
- shots_per_evaluation: 10000
- optimizer: Adam
- learning_rate: 0.1
- batch_size: 1000
- epochs_reported: 30
- extended_epochs_analyzed: 50-100 (reported for convergence analysis)
- mmd_kernel: Gaussian
- mmd_sigma: 3
- gradient_rule: parameter-shift
- loss_metrics: ['MMD', 'reverse KL (DKL(Q||P))']
- error_mitigation: Mthree measurement error mitigation
- execution_primitive: Qiskit Sampler

### Hardware
{'simulator': 'Qiskit aer_simulator (noiseless)', 'quantum_processor': 'ibm_fez (12 qubits)', 'cloud_provider': 'IBM Quantum (access via Qiskit)', 'shots': 10000, 'execution_interface': 'Qiskit Sampler; measurement error mitigation with Mthree'}

### Reproducibility
The paper specifies dataset source (Ministry of Finance Japan) and detailed training/hardware parameters (qubits, shots, optimizer, kernel bandwidth, ansatz depths). However, no code repository, notebooks, or explicit scripts are provided in the preprint, and there is no link to implementation artifacts. Reproducibility would require re-implementing prompts used with GPT-4.1 and the exact ansatz descriptions (not fully enumerated in the text), or requesting code from the authors.
## Findings
- [supported] Prompted LLMs (GPT-4.1) can be used to generate hardware-aware QCBM ansatz conditioned on device constraints (qubit connectivity, native gates, error rates) and iterative performance feedback.
- [supported] The LLM-generated ansatz are significantly shallower than the TwoLocal baseline (depth 28 vs 85) while remaining executable on the target 12-qubit IBM device.
- [supported] On a noiseless simulator the TwoLocal baseline attains slightly better KL divergence (3.10) than the LLM-generated ansatz (3.67), indicating higher expressivity of the deeper baseline in simulation.
- [supported] When executed on real 12-qubit IBM hardware, the LLM-generated ansatz shows better robustness to noise than the deeper TwoLocal circuit (KL: LLM 7.37 ± 0.11 no EM, 6.91 ± 0.13 with EM; TwoLocal 9.32 ± 0.06 no EM, 8.92 ± 0.07 with EM).
- [supported] Measurement error mitigation and post-selection materially improve generative performance on hardware; post-selection reduced KL to roughly 0.78 (LLM) and 0.68 (TwoLocal) on the best device outputs.
- [supported] Hardware-aware initialization via prompt engineering reduced the need for transpilation (authors executed the generated circuits on the device without further transpilation), helping control circuit depth and error accumulation.
- [supported] The LLM-guided iterative loop using metrics (KL divergence, circuit depth, validity) can steer architecture evolution (pruning/adding layers) toward hardware-feasible circuits.
- [supported] The authors observed that LLMs sometimes produce invalid or unsupported circuit components after many iterations (noted failure modes around 10–20 iterations).
- [supported] Training deep QCBMs is computationally demanding and noise in near-term devices necessitates error mitigation and post-processing.
- [speculative] LLM-driven quantum architecture search provides a promising path toward robust, deployable generative models on NISQ devices and could enable practical quantum advantage in generative tasks if scaled and generalized.

**Results summary:** The paper introduces a prompt-based framework using an LLM (GPT-4.1) to synthesize hardware-aware QCBM ansatz for a 12-qubit generative task (binary-encoded JGB interest-rate data). The LLM-generated circuits are substantially shallower (depth 28) than a standard TwoLocal baseline (depth 85). In noiseless simulation the deeper TwoLocal ansatz attains slightly better KL divergence, but on real IBM hardware the shallower LLM-generated ansatz attains lower KL divergence under both raw execution and with measurement error mitigation, indicating improved noise resilience. Post-selection and measurement-error mitigation further reduce KL substantially. The authors report occasional invalid circuit outputs from the LLM and note computational/training costs and the need for error mitigation as limitations.

**Performance claims:**
- LLM-generated ansatz depth: 28
- TwoLocal baseline ansatz depth: 85
- Noiseless simulator KL divergence — LLM-generated: 3.67
- Noiseless simulator KL divergence — TwoLocal: 3.10
- Real hardware (ibm_fez, 12 qubits) KL divergence — LLM (no EM): 7.37 ± 0.11
- Real hardware (ibm_fez, 12 qubits) KL divergence — LLM (with EM): 6.91 ± 0.13
- Real hardware (ibm_fez, 12 qubits) KL divergence — TwoLocal (no EM): 9.32 ± 0.06
- Real hardware (ibm_fez, 12 qubits) KL divergence — TwoLocal (with EM): 8.92 ± 0.07
- Post-selection KL divergence (best device outputs) — LLM-generated: ≈ 0.78
- Post-selection KL divergence (best device outputs) — TwoLocal: ≈ 0.68
- Training configuration: 10,000 measurement shots per circuit evaluation, Adam optimizer (lr=0.1), MMD loss with Gaussian kernel σ=3, training on simulator and then execution on hardware
## Quantum advantage claim
**Classification:** speculative

The paper reports improved hardware robustness of LLM-generated ansatz relative to a standard quantum-circuit baseline (TwoLocal) on a 12-qubit device, but it does not present comparisons to classical generative models nor claims a provable or empirical quantum advantage over classical methods. The suggestion that this approach is a path toward practical quantum advantage is presented as a prospective assertion rather than a demonstrated result.
## Limitations
- LLMs sometimes produce invalid or unsupported circuit components, especially after 10–20 iterations (author-stated).
- Training deep QCBMs is computationally demanding and is further complicated by noise in current quantum hardware, requiring effective error mitigation (author-stated).
- Generative performance degrades substantially on real hardware due to noise — post-selection and error mitigation are needed to recover quality, indicating sensitivity to device noise (author-stated/inferred).
- [inferred] The experiments are limited to a 12-qubit setting and a single financial dataset (JGB rates), so scalability and generalization to larger systems or other financial instruments are untested.
- [inferred] Evaluation compares mainly to a single baseline (TwoLocal); there is limited comparison to classical generative models or broader quantum baselines.
- [inferred] Reliance on prompt fidelity and accurate hardware profiling: the approach assumes access to accurate connectivity and error-rate information and that the LLM will correctly incorporate these details into circuit designs.
- [inferred] Dependence on a single LLM configuration (GPT-4.1) — potential sensitivity to LLM model/version, temperature, and prompt engineering is not explored.
- [inferred] Use of discretization/uniform binning for continuous financial time series may introduce quantization error and limit modeling fidelity.
- [inferred] The claim of running circuits 'without requiring transpilation' depends on successful hardware-aware ansatz generation; in practice, residual transpilation or device-specific compilation steps may still be needed and could increase depth.
- [inferred] Gradient estimation via parameter-shift rules scales linearly with parameters and can become costly for larger, more parameter-rich circuits.
- [inferred] Post-selection improvements suggest that recovered outputs may rely on selecting favorable runs rather than robust end-to-end performance, raising concerns about practical throughput and reproducibility.
## Open questions
- How well do LLM-generated ansatz scale to larger qubit counts and more complex financial datasets?
- How generalizable are the generated circuits across different quantum hardware backends with different topologies and noise characteristics?
- What is the robustness of the LLM-guided iterative refinement process over long sequences of iterations, and how can invalid-output drift be prevented?
- How sensitive are results to the specific LLM choice, prompt design, and LLM hyperparameters (e.g., temperature)?
- Can the approach consistently produce circuits that require zero or minimal transpilation across a wider set of hardware devices and compiler toolchains?
- To what extent do LLM-generated ansatzes provide an advantage over classical generative models for the same financial tasks?
- How effective and scalable are the employed error mitigation and post-selection strategies in realistic, production-like deployment scenarios?
- How does the choice of training loss (MMD vs various KL formulations or other divergences) affect trainability and hardware robustness for QCBMs?
- What automated validation and verification procedures are needed to ensure the safety and correctness of LLM-generated quantum circuits?
- How does device temporal variability (calibration drift) impact the usefulness of hardware-aware prompts that encode error rates and connectivity?

**Future work:**
- Improve LLM robustness and error handling to reduce the generation of invalid or unsupported circuit components.
- Explore diverse circuit templates as prompt examples to enhance the LLM’s ability to generate unique and valid circuits.
- Develop and integrate more effective error mitigation and noise-aware training strategies to address hardware noise (implied by the need for effective EM).
## Key ideas
- #idea:hybrid-approach — Use of an LLM (GPT-4.1) to generate hardware-aware QCBM ansatzes conditioned on device connectivity, native gates and error rates, with iterative feedback loop using KL, depth and validity metrics.
- #idea:near-term-feasibility — Demonstrated end-to-end training on a 12-qubit IBM device (ibm_fez) with measurement error mitigation (Mthree) and post-selection, illustrating a NISQ-era workflow.
- #idea:quantum-advantage — LLM-generated, substantially shallower circuits (depth 28 vs baseline depth ~85) show improved generative performance on real noisy hardware (lower reverse KL on device with and without error mitigation) suggesting increased noise robustness.
- #idea:quantum-advantage — Quantitative hardware results: real-device reverse KL (no EM) LLM 7.37 ± 0.11 vs TwoLocal 9.32 ± 0.06; with EM LLM 6.91 ± 0.13 vs TwoLocal 8.92 ± 0.07.
- #idea:near-term-feasibility — Post-selection reduces KL dramatically (reported ~0.78 LLM, ~0.68 TwoLocal) indicating that classical post-processing and validity filtering can strongly affect apparent model quality on hardware.
- #idea:hybrid-approach — Training pipeline uses classical simulators for optimization (noiseless aer_simulator), classical optimizers (Adam) and parameter-shift gradients, then deploys trained circuits to hardware — a hybrid workflow.
- #idea:hybrid-approach — The LLM uses empirical metrics returned from circuit evaluations to prune/extend architectures, indicating a human-in-the-loop / automated architecture search approach driven by textual prompts.
- #limitation:noise — Authors report hardware noise as a limitation and show differing behavior between noiseless simulation and noisy hardware; measurement error mitigation and post-selection materially change results.
- #limitation:data-encoding — The approach relies on uniform quantization and binary encoding (4 qubits per maturity) which imposes representational discretization and scaling constraints.
- #limitation:qubit-count — Experiments limited to 12 qubits; scalability to larger portfolios/more maturities or higher-resolution encodings is not demonstrated and would likely require more qubits or different encodings.
- #limitation:no-empirical-validation — (partial) While hardware runs are reported, reproducibility is limited by lack of released code, exact LLM prompts and full ansatz enumerations.
## Contradictions
- The LLM-generated ansatz outperforms the TwoLocal baseline on real noisy hardware (lower reverse KL with and without error mitigation) but performs worse on noiseless simulator metrics (simulator KL: LLM 3.67 vs TwoLocal 3.10). This contradicts a simple claim of across-the-board superiority and suggests the advantage is primarily due to noise-robustness/shallowness rather than better expressivity in the idealized setting.
## Notable quotes
<!-- Researcher-added — verbatim quotes with page references -->

## Researcher notes
<!-- Researcher-added — not LLM generated -->
