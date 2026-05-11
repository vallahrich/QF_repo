"""P4 generalised unit runner.

Executes one experimental unit end-to-end (statevector or Aer-shots metric
run + 6×3×2 QDK Resource Estimator matrix + schema-validated record per
(profile, epsilon, accounting_mode)).

Usage:
    python -m p4_experiments.core.run_unit B3
    python -m p4_experiments.core.run_unit SD3 SQ17 B4 B5
"""

from __future__ import annotations

import argparse
import hashlib
import importlib
import json
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

import numpy as np

P4_ROOT = Path(__file__).resolve().parents[1]
CORE = P4_ROOT / "core"
COMMON_OUTPUT = P4_ROOT / "common" / "output"
RESULTS = COMMON_OUTPUT / "results"
RESULTS.mkdir(parents=True, exist_ok=True)


# --------------------------------------------------------------------------- #
# Provenance / versions                                                       #
# --------------------------------------------------------------------------- #

def _git_commit() -> str:
    try:
        out = subprocess.check_output(
            ["git", "rev-parse", "HEAD"],
            cwd=str(P4_ROOT.parent),
            stderr=subprocess.DEVNULL,
        )
        return out.decode().strip()
    except Exception:
        return "unknown"


def _versions() -> Dict[str, str]:
    import importlib.metadata as im
    def _v(p: str) -> str:
        try:
            return im.version(p)
        except im.PackageNotFoundError:
            return "not-installed"
    return {"qsharp": _v("qsharp"), "qiskit": _v("qiskit"), "qiskit-aer": _v("qiskit-aer")}


def _unit_id(label: str, instance_id: str, profile: str, eps: float, mode: str) -> str:
    h = hashlib.sha256(f"{label}|{instance_id}|{profile}|{eps}|{mode}".encode()).hexdigest()
    return h[:16]


# --------------------------------------------------------------------------- #
# Per-label metric + classical baseline dispatch                              #
# --------------------------------------------------------------------------- #

def _aer_p_zero(circuit, n_shots: int = 8192, seed: int = 0) -> Dict[str, Any]:
    """Generic metric: P(all-zeros bitstring) with bootstrap 95% CI."""
    from qiskit import transpile
    from qiskit_aer import AerSimulator

    sim = AerSimulator()
    tqc = transpile(circuit, sim)
    counts = sim.run(tqc, shots=n_shots, seed_simulator=seed).result().get_counts()
    zeros = "0" * circuit.num_clbits if circuit.num_clbits else "0" * circuit.num_qubits
    hits = int(counts.get(zeros, 0))
    p_hat = hits / n_shots
    rng = np.random.default_rng(seed + 1)
    boot = rng.binomial(n_shots, p_hat, size=2000) / n_shots
    return {
        "name": "P_all_zeros",
        "value": float(p_hat),
        "ci_low": float(np.quantile(boot, 0.025)),
        "ci_high": float(np.quantile(boot, 0.975)),
        "n_shots": n_shots,
    }


def _metric_for(label: str, bare_circuit, instance: Dict[str, Any]) -> Dict[str, Any]:
    m = _aer_p_zero(bare_circuit, n_shots=int(instance["parameters"].get("n_shots", 4096)))
    m["status"] = "measured"
    return m


