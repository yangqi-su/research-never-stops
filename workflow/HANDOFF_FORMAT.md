# Workflow Handoff Format

Reference only: the canonical summary formats live in the agent and command prompts that actually run. Use concise Markdown summaries with the same stable header block and section order.

## Required header block

Every workflow summary file should begin with these bullet fields:

- `Plan ID`: stable stem such as `plans-20260321-1530-train-baseline`
- `Plan`: current path to the plan file
- `Run Directory`: current path to the sibling run directory
- `Path State`: `active` or `archived`
- `Status`: `success`, `failed`, `partial`, `blocked`, `running`, or `not-run`
- `Phase`: one-line description of the current active phase
- `Timestamp`: creation or update time if known

## Common writing rules

- Prefer short factual sections over long prose.
- Reference file paths instead of dumping large logs or artifacts.
- Distinguish confirmed results from hypotheses.
- Keep scope tied to one full plan and one current active phase within that plan.
- If the plan is archived, update the header paths to the archived location.

## Standard files

- `implementation-summary.md`
- `review-summary.md`
- `analysis-summary.md` when meaningful outputs need interpretation
- `workflow-summary.md`
- `result-manifest.md` when canonical outputs are external

## Decision contracts

- `workflow-summary.md` should expose the next orchestration decision for `orchestrator`.
- `workflow-summary.md` should include a short `Decision Basis` so `orchestrator` can relay the workflow decision without reconstructing the state itself.
- `implementation-summary.md` should expose both the execution-routing decision and the resulting execution state.
- `review-summary.md` should expose the recommended recovery or completion state after escalation.
- `analysis-summary.md` should expose what the current phase taught us, the main findings and caveats, and the recommended completion or follow-up state after meaningful outputs exist.

## Historical note

- Older archived examples may still mention `execution-summary.md` from an earlier workflow version. Treat `implementation-summary.md` as the current unified execution record.
