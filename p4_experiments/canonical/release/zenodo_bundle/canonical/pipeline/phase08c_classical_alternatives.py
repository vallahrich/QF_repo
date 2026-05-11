"""Phase 8c — Top-3 classical-method coverage for all current cohort labels.

Phase 8b measured one (or two) paper-faithful classical baseline per
*Faithful* label (13 of 71). Phase 8c extends coverage to **all 71
labels** by running the **top-3 silo-default classical methods** at the
label's instance-scale, regardless of fidelity.

Scope and scientific scope-limit
--------------------------------
- For Faithful labels, the top-3 measurement is run on the same
  instance.json that Phase 8b uses. Treated as supplementary evidence.
- For Proxy-declared labels, the top-3 measurement is run on the
  *template-proxy* instance.json. The resulting wall-clock numbers
  describe "the time a competent classical analyst would need on the
  template-proxy problem", not "the time on the paper's exact problem".
  This is reported as a cohort-coverage table in the manuscript and is
  NOT used for per-label same-algorithm equivalence claims.

Threats-to-validity link
------------------------
- IV-8 (linear-SVM substitution) applies whenever ``svm_linear_primal``
  appears in the silo top-3.
- IV-9 (selective Phase 8 incompleteness) is *partially mitigated* by
  Phase 8c's all-cohort coverage; the residual concern (paper-faithful
  vs proxy instance) is documented above.

Method palette per silo
-----------------------
derivative-pricing   : MC_lognormal | PDE_fd_CN  | binomial_tree
simulation-monte-carlo: MC_lognormal | MC_antithetic | QMC_sobol
quantum-ml-finance   : SVM_linear   | LR_IRLS    | kmeans_lloyd
portfolio-optimization: dense_linsolve | QP_meanvariance | MC_lognormal
risk-management      : empirical_VaR | parametric_VaR | MC_lognormal
fraud-detection      : LR_IRLS      | SVM_linear   | kmeans_lloyd
insurance-actuarial  : MC_lognormal | empirical_VaR | parametric_VaR
trading-execution    : LR_IRLS      | SVM_linear   | MC_lognormal
other                : dense_linsolve | SVM_linear  | MC_lognormal

Citations
---------
Boyle 1977             (MC lognormal)
Glasserman 2003 §4.2   (MC antithetic, parametric VaR, empirical VaR)
Crank-Nicolson 1947    (PDE FD)
Cox-Ross-Rubinstein 1979 (binomial tree)
Sobol 1967 + Niederreiter 1992 (QMC)
RiskMetrics 1996       (parametric VaR)
Markowitz 1952         (mean-variance QP / linsolve)
Cortes-Vapnik 1995     (linear SVM)
McCullagh-Nelder 1989  (logistic regression IRLS)
Lloyd 1982             (k-means)

Operator decision: 2026-04-19, DECISIONS_LOG.md (Phase 8c).
"""
from __future__ import annotations

import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable, Iterable

import numpy as np
from scipy.optimize import minimize
from scipy.stats import norm
from scipy.stats.qmc import Sobol

# Reuse existing kernels + helpers from Phase 8b.
from p4_experiments.canonical.pipeline.phase08b_classical_baselines import (
    BASELINES as PHASE8B_BASELINES,
    SINGLE_THREAD_NOTE,
    _derive_n_paths,
    _instance_path_for,
    _load_params,
)

ROOT = Path(__file__).resolve().parents[3]
CANON = ROOT / "p4_experiments" / "canonical"
COHORT_PATH = CANON / "cohort.json"
OUT_DIR = CANON / "outputs" / "phase08c_alternatives"
OUT_DIR.mkdir(parents=True, exist_ok=True)

N_REPEATS = 5
BUDGET_S = 60.0
SEED_BASE = 0x50414D50  # SEED — pinned across the canonical pipeline


# =============================================================================
# New kernels (numpy + scipy only)
# =============================================================================

def _bs_european_call_price(S0, K, T, r, sigma):
    """Closed-form Black-Scholes European call (used as PDE/binomial check)."""
    if T <= 0 or sigma <= 0:
        return max(S0 - K, 0.0)
    d1 = (np.log(S0 / K) + (r + 0.5 * sigma * sigma) * T) / (sigma * np.sqrt(T))
    d2 = d1 - sigma * np.sqrt(T)
    return float(S0 * norm.cdf(d1) - K * np.exp(-r * T) * norm.cdf(d2))


