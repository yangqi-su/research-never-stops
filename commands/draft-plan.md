---
description: Draft a full experiment plan in conversation without writing files
agent: pro-plan
---
Draft or refine one full experiment plan using the current conversation.

Behavior:

- stay in planning mode only
- do not create or edit files
- do not scaffold directories
- do not invoke `build`, `workflow`, `implementation`, `review`, `analysis`, or `status`
- do not narrow the work to an early concrete step just to fit downstream workflow machinery
- produce one bounded experiment plan that may contain multiple ordered phases
- the concept of different phases are that of almost self containing steps that minimally overlap with one another, for instance: a phase for writing code, a phase for actual execution and monitoring, a phase for interpreting results, etc.
- add a separate dry-run or smoke-test phase only when the real run is expensive enough that a failed start would cost significant time or compute; do not add one by default
- write each phase's `Completion Criteria` as one outcome-only sentence describing what should be true scientifically; never phrase it as a file-level, hash-level, manifest-level, or schema-level check, because implementation agents turn such criteria into code
- do not write `Deliverables` that name manifests, checksums, provenance records, validation reports, or status files unless the user explicitly asked for that artifact
- keep the plan detailed enough that `/write-plan` can persist it without re-planning
- if critical information is missing, ask only the minimum questions needed or state explicit assumptions
- output the plan using this exact structure and section order

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
- `Archive Condition`: archive only after all required phases are complete or intentionally skipped with recorded justification
```

When you stop, return the full plan markdown and clearly list any unresolved assumptions.
