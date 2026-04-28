---
description: Refresh structured workspace memory under copilot/memory/ from shared active and archived plan evidence
agent: status
---
Refresh workspace memory for this project.

Behavior:

- treat `copilot/memory/` as the canonical workspace memory store
- discover plans by directly reading `copilot/plans/`, `copilot/plans/active/`, and `copilot/plans/archive/` from the filesystem rather than using glob-style or git-aware discovery
- treat ignored plan directories as valid status input; `.gitignore` must not affect plan discovery
- compare discovered plans and run-directory summaries against `copilot/memory/index.json` first, then inspect only the missing or stale plan evidence in detail
- use the root `AGENTS.md` only as secondary project framing after plan discovery; do not read nested `README.md` files during normal updates
- if `copilot/plans/active/` and `copilot/plans/archive/` are absent or unreadable, report that directly and refresh only minimal memory instead of inferring workflow history from unrelated repo files
- update only the affected memory artifacts under `copilot/memory/`, including relevant per-plan files, `copilot/memory/index.json`, and aggregate files whose conclusions materially changed
- do not recreate any step-level memory layer under `copilot/memory/`
- leave unchanged files untouched; do not rewrite top-level summaries only because a scan occurred
- do not edit shared `STATUS.md` or `FIX.md`; use `/summary-update` when the shared layer should be refreshed
- prioritize active plans when updating the current workspace view
- use archived plans heavily for durable fixes, watchouts, and plan history
- only elevate repeated, costly, difficult, or broadly reusable lessons into `copilot/memory/watchouts.md` and `copilot/memory/fixes.md`
- if memory has not been initialized yet, initialize it first and then continue the refresh
- treat `$ARGUMENTS` as an optional plan selector, scope hint, or user preference about what to emphasize

When you stop, report what memory was refreshed, whether the refresh was a no-op or material update, the most important updates captured, and any evidence gaps that still remain.
