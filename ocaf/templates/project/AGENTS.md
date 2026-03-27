# Project Analysis Rules

This repository uses an agent-assisted analysis workflow.

## Working style

- prefer planning before editing
- keep changes small and reviewable
- inspect scripts, configs, and lightweight metadata before proposing broader changes
- preserve existing project conventions unless there is a clear reason to change them

## Safety

- do not directly read large data, results, binary artifacts, or large logs into context
- prefer metadata summaries, manifests, and directory inspection first
- note which conclusions are confirmed facts versus inferences

## Output style

- summarize findings clearly
- reference key files used for conclusions
- separate project understanding from modification proposals
