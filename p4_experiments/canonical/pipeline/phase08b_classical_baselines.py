"""Phase 8b — Classical baseline measurement.

For each Faithful (F-tier) label, run the paper-named (or silo-default
fallback) classical algorithm at the same instance size as the quantum
experiment, and record wall-clock time.

Spec (operator decisions, 2026-04-19):
  - Library set:        numpy + scipy only
  - Hardware:           operator laptop, single thread, no GPU
  - Repeats:            5 per measurement, 60s budget each
  - Reporting:          median + IQR (P25, P75)
    - Scope:              Faithful sub-cohort (13 current labels)
  - Both paper-named (primary) AND best-known silo default (sensitivity)

Output:
  p4_experiments/common/output/classical_results/<label>_<variant>.json

After this completes, run::

    python -m p4_experiments.canonical.pipeline.phase08b_update_cohort

to backfill ``classical_baseline.wall_clock_seconds`` in cohort.json,
then re-run Phase 9 to obtain the H4 result against MEASURED baselines.
"""
from __future__ import annotations

import json
import os

# Reproducibility guard 2026-05-02: pin BLAS threads to 1 BEFORE numpy/scipy
# import. The H4 wall-clock comparisons are valid only if the classical
# baselines run single-threaded (the SINGLE_THREAD_NOTE below documents this).
# Using `setdefault` so an explicit override (e.g. for parallel sensitivity
# studies) still wins, but a vanilla direct invocation cannot accidentally
# multi-thread BLAS through default linkage.
for _v in ("OMP_NUM_THREADS", "MKL_NUM_THREADS", "OPENBLAS_NUM_THREADS",
           "BLIS_NUM_THREADS", "VECLIB_MAXIMUM_THREADS", "NUMEXPR_NUM_THREADS"):
    os.environ.setdefault(_v, "1")

import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

import numpy as np
from scipy.optimize import minimize

# Canonical pipeline SEED (matches PRE_REGISTRATION.md §6.5 and Phase 9).
# Used as the deterministic random_state for sklearn estimators in Phase 8b
# (Phase B1, 2026-04-20). Numpy synthetic-data generation continues to use
# the per-repeat seed (0..N_REPEATS-1) so that the new svm_rbf_sklearn
# kernel sees byte-identical training data to svm_linear_primal — only the
# classifier differs.
CANONICAL_SEED = 0x50414D50

ROOT = Path(__file__).resolve().parents[3]
CANON = ROOT / "p4_experiments" / "canonical"
COHORT_PATH = CANON / "cohort.json"
OUT_DIR = ROOT / "p4_experiments" / "common" / "output" / "classical_results"
OUT_DIR.mkdir(parents=True, exist_ok=True)

# Set process to single-thread numpy (best-effort; takes effect for
# OpenBLAS / MKL / Accelerate when env vars are set BEFORE numpy import).
# We document this rather than enforce it, since import order is brittle.
SINGLE_THREAD_NOTE = (
    "Set OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 "
    "before invoking python for true single-thread enforcement."
)

N_REPEATS = 5
BUDGET_S = 60.0


def _baseline_scale_metadata(spec: dict[str, Any], variant_key: str) -> dict[str, Any]:
    relationship = spec.get("baseline_relationship", "paper_named_exact")
    if variant_key == "silo_default":
        scale_type = "silo_default_same_instance_sensitivity"
        headline_eligible = False
    elif relationship == "paper_named_exact":
        scale_type = "paper_named_same_instance_measured"
        headline_eligible = True
    elif relationship == "paper_named_component":
        scale_type = "paper_named_component_same_instance_measured"
        headline_eligible = True
    else:
        scale_type = "fallback_same_instance_measured"
        headline_eligible = False
    return {
        "baseline_scale_type": scale_type,
        "paper_published_scale_estimate_seconds": None,
        "paper_published_scale_estimate_status": "not_estimated",
        "headline_h4_eligible": headline_eligible,
        "baseline_claim_scope": (
            "Measured classical timing at the canonical label instance scale; "
            "not a reconstruction of the paper's full reported benchmark scale."
        ),
    }


# ---------------------------------------------------------------------------
# Per-label baseline mapping
# ---------------------------------------------------------------------------
# Each entry: (kernel_name, kernel_kwargs)
#   kernel_name -> function in BASELINES dict
#   kernel_kwargs -> kwargs derived from instance.json parameters
#
# `paper_named`  is what the paper compared against (primary, always run).
# `silo_default` is the Phase-5 silo-default baseline (run as sensitivity
#                 unless it equals paper_named, in which case it's omitted).
#
# Comments record the substitution rationale where the paper baseline is
# vague or requires a library outside (numpy, scipy).

