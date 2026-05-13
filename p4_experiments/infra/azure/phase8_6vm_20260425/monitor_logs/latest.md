# Phase 8 VM Monitor - 2026-04-26T16:11:49Z

Recover mode: `True`
Helper mode: `True`
Total: `0/2556` results, `2556` remaining.

| VM | Status | Owned Results | Total Results | Running | Unit | Action |
|---|---:|---:|---:|---:|---:|---|
| qf-p8-vm1 | ssh_error | 0/432 | 0 | 0 | 0 | none |
| qf-p8-vm2 | ssh_error | 0/432 | 0 | 0 | 0 | none |
| qf-p8-vm3 | ssh_error | 0/432 | 0 | 0 | 0 | none |
| qf-p8-vm4 | ssh_error | 0/432 | 0 | 0 | 0 | none |
| qf-p8-vm5 | ssh_error | 0/432 | 0 | 0 | 0 | none |
| qf-p8-vm6 | ssh_error | 0/396 | 0 | 0 | 0 | none |

## Helper Events
- relaunch qf-p8-vm1 -> qf-p8-vm4 labels=SX7,SX1 pid=
- relaunch qf-p8-vm2 -> qf-p8-vm5 labels=SX8,SX2 pid=
- relaunch qf-p8-vm3 -> qf-p8-vm6 labels=SX3,SQ8 pid=

## Active Helpers

| Helper | Owner | Labels | Status | PID |
|---|---|---|---:|---:|
| qf-p8-vm1 | qf-p8-vm4 | SX7,SX1 | launch_failed |  |
| qf-p8-vm2 | qf-p8-vm5 | SX8,SX2 | launch_failed |  |
| qf-p8-vm3 | qf-p8-vm6 | SX3,SQ8 | launch_failed |  |
