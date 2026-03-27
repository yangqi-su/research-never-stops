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

- `planning-handoff.md` when upstream planning context was provided
- `workflow-session.json`
- `implementation-summary.md`
- `review-summary.md`
- `analysis-summary.md` when meaningful outputs need interpretation
- `workflow-summary.md`
- optional execution-side artifacts such as `execution.sbatch`
- `result-manifest.md` when canonical results live outside the run directory

## Lifecycle

1. Start the workflow explicitly with `/workflow-start` or resume it with `/workflow-resume`.
2. Create a plan file in `plans/active/` using `plans/PLAN_TEMPLATE.md` as a starting point, or let `launch` create it.
3. Create or let `launch` create the sibling run directory.
4. Let `orchestrator` start `workflow` once for the plan and persist its `task_id` in `workflow-session.json`.
5. Let `orchestrator` invoke `implementation` and optional `review` or `analysis` one stage at a time.
6. After each stage, resume the same `workflow` session using the saved `task_id`.
7. Keep summaries and execution artifacts in the sibling run directory.
8. When the step is finished, move both the plan file and sibling run directory to `plans/archive/`.

## Step definition

One concrete step should be one decision-bearing research unit.

Examples:

- one pilot experiment to validate configuration correctness
- one method comparison on a fixed pilot split
- one preprocessing validation pass before full runs
- one interpretation pass over completed outputs

Avoid fragmenting these into tiny SWE-style subtasks when doing so would hide the actual decision the user needs.

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
- `launch` creates one concrete active step, initializes the run directory, and preserves upstream approved planning context in `planning-handoff.md` when it exists.
- `workflow` acts as a persistent sidecar for one plan, inspects the current state, writes `workflow-summary.md`, and recommends the next stage or archival decision.
- `implementation` changes code, decides `local` versus `slurm`, runs or submits the step when needed, monitors it, and writes `implementation-summary.md`.
- `review` writes `review-summary.md` only when deeper diagnosis is needed.
- `analysis` writes `analysis-summary.md` when the step has meaningful outputs that need interpretation before archival or the next decision.
- `status` is a project-memory subagent that primary agents may invoke explicitly when `STATUS.md` or `FIX.md` should be refreshed.

## Output placement

- Keep workflow-control artifacts, concise logs, readiness-test outputs, command snapshots, config snapshots, and Slurm scripts in the sibling run directory by default.
- Allow large or canonical scientific outputs outside the run directory only when the plan explicitly names the destination or the user approves it.
- If true experiment outputs need an external canonical location and none is specified, `implementation` should stop at `needs-user` rather than inventing one.
- When outputs are external, record them in `result-manifest.md` in the sibling run directory.

## Historical note

Older archived examples in this directory may still mention `execution-summary.md` from an earlier split execution design. The current workflow uses `implementation-summary.md` as the unified execution-routing and execution-state record.
