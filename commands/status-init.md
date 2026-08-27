---
description: Initialize structured workspace memory under copilot/memory/ from shared active and archived plans
agent: status
---
Initialize workspace memory for this project.

Behavior:

- create the canonical `copilot/memory/` directory structure if it does not already exist
- treat `copilot/memory/` as the canonical workspace memory store
- discover plans by directly reading `copilot/plans/`, `copilot/plans/active/`, and `copilot/plans/archive/` from the filesystem rather than using glob-style or git-aware discovery
- treat ignored plan directories as valid status input; `.gitignore` must not affect plan discovery
- backfill from both `copilot/plans/active/` and `copilot/plans/archive/`
- when archived plans already exist, backfill all of them rather than only the newest ones
- compare discovered plans against existing `copilot/memory/index.json` first, then inspect the plan file and sibling run-directory summaries only for missing or stale plan memory
- when many plans exist, prioritize missing, stale, active, recently changed, or directly relevant plans instead of rereading all archived evidence
- reconcile new evidence against existing memory and update or mark superseded findings, fixes, watchouts, and conclusions rather than only appending new entries
- use the root `AGENTS.md` only as secondary project framing after plan discovery; do not read nested `README.md` files during normal initialization
- if `copilot/plans/active/` and `copilot/plans/archive/` are absent or unreadable, initialize minimal memory and report that directly instead of inferring workflow history from unrelated repo files
- create missing baseline files under `copilot/memory/` and backfill missing or materially stale plan memory
- do not create a step-level layer; use `copilot/memory/plans/<plan-id>.md` as the only per-plan drill-down page
- update aggregate files such as `copilot/memory/current.md`, `copilot/memory/summary.md`, `copilot/memory/watchouts.md`, `copilot/memory/fixes.md`, and `copilot/memory/plans/index.md` only when the synthesized conclusions materially change
- do not create or refresh shared `STATUS.md` or `FIX.md`; use `/summary-init` or `/summary-update` for the shared layer
- only elevate repeated, costly, difficult, or broadly reusable lessons into `copilot/memory/watchouts.md` and `copilot/memory/fixes.md`
- mark older fixes or watchouts as superseded when newer confirmed evidence replaces them, and mark unresolved conflicts as `uncertain`
- preserve useful existing memory content unless it is contradicted, superseded, or clearly low-value noise
- do not regenerate all memory files just because initialization was invoked
- treat `$ARGUMENTS` as optional user preferences about scope, emphasis, or plan selection

When you stop, report what memory was initialized, what evidence was backfilled, and any gaps that limited the first pass.
