---
aliases:
- Quadratic Unconstrained Binary Optimization Approach for Incorporating Solvency
  Capital into Portfolio Optimization
- Quadratic Unconstrained Binary Optimization
authors:
- Ivica Turkalj
- Mohammad Assadsolimani
- Markus Braun
- Pascal Halffmann
- Niklas Hegemann
- Sven Kerstan
- Janik Maciejewski
- Shivam Sharma
- Yuanheng Zhou
auto_detected: true
classification: ''
contradiction_flags: []
doi: 10.3390/risks12020023
evaluation_type: simulator
evidence_type: ''
has_quantitative_results: true
idea_tags:
- idea:near-term-feasibility
- idea:hybrid-approach
journal_or_venue: Risks
methodology_tags:
- quantum-annealing-qubo
- hybrid-quantum-classical
paper_type: ''
quantum_advantage_claim: theoretical
related_papers: []
relevance_phase1: high
relevance_phase3: high
source_type: peer-reviewed-empirical
source_type_confidence: high
step1_date: '2026-04-14T12:30:17.873688'
step1_model: gpt-5-mini
step2_date: '2026-04-14T12:30:17.873688'
step2_model: gpt-5-mini
step3_date: '2026-04-14T12:30:17.873688'
step3_model: gpt-5-mini
step4_date: '2026-04-14T12:30:17.873688'
step4_model: gpt-5-mini
step5_date: '2026-04-14T12:30:17.873688'
step5_model: gpt-5-mini
step6_date: '2026-04-14T12:30:17.873688'
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
- topic/risk-management
- topic/insurance-actuarial
- method/quantum-annealing-qubo
- method/hybrid-quantum-classical
- idea/near-term-feasibility
- idea/hybrid-approach
title: Quadratic Unconstrained Binary Optimization Approach for Incorporating Solvency
  Capital into Portfolio Optimization
topic_tags:
- portfolio-optimization
- risk-management
- insurance-actuarial
year: '2024'
zotero_key: ''
---

## Abstract summary
The paper develops a quadratic proxy model to incorporate the Solvency Capital Requirement (SCR) into portfolio optimization by approximating the (non‑quadratic) SCR via least-squares regression and formulating the resulting problem as a quadratic unconstrained binary optimization (QUBO). The authors describe discretization and penalty techniques to map continuous portfolio weights to binary variables for future quantum (annealing or gate-based) solution methods, and evaluate the approach on a 26-asset insurance dataset, reporting high Pareto-front approximation quality.
## Methodology
The authors propose a pipeline to incorporate the Solvency Capital Requirement (SCR) into portfolio optimization by (1) approximating the SCR (computed via the Solvency II standard formula) with a quadratic proxy using least-squares regression, (2) translating the entire portfolio optimization (return, variance, approximated SCR) into a quadratic unconstrained binary optimization (QUBO) formulation by discretizing continuous portfolio weights into binary variables, and (3) solving the resulting QUBOs with classical heuristic solvers (simulated annealing) as a proxy for future quantum/quantum-inspired hardware. The SCR proxy is learned from labeled samples (portfolio weight vectors and corresponding SCR values) using a quadratic basis consisting of all xi xj monomials, linear xi terms and a constant; coefficients are estimated via general least-squares optimized by gradient descent in PyTorch. Continuous-to-binary encoding uses an m-bit fixed-point representation per asset (vector v of binary place weights); quadratic terms are mapped to a QUBO matrix using Kronecker products. The budget equality constraint (weights sum to 1) is handled by adding a quadratic penalty term with penalty factor λP to make the problem unconstrained. For multi-objective Pareto frontier exploration the weighted-sum scalarization is applied over a grid of weight vectors λ; for each λ the continuous baseline is solved with SciPy and the discretized QUBO is optimized with D-Wave Ocean's simulated annealer 'neal'. Performance is evaluated by (i) regression training/validation MSE, (ii) visual scatterplots of true vs. approximated SCR, and (iii) multi-objective indicators comparing continuous and QUBO solutions — specifically the hypervolume indicator (relative to the Nadir point) and a worst-case approximation factor APX over weight vectors.

