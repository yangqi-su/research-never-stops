---
description: Resume the explicit orchestrator workflow loop from the current active workflow state
agent: orchestrator
---
Resume workflow mode for the current project.

Behavior:

- use `$ARGUMENTS` as an optional plan id, plan path, or other resume hint
- resolve plan documents from `copilot/plans/docs/*.md`, match each by Plan ID to `copilot/plans/runs/<Plan ID>/`, and resume the sole plan whose `PLAN_STATUS.md` contains exactly `Status: active`
- exclude `claude-plans-*` from automatic selection and active-plan counts; if explicitly selected, stop and report that the plan belongs to the Claude workflow
- if multiple active plans exist and the arguments do not identify one, ask one focused question
- do not treat run-only historical families as executable plans, and do not guess when a lifecycle file is missing or invalid
- if the user explicitly requests fresh sessions for a migrated plan, preserve old ledgers as history but do not resume their task ids; this exception takes precedence over the wait-resume shortcut
- reopen a finished plan only on explicit user direction, through `workflow`, before dispatching leaf work
- resume the exact workflow task id stored in `workflow-session-root.json`; replace it only when absent or explicitly rejected by the task tool, except for an explicitly requested migrated-plan fresh-session handoff
- use or refresh `agent-sessions-root.json` for leaf-agent continuity
- after required reopening or migrated-session handoff, handle any explicit intervention first; otherwise, if the latest `workflow-summary.md` has `Next Stage: wait`, resume its current-phase `Wait Owner` before workflow using the orchestrator's wait-resume invariant, including legacy owner resolution
- if that owner's saved session is missing, phase-mismatched, or explicitly rejected, start one replacement session of the same agent with the wait-continuation context
- after the owner refreshes the phase state, resume the persistent `workflow` sidecar once so it can record the result and choose the next stage
- if neither an intervention nor a wait continuation applies, start or resume the persistent `workflow` sidecar normally
- if `$ARGUMENTS` contains an explicit user intervention, apply the orchestrator intervention fast path; dispatch a clearly requested implementation, review, or analysis action before resuming workflow
- resume the same persistent workflow session after the fast-path leaf action completes so workflow can record the resulting state
- keep delegating automatically according to `workflow` stage decisions until `workflow` returns a terminal state: `finished`, `wait`, `blocked`, or `needs-user`
- use the implementation agent selected by `workflow`; valid implementation agents are `implementation` and `pro-implementation`
- use `analysis` when meaningful outputs already exist and the current phase needs interpretation before the next phase or completion
- use `review` only for escalation due to failure, risky changes, or unclear results
- do not infer the next stage from leaf summaries yourself; resume `workflow` and follow its decision
- exception: detecting `Next Stage: wait` in `workflow-summary.md` is enough to trigger the wait-resume invariant before workflow runs
- do not stop and ask the user what agent to run next between normal non-terminal stages

When you stop, report the current plan path, run directory, whether `workflow-session-root.json` was resumed or replaced, the terminal state, and the key evidence.
