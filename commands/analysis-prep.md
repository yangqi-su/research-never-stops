---
description: Safely inspect the current project and recommend a minimal research-workflow scaffold
agent: pro-think
---
Inspect the current directory as a potential research or analysis project.

Work in safe planning mode:

- do not create or edit files
- avoid direct reads of large result, data, model, cache, and binary artifacts
- infer project structure from small files, scripts, workflow configs, manifests, README files, `AGENTS.md`, and directory layout
- identify likely languages, workflow tools, current stage, execution environments, and any existing agentic-analysis files
- identify likely large-artifact directories such as `data/`, `results/`, `output/`, `processed/`, `logs/`, `checkpoints/`, `models/`, and `artifacts/`
- determine whether this project already has `AGENTS.md`, `STATUS.md`, `.opencode/`, `copilot/plans/docs/`, `copilot/plans/runs/`, or `copilot/memory/`
- recommend the minimal project-local scaffold needed to support the research workflow
- do not assume the project is bioinformatics unless evidence or the user says so

Then provide:

1. a concise summary of what this directory appears to be doing
2. the likely project or analysis style
3. the key files or directories that support that conclusion
4. existing agentic-workflow files, if any
5. major ambiguities, risks, or large-artifact directories to avoid
6. the exact files and directories that `/analysis-init` should create or minimally update
7. optional next steps or domain-specific modules if relevant

Treat any arguments as user preferences, scope hints, or domain hints: $ARGUMENTS
