# Plan Step

- `Plan ID`: `plans-20260321-setup-example-workflow`
- `Created`: `2026-03-21 12:00`
- `Status`: `ready`
- `Owner`: `user and plan agent`

## Goal

Validate the new plan-centered agent workflow on one safe, low-risk step.

## Background

This repository now has global `workflow`, `implementation`, `execution`, and `review` agents plus global summary templates. Before using the workflow on a real ML or code task, we want a lightweight first run that exercises the handoff pattern.

## Scope

In scope:
- verify that the workflow agent can use this plan and its sibling run directory
- have the implementation agent create a structured implementation summary for this step
- have the review agent assess whether the scaffold is usable

Out of scope:
- broad repository changes
- long-running code execution
- Slurm submission for this example unless the workflow decides a tiny dry-run artifact is justified

## Inputs

- `AGENTS.md`
- `workflow/HANDOFF_FORMAT.md`
- `agents/workflow.md`
- `agents/implementation.md`
- `agents/execution.md`
- `agents/review.md`
- `plans/README.md`

## Concrete Step

Use the workflow system on this example plan. Confirm that the handoff-file convention is clear, write the expected summaries for this step, and keep any work limited to validating the workflow scaffold itself.

## Acceptance Criteria

- the sibling run directory exists for this plan
- the agents can reference the plan and run directory without ambiguity
- the step remains narrowly scoped to workflow validation
- the resulting summaries make it obvious how a real plan step would proceed next

## Execution Notes

- no GPU is expected for this example
- avoid cluster submission unless there is a very small justified dry-run
- the preferred result is a clean workflow trace rather than a substantive code change

## Risks

- the example may be too lightweight to exercise all workflow branches
- execution may be intentionally skipped for this dry-run step

## Archive Checklist

- plan file and sibling run directory exist
- implementation, execution, review, and workflow summaries are present or intentionally skipped
- next step is recorded before moving to `plans/archive/`
