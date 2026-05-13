# Phase 8 Six-VM Azure Setup

This folder is the fresh setup package for the current 71-label P4 Phase 8 run. It supersedes the older four-VM helper scripts under [../phase8_4vm_legacy_bootstrap/](../phase8_4vm_legacy_bootstrap/).

## Current Plan

- Cohort: `p4_experiments/canonical/cohort.json`
- Labels: 71
- Cells per label: 36
- Expected total cells: 2556
- Split: 12, 12, 12, 12, 12, 11 labels by sorted round-robin assignment
- Workers per VM: 1
- Per-cell wall-clock caps:
  - `P4_CELL_TIMEOUT_S=7200`
  - `P4_FIRST_CELL_TIMEOUT_S=7200`
  - `P4_TI_BARE_TIMEOUT_S=7200`

The setup scripts install a clean Python 3.11 venv on each VM and pin the Phase 8 runtime dependencies in `requirements.phase8-linux.txt`.

## Workflow

From the repo root:

```powershell
.\p4_experiments\infra\azure\phase8_6vm_20260425\Start-VMs.ps1
.\p4_experiments\infra\azure\phase8_6vm_20260425\Upload-And-Setup.ps1
.\p4_experiments\infra\azure\phase8_6vm_20260425\Check-Setup.ps1
```

`Upload-And-Setup.ps1` starts setup in the background on each VM and does not start Phase 8. Wait until `Check-Setup.ps1` reports `STATUS=setup_complete` for all six VMs.

After inspection, launch the run:

```powershell
.\p4_experiments\infra\azure\phase8_6vm_20260425\Start-Runs.ps1
.\p4_experiments\infra\azure\phase8_6vm_20260425\Probe-Runs.ps1
```

After the run finishes, sync results back:

```powershell
.\p4_experiments\infra\azure\phase8_6vm_20260425\Sync-Results.ps1
```

Then run the local Phase 8 audit from the repo root.

## Canonical Phase 8d: QAE/HHL High-N Scout

After the Phase 8 big run is fully complete and synced, the idle VMs run the canonical appendix-only Phase 8d fixed-precision QAE/HHL scout. The scout decouples problem size `N` from precision qubits `m` and writes records under `p4_experiments/canonical/outputs/phase08d_qae_hhl_scout/results/`.

First lock the data-derived 8d selection manifest. This must be run after Phase 8/8a, Phase 8b, and Phase 8c are complete; it selects the current Faithful QAE/HHL source labels and blocks launch if any dependency is missing.

```powershell
python -m p4_experiments.canonical.phase8d_select_experiments
```

Run canaries first:

```powershell
.\p4_experiments\infra\azure\phase8_6vm_20260425\Start-QAEHHLScout.ps1 -Plan canary
```

If the canaries behave, run the full floquet grid:

```powershell
.\p4_experiments\infra\azure\phase8_6vm_20260425\Start-QAEHHLScout.ps1 -Plan floquet
```

Only add surface-code Majorana after the floquet grid behaves:

```powershell
.\p4_experiments\infra\azure\phase8_6vm_20260425\Start-QAEHHLScout.ps1 -Plan surface
```

Sync scout results back locally:

```powershell
.\p4_experiments\infra\azure\phase8_6vm_20260425\Sync-QAEHHLScout.ps1
python -m p4_experiments.canonical.phase8d_finalize_qae_hhl
python -m p4_experiments.canonical.audit_phase8d
```

The default per-cell timeout is 36000 seconds (10 hours). `Start-QAEHHLScout.ps1` refuses to launch while `phase8_big_run` is still active unless `-SkipIdleCheck` is passed intentionally.

For the Deepcare failed-cell rerun, idle VMs can be automatically recycled as helper lanes:

```powershell
.\p4_experiments\infra\azure\phase8_6vm_20260425\Auto-DeepcareHelpers.ps1
.\p4_experiments\infra\azure\phase8_6vm_20260425\Register-DeepcareAutoHelpersTask.ps1 -IntervalMinutes 5
```

The auto-helper pass only launches from VMs with no active owner rerun and no active helper process. Helper outputs are written to separate `helper_results_*` directories and must be explicitly synced/reconciled before finalizing Phase 8d.

The deprecated Hoefler N-sweep scripts remain in the repo only for historical reproduction and require `--legacy-ok`; they are no longer the canonical Phase 8d path.
