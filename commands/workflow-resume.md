---
description: Resume the explicit orchestrator workflow loop from the current active workflow state
agent: orchestrator
---
Resume workflow mode for the current project.

Behavior:

- use `$ARGUMENTS` as an optional plan id, plan path, or other resume hint
- if exactly one active plan exists under `copilot/plans/active/`, resume it
- if multiple active plans exist and the arguments do not identify one, ask one focused question
- resume the exact workflow task id stored in `workflow-session-root.json`; replace it only when absent or explicitly rejected by the task tool
- use or refresh `agent-sessions-root.json` for leaf-agent continuity
- if the latest existing `workflow-summary.md` has `Next Stage: wait`, treat this as a suspended `pro-implementation` continuation: resume the current-phase `pro-implementation` task before resuming workflow, regardless of why the wait happened
- if that saved `pro-implementation` task cannot be resumed, start one replacement `pro-implementation` session with the current wait-continuation context
- after `pro-implementation` refreshes the phase state, resume the persistent `workflow` sidecar once so it can record the result and choose the next stage
- if the latest state is not `wait`, start or resume the persistent `workflow` sidecar normally
- if `$ARGUMENTS` contains an explicit user intervention, apply the orchestrator intervention fast path; dispatch a clearly requested implementation, review, or analysis action before resuming workflow
- resume the same persistent workflow session after the fast-path leaf action completes so workflow can record the resulting state
- keep delegating automatically according to `workflow` stage decisions until `workflow` returns a terminal state: `archive`, `wait`, `blocked`, or `needs-user`
- use the implementation agent selected by `workflow`; valid implementation agents are `implementation` and `pro-implementation`
- use `analysis` when meaningful outputs already exist and the current phase needs interpretation before the next phase or archival
- use `review` only for escalation due to failure, risky changes, or unclear results
- do not infer the next stage from leaf summaries yourself; resume `workflow` and follow its decision
- exception: detecting `Next Stage: wait` in `workflow-summary.md` is enough to trigger the wait-resume invariant before workflow runs
- do not stop and ask the user what agent to run next between normal non-terminal stages

When you stop, report the current plan path, run directory, whether `workflow-session-root.json` was resumed or replaced, the terminal state, and the key evidence.
