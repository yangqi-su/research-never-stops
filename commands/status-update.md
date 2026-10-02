---
description: Refresh structured workspace memory and shared STATUS.md and FIX.md from stable plan evidence
agent: status
---
Refresh workspace memory for this project.

Behavior:

- treat `copilot/memory/` as the canonical workspace memory store
- discover plan documents and run directories by directly reading `copilot/plans/docs/` and `copilot/plans/runs/` from the filesystem rather than using glob-style or git-aware discovery
- treat ignored plan directories as valid status input; `.gitignore` must not affect plan discovery
- derive lifecycle only from each run directory's `PLAN_STATUS.md`; report missing or invalid lifecycle rather than guessing
- compare discovered plans and run-directory summaries against `copilot/memory/index.json` first, then inspect only the missing or stale plan evidence in detail
- for `claude-plans-*`, use the plan-document `Progress Log`, run-directory `findings.md`, and `PLAN_STATUS.md`; register existing Claude-owned memory pages without creating or rewriting them
- determine memory-page ownership from `Memory Owner`, not `Plan Type` or the ID prefix; preserve every page marked `Memory Owner: claude`, and leave a Claude-workflow page with missing or conflicting ownership untouched while reporting the ambiguity
- when many plans exist, prioritize missing, stale, active, recently changed, or directly relevant plans instead of rereading all finished evidence
- reconcile new evidence against existing memory and update or mark superseded findings, fixes, watchouts, and conclusions rather than only appending new entries
- use the root `AGENTS.md` only as secondary project framing after plan discovery; do not read nested `README.md` files during normal updates
- if `copilot/plans/docs/` and `copilot/plans/runs/` are absent or unreadable, report that directly and refresh only minimal memory instead of inferring workflow history from unrelated repo files
- update only the affected memory artifacts under `copilot/memory/`, including relevant per-plan files, `copilot/memory/index.json`, and aggregate files whose conclusions materially changed
- do not recreate any step-level memory layer under `copilot/memory/`
- leave unchanged files untouched; do not rewrite top-level summaries only because a scan occurred
- refresh shared `STATUS.md` and `FIX.md` from canonical memory when their content materially changes
- prioritize active plans when updating the current workspace view
- use finished plans heavily for durable fixes, watchouts, and plan history
- only elevate repeated, costly, difficult, or broadly reusable lessons into `copilot/memory/watchouts.md` and `copilot/memory/fixes.md`
- mark older fixes or watchouts as superseded when newer confirmed evidence replaces them, and mark unresolved conflicts as `uncertain`
- if memory has not been initialized yet, initialize it first and then continue the refresh
- treat `$ARGUMENTS` as an optional plan selector, scope hint, or user preference about what to emphasize

When you stop, report what memory was refreshed, whether the refresh was a no-op or material update, the most important updates captured, and any evidence gaps that still remain.
