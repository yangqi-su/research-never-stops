---
description: Initialize shared workflow memory under copilot/memory via the Copilot status agent
agent: copilot-status
---
Initialize shared workflow memory for this project through the Copilot status agent.

Behavior:

- create the canonical `copilot/memory/` directory structure if it does not already exist
- use `copilot/memory/` as the canonical shared memory store
- discover plans by directly reading `copilot/plans/`, `copilot/plans/active/`, and `copilot/plans/archive/` from the filesystem rather than using glob-style or git-aware discovery
- treat ignored plan directories as valid status input; `.gitignore` must not affect plan discovery
- backfill from both `copilot/plans/active/` and `copilot/plans/archive/`
- when archived plans already exist, backfill all of them rather than only the newest ones
- compare discovered plans against existing `copilot/memory/index.json` first, then inspect the plan file and sibling run-directory summaries only for missing or stale plan memory
- use the root `AGENTS.md` only as secondary project framing after plan discovery; do not read nested `README.md` files during normal initialization
- if `copilot/plans/active/` and `copilot/plans/archive/` are absent or unreadable, initialize minimal memory and report that directly instead of inferring workflow history from unrelated repo files
- create missing baseline files under `copilot/memory/` and backfill missing or materially stale plan memory
- do not create root `memory/`
- do not create or refresh shared root `STATUS.md` or `FIX.md`; use `/summary-init` or `/summary-update` for that layer
- do not create a second compatibility-entrypoint layer under `copilot/`
- update aggregate memory files only when the synthesized conclusions materially change
- only elevate repeated, costly, difficult, or broadly reusable lessons into `copilot/memory/watchouts.md` and `copilot/memory/fixes.md`
- preserve useful existing memory unless it is contradicted, superseded, or clearly low-value noise
- treat `$ARGUMENTS` as optional user preferences about scope, emphasis, or plan selection

When you stop, report what memory was initialized, what evidence was backfilled, and any gaps that limited the first pass.
