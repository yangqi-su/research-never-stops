---
description: Write the approved experiment plan to disk and create the workflow scaffold
agent: build
---
Use the approved full experiment plan already present in the current conversation as the canonical source.

Behavior:

- act as a mechanical persistence layer, not a planning agent
- do not brainstorm, narrow phases, or re-plan the experiment
- do not invoke `workflow`, `implementation`, `review`, `analysis`, or `status`
- validate that the approved plan follows this exact structure and section order before writing it
- if required sections are missing or materially incomplete, stop and report what is missing instead of guessing
- treat the plan file itself as the only canonical handoff artifact
- do not create any additional handoff markdown file
- ensure `copilot/plans/`, `copilot/plans/active/`, and `copilot/plans/archive/` exist if needed
- if the approved plan already contains a valid `Plan ID`, reuse it; otherwise generate `plans-<timestamp>-<slug>`
- if `Created` is missing or `TBD`, fill it with the current timestamp
- because `/write-plan` implies approval, set `Status` to `ready` when it is still `draft` or `TBD`
- preserve the approved wording and phase structure everywhere else
- write the plan file at `copilot/plans/active/<Plan ID>.md`
- create the sibling run directory at `copilot/plans/active/<Plan ID>/`
- do not create `workflow-session.json`
- do not start `workflow`

Accepted plan structure:

```md
# Experiment Plan

- `Plan ID`: `plans-<timestamp>-<slug>`, `copilot-plans-<timestamp>-<slug>`, or `TBD`
- `Created`: `YYYY-MM-DD HH:MM` or `TBD`
- `Status`: `draft`, `ready`, `in-progress`, `blocked`, or `done`
- `Owner`: `user`, `primary agent`, or both

## Goal

## Background

## Research Questions

## Scope

- `In Scope`:
- `Out of Scope`:

## Inputs

## Phases

### Phase 1: <short phase name>

- `Objective`:
- `Depends On`:
- `Deliverables`:
- `Completion Criteria`:
- `Execution Notes`:

### Phase N: <short phase name>

- `Objective`:
- `Depends On`:
- `Deliverables`:
- `Completion Criteria`:
- `Execution Notes`:

## Acceptance Criteria

## Risks

## Workflow Notes

- `Implementation Cadence`: use fresh `implementation` agent sessions across phases when helpful
- `Phase Transition Rule`: only advance after the current phase completion criteria are met or the user explicitly approves a plan change
- `Archive Condition`: archive only after all required phases are complete or intentionally skipped with recorded justification
```

When you stop, report the plan path, run directory, whether the plan was newly written or updated, and whether any header normalization was applied.
