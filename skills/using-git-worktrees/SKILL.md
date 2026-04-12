---
name: using-git-worktrees
description: Create isolated git worktrees for package or model comparisons with code-level changes, using project-local AGENTS guidance first and `.worktrees/` by default.
compatibility: opencode
metadata:
  domain: engineering
  workflow: isolation-and-comparison
---

# Using Git Worktrees

Use this skill when code-level package or model changes should be isolated from the current workspace, especially for baseline-vs-variant comparisons or other implementation work where the user explicitly wants worktrees.

## Announce

At the start, say:

- `I'm using the using-git-worktrees skill to set up an isolated workspace.`

## When To Use

Use this skill when any of the following are true:

- the user explicitly asks to use worktrees
- a package change or model comparison requires code-level divergence rather than only hyper-parameter changes
- you want to compare multiple implementation variants without disturbing the current workspace
- risky or parallel feature work should stay isolated from the main checkout

## Core Principles

- consider that most of the times the worktree is for a particular repo under the current project root and not a worktree of the project itself
- preserve the current workspace
- keep the worktree location project-specific
- give top priority to guidance in the project's root `AGENTS.md`
- if root `AGENTS.md` does not specify a worktree location or policy, default to `<project-root>/.worktrees/`
- for code-level comparisons, use one worktree per meaningful branch or variant when that materially helps evaluation
- keep branch names descriptive and comparison-oriented
- do not auto-commit, auto-push, or auto-edit git config
- for project-local worktree directories, verify ignore safety before creating a worktree there
- if project-local ignore safety is not already in place, ask before editing `.gitignore`

## Repository Guidance Priority

Choose the worktree parent directory in this order:

1. explicit worktree preference or policy in the project's root `AGENTS.md`
2. `<project-root>/.worktrees/`

Do not fall back to a global shared worktree directory for this skill.

If `AGENTS.md` mentions worktrees but does not name a directory, still use `<project-root>/.worktrees/`.

## Safety Verification

For a project-local worktree directory such as `.worktrees/`, verify the directory is ignored before creating a worktree.

Use git-aware ignore checks rather than assumptions.

If the directory is not ignored:

- do not proceed silently
- ask before editing `.gitignore`
- never create a commit unless the user explicitly asks for one

Why this matters:

- unignored project-local worktrees can pollute repository status and create accidental tracking problems

## Branch And Path Naming

Use descriptive branch names tied to the comparison goal.

Examples:

- `compare/baseline-vs-new-loss`
- `compare/perttf-vs-variant-attn`
- `feature/package-api-refactor`

For multiple comparison worktrees, prefer names that make the role obvious, such as:

- `compare/<topic>-baseline`
- `compare/<topic>-variant`
- `compare/<topic>-ablation`

Default worktree path shape:

- `<project-root>/.worktrees/<branch-name>`

If `AGENTS.md` specifies a different project-local pattern, follow that pattern.

## Creation Flow

1. Identify repository root and project name.
2. Read the project's root `AGENTS.md` for worktree guidance.
3. If no explicit worktree location is specified there, use `<project-root>/.worktrees/`.
4. Verify ignore safety for the chosen project-local directory.
5. Create one or more worktrees with non-interactive git commands.
6. Run project setup using the repository's existing package or build tool.
7. Run the smallest meaningful baseline validation.
8. Report exact locations, branch names, and validation status.

## Project Setup

Auto-detect setup from repository files and existing conventions.

Examples:

- `package.json`: use the repo's Node package manager
- `pyproject.toml`: use the repo's established Python tool if clear
- `requirements.txt`: install Python requirements if that is the project convention
- `Cargo.toml`: build or fetch Rust dependencies
- `go.mod`: download Go dependencies

Do not invent a new package manager or environment flow when the repository already implies one.

## Baseline Validation

Always verify that the worktree starts from a usable baseline before implementation.

For normal software packages:

- run the standard fast test command if it exists and is reasonably scoped

For ML or model-comparison repositories:

- prefer the smallest meaningful validation that proves the environment and code path are usable
- examples: import check, CLI help, tiny smoke test, tiny canary, config validation, or a short project-standard sanity command
- do not default to a full training run as baseline verification

If baseline validation fails:

- report the failure clearly
- distinguish pre-existing failure from worktree-creation issues if possible
- ask whether to proceed anyway or investigate first

## Comparison-Specific Guidance

When comparing package or model variants with code-level differences:

- keep each meaningful implementation line on its own branch or worktree when practical
- keep outputs and result locations clearly separated
- avoid mixing comparison artifacts between branches
- prefer explicit naming for baseline and variant branches
- if the current workspace already serves as a valid baseline reference, only create the additional comparison worktree or worktrees actually needed

## Report Back

When the worktree setup is done, report:

- worktree path or paths
- branch name or names
- chosen parent directory
- setup command or commands run
- baseline validation command or commands run
- whether baseline passed, failed, or was only partially validated
- that the workspace is ready for the requested implementation or comparison

## Red Flags

Never:

- create a project-local worktree without verifying ignore safety
- auto-commit `.gitignore` changes without explicit user approval
- proceed past a clearly failing baseline without telling the user
- ignore a project-local `AGENTS.md` worktree preference
- browse unrelated repo files just to decide the worktree location

Always:

- read root `AGENTS.md` before choosing the worktree location
- default to `<project-root>/.worktrees/` when `AGENTS.md` is silent
- use non-interactive git commands
- validate the worktree with the smallest meaningful baseline
- keep the current workspace untouched

## Typical Outcomes

### Single isolated implementation branch

Use one worktree when the user wants isolated package or feature work.

### Baseline-vs-variant comparison

Use two worktrees when the user wants side-by-side code-level comparison between model or package variants and separate branches materially improve clarity.

### Multi-variant comparison

Use multiple worktrees only when the user explicitly wants several code-level variants or the comparison would otherwise become confusing in a single branch.
