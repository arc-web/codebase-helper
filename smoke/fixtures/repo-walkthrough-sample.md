# Repo Walkthrough Sample

## Map

| Path | Purpose |
| --- | --- |
| `README.md` | Human-facing command summary. |
| `AGENT.md` | Local operating contract for agents. |
| `scripts/preview_markdown.py` | Markdown preview entrypoint. |
| `docs/` | MkDocs source pages. |

## Walkthrough

1. Read `AGENT.md` for the workflow contract.
2. Run `mkdocs build --strict` before previewing a page.
3. Use `scripts/preview_markdown.py` for source Markdown handoffs.
4. Check `docs/artifacts/index.md` for recently rendered artifacts.

??? tip "Verification"
    The generated HTML should exist under `site/repo-walkthrough-sample/index.html`
    after a strict build.

