# Execution Agent Contract Draft

## Goal

Reintroduce a dedicated `execution` agent so that `implementation` stays focused on file changes and exact run preparation, while `execution` owns local or Slurm execution and monitoring.

This split is intended to reduce context rot in `implementation`, make execution behavior more uniform, and create cleaner recovery loops when long-running work fails or produces ambiguous evidence.

## Design principles

- Keep `implementation` narrow: edit, prepare, specify, stop.
- Keep `execution` literal: follow the declared contract, monitor, report, do not improvise.
- Keep `review` diagnostic: explain failures, ambiguities, and risky states without changing files.
- Keep `analysis` interpretive: summarize what meaningful outputs taught us.
- Keep `workflow` quiet between stage boundaries: it should update state after leaf stages, not micromanage the middle of a run.
- Keep `orchestrator` in charge of all delegation and all persisted subagent session bookkeeping.

## Proposed agent boundaries

### `implementation`

- edits code, config, prompts, scripts, and lightweight workflow artifacts
- may run tiny readiness checks when needed to confirm that a command is syntactically or structurally runnable
- must not launch substantive local runs or Slurm jobs
- writes `implementation-summary.md`
- defines the exact execution contract that `execution` must follow

### `execution`

- does not edit project code or prompts
- reads `implementation-summary.md` and any referenced scripts or config snapshots
- launches the declared command locally or through Slurm
- monitors queue state, heartbeats, output presence, completion, and failure evidence
- writes `execution-summary.md`
- stops on ambiguity instead of inventing fixes

### `review`

- reads `workflow-summary.md`, `implementation-summary.md`, `execution-summary.md`, and relevant lightweight evidence
- diagnoses failures, risky changes, and unclear results
- writes `review-summary.md`
- never changes files

### `analysis`

- reads `implementation-summary.md`, `execution-summary.md`, and step outputs when meaningful outputs exist
- writes `analysis-summary.md`
- records what the step taught us, what remains uncertain, and what should happen next

### `workflow`

- reads the latest summaries at stage boundaries
- updates `workflow-summary.md`
- recommends the next stage
- should not be resumed continuously just to watch a healthy execution loop

### `orchestrator`

- remains the only primary agent in the explicit workflow loop
- invokes `launch`, `workflow`, `implementation`, `execution`, `review`, and `analysis` directly
- persists and resumes all subagent task ids
- owns retry routing and stage transitions

## Proposed normal stage loop

1. `launch`
   - create the active plan and sibling run directory
   - preserve approved upstream context in `planning-handoff.md`

2. `workflow`
   - inspect current state
   - recommend `implementation` for normal work on a fresh step

3. `implementation`
   - make the required changes
   - prepare exact execution instructions
   - write `implementation-summary.md`
   - return one of:
     - `execution` when substantive run instructions are ready
     - `analysis` when the step already has meaningful outputs and only needs interpretation
     - `review` when the situation is already risky or ambiguous
     - `blocked` or `needs-user` when the contract cannot be completed safely
     - `archive` for truly non-execution steps that are complete and need no interpretation

4. `execution`
   - run the declared command exactly as specified
   - monitor until terminal state unless an intentional `wait` contract applies
   - write `execution-summary.md`
   - return one of:
     - `analysis` when meaningful outputs now exist and no escalation is needed
     - `review` on failure, ambiguity, or suspicious output
     - `archive` when the run succeeded and the step needs no interpretation
     - `wait`, `blocked`, or `needs-user` when appropriate

5. `review` when needed
   - diagnose the problem
   - recommend `implementation`, `wait`, `blocked`, `needs-user`, or `archive`

6. `analysis` when meaningful outputs need interpretation
   - interpret what was learned from the current step
   - recommend `implementation`, `review`, `blocked`, `needs-user`, or `archive`

7. `workflow`
   - resume after each leaf stage
   - update `workflow-summary.md`
   - continue only at stage boundaries

## Trigger rules

### Send work to `execution` when

- `implementation` has finished all intended edits for the current step
- an exact command or exact script entrypoint exists
- route, resources, expected outputs, and success signals are explicit enough to execute literally

### Send work to `review` when

- execution failed
- execution evidence is contradictory or incomplete
- the step introduced a risky change that needs diagnosis before more execution
- outputs exist but appear corrupted, unusable, or inconsistent with the plan

