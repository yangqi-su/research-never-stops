---
name: submitting-slurm-gpu-jobs
description: Submit and monitor Slurm GPU jobs with a scheduler-first policy and an optional opportunistic no-GRES fallback when standard GPU scheduling is blocked.
compatibility: opencode
metadata:
  domain: hpc
  workflow: slurm-gpu-submission
---

# Submitting Slurm GPU Jobs

Use this skill when a task needs GPU-backed Slurm execution, including normal `--gres` submissions and the cluster-specific opportunistic fallback that runs without `--gres` only when it is safe and allowed.

## Announce

At the start, say:

- `I'm using the submitting-slurm-gpu-jobs skill to route and monitor this GPU Slurm job.`

## When To Use

Use this skill when any of the following are true:

- the current phase requires one or more GPUs on Slurm
- the workload is deep-learning, CUDA, NCCL, or otherwise GPU-backed
- the task may need standard `--gres=gpu:N` submission with queue-aware monitoring
- the cluster allows opportunistic no-GRES fallback on actually idle GPUs when scheduler GPU resources are blocked

## Core Principles

- prefer standard Slurm GPU scheduling first
- treat the no-GRES path as a fallback, not the default
- use the fallback only when cluster policy allows it and the user or project guidance permits it
- do not interfere with other users' jobs
- if collision risk becomes material, abort rather than push through
- keep execution evidence explicit: requested GPUs, selected node, selected GPU ids, submission mode, and safety checks
- if the job is multi-node, use standard GRES-based scheduling in v1
- if the job uses the opportunistic fallback in v1, keep it single-node only

## Required Inputs

Before submitting, determine or infer:

- GPU count needed
- expected runtime
- CPU, memory, partition, account, and node constraints
- whether the job is single-node or multi-node
- launcher style such as `python`, `torchrun`, `accelerate`, or another framework launcher
- whether the workload can be cancelled safely if a collision is detected
- where logs and heartbeat signals will appear

If any of the above is unclear and materially affects safe submission, ask or stop with `needs-user`.

## Cluster Defaults

For this environment:

- include `#SBATCH --partition=ihc,all`
- include `#SBATCH --account=ihc`
- add `#SBATCH --nodelist=ihc-h200-1` only when the run clearly requires that GPU node in this environment

## Submission Modes

Always classify the chosen route as one of:

- `standard-gres`
- `opportunistic-no-gres`

Record that mode in the execution evidence and summary.

## Standard Path

Choose `standard-gres` when possible.

Use it by default for:

- any multi-node GPU job
- multi-node DDP or NCCL jobs
- jobs expected to run longer than `24 hours`
- jobs where collision-safe cancellation is not acceptable
- jobs where a specific node should not be trusted without scheduler GPU accounting

For the standard path:

- request GPUs with `--gres=gpu:N` or the cluster's equivalent
- keep normal Slurm accounting and queue behavior
- allow single-node or multi-node execution
- monitor with `squeue` and `sacct`, plus a heartbeat source from logs or outputs

## Fallback Eligibility Gate

Only consider `opportunistic-no-gres` if all of the following are true:

- standard `--gres` submission is currently blocked, unavailable, or materially delayed by scheduler GPU accounting
- the cluster explicitly allows this fallback when it does not interfere with other users
- the expected runtime is `24 hours` or less
- the job is single-node only
- the job can be cancelled immediately if another user's work appears on the chosen GPUs
- the job can be pinned cleanly with `CUDA_VISIBLE_DEVICES`
- the framework is expected to honor `CUDA_VISIBLE_DEVICES`

If any gate fails, do not use the fallback.

## Probe-And-Run Fallback Flow

The v1 fallback uses two separate jobs: a small probe job followed by the real run job.

### Probe Job

Submit a small non-GRES job that:

- lands on a candidate GPU node
- samples GPU state several times rather than once
- uses `nvidia-smi` or an equivalent lightweight GPU inspection command
- records, for each visible GPU, whether there are running compute processes, meaningful memory usage, and sustained activity
- outputs a machine-readable result with the candidate node, chosen GPU ids, and the evidence window

Probe conservatively.

Prefer GPUs only when they remain idle across repeated checks and show all of the following:

- no foreign compute process
- very low memory usage
- no sustained utilization spike

If the cluster uses MIG or another topology that makes raw device ids ambiguous, do not guess. Fall back to standard GRES unless the mapping is explicit and safe.

### Real Run Job

If the probe finds enough safe GPUs:

- submit the real job quickly after the probe completes
- pin the job to the probed node
- do not request `--gres`
- set `CUDA_VISIBLE_DEVICES` to the selected GPU ids
- perform an immediate pre-launch recheck inside the real job before starting the payload

If the pre-launch recheck no longer shows the chosen GPUs as safely idle, exit immediately and mark the attempt as blocked rather than launching anyway.

## Monitoring Requirements

For all GPU Slurm jobs:

- monitor scheduler state with `squeue` and `sacct`
- do not use bash or Python watcher scripts; use direct `sleep` plus repeated scheduler checks
- use shorter polling intervals for the first few checks, then widen the intervals when the job is healthy and long-running
- monitor a heartbeat source such as a log file, metric file, checkpoint timestamp, or explicit progress counter
- classify the run as queued normally, running with heartbeat, running without heartbeat, completed but unverified, blocked due to inactivity, or intentional wait
- if outputs or logs show no meaningful change for more than `20 minutes`, treat the job as `blocked` and record the evidence
- if the underlying script does not emit enough progress information to support that check, add or request lightweight progress logging before relying on the run
- do not treat `COMPLETED` alone as success; verify expected outputs or success signals
- use `wait` only when the job is healthy or normally queued, the next meaningful check is materially later, and a concrete resume condition is recorded

Additional monitoring for `opportunistic-no-gres`:

- re-check the chosen GPUs periodically while the job is running
- distinguish the job's own processes from foreign processes if possible
- if another user's work appears to start using one of the selected GPUs, cancel immediately with `scancel`
- if evidence is ambiguous, prefer cancelling and reporting the collision risk

## Framework Guidance

- assume `CUDA_VISIBLE_DEVICES` is the primary isolation mechanism for the fallback path
- for single-node multi-GPU jobs, ensure the launcher and world-size settings match the selected GPU count
- for multi-node DDP in v1, use `standard-gres` and do not attempt the fallback
- do not assume every framework handles reordered or sparse device ids identically; verify launcher arguments when needed

## Artifacts

Keep small submission artifacts in the run directory when there is one.

Typical artifacts include:

- probe sbatch script
- real run sbatch script
- probe output snapshot or summary
- selected node and GPU ids
- concise monitoring notes

## Report Back

When done, report at least:

- chosen submission mode
- requested GPU count
- selected node or nodes
- selected GPU ids when fallback is used
- why standard GRES was used or rejected
- evidence used to justify the fallback, if used
- monitoring and heartbeat source
- whether the job succeeded, failed, blocked, or was cancelled for safety

## Red Flags

Never:

- start with the no-GRES fallback when standard GRES is available enough for the job
- use the fallback for multi-node jobs in v1
- use the fallback for jobs expected to run longer than `24 hours`
- launch after a stale or single-snapshot probe result without an immediate recheck
- keep running after likely collision evidence appears
- pretend a bypassed job is scheduler-isolated when it is not

Always:

- prefer the scheduler-managed path first
- record the exact safety gates used for fallback eligibility
- cancel on collision risk rather than competing with another user
- keep the execution summary explicit about the route taken
