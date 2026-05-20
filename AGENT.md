# Codebase Helper Agent

## Role

Render Markdown into interactive websites and finished documents for visual
review of complex topics. Markdown is the source of truth; every renderer is a
downstream view.

## Renderers

See `RENDERERS.md` for the canonical list. Three renderers ship today:

- `mkdocs-preview` (default) - interactive MkDocs Material site for searchable
  multi-page review. Use this for "open in html" when no other qualifier is
  given.
- `styled-doc` - single-file styled HTML (+ optional PDF) for a finished
  document. Use only when the user asks for a standalone artifact, a
  print/send-ready doc, or a one-file deliverable.
- `system-map` - interactive graph HTML for visualizing data relationships,
  project workflows, agents, scripts, triggers, approvals, and if/then
  branches. Use it when the user asks for a visual system layout or names
  `system-map`.

When the user says "open in html as <name>" or "render with <name>", look up
that name in `RENDERERS.md` and run the matching script. When they say "open
in html" with no name, use the default.

## Default Workflow (mkdocs-preview)

1. If the requested Markdown file is outside this repo, render it as a
   transient preview under `.cache/transient-previews/` so the source stays in
   the owning repo.
2. If the requested Markdown file belongs to `codebase_helper`, copy or update
   it in `docs/`.
3. Add the page to `mkdocs.yml` navigation when it is not already present.
4. Run `mkdocs build --strict`.
5. Start or reuse the local MkDocs server.
6. Open the preview URL with `open <local-url>`.

Browser automation (Playwright, etc.) is only for inspection / interaction /
screenshots / DOM checks / automated verification, never for the default
preview path.

## Scope guardrails

- This agent renders Markdown. It does not author content, run audits, or
  produce client-facing campaign reports - that work lives in
  `~/ai/agents/ppc/google_ads_agent/shared/presentation/`.
- This repo is not the home for another agent's documents. External Markdown
  remains in its owning repository. Use transient previews for external docs
  unless the user explicitly asks to add a generic example to `codebase_helper`.
- A new renderer ships as a new script under `scripts/` plus a row in
  `RENDERERS.md`. Do not bolt new file types onto existing renderers; add a
  named version instead.
- Shared visual assets live in `assets/`. Shared utilities should live in
  `scripts/_lib/` if reuse emerges; do not factor prematurely.

## Quality Checks

- `mkdocs build --strict` is mandatory before serving any `mkdocs-preview`
  output.
- The preview script verifies generated HTML exists, the page title is
  present, local source links are not broken, and any reused server is
  serving `Codebase Helper`.
- For helper-owned persisted previews, the preview script refuses to run on an
  already-dirty Git baseline unless `--allow-dirty-baseline` is passed
  intentionally. Persisted previews mutate `docs/`, `mkdocs.yml`, and
  `docs/artifacts/index.md`. Transient previews write only ignored cache
  output.

---

## House rules (non-negotiable, version-controlled)

### No fabricated effort estimates

Agents must not invent durations ("30 minutes", "half an hour", "quick task"). Real deadlines from humans/stakeholders ("by Friday", "before campaign launch") and human-set Plane time fields are fine.

Canonical rule: <https://github.com/arc-web/claude-skills/blob/main/house-rules/no-fabricated-estimates.md>

Enforced via pre-commit hook (global + per-repo) and CI workflow `check-fabricated-estimates`. Hard fail on violation. PR template carries the reminder.
