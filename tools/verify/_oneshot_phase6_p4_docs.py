"""One-shot Phase-6 P4 doc edits (byte-safe; CRLF-preserving).

Per /memories/mixed-encoding-files.md, p4_experiments/canonical/*.md
files contain Latin-1 dashes (THREATS_TO_VALIDITY.md has 10 such
bytes). All read/write operations here are byte-level.

Idempotent via sentinels.

Run from repo root:
    python tools/verify/_oneshot_phase6_p4_docs.py
"""
from __future__ import annotations
from pathlib import Path


def _detect_nl(b: bytes) -> bytes:
    return b"\r\n" if b.count(b"\r\n") > 0 else b"\n"


def _to_native(text: str, nl: bytes) -> bytes:
    return text.replace("\n", nl.decode("ascii")).encode("utf-8")


# ---- 1. PRE_REGISTRATION.md: insert strict=0 callout under section 0 ----
PREREG = Path("p4_experiments/canonical/PRE_REGISTRATION.md")
b = PREREG.read_bytes()
nl = _detect_nl(b)
sentinel = b"### 0a. Tier semantics callout"
if sentinel in b:
    print("PRE_REGISTRATION.md: 0a callout already present; skipping.")
else:
    old = _to_native(
        "## 0. Status\n\n"
        "This file is the active Phase 4 canonical contract after the S2 quantitative\n"
        "source-provenance repair. It replaces any generated downstream reports that\n"
        "were tied to the earlier cohort state.\n",
        nl,
    )
    n = b.count(old)
    assert n == 1, f"PRE_REG anchor count: {n}"
    new = _to_native(
        "## 0. Status\n\n"
        "This file is the active Phase 4 canonical contract after the S2 quantitative\n"
        "source-provenance repair. It replaces any generated downstream reports that\n"
        "were tied to the earlier cohort state.\n\n"
        "### 0a. Tier semantics callout (added 2026-05-02)\n\n"
        "**STRICT TIER = 0.** No P4 cohort label is `paper-faithful-strict`. The\n"
        "H4 headline (no winners under the strict-advantage scoreboard) operates\n"
        "at the **paper-family-template tier (13 labels)** and the\n"
        "**proxy tier (58 labels)** only. Many template labels share\n"
        "`_u_proxy` (`core/templates/hhl.py`) or `grover_proxy`\n"
        "(`core/templates/qae.py`) scaffolding; the negative H4 result is robust\n"
        "*as a statement about the template family at the paper's stated scale*\n"
        "and cannot support the stronger reading \"no current finance paper passes\n"
        "any QA bar\". See [`THREATS_TO_VALIDITY.md`](THREATS_TO_VALIDITY.md) CV-5\n"
        "(HHL classical baseline inflated to clear C5 floor) and CV-6 (Hoefler\n"
        "optimistic constants) for the matched honest qualifications. The\n"
        "`paper_exact_claim_eligible` field in [`outputs/manuscript_artifacts/key_numbers.json`](outputs/manuscript_artifacts/key_numbers.json)\n"
        "is correctly 0; manuscript prose must not slip into stronger language.\n",
        nl,
    )
    PREREG.write_bytes(b.replace(old, new))
    print(f"PRE_REGISTRATION.md: insert OK; size now {PREREG.stat().st_size}")


# ---- 2. THREATS_TO_VALIDITY.md: append CV-5/6/7 ----
THREATS = Path("p4_experiments/canonical/THREATS_TO_VALIDITY.md")
b2 = THREATS.read_bytes()
nl2 = _detect_nl(b2)
sentinel2 = b"## Addendum 2026-05-02"
if sentinel2 in b2:
    print("THREATS_TO_VALIDITY.md: addendum already present; skipping.")