**Algorithms used:** Least-squares regression (quadratic basis), Gradient descent (PyTorch) for regression, Weighted-sum scalarization for multi-objective optimization, QUBO formulation (quadratic objective, binary variables), Simulated annealing (D-Wave Ocean 'neal'), Classical continuous optimization (SciPy)
**Frameworks:** PyTorch, SciPy, D-Wave Ocean (neal simulated annealer), pymoo (hypervolume computation), pygrnd (GitHub repository referenced)

**Experimental setup:** No quantum hardware was used. The QUBOs were solved using D-Wave Ocean's classical simulated annealer 'neal' (annealingSamples=200, annealingTime=100). The SCR proxy was trained with PyTorch using gradient descent for 100 epochs. Continuous baselines were solved with SciPy. Experiments were implemented in Python 3.11. Discretization resolution m was used (m=2 for reported QUBO experiments), and the budget-penalty factor λP was set to 15. The multi-objective weights λ were enumerated on a grid with entries {0, 0.05, 0.10, ..., 1} constrained to sum to 1.

**Dataset:** An anonymized, real-world insurance asset dataset consisting of 26 asset classes (clusters of many underlying assets). For each class the expected return vector µ, variances, and the full covariance/correlation matrix were provided. SCR labels were computed per portfolio using a company-internal tool implementing the Solvency II standard formula (company-specific parameters plus regulator calibrations).
## Experiment details
### Input
{'source': 'Proprietary insurance company data (26 anonymized asset classes) and a company tool implementing the Solvency II standard formula', 'size': 'Generated 60,000 portfolio examples total: 40,000 training points and 20,000 validation points', 'preprocessing': "Each portfolio weight vector was generated by sampling 26 independent uniform(0,1) values and normalizing to sum to 1. For each sampled weight vector, the SCR (f3) was computed using the insurer's standard-formula tool. Regression basis included all quadratic monomials xi*xj, linear xi, and a constant."}

### Process
{'steps': ['Generate portfolio weight samples: sample 26 i.i.d. U(0,1) values and normalize to sum=1 to create wl.', "Compute target SCR values ul = f3(wl) for each sample using the insurer's standard-formula tool.", 'Form regression dataset D = {(wl, ul)} with 40k train / 20k validation points.', 'Define quadratic basis functions: all xi*xj (n^2), xi (n) and constant (1).', 'Estimate quadratic proxy f3,approx(x) = x^T P x + b^T x + c by minimizing mean squared error via gradient descent in PyTorch (100 epochs).', 'Construct QUBO: discretize each xi with m bits (fixed-point vector v), replace x by T(y) and map quadratic form to QUBO matrix using Kronecker products; add linear budget constraint penalty λP*(sum xi - 1) as quadratic penalty.', 'Enumerate multi-objective weight vectors λ on a simplex grid (λi ∈ {0,0.05,...,1}, sum=1).', "For each λ: (a) solve continuous quadratic constrained problem with SciPy to obtain baseline Pareto points; (b) solve the discretized QUBO with D-Wave Ocean's 'neal' (annealingSamples=200, annealingTime=100) using resolution m (m=2 in reported experiments).", 'Collect QUBO solutions, compute objective images (f1,f2,f3), and evaluate performance vs. continuous baseline using hypervolume and APX metrics.'], 'parameters_and_iterations': {'regression_epochs': 100, 'training_size': 40000, 'validation_size': 20000, 'discretization_resolution_m': 2, 'penalty_lambdaP': 15, 'lambda_grid': 'λi ∈ {0, 0.05, 0.1, ..., 0.95, 1}, with sum(λ)=1', 'neal_parameters': {'annealingSamples': 200, 'annealingTime': 100}}}

