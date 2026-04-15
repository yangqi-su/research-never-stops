---
name: using-copilot-workflow
description: Use when the user wants the separate Copilot-optimized workflow fork with question-driven clarification, isolated Copilot plans, and direct agent delegation.
compatibility: opencode
metadata:
  domain: workflow
  workflow: copilot-fork
---

# Using Copilot Workflow

Use this skill when the user wants to use the separate Copilot-optimized workflow fork instead of the stable root workflow.

## Announce

At the start, say:

- `I'm using the Copilot workflow fork for this task so I can keep the flow inside the Copilot-specific commands, agents, and questions.`

## When To Use

Use this skill when any of the following are true:

- the user explicitly asks for the Copilot workflow fork
- the user wants a question-driven intake loop with as much interaction as possible kept inside one session
- the user wants isolated Copilot plans, sessions, summaries, and memory
- the user wants the Copilot stack's model assignments rather than the stable root workflow stack

## Default Entry Point

- prefer `/copilot-autoflow` as the default human entrypoint for new work
- use `/copilot-draft-plan` only for planning-only work
- use `/copilot-write-plan` only to persist an already approved Copilot plan
- use `/copilot-workflow-start`, `/copilot-workflow-resume`, and `/copilot-workflow-status` only when there is already a written Copilot plan
- route those workflow commands into `copilot-orchestrator` rather than entering other Copilot agents directly
- use `/copilot-status-init` and `/copilot-status-update` as direct Copilot memory maintenance entrypoints to `copilot-status`
- use `/summary-init` and `/summary-update` when the shared root `STATUS.md` and `FIX.md` layer should be refreshed from both stacks

## Core Rules

- treat the Copilot stack as separate from the root workflow stack
- keep required behavior in Copilot commands, agents, and skills rather than non-runtime docs
- prefer direct agent delegation over internal command chaining
- prefer `question` over stopping whenever a focused user answer can unblock the next safe step
- ask one focused question at a time
- prefer multiple-choice questions when practical
- for new work, let `copilot-plan` own repository grounding and plan drafting
- preserve the exact canonical Copilot plan block returned by `copilot-plan` when collecting approval and when delegating to `copilot-write`
- use one plan-write approval per plan revision
- for plan approval, expose only `Approve and write` as an explicit option and rely on the default freeform answer path for requested changes or cancellation
- if the user requests plan changes, resume the same `copilot-plan` session when possible, revise the canonical block, and invalidate the prior approval for the old revision
- after approval of the current revision, delegate directly to `copilot-write` without a separate conversational menu or second approval
- when a healthy long-running phase reaches a justified `wait`, prefer asking the user through `question` whether to keep monitoring inside the current session before ending the loop
- do not treat `wait` as the default outcome of normal queued or running jobs
- require explicit approval before writing a plan
- require explicit approval before starting execution-oriented workflow phases
- if the plan changes materially, re-confirm approval before proceeding

## Isolation Rules

- Copilot plans live under `copilot/plans/active/` and `copilot/plans/archive/`
- Copilot memory lives under `copilot/memory/`
- shared root `STATUS.md` and `FIX.md` may be read as cross-stack summary entrypoints without treating root `memory/` as Copilot-owned
- Copilot workflow session files such as `workflow-session.json` and `agent-sessions.json` live only inside Copilot run directories
- do not read or write the root `plans/` or `memory/` trees broadly unless the user explicitly asks for cross-stack comparison or migration work

## Runtime Ownership

- `copilot-orchestrator` is the user-facing entry agent for Copilot workflow execution and owns intake, approvals, existing-plan resolution, and workflow dispatch
- `copilot-plan` is a subagent that owns new-work repository grounding and planning only
- `copilot-write` is a subagent that owns plan persistence only
- `copilot-workflow` is a subagent and the phase and stage authority for one Copilot plan
- `copilot-implementation` is a subagent that owns code changes, validation, execution routing, and monitoring
- `copilot-review` and `copilot-analysis` are subagents for exception and interpretation paths
- `copilot-status` is the Copilot memory maintenance agent for `copilot/memory/` and may be entered directly by the Copilot status commands
- `workflow-session.json` is the canonical resume contract for the persistent `copilot-workflow` sidecar
- `agent-sessions.json` is an advisory ledger for leaf-agent task ids and should not override `copilot-workflow` stage decisions

## Do Not

- do not treat `copilot/README.md`, `copilot/plans/README.md`, or any other reference doc as the only source of required behavior
- do not mix Copilot workflow state with the root workflow state
- do not write a plan before approval
- do not start execution-oriented workflow work before approval
- do not depend on slash-command chaining between agents when direct delegation will work
