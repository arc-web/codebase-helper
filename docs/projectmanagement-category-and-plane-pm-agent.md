# Project Management Category + plane_agent Move + Swarm Program Skill

> **Plan file note**: harness pre-filled slug `witty-roaming-hoare.md`. After approval, rename via `mv` to `projectmanagement_category_and_plane_pm_agent.md` per memory rule `feedback_plan_naming.md`.

---

## 1. Context

We need a reusable system for the workflow we ran manually during the Path to Launch task today. That workflow created 66 Plane tasks in a parent/child tree, polished them with priority + labels + dates, and updated 3 doc files. Ad-hoc Python script. No reuse path. Next program would have to recreate the whole thing by hand.

**What exists today**:
- `~/ai/agents/projectmanagement/plane_agent/` - polished Python `plane` CLI (OpenBao auth, caching, retry, output formats). Self-contained repo with GitHub remote `arc-web/plane-pm-agent`.
- `~/ai/agents/projectmanagement/project-management-agent/` - DRY-unified merger of client_director + project_management_agent. Supabase-backed sprint/task tracker with templates (MCP/Voice AI/CRM). NOT Plane-connected. Has GitHub remote `arc-web/project-management-agent` (private, "Task management system: projects, sprints, tasks CLI + Vite dashboard. Work-in-progress.").
- `~/.claude/skills/plane-pm/SKILL.md` - basic Plane API reference. No parent/child, no bulk, no plan-parser.

**What you decided** (this turn):
- Locally, both PM-related repos should live under the `~/ai/agents/projectmanagement/` category directory.
- `arc-web/project-management-agent` should live at `~/ai/agents/projectmanagement/project-management-agent/`.
- Plane CLI agent should keep the local folder name `plane_agent`; its GitHub repo is `arc-web/plane-pm-agent`.
- Existing `arc-web/project-management-agent` GitHub repo is kept (you want to maintain it).

**The constraint**: per your directory law (CLAUDE.md line 17), each agent is a self-contained repo. No monorepo. The `projectmanagement/` directory is filesystem grouping only; each child stays its own repo with its own remote.

**Intended outcome**: any future multi-agent program ("Path to Launch v2", "Path to Launch for some-other-agent", etc.) can be enacted by saying `/swarm-program <plan-file>` and ending up with a complete Plane task tree, polished + linked + ready for agents to claim.

---

## 2. Out of Scope

- Not refactoring `project-management-agent`'s internal code. The DECOMPOSE.md follow-ups (relocate non-PM scripts, fix placeholder JWT, add `.env.1p`) stay as separate work.
- Not migrating Plane the platform.
- Not changing the workflow for Path to Launch itself (the 66 tasks created today stay where they are).
- Not building a unified dashboard.
- Not removing or renaming `arc-web/project-management-agent` GitHub repo.

---

## 3. Final Structure

After this plan executes:

```
~/ai/agents/projectmanagement/              <- category dir
   plane_agent/                             <- moved out of the web agent category
      plane                                 (existing CLI, gains `tree` subcommands later)
      SOP.md                                (operational SOP)
      README.md                             (updated with new path)
      .git/                                 (remote: arc-web/plane-pm-agent)
   project-management-agent/                <- existing arc-web/project-management-agent repo
      core/, cli/, apps/, gui/              (existing structure)
      pyproject.toml, README.md             (paths updated if needed)
      .git/                                 (remote: arc-web/project-management-agent)

GitHub:
   arc-web/plane-pm-agent                   <- private repo for local plane_agent
   arc-web/project-management-agent         <- unchanged (already exists)

~/.claude/skills/
   plane-pm/                                (existing reference skill)
   swarm-program/                           <- NEW skill (wraps `plane tree` workflow)
      SKILL.md
```

---

## 4. Plan Steps (in order)

### Step 1 - Create category + move plane_agent

```bash
mkdir -p ~/ai/agents/projectmanagement
ls ~/ai/agents/projectmanagement/plane_agent
```