LABEL_BASELINES: dict[str, dict[str, Any]] = {
    # ---- derivative-pricing ----
    "SD3": {
        "paper_named": ("mc_european_call_lognormal", {}),
        "silo_default": None,
        "baseline_relationship": "measured_fallback",
        "note": "Paper-named 'classical PDE solvers' baseline suffers curse of dimensionality. "
                "The paper does not provide enough discretization detail for a faithful PDE "
                "implementation at the template-proxy instance scale, so Phase 8b uses the "
                "derivative-pricing silo-default classical MC kernel as a conservative "
                "measured fallback.",
    },
    "SD7": {
        "paper_named": ("mc_european_call_lognormal", {}),
        "silo_default": None,
        "baseline_relationship": "measured_fallback",
        "note": "Paper-named 'classical FDM + Kunitomo-Ikeda' is barrier-option specific. "
                "Substituted with silo-default classical MC (Boyle 1977) at template-proxy "
                "instance size. Documented per operator decision 2026-04-19.",
    },
    "SD8": {
        "paper_named": ("mc_european_call_lognormal", {}),
        "silo_default": None,
        "baseline_relationship": "paper_named_component",
        "note": "Paper-named baseline includes Monte Carlo integration plus a full cosine "
                "expansion. The MC branch is implemented directly; full tensorized COS "
                "details are not derivable from the template-proxy instance file, so no "
                "separate COS timing is claimed.",
    },
    "SD10": {
        "paper_named": ("empirical_var_sliding_window", {}),
        "silo_default": ("mc_european_call_lognormal", {}),
        "note": "Paper-named empirical historical VaR on sliding window.",
    },
    "SD12": {
        "paper_named": ("mc_european_call_lognormal", {}),
        "silo_default": None,
        "note": "Paper-named classical MC (lognormal payoff sampling) = silo default.",
    },
    # ---- quantum-ml-finance ----
    "B3": {
        "paper_named": ("svm_rbf_sklearn", {}),
        "silo_default": ("svm_linear_primal", {}),
        "note": "Phase B1 (2026-04-20): paper-named RBF SVC restored (sklearn 1.7.2). "
                "Prior linear-SVM-primal kept as sensitivity. Retires IV-8.",
    },
    "B4": {
        "paper_named": ("svm_rbf_sklearn", {}),
        "silo_default": ("svm_linear_primal", {}),
        "note": "Phase B1 (2026-04-20): paper-named RBF SVC restored (sklearn 1.7.2). "
                "Prior linear-SVM-primal kept as sensitivity. Retires IV-8.",
    },
    "B5": {
        "paper_named": ("mc_european_call_lognormal", {}),
        "silo_default": ("svm_rbf_sklearn", {}),
        "note": "Paper-named 'Monte Carlo simulation' (QML paper used MC as the classical "
                "comparator); silo-default SVM run as sensitivity. Phase B1: silo-default "
                "upgraded to RBF SVC (sklearn 1.7.2) for consistency with B3/B4/SQ*.",
    },
    "SQ5": {
        "paper_named": ("svm_rbf_sklearn", {}),
        "silo_default": ("svm_linear_primal", {}),
        "note": "Phase B1 (2026-04-20): paper-named RBF SVC restored (sklearn 1.7.2). "
                "Prior linear-SVM-primal kept as sensitivity. Retires IV-8.",
    },
    "SQ17": {
        "paper_named": ("svm_rbf_sklearn", {}),
        "silo_default": ("svm_linear_primal", {}),
        "note": "Phase B1 (2026-04-20): paper-named RBF SVC restored (sklearn 1.7.2). "
                "Prior linear-SVM-primal kept as sensitivity. Retires IV-8.",
    },
    "SQ18": {
        "paper_named": ("svm_rbf_sklearn", {}),
        "silo_default": ("svm_linear_primal", {}),
        "note": "Phase B1 (2026-04-20): paper-named RBF SVC restored (sklearn 1.7.2). "
                "Prior linear-SVM-primal kept as sensitivity. Retires IV-8 (same as SQ17).",
    },
    # ---- portfolio-optimization ----
    "SP4": {
        "paper_named": ("dense_linsolve", {}),
        "silo_default": None,
        "note": "Paper-named 'analytical / by-hand 2-equation linear system; full 4x4 "
                "solved classically'; numpy.linalg.solve is the canonical implementation.",
    },
    # ---- simulation-monte-carlo ----
    "SM9": {
        "paper_named": ("mc_european_call_lognormal", {}),
        "silo_default": None,
        "note": "Paper-named 'Classical MC zeroth-order Pauli-operator-expansion'; "
                "substituted with silo-default classical MC. Pauli-expansion specific "
                "kernel not derivable from template-proxy instance.json.",
    },
    "SM10": {
        "paper_named": ("mc_european_call_lognormal", {}),
        "silo_default": None,
        "note": "Paper-named 'Grover-Rudolph (Qiskit built-in)' is a quantum-circuit "
                "state-preparation routine, not a classical algorithm. Substituted with "
                "silo-default classical MC.",
    },
    "SM5": {
        "paper_named": ("mc_european_call_lognormal", {}),
        "silo_default": None,
        "baseline_relationship": "measured_fallback",
        "note": "Paper-named baseline is 'classical fast Fourier transform simulation + "
                "classical direct trajectory writing'. The extraction does not provide the "
                "PSD/grid data needed for a faithful FFT trajectory implementation, so Phase "
                "8b uses the simulation-Monte-Carlo silo-default classical MC kernel at the "
                "template-proxy instance scale.",
    },
    # ---- risk-management ----
    "SR1": {
        "paper_named": ("empirical_var_sliding_window", {}),
        "silo_default": ("mc_european_call_lognormal", {}),
        "note": "Paper-named historical simulation (also CGAN/QCGAN); historical sim is "
                "empirical VaR on a sample.",
    },
    # ---- other ----
    "SX2": {
        "paper_named": ("dense_linsolve", {}),
        "silo_default": None,
        "note": "Paper-named ExactLSsolver (qiskit.aqua) which wraps numpy.linalg.solve.",
    },
    "SX3": {
        "paper_named": ("dense_linsolve", {}),
        "silo_default": None,
        "note": "Same as SX2.",
    },
    # ---- 2026-04-19 EXTENSION: 13 Faithful labels with PHASE_8_PENDING ----
    # See DECISIONS_LOG.md 2026-04-19 "Phase 8b extension: 13 labels".
    "SD13": {
        "paper_named": ("mc_european_call_lognormal", {}),
        "silo_default": None,
        "baseline_relationship": "measured_fallback",
        "note": "Paper-named 'IBM qiskit bitwise quantum-arithmetic baseline' is a "
                "quantum-circuit primitive (not a classical algorithm). Substituted "
                "with silo-default classical MC at template-proxy instance size. "
                "Documented per operator decision 2026-04-19 (Phase 8b extension).",
    },
    "SD14": {
        "paper_named": ("mc_european_call_lognormal", {}),
        "silo_default": None,
        "note": "Same as SD13: paper-named within-paper qiskit quantum-arithmetic "
                "comparator is not a classical algorithm; substituted with silo-default "
                "classical MC.",
    },
    "SM12": {
        "paper_named": ("mc_european_call_lognormal", {}),
        "silo_default": None,
        "note": "Paper-named 'classical MC / FFT-based spectral simulation'. The MC "
                "branch is the silo default; FFT-spectral specifics are not derivable "
                "from the template-proxy instance.json (no PSD provided). Substituted "
                "with silo-default classical MC.",
    },
    "SM13": {
        "paper_named": ("mc_european_call_lognormal", {}),
        "silo_default": None,
        "note": "Paper-named 'Classical Monte Carlo' = silo default.",
    },
    "SM14": {
        "paper_named": ("mc_european_call_lognormal", {}),
        "silo_default": None,
        "note": "Paper-named 'classical Monte Carlo' = silo default.",
    },
    "SM15": {
        "paper_named": ("mc_european_call_lognormal", {}),
        "silo_default": None,
        "baseline_relationship": "measured_fallback",
        "note": "Paper-named 'classical Monte Carlo' = silo default.",
    },
    "SP8": {
        "paper_named": ("dense_linsolve", {}),
        "silo_default": None,
        "note": "Paper-named 'Classical convex QP / Markowitz mean-variance "
                "(Markowitz 1952)'. Mean-variance optimisation reduces to a dense "
                "linear solve (KKT system) for the unconstrained / equality-only case; "
                "numpy.linalg.solve is the canonical implementation. Substitution "
                "omits explicit inequality constraints, which is consistent with the "
                "HHL template-proxy instance (no inequality data provided).",
    },
    "SP9": {
        "paper_named": ("dense_linsolve", {}),
        "silo_default": None,
        "note": "Same as SP8.",
    },
    "SQ13": {
        "paper_named": ("svm_linear_primal", {}),
        "silo_default": None,
        "note": "Paper-named 'Classical SVM / kernel SVM (Cortes & Vapnik 1995)'. "
                "Substituted with linear-SVM primal per scipy-only constraint. See B3 "
                "note for the kernel-substitution caveat.",
    },
    "SQ14": {
        "paper_named": ("svm_linear_primal", {}),
        "silo_default": None,
        "note": "Paper-named '(approximate) Sparsitron' (Klivans-Meka 2017). Sparsitron "
                "is an L1-constrained logistic-regression-style learner; not directly "
                "available in numpy/scipy. Substituted with linear-SVM primal as the "
                "closest scipy-only linear large-margin learner. Substitution may "
                "under- or over-estimate Sparsitron wall-clock; Phase 9 sensitivity "
                "flag `sensitivity_no_svm_substitution` already excludes SVM-substituted "
                "labels from the headline H4 result.",
    },
    "SQ15": {
        "paper_named": ("svm_linear_primal", {}),
        "silo_default": None,
        "note": "Paper-named 'Sparsitron (Klivans-Meka, Theorem 5) and Approximate "
                "Sparsitron (Theorem 6)'. Same substitution as SQ14.",
    },
    "SX5": {
        "paper_named": ("dense_linsolve", {}),
        "silo_default": None,
        "note": "Paper-named 'ExactLSsolver' (qiskit.aqua wrapper around numpy.linalg.solve). "
                "Identical kernel to SX2/SX3.",
    },
    "SX6": {
        "paper_named": ("ucb_heavy_tailed", {}),
        "silo_default": ("dense_linsolve", {}),
        "note": "Paper-named 'Classical heavy-tailed UCB (Bubeck-Cesa-Bianchi-Lugosi "
                "2013; Lee et al. 2020)'. Implemented in numpy as truncated-mean UCB "
                "on a synthetic K-arm Pareto-tailed reward instance. Silo-default "
                "dense_linsolve run as sensitivity since 'other' silo has no canonical "
                "baseline.",
    },
}


