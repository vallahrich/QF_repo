---
aliases:
- Implementing Quantum Generative Adversarial Network (qGAN) and QCBM in Finance
- Implementing Quantum Generative Adversarial
authors:
- Santanu Ganguly
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
journal_or_venue: IEEE conference (conference paper)
methodology_tags:
- variational-nisq
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
- method/variational-nisq
- method/quantum-ml
- method/hybrid-quantum-classical
- idea/quantum-advantage
- idea/near-term-feasibility
- idea/hybrid-approach
title: Implementing Quantum Generative Adversarial Network (qGAN) and QCBM in Finance
topic_tags:
- quantum-ml-finance
year: ''
zotero_key: ''
---

## Abstract summary
This paper implements and evaluates two quantum generative models—quantum Generative Adversarial Network (qGAN) and Quantum Circuit Born Machine (QCBM)—for financial applications using real-world Binance cryptocurrency data. Experiments were run in simulated environments (Qiskit) with a classical discriminator for qGAN and variational quantum circuits for both models; results show expected GAN loss dynamics and that QCBM (with SPSA optimization) can closely approximate target distributions, indicating potential for QML advantage in finance.
## Methodology
The study implements and compares two quantum generative modelling approaches for financial data: a Quantum Generative Adversarial Network (qGAN) and a Quantum Circuit Born Machine (QCBM). Real-world cryptocurrency time-series were fetched from the Binance API and preprocessed by removing samples below the 5th percentile and above the 95th percentile, then discretized into finite bins determined by a chosen qubit resolution per feature. The qGAN used a parametrized variational quantum circuit as the generator that prepares n-qubit output states whose basis measurement probabilities model the target distribution; the discriminator was a classical binary neural network. Training used PyTorch for data-loading/tensors and Qiskit (Aer) as the quantum back-end, with the batch size equal to the number of shots. The qGAN optimization employed an Adam optimizer and followed standard adversarial training (alternating discriminator and generator updates) for 2000 epochs with loss functions defined for the quantum setting. Fidelity between generated and target states was tracked. The QCBM was constructed as a layered parametrized circuit (five layers reported), trained to minimize a negative log-likelihood style cost (sum of -ln P_theta(x_d) over support points), and compared across classical optimizers (COBYLA, SPSA, Nelder–Mead). Circuit decompositions and layer interleaving were inspected to confirm structure. Results were analyzed via loss curves, fidelity evolution, and comparison of generated vs. empirical histograms/distributions.

**Algorithms used:** Quantum Generative Adversarial Network (qGAN), Quantum Circuit Born Machine (QCBM), Variational Quantum Circuit (parameterized ansatz), Adam optimizer, SPSA (Simultaneous Perturbation Stochastic Approximation), COBYLA, Nelder-Mead
**Frameworks:** Qiskit (IBM) 0.39, Qiskit Aer (simulator), PyTorch 2.0

**Experimental setup:** Simulated quantum experiments performed with IBM Qiskit Aer simulator (Qiskit 0.39). Quantum generator circuits implemented as parametrized variational forms; classical discriminator implemented as a neural network in PyTorch. Batch size defined number of shots. QCBM used layered parametrized circuits (5 layers) and classical optimizers for training.

**Dataset:** Real-world cryptocurrency time-series from Binance API: pairs BNBBTC, ETHBTC, LTCBTC, NEOBTC, QTUMETH; >5000 samples prior to percentile filtering.
## Experiment details
### Input
{'source': 'Binance API', 'symbols': ['BNBBTC', 'ETHBTC', 'LTCBTC', 'NEOBTC', 'QTUMETH'], 'size': 'More than 5,000 samples (per symbol)', 'preprocessing': 'Samples below 5th percentile and above 95th percentile discarded. Continuous values discretized into bins determined by qubit resolution; discretization vector used [3,3,3,3,3] (3 qubits per asset feature). Histograms produced to verify mapping.'}