### Output
{'formats': ['Regression training and validation mean squared error (numeric scalar per epoch)', 'Scatter plot of f3(w) vs f3,approx(w)', 'Sets of portfolio decisions (binary vectors) and corresponding objective triples (f1,f2,f3)', 'Pareto frontier approximations (continuous baseline and QUBO-derived points)'], 'metrics': ['Training and validation MSE', 'Hypervolume indicator (relative to Nadir point) comparing QUBO set to continuous Pareto set', 'Approximation factor APX (worst-case ratio of weighted-sum objective values between QUBO solutions and continuous optimum over all λ)', 'Additional descriptive statistics: percentage of weight vectors with APX ≤ 1.01'], 'baselines': 'Continuous constrained optimization solutions obtained via SciPy for the weighted-sum problems.'}

### Parameters
- regression: {'method': 'least-squares (quadratic basis)', 'optimizer': 'gradient descent (PyTorch)', 'epochs': 100}
- data: {'train_samples': 40000, 'validation_samples': 20000, 'num_assets': 26}
- discretization: {'resolution_m': 2, 'fixed_point_vector_v': '2^{m-1}-based weighting as described'}
- QUBO_and_solver: {'penalty_lambdaP': 15, 'weight_grid_step': 0.05, 'neal_annealingSamples': 200, 'neal_annealingTime': 100}

### Hardware
{'simulator': "D-Wave Ocean 'neal' (classical simulated annealer)", 'QPU_model': None, 'cloud_provider': None, 'other_runtime': 'PyTorch and SciPy executed under Python 3.11 on classical hardware (unspecified CPU/GPU)'}

