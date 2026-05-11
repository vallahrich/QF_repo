<!-- chapter-supporting-literature reading note
     paper_id:        e6ece474516c
     selection_id:    C-05
     source_text:     shared/extracted_text/text/e6ece474516c_warm_starting_quantum_optimization.md
     generated_at:    2026-05-03T10:01:21.649880+00:00
     model:           gpt-5-mini
     temperature:     0.2
     prompt_version:  1.0 (2026-05-03)
     prompt_sha:      72a0945464a5
     rendered_sha:    e2599843919e
     status:          PENDING researcher review
     accept by:       moving this file to ../<paper_id>__<slug>.md -->

> ⛔ **EXCLUSION FLAG (researcher discretion, 2026-05-03)**: This note is **TOO DETAILED** for the Background chapter scope. The substantive content (warm-start mixer Hamiltonian construction, R_Y rotation parameters, regularisation ε, rounded warm-starts, recursive QAOA) is below the level of abstraction the chapter operates at.
>
> **Action**: Do NOT use this note as a source for Chapter 1 or Chapter 2 prose. Only the conceptual framing remains in scope: "warm-starting QAOA from the solution of a classical relaxation"; the inheritance of classical approximation guarantees (Goemans–Williamson) by the quantum algorithm; and the Unique-Games-Conjecture limit ("even quantum cannot beat the GW bound under standard hardness conjectures") expressed in plain language.
>
> **Retain** the full extraction for possible reuse in Ch.4 / Ch.7.

# Warm-starting quantum optimization (2021)

**Authors**: Daniel J. Egger, Jakub Mareček, Stefan Woerner  
**Venue**: arXiv preprint (quant-ph)  
**DOI**: n/a  
**Suggested chapter sections**: §1.2 Motivation for quantum heuristics; §2.1 QUBO & relaxations; §2.2 QAOA and warm-start variants; §2.3 Randomized rounding & GW; §2.4 Performance guarantees & limits

## 1-paragraph summary
This paper proposes and analyzes "warm-start" strategies for quantum optimization (primarily QAOA) that initialize the quantum state from solutions of continuous relaxations (QP or SDP) or from randomized-rounding outputs (e.g., Goemans–Williamson). It defines modified initial states and mixer Hamiltonians (WS-QAOA), introduces rounded warm-starts and a WS-RQAOA recursive scheme, and presents numerical simulations (portfolio optimization, MAXCUT) showing improvements at low circuit depth. The work connects warm-start constructions to classical approximation guarantees (GW ratio) and discusses limitations under the Unique Games Conjecture and practical trade-offs for near-term hardware.

