---
description: Resume the Copilot workflow loop from the current Copilot workflow state
agent: copilot-orchestrator
---
Enter Copilot orchestrator mode `workflow-resume` for this task: $ARGUMENTS

Behavior:

- resolve the target plan from the arguments or the only active Copilot plan when unambiguous
- remain the only entry agent and delegate workflow decisions internally
- resume the persisted Copilot workflow sidecar when possible
- keep Copilot-family session handling distinct from root-family session files while using the shared `copilot/plans/` backend
- continue the normal Copilot workflow loop until a terminal state is reached
