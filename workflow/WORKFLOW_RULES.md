# Global Workflow Rules

These rules define the default behavior for the custom global workflow agents.

## When to use this workflow

- Use this workflow only when the user explicitly asks to start, resume, inspect, or continue the workflow.
- Preferred entrypoints are explicit planning and workflow commands such as `/draft-plan`, `/write-plan`, `/workflow-start`, `/workflow-resume`, and `/workflow-status`.
- Treat `orchestrator` as the dedicated primary agent for this workflow.
- Do not force the workflow for simple one-off tasks that do not benefit from plans or run directories.
- Use `/draft-plan` to draft the full experiment plan in conversation and `/write-plan` to persist that approved plan before orchestration begins. Use `workflow` when there is already an active plan to inspect or advance.

## Project structure expectations

- The canonical shared backend should contain `copilot/plans/active/` and `copilot/plans/archive/`.
- One full experiment plan should live in `copilot/plans/active/<plan-id>.md`.
- That plan file should have a sibling run directory with the same stem.
- Exact plan and summary formats live in the relevant command and agent prompts.
- Files in `workflow/` are reference material for maintaining those prompts, not a required runtime dependency.

## Invocation model

- Do not use subagent-to-subagent delegation for this workflow.
- `orchestrator` should invoke `workflow`, `implementation`, `review`, and `analysis` directly.
- `workflow`, `implementation`, `review`, and `analysis` should not invoke each other.
- For each active plan, `orchestrator` should start exactly one `workflow` subagent session and then resume it by `task_id` after each stage.
- Persist each workflow family's per-plan `task_id` in its own session file inside the sibling run directory.
- Treat plan files and summary files as the workflow state machine.
- Make every stage restart-safe and able to resume from existing files.
- Do not start the loop merely because an active plan exists; start it only from an explicit user request to the workflow system.

## Agent boundaries

- `orchestrator` owns the explicit workflow loop and stops only at terminal states such as `archive`, `wait`, `blocked`, or `needs-user`.
- `orchestrator` is the dispatcher and session owner, not a second workflow-policy engine; it should route work according to `workflow-summary.md` rather than inferring stage transitions from leaf summaries.
- `/write-plan` creates the plan file and sibling run directory from the approved full plan already present in conversation.
- `workflow` inspects one full plan, tracks the current phase, updates `workflow-summary.md`, resolves ambiguous or stale leaf-state evidence, and manages archival decisions as the persistent per-plan decision sidecar.
- `implementation` changes code, writes `implementation-summary.md`, decides whether execution should be `local` or `slurm`, runs or submits the current phase when needed, and monitors the resulting process or job.
- `review` reads summaries, diagnoses problems, suggests fixes, and writes `review-summary.md` only when escalation is needed.
- `analysis` reads the latest plan and phase evidence, interprets meaningful outputs, and writes `analysis-summary.md` when the current phase needs a decision-ready interpretation before the next phase or archival.
- `status` is outside the normal command-driven workflow loop and should only be invoked explicitly by a primary agent for project-memory initialization or refreshes.
- `summary-link` is outside the normal command-driven workflow loop and should only be invoked explicitly to refresh shared root `STATUS.md` and `FIX.md` from stack-local memory.

## Plan and phase granularity

- Treat one active plan as one bounded experiment or study rather than one tiny coding task.
- A valid plan may contain multiple large phases such as a pilot run, one comparison batch, one preprocessing validation phase, or one interpretation phase.
- Let `workflow` advance from one phase to the next instead of forcing the plan writer to pre-narrow the workflow to an early substep.

## Execution routing

> All execution routing, monitoring, heartbeat, and Slurm-specific rules now live in the `execution-selection`, `submitting-slurm-cpu-jobs`, and `submitting-slurm-gpu-jobs` skills. Agents are instructed to load and follow those skills rather than rely on this file.

- Agents should load `execution-selection` before launching execution and follow the appropriate Slurm skill when `slurm` is chosen.

## Output placement

- Keep workflow-control artifacts, concise logs, Slurm scripts, command snapshots, config snapshots, and readiness-test outputs in the plan's sibling run directory by default.
- Allow large or canonical scientific outputs outside the run directory only when the plan explicitly names the destination or the user approves it.
- If no external result destination has been specified for true experiment outputs in the current phase, `implementation` should stop at `needs-user` instead of inventing one.
- When outputs are external, `implementation` should write `result-manifest.md` in the sibling run directory.

## Archival behavior

- Archive only when the full plan is genuinely complete.
- When archiving, ensure summary headers and the workflow summary point at the final archived plan and run-directory paths.
- If the plan is blocked or incomplete, leave it in `copilot/plans/active/` and explain why.

## Slurm defaults

- Include `#SBATCH --partition=ihc,all`.
- Include `#SBATCH --account=ihc`.
- Include `#SBATCH --nodelist=ihc-h200-1` only when the run clearly requires a GPU.
