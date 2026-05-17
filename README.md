# Codebase Helper

Codebase Helper renders Markdown into interactive websites and finished
documents for visual review of complex topics. Markdown stays the source of
truth; every renderer is a downstream view.

The canonical list of renderers lives in `RENDERERS.md`. Three ship today:

- **`mkdocs-preview`** (default) - interactive Material for MkDocs site on
  `127.0.0.1:8012`. Searchable, multi-page, navigable. This is the original
  mission and the default for "open in html".
- **`styled-doc`** - single-file styled HTML (+ optional PDF) saved to
  `~/Desktop/`. Use only when a standalone, send-ready document is needed.
- **`system-map`** - interactive graph HTML saved to `~/Desktop/`. Use for
  visualizing schemas, project flows, agents, scripts, triggers, and if/then
  logic.

## Common Commands

Check the installed MkDocs runtime:

```bash
mkdocs --version
```

Build the current preview site:

```bash
mkdocs build --strict
```

Preview the current site:

```bash
mkdocs serve -a 127.0.0.1:8012
```

### Default renderer: `mkdocs-preview`

```bash
python3 scripts/preview_markdown.py path/to/note.md
```

Opens a localhost MkDocs Material page with site navigation and top-right
controls.

Without opening a browser:

```bash
python3 scripts/preview_markdown.py path/to/note.md --no-open
```

Richer artifact preset:

```bash
python3 scripts/preview_markdown.py path/to/handoff.md --preset handoff
```

Preview runs mutate `mkdocs.yml`, copied pages under `docs/`,
`docs/artifacts/index.md`, and `.cache/artifacts.json`. By default the helper
refuses to run when the Git worktree is already dirty. Use
`--allow-dirty-baseline` only when those existing changes are intentional.

Available presets:

- `note`
- `handoff`
- `repo-walkthrough`
- `implementation-summary`
- `review-packet`

The script records rendered pages in `docs/artifacts/index.md` unless
`--skip-gallery` is used. It also runs static checks after the strict MkDocs
build unless `--skip-checks` is used.

### Alternate renderer: `styled-doc`

Standalone styled HTML, written to `~/Desktop/` and opened in the browser:

```bash
scripts/render_styled.py path/to/doc.md
```

Also export a PDF (Chrome headless):

```bash
scripts/render_styled.py path/to/doc.md --pdf
```

Other flags: `--output PATH`, `--title "..."`, `--subtitle "..."`, `--no-open`.

`scripts/render_styled.py` uses the root `assets/*.css` files. For tests and
temporary previews, write outputs under `/tmp` so standalone artifacts do not
become repo state.

### Visual renderer: `system-map`

Interactive graph HTML, written to `~/Desktop/` and opened in the browser:

```bash
scripts/render_system_map.py docs/agent-system-map-sample.md
```

Test without opening:

```bash
scripts/render_system_map.py docs/agent-system-map-sample.md --output /tmp/codebase-helper-agent-system-map.html --no-open
```

The source Markdown owns the map data in a fenced `system-map`, `json`, or
`yaml` block. Use this renderer for database relationships, project workflows,
agent collaboration maps, script chains, triggers, approval gates, and
if/then branches.

## Adding a new renderer

See `RENDERERS.md`. Each renderer is one script under `scripts/`, one row in
`RENDERERS.md`, one kebab-case name. Do not extend an existing renderer with
new output formats; add a named version.

## Expected Use Cases

- Turn implementation notes into navigable local HTML.
- Package handoffs as searchable context packets.
- Convert repo walkthroughs into review-friendly pages.
- Produce a single styled file to send a client or stakeholder.
- Render visual maps for data relationships, project flows, agents, scripts,
  triggers, and decision branches.

## Audit Notes

The local HTML tooling inventory lives at `docs/html-tooling-inventory.md`. It
records source candidates checked, their reuse value, and the v2 direction.

## Migration Note

This project replaces the prototype previously stored at
`/Users/home/markdown_html5_lab`. That prototype has not been deleted, so it
remains available for manual comparison until a separate cleanup decision is
made.
