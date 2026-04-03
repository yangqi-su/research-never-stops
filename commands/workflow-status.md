---
description: Report the current workflow status without running the full orchestration loop
agent: orchestrator
---
Inspect the current workflow state for this project.

Behavior:

- use `$ARGUMENTS` as an optional plan id or plan path selector
- if multiple active plans exist and the arguments do not identify one, ask one focused question
- summarize the active or archived plan, run directory, and the latest `workflow-summary.md`, `implementation-summary.md`, `review-summary.md`, and `analysis-summary.md` state if present
- do not invoke `implementation`, `review`, or `analysis`
- prefer passive status reporting from the existing summaries and session files rather than reconstructing workflow state yourself
- only resume `workflow` if the user explicitly asks for a refreshed status or if the existing summaries are too stale or contradictory to summarize responsibly
- if meaningful outputs appear to exist but no `analysis-summary.md` is present yet, say that a full resume would likely continue with `analysis`

Report the current workflow state, the latest evidence, whether the summaries appear fresh or stale, and whether a resume would continue work or remain blocked.
