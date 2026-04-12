---
description: Draft a full Copilot workflow plan in conversation without writing files
agent: copilot-orchestrator
---
Enter Copilot orchestrator mode `draft-plan` for this task: $ARGUMENTS

Behavior:

- stay in planning mode only
- remain the only entry agent and delegate planning internally to `copilot-plan`
- do not create or edit files
- do not scaffold directories
- ask focused `question` prompts when critical information is missing
- ask one focused question at a time and prefer multiple-choice questions when practical
- use `copilot-think` selectively for exploratory or ambiguous requests
- let `copilot-plan` own repository grounding for new work and use `explore` or `general` when helpful
- produce one bounded multi-phase plan detailed enough for `copilot-write` to persist without re-planning
- return the exact canonical Copilot plan block required by `copilot-plan`