Wait - `plane_agent` has its own `.git` repo, it's not tracked by a parent. So `git mv` is a no-op as far as the parent tree goes. Use `mv` for the directory move, then update its internal git references:

```bash
cd ~/ai/agents/projectmanagement/plane_agent
# Update README path references
# Verify CLI still works after move
```

The CLI binary symlink (if installed) needs re-pointing:

```bash
ls -la ~/.local/bin/plane 2>/dev/null   # confirm symlink target
ln -sf ~/ai/agents/projectmanagement/plane_agent/plane ~/.local/bin/plane
```

### Step 2 - Create GitHub repo for plane_agent

```bash
cd ~/ai/agents/projectmanagement/plane_agent
/opt/homebrew/bin/gh repo create arc-web/plane-pm-agent --private \
  --description "Plane CE CLI + swarm-program orchestration. Lives under agents/projectmanagement."
git remote add origin git@github.com:arc-web/plane-pm-agent.git
git push -u origin main
```

### Step 3 - Move existing project-management-agent under category

```bash
mv ~/ai/agents/projectmanagement ~/ai/agents/.projectmanagement-repo-moving
mkdir -p ~/ai/agents/projectmanagement
mv ~/ai/agents/.projectmanagement-repo-moving ~/ai/agents/projectmanagement/project-management-agent
# Remote arc-web/project-management-agent stays unchanged
# Internal .git tracking is unchanged
```

Update path refs inside that repo if needed (most code uses relative paths).

### Step 4 - Extend plane-pm-agent CLI with tree subcommands

Edit `~/ai/agents/projectmanagement/plane_agent/plane` (single Python file). Add commands:

| Command | What it does |
|---|---|
| `plane tree create <plan.md> [--project AGENT] [--dry-run]` | Parse plan markdown for stage tables. Create root + stage parents + leaf children with `parent` field linkage. Write state file at `~/.cache/plane-cli/trees/<root-seq>.json` with sequence-id map. |
| `plane tree polish <root-seq>` | Bulk PATCH every task in the tree with priority + labels + assignee + target_date. Defaults applied per stage offset. |
| `plane tree status <root-seq>` | Walk the tree and report state of each leaf: Backlog / Todo / Approved / In Progress / Done / Blocked. |
| `plane tree resume <root-seq>` | Continue after crash. Read state file. Skip already-created tasks. Create missing ones. |
| `plane tree verify <root-seq>` | Read tree from Plane and confirm parent linkage on every child. Flag orphans. |

Parser rules (plan markdown):
- Section 0 (Plain English Overview) table with header `Stage | Dept | What | Why` defines stage parents.
- Per-stage subsections under Section 5 (Phased Program) with bold child names define leaves.
- Owner-gate children identified by `OWNER GATE` in title.
- Date offsets from today per stage column or computed (Stage 1 = +7d, Stage 2 = +14d, etc.).

State file format:
```json
{
  "plan_file": "/Users/home/.claude/plans/...",
  "root_seq": 231,
  "root_uuid": "08ae22b0-...",
  "stage_parents": {"L1": {"seq": 232, "uuid": "..."}, ...},
  "children": {"L1.1": {"seq": 241, "uuid": "..."}, ...},
  "created_at": "2026-05-16T...",
  "polished_at": "2026-05-16T..."
}
```

Idempotency rule: before POST, query existing issues by title prefix `[ARC-<code>]`. If found, skip create + record UUID in state file.

### Step 5 - Create swarm-program skill

New file: `~/ai/tools/ai/claude-skills/swarm-program/SKILL.md` (symlinked at `~/.claude/skills/swarm-program/SKILL.md`).

Skill content:
- Trigger: user says "build the Plane tree for plan X", "spin up the swarm program", "/swarm-program <plan-path>", or invokes `/swarm-program`.
- Steps the skill walks through:
  1. Read the plan file. Verify it has the required structure (Section 0 overview + Section 5 phases + dual vocabulary section if needed).
  2. Dry-run: `plane tree create <plan> --dry-run`. Show owner what tasks will be created.
  3. Wait for owner approval.
  4. Real run: `plane tree create <plan>`.
  5. Polish: `plane tree polish <root-seq>`.
  6. Verify: `plane tree verify <root-seq>`.
  7. Update plan file with Plane task IDs (write Appendix C section).
  8. Report back: root URL, total tasks, stage breakdown.
