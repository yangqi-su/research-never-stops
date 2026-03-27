---
description: Resume the explicit orchestrator workflow loop from the current active workflow state
agent: orchestrator
---
Resume workflow mode for the current project.

Behavior:

- use `$ARGUMENTS` as an optional plan id, plan path, or other resume hint
- if exactly one active plan exists, resume it
- if multiple active plans exist and the arguments do not identify one, ask one focused question
- resume or recreate `workflow-session.json` as needed
- start or resume the persistent `workflow` sidecar
- keep delegating automatically until `workflow` returns a terminal state: `archive`, `wait`, `blocked`, or `needs-user`
- use `implementation` for normal work and `review` only for escalation
- do not stop and ask the user what agent to run next between normal non-terminal stages

When you stop, report the current plan path, run directory, terminal state, and the key evidence.
