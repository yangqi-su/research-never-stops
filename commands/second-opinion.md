---
description: Ask Claude Code's read-only Opus agent about plans, phases, files, outputs, or a general project question
agent: build
---

Run `/second-opinion <question> [plan=<id>] [phases=3|2-4|all] [type=bug|implementation|results|plan|general] [files=...] [effort=low|medium|high|xhigh|max] [keep]` with these arguments: $ARGUMENTS

Work from the project root containing `copilot/`. This is an advisory check, not a workflow stage. Do not act on the findings or edit plan documents, Progress Logs, memory, or other agents' summaries. The report is the record.

1. Resolve the question and scope from the arguments and what the current conversation clearly identifies. Ask only if the question itself is unclear. A scope can be one phase, a phase range, a whole plan, named files/outputs, or a general project question; plan and file scopes can be combined. Infer the question type when omitted. When a plan is supplied without phases, default to `all`; without a plan, do not invent one. Resolve its document at `copilot/plans/docs/<Plan ID>.md` and run directory at `copilot/plans/runs/<Plan ID>/`, with plan type Claude for `claude-plans-*`, otherwise OpenCode. Include phase numbers/names from the document when available, and state unresolved evidence in the prompt rather than guessing or broadening scope. Treat a trailing `keep` as a request to retain the Claude session.

   Resolve effort from `effort=` when supplied (`low`, `medium`, `high`, `xhigh`, or `max`); otherwise use `high`. Use that same resolved value in the report header and Claude invocation for this call only.

2. Create `copilot/plans/runs/<Plan ID>/second-opinion/` when a plan is involved, otherwise `copilot/second-opinion/`. Set `TS=$(date +%Y%m%d-%H%M)` and `STEM=<TS>-claude-<scope>-<type>`. Use `phase-03`, `phases-02-04`, or `whole-plan` for plan scopes; otherwise use a lowercase, hyphen-separated 2–4 word slug of the question. If any of the three target files already exists, stop rather than overwrite or append another review to it. Write `<STEM>.md` with these four header lines and a blank line:

   ```md
   - `Checker`: Claude Code `second-opinion` agent, model `opus`, effort `<effort>`
   - `Session`: none (not saved)
   - `Scope`: <plan + phases, files, or general; include both plan and files when specified>
   - `Question`: <type> — <question>
   ```

   With `keep`, generate a UUID with `uuidgen` and use that UUID as the `Session` value. Write `<STEM>.prompt.txt` with this prompt, filling in the resolved scope and paths:

   ```text
   This is a second-opinion request from OpenCode. Nobody is watching: do not ask questions.
   Scope: <one phase | phases N-M | the whole plan | these files | general question about this project>
   Plan: <plan document path> (<Claude plan | OpenCode plan>) — or "none"
   Run directory: <run directory> — or "none"
   Phases: <list> — or "all" / "none"
   Files or outputs to focus on: <paths> — or "none"
   Question type: <type>
   Question: <question>
   Context from the caller: <2-5 lines: what was done, what is in doubt>
   Stay read-only and within the scope; you may read the web if it helps. Reply with the Verdict / Evidence / Problems or alternative explanations / Suggested next steps / Confidence structure (Verdict may be "n/a (open question)").
   ```

3. Run the command below after assigning `PROJECT_ROOT`, `DIR`, and `STEM` to the resolved values. Keep the prompt immediately after `-p`: the tool-list flags can otherwise consume it. Quote all paths. Give the shell tool a timeout longer than 1,200 seconds (for example 1,260,000 ms), or run it in the background and wait for its completion notification. A review may take 1–20 minutes; whole-plan reviews take longer. Do not use permission bypass flags or retry automatically.

   ```bash
   cd "$PROJECT_ROOT" && timeout 1200 claude -p "$(cat "$DIR/$STEM.prompt.txt")" \
     --agent second-opinion --model opus --effort high --no-session-persistence --permission-mode dontAsk \
     --allowedTools "Read" "Grep" "Glob" "WebFetch" "WebSearch" "Bash(git diff:*)" "Bash(git log:*)" "Bash(git show:*)" "Bash(git status:*)" \
       "Bash(ls:*)" "Bash(rg:*)" "Bash(head:*)" "Bash(tail:*)" "Bash(wc:*)" "Bash(squeue:*)" "Bash(sacct:*)" \
     --disallowedTools "Edit" "Write" "Bash(claude:*)" "Bash(opencode:*)" \
     < /dev/null >> "$DIR/$STEM.md" 2> "$DIR/$STEM.log"
   ```

   If `effort=` was supplied, replace `high` after `--effort` with the resolved value recorded in the header. With `keep`, replace `--no-session-persistence` with `--session-id "$SESSION_ID"`, using the UUID already recorded in the header. The user can later resume it with `claude --resume <id>`. Capture the exit code immediately; do not let a later command replace it.

4. If the exit code is nonzero or the report body after the header is empty, show the user the end of `<STEM>.log` and stop. On timeout, tell the user and suggest narrowing the scope. Preserve the report, prompt, and log for diagnosis; do not retry. Otherwise delete only `<STEM>.prompt.txt` and `<STEM>.log`. Read the report and flag missing response fields rather than claiming a complete check.

5. Show the verdict, main findings, and report path, followed by your own view: where you agree or disagree and why. Leave decisions and follow-up changes to the user.
