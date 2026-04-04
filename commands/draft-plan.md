---
description: Draft a full experiment plan in conversation without writing files
agent: plan
---
Draft or refine one full experiment plan using the current conversation.

Behavior:

- stay in planning mode only
- do not create or edit files
- do not scaffold directories
- do not invoke `build`, `workflow`, `implementation`, `review`, `analysis`, or `status`
- if the task is exploratory or ambiguous, selectively use `think` before finalizing the plan
- do not narrow the work to an early concrete step just to fit downstream workflow machinery
- produce one bounded experiment plan that may contain multiple ordered phases
- the concept of different phases are that of almost self containing steps that minimally overlap with one another, for instance: a phase for writing code, a phase for smoke tests/dry-runs, a phase for actual execution and monitoring, etc.
- keep the plan detailed enough that `/write-plan` can persist it without re-planning
- if critical information is missing, ask only the minimum questions needed or state explicit assumptions
- output the plan using this exact structure and section order

```md
# Experiment Plan

- `Plan ID`: `plans-<timestamp>-<slug>` or `TBD`
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

When you stop, return the full plan markdown and clearly list any unresolved assumptions.