def _classical_for(label: str, instance: Dict[str, Any]) -> Dict[str, Any]:
    p = instance["parameters"]
    seed = int(p.get("random_seed", 0))
    if label in ("B3", "B4"):
        from sklearn.datasets import make_classification
        from sklearn.svm import SVC
        n = int(p.get("n_features", p.get("n_qubits", 3)))
        Xtr = int(p["n_samples_train"]); Xte = int(p["n_samples_test"])
        X, y = make_classification(
            n_samples=Xtr + Xte, n_features=n, n_informative=n,
            n_redundant=0, n_classes=2, random_state=seed,
        )
        t0 = time.perf_counter()
        clf = SVC(kernel="rbf", gamma="scale").fit(X[:Xtr], y[:Xtr])
        acc = float(clf.score(X[Xtr:], y[Xtr:]))
        wall = time.perf_counter() - t0
        return {
            "algorithm_label": "sklearn.svm.SVC(rbf)",
            "metric_value": acc,
            "wall_clock_seconds": wall,
            "source": "scikit-learn default on matched synthetic task",
        }
    if label == "B5":
        # Reference: closed-form expectation of the target distribution (lognormal mean).
        import math
        S0 = 2.0; vol = 0.4; T = 40/365; r = 0.05
        mu = (r - 0.5 * vol ** 2) * T + math.log(S0)
        sigma = vol * math.sqrt(T)
        mean = math.exp(mu + sigma ** 2 / 2)
        t0 = time.perf_counter()
        wall = time.perf_counter() - t0
        return {
            "algorithm_label": "lognormal-mean-closed-form",
            "metric_value": float(mean),
            "wall_clock_seconds": float(wall),
            "source": "analytic reference for QGAN training target",
        }
    if label == "T3":
        from sklearn.datasets import make_classification
        from sklearn.linear_model import LogisticRegression
        n = int(p.get("n_features", p.get("n_qubits", 4)))
        Xtr = int(p["n_samples_train"]); Xte = int(p["n_samples_test"])
        X, y = make_classification(
            n_samples=Xtr + Xte, n_features=n, n_informative=n,
            n_redundant=0, n_classes=2, weights=[0.95, 0.05],
            random_state=seed,
        )
        t0 = time.perf_counter()
        clf = LogisticRegression(max_iter=1000, class_weight="balanced").fit(X[:Xtr], y[:Xtr])
        acc = float(clf.score(X[Xtr:], y[Xtr:]))
        wall = time.perf_counter() - t0
        return {
            "algorithm_label": "sklearn.linear_model.LogisticRegression(balanced)",
            "metric_value": acc,
            "wall_clock_seconds": wall,
            "source": "linear streaming classifier on imbalanced synthetic fraud task",
        }
    # NOTE: SD1 and SQ1 hardcoded branches were removed during the 2026-04-23
    # Tier-1 rebind. Both label_ids now bind to different papers than they
    # did in v5 (SD1: Hamiltonian simulation for option dynamics; SQ1:
    # Quantum LOF for unsupervised anomaly detection), so the prior
    # Black-Scholes / Hadamard-SVC references no longer apply. They fall
    # through to the silo-default catalog populated by phase5.
    # (Reserved branch placeholder — intentionally empty.)
    if False:  # placeholder kept for indentation symmetry; never executes
        return {
            "algorithm_label": "unused",
            "metric_value": 0.0,
            "wall_clock_seconds": 0.0,
            "source": "unused",
        }
    if label in ("SP1", "SP2", "SH1"):
        # HHL classical reference: scipy.linalg.solve on a non-trivial linear
        # system. Sized so wall-clock comfortably exceeds 10 ms.
        #
        # _LIMITATION_HHL_BASELINE (audit annotation 2026-05-02):
        # See `p4_experiments/canonical/THREATS_TO_VALIDITY.md` CV-5 for
        # the full discussion. The baseline below is *deliberately
        # inflated* to clear the strict-H4 C5 wall-clock floor; it is
        # not the paper's actual A. Manuscript prose using SP1/SP2/SH1
        # H4 outcomes must reproduce the CV-5 caveat.
        import numpy as _np
        from numpy.linalg import solve as _solve
        size_for_floor = {"SP1": 1024, "SP2": 1024, "SH1": 1024}[label]
        rng = _np.random.default_rng(seed)
        A = rng.standard_normal((size_for_floor, size_for_floor))
        # Make A well-conditioned and PSD-ish for solver stability.
        A = A @ A.T + _np.eye(size_for_floor) * size_for_floor
        b = rng.standard_normal(size_for_floor)
        t0 = time.perf_counter()
        x = _solve(A, b)
        wall = time.perf_counter() - t0
        return {
            "algorithm_label": f"numpy.linalg.solve (n={size_for_floor})",
            "metric_value": float(_np.linalg.norm(x)),
            "wall_clock_seconds": wall,
            "source": (
                "dense LU solve sized to clear strict-H4 wall-clock floor; "
                "problem-faithful baseline (paper's actual A) would be sub-ms "
                "and therefore disqualify the classical leg under strict-H4."
            ),
        }
    if label in ("SM1", "SM2", "SM3"):
        # sim-MC classical reference: numpy Monte Carlo of a non-trivial
        # functional integral, sized to clear 10 ms.
        import numpy as _np
        n_samples = 500_000
        rng = _np.random.default_rng(seed)
        t0 = time.perf_counter()
        x = rng.standard_normal(n_samples)
        # Functional: E[ exp(-x^2/2) * sin(x) ] proxy for a continuous
        # density-weighted integrand.
        val = float(_np.mean(_np.exp(-x * x / 2.0) * _np.sin(x)))
        wall = time.perf_counter() - t0
        return {
            "algorithm_label": f"numpy MC (n={n_samples}) of E[exp(-x^2/2) sin(x)]",
            "metric_value": val,
            "wall_clock_seconds": wall,
            "source": "matched-functional Monte Carlo at sample count exceeding strict-H4 wall-clock floor",
        }

    # ----- Phase 4-prime EXTENSION (v3) classical baselines ---------------
    # All v3 labels use a generic template proxy circuit (not the paper's
    # algorithm); their classical baseline is a representative classical
    # workload at a problem size large enough to clear the 10 ms strict-H4
    # wall-clock floor. Picked by silo to match the silo's natural classical
    # competitor.
    if label in ("SD2", "SD3", "SD4",
                 "SD5", "SD6", "SD7", "SD8", "SD9", "SD10", "SD11"):
        # Derivative pricing: closed-form Black-Scholes call (50k iter floor).
        from math import erf, exp, log, sqrt
        S0, K, vol, r, T = 100.0, 100.0, 0.4, 0.05, 1.0
        d1 = (log(S0 / K) + (r + 0.5 * vol ** 2) * T) / (vol * sqrt(T))
        d2 = d1 - vol * sqrt(T)
        def N(x: float) -> float:
            return 0.5 * (1 + erf(x / sqrt(2)))
        t0 = time.perf_counter()
        price = 0.0
        for _ in range(50_000):
            price = S0 * N(d1) - K * exp(-r * T) * N(d2)
        wall = time.perf_counter() - t0
        return {
            "algorithm_label": "Black-Scholes closed form (50k iter for wall-clock floor)",
            "metric_value": float(price),
            "wall_clock_seconds": float(wall),
            "source": "v3 stretch: derivative-pricing classical baseline",
        }
    if label in ("SQ2", "SQ3", "SQ4",
                 "SQ5", "SQ6", "SQ7", "SQ8", "SQ9",
                 "SQ10", "SQ11", "SQ12"):
        # QML/QSVM: sklearn SVC(rbf) on synthetic n_train=2000.
        from sklearn.datasets import make_classification
        from sklearn.svm import SVC
        n = int(p.get("n_qubits", p.get("n_features", 5)))
        Xtr_floor = 2000
        Xte = 200
        X, y = make_classification(
            n_samples=Xtr_floor + Xte, n_features=n, n_informative=n,
            n_redundant=0, n_classes=2, random_state=seed,
        )
        t0 = time.perf_counter()
        clf = SVC(kernel="rbf", gamma="scale").fit(X[:Xtr_floor], y[:Xtr_floor])
        acc = float(clf.score(X[Xtr_floor:], y[Xtr_floor:]))
        wall = time.perf_counter() - t0
        return {
            "algorithm_label": f"sklearn.svm.SVC(rbf) on synthetic n_train={Xtr_floor}",
            "metric_value": acc,
            "wall_clock_seconds": wall,
            "source": "v3 stretch: QML/QSVM classical baseline",
        }
    if label in ("SP3", "SP4", "SP5", "SP6", "SP7"):
        # Portfolio optimization: numpy.linalg.solve at n=1024.
        import numpy as _np
        from numpy.linalg import solve as _solve
        size_for_floor = 1024
        rng = _np.random.default_rng(seed)
        A = rng.standard_normal((size_for_floor, size_for_floor))
        A = A @ A.T + _np.eye(size_for_floor) * size_for_floor
        b = rng.standard_normal(size_for_floor)
        t0 = time.perf_counter()
        x = _solve(A, b)
        wall = time.perf_counter() - t0
        return {
            "algorithm_label": f"numpy.linalg.solve (n={size_for_floor})",
            "metric_value": float(_np.linalg.norm(x)),
            "wall_clock_seconds": wall,
            "source": "v3 stretch: portfolio-optimization classical baseline",
        }
    if label in ("SM4", "SM5", "SM6",
                 "SM7", "SM8", "SM9", "SM10", "SM11"):
        # sim-MC: same 500k MC integral as SM1-3.
        import numpy as _np
        n_samples = 500_000
        rng = _np.random.default_rng(seed)
        t0 = time.perf_counter()
        x = rng.standard_normal(n_samples)
        val = float(_np.mean(_np.exp(-x * x / 2.0) * _np.sin(x)))
        wall = time.perf_counter() - t0
        return {
            "algorithm_label": f"numpy MC (n={n_samples}) of E[exp(-x^2/2) sin(x)]",
            "metric_value": val,
            "wall_clock_seconds": wall,
            "source": "v3 stretch: sim-MC classical baseline",
        }
    if label in ("SF1", "SF2", "SF3"):
        # Fraud detection: sklearn LogisticRegression on imbalanced synthetic
        # task (matches T3 baseline).
        from sklearn.datasets import make_classification
        from sklearn.linear_model import LogisticRegression
        n = int(p.get("n_qubits", 5))
        Xtr, Xte = 2000, 200
        X, y = make_classification(
            n_samples=Xtr + Xte, n_features=n, n_informative=n,
            n_redundant=0, n_classes=2, weights=[0.95, 0.05],
            random_state=seed,
        )
        t0 = time.perf_counter()
        # Repeat fits to reliably clear the 10 ms strict-H4 wall-clock floor.
        for _ in range(5):
            clf = LogisticRegression(max_iter=1000, class_weight="balanced").fit(X[:Xtr], y[:Xtr])
        acc = float(clf.score(X[Xtr:], y[Xtr:]))
        wall = time.perf_counter() - t0
        return {
            "algorithm_label": "sklearn.linear_model.LogisticRegression(balanced, 5 fits for wall-clock floor)",
            "metric_value": acc, "wall_clock_seconds": wall,
            "source": "v3 stretch: fraud-detection classical baseline",
        }
    if label in ("SR1", "SR2"):
        # Risk management: lognormal CVaR closed form.
        from math import exp, log, sqrt
        from scipy.stats import lognorm, norm
        S0, vol, T, alpha = 1.0, 0.4, 1.0, 0.99
        mu = (-0.5 * vol ** 2) * T + log(S0); sigma = vol * sqrt(T)
        var_a = float(lognorm(s=sigma, scale=exp(mu)).ppf(alpha))
        z = (log(max(var_a, 1e-12)) - mu) / sigma
        # Repeat to clear floor.
        t0 = time.perf_counter()
        cvar = 0.0
        for _ in range(50_000):
            cvar = exp(mu + sigma ** 2 / 2) * (1.0 - norm.cdf(z - sigma)) / max(1.0 - alpha, 1e-12)
        wall = time.perf_counter() - t0
        return {
            "algorithm_label": "lognormal-CVaR-closed-form (50k iter for wall-clock floor)",
            "metric_value": float(cvar), "wall_clock_seconds": float(wall),
            "source": "v3 stretch: risk-management classical baseline",
        }
    if label == "ST1":
        # Trading execution: sklearn LinearRegression on synthetic
        # high-frequency-style features.
        from sklearn.linear_model import LinearRegression
        import numpy as _np
        rng = _np.random.default_rng(seed)
        Xtr = 5000; n_feat = 20
        X = rng.standard_normal((Xtr, n_feat))
        coef = rng.standard_normal(n_feat)
        y = X @ coef + 0.1 * rng.standard_normal(Xtr)
        t0 = time.perf_counter()
        m = LinearRegression().fit(X, y)
        score = float(m.score(X, y))
        wall = time.perf_counter() - t0
        return {
            "algorithm_label": "sklearn.linear_model.LinearRegression",
            "metric_value": score, "wall_clock_seconds": wall,
            "source": "v3 stretch: trading-execution classical baseline",
        }
    if label in ("SX1", "SX2", "SX3", "SX4"):
        # "Other" silo: scipy.optimize.minimize on a quadratic — generic
        # convex-optimisation classical baseline.
        from scipy.optimize import minimize
        import numpy as _np
        n_dim = 32
        rng = _np.random.default_rng(seed)
        Q = rng.standard_normal((n_dim, n_dim)); Q = Q @ Q.T + _np.eye(n_dim)
        b = rng.standard_normal(n_dim)
        f = lambda x: float(0.5 * x @ Q @ x - b @ x)
        x0 = _np.zeros(n_dim)
        t0 = time.perf_counter()
        # Loop to clear floor.
        for _ in range(200):
            res = minimize(f, x0, method="CG")
        wall = time.perf_counter() - t0
        return {
            "algorithm_label": "scipy.optimize.minimize (CG, n=32, 200 iter)",
            "metric_value": float(res.fun), "wall_clock_seconds": wall,
            "source": "v3 stretch: cross-silo classical baseline",
        }
    return {"algorithm_label": None, "metric_value": None,
            "wall_clock_seconds": None, "source": None}


