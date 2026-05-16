# Codebase Helper

Codebase Helper turns development work into clear, navigable artifacts for
humans and agents: interactive notes, repo walkthroughs, handoffs,
implementation summaries, and review-ready context packets.

The first supported workflow is a Material for MkDocs Markdown preview app.
It renders plain Markdown into a searchable local HTML site while preserving
the source as Markdown.

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

Render without opening a browser:

```bash
python3 scripts/preview_markdown.py path/to/note.md --no-open
```

## Expected Use Cases

- Turn implementation notes into navigable local HTML.
- Package handoffs as searchable context packets.
- Convert repo walkthroughs into review-friendly pages.
- Keep generated communication artifacts inside this project instead of a home
  directory prototype.

## Migration Note

This project replaces the prototype previously stored at
`/Users/home/markdown_html5_lab`. That prototype has not been deleted, so it
remains available for manual comparison until a separate cleanup decision is
made.

