# Quantum Advantage Assessment — 4 Core + 1 Optional Veto

This module assesses quantum advantage claims from extracted experiments across the 8 active finance silos, using a **4-core + 1 optional-veto layered design** where each layer tests a different aspect of the claim.

## Scope notes (refreshed 2026-05-02)

> Three honest scoping qualifications apply to the assessor implementations
> below. Examiners familiar with the cited papers will press on these points;
> the prose here matches what the code actually does.
>
> - **L3 — "Beverland-inspired".** The L3 assessor folder is
>   `beverland_2022/` and the framework ID emitted by `make_verdict()` is
>   **`beverland_inspired_2022`** (renamed 2026-05-02; legacy
>   `beverland_2022` retained in enums for back-compat with frozen
>   results). The implementation sweeps Babbush 2021 Eq. (5) across
>   Beverland's 6 hardware-scenario *names*; it does **not** perform
>   end-to-end QEC code-distance selection, T-factory scheduling, or
>   full physical-qubit/runtime estimation. See
>   [`beverland_2022/BEVERLAND_CAVEAT.md`](beverland_2022/BEVERLAND_CAVEAT.md).
>
> - **L1 — Rønnow taxonomy applied to gate-based algorithms only.** The
>   four Rønnow pitfalls (optimal-annealing-time tuning, fixed-time
>   artefacts, hardware parity, instance-class fairness) are
>   annealing/QAOA/Grover-specific. As of the 2026-05-02 fix
>   `assess_ronnow.py` early-returns `not_applicable` for algorithm
>   families outside `{qaoa, grover, amplitude_estimation,
>   amplitude_amplification, quantum-annealing}` unless the experiment
>   carries an explicit `benchmark_validity_study=true` flag.
>
> - **L2 (Hoefler) — Tables 1 & 2 only, not the 12 rules.** The Hoefler
>   assessor implements the future-quantum performance table and the
>   max-ops-by-speedup-order table; it does not evaluate the 12
>   benchmarking rules (which require per-paper checklist data the
>   extraction schema does not expose).
>
> - **L4 — silo coverage gaps.** L4 routes to Chakrabarti 2021 for
>   pricing/risk/MC and Dalzell 2023 for portfolio/optimization. Two
>   active silos sit outside this routing: **PD-05 fraud-detection**
>   gets `not_applicable` at L4 (no Chakrabarti or Dalzell coverage);
>   **PD-08 cryptography-security** is excluded from the active P3
>   pipeline entirely (`silo_inclusion.json::excluded_silos`).
>
> - **L4 (Dalzell QIPM gate, fix 2026-05-02).** The previous version
>   force-failed every portfolio-optimization experiment via a
>   silo-wide `is_infeasible` flag. As of the QA-5 fix the gate is
>   restricted to algorithm.family in `{qipm, quantum-interior-point,
>   ...}`; non-QIPM portfolio algorithms now receive `not_applicable`
>   with an explicit scope-out reason rather than a forced fail.
>
> - **L2 sub-framework disagreement.** Each row carries an
>   `L2_merge_disagreement` boolean (added 2026-05-02), True iff Hoefler
>   and Babbush both produced a scored verdict and disagreed. Surfaces
>   the disagreement masked by the L2 min-merge.

## Layer Design

### Core Layers (scored for every applicable experiment)

| # | Layer | Assessor(s) | Folder(s) | What it tests | When to apply |
|---|---|---|---|---|---|
| **L1** | Benchmark validity | Rønnow 2014 | `ronnow/` | Whether the speedup claim is well-defined and the classical comparator is fair | Every paper claiming "advantage," "speedup," or "supremacy/utility" |
| **L2** | Practicality & crossover | Hoefler 2023 + Babbush 2021 | `hoefler_assessment/` + `babbush_2021/` | I/O bottlenecks, crossover size, and whether polynomial speedups survive FT overheads | Any paper with asymptotic advantage claims; quadratic-only claims are downgraded |
| **L3** | Full-stack resource | Beverland-inspired 2022 | `beverland_2022/` | Logical/physical qubits, runtime, distillation, space-time tradeoffs under swept hardware scenarios. **Implemented as Babbush Eq. (5) parameter-sweep across Beverland's 6 hardware-scenario names; framework_id=`beverland_inspired_2022`.** | Whenever a paper makes FT claims or can be reverse-engineered into one |
| **L4** | Finance-domain realism | Chakrabarti 2021 *or* Dalzell 2023 | `chakrabarti_2021/` or `dalzell_2023/` | Whether the workload matters commercially under realistic FT assumptions | Chakrabarti for pricing/risk/MC; Dalzell for portfolio/optimization. **Not both per experiment.** |