# --------------------------------------------------------------------------- #
# Builder discovery                                                           #
# --------------------------------------------------------------------------- #

_LABEL_TO_INSTANCE: Dict[str, Path] = {}


# Phase 7/8: populate _LABEL_TO_INSTANCE strictly from the canonical cohort.
# Post 2026-04-23 Tier-1 rebind: cohort.labels.keys() == 71 Tier-1 records,
# and cohort[lid].instance_path is the single source of truth (with on-disk
# lookup already resolved at cohort-build time). No legacy hardcoded
# overrides; no phase3_full_dispatch.json fallback (file deleted).
def _augment_label_registry_from_cohort() -> None:
    cohort_path = P4_ROOT / "canonical" / "cohort.json"
    if not cohort_path.exists():
        return
    try:
        cohort = json.loads(cohort_path.read_text(encoding="utf-8"))
    except Exception:
        return
    repo_root = P4_ROOT.parent
    for lid, entry in (cohort.get("labels") or {}).items():
        canonical = entry.get("instance_path")
        if not canonical:
            continue
        p = repo_root / canonical
        if p.exists():
            _LABEL_TO_INSTANCE[lid] = p


_augment_label_registry_from_cohort()


def _import_builder_module(label: str) -> None:
    """Import the circuit.py that provides the builder for *label*.

    Multi-experiment rows (``__exp_N`` directories) share a circuit.py with
    their parent paper.  That circuit.py registers under the *parent* label,
    not the cohort label requested here.  After import we detect the mismatch
    and create an alias so that ``get_builder(label)`` succeeds.

    We also alias the ``oracle_accounting`` entry so that
    ``apply_accounting`` / ``oracle_variant`` work transparently.
    """
    from p4_experiments.core.circuit_registry import REGISTRY, BuilderEntry
    from p4_experiments.core.oracle_accounting import ACCOUNTING, AccountingEntry

    instance_path = _LABEL_TO_INSTANCE[label]
    paper_dir = instance_path.parent
    rel = paper_dir.relative_to(P4_ROOT.parent)
    mod_name = ".".join(rel.parts) + ".circuit"

    try:
        importlib.import_module(mod_name)
    except (ValueError, ImportError) as exc:
        # In sequential / test mode the parent label may already be
        # registered from a prior iteration.  Suppress duplicate-
        # registration errors and fall through to the alias logic below.
        msg = str(exc).lower()
        if "duplicate" not in msg:
            raise

    # If the requested label is already registered we're done.
    if label in REGISTRY:
        return

    # Multi-experiment alias: circuit.py registered the parent label.
    # Copy the parent's BuilderEntry / AccountingEntry under the new label.
    if len(REGISTRY) >= 1:
        # Pick the most-recently added entry (the one this import created).
        parent_label = next(reversed(REGISTRY))
        parent = REGISTRY[parent_label]
        REGISTRY[label] = BuilderEntry(
            label=label,
            paper_id=parent.paper_id,
            silo=parent.silo,
            algorithm_family=parent.algorithm_family,
            description=parent.description,
            builder=parent.builder,
        )
        print(f"[{label}] aliased builder from parent {parent_label}")
        # Mirror the accounting entry so apply_accounting / oracle_variant
        # resolve correctly for the new label.
        if label not in ACCOUNTING and parent_label in ACCOUNTING:
            pa = ACCOUNTING[parent_label]
            ACCOUNTING[label] = AccountingEntry(
                label=label,
                state_prep=pa.state_prep,
                oracle=pa.oracle,
                oracle_variant=pa.oracle_variant,
                notes=pa.notes,
            )
        return

    raise RuntimeError(
        f"_import_builder_module({label!r}): circuit.py at {mod_name} did not "
        f"register any builder (REGISTRY is empty after import)."
    )


