---
description: Initialize shared STATUS.md and FIX.md from root and Copilot memory
agent: summary-link
---
Initialize the shared cross-workflow summary layer for this project.

Behavior:

- create `STATUS.md` and `FIX.md` if they do not already exist
- inspect `memory/` and `copilot/memory/` directly from the filesystem rather than inferring their existence from git-aware search
- treat stack-local memory stores as the source of truth for their own workflow stacks
- prefer `current.md`, `summary.md`, `watchouts.md`, `fixes.md`, and `index.json` from each stack-local memory store before drilling deeper
- use `memory/plans/` or `copilot/memory/plans/` only when needed for attribution or conflict resolution
- do not scan `plans/` or `copilot/plans/` directly during normal shared-summary initialization when stack-local memory is available
- if one or both stack-local memory stores are absent or unreadable, initialize minimal shared summaries and report that gap directly
- do not edit `memory/` or `copilot/memory/`
- treat `$ARGUMENTS` as optional user preferences about scope, emphasis, or which stack to foreground

When you stop, report what shared files were initialized, what memory sources were used, the most important shared conclusions captured, and any evidence gaps that limited the first pass.