else:
    addendum = (
        "\n\n---\n\n"
        "## Addendum 2026-05-02 - audit-surfaced threats CV-5..CV-7\n\n"
        "The following three threats were surfaced by a senior-review pass on\n"
        "2026-05-02 and added here for completeness. They are not new design\n"
        "choices; they document *existing* construct-validity weaknesses that\n"
        "reviewers familiar with the field will press on.\n\n"
        "### CV-5. HHL classical baseline inflated to clear the strict-H4 C5 floor\n\n"
        "The classical baselines for SP1 / SP2 / SH1 (the HHL-family labels)\n"
        "in `p4_experiments/core/run_unit.py` (lines ~182-233) construct a\n"
        "**synthetic dense 1024x1024 system explicitly sized to clear the\n"
        "strict-H4 10 ms wall-clock floor**. The source comment is candid:\n"
        "\"problem-faithful baseline (paper's actual A) would be sub-ms and\n"
        "therefore disqualify the classical leg under strict-H4\". The headline\n"
        "H4 result is then computed against this inflated baseline.\n\n"
        "Because the H4 verdict is **negative** (no winners), CV-5 *helps* the\n"
        "bifurcation argument - the bar is generous and still nothing passes.\n"
        "If a future iteration produced an H4 winner, the inflated baseline\n"
        "would have to be replaced with a paper-faithful one (or a tuned\n"
        "modern competitor) before the result could be published.\n\n"
        "**Mitigation in this release:** disclosure here, in the matching\n"
        "PRE_REGISTRATION.md section 0a callout, and in the\n"
        "`outputs/manuscript_artifacts/caption_pack.md` per-figure caveat\n"
        "banner for any figure that touches SP1 / SP2 / SH1.\n\n"
        "### CV-6. Hoefler crossover figure uses optimistic constants\n\n"
        "`pipeline/phase10_hoefler_scaling_figure.py` faithfully reproduces\n"
        "Hoefler-Haner-Troyer's Table 1 fp16 numbers (A100 GPU 195 Top/s,\n"
        "ASIC 0.55 Pop/s, FT-quantum 10.5 kop/s, deadline 1e6 s) and the\n"
        "crossover formula `N* = (t_q / t_c)^(1 / (k-1))`. The constants are\n"
        "correct as-cited but optimistic for the quantum side: a 10k-logical-\n"
        "qubit fp16 Majorana machine is the limit-of-possibility scenario,\n"
        "not a near-term forecast. The figure also fixes the classical\n"
        "exponent `k = 2`; for any exponential-speedup claim, `k` is the\n"
        "whole story.\n\n"
        "**Mitigation:** disclosure here. A `k in {1.5, 2, 3}` panel sweep is\n"
        "recorded as a Stronger-version remediation item; the current figure\n"
        "should be read as one slice through that family, not as the family\n"
        "itself.\n\n"
        "### CV-7. Single-thread numpy/scipy classical baselines vs idealised future quantum\n\n"
        "Phase 8b / 8c classical baselines run as numpy + scipy + single\n"
        "thread (`OMP_NUM_THREADS=1`), while the future-quantum side is\n"
        "given the optimistic Hoefler constants from CV-6 (10k logical qubits,\n"
        "fp16 Majorana, deadline 1e6 s). This is the **standard quantum-\n"
        "advantage tilt**: a generous quantum future against a deliberately\n"
        "small classical present. As with CV-5, this *helps* the negative\n"
        "H4 verdict and *would have to be revisited* if any label flipped\n"
        "positive. A Stronger-version remediation step adds a tuned\n"
        "classical sensitivity tier (e.g. CPLEX for SP4 mean-variance QP;\n"
        "QuantLib MC with control variates for derivative-pricing labels)\n"
        "on at least 2-3 labels; that work is out of MDV scope.\n"
    )
    THREATS.write_bytes(b2 + _to_native(addendum, nl2))
    print(f"THREATS_TO_VALIDITY.md: append OK; size now {THREATS.stat().st_size}")

# Verify the latin1 dashes are still intact in THREATS
b3 = THREATS.read_bytes()
preserved = sum(1 for x in b3 if x in (0x96, 0x97))
print(f"THREATS_TO_VALIDITY.md latin1-dashes preserved: {preserved} (expected 10)")