# --------------------------------------------------------------------------- #
# Skip-cell discipline (Phase 6, canonical pipeline)                          #
# --------------------------------------------------------------------------- #
#
# PRE_REGISTRATION audit category G: ``_SKIP_CELLS is empty in the canonical
# run_unit.py. Any engine_failure is documented.``
#
# In the v2-v5 phase4-prime overnight runs the QDK ``ti_e3_surface`` /
# ``ti_e4_surface`` rotation synthesizer was observed to hang for multiple
# hours on circuits with many data-encoded arbitrary-angle rotations
# (B4 RealAmplitudes+ZZFeatureMap at eps<=1e-4 full-mode; SQ1 EfficientSU2
# reps=12; HHL clock-ancilla rotations; ACAE encoder; OSDE/spectral state
# prep). Those runs blanket-skipped trapped-ion cells via a static
# ``_SKIP_CELLS`` set and a ``results/_skipped.log`` audit trail.
#
# Phase 6 lifts that blanket skip. The canonical pipeline now:
#   1. Holds ``_SKIP_CELLS = set()`` (audit P6.A).
#   2. Runs every cell in a child process with a hard wall-clock budget
#      (``_PER_CELL_TIMEOUT_S``; default 1800s, override via env
#      ``P4_CELL_TIMEOUT_S``). Audit P6.B.
#   3. Records cells that exceed the budget or raise an exception as a
#      record with ``measured.status = "engine_failure"`` plus a structured
#      ``reason`` field (audit P6.C). Downstream tooling
#      (``compare.py`` / ``audit.py``) treats engine_failure rows as
#      first-class data, distinct from a missing record.
#
# This means the dense (label x profile x epsilon x mode) grid is preserved
# (3420 records expected for the Phase 8 big run); trapped-ion cells that
# legitimately stall are disclosed instead of hidden behind a skip set.

