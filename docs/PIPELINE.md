# Research Pipeline

The thesis is a four-part research pipeline. Each phase produces an artifact consumed by the next phase, while freeze files preserve the final claim boundary.

## Flow

```text
P1 framework synthesis
  -> taxonomy and codebook
P2 systematic review
  -> screened/classified corpus
P3 thematic synthesis
  -> silo themes, quantitative benchmark extraction, quantum-advantage assessment
P4 experiments
  -> resource-estimation evidence and final empirical claim checks
```

## Phase Summary

| Phase | Folder | Movement | Main Output |
|---|---|---|---|
| P1 Framework synthesis | `p1_framework_synthesis/` | Exploratory / inductive with researcher normalisation | Problem-domain x solution-approach taxonomy and codebook. |
| P2 Systematic review | `p2_systematic_review/` | Deductive classification | 777 processed papers, screening evidence, and corpus tags. |
| P3 Thematic synthesis | `p3_thematic_synthesis/` | Inductive within-silo synthesis plus quantitative/QA layers | 8 active silos, 501 S2 extraction files / 1,046 experiments, S3 filtered QA outputs, S4 themes, S5 cross-silo synthesis. |
| P4 Experiments | `p4_experiments/` | Experimental validation / resource estimation | 71-label canonical cohort and 2,556 Phase-8 resource-estimator records. |

## Phase 3 Detail

Phase 3 is the thesis's main synthesis layer:

| Step | Folder | Purpose |
|---|---|---|
| S1 | `s1_silo_scoping/` | Define active finance silos and inclusion boundaries. |
| S2 | `s2_quantitative/` | Extract quantitative benchmark/experiment records. |
| S3 | `s3_quantum_advantage/` | Apply the 4-core + 1-veto quantum-advantage assessment. |
| S4 | `s4_thematic_coding/` | Produce per-paper coding, memos, reviewed records, and silo themes. |
| S5 | `s5_cross_silo/` | Build cross-silo meta-themes and literature crosswalks. |
| S6 | `s6_silo_framing/` | Descriptive finance framing sibling used for chapter context. |

## Verification

Run the full retained verification surface from the repository root:

```powershell
pwsh .\verify.ps1
python -m pytest
```

The verifier uses existing artifacts only. It does not rerun LLM extraction, classification, or expensive experiment jobs.