# OCAF Core Safety

These instructions apply across analysis-focused OpenCode work.

- Prefer safe inspection before action.
- Do not directly read or dump large binary, matrix, model, cache, or result artifacts into context unless the task explicitly requires it and no lighter summary is available.
- Prefer directory structure, filenames, manifests, config files, workflow definitions, and lightweight metadata summaries over raw outputs.
- If a task may alter user configuration, preserve existing files and prefer additive changes.
- If a file already exists and ownership is unclear, update minimally and explain the change.
- Separate project understanding from project modification.
- Summarize findings clearly before proposing irreversible or wide-scope actions.
