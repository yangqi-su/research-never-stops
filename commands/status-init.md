---
description: Initialize structured workspace memory under memory/ from active and archived plans
agent: status
---
Initialize workspace memory for this project.

Behavior:

- create the canonical `memory/` directory structure if it does not already exist
- treat `memory/` as the canonical workspace memory store
- discover plans by directly reading `plans/`, `plans/active/`, and `plans/archive/` from the filesystem rather than using glob-style or git-aware discovery
- treat ignored `plans/` directories as valid status input; `.gitignore` must not affect plan discovery
- backfill from both `plans/active/` and `plans/archive/`
- when archived plans already exist, backfill all of them rather than only the newest ones
- compare discovered plans against existing `memory/index.json` first, then inspect the plan file and sibling run-directory summaries only for missing or stale plan memory
- use the root `AGENTS.md` only as secondary project framing after plan discovery; do not read nested `README.md` files during normal initialization
- if `plans/active/` and `plans/archive/` are absent or unreadable, initialize minimal memory and report that directly instead of inferring workflow history from unrelated repo files
- create missing baseline files under `memory/` and backfill missing or materially stale plan memory
- do not create a `memory/steps/` layer; use `memory/plans/<plan-id>.md` as the only per-plan drill-down page
- update aggregate files such as `memory/current.md`, `memory/summary.md`, `memory/watchouts.md`, `memory/fixes.md`, and `memory/plans/index.md` only when the synthesized conclusions materially change
- do not create or refresh shared `STATUS.md` or `FIX.md`; use `/summary-init` or `/summary-update` for the shared layer
- only elevate repeated, costly, difficult, or broadly reusable lessons into `memory/watchouts.md` and `memory/fixes.md`
- preserve useful existing memory content unless it is contradicted, superseded, or clearly low-value noise
- do not regenerate all memory files just because initialization was invoked
- treat `$ARGUMENTS` as optional user preferences about scope, emphasis, or plan selection

When you stop, report what memory was initialized, what evidence was backfilled, and any gaps that limited the first pass.