### Optional Veto Layer

| # | Layer | Assessor | Folder | What it tests | When to apply |
|---|---|---|---|---|---|
| **L5** | NISQ veto | Stilck França 2021 | `stilck_franca_2021/` | Whether noisy-circuit output is indistinguishable from random (p×L bound) | NISQ optimization, annealing, QAOA, VQE-like finance papers only. Caps but cannot upgrade consensus. |

## Layer Rationale

**L1 — Rønnow (benchmark validity).** Still the clearest source for distinguishing a fair advantage claim from a weak one. Many finance papers compare against toy baselines, cherry-pick instances, or blur algorithmic/hardware/implementation claims. Later benchmark guidance operationalizes the same concerns but does not replace the original taxonomy.

**L2 — Hoefler + Babbush (practicality & crossover).** Merged as a single scored layer because they address the same construct from complementary angles: crossover realism (Hoefler) and the insufficiency of quadratic speedups under FT overheads (Babbush). Hoefler explicitly reaches a similar conclusion and cites Babbush; scoring them separately would double-count. The merged verdict takes the more pessimistic of the two.

**L3 — Beverland (full-stack resource).** The most operational generalized resource-estimation framework, translated into the Azure Quantum Resource Estimator. Preprint rather than journal, but its modeling assumptions are actively maintained in downstream tooling. Sweeps a grid of hardware scenarios rather than a single threshold.

**L4 — Chakrabarti / Dalzell (finance-domain realism).** Chakrabarti is the primary pricing/risk threshold source (QAE for derivative pricing). Dalzell is the optimization-specific end-to-end resource analysis (QIPM for portfolio). Only one is scored per experiment based on silo routing:
- Pricing, risk, Monte Carlo, insurance → Chakrabarti
- Portfolio, trading, credit, ML → Dalzell

**L5 — Stilck França (optional veto).** Central conclusion still strong (noisy optimization advantages unlikely without much lower noise), but later results complicate blanket readings. Applied as a cautionary cap rather than an automatic rejection.

## Legacy Frameworks

Montanaro 2015 (subsumed by L2 — Babbush covers the quadratic QAE overhead
result) and dequantization (a narrow negative control) were considered
during scoping but are **not present in this folder**. Their reasoning is
preserved in the s3 design notes / archive; only the 7 active assessor
folders below participate in triangulation scoring.

## Running

```bash
# Run all active assessors (from repo root)
python -m p3_thematic_synthesis.s3_quantum_advantage.ronnow.assess_ronnow
python -m p3_thematic_synthesis.s3_quantum_advantage.hoefler_assessment.assess_hoefler
python -m p3_thematic_synthesis.s3_quantum_advantage.babbush_2021.assess_babbush
python -m p3_thematic_synthesis.s3_quantum_advantage.beverland_2022.assess_beverland
python -m p3_thematic_synthesis.s3_quantum_advantage.chakrabarti_2021.assess_chakrabarti
python -m p3_thematic_synthesis.s3_quantum_advantage.dalzell_2023.assess_dalzell
python -m p3_thematic_synthesis.s3_quantum_advantage.stilck_franca_2021.assess_stilck_franca

# Triangulate (4 core + 1 veto)
python -m p3_thematic_synthesis.s3_quantum_advantage.combined.triangulate
```

Each assessor reads from `p3_thematic_synthesis/s2_quantitative/output/extractions/` through `_shared/extraction_loader.py` and writes to its own `results/` folder.

## Common Verdict Schema

Every assessor emits verdicts conforming to `_shared/common_verdict_schema.json`:

