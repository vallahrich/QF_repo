# STATUS: EXCLUDED FROM ACTIVE PIPELINE

**Silo code:** PD-08 — Cryptography and Financial Security
**Status:** Excluded as of 2026-04-19
**Source of truth:** [`shared/config/silo_inclusion.json`](../../../shared/config/silo_inclusion.json) `excluded_silos[]`

## Why excluded

The PD-08 corpus is dominated by quantum key distribution (QKD) and
post-quantum cryptography papers, which are out of scope for a
gate-based quantum-finance thesis. The Phase-3 active silo set
explicitly excludes PD-08 on those grounds.

## Where it still appears

- [`shared/config/unified_taxonomy.json`](../../../shared/config/unified_taxonomy.json) PD-08
  entry, annotated `"status": "excluded"` (added 2026-05-02 to make
  the source-of-truth taxonomy match the executed pipeline).
- [`p1_framework_synthesis/s3_taxonomy/problem-space.md`](../../../p1_framework_synthesis/s3_taxonomy/problem-space.md)
  PD-08 heading marked **⚠️ EXCLUDED FROM ACTIVE PIPELINE**.

## What this folder contains

This folder is **retained for traceability** so an examiner can see
that the PD-08 silo was scoped out rather than overlooked. It does
not feed downstream synthesis (`s4_thematic_coding/`, `s5_cross_silo/`,
`s6_silo_framing/`).
