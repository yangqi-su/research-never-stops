---
name: migrating-plan-layout
description: Use when migrating existing copilot or legacy plans out of active/archive or plans/legacy-by-family folders into stable copilot/plans paths with per-plan PLAN_STATUS.md, including discovery beneath a parent directory and updating embedded path references.
---

# Migrate plans to stable locations

Use the bundled `scripts/migrate_plans.py` with Python 3. Work one project at a time. Separate plan documents from run directories while preserving the depth of sources under `copilot/plans/{active,archive}`:

```text
copilot/plans/docs/<plan-id>.md
copilot/plans/runs/<plan-id>/PLAN_STATUS.md
```

The status file contains exactly `Status: active` or `Status: finished`, followed by a newline. Folder location supplies the initial status: active → active, archive → finished. Finishing and reopening must subsequently change status rather than move files.

Families directly beneath `plans/legacy-by-family/` are also discovered and migrated without a preliminary move into active/archive. That container conveys no lifecycle status: ask the user and supply `--legacy-status active` or `--legacy-status finished` when auditing. The choice is stored in the report and reused by apply/verify. Without it, the audit reports a blocker instead of guessing. Conflicting existing statuses and duplicate family/plan IDs also block migration. The container's top-level `README.md` and `family-index.tsv` remain overview/index files at their current paths; their embedded references are scanned and updated during apply, with original content backed up if changed. They are not plans and receive no lifecycle status. Each family directory moves intact to `runs/`, including its nested Markdown documents. Other standalone top-level `.md` files go to `docs/`.

## Before migration

Ask for the parent directory and permission to inspect it when outside the current workspace. Discover first; finding a project is not approval to change it. Resolve the script location from this skill's directory; commands below abbreviate it as `$SCRIPT`.

```bash
python "$SCRIPT" discover --parent /approved/parent
```

Discovery includes ignored and hidden directories, skips `.git`, `.plan-migration`, Python caches and `node_modules`, and does not follow symlinks. Its JSON output lists projects and skipped links. A project is identified by one of the five supported old directory layouts, not by the presence of Git.

Before applying changes, ensure the workflow instructions have been updated for the new layout. This tool does not change OpenCode configuration. Creation, active-plan selection, completion/reopening, workflow permissions, memory status conventions, and summaries must use the new paths and status authority. Restart OpenCode after those configuration changes. Do not resume an old workflow session with stale instructions.

## Audit and approve one project

Run from the approved project. Audit writes only its report, under the reserved `.plan-migration/` directory; plan files remain untouched.

```bash
python "$SCRIPT" audit --project .
# If legacy families are present, use the user-approved initial status:
python "$SCRIPT" audit --project . --legacy-status finished
```

The audit CLI prints stage messages and approximately once-per-minute file-scan progress to stderr (entry count, bytes read, elapsed time, and current file). Stdout remains the JSON result. Progress is emitted between files, so a single slow read or the initial discovery traversal can delay the next message. These log messages are separate from the deterministic audit report. Replacement recognizes the old-layout prefix before looking up the discovered plan entry; files without a supported old prefix skip replacement searching.

For a known alternate spelling of this project's absolute root, add `--alias /alternate/project/root` (repeatable). Never guess aliases or supply a parent directory as an alias.

Read `.plan-migration/audit.json`. Present destinations, initial lifecycle status, edit counts, blockers, and review items. Stop on collisions; do not merge plans or invent names. Review archived-but-incomplete plans and contradictory status evidence with the user. Correct the source status/layout explicitly and re-audit if necessary.

The script recognizes paired markdown/run directories as well as markdown-only or independent directory-only plans. Other top-level objects block migration. In UTF-8 text (including logs and notebooks), it routes discovered top-level Markdown files to `copilot/plans/docs/` and discovered run directories to `copilot/plans/runs/`, preserving suffixes within run directories. Each discovered entry is recognized under all five former layout prefixes, regardless of its current location. Project-relative paths and absolute paths under the project root or explicit aliases are supported. Replacements do not match inside another project's absolute paths or `../` paths. Bare container references and unknown plan entries remain review items because their destinations are not established by the inventory.

