# Plan Step

- `Plan ID`: `plans-<timestamp>-<slug>`
- `Created`: `YYYY-MM-DD HH:MM`
- `Status`: `draft`, `ready`, `in-progress`, `blocked`, or `done`
- `Owner`: `user`, `plan agent`, or both

## Goal

What should this single concrete step achieve?

## Background

Short context needed to understand the step.

## Scope

List what is in scope and out of scope for this step.

## Inputs

Reference the files, configs, scripts, or prior plans that matter.

## Concrete Step

Describe the exact decision-bearing research unit to hand to the workflow agent.

## Acceptance Criteria

Define how success will be judged.

## Execution Notes

Note expected commands, environment details, CPU or GPU expectations, and expected outputs if known.

## Risks

List important unknowns, resource constraints, or dependencies.

## Archive Checklist

- plan file and sibling run directory exist
- `planning-handoff.md` exists when upstream planning context was provided
- implementation, review, and workflow summaries are present or intentionally skipped
- analysis and result-manifest artifacts are present or intentionally skipped when the step produced interpretable outputs or external results
- optional execution artifacts in the run directory are recorded if they were created
- next step is recorded before moving to `plans/archive/`
