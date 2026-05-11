<!-- chapter-supporting-literature reading note
     paper_id:        78cc9d5068f3
     selection_id:    C-03
     source_text:     shared/extracted_text/text/78cc9d5068f3_quantum_algorithms_for_portfolio_optimization.md
     generated_at:    2026-05-03T09:59:33.594576+00:00
     model:           gpt-5-mini
     temperature:     0.2
     prompt_version:  1.0 (2026-05-03)
     prompt_sha:      72a0945464a5
     rendered_sha:    b7405e76214c
     status:          PENDING researcher review
     accept by:       moving this file to ../<paper_id>__<slug>.md -->

> ⛔ **EXCLUSION FLAG (researcher discretion, 2026-05-03)**: This note is **TOO DETAILED** for the Background chapter scope. Most concepts (SOCP reduction, short-step interior-point method, block encodings, tomography precision, Newton linear systems) are below the level of abstraction the chapter operates at.
>
> **Action**: Do NOT use this note as a source for Chapter 1 or Chapter 2 prose. Only the high-level claims ("first quantum algorithm for *constrained* portfolio optimization"; "polynomial speedup over classical IPM"; empirical "almost O(n) speedup over the practical O(n^3.5) classical complexity") and the headline limitations (problem-dependent parameters; no worst-case guarantee; QRAM assumption) remain in scope.
>
> **Retain** the full extraction in this file for possible reuse in Ch.4 (methodology contrast) or Ch.7 (experiments).

# Quantum Algorithms for Portfolio Optimization (2019)

**Authors**: Iordanis Kerenidis, Anupam Prakash, Dániel Szilágyi  
**Venue**: arXiv preprint (arXiv:1908.08040v1)  
**DOI**: n/a  
**Suggested chapter sections**: §1.1 Motivation (Chapter 1), §2.1 Portfolio optimization formulation, §2.2 Convex conic programs (SOCP), §2.3 Interior-point methods, §2.4 Quantum linear algebra & block encodings, §2.5 Quantum interior-point methods for optimization

## 1-paragraph summary
This paper presents a quantum algorithm for the constrained portfolio optimization problem by reducing it to a second-order cone program (SOCP) and applying a quantum short-step interior-point method. The authors give a complexity expression (in terms of n, r and problem-dependent parameters κ, ζ, δ, ϵ), prove convergence guarantees (duality gap, feasibility up to δ), and provide numerical experiments on subsamples of S&P-500 data to estimate the problem-dependent factors and argue an average-case polynomial speedup (empirical exponent ≈2.387). The work builds on prior quantum IPM and block-encoding techniques and emphasizes conditions under which the quantum approach may outperform classical IPM solvers.

## Key concepts (with location)
- **Constrained portfolio optimization (SOCP formulation)** — Section 2 PORTFOLIO OPTIMIZATION — "min
xT MT Mx
s.t.
µT x = R
Ax = b
x ≥0.
(2)"
- **n-dimensional Lorentz cone (second-order cone)** — Definition 3.1 — "Deﬁnition 3.1. Te n-dimensional Lorentz cone, for n ≥0 is defined as Ln := {x = (x0; ex) ∈Rn+1 | ∥ex∥≤x0}."
- **SOCP primal / dual forms** — Section 3 REDUCING PORTFOLIO OPTIMIZATION TO SOCP — "min
cT x
s.t.
Ax = b
x ∈L,
(3)
...
max
bTy
s.t.
ATy + s = c
s ∈L.
(4)"
- **Short-step interior-point Newton linear system (per iteration)** — Section 4 THE SHORT STEP INTERIOR-POINT METHOD FOR SOCP — "
A
0
0
0
AT
I
Arw(s)
0
Arw(x)


∆x
∆y
∆s

=

b −Ax
c −s −ATy
σνe −Arw(x)s

