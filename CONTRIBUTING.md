# Contributing

This archive is the **frozen supplementary repository** for the MSc thesis
*Quantum Computing in Financial Services* (Copenhagen Business School, 2026).
It is a hand-in artifact distributed as a `.zip`. **Contributions are not
accepted, and the contents are not under active development.**

The archive is intended only for examiner verification, reproducibility, and
secondary citation as a Zenodo deposit.

## For Reviewers

Start here:

- [`README.md`](README.md) — submission boundary and verification commands.
- [`FREEZE.md`](FREEZE.md) — frozen status table and headline numbers.
- [`REPRODUCIBILITY.md`](REPRODUCIBILITY.md) — toolchain, setup, per-phase
  reproduction entry points.
- [`docs/ARTIFACT_CLAIM_LEDGER.md`](docs/ARTIFACT_CLAIM_LEDGER.md) — every
  manuscript claim mapped to its source file and verification command.

The verification surface (`pwsh ./verify.ps1`, `python -m pytest`) and the
`tools/verify/` validators read existing artifacts only; they do not re-run any
LLM or experiment job.

## Provenance Note

During development, work was done with one branch per feature/fix, squash-merge
PRs into `main`, and conventional commit prefixes (`feat:`, `fix:`, `docs:`,
`chore:`). The development repository, branch history, and code-review
discussion are not part of this submission archive; only the frozen tree at
hand-in time is included.

## Errata

If you find an error of fact in the manuscript or supplementary materials,
please raise it through the official Copenhagen Business School examination
channel rather than as a code change to this archive.
