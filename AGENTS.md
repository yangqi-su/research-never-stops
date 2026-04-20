# OpenCode Guidelines

General behavioral guidelines for working in this repository. Keep these rules broad and durable.

## 1. Think Before Acting

- Understand the existing code, files, and local conventions before changing them.
- Do not silently assume missing requirements when they materially affect the implementation.
- If multiple reasonable interpretations exist, ask a focused question or state the tradeoff explicitly.
- Keep multi-step work goal-driven: know what success looks like before making substantial changes.

## 2. Simplicity First

- Prefer the smallest correct solution.
- Do not add abstractions, configurability, compatibility layers, or cleanup work that was not needed for the task.
- Keep scope aligned to the user's request.

## 3. Surgical Changes

- Touch only the files and lines needed for the task.
- Preserve unrelated user changes.
- Match the existing style and structure unless there is a clear reason not to.
- Do not clean up unrelated code, comments, or formatting while making the change.
- Remove only imports, variables, helpers, or dead code made unnecessary by your own edits.
- If you notice unrelated issues, mention them instead of fixing them unasked.

## 4. Safety

- Do not directly load large data, model artifacts, checkpoints, binaries, or large logs into context unless the task truly requires it.
- Prefer lightweight metadata, configs, manifests, small scripts, and concise summaries over heavy raw outputs.
- If a change may affect user-owned configuration, workflow state, or results, prefer the smallest safe update and preserve existing information.
- If evidence is missing or ambiguous, say so directly instead of guessing or ask user for clarification or help.

## 5. Verify Outcomes

- Use the lightest verification that can show the task is done correctly.
- When possible, tie verification directly to the user's goal.
- If something could not be verified, say so plainly and explain the gap.

## 6. Keep Context Lightweight

- Prefer small source files, configs, manifests, and summaries over large logs or artifacts.
- Use specialized agents, commands, and skills only when the task clearly calls for them.
- Detailed workflow, execution, and command behavior belongs in the relevant agent, command, or skill instructions, not here.

## EXTRA:

- when using `rg` add `--no-ignore-vcs` to ignore `.gitgnore`