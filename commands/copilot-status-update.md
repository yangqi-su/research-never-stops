---
description: Refresh shared workflow memory under copilot/memory via the Copilot status agent
agent: copilot-status
---
Refresh shared workflow memory for this project through the Copilot status agent.

Behavior:

- treat `copilot/memory/` as the canonical shared workflow memory store
- discover plans by directly reading `copilot/plans/`, `copilot/plans/active/`, and `copilot/plans/archive/` from the filesystem rather than using glob-style or git-aware discovery
- treat ignored plan directories as valid status input; `.gitignore` must not affect plan discovery
- compare discovered plans and run-directory summaries against `copilot/memory/index.json` first, then inspect only the missing or stale plan evidence in detail
- use the root `AGENTS.md` only as secondary project framing after plan discovery; do not read nested `README.md` files during normal updates
- if `copilot/plans/active/` and `copilot/plans/archive/` are absent or unreadable, report that directly and refresh only minimal memory instead of inferring workflow history from unrelated repo files
- update only the affected memory artifacts under `copilot/memory/`, including relevant per-plan files, `copilot/memory/index.json`, and aggregate files whose conclusions materially changed
- leave unchanged memory files untouched; do not rewrite top-level summaries only because a scan occurred
- prioritize active plans when updating `copilot/memory/current.md`
- use archived plans heavily for durable fixes, watchouts, and plan history
- if memory has not been initialized yet, initialize it first and then continue the refresh
- do not edit root `memory/`
- do not edit shared root `STATUS.md` or `FIX.md`; use `/summary-update` when the shared layer should be refreshed
- do not create a second compatibility-entrypoint layer under `copilot/`
- treat `$ARGUMENTS` as an optional plan selector, scope hint, or user preference about what to emphasize

When you stop, report what memory was refreshed, whether the refresh was a no-op or material update, the most important updates captured, and any evidence gaps that still remain.
