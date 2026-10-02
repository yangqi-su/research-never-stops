---
description: Refresh shared STATUS.md and FIX.md from canonical workspace memory
agent: status
---
Refresh the shared workspace summary layer for this project through the canonical status agent.

Behavior:

- treat `STATUS.md` and `FIX.md` as shared workspace entrypoints derived only from `copilot/memory/`
- use `copilot/memory/` as the only supported workspace memory store
- compare existing shared summaries against the current stack-local memory files before deciding what to update
- prefer active memory entries over superseded ones; include superseded fixes or watchouts only when they explain an important historical trap or transition
- prefer stack-local `current.md`, `summary.md`, `watchouts.md`, `fixes.md`, and `index.json` as the normal evidence sources
- use `copilot/memory/plans/` only when plan-level attribution or conflict resolution is still needed
- let `status` directly inspect `copilot/plans/docs/` and `copilot/plans/runs/` for freshness, but do not reread detailed plan evidence when usable canonical memory is current
- refresh affected canonical `copilot/memory/` files first when plan evidence changed, then derive `STATUS.md` and `FIX.md`
- if the canonical memory store is missing or unreadable, initialize it from available plan evidence before deriving the shared files; record evidence gaps explicitly
- do not read or merge a root `memory/` store; the user handles any such merge manually before this command
- if shared summaries do not exist yet, initialize them first and then continue the refresh
- leave unchanged shared files untouched; do not rewrite them only because a scan occurred
- treat `$ARGUMENTS` as an optional scope hint or user preference about what to emphasize

When you stop, report what shared files were refreshed, whether the refresh was a no-op or material update, the most important shared updates captured, and any remaining evidence gaps.
