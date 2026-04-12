---
description: Initialize Copilot workspace memory under copilot/memory from Copilot plan evidence
agent: copilot-status
---
Initialize Copilot workspace memory for this project.

Behavior:

- create the canonical `copilot/memory/` directory structure if it does not already exist
- use `copilot/memory/` as the canonical memory store
- discover plans by directly reading `copilot/plans/`, `copilot/plans/active/`, and `copilot/plans/archive/` from the filesystem rather than using glob-style or git-aware discovery
- treat ignored Copilot plan directories as valid status input; `.gitignore` must not affect Copilot plan discovery
- backfill from both `copilot/plans/active/` and `copilot/plans/archive/`
- when archived Copilot plans already exist, backfill all of them rather than only the newest ones
- compare discovered Copilot plans against existing `copilot/memory/index.json` first, then inspect the plan file and sibling run-directory summaries only for missing or stale plan memory
- use the root `AGENTS.md` only as secondary project framing after Copilot plan discovery; do not read nested `README.md` files during normal initialization
- if `copilot/plans/active/` and `copilot/plans/archive/` are absent or unreadable, initialize minimal Copilot memory and report that directly instead of inferring workflow history from unrelated repo files
- create missing baseline files under `copilot/memory/` and backfill missing or materially stale Copilot plan memory
- do not create root `memory/`, `STATUS.md`, or `FIX.md`
- do not create a second compatibility-entrypoint layer under `copilot/`
- update aggregate Copilot memory files only when the synthesized conclusions materially change
- only elevate repeated, costly, difficult, or broadly reusable lessons into `copilot/memory/watchouts.md` and `copilot/memory/fixes.md`
- preserve useful existing Copilot memory unless it is contradicted, superseded, or clearly low-value noise
- treat `$ARGUMENTS` as optional user preferences about scope, emphasis, or plan selection

When you stop, report what Copilot memory was initialized, what evidence was backfilled, and any gaps that limited the first pass.
