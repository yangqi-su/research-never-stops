---
description: Write the approved Copilot workflow plan to disk and create the Copilot workflow scaffold
agent: copilot-orchestrator
---
Enter Copilot orchestrator mode `write-plan` for this task.

Behavior:

- act as a mechanical persistence layer, not a planning agent
- remain the only entry agent and delegate plan persistence internally to `copilot-write`
- require exactly one canonical Copilot plan block in conversation and pass it to `copilot-write` verbatim
- treat only orchestrator-recorded approval of the current plan revision as valid plan-write approval; planner direction checks do not count as write approval
- if the current plan revision is already approved in Copilot session state, do not ask for approval again before delegating to `copilot-write`
- validate the plan structure before writing it
- write the plan only under `copilot/plans/active/`
- create the sibling run directory if missing
- keep the plan file itself as the only canonical handoff artifact
- do not create extra handoff files
- do not start workflow automatically
