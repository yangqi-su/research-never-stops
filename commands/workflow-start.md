---
description: Start the explicit orchestrator workflow loop for an existing active plan
agent: orchestrator
---
Enter workflow mode for this task: $ARGUMENTS

Behavior:

- treat the arguments as a plan selector or resume hint, not as a request to draft or write a new plan inline
- if the arguments identify an existing active plan, use it directly
- if exactly one active plan exists and the arguments are empty, use it directly and begin the agent delegation process without stopping
- if there is no suitable active plan, stop and tell the user to use `/draft-plan` followed by `/write-plan` first
- resolve active plans from `copilot/plans/active/`
- create or resume `workflow-session-root.json` for that plan
- maintain `agent-sessions-root.json` for root-family leaf-agent continuity
- start or resume the persistent `workflow` sidecar
- keep delegating automatically according to `workflow` stage decisions until `workflow` returns a terminal state: `archive`, `wait`, `blocked`, or `needs-user`
- use `implementation` agent for code changes, validation, execution routing, actual local or Slurm execution, and monitoring
- when `workflow` agent recommends `implementation (start fresh agent)`, start new `implementation` agent
- use `analysis` when `implementation` has produced meaningful outputs and the current phase needs interpretation before the next phase or archival
- use `review` only when the workflow state or implementation evidence calls for escalation due to failure, risky changes, or unclear results
- do not infer the next stage from leaf summaries yourself; resume `workflow` and follow its decision
- do not stop and ask the user what agent to run next between normal non-terminal stages
- if multiple active plans exist and the arguments do not identify one, ask one focused question

When you stop, report the current plan path, run directory, whether `workflow-session-root.json` was created, resumed, or replaced, the terminal state, and the key evidence.
