---
name: using-research-workflow
description: Use when the user wants the plan-centered research workflow with explicit human checkpoints, project-local scaffolding, workflow state, implementation, review, analysis, and memory updates.
compatibility: opencode
metadata:
  domain: workflow
  workflow: research-assistant
---

# Using Research Workflow

Use this skill when the user explicitly wants to use the plan-centered research workflow for a bounded research, analysis, or experiment task.

## When To Use

Use this skill when any of the following are true:

- the user asks to draft, write, start, resume, or inspect a workflow plan
- the task benefits from a written multi-phase plan and run directory
- the task involves code writing plus execution, review, analysis, or result interpretation
- the user wants structured human-in-the-loop research assistance rather than full automation

Do not use this skill for simple one-off edits, short explanations, or direct questions that do not need a plan.

## Entry Points

- Use `/analysis-prep` to inspect a new project and recommend a minimal research-workflow scaffold without editing files.
- Use `/analysis-init` to create the minimal project-local scaffold after safe inspection or user direction.
- Use `/draft-plan` to draft or refine a full experiment plan in conversation only.
- Use `/write-plan` to persist an approved full plan under `copilot/plans/docs/`, create `copilot/plans/runs/<plan-id>/`, and initialize its lifecycle as active.
- Use `/workflow-start` to begin the explicit workflow loop for an existing active plan.
- Use `/workflow-resume` to continue an active workflow from saved state.
- Use `/workflow-status` to inspect current workflow state without running the full loop.
- Use `/status-init` and `/status-update` for durable workspace memory under `copilot/memory/`.
- Use `/summary-init` and `/summary-update` to refresh shared root `STATUS.md` and `FIX.md` from memory.

## Runtime Ownership

- `pro-plan` owns full plan drafting and repository grounding for new planned work.
- `build` owns mechanical plan persistence and project-local scaffold creation when invoked by commands.
- `orchestrator` owns the explicit workflow loop and leaf-agent session management.
- `workflow` owns phase selection, stage decisions, workflow summaries, and lifecycle changes in `PLAN_STATUS.md`.
- `implementation` and `pro-implementation` own code changes, validation, execution routing, local or Slurm execution, monitoring, and implementation summaries.
- `review` owns failure diagnosis, risky-change assessment, and unclear-result triage.
- `analysis` owns interpretation of meaningful outputs and decision-ready result summaries.
- `status` owns durable workspace memory under `copilot/memory/` and the derived root `STATUS.md` and `FIX.md` entrypoints.

## Core Rules

- Start workflow mode only when the user explicitly asks through a workflow command or direct instruction.
- Treat one active plan as one bounded experiment or study, not as a tiny coding subtask.
- Keep human decision points explicit, especially for scientific interpretation, external result locations, material plan changes, and marking a plan finished.
- Let `workflow` choose the next stage from plan evidence and summaries; do not infer stage transitions from leaf summaries alone.
- Let the plan or workflow summary select `implementation` or `pro-implementation` for each phase.
- Keep workflow-control artifacts, concise logs, Slurm scripts, command snapshots, and readiness-test outputs in `copilot/plans/runs/<plan-id>/` by default.
- Allow canonical scientific outputs outside the run directory only when the plan names the destination or the user approves it.
- Use `review` for execution failures, risky changes, and unclear runtime evidence.
- Use `analysis` for meaningful scientific, analytical, or operational interpretation before advancing phases or marking a plan finished.
- Use `status` only when memory or shared summaries should be refreshed; do not make it an automatic normal workflow stage.

## Shared Backend

- Plan documents live under `copilot/plans/docs/`.
- Plan run directories live under `copilot/plans/runs/` with the same Plan ID.
- Each run directory contains `PLAN_STATUS.md`; exactly `Status: active` or `Status: finished` is authoritative for lifecycle.
- Finishing or reopening a plan changes only `PLAN_STATUS.md`; plan documents and run directories never move for lifecycle changes.
- Run-only migrated families are historical evidence, not automatically executable plans.
- Plan IDs beginning with `claude-plans-` belong to the Claude workflow. OpenCode excludes them from start/resume discovery and may only report their ownership, stable paths, and lifecycle when explicitly selected for status.
- Durable project memory lives under `copilot/memory/` when initialized.
- Root `STATUS.md` and `FIX.md` are short shared entrypoints synthesized from memory.
- Existing summaries may retain legacy `Plan Sibling Directory`, `Path State`, `Suggested Workflow State: archive`, or `Next Stage: archive` fields. Read them for history, but use `PLAN_STATUS.md` for current lifecycle and write the new field names on substantive updates.
- When explicitly resuming migrated work with fresh sessions, preserve old session ledgers as history and hand off the current phase, bounded summaries, pending decisions, and resume condition to new sessions.

## Do Not

- Do not write a plan before the user approves it.
- Do not start execution-oriented workflow phases before a plan exists.
- Do not copy global agents, commands, skills, or workflow reference files into project-local scaffolds by default.
- Do not treat project-local scaffolding as approval to run experiments.
- Do not treat Slurm `COMPLETED` alone as scientific or workflow success.
