# Workflow Handoff Format

Use concise Markdown summaries with the same stable header block and section order.

## Required header block

Every workflow summary file should begin with these bullet fields:

- `Plan ID`: stable stem such as `plans-20260321-1530-train-baseline`
- `Plan`: current path to the plan file
- `Run Directory`: current path to the sibling run directory
- `Path State`: `active` or `archived`
- `Status`: `success`, `failed`, `partial`, `blocked`, `running`, or `not-run`
- `Step`: one-line description of the concrete step
- `Timestamp`: creation or update time if known

## Common writing rules

- Prefer short factual sections over long prose.
- Reference file paths instead of dumping large logs or artifacts.
- Distinguish confirmed results from hypotheses.
- Keep scope tied to one concrete plan step.
- If the step is archived, update the header paths to the archived location.

## Standard files

- `planning-handoff.md` when upstream approved context was provided
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
- `analysis-summary.md` should expose what the current step taught us, the main findings and caveats, and the recommended completion or follow-up state after meaningful outputs exist.

## Planning handoff file

- `planning-handoff.md` should preserve approved upstream wording as literally as possible.
- Use it as the canonical preserved handoff context, not as a fresh summary.
- Add only minimal appended clarification when needed to name the already-selected concrete step.

## Historical note

- Older archived examples may still mention `execution-summary.md` from an earlier workflow version. Treat `implementation-summary.md` as the current unified execution record.
