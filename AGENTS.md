# Global Workflow Preferences

These are global OpenCode preferences for the custom workflow agents.

Use this workflow only when the user explicitly asks for plan-centered execution, stepwise orchestration, or Slurm-backed runs.
Preferred entrypoints are explicit workflow commands such as `/workflow-start`, `/workflow-resume`, and `/workflow-status`.
Treat `orchestrator` as the dedicated primary agent for this workflow.

## Plan lifecycle

- Active plan files live at `plans/active/plans-<timestamp>-<slug>.md` inside the current project.
- Each active plan file has a sibling run directory with the same stem, for example `plans/active/plans-<timestamp>-<slug>/`.
- Agent handoff files for that step live in the sibling run directory.
- When the step is finished, move both the plan file and the sibling run directory to `plans/archive/`.

## Agent roles

- `orchestrator` owns the explicit workflow loop, delegates stages, and persists `workflow-session.json`.
- `launch` creates one concrete active plan step and initializes `plans/` structure.
- `workflow` is a persistent sidecar for one plan step, updates `workflow-summary.md`, recommends the next stage, and archives finished plans.
- `implementation` owns code changes, lightweight validation, execution routing, actual local or Slurm execution, and monitoring, and writes `implementation-summary.md`.
- `review` is an optional escalation agent that reads the latest summaries, suggests fixes when needed, and writes `review-summary.md`.

## Invocation model

- Avoid subagent-to-subagent delegation for this workflow.
- `orchestrator` should own all delegation for this workflow.
- `launch`, `workflow`, `implementation`, and `review` should never invoke each other.
- `orchestrator` should start `workflow` once per plan and then resume that same `workflow` subagent session after each stage.
- Persist the workflow subagent `task_id` in a `workflow-session.json` inside the plan's sibling run directory.
- Treat plan files and summary files as the durable workflow state; treat sessions as disposable.
- Do not enter this workflow loop unless the user explicitly invoked it.

## Working style

- Prefer planning before editing.
- Keep changes small and reviewable.
- Preserve existing project conventions and unrelated user changes.
- Keep scope to one concrete plan step unless the user asks otherwise.

## Project memory

- `status` is the primary agent for maintaining `STATUS.md` and `FIX.md` as durable project memory.
- `status` should update project memory from fresh evidence on disk and should not act as an execution or orchestration agent.

## Safety

- Do not directly load large data, model artifacts, checkpoints, binaries, or large logs into context.
- Prefer lightweight metadata, configs, small scripts, and concise summaries.
- Keep `workflow` focused on planning and state decisions rather than execution details.
- Let `implementation` decide whether execution should be `local` or `slurm`.
- `implementation` should decide and record its execution route before launching any run.

## Slurm defaults

- Slurm submissions should include `#SBATCH --partition=ihc,all`.
- Slurm submissions should include `#SBATCH --account=ihc`.
- Add `#SBATCH --nodelist=ihc-h200-1` only when the run clearly requires a GPU.

## Execution routing

- `implementation` should choose `slurm` for any substantive experiment, sweep, batch, or multi-step job unless it is clearly tiny and short-lived.
- `implementation` should choose `slurm` when any relevant input file exceeds `1GB`.
- `implementation` should choose `slurm` when the job is highly parallelizable or can fan out safely across independent units of work.
- `implementation` should choose `slurm` for deep-learning or GPU-requiring work.
- `implementation` should choose `slurm` when expected runtime may exceed `30 minutes`.
- `implementation` should choose `slurm` whenever a local run would likely hit bash timeouts, require repeated manual reruns, or tempt parameter weakening.
- `implementation` should require at least `8` CPU cores for any substantive run, local or Slurm, unless technically impossible; if fewer are used, record the exception.
- `implementation` should prefer parallel execution when safe instead of serially looping through independent work.
- `implementation` should not silently reduce epochs, batch size, sample count, data volume, retries, or other experiment settings just to fit a local timeout.
- Otherwise `implementation` should prefer `local` execution only for genuinely small validation or inspection steps.
- If uncertain and the task may cross one of those thresholds, prefer `slurm`.

## Monitoring expectations

- When `implementation` launches a Slurm-backed step, it should continue monitoring until the job reaches `success`, `failed`, or `blocked` before finalizing `implementation-summary.md`.
- Treat `wait` as exceptional rather than the default Slurm behavior.
- If outputs or logs show no meaningful change for more than `20 minutes`, `implementation` should treat the run as `blocked` and record the evidence.
- If scripts do not emit enough progress information to support that check, `implementation` should add or request lightweight progress logging.
