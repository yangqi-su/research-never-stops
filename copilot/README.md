# Copilot Workflow Fork

Non-canonical overview only. Runtime behavior for the Copilot workflow fork lives in Copilot agent prompts, Copilot command prompts, and runtime-visible skills such as `using-copilot-workflow`.

This directory contains a fully separate workflow stack optimized for long-running agent-driven sessions that keep user interaction inside `question` calls whenever possible.

It is intentionally isolated from the stable root workflow.

## Separation

- use `copilot/plans/active/` and `copilot/plans/archive/` for Copilot workflow plans
- use `copilot/memory/` for Copilot memory only
- use root `STATUS.md` and `FIX.md` only as shared cross-stack entrypoints; do not treat them as Copilot-owned memory
- use `copilot/workflow/` for Copilot workflow reference docs
- do not mix Copilot workflow session files with the root `plans/` workflow

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

- keep the stable workflow unchanged
- allow more question-driven clarification before and during execution
- keep plans, summaries, and sessions isolated to avoid cross-stack collisions