### Reproducibility
Code implementing key parts of the pipeline is referenced (pygrnd GitHub repository: https://github.com/JoSQUANTUM/pygrnd). The proprietary asset dataset and the insurer's SCR-computation tool are not publicly available; data are available from the corresponding author on request but are private due to confidentiality. Exact hardware specs for classical runs are not specified. All solver parameters used (regression epochs, annealer parameters, discretization resolution, penalty factor, λ-grid) are reported in the paper, enabling approximate reproduction on classical solvers.
## Findings
- [supported] A quadratic proxy model for the Solvency Capital Requirement (SCR) can be learned via least-squares regression from simulated portfolio–SCR pairs (training set 40,000, validation 20,000) with low training and validation MSE.
- [supported] The learned quadratic SCR approximation (xtPx + btx + c) can be integrated with classical return and variance objectives to form a single quadratic objective suitable for QUBO encoding.
- [supported] Continuous portfolio weights can be discretized into binary variables via fixed-bit encoding (resolution m) and mapped into a QUBO using Kronecker-product structure; this was implemented and tested.
- [supported] Converting the budget equality constraint into a penalty term (λP = 15 used in experiments) yields a quadratic unconstrained binary optimization (QUBO) whose solutions approximate constrained solutions.
- [supported] Experimental tests (n = 26 asset classes) using classical optimizers and D-Wave's simulated annealer (neal) on the QUBO with resolution m = 2 produced Pareto-front approximations close to the continuous constrained solution (hypervolume 0.9883).
- [supported] Quantitative performance measures from experiments: overall approximation factor APX = 1.2179; for 95% of weight vectors the approximation factor ≤ 1.01.
- [supported] The produced quadratic SCR proxy is not guaranteed to be convex (and empirically need not be), so the resulting optimization can be non-convex.
- [supported] For the dataset and standard-formula SCR implementation used, regression training converged rapidly (reported training/validation MSE decreasing to ~4e-7/5e-7 after 100 epochs).
- [supported] The authors provide code and used established tooling (PyTorch, SciPy, D-Wave Ocean 'neal' sampler) to implement training and QUBO solution pipelines.
- [supported] The authors report practical limitations mapping their QUBO to current D-Wave hardware due to large QUBO matrix bandwidth, preventing direct hardware runs.
- [speculative] The QUBO formulation could benefit from quantum annealing or gate-based algorithms (e.g., QAOA) on future, more capable quantum hardware, potentially yielding speedups over classical methods.
- [speculative] Extending proxy-approximation-by-regression to other regulatory or accounting objectives (IFRS metrics, valuation reserves) and/or using higher-order polynomial proxies could be promising future directions.
- [speculative] The main methodological contribution is the demonstration that machine-learning-derived quadratic proxies enable end-to-end QUBO formulation for portfolio optimization including SCR.

**Results summary:** The paper proposes and implements a pipeline that (1) learns a quadratic proxy for the Solvency Capital Requirement (SCR) via least-squares regression, (2) integrates that proxy with mean–variance objectives, (3) discretizes weights into binary variables, and (4) encodes the resulting problem as a QUBO by adding a budget-penalty term. On a real-world-inspired use case with 26 asset classes and large training/validation samples (40k/20k), the quadratic proxy fit the SCR data with very low MSE, and solving the QUBOs (using a simulated annealer) with a coarse resolution (m=2) produced Pareto-front approximations close to continuous constrained solutions (hypervolume 0.9883). The authors note current limits in mapping their QUBOs to present D-Wave hardware and frame practical quantum advantage as a future possibility rather than an achieved outcome.

**Performance claims:**
- Training dataset size: 40,000 samples; validation: 20,000 samples.
- Regression training converged to low errors: example reported training MSE ≈ 4e-7 and validation MSE ≈ 5e-7 after 100 epochs (table shows rapid decrease).
- Discretization resolution used in experiments: m = 2 bits per asset weight.
- Penalty factor for budget equality used: λP = 15.
- Hypervolume indicator comparing QUBO solutions to continuous constrained solutions: 0.9883 (i.e., QUBO covered ≈98.83% of dominated hypervolume).
- Overall approximation factor APX = 1.2179 (worst-case over tested weight vectors); for 95% of weight vectors, approximation factor ≤ 1.01.
- Weight grid for scalarization: λi ∈ {0, 0.05, 0.1, ..., 1} with λ1+λ2+λ3=1.
## Quantum advantage claim
**Classification:** theoretical

The authors argue that casting the problem as a QUBO enables use of quantum annealing or QAOA and cite potential future speedups, but they do not demonstrate empirical quantum advantage on quantum hardware; experiments used classical optimizers and a classical simulated-annealing sampler (D-Wave 'neal'). Claims of quantum speedup are therefore speculative/theoretical pending future hardware advances.
## Limitations
- The SCR objective f3 is approximated by the Solvency II standard formula rather than computed from the full loss distribution (author-stated).
- The quadratic surrogate f3,approx obtained by regression is not necessarily convex and therefore does not remove the intrinsic non-convexity of the optimization problem (author-stated).
- Discretization of continuous portfolio weights (binary encoding) reduces accuracy; approximation accuracy depends on the chosen resolution m (author-stated).
- The linear budget constraint is enforced via a penalty term, which only enforces the constraint approximately; solutions depend on the penalty factor λP and require careful tuning (author-stated).
- Current quantum annealing hardware (e.g., D-Wave) is not well suited for the authors' QUBO matrices due to large bandwidth; mapping inefficiencies limit practical hardware execution today (author-stated).
- Experiments used simulated annealing (D-Wave’s neal) rather than execution on quantum hardware — results do not demonstrate real quantum speedup (author-stated/inferred).
- Training and validation used randomly sampled normalized portfolios (40k train / 20k validation); performance relies on representativeness of those samples and the company-specific parameters used (author-stated/inferred).
- The reported approximation factor APX has a worst-case value ≈1.2179 (though 95% of weights give APX ≤ 1.01), indicating some weight vectors produce materially worse approximations (author-stated).
- The approach assumes own funds (o f) are a constant in the SCR ratio formulation, which may oversimplify in some settings (author-stated/inferred).
- Scalability to higher resolution (larger m) or to substantially more assets will require many more qubits and connectivity, posing practical limits with current hardware (inferred).
- The quadratic regression surrogate (least squares) may miss complex nonlinearities vs. more expressive ML models (e.g., neural networks); choice of model limits fidelity of the proxy (inferred).
- Data and company-specific parameters are confidential and not publicly available, limiting reproducibility and generalizability checks (author-stated).
## Open questions
- Can the proposed QUBO formulation deliver a practical advantage (speed or solution quality) on real quantum annealers or future gate-based quantum hardware?
- How should the discretization resolution m and penalty factor λP be chosen/tuned optimally for a given hardware constraint and accuracy target?
- How robust is the quadratic proxy f3,approx across different market regimes, scenarios, or companies with different balance-sheet structures and regulator-calibrated parameters?
- To what extent does the weighted-sum scalarization (used to recover the Pareto frontier) miss unsupported Pareto-optimal solutions given the non-convexity introduced by f3,approx?
- Would higher-degree polynomial surrogates (beyond quadratic) materially improve approximation of SCR and justify the additional complexity for quantum or classical solvers?
- How does the method scale (solution quality and computational resources) when increasing asset class dimensionality or when using finer resolution (larger m)?
- What are the trade-offs between different regression/modeling choices (least squares vs. neural networks or other ML methods) for building the SCR proxy in terms of approximation accuracy and QUBO representability?
- How sensitive are results to the sampling strategy for generating training portfolios, and what sampling schemes ensure robust generalization?
- Can the approach be extended to approximate SCR computed directly from nested simulations or full loss-distribution methods (not just the standard formula)?
- How do classical heuristics and solvers compare with the proposed QUBO-based method in runtime and solution quality on equivalent computational budgets?

**Future work:**
- Consideration of further economically relevant objective functions, such as key figures from the IFRS balance sheet or valuation reserves (author-stated).
- Expanding focus beyond QUBOs by allowing higher-degree polynomial approximations (author-stated).
- Applying the formulation on future generations of quantum annealing hardware or on fault-tolerant gate-based quantum computers (author-stated/implied).
- Exploring alternative or more expressive proxy models (e.g., neural networks) for SCR and studying their suitability for QUBO or other quantum-friendly encodings (inferred).
- Investigating methods beyond the weighted-sum scalarization to better capture unsupported Pareto-optimal points in the non-convex multi-objective landscape (inferred).
- Studying scalability and hardware mapping strategies to handle larger numbers of assets and higher-resolution encodings (inferred).
- Empirical comparison with classical optimization and heuristic methods to quantify potential quantum advantage in this application (inferred).
## Key ideas
- #idea:hybrid-approach — Use classical regression (least-squares quadratic proxy) to approximate the Solvency Capital Requirement (SCR) and convert the full portfolio problem into a QUBO via discretization, enabling future solution on quantum annealers or gate-based QPUs while keeping heavy preprocessing classical.
- #idea:near-term-feasibility — Demonstrates pipeline end-to-end on real insurance data (26 asset classes, 60k samples) and small-resolution discretization (m=2), showing high Pareto-front approximation quality versus continuous baselines when solved with a classical simulated annealer (neal).
- #idea:hybrid-approach — Multi-objective Pareto exploration performed via weighted-sum scalarization; continuous baselines solved with SciPy and discretized QUBOs solved with D-Wave Ocean's simulated annealer to evaluate approximation loss from discretization and QUBO encoding.
- #limitation:simulation-only — No quantum hardware experiments; all QUBOs solved with a classical simulated annealer (D-Wave Ocean 'neal'), so results do not demonstrate performance on actual QPUs.
- #limitation:no-empirical-validation — The quantum-side claim is prospective: mapping to QUBO is validated classically, but there is no empirical validation on quantum annealers or gate-model hardware.
- #limitation:data-encoding — Discretization (fixed-point m-bit encoding) and Kronecker-product mapping are used; the paper highlights encoding design choices (resolution m, penalty lambdaP) that impact solution quality and problem size.
- #limitation:qubit-count — Practical deployment would require many binary variables (one per bit per asset and quadratic interactions), and experiments use low resolution (m=2), implicitly reflecting qubit-count/scaling limitations for near-term hardware.
## Contradictions
<!-- Step 6 output — where this paper contradicts others -->

## Notable quotes
<!-- Researcher-added — verbatim quotes with page references -->

## Researcher notes
<!-- Researcher-added — not LLM generated -->
