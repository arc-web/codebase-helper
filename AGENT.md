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

## Visualization menu (mandatory when renderer not specified)

When the user asks to "visualize", "show visually", "diagram", "map out",
"create a visual for", or similar — without naming a specific renderer —
respond with a lettered menu of the options that fit the content. Do NOT
auto-pick and run. Wait for the user to choose.

Format:
```
Which visualization?

a) arch-viz — <one-line fit description>
b) system-map — <one-line fit description>
c) graphify — <one-line fit description>
d) deck — <one-line fit description>
e) mkdocs-preview — <one-line fit description>
```

Only include renderers that make sense for the content. Order by best fit
first. Always include at least 2 options. Descriptions must be specific to
the user's content, not generic ("identity cards for your 4 auth roles"
not "interactive dark-theme HTML").

Renderer selection guide:
- `arch-viz`: auth flows, credential architectures, identity/access patterns,
  anything with entities + animated step-by-step flows + policy scopes
- `system-map`: node/edge diagrams — agents, scripts, triggers, workflows,
  data pipelines, schema relationships, approval chains
- `graphify`: entity-relationship knowledge graphs extracted from docs or
  code — best when the content is prose-heavy or has many cross-references
- `deck`: presentations, slide decks, briefings, anything meant to be shown
  to an audience sequentially
- `mkdocs-preview`: complex multi-page content, SOPs, reference docs,
  anything that benefits from search + sidebar navigation
- `styled-doc`: finished polished document to send or print (PDF-ready)
- `pandoc`: plain one-off HTML with no framework, fully portable

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