### Send work to `analysis` when

- the step produced meaningful outputs
- the workflow needs to decide what those outputs mean before archival or the next implementation pass
- the situation is not primarily a failure-diagnosis problem

### Skip `analysis` when

- the step only changed scaffolding, config, prompts, or code with no meaningful outputs yet
- the main issue is still an execution or implementation failure
- the step is blocked before usable outputs exist

## Summary file contract

### `implementation-summary.md`

This becomes the source of truth for what was changed and exactly how `execution` should run the step.

Required content should include:

- step goal and scope
- files changed
- readiness checks performed, if any
- execution route: `local`, `slurm`, or `none`
- exact command or exact script entrypoint
- working directory
- environment assumptions and required inputs
- resource requirements such as CPU, memory, GPU, walltime, and partition if applicable
- expected outputs and their locations
- success signals and failure signals
- monitoring expectations such as heartbeat files, log lines, or artifact checks
- allowed execution flexibility, which should default to `none`
- suggested next stage

### `execution-summary.md`

This becomes the source of truth for what was actually run and what happened.

Required content should include:

- execution source summary path
- route actually used: `local` or `slurm`
- command or script actually run
- working directory used
- job id or pid when applicable
- launch timestamp and terminal timestamp
- terminal status: `success`, `failed`, `partial`, `running`, `queued`, `blocked`, `wait`, or `not-run`
- heartbeat and progress evidence
- outputs observed
- key logs or error evidence by path
- deviations from the declared contract, which should normally be `none`
- suggested next stage

### `review-summary.md`

Should explicitly cite both `implementation-summary.md` and `execution-summary.md` when execution has occurred.

### `analysis-summary.md`

Should treat `execution-summary.md` as the operational evidence source and the actual outputs as the interpretive evidence source.

## Literal execution rule

`execution` should follow the declared contract exactly unless `implementation-summary.md` explicitly grants bounded flexibility.

Default rule:

- no silent parameter changes
- no silent route changes between local and Slurm
- no silent retries with altered settings
- no silent output relocation
- no silent substitution of scripts, configs, or environments

If any of those become necessary, `execution` should stop and route to `review` or `needs-user` instead of improvising.

## Session persistence

To support clean resumes, move from a workflow-only session file to a run-directory file that tracks all active subagent sessions.

Recommended file: `agent-sessions.json`

Suggested shape:

```json
{
  "plan_id": "plans-<timestamp>-<slug>",
  "workflow_task_id": "ses_...",
  "implementation_task_id": "ses_...",
  "execution_task_id": "ses_...",
  "review_task_id": "ses_...",
  "analysis_task_id": "ses_...",
  "created_by": "orchestrator",
  "created_at": "YYYY-MM-DD HH:MM:SS",
  "updated_at": "YYYY-MM-DD HH:MM:SS"
}
```

Notes:

- `orchestrator` owns this file exclusively
- missing task ids are allowed for stages that have not run yet
- `review_task_id` can remain optional if review stays mostly one-shot in practice
- `workflow-session.json` can be kept temporarily for backward compatibility during migration

## Recommended workflow behavior changes

- `workflow` should update after `implementation`, `execution`, `review`, or `analysis`, not during active monitoring unless a refresh is explicitly needed
- `/workflow-status` should summarize `execution-summary.md` alongside the other summaries
- `status` should treat `analysis-summary.md` and `execution-summary.md` as primary evidence sources for durable project memory

## Migration notes

If this redesign is implemented, the main prompt and template updates will likely include:

- adding `agents/execution.md`
- updating `agents/implementation.md` to remove substantive execution ownership
- updating `agents/orchestrator.md` task permissions and loop rules
- updating `agents/workflow.md` next-stage rules to include `execution`
- restoring or recreating an `EXECUTION_SUMMARY_TEMPLATE`
- updating command docs so `/workflow-start`, `/workflow-resume`, and `/workflow-status` all account for `execution`

## Open design choice

The main remaining choice is whether `execution` is allowed to choose `local` versus `slurm` when `implementation` gives only constraints, or whether `implementation` must always declare the exact route.

Current recommendation:

- for maximum robustness, `implementation` should declare the route explicitly and `execution` should follow it literally