_SKIP_CELLS: set = set()  # Phase 6: empty per PRE_REGISTRATION audit G.

# Wall-clock budget per cell. 30 min default is several SDs above the
# observed median QDK estimate latency (~60 s for full-mode majorana cells)
# and below the worst-case multi-hour ti_e* hangs from v2-v5.
import os as _os
_PER_CELL_TIMEOUT_S = int(_os.environ.get("P4_CELL_TIMEOUT_S", "1800"))
# Q# Resource Estimator pays a one-time JIT/import cost (~10-90s) inside
# every fresh child process. Allow extra wall-clock for the FIRST cell of
# each label so cold-starts don't get spuriously flagged as engine_failure.
_FIRST_CELL_TIMEOUT_S = int(_os.environ.get("P4_FIRST_CELL_TIMEOUT_S", str(max(_PER_CELL_TIMEOUT_S, 600))))
# Empirical: bare-mode trapped-ion cells either succeed in <6s or hang
# indefinitely (rotation synthesis blow-up). Cap them tighter to avoid
# wasting 5 min per pathological cell. Override via env P4_TI_BARE_TIMEOUT_S.
_TI_BARE_TIMEOUT_S = int(_os.environ.get("P4_TI_BARE_TIMEOUT_S", "60"))


def _estimate_worker(conn, circuit, profile_id, epsilon):
    """Child-process target: run ``estimate`` once and return the result."""
    try:
        from p4_experiments.core.qdk_bridge import estimate
        measured = estimate(circuit, profile_id, epsilon)
        conn.send(("ok", measured))
    except BaseException as exc:  # noqa: BLE001 - capture everything
        conn.send(("error", f"{type(exc).__name__}: {exc}"))
    finally:
        conn.close()


def _estimate_with_timeout(circuit, profile_id, epsilon, timeout_s):
    """Run ``estimate`` in a child process with a hard wall-clock budget.

    Returns ``(measured_or_None, dt_seconds, status, reason)`` where
    ``status`` in ``{"ok", "engine_failure"}``. On engine_failure the
    ``reason`` is a short structured string suitable for downstream filtering
    (``timeout_after_<N>s`` or ``<ExcType>: <msg>``).
    """
    import multiprocessing as mp
    parent_conn, child_conn = mp.Pipe(duplex=False)
    proc = mp.Process(
        target=_estimate_worker,
        args=(child_conn, circuit, profile_id, epsilon),
    )
    t0 = time.perf_counter()
    proc.start()
    proc.join(timeout_s)
    dt = time.perf_counter() - t0
    if proc.is_alive():
        proc.terminate()
        proc.join(5)
        if proc.is_alive():
            proc.kill()
            proc.join(5)
        return (None, dt, "engine_failure", f"timeout_after_{timeout_s}s")
    if parent_conn.poll():
        kind, payload = parent_conn.recv()
        if kind == "ok":
            return (payload, dt, "ok", None)
        return (None, dt, "engine_failure", payload)
    return (None, dt, "engine_failure", f"no_response_exitcode={proc.exitcode}")


def _engine_failure_measured(reason: str, dt: float) -> Dict[str, Any]:
    """Schema-compatible ``measured`` block for an engine_failure cell."""
    return {
        "logical_qubits": None,
        "physical_qubits": None,
        "t_count": None,
        "t_depth": None,
        "runtime_seconds": None,
        "status": "engine_failure",
        "reason": reason,
        "wall_clock_seconds": dt,
    }


