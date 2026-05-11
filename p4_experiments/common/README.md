# `p4_experiments/common/` - Raw output store

This folder is intentionally small. It keeps the guarded raw output records that
anchor the canonical Phase 8 and Phase 8b/8c evidence. Reusable implementation
code lives in [`../core/`](../core/); phase and audit code lives in
[`../canonical/pipeline/`](../canonical/pipeline/) and
[`../canonical/audits/`](../canonical/audits/).

| File / folder | Purpose |
|---------------|---------|
| `output/` | **Guarded raw output store** — the 2,556 canonical Phase-8 result records (`results/`) and the Phase-8b classical baselines (`classical_results/`). Not a wrapper. |

See parent [`../README.md`](../README.md).