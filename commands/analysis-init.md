---
description: Initialize a minimal project-local scaffold for the research workflow
agent: build
---
Initialize the minimal project-local scaffold for the research workflow in the current directory.

Behavior:

- use the latest `/analysis-prep` output when available; otherwise inspect the directory safely before writing
- make `AGENTS.md` and `STATUS.md` project-aware rather than generic placeholders
- preserve existing files wherever possible
- create only the smallest useful scaffold
- prefer additive changes over replacement
- if `AGENTS.md`, `STATUS.md`, `.opencode/`, `copilot/plans/`, or `copilot/memory/` already exists, add only missing pieces or make minimal compatible updates
- if ownership or intended content is unclear, stop and ask rather than overwriting
- do not copy global agents, commands, skills, or workflow reference files into the project by default
- project-local files should capture project context, constraints, output locations, and safety notes, not duplicate global workflow mechanics
- do not impose a bioinformatics-specific structure unless the user explicitly asks for it

The target scaffold should usually include:

- `AGENTS.md` if missing, or a minimal additive update if present
- `STATUS.md` if missing
- `copilot/plans/active/`
- `copilot/plans/archive/`
- `opencode.json` if missing, containing an empty JSON object: `{}`

Only create `copilot/memory/` when the user asks to initialize durable memory now; otherwise leave memory creation to `/status-init`.

Treat any arguments as user preferences or domain hints: $ARGUMENTS