# ---------------------------------------------------------------------------
# Baseline kernels (numpy + scipy only)
# ---------------------------------------------------------------------------

def _derive_n_paths(params: dict) -> int:
    """Derive Monte Carlo path count from instance parameters.

    Convention: n_paths = n_shots if present (matches the quantum shot
    count one-for-one), else 4096.
    """
    return int(params.get("n_shots", 4096))


def kernel_mc_european_call_lognormal(params: dict, seed: int) -> dict:
    """Vectorised numpy MC for European call price under lognormal payoff.

    Reference: Boyle, P. (1977), "Options: A Monte Carlo Approach",
    Journal of Financial Economics 4(3):323-338, doi:10.1016/0304-405X(77)90005-8.
    Standard textbook lognormal-GBM Monte Carlo for European-style payoffs;
    used as the silo-default classical baseline for derivative-pricing labels.

    Uses parameters from instance.json when present, otherwise template-proxy
    fallbacks. Returns the present-value estimate alongside the wall-clock.
    """
    rng = np.random.default_rng(seed)
    n_paths = _derive_n_paths(params)
    S0 = float(params.get("S0", 2.0))
    sigma = float(params.get("volatility", 0.4))
    r = float(params.get("risk_free_rate", 0.05))
    T_days = float(params.get("time_to_maturity_days", 40))
    T = T_days / 365.0
    K = float(params.get("strike_price", S0 * 0.948))

    z = rng.standard_normal(n_paths)
    ST = S0 * np.exp((r - 0.5 * sigma**2) * T + sigma * np.sqrt(T) * z)
    payoff = np.maximum(ST - K, 0.0)
    pv = float(np.exp(-r * T) * payoff.mean())
    return {"estimate": pv, "n_paths": n_paths}


