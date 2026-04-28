---
description: Initialize shared STATUS.md and FIX.md from root and Copilot memory
agent: summary-link
---
Initialize the shared cross-workflow summary layer for this project.

Behavior:

- create `STATUS.md` and `FIX.md` if they do not already exist
- inspect `copilot/memory/` first and `memory/` second when those directories exist
- treat `copilot/memory/` as canonical and `memory/` as legacy optional input
- prefer `current.md`, `summary.md`, `watchouts.md`, `fixes.md`, and `index.json` from each stack-local memory store before drilling deeper
- use `copilot/memory/plans/` first and `memory/plans/` only when legacy attribution or conflict resolution is still needed
- do not scan `copilot/plans/` or `plans/` directly during normal shared-summary initialization when usable memory is available
- if the canonical memory store is absent or unreadable, initialize minimal shared summaries and report that gap directly
- do not edit `copilot/memory/` or `memory/`
- treat `$ARGUMENTS` as optional user preferences about scope, emphasis, or which stack to foreground

When you stop, report what shared files were initialized, what memory sources were used, the most important shared conclusions captured, and any evidence gaps that limited the first pass.