.
(6)"
- **Quantum linear system problem / state encoding** — Section 6.1 Qantum linear algebra — "Given a matrix A and a vectorb, the quantum linear system problem is to construct the quantum state |A−1b⟩(using the notation from (7))."
- **(ζ, ℓ) block encoding (QRAM-based)** — Definition 6.1 and Theorem 6.2 — "Deﬁnition 6.1. Let A ∈Rn×n be a matrix. Ten, the ℓ-qubit unitary matrix U ∈C2ℓ×2ℓis a (ζ, ℓ) block encoding of A if U = A/ζ · · · · ." and "Teorem 6.2 (Block encodings using QRAM data structures [17, 18]). Tere exist QRAM data structures ... A (ζ (A), 2 logn) unitary block encoding for A ... can be implemented in time e O(log(n))."
- **Tomography cost (to recover classical vector)** — Theorem 6.4 — "Given a unitary mapping U : |0⟩7→|x⟩in time TU and δ > 0, there is an algorithm that produces an estimate x ∈Rd with ∥x∥= 1 such that ∥x −x∥≤δ with probability at least (1 −1/d0.83) in time O( TU d logd / δ 2 )."

## Quotable claims (with location)
- Abstract — "We develop the ﬁrst quantum algorithm for the constrained portfo- lio optimization problem." — *useful for: §1.1 Motivation*
- Abstract — "Te algorithm has running time
e
O

n√r ζ κ
δ 2 log (1/ϵ)

, where r is the number of positivity and bud- get constraints, n is the number of assets in the portfolio, ϵ the desired precision, and δ,κ,ζ are problem-dependent parameters related to the well-conditioning of the intermediate solutions." — *useful for: §2.4 Quantum algorithm complexity*
- Abstract — "If only a moderately accurate solution is required, our quantum al- gorithm can achieve a polynomial speedup over the best classical algorithms with complexity e
O √rnω log(1/ϵ), where ω is the ma- trix multiplication exponent..." — *useful for: §1.2 Comparative advantage / scope*
- Abstract — "these experiments suggest that for most instances the quantum algorithm can potentially achieve an O(n) speedup over its classical counterpart." — *useful for: §1.3 Empirical motivation / caveats*
- Introduction — "The main limitation of their algorithm is that it can not incorporate positivity or budget constraints, thus restricting its applicability to real world problems that can have complex budget constraints." (referring to Rebentrost & Lloyd) — *useful for: §2.1 Prior work limitations*
- Section 5 OUR RESULTS — "Theorem 5.1. Tere is a quantum algorithm for the constrained portfolio optimization problem 2 that outputs a solution x with the following guarantees." (followed by (i)-(iii)) — *useful for: §2.4 Formal guarantees*
- Theorem 5.1, part (iii) — "Te running time for the algorithm is
T = e
O
√r log (n/ϵ) · nκζ
δ2 log
κζ
δ

." — *useful for: §2.4 Complexity breakdown*
- Section 6.1 — "Puting together Teorems 6.2, 6.3 and 6.4, we obtain that there is a quantum algo- rithm that outputs a classical solution to the linear system Ax = b to accuracy δ in the ℓ2-norm in time e
O

n · κζ
δ 2

." — *useful for: §2.4 Quantum linear algebra cost and tomography*
- Section 6.2 Algorithm 2 — "Algorithm 2 Te quantum interior point method for Portfolio optimization." (algorithm overview steps 1–4) — *useful for: §2.3 Algorithmic pipeline*
- Section 7 EXPERIMENTAL RESULTS — "We sub-sampled the dataset to 50 companies and considered the stock performance for the first 100 days for our experiments. We computed the optimal portfolio for this dataset." — *useful for: §2.5 Single-instance benchmark — optimal portfolio computed on a fixed dataset (Figs 1–2)*
- Section 7 EXPERIMENTAL RESULTS — "the instances of (9) were constructed by choosing 100 random companies, choosing a random subinterval of t days (such that t is uniform in [10, 500]), and setting the precision parameter to ϵ = 0.1." — *useful for: §2.5 Scaling study for the quantum algorithm — empirical κ, δ, ζ across instance sizes (Figs 3–5)* 
- Section 7 EXPERIMENTAL RESULTS — "By finding the least-squares fit of a power law through these points, one obtains a dependence of O(n^2.387), with a 95% confidence bound of [2.184, 2.589]." — *useful for: §2.5 Empirical complexity estimate (note: fit is on log-log scale, after removing the top 1% of outliers; cf. Section 8 restates the same CI as 2.387 ± 0.202)*
- Section 8 CONCLUDING REMARKS — "the exponent b has a 95% confidence interval of 2.387 ± 0.202. Therefore, for most instances, we obtain an almost O(n)-speedup over the practical O(n^3.5) complexity of the classical algorithm." — *useful for: §2.5 Headline speedup claim (frame as average-case, conditional on bounded κ)*