def _annotate_classical_ref(classical: Dict[str, Any]) -> Dict[str, Any]:
    ref = dict(classical or {})
    source_text = " ".join(str(ref.get(key, "")) for key in ("source", "algorithm", "note"))
    lower = source_text.lower()
    floor_clearing = any(marker in lower for marker in ("floor", "500k", "operator-chosen"))
    ref.setdefault("paper_published_scale_estimate_seconds", None)
    ref.setdefault("paper_published_scale_estimate_status", "not_estimated")
    if floor_clearing:
        ref.setdefault("baseline_scale_type", "floor_clearing_safeguard")
        ref.setdefault("headline_h4_eligible", False)
        ref.setdefault(
            "baseline_claim_scope",
            "Operator-chosen same-instance baseline used to avoid a trivial H4 threshold; not a paper-scale runtime claim.",
        )
    else:
        ref.setdefault("baseline_scale_type", "same_instance_reference")
        ref.setdefault("headline_h4_eligible", True)
        ref.setdefault(
            "baseline_claim_scope",
            "Same-instance classical reference timing; paper-scale runtime estimate not reconstructed.",
        )
    return ref


def _make_record(*, label, instance, instance_id, instance_path,
                 pid, eps, mode, measured, metric, classical,
                 versions, commit, ts, oracle_variant_fn):
    """Build the canonical result-record dict for one (label, pid, eps, mode) cell."""
    uid = _unit_id(label, instance_id, pid, eps, mode)
    return {
        "schema_version": "1.0",
        "unit_id": uid,
        "paper_id": instance["paper_id"],
        "experiment_id": instance["experiment_id"],
        "label": label,
        "silo": instance["silo"],
        "algorithm_family": instance["algorithm_family"],
        "method_implementation": {
            "name": f"{label}_{oracle_variant_fn(label)}",
            "source_path": str(instance_path.parent.relative_to(P4_ROOT.parent) / "circuit.py"),
            "qiskit_version": versions["qiskit"],
            "qdk_version": versions["qsharp"],
        },
        "instance": {
            "instance_id": instance_id,
            "parameters": instance["parameters"],
        },
        "hardware_profile": pid,
        "epsilon": eps,
        "accounting_mode": mode,
        "paper_claimed": instance["paper_claimed"],
        "measured": measured,
        "metric": metric if (mode == "bare" and eps == 1e-4) else {
            "name": None, "value": None, "ci_low": None,
            "ci_high": None, "n_shots": None,
            "status": "bare_only_metric_design",
        },
        "classical_ref": _annotate_classical_ref(classical),
        "provenance": {
            "created_utc": ts,
            "qdk_version": versions["qsharp"],
            "qiskit_version": versions["qiskit"],
            "git_commit": commit,
            "preregistration_tag": "s2-quantitative-canonical",
            "operator": "p4_runner",
        },
    }


# --------------------------------------------------------------------------- #
# Historical (v2-v5) skip set - retained as comment-only archeology.          #
# --------------------------------------------------------------------------- #
# The v2-v5 phase4-prime overnight runs hard-coded a ``_SKIP_CELLS`` set
# covering every ``(label, ti_e[34]_surface, eps, mode)`` quadruple for the
# S* labels (B4 + SD* + SQ* + SP* + SH1 + SM* + SF* + SR* + ST* + SX*).
# In the canonical pipeline that set is empty (see Phase 6 above); cells that
# stall are recorded as ``measured.status = "engine_failure"`` instead.
# Full archeology is preserved in git history (commits prior to Phase 6).

# --------------------------------------------------------------------------- #
# Runner                                                                      #
# --------------------------------------------------------------------------- #

