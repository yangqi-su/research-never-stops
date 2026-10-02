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
- resolve plan documents from `copilot/plans/docs/*.md`, match each by Plan ID to `copilot/plans/runs/<Plan ID>/`, and select active plans only when `PLAN_STATUS.md` contains exactly `Status: active`
- exclude `claude-plans-*` from automatic selection and active-plan counts; if explicitly selected, stop and report that the plan belongs to the Claude workflow
- do not treat run-only historical families as executable plans, and do not guess when a lifecycle file is missing or invalid
- if the user explicitly requests fresh sessions for a migrated plan, preserve old ledgers as history but do not resume their task ids
- create `workflow-session-root.json` only when no workflow task id exists; otherwise resume its exact task id and replace it only after an explicit failed resume, except for an explicitly requested migrated-plan fresh-session handoff
- maintain `agent-sessions-root.json` for leaf-agent continuity
- start or resume the persistent `workflow` sidecar
- keep delegating automatically according to `workflow` stage decisions until `workflow` returns a terminal state: `finished`, `wait`, `blocked`, or `needs-user`
- use the implementation agent selected by `workflow`; valid implementation agents are `implementation` and `pro-implementation`
- when `workflow` recommends `<agent> (start fresh agent)`, start a new session of that specified implementation agent
- when `workflow` recommends `<agent> (resume existing agent)`, resume that specified implementation agent only when phase-compatible
- use `analysis` when the implementation agent has produced meaningful outputs and the current phase needs interpretation before the next phase or completion
- use `review` only when the workflow state or implementation evidence calls for escalation due to failure, risky changes, or unclear results
- do not infer the next stage from leaf summaries yourself; resume `workflow` and follow its decision
- do not stop and ask the user what agent to run next between normal non-terminal stages
- if multiple active plans exist and the arguments do not identify one, ask one focused question

When you stop, report the current plan path, run directory, whether `workflow-session-root.json` was created, resumed, or replaced, the terminal state, and the key evidence.
