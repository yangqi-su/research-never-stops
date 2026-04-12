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
- keep this flow isolated from the root workflow stack
- create or resume `workflow-session.json` for that Copilot plan
- keep delegating automatically according to `copilot-workflow` stage decisions until `archive`, `wait`, `blocked`, or `needs-user`
