---
name: submitting-slurm-cpu-jobs
description: Submit and monitor Slurm CPU jobs with cluster defaults, explicit heartbeat checks, and bounded waiting.
compatibility: opencode
metadata:
  domain: hpc
  workflow: slurm-cpu-submission
---

# Submitting Slurm CPU Jobs

Use this skill when a task needs CPU-backed Slurm execution without requesting GPUs.

## Announce

At the start, say:

- `I'm using the submitting-slurm-cpu-jobs skill to route and monitor this CPU Slurm job.`

## When To Use

Use this skill when any of the following are true:

- the current phase should run on Slurm and does not require GPUs
- the workload is CPU-bound, batch-oriented, or parallel across CPU workers only
- the job needs normal Slurm accounting, queueing, and monitoring without GPU-specific routing

## Core Principles

- prefer scheduler-managed execution over ad hoc background processes
- keep the submission explicit: requested cores, memory, runtime expectation, command, logs, and output location
- request enough CPU resources for the real workload rather than weakening the run to fit local execution
- keep small submission artifacts and monitoring notes in the run directory when there is one
- record a heartbeat source so monitoring can distinguish healthy progress from a stuck job

## Required Inputs

Before submitting, determine or infer:

- expected runtime
- CPU core count needed
- memory requirement
- whether the job is single-node or multi-node
- the launcher or command that Slurm should run
- where logs and heartbeat signals will appear
- where the primary outputs will be written

If any of the above is unclear and materially affects safe submission, ask or stop with `needs-user`.

## Cluster Defaults

For this environment:

- include `#SBATCH --partition=ihc,all`
- include `#SBATCH --account=ihc`
- include `#SBATCH --nodelist=bellatrix,grid-2-1-1,grid-2-1-2,grid-2-1-3,grid-2-1-4,grid-2-1-5,grid-2-1-6,grid-2-1-7,grid-2-1-8,grid-2-1-9,juggernaut,ihc-grid-1-1-1`
- do not add GPU-node pinning such as `#SBATCH --nodelist=ihc-h200-1` unless the user or project explicitly requires a specific node

## Submission Guidance

- request at least `8` CPU cores for substantive runs unless that is technically impossible or clearly unnecessary
- prefer job arrays or other scheduler-visible parallel fanout when the work splits safely into independent units
- keep stdout and stderr paths explicit so monitoring has a stable place to look
- record the chosen CPU count, memory, and any parallelization strategy in the execution evidence

## Monitoring Requirements

- monitor scheduler state with `squeue` and `sacct`
- do not use bash or Python watcher scripts; use direct `sleep` plus repeated scheduler checks
- use shorter polling intervals for the first few checks, then widen the intervals when the job is healthy and long-running
- monitor a heartbeat source such as a log file, checkpoint timestamp, metric file, or explicit progress counter
- if outputs or logs show no meaningful change for more than `20 minutes`, treat the job as `blocked` and record the evidence
- if the underlying script does not emit enough progress information to support that check, add or request lightweight progress logging before relying on the run
- do not treat Slurm `COMPLETED` alone as success; verify that expected outputs or success signals exist
- use `wait` only when the job is healthy or normally queued, the next meaningful check is materially later, and a concrete resume condition is recorded

## Artifacts

Keep small submission artifacts in the run directory when there is one.

Typical artifacts include:

- sbatch script
- command snapshot
- log paths
- concise monitoring notes
- output manifest or result pointer when relevant

## Report Back

When done, report at least:

- requested CPU count
- requested memory
- whether the job was single-node or multi-node
- job id
- why Slurm was chosen
- monitoring and heartbeat source
- whether the job succeeded, failed, blocked, or entered a justified `wait` state

## Red Flags

Never:

- pin a GPU node for a CPU-only job without an explicit reason
- silently downsize the workload just to make it fit a local timeout
- treat `COMPLETED` as enough without checking outputs
- leave the job in `wait` without a concrete resume condition

Always:

- keep the requested resources explicit
- keep monitoring evidence explicit
- prefer a clear `blocked` report over pretending progress exists