Known plan paths also support the observed project-root prefixes `${REPO_ROOT}/`, `$REPO_ROOT/`, `${PROJECT_ROOT}/`, `$PROJECT_ROOT/`, and `{repo_root}/`. Confirm these variables denote this project before approving their edits; the scanner does not evaluate variable assignments. Arbitrary variables such as `${OTHER_ROOT}` are not recognized. The following explicitly run-oriented assembled expressions are rewritten to `copilot/plans/runs`:

- R assignments `run_dir <- file.path(repo_root, "<old-layout>", plan_id)` (also `=` and single quotes).
- Templates `{repo_root}/<old-layout>/{plan_id}` and paths beneath that directory, but not `{plan_id}.md`.

These narrow rules do not blanket-replace ambiguous container strings, Markdown globs such as `plans/archive/*.md`, historical prose, or dynamic document expressions. Review those by meaning: documents belong in `docs/`, run contents in `runs/`, and lifecycle transitions change status rather than move files. Relative-path findings remain review-only.

Simple relative Markdown links and reference definitions are checked against the proposed destinations. Changed links receive a suggested relative target (for example, a document link `p/output.txt` becomes `../runs/p/output.txt`); these suggestions are not automatically applied. Complex Markdown and embedded HTML still need review. Parent depth stays the same for the `copilot/plans/active` and `copilot/plans/archive` layouts, but root `plans/active`, `plans/archive`, and `plans/legacy-by-family` sources gain one directory level.

Relative paths are reviewed rather than automatically rewritten. For direct Python `Path(__file__)` chains using `.parent` or literal `.parents[n]` (optionally `.resolve()` or `.absolute()`), the audit compares lexical targets before and after relocation and reports changed targets with line numbers and the intended relocated target. Unchanged internal chains and ordinary `target.parent.mkdir()` operations are not flagged. Other `../`, `.parents[...]`, `chdir`, and `dirname` patterns retain line-level review items. Aliased variables, dynamic expressions, imports of Path under another name, notebook code, and working-directory assumptions still need manual inspection; this is not a general Python evaluator. Symlink entries include before/after/expected target comparisons, but targets are neither followed nor rewritten. Confirm intermediate symlinks separately because comparisons are lexical.

The scan reports unsupported/binary files, files over 16 MiB, symlinks, hardlinks that would be rewritten, nested projects, and residual old-layout strings. Inspect these without loading large artifacts into conversation. Do not claim that a clean text scan proves every executable path is correct. Old audits must be regenerated after changing the script's replacement or review rules.

Files in nested projects are excluded from this project's edits. Cross-project references and aliases need coordinated review; do not broaden replacement rules to catch them automatically. Project memory indexes and summaries receive path-string changes only: reconcile their lifecycle fields separately from `PLAN_STATUS.md`. Never globally replace the word `archived` with `finished`.

Approve the exact audit after resolving or explicitly accounting for review items. Pause jobs and agents that use the affected paths. The script re-audits before applying and refuses a changed input snapshot.

For large projects, the user may explicitly choose the saved-audit route below instead of repeating the full scan. This is an alternative to the default re-audit requirement; it does not waive review of the proposed changes.

Sockets inside moved plan trees are listed separately in `socket_deletions`, with path, device, and inode, rather than as hard blockers. Classification uses `lstat` and the filesystem socket type, never a filename pattern. Audit never deletes them. Socket type does not establish inactivity: confirm the originating jobs/processes are stopped before authorizing deletion. Sockets outside the moved trees and other special objects (FIFOs/devices) remain hard blockers. Symlink targets are not followed for cleanup.

## Apply and verify

```bash
python "$SCRIPT" apply --project .
python "$SCRIPT" verify --project .
```

### Applying a saved audit without another full-project scan

If the audit captured its own growing progress log, preserve that log with `--exclude-rewrite logs/<exact-audit-log-name>.err` on the saved-audit apply command. This repeatable option accepts exact project-relative paths already in the audit's edit list, not globs. It skips rewriting and hash validation only for those files, records their original edit entries in `excluded_rewrites` in the backup audit, and adds explicit review findings. The original audit is unchanged. Do not exclude a changed source/configuration file merely to make application proceed; inspect its change first. For future audits, place audit stdout/stderr under `.plan-migration/` (which the scanner excludes) to avoid scanning its own output.

