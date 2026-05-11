---
aliases:
- SCALING PORTFOLIO DIVERSIFICATION WITH QUANTUM CIRCUIT CUTTING TECHNIQUES
- SCALING PORTFOLIO DIVERSIFICATION QUANTUM
authors:
- Vicente P. Soloviev
- Antonio Márquez Romero
- Josh Kirsopp
- Michal Krompiec
auto_detected: true
classification: ''
contradiction_flags:
- contradiction:scalability
doi: ''
evaluation_type: simulator
evidence_type: ''
has_quantitative_results: true
idea_tags:
- idea:quantum-advantage
- idea:near-term-feasibility
- idea:hybrid-approach
journal_or_venue: arXiv preprint (arXiv:2506.08947)
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
- method/variational-nisq
- method/hybrid-quantum-classical
- method/error-mitigation
- idea/quantum-advantage
- idea/near-term-feasibility
- idea/hybrid-approach
- contradiction/scalability
title: SCALING PORTFOLIO DIVERSIFICATION WITH QUANTUM CIRCUIT CUTTING TECHNIQUES
topic_tags:
- portfolio-optimization
year: '2025'
zotero_key: ''
---

## Abstract summary
The authors introduce QuantCut, an automatic gate-cutting framework that decomposes large quantum circuits into smaller subcircuits via quasiprobability decompositions to enable execution on limited hardware. They apply QuantCut to a 71-qubit QAOA ansatz for portfolio diversification on S&P 500 assets, validating the approach on noisy Max-Cut toy simulations and a real-world financial optimization, and report that circuit cutting can facilitate larger-scale quantum computations with competitive results.
## Methodology
The authors developed QuantCut, an automatic gate-cutting framework, and applied it to QAOA instances for portfolio diversification. Their pipeline: (1) data engineering on S&P500 time series (selected 71 assets), normalize and standardize returns and compute covariance; (2) graph encoding where each asset is a node and edges are covariances thresholded at alpha=0.2 to produce a weighted graph; (3) map the diversification objective to a Max-Cut cost Hamiltonian and construct a QAOA ansatz (cost and mixer layers); (4) apply automatic gate-cutting with QuantCut: an automatic cut-finder (uses an estimation-of-distribution evolutionary procedure via EDAspy to minimize the number of 2-qubit gate cuts subject to subcircuit size limits), generate the required sub-experiments using the quasiprobability decomposition (six single-qubit experiments per two-qubit cut following Mitarai & Fujii), execute experiments on a simulator/noisy backend, and post-process to reconstruct expectation values; (5) iteratively optimize the QAOA parameters with a classical optimizer (optimizer type unspecified) using the reconstructed expectation value in each classical iteration; (6) extract solutions by sampling the final parameterized circuit and obtaining highest-amplitude bitstrings using tensor-network (MPS/tensor contraction) simulation implemented with NVIDIA cuQuantum integrated into pytket, executed on an NVIDIA A100 GPU. They validated the approach on (i) a toy Max-Cut problem (Erdos–Rényi n=10) including a simple readout noise model and varying QAOA depth p in {1,2,3} and (ii) a 71-qubit portfolio diversification proof-of-concept (p=1) using 3 gate-cuts per layer. Baselines include random sampling and a classical evolutionary algorithm (EA). Reported outputs include expectation-value convergence traces and Max-Cut / Acum(Gi) metrics.

