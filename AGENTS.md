# Global Workflow Preferences

These are global OpenCode preferences for the custom workflow agents.

Use this workflow only when the user explicitly asks for plan-centered execution, stepwise orchestration, or Slurm-backed runs.
Preferred entrypoints are explicit workflow commands such as `/workflow-handoff`, `/workflow-start`, `/workflow-resume`, and `/workflow-status`.
Treat `orchestrator` as the dedicated primary agent for this workflow.

## Plan lifecycle

- Active plan files live at `plans/active/plans-<timestamp>-<slug>.md` inside the current project.
- Each active plan file has a sibling run directory with the same stem, for example `plans/active/plans-<timestamp>-<slug>/`.
- Agent handoff files for that step live in the sibling run directory.
- When the step is finished, move both the plan file and the sibling run directory to `plans/archive/`.

## Agent roles

- `orchestrator` owns the explicit workflow loop, delegates stages according to `workflow` decisions, and persists `workflow-session.json`.
- `launch` initializes one concrete active plan step, creates `plans/` structure, and preserves approved upstream context in `planning-handoff.md` with minimal paraphrase.
- `workflow` is a persistent sidecar and stage-decision authority for one plan step, updates `workflow-summary.md`, recommends the next stage, and archives finished plans.
- `implementation` owns code changes, lightweight validation, execution routing, actual local or Slurm execution, and monitoring, and writes `implementation-summary.md`.
- `review` is an optional escalation agent that reads the latest summaries, suggests fixes when needed, and writes `review-summary.md`.
- `analysis` interprets meaningful outputs from the current step and writes `analysis-summary.md` when the workflow needs a decision-ready interpretation before archival or the next step.
- `status` is a research-memory subagent that maintains canonical workspace memory under `memory/` and refreshes `STATUS.md` and `FIX.md` as compatibility entrypoints when a primary agent explicitly asks for a memory refresh.
- `think` is an exploratory research-framing subagent that helps `plan` or another primary agent refine ambiguous, multi-repo, or method-comparison-heavy work before launch.

## Invocation model

- Avoid subagent-to-subagent delegation for this workflow.
- `orchestrator` should own all delegation for this workflow.
- `launch`, `workflow`, `implementation`, `review`, and `analysis` should never invoke each other.
- `orchestrator` should start `workflow` once per plan and then resume that same `workflow` subagent session after each stage.
- Persist the workflow subagent `task_id` in a `workflow-session.json` inside the plan's sibling run directory.
- Treat plan files and summary files as the durable workflow state; treat sessions as disposable.
- Do not enter this workflow loop unless the user explicitly invoked it.
- `orchestrator` should treat `workflow-summary.md` as the authoritative next-stage contract and should not infer stage transitions directly from leaf summaries.

## Working style

- Prefer planning before editing.
- Keep changes small and reviewable.
- if the Glob tool fails to find something (most likely due to .gitignore settings), use ls and/or grep to try again
- Preserve existing project conventions and unrelated user changes.
- Keep scope to one concrete plan step unless the user asks otherwise.
- Treat one concrete plan step as one decision-bearing research unit. A good step can be a pilot run, one comparison experiment, one preprocessing validation pass, or one interpretation pass.

## Planning and handoff

- Built-in `plan` remains the normal intake surface.
- `plan` should selectively invoke `think` when a task is exploratory, ambiguous, multi-repo, method-comparison heavy, or lacks a clear next experiment.
- Skip `think` when the request is already concrete and execution-ready.
- Because built-in `plan` is discussion-first and may not persist files, treat built-in `build` as the authoritative pre-launch handoff layer when it shares the approved planning context with `launch`.
- Prefer `/workflow-handoff` when the user wants approved planning context preserved literally before the workflow loop starts.
- Treat `/workflow-handoff` as a primary-agent command that uses the approved context already present in the conversation and then delegates to `launch`.
- When `launch` receives approved upstream context from `build`, `orchestrator`, or the user, it should preserve that context in `planning-handoff.md` with minimal paraphrase and should not summarize or narrow broad context on its own.

## Project memory

- `status` is the dedicated subagent for maintaining canonical workspace memory under `memory/`.
- `status` should refresh memory from fresh evidence on disk and should not act as an execution, analysis, review, or orchestration agent.
- `status` should read both `plans/active/` and `plans/archive/`, starting from plan files and run-directory summaries before broader repo context.
- `status` should keep concise narrative memory for fast understanding, with lightweight drill-down pointers in markdown files and exact provenance primarily in `memory/index.json` and canonical plan/run-directory files.
- primary planning agents may read `memory/current.md` and `memory/summary.md` as concise workspace context before drilling into deeper evidence.
- `implementation` and `review` should primarily read relevant entries in `memory/watchouts.md` and `memory/fixes.md`, then follow pointers into `memory/plans/` when needed; only read canonical archived plan summaries if the memory plan page is insufficient.
- `analysis` may read `memory/current.md` and `memory/summary.md` when broader context is useful, and should normally reach archived history through a relevant `memory/plans/<plan-id>.md` page before reading original archived summaries.
- archived workflow history should normally be accessed through `memory/plans/<plan-id>.md` first, not by scanning `plans/archive/` directly.
- agents should not read all of `memory/` by default; memory access should stay selective and role-appropriate.
- root `STATUS.md` and `FIX.md` should remain as short compatibility entrypoints that point into `memory/`.
- explicit memory entrypoints should include `/status-init` and `/status-update`.
- Any primary agent may explicitly invoke `status` when a memory refresh is useful.

## Safety

- Do not directly load large data, model artifacts, checkpoints, binaries, or large logs into context.
- Prefer lightweight metadata, configs, small scripts, and concise summaries.
- Keep `workflow` focused on planning and state decisions rather than execution details.
- Keep `orchestrator` focused on delegation, session continuity, and user-facing state reporting rather than failure diagnosis or output interpretation.
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

## Output placement

- Keep workflow-control artifacts, Slurm scripts, concise logs, command snapshots, config snapshots, readiness-test outputs, and other implementation-side trace artifacts in the plan's sibling run directory by default.
- Allow large or canonical scientific outputs outside the run directory only when the plan explicitly names the destination or the user approves it.
- If a step needs an external canonical result location and none is specified, `implementation` should stop at `needs-user` instead of inventing one.
- When outputs are external, write `result-manifest.md` in the sibling run directory that points to the external locations and maps them back to the current plan step.

## Monitoring expectations

- When `implementation` launches a Slurm-backed step, it should continue monitoring until the job reaches `success`, `failed`, or `blocked` before finalizing `implementation-summary.md`.
- Treat `wait` as exceptional rather than the default Slurm behavior.
- If outputs or logs show no meaningful change for more than `20 minutes`, `implementation` should treat the run as `blocked` and record the evidence.
- If scripts do not emit enough progress information to support that check, `implementation` should add or request lightweight progress logging.
- `implementation` should distinguish queued jobs, healthy running jobs with heartbeat, running jobs without heartbeat, completed-but-unverified jobs, blocked jobs, and intentional waits.
- `implementation` should use `wait` only when the job is healthy, expected to keep running, and the resume condition is explicitly recorded.
