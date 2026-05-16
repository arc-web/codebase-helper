# Codebase Helper

This is the working surface for converting Markdown notes, handoffs, and
codebase walkthroughs into a searchable HTML5 learning interface.

## What This Proves

- A plain `.md` file can become a navigable HTML site.
- Headings become the page outline and table of contents.
- Code blocks get syntax highlighting and copy buttons.
- Admonitions, tabs, details blocks, tables, and task lists create richer study
  views without custom JavaScript.

## Fast Commands

Build the static site:

```bash
mkdocs build --strict
```

Preview locally:

```bash
mkdocs serve -a 127.0.0.1:8012
```

Render and open a Markdown file:

```bash
python3 scripts/preview_markdown.py path/to/note.md
```

## Next Conversion Pattern

Run the helper script with an existing Markdown file. The script copies it into
`docs/`, adds it to navigation, runs a strict build, starts or reuses a local
server, and opens the preview URL.

## Artifact Mode

Use presets when the page is more than a quick note:

```bash
python3 scripts/preview_markdown.py path/to/handoff.md --preset handoff
python3 scripts/preview_markdown.py path/to/walkthrough.md --preset repo-walkthrough
```

The helper records rendered pages in the [Artifact Gallery](artifacts/index.md)
and keeps the local HTML tooling audit in the
[HTML Tooling Inventory](html-tooling-inventory.md).

Preview runs update repo files and refuse to start from a dirty Git baseline
unless `--allow-dirty-baseline` is passed.
