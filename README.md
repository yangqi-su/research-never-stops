# OpenCode harness config

This repo is `~/.config/opencode`. It is one half of a two-harness research setup. The other half is the Claude Code config in `~/.claude` (private repo `yangqi-su/claude-harness`). How the two interact (shared project folders, second opinions in both directions, duplicated skills) is described in `~/.claude/README.md`.

Use branch `main` (the default). `execution-agent-redesign` is an older branch.

## Setting up on a new server

These steps are written so an agent on the new server can follow them. Stop and ask the user wherever a step says so.

### 1. Tools

Needed on `PATH`: `opencode`, `claude`, `git`, `gh`, `bun`, `node`, `jq` (Claude status line), `rg`, `uvx` (Serena MCP), Slurm client commands. Reference versions from the original server: OpenCode v2.0.21, Claude Code 2.1.296.

### 2. Clone both repos

```bash
git clone https://github.com/yangqi-su/research-never-stops ~/.config/opencode
git clone https://github.com/yangqi-su/claude-harness ~/.claude
cd ~/.config/opencode && bun install
```

If `~/.claude` already exists (Claude Code was run before), clone into a temporary folder inside the home directory and move its contents, including `.git`, into `~/.claude` without overwriting files that are already there.

### 3. Log in and recreate untracked files

- `opencode auth login` for the providers used in `opencode.json` (`openai`, `openrouter`).
- Run `claude` once and log in. The claude.ai connectors (PubMed, bioRxiv, etc.) come with the account.
- `service.json` is not committed. It holds one field, `{"password": "..."}`. Ask the user for the value. Create it with mode 600.
- `cli.json` (TUI preferences) is not committed. It is optional.

### 4. Claude MCP servers (user scope)

```bash
claude mcp add --scope user serena -- uvx --from serena-agent serena start-mcp-server --project-from-cwd --context claude-code --open-web-dashboard False
claude mcp add --scope user headroom -- <path to headroom executable> mcp serve
```

`headroom` was installed with pip in a conda env on the original server. Ask the user where it should live on this server. Check with `claude mcp list`.

### 5. Adapt server-specific settings

The original server's paths are `/autofs/projects-t3/lilab/yangqisu/...` and `/local/projects-t3/lilab/yangqisu/...` (repos and miniforge). Find every place that needs changing:

```bash
rg --no-ignore-vcs -n 'projects-t3|lilab' ~/.config/opencode --glob '!node_modules' --glob '!package-lock.json'
rg --no-ignore-vcs -n 'projects-t3|lilab' ~/.claude/CLAUDE.md ~/.claude/settings.json ~/.claude/agents ~/.claude/skills
```

Currently that is:
- `opencode.json`: `permissions` and `experimental.policies` (repo and conda paths)
- `AGENTS.md`: the approved external read-only directories
- `agents/second-opinion.md`: allowed external directories

Slurm partitions, accounts, QOS and GPU types are written into these skills:
- OpenCode: `skills/submitting-slurm-cpu-jobs`, `skills/submitting-slurm-gpu-jobs`, `skills/execution-selection`
- Claude: `skills/slurm-jobs`, `skills/execution-selection`

Find this cluster's values with `sinfo -s`, `sinfo -o "%P %G %N"` and `sacctmgr show assoc user=$USER format=account,partition,qos`. Confirm them with the user before editing.

These edits apply to this server only. Do not commit or push them to `main` without asking the user.

### 6. Check

- `claude mcp list` shows `serena` and `headroom` connected.
- Start `opencode` and `claude` in a research repo and confirm that the custom agents and skills are listed.
- Optional: run `/second-opinion` from each harness on a small question. This shows that each one can call the other.