**Algorithms used:** QAOA, circuit cutting (gate cutting, quasiprobability decomposition), estimation-of-distribution algorithm (EDA) for cut placement, evolutionary algorithm (EA) (used as baseline), Erdos–Rényi random graph generator (toy), tensor-network (MPS) contraction for state sampling
**Frameworks:** QuantCut (authors' framework), pytket, NVIDIA cuQuantum, EDAspy

**Experimental setup:** Simulations run with pytket + NVIDIA cuQuantum tensor-network backend; state sampling / tensor contractions executed on an NVIDIA A100 GPU. Noise experiments used a simple readout error model (confusion matrix [[0.99,0.01],[0.01,0.99]]). No physical QPU was reported; experiments are simulator-based (noise model or ideal).

**Dataset:** S&P 500 historical stock price dataset (Kaggle: camnugent/sandp500). 71 assets selected from the S&P500 time series covering ~5 years.
## Experiment details
### Input
{'source': 'https://www.kaggle.com/datasets/camnugent/sandp500', 'size': '71 assets selected from the S&P500 (subset of the 500 available tickers); toy experiment used n=10 (Erdos–Rényi random graph)', 'preprocessing': 'Normalize each time series to [0,1] then standardize to zero mean and unit variance; compute covariance matrix; threshold edges with alpha=0.2 (covariances below threshold removed) to form the market graph; for toy graph use Erd˝os–Rényi random generation.'}

### Process
['Data preprocessing: normalize and standardize time series; compute covariance matrix; threshold at alpha=0.2 to build weighted graph.', 'Map portfolio diversification to Max-Cut and construct QAOA cost Hamiltonian accordingly (one qubit per asset).', 'Build QAOA ansatz with p layers (cost and mixer operators); edges implemented via controlled-RZ gates (CRZ) for reduced complexity.', 'Run QuantCut automatic cut-finder once at the start (EDA-based) to determine gate cuts subject to subcircuit qubit-size constraints.', 'For each classical optimization iteration: generate sub-experiments per cut using quasiprobability decomposition (six single-qubit circuits per two-qubit cut), execute subcircuits on the designated backend (simulator/noisy model), reconstruct expectation value via post-processing, feed expectation back to classical optimizer to update parameters.', 'After optimization, extract solutions by sampling the final parameterized circuit and computing amplitudes with tensor-network (MPS) contraction via cuQuantum/pytket to obtain highest-amplitude bitstrings.', 'Compare outputs against baselines: random sampling and a classical EA.']

### Output
{'formats': 'Reconstructed expectation values per optimizer iteration (convergence traces); sampled bitstrings and associated amplitudes; numeric Max-Cut(G) and Acum(Gi) metrics.', 'metrics': ['Expectation value (QAOA cost) vs iterations', 'Max-Cut(G) value (objective from Eq.9)', 'Acum(Gi) values (sum of internal subgraph edge weights, Eq.14)'], 'baselines': ['Random sampling (with reported mean ± std)', 'Classical evolutionary algorithm (EA)'], 'representations': 'Convergence plots and tabulated numeric comparisons (e.g., Max-Cut and Acum(Gi) for Random, QAOA p=1, and EA).'}

### Parameters
- main_problem_qubits: 71
- toy_problem_qubits: 10
- qaoa_layers_tested_toy: [1, 2, 3]
- qaoa_layers_main: 1
- gate_cuts_per_layer_toy: 1
- gate_cuts_per_layer_main: 3
- covariance_threshold_alpha: 0.2
- noise_model_readout_matrix: [[0.99, 0.01], [0.01, 0.99]]
- backend_for_tensor_simulation: pytket + NVIDIA cuQuantum (tensor-network / MPS)
- tensor_hardware: NVIDIA A100 GPU
- optimizer: classical optimizer (unspecified); baseline EA used (unspecified implementation)
- iterations_reported: toy: up to ~30 iterations in plots; 71-qubit: ~16 optimization steps shown
- shots: None
- random_seed: None

### Hardware
{'simulator': 'pytket with NVIDIA cuQuantum tensor-network backend', 'gpu': 'NVIDIA A100 (single GPU used for tensor contractions / sampling)', 'qpu': None, 'cloud_provider': None}

### Reproducibility
Dataset is publicly available (Kaggle link provided). The authors describe QuantCut and implementation components (pytket, cuQuantum, EDAspy) but do not provide a public code repository or experiment scripts in the preprint. Key execution details missing for full reproducibility: exact classical optimizer type and hyperparameters, number of shots per sub-experiment, random seeds, and the QuantCut code/parameters (beyond conceptual description). Reproducing results is possible in principle given the dataset and the described methods, but would require reimplementation of QuantCut and parameter tuning.
## Findings
- [supported] The authors developed QuantCut, an automatic framework for gate-based circuit cutting that (a) finds gate cuts given a maximum subcircuit size, (b) generates and runs the required sub-experiments, and (c) reconstructs expectation values and (limited-size) state vectors.
- [speculative] QuantCut is the first publicly disclosed implementation of an automatic algorithm that finds optimal gate cuts based on qubit connectivity (claim of novelty: 'to the best of our knowledge').
- [supported] QuantCut was used to evaluate a 71-qubit QAOA ansatz for a portfolio-diversification (Max-Cut) encoding by performing circuit cutting across iterations of the optimizer.
- [supported] In a 10-qubit noisy Max-Cut toy simulation (readout error model P(0|1)=P(1|0)=0.01), circuit cutting produced better convergence than the uncut circuit for p>=2 QAOA layers, while for p=1 the uncut circuit converged better in that specific noise model and setup.
- [supported] For the 71-qubit portfolio-diversification instance (p=1, three gate-cuts per layer), QAOA with QuantCut produced a Max-Cut objective value (43.41) substantially better than random sampling (26.1 ± 2.1) but worse than a classical evolutionary algorithm (46.51).
- [speculative] The authors suggest circuit cutting can act as an error-mitigation / noise-resilience strategy (they report simulation evidence in a limited toy model and generalize the possibility).
- [speculative] QuantCut can be integrated into distributed quantum computing workflows and scale large-circuit evaluation by trading quantum width for classical postprocessing (general proposition based on circuit cutting principles).
- [speculative] Increasing QAOA depth (p) is expected to improve QAOA+QuantCut performance and potentially close the gap with classical solvers (stated as future work and extrapolation).
- [speculative] Reconstructing full state vectors via QuantCut is possible in principle but practically limited by exponential classical memory; expectation-value reconstruction scales better (implementation caveat).
- [speculative] The number of required experiments and classical postprocessing grows exponentially with the number of cuts (stated as a limitation and consistent with prior literature).

**Results summary:** The paper introduces QuantCut, an automated gate-cutting tool that finds gate-cut placements, generates the required single-qubit sub-experiments, and reconstructs expectation values (and small state vectors). In simulation studies the authors show (a) in a 10-qubit noisy Max-Cut toy example circuit cutting yields improved optimizer convergence for p>=2 layers though for p=1 cutting was worse in that noise model, and (b) for a 71-qubit QAOA portfolio-diversification mapping (p=1, three cuts per layer) QuantCut-enabled simulation produced a Max-Cut value (43.41) substantially better than random sampling but not as good as a classical evolutionary algorithm (46.51). The implementation uses pytket, NVIDIA cuQuantum tensor-network simulation on an A100, and an evolutionary optimizer (EDAspy) for cut placement. The authors emphasize practical limits: exponential overhead with cuts and classical memory limits for full state reconstruction.

**Performance claims:**
- 71 qubits: QAOA (p=1) with QuantCut produced Max-Cut(G) = 43.41 on the reported S&P500-derived 71-node instance.
- Random sampling baseline: Max-Cut(G) = 26.1 ± 2.1 (mean ± std) on same instance.
- Classical evolutionary algorithm (EA) baseline: Max-Cut(G) = 46.51 on same instance.
- Acum(G0) / Acum(G1) (sub-portfolio internal-edge sums) — Random sampling: 15.2 ± 5.0 and 7.9 ± 7.1; QAOA (p=1): 2.439 and 4.113; EA: 1.190 and 2.110.
- Toy-model (n=10) noisy readout model used: P(0|0)=0.99, P(0|1)=0.01, P(1|0)=0.01, P(1|1)=0.99.
- Circuit-cutting experiments in the toy model used one gate cut per layer; 71-qubit experiments used three gate cuts per layer.
- Tensor-network based sampling and amplitude extraction implemented using NVIDIA cuQuantum integrated into pytket and executed on an NVIDIA A100 GPU.
## Quantum advantage claim
**Classification:** not-applicable

The paper does not demonstrate quantum computational advantage. Results are simulations (tensor-network/cuQuantum) of QAOA with circuit cutting; QAOA (p=1) outperformed random sampling on the instance but was outperformed by a classical evolutionary optimizer. No empirical demonstration of advantage over classical methods or on quantum hardware is provided.
## Limitations
- Circuit-cutting overhead scales exponentially with the number of cuts (post-processing and experiment-count blowup).
- Reconstructing full state vectors is limited to small qubit counts due to exponential memory/storage cost.
- Results are based on simulations (tensor-network and noise-model simulations); no demonstrated 71-qubit runs on physical QPUs in this work.
- The 71-qubit QAOA experiment used only p = 1 layer; low-depth ansatz limited solution quality (classical EA outperformed QAOA p = 1).
- The mapping used one asset per qubit; multi-asset-per-qubit encodings were not implemented (out of scope).
- Only a limited noise model was studied in the toy example (simple readout error model); robustness under diverse and realistic noise channels is unexplored.
- [inferred] The automatic cut-finder is implemented with an estimation-of-distribution / evolutionary approach (EDASpy); this may be computationally intensive and could yield suboptimal partitions for very large circuits.
- [inferred] Cuts are determined only once (automatic cut finder run on the first iteration) and then held fixed during optimization, potentially missing better dynamic re-partitionings as parameters evolve.
- [inferred] Use of CRZ gates instead of CX for edges (to reduce experiment complexity) is a design choice whose effect on solution fidelity and mapping generality was not fully characterized.
- [inferred] Tensor-network (MPS) based sampling assumes favourable circuit structure (e.g., limited entanglement / nearest-neighbour interactions); circuits requiring many SWAPs or with high entanglement may be hard to simulate efficiently.
- [inferred] The graph threshold α (used to sparsify correlations) was chosen empirically (α = 0.2); sensitivity of results to this threshold selection was not explored.
## Open questions
- How does QuantCut (gate-cutting) perform on real quantum hardware (with full device noise, crosstalk, and gate errors) compared to simulations?
- How does the approach scale as the number of QAOA layers p increases for large instances (e.g., will QAOA with higher p match or exceed classical EA performance)?
- What are practical limits on the number of cuts that can be applied before circuit-cutting overhead makes the approach infeasible for real tasks?
- Can the automatic cut-finder be improved (in speed or optimality) or replaced with algorithms that give provable guarantees for very large circuits?
- What is the impact of different problem encodings (e.g., mapping multiple assets per qubit) on solution quality and resource requirements when combined with circuit cutting?
- How sensitive are the diversification results to the choice of correlation/covariance threshold (α) used to construct the market graph?
- How effective is circuit cutting as an error-mitigation strategy across varied, realistic noise channels (coherent noise, amplitude damping, crosstalk) beyond the simple readout model used here?
- What are the best strategies to reduce the classical post-processing and sampling cost (quasiprobability reconstruction) associated with gate cuts?
- Can state reconstruction or sampling be scaled beyond current tensor-network limits (e.g., via approximate contractions, distributed simulation) while preserving useful solution fidelity?
- How can QuantCut be integrated into distributed quantum computing workflows in practice, and what are the communication and orchestration trade-offs?

**Future work:**
- Apply other problem mappings that allow assigning more than one asset per qubit.
- Increase the number of layers in the QAOA ansatz (study performance for larger p).
- Analyze the performance of the approach and resilience of circuit cutting under different types of quantum noise.
## Key ideas
- #idea:quantum-advantage — QuantCut decomposes a 71-qubit QAOA circuit via quasiprobability gate cutting and reports competitive Max-Cut/objective metrics versus random sampling and a classical EA baseline.
- #idea:near-term-feasibility — Circuit cutting + classical optimization + tensor-network sampling is proposed as a NISQ-era pathway to run larger logical circuits; demonstrated in simulation for p=1 on a 71-qubit portfolio instance.
- #idea:hybrid-approach — The pipeline is hybrid: an EDA-based automatic cut-finder determines cuts, subcircuits are executed on a (noisy) simulator, classical optimizers ingest reconstructed expectations, and final sampling uses MPS/cuQuantum on a GPU.
- #limitation:simulation-only — All experiments are simulator-based (tensor-network on NVIDIA A100) with no execution on an actual QPU.
- #limitation:noise — Noise evaluation is limited to a simple readout confusion-matrix model; realistic gate-level noise and the full cost of quasiprobability sampling under noise are not assessed.
- #limitation:qubit-count — The method is motivated by limited qubit hardware and relies on cutting to emulate larger circuits, which incurs overhead; demonstrated only at low circuit depth (p=1) for the real-world instance.
- #limitation:no-empirical-validation — Key reproducibility details (QuantCut code, optimizer type/hyperparameters, shots, seeds) are not provided, hindering independent validation.
## Contradictions
- contradiction:scalability — The paper claims QuantCut can facilitate larger-scale quantum computations, but the evidence is limited to simulator-based demonstrations at QAOA depth p=1 with a simplistic noise model; the quasiprobability overhead and untested gate/noise accumulation leave scalability to real noisy QPUs unproven.
## Notable quotes
<!-- Researcher-added — verbatim quotes with page references -->

## Researcher notes
<!-- Researcher-added — not LLM generated -->