def kernel_mc_antithetic_lognormal(params: dict, seed: int) -> dict:
    """Antithetic-variate MC for European call.

    Reference: Glasserman, P. (2003), "Monte Carlo Methods in Financial
    Engineering", Springer, §4.2 (Antithetic Variates), doi:10.1007/978-0-387-21617-1.
    """
    rng = np.random.default_rng(seed)
    n_paths = max(_derive_n_paths(params) // 2, 1)  # antithetic doubles effective sample
    S0 = float(params.get("S0", 2.0))
    sigma = float(params.get("volatility", 0.4))
    r = float(params.get("risk_free_rate", 0.05))
    T = float(params.get("time_to_maturity_days", 40)) / 365.0
    K = float(params.get("strike_price", S0 * 0.948))
    z = rng.standard_normal(n_paths)
    z_pair = np.concatenate([z, -z])
    ST = S0 * np.exp((r - 0.5 * sigma**2) * T + sigma * np.sqrt(T) * z_pair)
    payoff = np.maximum(ST - K, 0.0)
    pv = float(np.exp(-r * T) * payoff.mean())
    return {"estimate": pv, "n_paths_effective": int(z_pair.size)}


def kernel_qmc_sobol_european(params: dict, seed: int) -> dict:
    """Sobol-sequence QMC for European call.

    References:
      Sobol, I.M. (1967), "On the Distribution of Points in a Cube...",
        USSR Comp. Math. Phys. 7(4):86-112.
      Niederreiter, H. (1992), "Random Number Generation and Quasi-Monte
        Carlo Methods", SIAM CBMS-NSF 63, doi:10.1137/1.9781611970081.
    """
    n_paths = _derive_n_paths(params)
    # Sobol requires power-of-2 sample sizes for full balance properties.
    m = max(int(np.ceil(np.log2(max(n_paths, 2)))), 4)
    n_eff = 2 ** m
    S0 = float(params.get("S0", 2.0))
    sigma = float(params.get("volatility", 0.4))
    r = float(params.get("risk_free_rate", 0.05))
    T = float(params.get("time_to_maturity_days", 40)) / 365.0
    K = float(params.get("strike_price", S0 * 0.948))
    sob = Sobol(d=1, scramble=True, seed=seed)
    u = sob.random_base2(m=m).ravel()
    u = np.clip(u, 1e-12, 1 - 1e-12)
    z = norm.ppf(u)
    ST = S0 * np.exp((r - 0.5 * sigma**2) * T + sigma * np.sqrt(T) * z)
    pv = float(np.exp(-r * T) * np.maximum(ST - K, 0.0).mean())
    return {"estimate": pv, "n_paths_qmc": int(n_eff)}


def kernel_pde_fd_european(params: dict, seed: int) -> dict:
    """Crank-Nicolson finite-difference PDE solver for European call.

    Reference: Crank, J. & Nicolson, P. (1947), "A Practical Method for
    Numerical Evaluation of Solutions of PDEs of the Heat-Conduction Type",
    Proc. Cambridge Philos. Soc. 43(1):50-67, doi:10.1017/S0305004100023197.
    Standard discretisation of Black-Scholes PDE on a price-time grid.
    """
    S0 = float(params.get("S0", 2.0))
    sigma = float(params.get("volatility", 0.4))
    r = float(params.get("risk_free_rate", 0.05))
    T = float(params.get("time_to_maturity_days", 40)) / 365.0
    K = float(params.get("strike_price", S0 * 0.948))

    # Grid: derive size from n_shots so quantum-shot scale ↔ classical work.
    n_shots = _derive_n_paths(params)
    M = int(np.clip(np.sqrt(n_shots), 32, 1024))   # price grid
    N = int(np.clip(np.sqrt(n_shots), 32, 1024))   # time grid
    Smax = max(4 * S0, 2 * K)
    dS = Smax / M
    dt = T / N
    S = np.linspace(0.0, Smax, M + 1)
    V = np.maximum(S - K, 0.0)  # terminal payoff

    # Tridiagonal Crank-Nicolson coefficients
    j = np.arange(1, M)
    a = 0.25 * dt * (sigma**2 * j**2 - r * j)
    b = -0.5 * dt * (sigma**2 * j**2 + r)
    c = 0.25 * dt * (sigma**2 * j**2 + r * j)
    # Build A (LHS) and B (RHS) tridiagonal matrices on interior points
    interior = M - 1
    A = np.zeros((interior, interior))
    B = np.zeros((interior, interior))
    for i in range(interior):
        if i > 0:
            A[i, i - 1] = -a[i]
            B[i, i - 1] = a[i]
        A[i, i] = 1 - b[i]
        B[i, i] = 1 + b[i]
        if i < interior - 1:
            A[i, i + 1] = -c[i]
            B[i, i + 1] = c[i]

    # March backwards in time
    for _ in range(N):
        rhs = B @ V[1:M]
        # Boundary: V[0]=0, V[M]=Smax-K*exp(-r*tau)
        rhs[-1] += c[-1] * (Smax - K)  # plus S[M] payoff approximation
        V[1:M] = np.linalg.solve(A, rhs)
        V[0] = 0.0
        V[M] = Smax - K
    pv = float(np.interp(S0, S, V))
    return {"estimate": pv, "M": M, "N": N}


def kernel_binomial_tree_european(params: dict, seed: int) -> dict:
    """Cox-Ross-Rubinstein binomial-tree European call.

    Reference: Cox, J.C., Ross, S.A. & Rubinstein, M. (1979), "Option
    Pricing: A Simplified Approach", J. Financial Economics 7(3):229-263,
    doi:10.1016/0304-405X(79)90015-1.
    """
    S0 = float(params.get("S0", 2.0))
    sigma = float(params.get("volatility", 0.4))
    r = float(params.get("risk_free_rate", 0.05))
    T = float(params.get("time_to_maturity_days", 40)) / 365.0
    K = float(params.get("strike_price", S0 * 0.948))
    n_shots = _derive_n_paths(params)
    Nsteps = int(np.clip(n_shots // 8, 64, 2048))
    dt = T / Nsteps
    u = float(np.exp(sigma * np.sqrt(dt)))
    d = 1.0 / u
    p = (np.exp(r * dt) - d) / (u - d)
    # Terminal asset prices and payoffs
    j = np.arange(Nsteps + 1)
    ST = S0 * (u ** (Nsteps - j)) * (d ** j)
    V = np.maximum(ST - K, 0.0)
    disc = np.exp(-r * dt)
    for step in range(Nsteps, 0, -1):
        V = disc * (p * V[:-1] + (1 - p) * V[1:])
    return {"estimate": float(V[0]), "n_steps": Nsteps}


def kernel_variance_covariance_var(params: dict, seed: int) -> dict:
    """Parametric (variance-covariance) Gaussian VaR.

    Reference: J.P. Morgan / Reuters (1996), "RiskMetrics — Technical
    Document, 4th ed.", New York.
    Computes the alpha-VaR on a synthetic d-dimensional return distribution.
    """
    rng = np.random.default_rng(seed)
    d = int(params.get("n_features", params.get("n_qubits",
            params.get("num_uncertainty_qubits", 4))))
    n_obs = max(_derive_n_paths(params), 1024)
    sigma = float(params.get("volatility", 0.2))
    alpha = float(params.get("alpha", params.get("cvar_confidence_level", 0.05)))
    # Synthetic returns; estimate covariance and parametric VaR
    R = sigma * rng.standard_normal((n_obs, d))
    mu = R.mean(axis=0)
    Cov = np.cov(R, rowvar=False) if d > 1 else np.array([[float(R.var())]])
    # Equal-weight portfolio variance
    w = np.ones(d) / d
    port_mu = float(w @ mu)
    port_var = float(w @ Cov @ w)
    z = float(norm.ppf(alpha))
    var_alpha = float(port_mu + z * np.sqrt(port_var))
    return {"estimate": var_alpha, "n_obs": n_obs, "d": d, "alpha": alpha}


def kernel_qp_markowitz_meanvariance(params: dict, seed: int) -> dict:
    """Mean-variance QP via scipy.optimize.minimize (SLSQP).

    Reference: Markowitz, H. (1952), "Portfolio Selection", J. Finance
    7(1):77-91, doi:10.1111/j.1540-6261.1952.tb01525.x. Solves
    min 0.5 w' Sigma w subject to 1'w = 1, w >= 0 for a synthetic
    n-asset universe.
    """
    rng = np.random.default_rng(seed)
    n = int(params.get("n_features", params.get("n_qubits",
            params.get("n_b", params.get("num_uncertainty_qubits", 6)))))
    n = max(n, 4)
    A = rng.standard_normal((n, n))
    Sigma = A @ A.T + n * np.eye(n)
    mu = rng.standard_normal(n)

    def obj(w):
        return 0.5 * w @ Sigma @ w - 0.05 * (mu @ w)

    cons = [{"type": "eq", "fun": lambda w: float(w.sum() - 1.0)}]
    bnds = [(0.0, 1.0)] * n
    w0 = np.ones(n) / n
    res = minimize(obj, w0, method="SLSQP", bounds=bnds, constraints=cons,
                   options={"maxiter": 200, "ftol": 1e-9})
    return {"objective": float(res.fun), "n": n, "iters": int(res.nit)}


def kernel_logistic_regression_irls(params: dict, seed: int) -> dict:
    """Logistic regression via Iteratively Reweighted Least Squares.

    Reference: McCullagh, P. & Nelder, J.A. (1989), "Generalized Linear
    Models" (2nd ed.), Chapman & Hall, doi:10.1007/978-1-4899-3242-6.
    """
    def sigmoid(x: np.ndarray) -> np.ndarray:
        return 1.0 / (1.0 + np.exp(-np.clip(x, -500, 500)))

    rng = np.random.default_rng(seed)
    d = int(params.get("n_features", params.get("n_qubits", 3)))
    n = int(params.get("n_samples_train", 64))
    w_true = rng.standard_normal(d)
    X = rng.standard_normal((n, d))
    p_true = sigmoid(X @ w_true)
    y = (rng.uniform(size=n) < p_true).astype(float)
    # IRLS
    w = np.zeros(d)
    for _ in range(50):
        eta = X @ w
        p = sigmoid(eta)
        W = p * (1 - p) + 1e-9
        z = eta + (y - p) / W
        # Weighted least squares: (X' W X) w = X' W z
        WX = X * W[:, None]
        H = X.T @ WX + 1e-6 * np.eye(d)
        g = X.T @ (W * z)
        w_new = np.linalg.solve(H, g)
        if np.linalg.norm(w_new - w) < 1e-8:
            w = w_new
            break
        w = w_new
    pred = (X @ w >= 0).astype(float)
    acc = float((pred == y).mean())
    return {"train_acc": acc, "n": n, "d": d}


def kernel_kmeans_lloyd(params: dict, seed: int) -> dict:
    """k-means clustering via Lloyd's algorithm.

    Reference: Lloyd, S.P. (1982), "Least Squares Quantization in PCM",
    IEEE Trans. Information Theory 28(2):129-137, doi:10.1109/TIT.1982.1056489.
    """
    rng = np.random.default_rng(seed)
    d = int(params.get("n_features", params.get("n_qubits", 3)))
    n = int(params.get("n_samples_train", 128))
    K = max(2, min(8, d))
    X = rng.standard_normal((n, d))
    # Init: random sample of points
    idx = rng.choice(n, size=K, replace=False)
    C = X[idx].copy()
    for _ in range(50):
        D = ((X[:, None, :] - C[None, :, :]) ** 2).sum(axis=2)
        labels = D.argmin(axis=1)
        C_new = np.array([X[labels == k].mean(axis=0) if (labels == k).any()
                          else C[k] for k in range(K)])
        if np.linalg.norm(C_new - C) < 1e-8:
            C = C_new
            break
        C = C_new
    inertia = float(((X - C[labels]) ** 2).sum())
    return {"inertia": inertia, "K": K, "n": n}


# =============================================================================
# Kernel registry (existing + new)
# =============================================================================

BASELINES_C: dict[str, Callable[[dict, int], dict]] = {
    **PHASE8B_BASELINES,
    "mc_antithetic_lognormal":     kernel_mc_antithetic_lognormal,
    "qmc_sobol_european":          kernel_qmc_sobol_european,
    "pde_fd_european":             kernel_pde_fd_european,
    "binomial_tree_european":      kernel_binomial_tree_european,
    "variance_covariance_var":     kernel_variance_covariance_var,
    "qp_markowitz_meanvariance":   kernel_qp_markowitz_meanvariance,
    "logistic_regression_irls":    kernel_logistic_regression_irls,
    "kmeans_lloyd":                kernel_kmeans_lloyd,
}


# =============================================================================
# Silo -> top-3 method palette (rank 1, 2, 3)
# =============================================================================

SILO_TOP3: dict[str, list[tuple[str, str]]] = {
    # silo : [(rank, kernel_name), ...]
    "derivative-pricing": [
        ("rank1", "mc_european_call_lognormal"),
        ("rank2", "pde_fd_european"),
        ("rank3", "binomial_tree_european"),
    ],
    "simulation-monte-carlo": [
        ("rank1", "mc_european_call_lognormal"),
        ("rank2", "mc_antithetic_lognormal"),
        ("rank3", "qmc_sobol_european"),
    ],
    "quantum-ml-finance": [
        ("rank1", "svm_linear_primal"),
        ("rank2", "logistic_regression_irls"),
        ("rank3", "kmeans_lloyd"),
    ],
    "portfolio-optimization": [
        ("rank1", "dense_linsolve"),
        ("rank2", "qp_markowitz_meanvariance"),
        ("rank3", "mc_european_call_lognormal"),
    ],
    "risk-management": [
        ("rank1", "empirical_var_sliding_window"),
        ("rank2", "variance_covariance_var"),
        ("rank3", "mc_european_call_lognormal"),
    ],
    "fraud-detection": [
        ("rank1", "logistic_regression_irls"),
        ("rank2", "svm_linear_primal"),
        ("rank3", "kmeans_lloyd"),
    ],
    "insurance-actuarial": [
        ("rank1", "mc_european_call_lognormal"),
        ("rank2", "empirical_var_sliding_window"),
        ("rank3", "variance_covariance_var"),
    ],
    "trading-execution": [
        ("rank1", "logistic_regression_irls"),
        ("rank2", "svm_linear_primal"),
        ("rank3", "mc_european_call_lognormal"),
    ],
    "other": [
        ("rank1", "dense_linsolve"),
        ("rank2", "svm_linear_primal"),
        ("rank3", "mc_european_call_lognormal"),
    ],
}


# =============================================================================
# Measurement loop
# =============================================================================

def measure(kernel_name: str, params: dict, base_seed: int = SEED_BASE) -> dict:
    fn = BASELINES_C[kernel_name]
    times: list[float] = []
    estimates: list[dict] = []
    started = datetime.now(timezone.utc).isoformat()
    for r in range(N_REPEATS):
        seed = base_seed + r
        t0 = time.perf_counter()
        try:
            out = fn(params, seed)
            err = None
        except Exception as e:  # never let one bad kernel kill the run
            out = {"error": f"{type(e).__name__}: {e}"}
            err = str(e)
        elapsed = time.perf_counter() - t0
        times.append(elapsed)
        estimates.append(out)
        if err is not None:
            break
        if elapsed > BUDGET_S:
            break
    arr = np.array(times)
    return {
        "kernel": kernel_name,
        "n_repeats_completed": len(times),
        "wall_clock_seconds_median": float(np.median(arr)),
        "wall_clock_seconds_iqr": [float(np.quantile(arr, 0.25)),
                                   float(np.quantile(arr, 0.75))],
        "wall_clock_seconds_per_repeat": [float(t) for t in times],
        "kernel_outputs_per_repeat": estimates,
        "started_utc": started,
        "completed_utc": datetime.now(timezone.utc).isoformat(),
        "thread_env": {
            "OMP_NUM_THREADS": os.environ.get("OMP_NUM_THREADS"),
            "MKL_NUM_THREADS": os.environ.get("MKL_NUM_THREADS"),
            "OPENBLAS_NUM_THREADS": os.environ.get("OPENBLAS_NUM_THREADS"),
        },
    }


def run_label(label: str, silo: str, fidelity: str) -> dict:
    palette = SILO_TOP3.get(silo)
    if palette is None:
        rec = {
            "schema_version": "phase8c.1.0",
            "label": label,
            "silo": silo,
            "fidelity": fidelity,
            "skipped": True,
            "reason": f"no SILO_TOP3 palette for silo={silo!r}",
            "baseline_scale_type": "not_applicable_no_palette",
            "paper_published_scale_estimate_seconds": None,
            "paper_published_scale_estimate_status": "not_estimated",
            "headline_h4_eligible": False,
            "scope_note": (
                "Phase 8c top-3 alternatives are defined only for silos with "
                "registered finance-domain classical palettes. This label is "
                "retained as an explicit skip rather than assigned an unrelated "
                "fallback palette."
            ),
        }
        out_path = OUT_DIR / f"{label}.json"
        out_path.write_text(json.dumps(rec, indent=2), encoding="utf-8")
        print(f"  [{label:<6} {silo:<23} {fidelity}] skipped: {rec['reason']} -> {out_path.name}")
        return rec
    try:
        params, inst_path = _load_params(label)
    except Exception as e:
        return {"label": label, "silo": silo, "fidelity": fidelity,
                "error": f"_load_params: {type(e).__name__}: {e}"}
    measurements = {}
    for rank, kname in palette:
        m = measure(kname, params)
        measurements[rank] = {"kernel": kname, **m}
    baseline_scale_type = (
        "faithful_label_instance_scale" if fidelity == "F" else "proxy_template_instance_scale"
    )
    rec = {
        "schema_version": "phase8c.1.0",
        "label": label,
        "silo": silo,
        "fidelity": fidelity,
        "instance_path": inst_path,
        "instance_parameters": params,
        "baseline_scale_type": baseline_scale_type,
        "paper_published_scale_estimate_seconds": None,
        "paper_published_scale_estimate_status": "not_estimated",
        "headline_h4_eligible": False,
        "scope_note": (
            "Top-3 silo-default classical methods at the label's instance "
            "scale. For Faithful labels: paper-comparable. For Proxy-declared "
            "labels: template-proxy instance scale (cohort-coverage table "
            "only; not per-label same-algorithm equivalence). See "
            "DECISIONS_LOG.md 2026-04-19 Phase 8c and THREATS_TO_VALIDITY.md "
            "IV-9."
        ),
        "single_thread_note": SINGLE_THREAD_NOTE,
        "measurements": measurements,
    }
    out_path = OUT_DIR / f"{label}.json"
    out_path.write_text(json.dumps(rec, indent=2), encoding="utf-8")
    # short stdout line
    fastest = min(
        ((rank, m["wall_clock_seconds_median"]) for rank, m in measurements.items()
         if isinstance(m.get("wall_clock_seconds_median"), float)),
        key=lambda x: x[1],
        default=(None, None),
    )
    print(f"  [{label:<6} {silo:<23} {fidelity}] "
          f"r1={measurements['rank1']['wall_clock_seconds_median']:.4g}s "
          f"r2={measurements['rank2']['wall_clock_seconds_median']:.4g}s "
          f"r3={measurements['rank3']['wall_clock_seconds_median']:.4g}s "
          f"best={fastest[0]} -> {out_path.name}")
    return rec


def main(argv: list[str] | None = None) -> int:
    cohort = json.loads(COHORT_PATH.read_text(encoding="utf-8"))
    labels = cohort["labels"]
    print(f"[Phase 8c] starting; output -> {OUT_DIR.relative_to(ROOT)}")
    print(f"[Phase 8c] {SINGLE_THREAD_NOTE}")
    print(f"[Phase 8c] N_REPEATS={N_REPEATS} BUDGET_S={BUDGET_S} SEED={hex(SEED_BASE)}")
    print(f"[Phase 8c] {len(labels)} labels to measure (all silos, all fidelities)")
    n_ok = n_err = n_skip = 0
    for lid, e in labels.items():
        silo = e.get("silo", "?")
        fid = e.get("fidelity", "?")
        rec = run_label(lid, silo, fid)
        if rec.get("error"):
            n_err += 1
        elif rec.get("skipped"):
            n_skip += 1
        else:
            n_ok += 1
    print(f"[Phase 8c] done; ok={n_ok} err={n_err} skipped={n_skip}")

    # Self-record phase status + write a per-label summary into cohort.json
    summary = {}
    for lid in labels.keys():
        p = OUT_DIR / f"{lid}.json"
        if not p.exists():
            continue
        d = json.loads(p.read_text(encoding="utf-8"))
        ms = d.get("measurements", {})
        summary[lid] = {
            rank: {
                "kernel": m["kernel"],
                "wall_clock_seconds_median": m["wall_clock_seconds_median"],
            }
            for rank, m in ms.items()
        }
    cohort.setdefault("_phase_status", {})["phase8c_alternatives"] = {
        "status": "complete",
        "completed_utc": datetime.now(timezone.utc).isoformat(),
        "labels_attempted": len(labels),
        "ok": n_ok, "err": n_err, "skipped": n_skip,
        "n_repeats": N_REPEATS,
        "budget_seconds": BUDGET_S,
        "seed": hex(SEED_BASE),
        "results_dir": str(OUT_DIR.relative_to(ROOT)).replace("\\", "/"),
        "kernels_registered": sorted(BASELINES_C.keys()),
        "silos_with_palette": sorted(SILO_TOP3.keys()),
    }
    cohort["classical_alternatives_top3"] = summary
    COHORT_PATH.write_text(json.dumps(cohort, indent=2), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