| Verdict | Meaning |
|---|---|
| `viable` | Passes all framework tests — advantage plausible |
| `likely_viable` | Strong evidence (quartic+, exponential speedup) |
| `potentially_viable` | Conditional evidence (borderline, within envelope) |
| `conditional` | Partially meets criteria; needs refinement |
| `fails` | Does not pass framework's test |
| `not_applicable` | Framework doesn't cover this silo/algorithm |
| `insufficient_data` | Missing data to assess |

## Triangulation Output

`combined/output/` contains:

- **triangulation_matrix.json** — one row per experiment, columns: L1–L4 layer verdicts, L5 veto, raw framework verdicts (audit), consensus
- **consensus_summary.json** — by-silo and by-algorithm rollups, veto statistics
- **disagreement_cases.json** — top 50 experiments by inter-layer disagreement

### Layer merging rules

| Merge | Rule |
|---|---|
| L2 (Hoefler + Babbush) | Take the more pessimistic scored verdict (min score); if one is not_applicable, use the other |
| L4 (Chakrabarti / Dalzell) | Route by silo; only one applies per experiment |
| L5 veto | Can only downgrade consensus (cap at `fails` or `conditional`); never upgrades |

### Consensus categories

| Label | Meaning |
|---|---|
| `unanimous_viable` | All scored core layers agree ≥ potentially_viable |
| `majority_viable` | >50% of scored core layers say ≥ potentially_viable |
| `split` | No majority either way |
| `majority_fails` | >50% of scored core layers say fails |
| `unanimous_fails` | All scored core layers agree: fails |
| `insufficient_data` | All layers returned not_applicable or insufficient_data |

## Phase 4 consumption

- Filter by `consensus_verdict ∈ {unanimous_viable, majority_viable}` for robust simulation candidates
- Dig into `disagreement_cases.json` for research-interesting edge cases
- Use Beverland's `scenario_verdicts` (L3) to find the Pareto frontier of hardware assumptions
- Check `L5_veto_applied` to identify NISQ experiments capped by noise bounds

## Folder structure

```
quantum_advantage/
├── README.md                    (this file)
├── _shared/                     (utilities: extraction loader, verdict schema, speedup inference)
├── ronnow/                      (L1: Rønnow 2014 — benchmark validity)
├── hoefler_assessment/          (L2a: Hoefler 2023 — practicality/crossover)
├── babbush_2021/                (L2b: Babbush 2021 — polynomial crossover Eq. 5)
├── beverland_2022/              (L3: Beverland 2022 — full-stack resource scenarios)
├── chakrabarti_2021/            (L4-pricing: Chakrabarti 2021 — QAE derivative threshold)
├── dalzell_2023/                (L4-optim: Dalzell 2023 — end-to-end QIPM/portfolio)
├── stilck_franca_2021/          (L5: Stilck França 2021 — optional NISQ veto)
├── combined/                    (triangulation layer)
│   └── output/                  (consensus matrix, summary, disagreements)
└── derived_fields/              (enriched complexity data)
```

## Paper Reference Table

| Paper | Layer | Role | Key assumptions | Currency |
|---|---|---|---|---|
| Rønnow et al. (2014) | L1 | Benchmark-validity anchor | Annealing benchmarking context; no FT resource or business-value analysis | Still primary; later papers refine reporting, not the taxonomy |
| Hoefler, Häner, Troyer (2023) | L2 | Practicality/crossover framework | Coarse, optimistic future-QC model; not finance-specific | Current; no newer universal practicality framework |
| Babbush et al. (2021) | L2 | Quadratic-downgrade rule | Surface-code-centric; optimistic assumptions | Current; qualitative result not overturned |
| Beverland et al. (2022) | L3 | Full-stack resource estimation | Preprint; abstracted stack model | Primary in practice; operationalized via Azure QRE |
| Chakrabarti et al. (2021) | L4 | Finance-native pricing/risk threshold | Strongest for derivative pricing + QAE | Primary; modified by later market-risk work, not replaced |
| Dalzell et al. (2023) | L4 | Portfolio/optimization realism | QIPM/SOCP-specific; small-instance numerics | Primary for this niche; too narrow for universal use |
| Stilck França & García-Patrón (2021) | L5 | Optional NISQ veto | Not a full FT framework; not blanket anti-NISQ | Relevant; treat as caution, not prohibition |