### Process
1) Load Binance data and apply percentile filtering (remove <5% and >95%). 2) Discretize each feature according to chosen qubit resolution array [3,3,3,3,3], mapping continuous values to discrete basis states. 3) Build qGAN: define parametrized variational quantum generator circuit (multi-layer ansatz with single- and two-qubit gates: RX/RZ/RX sequences and pairwise controlled gates), classical discriminator NN in PyTorch. Create quantum instance on Qiskit Aer; use batch size as number of shots. 4) Train qGAN for 2000 epochs using Adam: alternate discriminator and generator updates using quantum measurement results; monitor generator and discriminator losses and fidelity evolution. 5) Build QCBM: construct layered parameterized circuit (5 layers), define cost C(theta) = - (1/d) sum_d ln(max(epsilon, P_theta(x_d))). 6) Train QCBM by minimizing cost using classical optimizers (COBYLA, SPSA, Nelder–Mead), compare optimizer performance and resulting output distributions. 7) Evaluate results by comparing generated distributions to empirical histograms and tracking loss/fidelity curves.

### Output
{'formats': ['Loss curves for generator and discriminator (qGAN)', 'Fidelity evolution between generated and training states (qGAN)', 'Histograms / empirical vs generated probability distributions (qGAN and QCBM)', 'Optimizer convergence comparisons (QCBM)'], 'metrics_reported': ['Generator loss and discriminator loss (values converging toward -ln(1/2) ≈ 0.6931 at equilibrium for qGAN)', 'Fidelity (increasing over iterations)', 'Visual/quantitative proximity of generated vs real histograms (QCBM & qGAN)'], 'baselines': 'Classical GAN behavior (theoretical equilibrium) and comparisons between classical optimizers for QCBM; no explicit classical generative-model baselines (e.g., RBM) run in this work though prior work cited.'}

### Parameters
- qgan: {'discretization_qubits_per_feature': [3, 3, 3, 3, 3], 'total_qubits': 15, 'training_epochs': 2000, 'batch_size': 1000, 'shots': 'equal to batch_size (1000)', 'optimizer': 'Adam', 'generator_ansatz_description': 'Multi-layer variational form composed of RX/RZ/RX single-qubit rotations and pairwise controlled (entangling) gates; parameter count noted as 5*n*L (5 parameters per qubit per layer).', 'discriminator': 'Classical binary neural network (PyTorch)'}
- qcbm: {'layers': 5, 'cost_function': 'C(theta) = -(1/d) sum_d ln(max(eps, P_theta(x_d)))', 'optimizers_compared': ['COBYLA', 'SPSA', 'Nelder-Mead'], 'best_reported_optimizer': 'COBYLA marginally better by objective, SPSA produced closer simulated distribution visually'}
- general: {'quantum_backend': 'Qiskit Aer (simulator)', 'software_versions': {'qiskit': '0.39', 'pytorch': '2.0'}}

### Hardware
{'simulator_name': 'Qiskit Aer', 'qpu_model': '', 'cloud_provider': 'IBM (Qiskit framework). Execution performed on simulator rather than physical QPU.'}