def kernel_empirical_var_sliding_window(params: dict, seed: int) -> dict:
    """Empirical VaR on a synthetic returns time series.

    Reference: Glasserman, P. (2003), "Monte Carlo Methods in Financial
    Engineering", Springer, doi:10.1007/978-0-387-21617-1, Ch. 9 (Risk
    Management). Sliding-window historical-simulation VaR is the canonical
    silo-default for risk-management and simulation-monte-carlo labels.

    Generates a synthetic GBM-style returns series and computes 95% VaR on
    a sliding window. Window size derived from n_shots (default 4096).
    """
    rng = np.random.default_rng(seed)
    n_paths = _derive_n_paths(params)
    sigma = float(params.get("volatility", 0.2))
    n_total = max(2 * n_paths, 8192)
    returns = sigma * rng.standard_normal(n_total)
    # Sliding-window VaR (window = n_paths/4, stride 1)
    window = max(n_paths // 4, 256)
    n_windows = n_total - window
    var95 = np.empty(n_windows)
    for i in range(n_windows):
        var95[i] = np.quantile(returns[i:i + window], 0.05)
    return {"estimate": float(np.median(var95)), "n_paths": n_total, "window": window}


def kernel_dense_linsolve(params: dict, seed: int) -> dict:
    """numpy.linalg.solve on a synthetic dense well-conditioned system.

    Reference: Markowitz, H. (1952), "Portfolio Selection", Journal of
    Finance 7(1):77-91, plus standard direct dense linear-solve
    (LAPACK GESV via numpy). Used as the silo-default classical baseline
    for portfolio-optimisation labels whose paper-stated method is a
    direct quadratic-programming or linear-system solve.

    Size derived from n_qubits (n = 2**n_qubits) so the classical work
    matches the quantum problem dimension.
    """
    rng = np.random.default_rng(seed)
    n_q = int(params.get("n_qubits", params.get("n_state", params.get("n_features", 4))))
    n = 2 ** n_q
    # Build a diagonally-dominant SPD matrix
    A = rng.standard_normal((n, n))
    A = A @ A.T + n * np.eye(n)
    b = rng.standard_normal(n)
    x = np.linalg.solve(A, b)
    return {"estimate_norm": float(np.linalg.norm(x)), "n": n}


def kernel_svm_linear_primal(params: dict, seed: int) -> dict:
    """Linear-SVM primal (hinge loss + L2 reg) via scipy.optimize.

    Reference: Cortes, C. & Vapnik, V. (1995), "Support-Vector Networks",
    Machine Learning 20(3):273-297, doi:10.1007/BF00994018.

    SUBSTITUTION NOTE (THREATS_TO_VALIDITY IV-8). Five Faithful labels
    (B3, B4, SQ5, SQ17, SQ18) cite RBF (or polynomial) kernel SVMs as
    the paper-stated baseline. We substitute a linear primal because
    the canonical pipeline excludes scikit-learn (operator decision
    2026-04-19, DECISIONS_LOG). Linear and RBF SVMs are distinct
    algorithms; the substitution may underestimate the wall-clock cost
    of the paper-faithful baseline. Phase 9 emits
    `H4.sensitivity_no_svm_substitution` excluding these labels so the
    headline H4 result can be audited without the substitution.

    Synthetic binary classification at the instance's (n_features,
    n_samples_train) scale.
    """
    rng = np.random.default_rng(seed)
    d = int(params.get("n_features", params.get("n_qubits", 3)))
    n = int(params.get("n_samples_train", 40))
    # Synthetic linearly separable data with noise
    w_true = rng.standard_normal(d)
    X = rng.standard_normal((n, d))
    y = np.sign(X @ w_true + 0.1 * rng.standard_normal(n))
    y[y == 0] = 1
    C = 1.0

    def loss(w_):
        margins = 1 - y * (X @ w_)
        hinge = np.maximum(0.0, margins).sum()
        return 0.5 * np.dot(w_, w_) + C * hinge

    w0 = np.zeros(d)
    res = minimize(loss, w0, method="L-BFGS-B")
    pred = np.sign(X @ res.x)
    pred[pred == 0] = 1
    acc = float((pred == y).mean())
    return {"train_acc": acc, "loss": float(res.fun), "n": n, "d": d}


def kernel_svm_rbf_sklearn(params: dict, seed: int) -> dict:
    """Paper-named RBF-kernel SVC via scikit-learn 1.7.2.

    Reference: Cortes, C. & Vapnik, V. (1995), "Support-Vector Networks",
    Machine Learning 20(3):273-297, doi:10.1007/BF00994018; sklearn libsvm
    backend (Pedregosa et al. 2011, JMLR 12:2825-2830).

    Phase B1 (2026-04-20) restores the paper-faithful kernel for the five
    QML-finance labels (B3, B4, SQ5, SQ17, SQ18) that cite RBF / polynomial
    SVMs as their classical baseline. Retires THREATS_TO_VALIDITY IV-8.
    sklearn 1.7.2 is pinned in requirements.lock; the prior scipy-only
    substitution (kernel_svm_linear_primal) is retained as the silo-default
    sensitivity row.

    Synthetic data generator is identical to kernel_svm_linear_primal
    (same RNG, same n / d, same labels) so the only difference between the
    paper_named and silo_default measurement records is the classifier.
    SVC.random_state is set from CANONICAL_SEED (PRE_REGISTRATION §6.5)
    rather than the per-repeat seed; SVC's RNG affects only tie-breaking
    and cache shuffling for kernel='rbf' without probability calibration,
    so this choice is documented but not numerically critical.

    Single-thread enforcement: see SINGLE_THREAD_NOTE. libsvm's RBF fit is
    inherently single-threaded (no internal threadpool); the OMP/MKL/
    OPENBLAS env vars only affect the Gram matrix prep on large n. For
    Phase 8b's tiny (n<=40) instances the kernel matrix fits in L2.
    """
    from sklearn.svm import SVC

    rng = np.random.default_rng(seed)
    d = int(params.get("n_features", params.get("n_qubits", 3)))
    n = int(params.get("n_samples_train", 40))
    # Synthetic linearly separable data with noise (BYTE-IDENTICAL to
    # kernel_svm_linear_primal at the same `seed`; do not edit either site
    # without updating both).
    w_true = rng.standard_normal(d)
    X = rng.standard_normal((n, d))
    y = np.sign(X @ w_true + 0.1 * rng.standard_normal(n))
    y[y == 0] = 1

    clf = SVC(kernel="rbf", C=1.0, gamma="scale", random_state=CANONICAL_SEED)
    clf.fit(X, y)
    pred = clf.predict(X)
    pred[pred == 0] = 1
    acc = float((pred == y).mean())
    return {
        "train_acc": acc,
        "n": n,
        "d": d,
        "n_support_": [int(s) for s in clf.n_support_],
        "implementation": "sklearn.svm.SVC",
        "sklearn_kernel": "rbf",
        "C": 1.0,
        "gamma": "scale",
        "random_state": CANONICAL_SEED,
    }


def kernel_ucb_heavy_tailed(params: dict, seed: int) -> dict:
    """Truncated-mean UCB on a synthetic heavy-tailed K-arm bandit.

    Reference: Bubeck, S., Cesa-Bianchi, N. & Lugosi, G. (2013), "Bandits with
    Heavy Tail", IEEE Trans. Information Theory 59(11):7711-7717,
    doi:10.1109/TIT.2013.2277869. Truncated-mean estimator is the canonical
    classical algorithm for the heavy-tailed multi-armed-bandit problem.

    Generates K Pareto-tailed reward arms (shape = 2.1, finite mean / infinite
    variance regime where heavy-tailed UCB strictly outperforms vanilla UCB)
    and runs T rounds of truncated-mean UCB. K and T are derived from the
    instance: K = 2**n_qubits (matches arm-encoding qubit count) and T =
    n_shots (matches the quantum shot budget).

    Returns the empirical pseudo-regret as the estimate.
    """
    rng = np.random.default_rng(seed)
    n_q = int(params.get("n_qubits", params.get("n_state", 4)))
    K = max(2 ** n_q, 4)
    T = int(params.get("n_shots", 4096))
    # Pareto-tailed arm means in [0, 1)
    true_means = rng.uniform(0.1, 0.9, size=K)
    best = float(true_means.max())
    pulls = np.zeros(K, dtype=np.int64)
    sums = np.zeros(K, dtype=np.float64)
    pseudo_regret = 0.0
    # Truncation threshold u_t = (t / log(1/delta))**(1/(1+epsilon)),
    # epsilon=1.1 gives the finite-mean / infinite-variance regime.
    eps = 1.1
    delta = 1.0 / max(T, 2)
    log_inv_delta = np.log(1.0 / delta)
    # Pull each arm once for initialisation
    for k in range(K):
        # Heavy-tailed reward: shifted Pareto with mean true_means[k]
        r = (rng.pareto(2.1) + 1.0) * (true_means[k] / 2.0)
        pulls[k] += 1
        sums[k] += r
        pseudo_regret += best - true_means[k]
    for t in range(K, T):
        # Truncated-mean UCB index per arm
        u_t = (t / log_inv_delta) ** (1.0 / (1.0 + eps))
        # Truncate empirical sum with current threshold
        emp = sums / np.maximum(pulls, 1)
        bonus = np.sqrt(2.0 * log_inv_delta / np.maximum(pulls, 1)) * np.minimum(1.0, u_t)
        idx = int(np.argmax(emp + bonus))
        r = (rng.pareto(2.1) + 1.0) * (true_means[idx] / 2.0)
        # Apply truncation per Bubeck et al.: keep r if |r| <= u_t
        if abs(r) > u_t:
            r = 0.0
        pulls[idx] += 1
        sums[idx] += r
        pseudo_regret += best - true_means[idx]
    return {"pseudo_regret": float(pseudo_regret), "K": K, "T": T,
            "best_arm_pulls": int(pulls.max())}


BASELINES: dict[str, Callable[[dict, int], dict]] = {
    "mc_european_call_lognormal": kernel_mc_european_call_lognormal,
    "empirical_var_sliding_window": kernel_empirical_var_sliding_window,
    "dense_linsolve": kernel_dense_linsolve,
    "svm_linear_primal": kernel_svm_linear_primal,
    "svm_rbf_sklearn": kernel_svm_rbf_sklearn,
    "ucb_heavy_tailed": kernel_ucb_heavy_tailed,
}


# ---------------------------------------------------------------------------
# Measurement loop
# ---------------------------------------------------------------------------

def _instance_path_for(label: str) -> Path:
    """Locate instance.json for a label by importing the registry lazily."""
    from p4_experiments.core.run_unit import _LABEL_TO_INSTANCE
    p = _LABEL_TO_INSTANCE.get(label)
    if p is None:
        raise KeyError(f"Label {label!r} not in _LABEL_TO_INSTANCE registry")
    return p


def _load_params(label: str) -> tuple[dict, str]:
    inst_path = _instance_path_for(label)
    inst = json.loads(inst_path.read_text(encoding="utf-8"))
    params = inst.get("parameters") or inst.get("instance", {}).get("parameters", {})
    return params, str(inst_path)


def _current_faithful_labels() -> list[str]:
    cohort = json.loads(COHORT_PATH.read_text(encoding="utf-8"))
    return sorted(
        label for label, entry in cohort["labels"].items()
        if entry.get("fidelity") == "F" or entry.get("paper_fidelity") == "F"
    )


def measure(label: str, kernel_name: str, params: dict, base_seed: int = 0) -> dict:
    """Run kernel N_REPEATS times with seed offsets, capped at BUDGET_S each."""
    fn = BASELINES[kernel_name]
    times = []
    estimates = []
    started = datetime.now(timezone.utc).isoformat()
    for r in range(N_REPEATS):
        seed = base_seed + r
        # Soft-budget: kernel call itself is fast for our sizes; we record
        # the wall-clock and bail (advisory) if it exceeds BUDGET_S.
        t0 = time.perf_counter()
        out = fn(params, seed)
        elapsed = time.perf_counter() - t0
        times.append(elapsed)
        estimates.append(out)
        if elapsed > BUDGET_S:
            # Record the over-budget run but stop further repeats
            break
    arr = np.array(times)
    return {
        "kernel": kernel_name,
        "n_repeats_completed": len(times),
        "wall_clock_seconds_median": float(np.median(arr)),
        "wall_clock_seconds_iqr": [float(np.quantile(arr, 0.25)), float(np.quantile(arr, 0.75))],
        "wall_clock_seconds_per_repeat": [float(t) for t in times],
        "kernel_outputs_per_repeat": estimates,
        "started_utc": started,
        "completed_utc": datetime.now(timezone.utc).isoformat(),
        "single_thread_note": SINGLE_THREAD_NOTE,
        "thread_env": {
            "OMP_NUM_THREADS": os.environ.get("OMP_NUM_THREADS"),
            "MKL_NUM_THREADS": os.environ.get("MKL_NUM_THREADS"),
            "OPENBLAS_NUM_THREADS": os.environ.get("OPENBLAS_NUM_THREADS"),
        },
    }


def run_label(label: str) -> list[Path]:
    spec = LABEL_BASELINES.get(label)
    if spec is None:
        raise KeyError(f"No Phase 8b spec for label {label!r}")
    params, inst_path = _load_params(label)
    written: list[Path] = []
    for variant_key in ("paper_named", "silo_default"):
        kspec = spec.get(variant_key)
        if kspec is None:
            continue
        kernel_name, kkwargs = kspec
        merged_params = {**params, **kkwargs}
        result = measure(label, kernel_name, merged_params)
        rec = {
            "schema_version": "phase8b.1.0",
            "label": label,
            "variant": variant_key,
            "kernel": kernel_name,
            "instance_path": inst_path,
            "instance_parameters": params,
            "note": spec.get("note", ""),
            "baseline_relationship": spec.get("baseline_relationship", "paper_named_exact"),
            "measurement": result,
            "phase": "phase8b_classical_baseline",
            "operator_decisions_ref": "DECISIONS_LOG.md 2026-04-19 Phase 8b",
            **_baseline_scale_metadata(spec, variant_key),
        }
        out_path = OUT_DIR / f"{label}_{variant_key}.json"
        out_path.write_text(json.dumps(rec, indent=2), encoding="utf-8")
        written.append(out_path)
        print(f"  [{label}/{variant_key}] kernel={kernel_name} "
              f"median={result['wall_clock_seconds_median']:.4g}s "
              f"iqr={result['wall_clock_seconds_iqr']} -> {out_path.name}")
    return written


def main(argv: list[str] | None = None) -> int:
    import argparse, sys
    parser = argparse.ArgumentParser(description="Phase 8b classical-baseline runner")
    parser.add_argument("--labels", default="",
                        help="Comma-separated label subset (e.g. SD13,SP8). "
                             "Default: run all labels in LABEL_BASELINES.")
    parser.add_argument("--skip-existing", action="store_true",
                        help="Skip a label if its <label>_paper_named.json record "
                             "file already exists in the output directory.")
    args = parser.parse_args(argv if argv is not None else sys.argv[1:])

    print(f"[Phase 8b] starting; output -> {OUT_DIR.relative_to(ROOT)}")
    print(f"[Phase 8b] {SINGLE_THREAD_NOTE}")
    print(f"[Phase 8b] N_REPEATS={N_REPEATS} BUDGET_S={BUDGET_S}")
    if args.labels.strip():
        requested = [s.strip() for s in args.labels.split(",") if s.strip()]
        unknown = [l for l in requested if l not in LABEL_BASELINES]
        if unknown:
            print(f"[Phase 8b] ERROR: unknown labels {unknown}; "
                  f"known: {sorted(LABEL_BASELINES)}")
            return 2
        labels = requested
    else:
        labels = _current_faithful_labels()
        missing = [label for label in labels if label not in LABEL_BASELINES]
        if missing:
            print(f"[Phase 8b] ERROR: current Faithful labels missing specs: {missing}")
            return 3
    if args.skip_existing:
        before = len(labels)
        labels = [l for l in labels if not (OUT_DIR / f"{l}_paper_named.json").exists()]
        print(f"[Phase 8b] --skip-existing: {before - len(labels)} labels already "
              f"have records; running {len(labels)} new.")
    print(f"[Phase 8b] {len(labels)} labels to measure: {labels}")
    all_written: list[Path] = []
    for lid in labels:
        try:
            all_written.extend(run_label(lid))
        except Exception as e:
            print(f"  [{lid}] ERROR {type(e).__name__}: {e}")
    print(f"[Phase 8b] done; {len(all_written)} record files written")
    # Self-record phase status so run_pipeline's --resume can skip
    # this expensive measurement step on subsequent invocations.
    cohort = json.loads(COHORT_PATH.read_text(encoding="utf-8"))
    current_faithful = _current_faithful_labels()
    labels_with_records = [
        label for label in current_faithful
        if (OUT_DIR / f"{label}_paper_named.json").exists()
    ]
    missing_records = sorted(set(current_faithful) - set(labels_with_records))
    ps = cohort.get("_phase_status")
    if not isinstance(ps, dict):
        ps = {}
    ps["phase8b_run"] = {
        "status": "complete" if not missing_records else "incomplete",
        "completed_utc": datetime.now(timezone.utc).isoformat(),
        "labels_attempted": len(labels),
        "records_written": len(all_written),
        "current_faithful_labels": current_faithful,
        "labels_with_paper_named_records": labels_with_records,
        "missing_paper_named_records": missing_records,
        "n_repeats": N_REPEATS,
        "budget_seconds": BUDGET_S,
        "results_dir": str(OUT_DIR.relative_to(ROOT)).replace("\\", "/"),
    }
    cohort["_phase_status"] = ps
    COHORT_PATH.write_text(json.dumps(cohort, indent=2), encoding="utf-8")
    return 0 if not missing_records else 1


if __name__ == "__main__":
    raise SystemExit(main())
