---
name: execution-selection
description: Choose the execution route for a plan phase: local, Slurm CPU, or Slurm GPU.
compatibility: opencode
metadata:
  domain: workflow
  workflow: execution-routing
---

# Execution Selection

Use this skill before launching execution for a plan phase. Its job is to choose one route:

- `local`
- `slurm-cpu`
- `slurm-gpu`

## Announce

At the start, say:

- `I'm using the execution-selection skill to choose whether this phase should run locally, on Slurm CPU, or on Slurm GPU.`

## Required Inputs

Before choosing a route, determine or infer:

- whether the phase requires GPUs
- expected runtime
- whether the phase is a small validation step or a substantive run
- whether the workload is highly parallelizable or can fan out across independent units
- approximate size of the relevant inputs when that affects routing
- whether local execution is likely to hit bash timeout limits or tempt parameter weakening
- the minimum CPU resources needed for a real run
- where the primary outputs should go if the phase produces canonical results

If any of the above is unclear and materially affects safe execution, ask or stop with `needs-user`.

## Route Selection

Choose `local` only when all of the following are true:

- the phase is a genuinely small validation, smoke test, inspection step, or short-lived utility run
- expected runtime is comfortably short and unlikely to hit local timeout limits
- the work does not require GPUs
- the work does not need substantial safe fanout better handled by the scheduler
- local execution does not require weakening the plan, shrinking the workload, or dropping important checks

Choose `slurm` when any of the following are true:

- the phase is a substantive experiment, sweep, batch, or multi-step run
- expected runtime may exceed `15 minutes`
- memory requirements may exceed `8GB`
- relevant inputs exceed `1GB`
- the work is highly parallelizable or can fan out safely across independent units
- local execution would likely hit bash timeouts, require manual babysitting, or tempt a weaker run than the plan calls for
- the workload requires GPUs or is clearly deep-learning, CUDA, NCCL, or otherwise accelerator-backed

If `slurm` is chosen, then choose one of:

- `slurm-gpu` when the phase requires GPUs, CUDA, NCCL, deep-learning training or inference, or another explicit accelerator-backed path
- `slurm-cpu` otherwise

## Guardrails

- do not silently reduce epochs, batch size, sample count, data volume, retries, or other experiment settings just to make `local` fit
- require at least `8` CPU cores for any substantive run, local or Slurm, unless that is technically impossible or clearly unnecessary; if fewer are used, record the exception
- prefer scheduler-visible parallelism over fragile local looping when the work splits cleanly
- if canonical external result placement is required and still unspecified, stop with `needs-user` instead of inventing a destination

## Report Back

When done, report at least:

- the chosen route: `local`, `slurm-cpu`, or `slurm-gpu`
- the decision basis
- the requested CPU count if known
- why the rejected routes were not appropriate

## Next Action

- if the chosen route is `local`, proceed with local execution planning
- if the chosen route is `slurm-cpu`, load `submitting-slurm-cpu-jobs`
- if the chosen route is `slurm-gpu`, load `submitting-slurm-gpu-jobs`
