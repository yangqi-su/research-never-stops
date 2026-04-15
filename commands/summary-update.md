---
description: Refresh shared STATUS.md and FIX.md from root and Copilot memory
agent: summary-link
---
Refresh the shared cross-workflow summary layer for this project.

Behavior:

- treat `STATUS.md` and `FIX.md` as shared cross-workflow entrypoints derived from `memory/` and `copilot/memory/`
- inspect `memory/` and `copilot/memory/` directly from the filesystem rather than inferring their existence from git-aware search
- compare existing shared summaries against the current stack-local memory files before deciding what to update
- prefer stack-local `current.md`, `summary.md`, `watchouts.md`, `fixes.md`, and `index.json` as the normal evidence sources
- use `memory/plans/` or `copilot/memory/plans/` only when needed for attribution or conflict resolution
- do not scan `plans/` or `copilot/plans/` directly during normal shared-summary refresh when stack-local memory is available
- do not edit `memory/` or `copilot/memory/`
- if one stack-local memory store is missing or unreadable, refresh from the available store and record the gap explicitly
- if shared summaries do not exist yet, initialize them first and then continue the refresh
- leave unchanged shared files untouched; do not rewrite them only because a scan occurred
- treat `$ARGUMENTS` as an optional scope hint or user preference about what to emphasize

When you stop, report what shared files were refreshed, whether the refresh was a no-op or material update, the most important shared updates captured, and any remaining evidence gaps.
