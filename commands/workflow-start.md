---
description: Start the explicit orchestrator workflow loop for a new or existing plan-centered task
agent: orchestrator
---
Enter workflow mode for this task: $ARGUMENTS

Behavior:

- treat the arguments as the workflow goal unless they clearly identify an existing active plan
- if the arguments identify an existing active plan, use it directly
- if there is no suitable active plan and the current input is already concrete enough for direct scaffolding, call `launch` and pass the approved context through with minimal paraphrase
- if there is no suitable active plan and the current input is still broad or multi-step, tell the user to use `/workflow-handoff` first or provide one concrete step to start from
- create or resume `workflow-session.json` for that plan
- start or resume the persistent `workflow` sidecar
- keep delegating automatically according to `workflow` stage decisions until `workflow` returns a terminal state: `archive`, `wait`, `blocked`, or `needs-user`
- use `implementation` for code changes, validation, execution routing, actual local or Slurm execution, and monitoring
- use `analysis` when `implementation` has produced meaningful outputs and the current step needs interpretation before archival or the next decision
- use `review` only when the workflow state or implementation evidence calls for escalation due to failure, risky changes, or unclear results
- do not infer the next stage from leaf summaries yourself; resume `workflow` and follow its decision
- do not stop and ask the user what agent to run next between normal non-terminal stages
- if multiple active plans exist and the arguments do not identify one, ask one focused question

When you stop, report the current plan path, run directory, terminal state, and the key evidence.
