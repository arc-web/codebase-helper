# Plan: Locate the "styled artifact / md → HTML" tool the user recently built

## Context

User asked to open `~/.claude/plans/plane_docs_sync.md` "in html" using a tool they "just built" that "actually styles and does something meaningful." I converted with plain `pandoc -s` (default Pandoc CSS) and opened it; user said that was not the tool. They want me to find it.

Confirmed dead ends so far:
- `~/.claude/skills/web-artifacts-builder/` exists but only contains `test-artifact/node_modules/` (no SKILL.md, no source). Not the tool, or it lives elsewhere and this is a stale scaffold.
- `git log` in `~/ai/tools/ai/claude-skills` shows last skill commit was `plane-pm` (0360511); no `web-artifacts-builder` commits.
- `/deck` skill exists (presentations), `/web-design` (full LP pipeline) — neither is "open this MD as styled HTML."

This plan describes a deterministic, exhaustive search so I don't keep guessing.

## Critical files / locations to inspect

- `~/.claude/skills/` (and source `~/ai/tools/ai/claude-skills/`) — primary skill registry
- `~/.claude/plugins/` and `~/.claude/commands/` — slash commands and plugin definitions
- `~/ai/tools/` recursive — bespoke CLIs
- `~/ai/agents/` recursive — agent-bundled tools
- `~/.local/bin`, `/opt/homebrew/bin`, `/usr/local/bin` — installed CLIs
- Shell histories: `~/.zsh_history`, `~/.bash_history`
- Claude Code transcripts: `~/.claude/projects/-Users-home/*/transcript*.jsonl` (recent sessions, last 7 days)
- Plane "Internal" workspace AGENT project recent issues (last 7 days) — user creates tasks for everything they build
- Recently modified files anywhere under `~/ai/` (last 7 days, name containing "render", "artifact", "doc", "md", "html", "style", "pretty")
- Git history on every `~/ai/tools/*` and `~/ai/agents/*` repo for commits in last 14 days

## Search procedure

Run in this exact order; stop early on first solid hit.

### Step 1 — Recent filesystem activity (cheapest, highest signal)

```bash
find /Users/home/ai -maxdepth 8 -type f -mtime -7 \
  \( -name 'SKILL.md' -o -name 'README*' -o -name '*.sh' -o -name '*.js' -o -name '*.ts' -o -name '*.py' \) \
  -not -path '*/node_modules/*' -not -path '*/.git/*' 2>/dev/null \
  | xargs grep -l -i -E 'markdown.*to.*html|md.*to.*html|render.*md|styled.*doc|artifact.*build|pretty.*md' 2>/dev/null
```

Also list all files modified in last 7 days under `~/ai/tools/` and `~/.claude/`:

```bash
find /Users/home/ai/tools /Users/home/.claude -type f -mtime -7 \
  -not -path '*/node_modules/*' -not -path '*/.git/*' 2>/dev/null | head -100
```

### Step 2 — Slash commands and plugins

```bash
ls -la /Users/home/.claude/commands/ /Users/home/.claude/plugins/ 2>/dev/null
find /Users/home/.claude/commands /Users/home/.claude/plugins -type f 2>/dev/null \
  | xargs grep -l -i -E 'markdown|html|style|render|artifact' 2>/dev/null
```

### Step 3 — Installed CLI binaries with relevant names

```bash
for p in /Users/home/.local/bin /opt/homebrew/bin /usr/local/bin; do
  ls $p 2>/dev/null | grep -i -E 'md|html|doc|render|artifact|pretty|style'
done
```

### Step 4 — Shell history (last 500 lines, grep for invocation)

```bash
tail -500 /Users/home/.zsh_history 2>/dev/null \
  | grep -i -E 'md.*html|render|artifact|styled|pretty' \
  | tail -30
```

### Step 5 — Claude Code transcripts (last 7 days, last 5 sessions)

```bash
find /Users/home/.claude/projects/-Users-home -type f -name '*.jsonl' -mtime -7 \
  -exec grep -l -i -E 'styled.*html|md.*to.*html|artifact.*builder|render.*plan' {} \; \
  | head -5
```

For any hit: open file, find the bash invocation or skill reference.

### Step 6 — Plane AGENT project recent issues

```python
# todovibes / AGENT, last 7 days, filter for build/tool tasks
import subprocess, json
KEY = subprocess.check_output(['op','item','get','x7qhfdaos76fcymuztjjscmrpa','--vault','Zeroclaw','--reveal','--fields','credential'], text=True).strip()
url = 'https://arc.todovibes.com/api/v1/workspaces/todovibes/projects/0e399778-93d9-4a95-ba2f-755990dd69bc/issues/?per_page=100'
r = json.loads(subprocess.check_output(['curl','-s','-H',f'X-API-Key: {KEY}','-H','User-Agent: plane-cli/1.0',url], text=True))
for i in r['results']:
    if any(w in (i.get('name','') or '').lower() for w in ['html','render','artifact','md','styled','pretty','doc']):
        print(i['sequence_id'], i['name'])
```

### Step 7 — Git history across `~/ai/tools/*` and `~/ai/agents/*` (last 14 days)

```bash
for d in /Users/home/ai/tools/*/.git /Users/home/ai/agents/*/.git \
         /Users/home/ai/tools/*/*/.git /Users/home/ai/agents/*/*/.git; do
  repo="${d%/.git}"
  hits=$(git -C "$repo" log --since='14 days ago' --oneline 2>/dev/null \
    | grep -i -E 'md|html|render|artifact|styled|pretty|doc')
  [ -n "$hits" ] && { echo "== $repo =="; echo "$hits"; }
done
```

### Step 8 — `web-artifacts-builder` scaffold provenance

Even though the dir is empty, look for the commit that created it (in claude-skills repo) or any README in `~/ai/docs/claude-config/claude-skills/web-artifacts-builder/`. If empty everywhere, ask user where the source lives.

```bash
git -C /Users/home/ai/tools/ai/claude-skills log --all --oneline -- web-artifacts-builder 2>&1
git -C /Users/home/ai/docs/claude-config/claude-skills log --all --oneline 2>&1 | head -20
find /Users/home/ai/docs/claude-config/claude-skills/web-artifacts-builder -type f -not -path '*/node_modules/*' 2>/dev/null
```

### Step 9 — Web/IDE app context (if "just built" means on the web Claude)

If steps 1-8 yield nothing local, the tool was likely built/used in the Claude.ai web app (artifacts panel) or sits in a different machine. Stop and confirm with user before guessing further.

## Outputs

For each hit, capture:
- File path of the tool's entry point (`SKILL.md`, CLI script, slash command)
- Invocation syntax (one-liner)
- Recent example of it being run (from transcript or shell history)

Then run it against `/Users/home/.claude/plans/plane_docs_sync.md`, output to `~/Desktop/plane_docs_sync.html`, open with `open`.

## Verification

- Tool runs without error.
- Output HTML opens in browser.
- Visual styling is clearly non-default (custom fonts, colors, layout — not Pandoc default).
- User confirms "yes that's the tool."

## Stop conditions

- Tool found and runs cleanly → execute on the plan file, return path + open.
- Steps 1-9 all empty → return a one-line report: "Searched 9 places, nothing called 'styled MD → HTML' exists locally. Where did you build it?" Do not invent or substitute.
