# Copilot Workflow Family

Non-canonical overview only. Runtime behavior for the Copilot workflow family lives in Copilot agent prompts, Copilot command prompts, and runtime-visible skills such as `using-copilot-workflow`.

This directory contains the shared workflow backend plus the Copilot-routed workflow family optimized for long-running agent-driven sessions that keep user interaction inside `question` calls whenever possible.

It shares plans, summaries, and memory with the root workflow family while keeping Copilot-family session files separate.

## Shared Backend

- use `copilot/plans/active/` and `copilot/plans/archive/` for Copilot workflow plans
- use `copilot/memory/` as the canonical workflow memory store
- use root `STATUS.md` and `FIX.md` as shared cross-family entrypoints
- use `copilot/workflow/` for Copilot workflow reference docs
- do not mix Copilot workflow session files with root-family session files

## Commands

- `/copilot-autoflow`
- `/copilot-draft-plan`
- `/copilot-write-plan`
- `/copilot-workflow-start`
- `/copilot-workflow-resume`
- `/copilot-workflow-status`
- `/copilot-status-init`
- `/copilot-status-update`

## Design Intent

- keep Copilot-family model routing and question-driven behavior distinct from the root family
- allow more question-driven clarification before and during execution
- keep session ledgers distinct while sharing plans, summaries, and memory
