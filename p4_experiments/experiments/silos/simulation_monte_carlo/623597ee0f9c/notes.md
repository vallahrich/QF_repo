# SM3 — OSDE-based QMCI for stochastic time evolution

- **paper_id:** `623597ee0f9c`
- **Title:** Dividing quantum circuits for time evolution of stochastic processes by orthogonal series density estimation
- **Author:** Koichi Miyamoto (2025)
- **Silo:** simulation-monte-carlo
- **Template:** `templates.sim_mc_state_prep` + `templates.qae`.

## Reconstruction status — REQUIRES_HUMAN_REVIEW

- [ ] No qubit count in P3 extraction; defaults (n_state=4, num_eval=3, layers=2).
- [ ] OSDE chains many AE blocks; `notes.md` documents tau is per-block, not per-end-to-end-algorithm.

## Classical baseline plan

`scipy.integrate.solve_ivp` of the matched stochastic ODE; should easily clear 10 ms for non-trivial drift coefficients.