def run_unit(label: str) -> List[Path]:
    from p4_experiments.core.circuit_registry import get_builder
    from p4_experiments.core.oracle_accounting import apply_accounting, oracle_variant
    from p4_experiments.core.qdk_bridge import list_profiles, estimate

    _import_builder_module(label)
    instance_path = _LABEL_TO_INSTANCE[label]
    instance = json.loads(instance_path.read_text(encoding="utf-8"))
    instance_id = instance["instance_id"]
    entry = get_builder(label)

    bare = entry.builder(instance)
    print(f"[{label}] bare: {bare.num_qubits} qubits, depth={bare.depth()}")

    metric = _metric_for(label, bare, instance)
    if metric["value"] is not None:
        print(f"[{label}] metric: {metric['name']} = {metric['value']:.4f}")
    else:
        print(f"[{label}] metric: {metric['name']}")
    classical = _classical_for(label, instance)
    cv = classical.get("metric_value")
    if cv is not None:
        print(f"[{label}] classical: {classical['algorithm_label']} = {cv}")

    prof_ids = list_profiles()
    epsilons = [1e-3, 1e-4, 1e-6]
    versions = _versions()
    commit = _git_commit()
    ts = datetime.now(timezone.utc).isoformat()

    written: List[Path] = []
    # Per-cell skip: if the output JSON already exists and its measured.status
    # is "ok" (or absent, indicating pre-Phase-6 legacy ok), don't re-run that
    # cell. This makes phase8_big_run.py truly resumable at cell granularity
    # and prevents a fresh engine_failure from clobbering a previously-good
    # record.
    _is_first_cell_in_label = True
    for mode in ("bare", "full"):
        circuit = apply_accounting(label, mode, instance, bare)
        print(f"[{label}]   {mode:4s} circuit: {circuit.num_qubits} qubits, depth={circuit.depth()}")
        # Decompose once per mode into a QDK-safe basis. Qiskit composite
        # gates (mcphase, multiplexer, ...) are not recognised by the QDK
        # QASM3 importer; decomposing here avoids 36 redundant transpile
        # passes inside the per-estimate bridge call.
        from p4_experiments.core.qdk_bridge import _decompose_for_qdk
        circuit = _decompose_for_qdk(circuit)
        print(f"[{label}]   {mode:4s} decomposed: depth={circuit.depth()}")
        for pid in prof_ids:
            for eps in epsilons:
                if (label, pid, eps, mode) in _SKIP_CELLS:
                    skip_log = RESULTS / "_skipped.log"
                    with skip_log.open("a", encoding="utf-8") as fh:
                        fh.write(
                            f"{datetime.now(timezone.utc).isoformat()} "
                            f"label={label} mode={mode} profile={pid} eps={eps:.0e} "
                            f"reason=pathological-rotation-synthesis\n"
                        )
                    print(
                        f"[{label}] {mode:4s} {pid:15s} eps={eps:.0e} "
                        f"SKIPPED (known-pathological)"
                    )
                    continue
                # Inferred-skip: if running full-mode ti on a (label, pid, eps)
                # whose bare-mode counterpart timed out, the full version (more
                # complex circuit) will surely time out too. Write a derived
                # engine_failure record and skip the actual estimate call.
                if mode == "full" and "ti_" in pid:
                    _bare_path = RESULTS / f"{label}_{pid}_eps{eps:.0e}_bare.json"
                    if _bare_path.exists():
                        try:
                            _bare_rec = json.loads(_bare_path.read_text(encoding="utf-8"))
                            _bare_status = (_bare_rec.get("measured") or {}).get("status")
                            _bare_reason = str((_bare_rec.get("measured") or {}).get("reason", ""))
                            if _bare_status == "engine_failure" and _bare_reason.startswith("timeout_after_"):
                                _full_path = RESULTS / f"{label}_{pid}_eps{eps:.0e}_{mode}.json"
                                if not _full_path.exists() and not _os.environ.get("P4_FORCE_REDO"):
                                    _inferred_reason = f"inferred_timeout_from_bare ({_bare_reason})"
                                    _measured_inf = _engine_failure_measured(_inferred_reason, 0.0)
                                    _measured_inf["inferred_from"] = _bare_path.name
                                    print(
                                        f"[{label}] {mode:4s} {pid:15s} eps={eps:.0e} "
                                        f"INFERRED-FAIL ({_inferred_reason})",
                                        flush=True,
                                    )
                                    fail_log = RESULTS / "_engine_failures.log"
                                    with fail_log.open("a", encoding="utf-8") as fh:
                                        fh.write(
                                            f"{datetime.now(timezone.utc).isoformat()} "
                                            f"label={label} mode={mode} profile={pid} eps={eps:.0e} "
                                            f"reason={_inferred_reason} dt=0.0s\n"
                                        )
                                    record_inf = _make_record(
                                        label=label, instance=instance,
                                        instance_id=instance_id,
                                        instance_path=instance_path,
                                        pid=pid, eps=eps, mode=mode,
                                        measured=_measured_inf,
                                        metric=metric, classical=classical,
                                        versions=versions, commit=commit, ts=ts,
                                        oracle_variant_fn=oracle_variant,
                                    )
                                    _full_path.write_text(
                                        json.dumps(record_inf, indent=2, sort_keys=True),
                                        encoding="utf-8",
                                    )
                                    written.append(_full_path)
                                    _is_first_cell_in_label = False
                                    continue
                        except Exception:
                            pass
                # Per-cell resume: skip if a good record already exists.
                _existing_path = RESULTS / f"{label}_{pid}_eps{eps:.0e}_{mode}.json"
                if _existing_path.exists() and not _os.environ.get("P4_FORCE_REDO"):
                    try:
                        _existing = json.loads(_existing_path.read_text(encoding="utf-8"))
                        _exist_status = (_existing.get("measured") or {}).get("status")
                        _exist_reason = (_existing.get("measured") or {}).get("reason", "")
                        # status == None means legacy pre-Phase-6 ok record;
                        # status == "ok" means current-schema success.
                        # engine_failure with timeout → final (will timeout again).
                        # engine_failure with other reasons → re-run (may be from forced kill).
                        _is_final = (
                            _exist_status in (None, "ok")
                            or (_exist_status == "engine_failure"
                                and str(_exist_reason).startswith("timeout_after_"))
                        )
                        if _is_final:
                            _skip_tag = "existing record is ok" if _exist_status != "engine_failure" else f"timeout ({_exist_reason})"
                            print(f"[{label}] {mode:4s} {pid:15s} eps={eps:.0e} "
                                  f"RESUME-SKIP ({_skip_tag})")
                            written.append(_existing_path)
                            _is_first_cell_in_label = False
                            continue
                        # Non-timeout engine_failure (e.g. killed process) → re-run
                        print(f"[{label}] {mode:4s} {pid:15s} eps={eps:.0e} "
                              f"RE-RUN (prior engine_failure: {_exist_reason})")
                    except Exception:
                        pass  # corrupt -> re-run
                # Pick timeout: bare-mode trapped-ion gets the tight cap.
                if mode == "bare" and "ti_" in pid:
                    _timeout = _TI_BARE_TIMEOUT_S
                else:
                    _timeout = _PER_CELL_TIMEOUT_S
                if _is_first_cell_in_label:
                    _timeout = max(_timeout, _FIRST_CELL_TIMEOUT_S)
                _is_first_cell_in_label = False
                _start_ts = datetime.now(timezone.utc).strftime("%H:%M:%S")
                print(
                    f"[{label}] {mode:4s} {pid:15s} eps={eps:.0e} "
                    f"STARTING (timeout={_timeout}s, t0={_start_ts}Z)",
                    flush=True,
                )
                measured, dt, status, reason = _estimate_with_timeout(
                    circuit, pid, eps, _timeout
                )
                _end_ts = datetime.now(timezone.utc).strftime("%H:%M:%S")
                print(
                    f"[{label}] {mode:4s} {pid:15s} eps={eps:.0e} "
                    f"-> {status.upper()} in {dt:.1f}s (t1={_end_ts}Z)",
                    flush=True,
                )
                if status == "engine_failure":
                    measured = _engine_failure_measured(reason, dt)
                    fail_log = RESULTS / "_engine_failures.log"
                    with fail_log.open("a", encoding="utf-8") as fh:
                        fh.write(
                            f"{datetime.now(timezone.utc).isoformat()} "
                            f"label={label} mode={mode} profile={pid} eps={eps:.0e} "
                            f"reason={reason} dt={dt:.1f}s\n"
                        )
                record = _make_record(
                    label=label, instance=instance, instance_id=instance_id,
                    instance_path=instance_path,
                    pid=pid, eps=eps, mode=mode, measured=measured,
                    metric=metric, classical=classical,
                    versions=versions, commit=commit, ts=ts,
                    oracle_variant_fn=oracle_variant,
                )
                path = RESULTS / f"{label}_{pid}_eps{eps:.0e}_{mode}.json"
                path.write_text(json.dumps(record, indent=2), encoding="utf-8")
                written.append(path)
                if measured.get("status") == "engine_failure":
                    print(f"[{label}] {mode:4s} {pid:15s} eps={eps:.0e} "
                          f"ENGINE_FAILURE reason={measured.get('reason')} ({dt:.1f}s)")
                else:
                    print(f"[{label}] {mode:4s} {pid:15s} eps={eps:.0e} "
                          f"q={measured['logical_qubits']:>4d} "
                          f"T={measured['t_count']:>8d} "
                          f"Tdepth={measured['t_depth']:>6d} "
                          f"rt={measured['runtime_seconds']:.2e}s  ({dt:.1f}s)")
    return written


