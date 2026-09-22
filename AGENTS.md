# OpenCode Guidelines

General behavioral guidelines for working in this repository. Keep these rules broad and durable.

Default behavior:
ALWAYS perfer quick prototyping over fully robust software; ALWAYS prefer code that is easy to read and understand over multiple layers of abstractions that are difficult to follow.

Any communication with the user should use researcher and human oriented YET non software engineering language to make it easier for user to understand

## 1. Think Before Acting

- Understand the existing code, files, and local conventions before changing them.
- Do not silently assume missing requirements when they materially affect the implementation.
- If multiple reasonable interpretations exist, ask a focused question or state the tradeoff explicitly.
- Keep multi-step work goal-driven: know what success looks like before making substantial changes.

## 2. Simplicity First for Research Code: Readability and Scope

- Prefer the smallest correct solution.
- Do not add abstractions, configurability, compatibility layers, or cleanup work that was not needed for the task.
- Keep scope aligned to the user's request.

Optimize for researcher understanding and modifying the supported workflow.
Prefer straightforward code over both clever brevity and comprehensive
defensive engineering. Line count alone is not a measure of simplicity.

- Implement the requested use case, not a general framework. Support only
  the specified inputs, environment, APIs, and execution modes unless broader
  support is explicitly required.

- Keep the main scientific sequence visible. Use descriptive names and
  explicit intermediate variables where they clarify data, units, shapes,
  or scientific meaning. Avoid dense expressions and unnecessary indirection.

- Inspect relevant existing functionality before implementing an operation.
  Reuse it when its behavior matches the task. Add an adapter only for a
  concrete mismatch; do not wrap an existing function merely to rename it,
  forward arguments, or add generic checks.

- Keep one authoritative source for each setting or policy. Derive dependent
  values rather than maintaining independent copies. Record resolved values
  for reproducibility without creating another editable source of truth.

- Add helpers when they express a meaningful operation or remove substantial
  repeated logic. Do not extract trivial helpers just to shorten a function.
  Small local repetition is preferable to a confusing abstraction.

- The default number of correctness checks in new code is zero. Add a check only
  when a wrong-but-runnable result would be produced and would not be visible in
  the output, or when the operation is destructive or expensively irreversible.
  Shape, dtype, length, key, path, file, and API errors do not qualify: let them
  propagate with their native error. Place any justified check at the single
  boundary where it is needed and never repeat it downstream.

- Do not catch an exception merely to print it, re-raise it with a longer
  message, or continue past it. Add context to an error only when the native
  error genuinely does not identify the cause.

- Do not add automatic fallbacks, guessed defaults, compatibility branches,
  or silent data repair unless explicitly requested. When the supported route
  fails, stop clearly. An observed incompatibility may justify a narrow fix,
  not support for hypothetical environments.

- Comments should explain scientific reasoning, assumptions, or non-obvious
  API behavior. Do not narrate obvious statements or repeat plan history.

- Required provenance is exactly this: the resolved config and the command line,
  written once by the run wrapper. Nothing else is required. Do not write
  manifests, checksums, run metadata, or status files from inside scientific
  code, and do not add any record that has no named consumer reading it.

These rules apply to new or modified code. They do not authorize unrelated
cleanup, changes to scientific behavior, or removal of required safeguards.

## 3. Surgical Changes

- Touch only the files and lines needed for the task.
- Preserve unrelated user changes.
- Match the existing style and structure unless there is a clear reason not to.
- Do not clean up unrelated code, comments, or formatting while making the change.
- Remove only imports, variables, helpers, or dead code made unnecessary by your own edits.
- If you notice unrelated issues, mention them instead of fixing them unasked.

## 4. Safety

- Do not directly load large data, model artifacts, checkpoints, binaries, or large logs into context unless the task truly requires it.
- YOU ALWAYS operate in `./` directory, which you can find the full path via `pwd`, DO NOT operate or create files outside of this directory (because it will require asking user for permission and un-necessarily blocking the agentic workflow), especially DO NOT try to access anything directly in `/`
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

## IMPORTANT RULES

- when using `rg` add `--no-ignore-vcs` to ignore `.gitgnore`
- `Glob` is not always useful because it respects `.gitignore`, use `rg --no-ignore-vcs` or `grep` and `ls` instead
- NEVER use `Explore` agent to only read files, read files using `read` tool 
- `plan` agent should NEVER write or create files or directories
- `build` agent should perform only the requested file edits or file creation needed for the task
- `build` agent should NEVER delegate `implementation` or `pro-implementation` agents unless EXPLICITLY required by the user
- `plan` agent may use `explore` agent to explore repositories to understand structure of project
- `plan` agent may use `think` agent or `general` agent for the following subtasks:
    1. validate/review claims
    2. comeup with ideas/second opinions
    3. perform websearch about a topic or URL
