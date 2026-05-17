# Plane-GitHub Bridge

## Context

Plane tasks and GitHub PRs live in separate worlds. No one knows which branch belongs to which task. When a PR merges, the task stays open until someone manually closes it. This plan fixes that with GitHub Actions - automatic scripts that fire every time something happens on GitHub, no human needed.

---

## Plain English: How It Works After This Is Built

1. You (or Claude) start work on a Plane task → get a ready-made branch name
2. Claude opens a PR with `Plane-Task: AGENT-224` in the description
3. **Automatically**: Plane task moves to In Progress, gets a comment with the PR link
4. PR merges → **automatically**: Plane task moves to Done
5. PR closed without merging → **automatically**: Plane task goes back to Todo

No manual Plane updates ever again.

---

## Architecture

```
GitHub PR opened/merged
        ↓
  GitHub Actions fires
  (reads "Plane-Task: AGENT-224" from PR body)
        ↓
  Calls Plane API
  (updates task state + posts comment)
        ↓
  Plane task reflects reality
```

Plane → GitHub direction is agent-driven: Claude generates the branch name when starting a task. That's enough - the branch name encodes the task ID.

---

## Components

### 1. GitHub Org Secret: `PLANE_API_KEY`

Set once at arc-web org level → available to all repos automatically, no per-repo setup.

Value: fetch from 1P Zeroclaw vault item `x7qhfdaos76fcymuztjjscmrpa` field `credential`.

User does this in GitHub Settings → Organization → Secrets (one-time manual step, takes 2 minutes).

---

### 2. Reusable Workflow: `arc-web/review-workflows`

File: `.github/workflows/plane-sync.yml` in `arc-web/review-workflows` repo.

What it does:
- Parses PR body for `Plane-Task: AGENT-224` (or any project prefix)
- On PR opened → PATCH Plane task to In Progress + POST comment "PR #N opened: <link>"
- On PR merged → PATCH Plane task to Done + POST comment "PR #N merged to main"
- On PR closed (no merge) → PATCH Plane task back to Todo + POST comment "PR #N closed without merge"
- If no `Plane-Task:` line found → silently skip (no error)

Detects project from task ID prefix (AGENT, INFRA, COMM, ADS, LAND, JOHAN) → maps to UUID automatically.

---

### 3. Caller File (added to each repo as touched)

`.github/workflows/plane-sync.yml` in any repo that wants the sync:

```yaml
name: Plane Sync
on:
  pull_request:
    types: [opened, closed]

jobs:
  sync:
    uses: arc-web/review-workflows/.github/workflows/plane-sync.yml@main
    secrets:
      PLANE_API_KEY: ${{ secrets.PLANE_API_KEY }}
```

8 lines. Added to `arc-web/reportcard-agent` first as the test case.

---

### 4. Skill Updates

**`/github-pr-flow` skill** (`~/.claude/skills/github-pr-flow/SKILL.md`):
- Accept optional `plane_task_id` input
- Step 9 (open PR): always include `Plane-Task: AGENT-XXX` in PR body metadata block alongside existing Agent/Session/Plan trailers
- Branch name when task ID provided: `<agent>/<type>/<task-id-lowercase>-<slug>` e.g. `claude/feat/agent-224-gsc-oauth`

**`/plane-pm` skill** (`~/.claude/skills/plane-pm/SKILL.md`):
- Add branch name generator: given a Plane task ID + title, output the `git checkout -b` command
- Pattern: `claude/feat/<project-id-lowercase>-<slug-from-title-max-5-words>`

Both skills live in `~/ai/tools/ai/claude-skills/` - auto-commit to arc-web/claude-skills on edit.

---

## Files Changed

| File | Action |
|------|--------|
| `arc-web/review-workflows/.github/workflows/plane-sync.yml` | Create (reusable workflow) |
| `arc-web/reportcard-agent/.github/workflows/plane-sync.yml` | Create (caller, first test repo) |
| `~/.claude/skills/github-pr-flow/SKILL.md` | Update (add Plane-Task line + branch naming) |
| `~/.claude/skills/plane-pm/SKILL.md` | Update (add branch name generator) |

---

## One-Time User Step

Go to: `https://github.com/organizations/arc-web/settings/secrets/actions`
Add secret: `PLANE_API_KEY` = (value from 1P Zeroclaw item `x7qhfdaos76fcymuztjjscmrpa` field `credential`)

Everything else Claude handles.

---

## Execution Order

1. User sets org secret `PLANE_API_KEY` in GitHub (manual, 2 min)
2. Create reusable workflow in `arc-web/review-workflows`
3. Add caller to `arc-web/reportcard-agent`
4. Update both skills + auto-commit to arc-web/claude-skills
5. Test: open a test PR on reportcard-agent with `Plane-Task: AGENT-224` in body → confirm Plane updates

---

## Verification

1. Open test PR on `arc-web/reportcard-agent` with body containing `Plane-Task: AGENT-224`
2. Check GitHub Actions tab → workflow runs, exits 0
3. Check Plane AGENT-224 → state = In Progress, comment with PR link
4. Merge PR → check AGENT-224 → state = Done, second comment
5. Run the same flow on a PR with no `Plane-Task:` line → confirm workflow exits silently

<div class="artifact-meta" markdown="1">

**Preset:** Note
**Source:** `.claude/plans/plane_github_bridge.md`
**Use:** Fast Markdown preview with source provenance.

</div>
