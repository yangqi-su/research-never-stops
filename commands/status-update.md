---
description: Refresh structured workspace memory under memory/ from current active and archived plan evidence
agent: status
---
Refresh workspace memory for this project.

Behavior:

- treat `memory/` as the canonical workspace memory store
- discover plans by directly reading `plans/`, `plans/active/`, and `plans/archive/` from the filesystem rather than using glob-style or git-aware discovery
- treat ignored `plans/` directories as valid status input; `.gitignore` must not affect plan discovery
- compare discovered plans and run-directory summaries against `memory/index.json` first, then inspect only the missing or stale plan evidence in detail
- use the root `AGENTS.md` only as secondary project framing after plan discovery; do not read nested `README.md` files during normal updates
- if `plans/active/` and `plans/archive/` are absent or unreadable, report that directly and refresh only minimal memory instead of inferring workflow history from unrelated repo files
- update only the affected memory artifacts under `memory/`, including relevant per-plan files, `memory/index.json`, and aggregate files whose conclusions materially changed
- do not recreate any step-level memory layer under `memory/`
- leave unchanged files untouched; do not rewrite top-level summaries only because a scan occurred
- refresh short compatibility entrypoints at `STATUS.md` and `FIX.md` only when their linked summaries or main conclusions changed
- prioritize active plans when updating the current workspace view
- use archived plans heavily for durable fixes, watchouts, and plan history
- only elevate repeated, costly, difficult, or broadly reusable lessons into `memory/watchouts.md` and `memory/fixes.md`
- if memory has not been initialized yet, initialize it first and then continue the refresh
- treat `$ARGUMENTS` as an optional plan selector, scope hint, or user preference about what to emphasize

When you stop, report what memory was refreshed, whether the refresh was a no-op or material update, the most important updates captured, and any evidence gaps that still remain.
