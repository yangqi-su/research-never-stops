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
- ensure `copilot/plans/docs/` and `copilot/plans/runs/` exist if needed
- if the approved plan already contains a valid `Plan ID`, reuse it; otherwise generate `plans-<timestamp>-<slug>`
- if `Created` is missing or `TBD`, fill it with the current timestamp
- because `/write-plan` implies approval, set `Status` to `ready` when it is still `draft` or `TBD`
- preserve the approved wording and phase structure everywhere else
- write the plan file at `copilot/plans/docs/<Plan ID>.md`
- create the run directory at `copilot/plans/runs/<Plan ID>/`
- for a newly written plan, create `copilot/plans/runs/<Plan ID>/PLAN_STATUS.md` containing exactly `Status: active` followed by a newline
- when updating an existing plan, require and preserve a valid existing `PLAN_STATUS.md`; do not silently repair lifecycle or reopen a finished plan
- do not create `workflow-session.json`
- do not start `workflow`

Accepted plan structure:

```md
# Experiment Plan

- `Plan ID`: `plans-<timestamp>-<slug>`, `copilot-plans-<timestamp>-<slug>`, or `TBD`
- `Created`: `YYYY-MM-DD HH:MM` or `TBD`
- `Status`: `draft`, `ready`, `in-progress`, `blocked`, or `done`
- `Owner`: `user`, `primary agent`, or both
- `Implementation Agent`: `implementation` or `pro-implementation`

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
- `Implementation Agent`: (optional; overrides plan header)
- `Commit Policy`: (optional; required only for phases that edit project repositories)

### Phase N: <short phase name>

- `Objective`:
- `Depends On`:
- `Deliverables`:
- `Completion Criteria`:
- `Execution Notes`:
- `Implementation Agent`: (optional; overrides plan header)
- `Commit Policy`: (optional; required only for phases that edit project repositories)

## Acceptance Criteria

## Risks

## Workflow Notes

- `Implementation Cadence`: use fresh implementation agent sessions across phases, respecting per-phase `Implementation Agent` overrides
- `Phase Transition Rule`: only advance after the current phase completion criteria are met or the user explicitly approves a plan change
- `Completion Condition`: mark the plan finished only after all required phases are complete or intentionally skipped with recorded justification
```

When you stop, report the plan path, run directory, whether the plan was newly written or updated, and whether any header normalization was applied.
