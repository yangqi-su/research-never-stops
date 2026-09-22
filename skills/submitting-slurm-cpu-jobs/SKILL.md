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

For this environment, you have 2 options:
- use the `ihc-grid-1-1-1` node for lower number of slurm jobs (recommended for most jobs)
  - include `#SBATCH --partition=ihc`
  - include `#SBATCH --account=ihc`
  - include `#SBATCH --nodelist=ihc-grid-1-1-1`

-OR for a larger set of jobs (more than 50 jobs, like a large jobarray)
  - include `#SBATCH --partition=all`
  - include `#SBATCH --account=ihc`
  - include `#SBATCH --nodelist=bellatrix,grid-2-1-1,grid-2-1-2,grid-2-1-3,grid-2-1-4,grid-2-1-5,grid-2-1-6,grid-2-1-7,grid-2-1-8,grid-2-1-9,juggernaut`

- do not add GPU-node pinning such as `#SBATCH --nodelist=ihc-h200-1` since this is for cpu jobs only

## Submission Guidance

- request at least `8` CPU cores for substantive runs unless that is technically impossible or clearly unnecessary
- prefer job arrays or other scheduler-visible parallel fanout when the work splits safely into independent units
- keep stdout and stderr paths explicit so monitoring has a stable place to look
- record the chosen CPU count, memory, and any parallelization strategy in the execution evidence

## Monitoring Requirements

- monitor scheduler state with `squeue` and `sacct`
- do not use bash or Python watcher scripts; use direct `sleep` plus repeated scheduler checks
- monitor a heartbeat source such as a log file, checkpoint timestamp, metric file, or explicit progress counter
- immediately after submission, record job id, queue state, heartbeat source, and the first expected progress signal
- make one startup follow-up check after about `1 minute` to confirm scheduler state and heartbeat if the job starts quickly
- before repeated polling, try to estimate ETA from logs or output progress markers
- prefer explicit log ETA when present; otherwise estimate from completed versus total epochs/steps and observed time per epoch/step across at least two observations
- treat Slurm wall time as an upper bound only, not as a progress ETA
- if the ETA is reliable and greater than `15 minutes`, stop active polling and return `wait` with a concrete recommended resume time or resume condition
- if the ETA is reliable and no more than `15 minutes`, make the next check near the estimated completion time rather than polling at a fixed short interval
- if ETA is still uncertain after trying to estimate from logs, run at most five delayed checks after `1`, `2`, `4`, `8`, and `16` minutes; after each check, re-estimate ETA and stop early if the job completes or ETA becomes reliable
- after the fifth uncertain-ETA healthy check, return `wait` rather than continuing to poll
- if outputs or logs show no meaningful change for more than `20 minutes`, treat the job as `blocked` and record the evidence
- if the underlying script emits no progress information, prefer an external heartbeat such as output-file mtime, checkpoint timestamp, or Slurm log growth; only add logging to the script when no external signal exists, and then add at most one periodic print of the loop counter — never a metrics file, status file, or progress framework
- do not treat Slurm `COMPLETED` alone as success; verify that expected outputs or success signals exist
- all shell calls that include `sleep` must use a command timeout longer than the sleep interval plus expected scheduler-check time
- never repeat fixed-interval polling such as `sleep 110` loops for a healthy long-running job
- use `wait` when the job is healthy or normally queued, active monitoring is no longer useful, and a concrete resume condition is recorded

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
- progress marker, estimated remaining time, ETA confidence, ETA basis, last heartbeat, and recommended resume time when the job is still running
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
