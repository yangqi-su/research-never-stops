---
description: Create the minimal OCAF-compatible scaffold in the current directory after a review pass
agent: ocaf-analysis
---
Initialize the minimal OCAF-compatible scaffold in the current directory.

Behavior:

- first obtain a safe project summary and scaffold recommendation from `ocaf-analysis-plan`
- use that planning output to make the initial `AGENTS.md` and `STATUS.md` project-aware rather than leaving them as generic placeholders
- inspect the directory safely first
- preserve existing files wherever possible
- create only the smallest useful scaffold
- prefer additive changes over replacement
- use the installed OCAF project templates under `~/.config/opencode/ocaf/templates/project/` as the baseline when helpful
- if the repository already has some framework files, add only the missing pieces or make minimal compatible updates
- do not impose a bioinformatics-specific structure unless the user explicitly asks for it

The target scaffold should usually include:

- `AGENTS.md`
- `STATUS.md`
- `plans/PLAN_TEMPLATE.md`
- `.opencode/skills/README.md`
- `.opencode/agents/README.md`
- `opencode.json` if missing

Treat any arguments as user preferences or domain hints: $ARGUMENTS