- Auto-commit per memory rule (skill edits commit + push to `arc-web/claude-skills`).

### Step 6 - Update doc set

Files to update:

| File | Update |
|---|---|
| `/Users/home/ai/apps/products/todovibes/CLAUDE.md` | Ensure project-management-agent references point to `~/ai/agents/projectmanagement/project-management-agent/`. Add cross-ref to swarm-program skill if still relevant. |
| `~/ai/agents/projectmanagement/plane_agent/SOP.md` | Add new section "Tree commands" documenting `plane tree create/polish/status/resume/verify` when those commands are implemented. Remove the "Subtasks/parent links not surfaced" gap then. |
| `~/ai/agents/projectmanagement/plane_agent/README.md` | Update path in Setup section. Add tree commands table when those commands are implemented. |
| `~/.claude/CLAUDE.md` (Domain rules table) | Add row: `Plane swarm program (build a multi-agent task tree from a plan) -> ~/.claude/skills/swarm-program/SKILL.md`. |
| `~/ai/apps/products/todovibes/evaluations/plane/plane-agent-context.md` | Already has pointer to canonical rules. Just update the agent path. |
| `~/ai/agents/comms/discord_agent/docs/plane_team_onboarding_runbook.md` | Path refs updated. |
| `/Users/home/.claude/plans/google_ads_agent_production_readiness_program.md` | Add note in Appendix C that future programs use `/swarm-program <plan>`. |

### Step 7 - Verify end-to-end

```bash
# 1. CLI still works after move
plane projects
plane issues AGENT --priority urgent

# 2. Tree status against the existing Path to Launch tree
plane tree status 231
# Expected: report all 66 task states by stage

# 3. Dry-run on a tiny test plan
echo "# Test Plan
## Section 0
| Stage | Dept | What | Why |
|---|---|---|---|
| 1 - Test | Testing | Verify swarm works | proves it |
## Section 5
### Stage 1
- **Test child 1**
- **Test child 2**
- **OWNER GATE - approve test exit**
" > /tmp/test_plan.md
plane tree create /tmp/test_plan.md --dry-run
# Expected: shows 1 root + 1 parent + 3 children, no API writes

# 4. Real run on test plan in a sandbox project
plane tree create /tmp/test_plan.md --project AGENT
# Expected: creates 5 tasks, returns root_seq

# 5. Polish + verify
plane tree polish <root_seq>
plane tree verify <root_seq>

# 6. Cleanup the test tree
plane tree delete <root_seq>   # optional, or leave as evidence

# 7. Test the skill end-to-end
# In a fresh Claude Code session: /swarm-program /tmp/test_plan.md
# Expected: dry-run -> wait for approval -> create -> polish -> verify -> report
```

---

## 5. Critical Files Map

**Read** (not modified):
- `~/ai/agents/projectmanagement/plane_agent/plane` (CLI source, ~600 lines)
- `~/ai/agents/projectmanagement/plane_agent/SOP.md`
- `~/ai/agents/projectmanagement/plane_agent/README.md`
- `~/ai/agents/projectmanagement/project-management-agent/DECOMPOSE.md`
- `/Users/home/.claude/plans/google_ads_agent_production_readiness_program.md` (template for what a "plan" looks like in our system)

**Moved** (filesystem `mv`):
- former web-category Plane CLI repo -> `~/ai/agents/projectmanagement/plane_agent/`
- `~/ai/agents/projectmanagement/` repo root -> `~/ai/agents/projectmanagement/project-management-agent/`

