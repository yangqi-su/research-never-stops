# Plans Workflow

Use `plans/active/` for in-progress task steps and `plans/archive/` for completed ones.

The global workflow files under `workflow/` are reference material for maintaining agent prompts, not required runtime dependencies.

## Naming

- Active plan files should use `plans-<timestamp>-<slug>.md`.
- Each active plan file should have a sibling run directory with the same stem.
- Example:
  - `plans/active/plans-20260321-1530-train-baseline.md`
  - `plans/active/plans-20260321-1530-train-baseline/`

## Expected run-directory files

- `workflow-session.json`
- `implementation-summary.md`
- `review-summary.md`
- `workflow-summary.md`
- optional execution-side artifacts such as `execution.sbatch`

## Lifecycle

1. Start the workflow explicitly with `/workflow-start` or resume it with `/workflow-resume`.
2. Create a plan file in `plans/active/` using `plans/PLAN_TEMPLATE.md` as a starting point, or let `launch` create it.
3. Create or let `launch` create the sibling run directory.
4. Let `orchestrator` start `workflow` once for the plan and persist its `task_id` in `workflow-session.json`.
5. Let `orchestrator` invoke `implementation` and optional `review` one stage at a time.
6. After each stage, resume the same `workflow` session using the saved `task_id`.
7. Keep summaries and execution artifacts in the sibling run directory.
8. When the step is finished, move both the plan file and sibling run directory to `plans/archive/`.

## Workflow sidecar file

Use `workflow-session.json` in the sibling run directory to bind one persistent workflow sidecar session to one plan.

Recommended shape:

```json
{
  "plan_id": "plans-<timestamp>-<slug>",
  "workflow_task_id": "ses_...",
  "created_by": "orchestrator",
  "created_at": "YYYY-MM-DD HH:MM:SS"
}
```

If the saved `workflow_task_id` cannot be resumed, `orchestrator` should create a new workflow sidecar session and overwrite this file.

## Agent responsibilities

- `orchestrator` owns the explicit workflow loop and persists `workflow-session.json`.
- `launch` creates one concrete active step and initializes the run directory.
- `workflow` acts as a persistent sidecar for one plan, inspects the current state, writes `workflow-summary.md`, and recommends the next stage or archival decision.
- `implementation` changes code, decides `local` versus `slurm`, runs or submits the step when needed, monitors it, and writes `implementation-summary.md`.
- `review` writes `review-summary.md` only when deeper diagnosis is needed.