### Reproducibility
The paper states implementation used Qiskit 0.39 and PyTorch 2.0 and data were obtained from the Binance API, but no code repository or scripts are provided in the paper. Key hyperparameters (discretization vector, epochs, batch size, optimizers, number of QCBM layers) and framework versions are reported, which aids reproducibility, but full circuit definitions, random seeds, exact discriminator architecture, and training scripts are not included. Data access via Binance API should allow dataset reconstruction given the listed symbols and sample filtering procedure.
## Findings
- [speculative] Quantum machine learning (QML) is a promising area for finance and may deliver advantages on NISQ devices for certain applications.
- [speculative] Quantum computers are a natural fit for Monte Carlo simulations relevant to derivatives pricing and risk metrics (VaR/CVaR).
- [speculative] Quantum annealers have been found to be efficient for multi-period integer portfolio optimization (an NP-complete problem).
- [supported] The author implemented a qGAN using real Binance cryptocurrency data on an IBM Qiskit simulator (Qiskit Aer) and PyTorch.
- [supported] The qGAN discriminator and generator loss dynamics in simulation behaved as theoretically expected, approaching the Nash-like equilibrium where the discriminator output ≈ 1/2 (implying generator and discriminator losses tending toward −log(1/2) ≈ 0.6931).
- [supported] Fidelity between the qGAN generator output and target data distribution increased steadily over training iterations in the reported simulations.
- [speculative] The paper claims the qGAN produced expected results in far fewer iterations than a classical GAN would require (no direct classical baseline comparison provided).
- [supported] The author implemented a Quantum Circuit Born Machine (QCBM) for the same dataset and performed circuit decomposition and layer design verification using Qiskit.
- [supported] For the QCBM experiments, optimizer comparisons (COBYLA, SPSA, Nelder–Mead) were performed; COBYLA was reported as marginally better overall, while SPSA produced simulated distributions that appeared close to the real distribution.
- [supported] The QCBM trained with SPSA produced simulated probability distributions that were visually similar/close to the target distribution in the simulation experiments presented.
- [speculative] The paper asserts that both qGANs and QCBMs 'promise advantage' from a quantum machine learning perspective for financial data science, but provides simulation-level results without demonstrating clear empirical quantum advantage on hardware.
- [speculative] The author suggests combining QCBM with annealing may yield promising quantum advantage (cites related work), but does not present new empirical evidence for such a hybrid advantage in this paper.
- [supported] Data preprocessing choices are reported: >5000 Binance samples per asset, removal of samples below 5% and above 95% percentiles, discretization using 3 qubits per feature giving 2^5 = 32 discrete grid points for five assets, batch size 1000 and up to 2000 training epochs in simulations.

**Results summary:** The paper reports simulation implementations of a quantum GAN (qGAN) and a Quantum Circuit Born Machine (QCBM) on IBM Qiskit Aer using real Binance cryptocurrency datasets. The qGAN (quantum generator with a classical discriminator) exhibited expected adversarial loss dynamics and steadily increasing fidelity to the target distribution in the simulator experiments. The QCBM was trained to approximate the target distribution; optimizer comparisons showed COBYLA marginally outperforming others in the study, while SPSA produced simulated distributions visually close to the real data. The authors interpret these simulation results as supporting the potential of qGANs and QCBMs for financial probabilistic modeling, but they do not demonstrate empirical quantum advantage on quantum hardware or provide quantitative comparisons to classical baselines.
## Quantum advantage claim
**Classification:** speculative

The paper frequently asserts that qGANs and QCBMs 'promise' quantum advantage (particularly on NISQ devices) and cites related literature, but the results presented are simulator-based experiments without hardware demonstrations or quantitative head-to-head comparisons to classical algorithms; thus any claim of advantage remains speculative rather than demonstrated.
## Limitations
- qGANs and QCBMs are still nascent research areas with limited maturity and practical demonstrations (author-stated).
- Experiments were performed on simulators (Qiskit Aer) rather than on real quantum hardware, so effects of noise and device errors are not evaluated (author-stated).
- Data preprocessing discarded samples outside the 5th–95th percentiles to reduce qubit requirements, causing loss of tail information important for finance (author-stated).
- The data encoding used a small number of qubits per feature (e.g. 3 qubits → 32 discrete values), imposing coarse discretization and limited resolution of distributions (author-stated).
- The discriminator in the qGAN implementation is classical, so the full potential of quantum discriminators was not explored (author-stated).
- Optimization behavior is sensitive to optimizer choice (Cobyla, SPSA, Nelder-Mead) and results are inconsistent (author-stated).
- [inferred] Scalability is limited by available qubits and circuit depth on NISQ devices — increasing dimensionality or resolution will substantially increase resource requirements.
- [inferred] The study does not provide rigorous, quantitative benchmarking against classical generative models (e.g., RBMs, classical GANs) on the same tasks/datasets.
- [inferred] Potential qGAN training pathologies known in classical GANs (instability, vanishing gradients, mode collapse) remain a concern and were not deeply addressed experimentally for the quantum case.
- [inferred] The paper lacks evaluation of runtime, sample complexity, and whether the observed training speedups on simulator translate to real hardware advantage.
- [inferred] Choice of circuit ansatz, layer count and entangling connectivity effects on learned distributions are not systematically analyzed.
- [inferred] Handling of multivariate dependencies and tail-risk events in financial datasets may be inadequate given coarse discretization and percentile filtering.
## Open questions
- Can qGANs and QCBMs demonstrate a clear quantum advantage over classical generative models on realistic financial tasks when run on real NISQ hardware?
- How do device noise and gate errors on real quantum computers affect the training, fidelity and generalization of qGANs and QCBMs?
- What are the best practices for encoding continuous, heavy-tailed financial data into qubit registers without losing critical tail information?
- How do different circuit ansätze (layer depth, entangling patterns) and the number of qubits affect expressivity, trainability and scalability for multivariate financial distributions?
- Which classical or quantum optimizers (e.g., SPSA, Cobyla, gradient-based methods) are most robust and efficient for training QCBMs and qGANs in noisy, high-dimensional settings?
- How do qGANs/QCBMs compare quantitatively to classical baselines (e.g., RBMs, classical GANs, parametric models) in terms of sample quality, convergence speed, and downstream financial metrics (e.g., option pricing accuracy, VaR/CVaR)?
- Can quantum discriminators (fully quantum qGANs) offer advantages over hybrid implementations with classical discriminators?
- What are the implications of coarse discretization (limited qubits per feature) on risk-sensitive financial applications that rely on tail events?
- How can training instabilities such as mode collapse or barren plateaus be mitigated specifically in quantum generative models applied to finance?
- Is combining QCBMs with quantum annealing or hybrid annealing schemes a practical pathway to improved performance for financial risk aggregation and copula modeling?