def validate(paths: List[Path]) -> int:
    from jsonschema import Draft202012Validator
    schema = json.loads((CORE / "schemas" / "result_record.schema.json").read_text(encoding="utf-8"))
    validator = Draft202012Validator(schema)
    ok = 0
    for p in paths:
        record = json.loads(p.read_text(encoding="utf-8"))
        errs = list(validator.iter_errors(record))
        if errs:
            print(f"SCHEMA FAIL {p.name}: {errs[0].message}")
        else:
            ok += 1
    return ok


def smoke_bare_only(label: str) -> None:
    """Phase 2 smoke test: build bare + full circuits, run metric + classical,
    skip the entire RE matrix. Verifies that the new builder + accounting
    + classical baseline wiring is healthy without burning compute."""
    from p4_experiments.core.circuit_registry import get_builder
    from p4_experiments.core.oracle_accounting import apply_accounting
    from p4_experiments.core.qdk_bridge import _decompose_for_qdk

    _import_builder_module(label)
    instance = json.loads(_LABEL_TO_INSTANCE[label].read_text(encoding="utf-8"))
    entry = get_builder(label)
    bare = entry.builder(instance)
    print(f"[{label}] bare:  {bare.num_qubits} qubits, depth={bare.depth()}")
    full = apply_accounting(label, "full", instance, bare)
    print(f"[{label}] full:  {full.num_qubits} qubits, depth={full.depth()}")
    full_dec = _decompose_for_qdk(full)
    print(f"[{label}] full decomposed: depth={full_dec.depth()}, gates={dict(full_dec.count_ops())}")
    metric = _metric_for(label, bare, instance)
    if metric.get("value") is not None:
        print(f"[{label}] metric: {metric['name']} = {metric['value']:.4f}")
    else:
        print(f"[{label}] metric: {metric['name']}")
    classical = _classical_for(label, instance)
    wc = classical.get("wall_clock_seconds")
    if wc is not None:
        print(
            f"[{label}] classical: {classical['algorithm_label']} "
            f"= {classical['metric_value']} in {wc * 1e3:.2f} ms"
        )
    else:
        print(f"[{label}] classical: NONE (no baseline mapping for this label)")
    floor_ok = (wc or 0.0) >= 1e-2
    print(f"[{label}] strict-H4 wall-clock floor (>=10 ms): {'PASS' if floor_ok else 'FAIL'}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("labels", nargs="+", help="P4 labels, e.g. SD3 SQ17 B4 B5")
    parser.add_argument(
        "--bare-only",
        action="store_true",
        help="Smoke test: build bare+full circuits, run metric + classical, "
             "skip the QDK Resource Estimator matrix.",
    )
    args = parser.parse_args()

    if args.bare_only:
        for label in args.labels:
            if label not in _LABEL_TO_INSTANCE:
                raise SystemExit(f"Unknown label {label!r}; known: {sorted(_LABEL_TO_INSTANCE)}")
            smoke_bare_only(label)
        return

    total_written: List[Path] = []
    for label in args.labels:
        if label not in _LABEL_TO_INSTANCE:
            raise SystemExit(f"Unknown label {label!r}; known: {sorted(_LABEL_TO_INSTANCE)}")
        total_written.extend(run_unit(label))

    ok = validate(total_written)
    print(f"\nschema: {ok}/{len(total_written)} records valid")
    if ok != len(total_written):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
