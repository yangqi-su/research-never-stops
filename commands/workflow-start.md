---
description: Start the explicit orchestrator workflow loop for a new or existing plan-centered task
agent: orchestrator
---
Enter workflow mode for this task: $ARGUMENTS

Behavior:

- treat the arguments as the workflow goal unless they clearly identify an existing active plan
- if there is no suitable active plan, call `launch` to create one concrete step and its sibling run directory
- create or resume `workflow-session.json` for that plan
- start or resume the persistent `workflow` sidecar
- keep delegating automatically until `workflow` returns a terminal state: `archive`, `wait`, `blocked`, or `needs-user`
- use `implementation` for code changes, validation, execution routing, actual local or Slurm execution, and monitoring
- use `review` only when the workflow state or implementation evidence calls for escalation
- do not stop and ask the user what agent to run next between normal non-terminal stages
- if multiple active plans exist and the arguments do not identify one, ask one focused question

When you stop, report the current plan path, run directory, terminal state, and the key evidence.