## Key concepts (with location)
- **Warm-start QAOA (WS-QAOA)** — 2.2 Continuous warm-start QAOA — "The solutions of either continuous-valued relaxation (QP or SDP) can be used to initialize quantum-classical hybrid algorithms, which is known as warm-starting them [69]. In particular, we focus on warm-starting QAOA."
- **Initial state |φ∗⟩ from relaxation c∗** — 2.2 Continuous warm-start QAOA — "In the simplest variant of WS-QAOA, we replace the initial equal superposition state |+⟩⊗n with a state |φ∗⟩= ⊗_{i=0}^{n−1} ˆRY(θi) |0⟩^n , (1) which corresponds to the solution c∗ of the relaxed Problem (QP)."
- **Mapping binary ↔ qubit** — 2.2 Continuous warm-start QAOA — "In QAOA, each decision variable xi of the discrete optimization problem corresponds to a qubit by the relation xi = (1 −zi)/2."
- **Warm-start mixer ˆH(ws)_M** — 2.2 Continuous warm-start QAOA — "We also replace the mixer Hamiltonian ˆHM = −∑_{i=0}^{n−1} ˆXi with ˆH(ws)_M = ∑_{i=0}^{n−1} ˆH(ws)_{M,i} where ˆH(ws)_{M,i} = [ 2c∗_i −1  −2√{c∗_i(1−c∗_i)};  −2√{c∗_i(1−c∗_i)}  1−2c∗_i ] (2) and has ˆRY(θi) |0⟩ as ground state with eigenvalue of −1."
- **Regularization parameter ε linking WS-QAOA and standard QAOA** — 2.2 Continuous warm-start QAOA — "The parameter ε provides a continuous mapping between WS-QAOA and standard QAOA since at ε = 0.5 the initial state is the equal superposition state and the mixer Hamiltonian is the X operator."
- **Rounded warm-start (GW rounding)** — 2.3 Rounded warm-start QAOA — "Two notable examples are the random-hyperplane rounding of SDP relaxations for MAXCUT [53], see Appendix B, and iterative rounding of SDP relaxations for a wider variety of problems, see Appendix D."
- **Warm-start RQAOA (WS-RQAOA)** — 2.3 Rounded warm-start QAOA — "Rounding in the classical pre-processing readily leads to the warm-started recursive QAOA (WS-RQAOA), illustrated in Fig. 3 and demonstrated in Sec. 4."
- **Goemans–Williamson approximation constant** — Introduction (and Appendix B) — "the celebrated Goemans-Williamson (GW) random hyperplane rounding [53, 54] for MAXCUT finds cuts whose expected value is an α fraction of the global optimum, for 0.87856 < α < 0.87857, with the expectation over the randomization in the rounding procedure."

## Quotable claims (with location)
- Abstract — "Here, we discuss how to warm-start quantum optimization with an initial state corresponding to the solution of a relaxation of a combinatorial optimization problem and how to analyze properties of the associated quantum algorithms." — *useful for: §1.2 Motivation / §2.2 Warm-start definition*
- 1 Introduction — "The quantum approximate optimization algorithm (QAOA) [16–18], inspired by a Trotterization of adiabatic quantum computing [19–21], runs on gate-based quantum computers [22, 23]. This algorithm encodes a combinatorial optimization problem in a Hamiltonian ˆHC whose ground state is the optimum solution." — *useful for: §2.1 Background on QAOA*
- 1 Introduction — "This algorithm has lacked theoretical guarantees on its performance ratio and for certain problem instances of MAXCUT it cannot, with constant depth, outperform the classical Goemans-Williamson randomized rounding approximation [24, 25]." — *useful for: §2.4 Limits of QAOA guarantees*
- 2.2 Continuous warm-start QAOA — "Each decision variable xi of the discrete optimization problem corresponds to a qubit by the relation xi = (1 −zi)/2." — *useful for: §2.2 QUBO ↔ qubit encoding*
- 2.2 Continuous warm-start QAOA — "If a coordinate in the optimal solution of a continuous relaxation is c∗_i = 0 or c∗_i = 1, qubit i would be initialized in state |0⟩ or |1⟩, respectively. In such cases, the qubit will remain in its initial state throughout the QAOA optimization when ˆHC contains only ˆZi ˆZj and identity spin-operators." — *useful for: §2.2 Practical issues / reachability*
- 2.2 Continuous warm-start QAOA — "For large enough p, (WS-)QAOA therefore reproduces the adiabatic evolution transforming the ground state of the mixer into the ground state of ˆHC." — *useful for: §2.2 Convergence discussion*
- 2.3 Rounded warm-start QAOA — "This adjustment also comes with a drawback. Since the prepared initial state is no longer an eigenstate of the mixer (otherwise we would not be able to deviate from it) we cannot use the same arguments as in [16] to derive the convergence of the algorithm to the global optimum with increasing depth p." — *useful for: §2.3 Trade-offs of rounded warm-starts*
- 2.5 Discussion of warm-starting quantum optimization — "Under the Unique Games Conjecture [83, 84], it is strictly impossible to improve upon the guarantees of GW [53] using either quantum or classical algorithms running in polynomial time, unless a quantum computer can solve NP-Hard problems in polynomial time, which is not believed to be the case [85], or if P = NP." — *useful for: §2.4 Performance guarantees & hardness*
- 3 Simulations with Continuous-Valued Warm-start — "The probability of sampling the optimal binary solution d∗ is more than 5 times higher with WS-QAOA then standard QAOA for the simulated depths 1 ≤ p ≤ 5, see Fig. 4(a)." — *useful for: §3 Numerical evidence (portfolio example)*
- 5 Discussion and Conclusion — "An implementation of WS-QAOA is available in Qiskit [94], the open-source software development kit for working with quantum computers." — *useful for: §1.3 Reproducibility / tools*

