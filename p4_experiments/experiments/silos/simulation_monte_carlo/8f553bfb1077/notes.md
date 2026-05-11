# SM2 — Quantum spectral method for stochastic processes

- **paper_id:** `8f553bfb1077`
- **Title:** A quantum spectral method for simulating stochastic processes, with applications to Monte Carlo
- **Authors:** Bouland, Dandapani, Prakash (2023)
- **Silo:** simulation-monte-carlo
- **Template:** `templates.sim_mc_state_prep` + `templates.qae`.

## Reconstruction status — REQUIRES_HUMAN_REVIEW

- [ ] No qubit count in P3 extraction; defaults (n_state=5, num_eval=3, layers=3).
- [ ] State-prep proxy does not encode fractional Brownian motion; faithful version would implement Karhunen–Loève coefficients (paper §IV).

## Classical baseline plan

`numpy.random.standard_normal` Monte Carlo of the same fBM inner product, ~10⁵ samples → ~50 ms. Comfortably above the 10 ms floor.
