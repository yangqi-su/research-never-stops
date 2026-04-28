---
description: Report the current Copilot workflow status without forcing the full Copilot loop
agent: copilot-orchestrator
---
Enter Copilot orchestrator mode `workflow-status` for this task: $ARGUMENTS

Behavior:

- summarize the latest Copilot workflow state files
- remain the only entry agent and delegate workflow inspection internally when needed
- prefer existing Copilot summaries over reconstruction
- keep Copilot-family session handling distinct from root-family session files while using the shared `copilot/plans/` backend
- if state looks stale or contradictory, say so plainly and recommend `/copilot-workflow-resume`