## Limitations stated by authors
- Dependence on problem-specific parameters and no worst-case speedup — Introduction — "the running time of all these quantum algorithms depends on a number of problem speciﬁc parameters and they do not achieve a worst case speedup over classical algorithms."
- Feasibility / tomography error leads to approximate equality constraints (δ) — Section 5 OUR RESULTS — "As the solutions to the linear system are reconstructed using quantum tomography and are not exact, unlike the classical case the solutions may not be exactly feasible, the error parameter δ in part (ii) of Teorem 5.1 corresponds to the error induced by quantum tomography."
- QRAM / data-structure assumptions for block-encodings — Section 6.1 — "Note that |i⟩is the notation for the ⌈log(m)⌉qubit state ... Te QRAM can be thought of as the quantum analogue to RAM ..." (implying QRAM access assumption)
- Empirical/average-case nature of speedup claim — Conclusion — "Tese experiments suggest that there is no observable growth in the condition number κ as the problem size increases, whereas the most signiﬁcant impact on the running time of Algorithm 2 comes from the factor 1/δ2, which has been observed to grow roughly linearly with the problem size." (suggests empirical, not worst-case)

## How this paper might be used in the chapter
- §1 (Introduction): use the opening claims and the Abstract quotes to motivate why constrained portfolio optimization is an important target for quantum algorithms and to state the main contribution ("first quantum algorithm for the constrained portfolio optimization problem").
- §2 (Background — Quantum algorithms): cite the explanations of block encodings, QRAM assumptions, and the quantum linear system / tomography cost (Section 6.1) when introducing the technical prerequisites needed for quantum convex optimization.
- §2 (Background — Optimization methods): use the SOCP reduction (Section 3) and the short-step IPM Newton system (Section 4) to explain how portfolio QP maps to SOCP and why interior-point methods are the natural classical baseline.
- §2 (Background — Limitations & assumptions): discuss the role of problem-dependent parameters (κ, ζ, δ) and the QRAM/data-access model using the authors' explicit caveats; consider citing their empirical findings as illustrative (not definitive).
- §1 or §2 (Empirical context): use the experiments (Section 7) as an example of how authors estimate κ and δ and derive an empirical exponent ≈2.387; treat as suggestive evidence to motivate further empirical study.

## Researcher to verify
- [X] Confirm exact math formatting and intended meaning of the running-time expressions (the paper uses e O(·) and typeset fractions/parentheses across lines; verify the final intended asymptotic forms in the PDF source).  
- [x] Verify dataset subsampling details — RESOLVED: the two descriptions correspond to two different experiments. "50 companies × 100 days" = single-instance run used to compute the optimal portfolio reference (Figs 1–2). "100 random companies, t ∈ [10, 500] days" = scaling study for the simulated quantum algorithm (Figs 3–5).
- [x] Check the exact numerical fit reported for the empirical exponent (2.387 ± 0.202) and the method used — RESOLVED: §7 reports the CI as [2.184, 2.589] (least-squares power-law fit on log-log, after removing top 1% of outliers); §8 restates it as 2.387 ± 0.202 (the average half-width). Both refer to the same fit; consistent.
- [x] Confirm QRAM model assumptions and any claimed costs for constructing block encodings from classical data (Theorem 6.2) as implemented in experiments — RESOLVED-VIA-EXCLUSION: Theorem 6.2 details (block encoding cost Õ(log n), single-pass construction, O(log² n) update) are below the chapter's level of abstraction (see EXCLUSION FLAG above). Mention QRAM only as a high-level assumption ("requires a specialised quantum-data-structure assumption"), do NOT cite the theorem.
- [x] Note and confirm typographical occurrences of "Qantum" — RESOLVED: OCR artefact ("Qu" ligature dropped). Always cite as "Quantum". Title in this note already corrected.
