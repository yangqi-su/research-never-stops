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
- Use `/write-plan` to persist an approved full plan under `copilot/plans/active/` and create its sibling run directory.
- Use `/workflow-start` to begin the explicit workflow loop for an existing active plan.
- Use `/workflow-resume` to continue an active workflow from saved state.
- Use `/workflow-status` to inspect current workflow state without running the full loop.
- Use `/status-init` and `/status-update` for durable workspace memory under `copilot/memory/`.
- Use `/summary-init` and `/summary-update` to refresh shared root `STATUS.md` and `FIX.md` from memory.

## Runtime Ownership

- `pro-plan` owns full plan drafting and repository grounding for new planned work.
- `build` owns mechanical plan persistence and project-local scaffold creation when invoked by commands.
- `orchestrator` owns the explicit workflow loop and leaf-agent session management.
- `workflow` owns phase selection, stage decisions, workflow summaries, and archival recommendations.
- `implementation` and `pro-implementation` own code changes, validation, execution routing, local or Slurm execution, monitoring, and implementation summaries.
- `review` owns failure diagnosis, risky-change assessment, and unclear-result triage.
- `analysis` owns interpretation of meaningful outputs and decision-ready result summaries.
- `status` owns durable workspace memory under `copilot/memory/`.
- `summary-link` owns shared root `STATUS.md` and `FIX.md`.

## Core Rules

- Start workflow mode only when the user explicitly asks through a workflow command or direct instruction.
- Treat one active plan as one bounded experiment or study, not as a tiny coding subtask.
- Keep human decision points explicit, especially for scientific interpretation, external result locations, material plan changes, and final archival.
- Let `workflow` choose the next stage from plan evidence and summaries; do not infer stage transitions from leaf summaries alone.
- Let the plan or workflow summary select `implementation` or `pro-implementation` for each phase.
- Keep workflow-control artifacts, concise logs, Slurm scripts, command snapshots, and readiness-test outputs in the plan sibling directory by default.
- Allow canonical scientific outputs outside the run directory only when the plan names the destination or the user approves it.
- Use `review` for execution failures, risky changes, and unclear runtime evidence.
- Use `analysis` for meaningful scientific, analytical, or operational interpretation before advancing phases or archiving.
- Use `status` and `summary-link` only when memory or shared summaries should be refreshed; do not make them automatic normal workflow stages.

## Shared Backend

- Active plans live under `copilot/plans/active/`.
- Archived plans live under `copilot/plans/archive/`.
- Each plan file should have a sibling run directory with the same stem.
- Durable project memory lives under `copilot/memory/` when initialized.
- Root `STATUS.md` and `FIX.md` are short shared entrypoints synthesized from memory.

## Do Not

- Do not write a plan before the user approves it.
- Do not start execution-oriented workflow phases before a plan exists.
- Do not copy global agents, commands, skills, or workflow reference files into project-local scaffolds by default.
- Do not treat project-local scaffolding as approval to run experiments.
- Do not treat Slurm `COMPLETED` alone as scientific or workflow success.
