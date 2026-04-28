---
description: Resume the explicit orchestrator workflow loop from the current active workflow state
agent: orchestrator
---
Resume workflow mode for the current project.

Behavior:

- use `$ARGUMENTS` as an optional plan id, plan path, or other resume hint
- if exactly one active plan exists under `copilot/plans/active/`, resume it
- if multiple active plans exist and the arguments do not identify one, ask one focused question
- resume or recreate `workflow-session-root.json` as needed
- use or refresh `agent-sessions-root.json` for root-family leaf-agent continuity
- start or resume the persistent `workflow` sidecar
- if `$ARGUMENTS` contains user feedback about a current workflow run, treat it as intervention context to hand to `workflow` rather than as a prompt for orchestrator-side diagnosis
- keep delegating automatically according to `workflow` stage decisions until `workflow` returns a terminal state: `archive`, `wait`, `blocked`, or `needs-user`
- use `implementation` for normal work
- use `analysis` when meaningful outputs already exist and the current phase needs interpretation before the next phase or archival
- use `review` only for escalation due to failure, risky changes, or unclear results
- do not infer the next stage from leaf summaries yourself; resume `workflow` and follow its decision
- do not stop and ask the user what agent to run next between normal non-terminal stages

When you stop, report the current plan path, run directory, whether `workflow-session-root.json` was resumed or replaced, the terminal state, and the key evidence.
