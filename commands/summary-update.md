---
description: Refresh shared STATUS.md and FIX.md from root and Copilot memory
agent: summary-link
---
Refresh the shared cross-workflow summary layer for this project.

Behavior:

- treat `STATUS.md` and `FIX.md` as shared cross-workflow entrypoints derived primarily from `copilot/memory/` and secondarily from legacy `memory/` when it exists
- inspect `copilot/memory/` first and `memory/` second when those directories exist
- compare existing shared summaries against the current stack-local memory files before deciding what to update
- prefer stack-local `current.md`, `summary.md`, `watchouts.md`, `fixes.md`, and `index.json` as the normal evidence sources
- use `copilot/memory/plans/` first and `memory/plans/` only when legacy attribution or conflict resolution is still needed
- do not scan `copilot/plans/` or `plans/` directly during normal shared-summary refresh when usable memory is available
- do not edit `copilot/memory/` or `memory/`
- if the canonical memory store is missing or unreadable, refresh from any available legacy store and record the gap explicitly
- if shared summaries do not exist yet, initialize them first and then continue the refresh
- leave unchanged shared files untouched; do not rewrite them only because a scan occurred
- treat `$ARGUMENTS` as an optional scope hint or user preference about what to emphasize

When you stop, report what shared files were refreshed, whether the refresh was a no-op or material update, the most important shared updates captured, and any remaining evidence gaps.
