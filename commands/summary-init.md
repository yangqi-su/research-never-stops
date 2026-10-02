---
description: Initialize shared STATUS.md and FIX.md from canonical workspace memory
agent: status
---
Initialize the shared workspace summary layer for this project through the canonical status agent.

Behavior:

- create `STATUS.md` and `FIX.md` if they do not already exist
- use `copilot/memory/` as the only supported workspace memory store
- prefer `current.md`, `summary.md`, `watchouts.md`, `fixes.md`, and `index.json` before drilling deeper
- prefer active memory entries over superseded ones; include superseded fixes or watchouts only when they explain an important historical trap or transition
- use `copilot/memory/plans/` only when plan-level attribution or conflict resolution is still needed
- let `status` directly inspect `copilot/plans/docs/` and `copilot/plans/runs/` for freshness, but do not reread detailed plan evidence when usable canonical memory is current
- if the canonical memory store is absent or unreadable, initialize it from available plan evidence; if no plan evidence exists, create minimal canonical memory that records the gap
- do not read or merge a root `memory/` store; the user handles any such merge manually before this command
- initialize or refresh canonical `copilot/memory/` first when it is missing or stale, then derive `STATUS.md` and `FIX.md`
- treat `$ARGUMENTS` as optional user preferences about scope, emphasis, or which stack to foreground

When you stop, report what memory and shared files were initialized, what evidence was used, the most important conclusions captured, and any evidence gaps that limited the first pass.