**Future work:**
- Evaluate qGANs and QCBMs on real quantum hardware to assess noise robustness and practical feasibility (author-stated implication).
- Investigate scaling to higher-dimensional problems and higher-resolution encodings (more qubits per feature) to better capture multivariate and tail behavior (author-stated implication).
- Explore fully quantum discriminators (replace classical discriminator) and other hybrid quantum/classical architectures to determine performance trade-offs.
- Perform systematic benchmarking and quantitative comparisons against classical generative models (e.g., RBMs, classical GANs) on the same financial datasets.
- Study and optimize circuit ansätze, entangling strategies and layer counts to improve expressivity and trainability.
- Research optimizer selection and training strategies (e.g., SPSA vs. Cobyla vs. gradient-based) tailored to QCBM/qGAN training in noisy environments.
- Develop improved data encoding schemes that preserve tail events and reduce information loss from discretization.
- Investigate mitigation strategies for qGAN training pathologies (instability, vanishing gradients, mode collapse, barren plateaus).
- Explore hybrid approaches combining QCBM with annealing (as suggested by recent reports) for copula-based risk aggregation and other finance tasks.
- Extend applications beyond the uncertainty model for option pricing to broader financial engineering problems (e.g., derivatives pricing, portfolio loss distribution, credit risk).
## Key ideas
- #idea:quantum-advantage — QCBM (trained with SPSA and other classical optimizers) can closely approximate target cryptocurrency distributions in simulation, suggesting potential quantum ML benefit for generative modelling in finance.
- #idea:hybrid-approach — qGAN architecture uses a parameterized quantum generator and a classical neural-network discriminator, demonstrating a practical hybrid QPU-CPU workflow for financial data generation.
- #idea:near-term-feasibility — Implementation uses modest circuit sizes (15 qubits: 3 qubits per asset feature) and NISQ-style optimizers (SPSA, COBYLA), indicating experiments are feasible in near-term simulated/NISQ settings.
- #limitation:simulation-only — All experiments were performed on the Qiskit Aer simulator; no physical QPU results are reported.
- #limitation:no-empirical-validation — No code repository or full training scripts/seeds provided and no real-hardware validation, limiting reproducibility and empirical claims.
- #limitation:data-encoding — Continuous financial time-series are discretized into 3-qubit bins per feature; this binning/discretization may limit fidelity and does not scale easily with higher resolution.
- #limitation:qubit-count — The 15-qubit problem size used is small and likely insufficient for realistic, high-dimensional financial generative tasks without further classical/quantum scaling strategies.
## Contradictions
<!-- Step 6 output — where this paper contradicts others -->

## Notable quotes
<!-- Researcher-added — verbatim quotes with page references -->

## Researcher notes
<!-- Researcher-added — not LLM generated -->
