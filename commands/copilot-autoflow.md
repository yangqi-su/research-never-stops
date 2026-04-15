---
description: Run the Copilot end-to-end intake, planning, approval, write, and workflow-start loop
agent: copilot-orchestrator
---
Enter Copilot orchestrator mode `autoflow` for this task: $ARGUMENTS

Behavior:

- treat this as the one-shot end-to-end entrypoint for the Copilot workflow fork
- remain the only entry agent and delegate all other Copilot work internally
- clarify missing requirements with `question` rather than stopping whenever possible
- ask one focused question at a time and prefer multiple-choice questions when practical
- delegate repository grounding and planning for new work to `copilot-plan`
- allow `copilot-plan` to ask brief clarification questions and, when needed, one brief direction-check question before drafting
- keep planner and orchestrator `question` prompts concise and do not restate full plan blocks in them
- preserve the exact canonical Copilot plan block returned by `copilot-plan` only for verbatim handoff to `copilot-write`
- ask exactly one plan approval `question` with the single explicit option `Approve and write`, relying on the default freeform answer path for requested changes or cancellation
- keep final plan-write approval owned by `copilot-orchestrator`
- if the user asks for changes, resume the same `copilot-plan` session when possible and re-run approval on the revised canonical block
- after approval, delegate directly to `copilot-write` without presenting a separate next-step menu
- require explicit approval before starting execution-oriented workflow stages
- create or resume the Copilot workflow sidecar only after the plan is written and execution is approved
- when workflow reaches a justified `wait`, ask the user whether to continue monitoring inside the current session before stopping
- keep required behavior inside Copilot commands, agents, and skills rather than relying on Copilot reference docs
- when workflow reaches `blocked` or `needs-user`, ask a focused question and, unless the user explicitly pauses, stops, cancels, or defers, relay the reply back into the same workflow session and continue the loop
- keep running until a true terminal state is reached: `archive`, an explicitly accepted `wait`, unresolved `blocked` or `needs-user` after user deferral, or user refusal

When you stop, report the Copilot plan path, run directory, current state, and key evidence.