With the user's approval, use:

```bash
python "$SCRIPT" apply --project . --use-saved-audit
# If the audit blocked on an empty placeholder that has since been removed:
python "$SCRIPT" apply --project . --use-saved-audit \
  --acknowledge-removed-empty plans/archive/.gitkeep
```

Do not edit `audit.json` to remove blockers. The repeatable `--acknowledge-removed-empty` option accepts only project-relative entries recorded as empty regular files with the empty-content hash, blocked as unsupported plan entries, and now absent. Other blockers still stop application. The original audit stays unchanged. The effective audit in `backup/audit.json` records the acknowledged removals and the `saved-audit-targeted` validation scope for recovery and subsequent verification.

Saved-audit mode rechecks the immediate plan inventory, destination collisions, and lifecycle statuses without directory discovery or a full content scan. Before creating a backup or moving anything, it verifies every proposed rewrite against both the saved input hash and the saved output hash; changed replacement rules or changed rewrite inputs stop the operation. Linked paths and hardlinked rewrite files are rejected. Input and output hashes are checked again immediately before each rewrite. Stop affected jobs and agents throughout, as with the default route. Socket deletion still requires `--delete-sockets` and the original socket checks.

Verification for a saved-audit application checks moves, rewritten-file hashes, lifecycle statuses, acknowledged removals, and approved socket deletions. It uses the recorded scope automatically, including when running `verify` separately. It does **not** rescan unrelated content, hash unchanged artifacts, discover new nested projects, or detect newly added references. Its review list is the original audit's findings, not a fresh scan. New/changed contents within unchanged run subdirectories are not inventoried. Report these coverage limits explicitly; targeted mechanical success does not resolve outstanding review items. A later full `audit` can assess residual references when desired. The default apply/verify route retains full-project checks.

If the approved audit contains socket deletion candidates, use `apply --project . --delete-sockets`. Without that explicit option, apply stops before backup or mutation. With it, apply rechecks each audited socket's type, device/inode, and linked ancestors immediately before unlinking that exact object. This is not an automatic check for running processes. Deleted sockets are not backed up or recreated.

Apply first creates `.plan-migration/backup/`, containing the approved audit and original bytes only for files whose contents will be rewritten (including existing status files if their contents would change). Unmodified plan documents, matrices, checkpoints, and run trees are not copied. Their recovery is by reversing the saved moves. A pre-existing backup blocks another apply, to preserve recovery evidence. Verify checks the saved moves, status files, expected rewritten-file hashes, and absence of approved deleted sockets; it also scans for residual old-layout strings. Review items remain explicit in the output even when the mechanical checks pass.

If apply fails partway, stop. Use the backup audit to identify completed moves, reverse those moves deliberately, and restore backed-up content to the original paths. Remove newly created status files only when the audit snapshot confirms they did not exist before migration; retain pre-existing ones. Markdown-only plans may have newly created run directories for their status files. Do not blindly rerun apply or overlay the backup onto a running project. This is migration recovery, not a full data backup. The script is not an atomic filesystem transaction and has no automatic rollback. Preserve `.plan-migration/` until the migrated project has been checked successfully.

Check representative commands/configs and manually handled relative paths. Rebuild derived memory/status views using the updated workflow. Audit again: an already migrated project should propose no moves or edits. Pilot one representative project before the rest.

## Coordination

Default to sequential migration. For many projects, the main agent may delegate one approved project to an existing general-purpose agent, giving it this skill, the approved audit, and the unresolved review items. Do not delegate independent writes per plan: plans share references and memory files. Parallel read-only audits are useful; parallel writes require disjoint project trees and no shared writable targets.

Report the projects scanned/migrated, plan and edited-file counts, backup locations, verification results, remaining exceptions, and workflow-configuration readiness. Do not describe a migration as complete while relevant exceptions remain unresolved.
