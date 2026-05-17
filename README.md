# Codebase Helper

Codebase Helper turns development work into clear, navigable artifacts for
humans and agents: interactive notes, repo walkthroughs, handoffs,
implementation summaries, and review-ready context packets.

The first supported workflow is a Material for MkDocs Markdown preview app.
It renders plain Markdown into a searchable local HTML site while preserving
the source as Markdown.

v2 adds artifact presets, a shared visual layer, a local artifact gallery, and
static checks while keeping the same Markdown-first contract.

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

Render and open a Markdown file:

```bash
python3 scripts/preview_markdown.py path/to/note.md
```

This is the default HTML preview path. It opens a localhost MkDocs Material page
with site navigation and top-right controls.

Render without opening a browser:

```bash
python3 scripts/preview_markdown.py path/to/note.md --no-open
```

Render a richer handoff artifact:

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

Render a standalone styled HTML document without adding it to the MkDocs site
only when a standalone finished document is explicitly requested:

```bash
python3 scripts/render_styled.py docs/supabase-visual-reference-research.md --output /tmp/codebase-helper-supabase-reference.html --no-open
```

`scripts/render_styled.py` uses the root `assets/*.css` files and writes to
`~/Desktop` by default. For tests and temporary previews, write outputs under
`/tmp` so standalone artifacts do not become repo state.

## Expected Use Cases

- Turn implementation notes into navigable local HTML.
- Package handoffs as searchable context packets.
- Convert repo walkthroughs into review-friendly pages.
- Keep generated communication artifacts inside this project instead of a home
  directory prototype.

## Audit Notes

The current local HTML tooling inventory lives at
`docs/html-tooling-inventory.md`. It records the source candidates checked,
their reuse value, and the v2 direction.

## Migration Note

This project replaces the prototype previously stored at
`/Users/home/markdown_html5_lab`. That prototype has not been deleted, so it
remains available for manual comparison until a separate cleanup decision is
made.
