# Plans Workflow

Use `plans/active/` for in-progress experiment plans and `plans/archive/` for completed ones.

The global workflow files under `workflow/` are reference material for maintaining agent prompts, not required runtime dependencies. The canonical experiment-plan template now lives in `/draft-plan` and `/write-plan`, not in standalone template files.

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
- `analysis-summary.md` when meaningful outputs need interpretation
- `workflow-summary.md`
- optional execution-side artifacts such as `execution.sbatch`
- `result-manifest.md` when canonical results live outside the run directory

## Lifecycle

1. Use `/draft-plan` to draft or refine the full multi-phase experiment plan in conversation only.
2. Use `/write-plan` to write the approved plan to `plans/active/` and create the sibling run directory.
3. Start the workflow explicitly with `/workflow-start` or resume it later with `/workflow-resume`.
4. Let `orchestrator` start `workflow` once for the plan and persist its `task_id` in `workflow-session.json`.
5. Let `workflow` pick the current active phase and recommend the next stage.
6. Let `orchestrator` invoke fresh `implementation` rounds phase-by-phase, with optional `review` or `analysis` when needed.
7. After each leaf stage, resume the same `workflow` session using the saved `task_id`.
8. Keep summaries and execution artifacts in the sibling run directory.
9. When the full plan is finished, move both the plan file and sibling run directory to `plans/archive/`.

## Plan and phase definition

One active plan should be one bounded experiment or study.

Examples of valid phases inside one plan:

- one pilot experiment to validate configuration correctness
- one method-comparison batch on a fixed pilot split
- one preprocessing validation phase before full runs
- one interpretation phase over completed outputs

Avoid fragmenting these into tiny SWE-style subtasks when doing so would hide the real experimental decision. Let `workflow` manage phase progression inside the full plan.

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

- `orchestrator` owns the explicit workflow loop, persists `workflow-session.json`, and delegates stages according to `workflow-summary.md`.
- `/write-plan` is the mechanical plan-writing path that persists the approved full plan and initializes the run directory.
- `workflow` acts as a persistent sidecar and stage-decision authority for one plan, tracks the current phase, writes `workflow-summary.md`, and recommends the next stage or archival decision.
- `implementation` changes code, decides `local` versus `slurm`, runs or submits the current phase when needed, monitors it, and writes `implementation-summary.md`.
- `review` writes `review-summary.md` only when deeper diagnosis is needed.
- `analysis` writes `analysis-summary.md` when the current phase has meaningful outputs that need interpretation before the next phase or archival.
- `status` is a project-memory subagent that primary agents may invoke explicitly when workspace memory under `memory/` should be initialized or refreshed.

## Workspace memory

- canonical project memory should live under `memory/` in the project root
- `status` should read both `plans/active/` and `plans/archive/` when initializing or refreshing memory
- `status` should prefer plan files and sibling run-directory summaries as its primary evidence source
- `memory/plans/` should be the only per-plan drill-down memory layer
- plan pages should be concise historical summaries rather than path catalogs or stage-by-stage mirrors
- exact plan and run-directory provenance should live primarily in `memory/index.json` and the canonical plan/run-directory files
- agents should normally reach archived context through a relevant `memory/plans/<plan-id>.md` page before reading the original archived plan or run-directory summaries
- top-level memory such as `memory/current.md` and `memory/summary.md` should stay story-first and path-light
- root `STATUS.md` and `FIX.md` should stay short and point readers into `memory/`

## Output placement

- Keep workflow-control artifacts, concise logs, readiness-test outputs, command snapshots, config snapshots, and Slurm scripts in the sibling run directory by default.
- Allow large or canonical scientific outputs outside the run directory only when the plan explicitly names the destination or the user approves it.
- If true experiment outputs need an external canonical location and none is specified, `implementation` should stop at `needs-user` rather than inventing one.
- When outputs are external, record them in `result-manifest.md` in the sibling run directory.

## Historical note

Older archived examples in this directory may still mention `execution-summary.md` from an earlier split execution design or older single-step plans. The current workflow uses `implementation-summary.md` as the unified execution-routing and execution-state record and treats one active plan as a multi-phase experiment contract.