**Edited**:
- `~/ai/agents/projectmanagement/plane_agent/plane` (add tree subcommands later)
- `~/ai/agents/projectmanagement/plane_agent/SOP.md` (add Tree commands section later, drop Known Gap then)
- `~/ai/agents/projectmanagement/plane_agent/README.md` (update paths now, add tree table later)
- `~/.claude/CLAUDE.md` (add domain row for swarm-program skill)
- `/Users/home/ai/apps/products/todovibes/CLAUDE.md` (path refs + skill pointer)
- `~/ai/agents/comms/discord_agent/docs/plane_team_onboarding_runbook.md` (path refs)

**Created**:
- `~/ai/agents/projectmanagement/` (category dir)
- `~/ai/agents/projectmanagement/project-management-agent/` (moved repo path)
- `~/ai/agents/projectmanagement/plane_agent/` (moved repo path)
- `~/ai/tools/ai/claude-skills/swarm-program/SKILL.md` (new skill, symlinked into `~/.claude/skills/`)
- New private GitHub repo: `arc-web/plane-pm-agent`

**Unchanged**:
- `arc-web/project-management-agent` GitHub repo (description, code, remote URL all stay)
- The 66 Path to Launch Plane tasks (AGENT-231 through AGENT-297)

---

## 6. Reused Existing Code

From the exploration:
- **OpenBao token retrieval** (`~/ai/agents/projectmanagement/plane_agent/plane` lines 31-52 in CLI). Reuse for tree commands.
- **HTTP retry with backoff** (`~/ai/agents/projectmanagement/plane_agent/plane` lines 56-82). Reuse for bulk operations.
- **Cache pattern** (`~/.cache/plane-cli/`). Extend with `trees/` subdir for state files.
- **Plan markdown structure** (`/Users/home/.claude/plans/google_ads_agent_production_readiness_program.md` Section 0 + Section 5). Use as template the parser keys off of.
- **Python create + PATCH pattern** (`~/.claude/skills/plane-pm/SKILL.md` lines 78-127). Same auth + headers + payload shape.
- **Task quality gate field list** (`/Users/home/ai/apps/products/todovibes/CLAUDE.md` Task Quality Gate section lines 202-210). Use for the polish step defaults.

---

## 7. Open Decisions for Owner

Two small decisions before Step 1:

1. **CLI binary name**: keep `plane` as the command name (you type `plane projects`) even though the remote repo is named `plane-pm-agent`. Yes / no.
2. **Skill location**: skill lives in `arc-web/claude-skills` (the symlinked skill dir). Auto-commits per memory rule. Confirm or change.

Defaults shown are recommendations. If you approve without choosing, I take the defaults.

---

## 8. Verification (end-to-end)

After all 7 steps complete:

1. `which plane` -> resolves to symlink pointing at new path.
2. `plane projects` -> works (cache + token still fine).
3. `ls ~/ai/agents/projectmanagement/` -> shows `plane_agent/` and `project-management-agent/`.
4. `git -C ~/ai/agents/projectmanagement/project-management-agent remote -v` -> shows `arc-web/project-management-agent`.
5. `ls ~/ai/agents/web/` -> no `plane_agent/` (moved out).
6. `gh repo view arc-web/plane-pm-agent` -> exists, private.
7. `gh repo view arc-web/project-management-agent` -> still exists, unchanged.
8. `plane tree status 231` -> reports 66 task states after tree commands are implemented.
9. `/swarm-program /tmp/test_plan.md` in a fresh session -> end-to-end works after the skill is implemented.
10. The doc updates (CLAUDE.md, SOP.md, README.md, onboarding runbook) all point at the new paths.

If any of those 10 checks fail, the plan is not done. Each one is a hard gate.

---

## 9. Notes on the existing project-management-agent

The DECOMPOSE.md inside that repo flags non-PM scripts at root (airtable, budget migrations, contacts, sentiment, etc.) that should relocate elsewhere. This plan does NOT do that decomposition. It moves the whole directory as-is. Decomposition stays a follow-up plan after this one lands.

---

**End of plan.**

<div class="artifact-meta" markdown="1">

**Preset:** Implementation Summary
**Source:** `.claude/plans/projectmanagement_category_and_plane_pm_agent.md`
**Use:** Change summary with affected files, commands, and verification evidence.

</div>
