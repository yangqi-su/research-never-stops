---
description: Report the current workflow status without running the full orchestration loop
agent: orchestrator
---
Inspect the current workflow state for this project.

Behavior:

- use `$ARGUMENTS` as an optional plan id or plan path selector under the shared `copilot/plans/` backend
- if multiple active plans exist and the arguments do not identify one, ask one focused question
- resolve the plan document under `copilot/plans/docs/`, its matching directory under `copilot/plans/runs/`, and lifecycle from `PLAN_STATUS.md`
- exclude `claude-plans-*` from automatic selection; when one is explicitly selected, report only its Claude ownership, plan path, run directory, and authoritative lifecycle without invoking `workflow` or requiring OpenCode summaries
- summarize active or finished lifecycle separately from execution progress, along with root session files such as `workflow-session-root.json` and `agent-sessions-root.json` and the latest bounded summaries when present
- permit passive inspection of a finished plan without reopening it; do not treat run-only historical families as executable plans
- report the selected `Implementation Agent` from `workflow-summary.md` when present
- do not invoke `implementation`, `review`, or `analysis`
- prefer passive status reporting from the existing summaries and session files rather than reconstructing workflow state yourself
- only resume `workflow` if the user explicitly asks for a refreshed status or if the existing summaries are too stale or contradictory to summarize responsibly
- if meaningful outputs appear to exist for the current phase but no `analysis-summary.md` is present yet, say that a full resume would likely continue with `analysis`

Report the current workflow state, the latest evidence, whether the summaries appear fresh or stale, and whether a resume would continue work or remain blocked.
