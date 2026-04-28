# Copilot Plans Workflow

Non-canonical overview only. Runtime behavior for Copilot plan creation, writing, lifecycle, and archival lives in Copilot agent prompts, Copilot command prompts, and runtime-visible skills.

Use `copilot/plans/active/` for in-progress workflow plans and `copilot/plans/archive/` for completed ones.

## Naming

- active plan files may use `copilot-plans-<timestamp>-<slug>.md` or `plans-<timestamp>-<slug>.md`
- each active plan file should have a sibling run directory with the same stem

## Expected run-directory files

- `workflow-session.json`
- `agent-sessions.json`
- `workflow-session-root.json` when the root family takes over the same plan
- `agent-sessions-root.json` when the root family takes over the same plan
- `workflow-summary.md`
- `implementation-summary.md`
- `review-summary.md`
- `analysis-summary.md` when needed
- `result-manifest.md` when canonical results live elsewhere

## Lifecycle

1. Use `/copilot-autoflow` for end-to-end intake, planning, approval, writing, and workflow start.
2. Use `/copilot-draft-plan` for planning only.
3. Use `/copilot-write-plan` to persist an approved Copilot plan.
4. Use `/copilot-workflow-start` or `/copilot-workflow-resume` to run the Copilot workflow loop.
5. Archive only when the full Copilot plan is complete.

## Session Rules

- keep Copilot-family session files separate from root-family session files
- treat `workflow-summary.md` and the plan markdown as the canonical shared state across families
- treat task IDs as family-local advisory state rather than shared workflow truth