## Limitations stated by authors
- Reachability when relaxation is integral — 2.2 Continuous warm-start QAOA — "This creates a reachability issue when the optimal continuous and discrete solutions do not overlap, i.e., d∗_i = 1 and c∗_i = 0 or d∗_i = 0 and c∗_i = 1, where d∗ is the solution to the (QUBO)." 
- Loss of convergence argument for modified mixer — 2.3 Rounded warm-start QAOA — "This adjustment also comes with a drawback. Since the prepared initial state is no longer an eigenstate of the mixer ... we cannot use the same arguments as in [16] to derive the convergence of the algorithm to the global optimum with increasing depth p."
- Classical pre-processing cost for strong relaxations — 2.5 Discussion of warm-starting quantum optimization — "higher-order relaxations within these hierarchies [72–74] require a run-time of the classical SDP solver which is super-polynomial in the number n of integral decision variables in (QUBO) and the order in the hierarchy [72–74]."
- Fundamental hardness under UGC — 2.5 Discussion of warm-starting quantum optimization — "If the Unique Games Conjecture is true, these guarantees cannot be improved upon by classical or quantum algorithms running in polynomial time."

## How this paper might be used in the chapter
- §1 (Introduction): Use the Abstract and opening paragraphs to motivate warm-starting as a hybrid classical–quantum strategy and to cite concrete claims about inheriting classical approximation guarantees.
- §2 (Background): Cite the WS-QAOA construction (initial state |φ∗⟩ and ˆH(ws)_M) when describing QAOA variants and mixer choices; include the regularization-ε continuity to show relation to standard QAOA.
- §2 (Background — relaxations): Use the discussion of QP vs SDP relaxations and GW randomized rounding to explain classical relaxations that feed quantum warm starts.
- §2 (Limitations/Complexity): Quote the statements about reachability, loss of convergence guarantees for modified mixer, and dependence on Unique Games Conjecture when discussing theoretical limits.
- §3 (Applications / Numerical illustrations): Reference the portfolio and MAXCUT simulation results as evidence that warm-starts help at low depth and to justify further experiments in the thesis.
- Method notes / reproducibility: Mention the Qiskit implementation note and Appendix material (e.g., algorithms for evaluating correlators) as pointers for implementation details or replication.

## Researcher to verify
- [x] Locate and confirm the formal statement or proof in the paper that "for MAXCUT a warm-start can preserve the GW approximation ratio at any depth p" — RESOLVED-VIA-EXCLUSION: the formal MAXCUT/GW result is below the chapter's level of abstraction. Cite only the conceptual claim that warm-starts inherit classical approximation guarantees.
- [x] Verify the exact GW approximation numerical bounds reported ("for 0.87856 < α < 0.87857") — RESOLVED-VIA-EXCLUSION: the precise GW constant is below the chapter's level of abstraction. Reference "≈88%" or "the Goemans–Williamson bound" in plain prose if needed.
- [x] Confirm the Qiskit implementation reference [94] — RESOLVED-VIA-EXCLUSION: implementation pointer is below the chapter's level of abstraction. Not cited.
- [x] Check numerical details of simulation claims (e.g., "probability ... more than 5 times higher with WS-QAOA") — RESOLVED-VIA-EXCLUSION: simulation specifics are below the chapter's level of abstraction. Not cited.
