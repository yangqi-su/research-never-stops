---
description: Start the Copilot workflow loop for an existing Copilot plan
agent: copilot-orchestrator
---
Enter Copilot orchestrator mode `workflow-start` for this task: $ARGUMENTS

Behavior:

- treat the arguments as a Copilot plan selector or resume hint
- remain the only entry agent and delegate workflow decisions internally
- if the arguments identify an existing active Copilot plan, use it directly
- if exactly one active Copilot plan exists and the arguments are empty, use it directly
- if there is no suitable active Copilot plan, stop and tell the user to use `/copilot-draft-plan` followed by `/copilot-write-plan` first
- keep Copilot-family session handling distinct from root-family session files while using the shared `copilot/plans/` backend
- create or resume `workflow-session.json` for that Copilot plan
- when `copilot-workflow` reaches `blocked` or `needs-user`, ask a focused question and, unless the user explicitly pauses, stops, cancels, or defers, relay the reply back into the same workflow session and continue the loop
- keep delegating automatically according to `copilot-workflow` stage decisions until `archive`, an explicitly accepted `wait`, or unresolved `blocked` or `needs-user` after user deferral
