# Codebase Helper

**Turn any Markdown file into a browser-ready interactive artifact in one command.** No manual HTML, no copy-paste into editors, no formatting fights. Write once in Markdown; pick a renderer; open in browser.

Markdown stays the source of truth. Every renderer is a downstream view that you can regenerate at any time.

---

## Why use this instead of just opening a .md file

Raw Markdown in a text viewer is flat, unsearchable, and ugly. What you actually want:

- **Complex docs** → searchable, multi-page, navigable website with a sidebar (30 seconds, not 30 minutes)
- **SOPs / handoffs** → polished single-file HTML you can email or print to PDF
- **Workflows, agent maps, pipelines** → interactive node/edge diagram with hover focus and animated connections
- **Auth flows, credential architectures** → dark-theme identity cards with animated step-by-step flows, policy scope grids, audit log previews
- **Entity relationships from docs/code** → clickable knowledge graph with clustered communities
- **Briefings for stakeholders** → animated slide deck with transitions
- **Everything else** → your choice of 7 renderers, one command each

---

## Renderers

Ask for a visualization and get a lettered menu of options suited to your content. Pick one.

| Renderer | Output | Best for |
|----------|--------|----------|
| `mkdocs-preview` | Live local MkDocs Material site | Complex docs, SOPs, multi-page reference, anything needing search + sidebar |
| `styled-doc` | Single-file HTML + optional PDF on Desktop | Finished documents to send, print, or share |
| `system-map` | Interactive node/edge graph on Desktop | Workflows, agent maps, data pipelines, approval chains, if/then logic |
| `arch-viz` | Interactive dark-theme identity flow HTML on Desktop | Auth/credential flows, identity cards, policy scope grids, animated step-by-step |
| `graphify` | Clustered knowledge graph on Desktop | Entity relationships extracted from prose, docs, or code |
| `deck` | Animated slide presentation on Desktop | Briefings, walkthroughs, anything shown to an audience sequentially |
| `pandoc` | Plain portable HTML on Desktop | One-off conversion, no framework, fully self-contained |

Full data shapes and usage in `RENDERERS.md`.

---

## Usage

### Ask for a visualization (menu appears)

When you say "visualize X" without naming a renderer, you get a lettered menu of options suited to the content. Pick one and it runs.

### Run a specific renderer directly

```bash
# Default: navigable MkDocs site (opens at localhost:8012)
python3 scripts/preview_markdown.py path/to/note.md

# Polished single-file HTML + PDF
python3 scripts/render_styled.py path/to/doc.md --pdf

# Interactive workflow/agent diagram
python3 scripts/render_system_map.py path/to/map.md

# Auth/credential flow visualization
python3 scripts/render_arch_viz.py path/to/arch.md

# Knowledge graph from docs or code
python3 scripts/render_graphify.py path/to/content.md

# Slide deck
python3 scripts/render_deck.py path/to/deck.md

# Plain portable HTML
python3 scripts/render_pandoc.py path/to/doc.md
```

All renderers share the same flags: `--output PATH`, `--title "..."`, `--no-open`.

### External Markdown (from another repo)

Works without touching the source file:

```bash
python3 scripts/preview_markdown.py ~/ai/other-project/docs/notes.md
```

Renders as a transient preview under `.cache/` — source stays in the owning repo, nothing gets copied into `codebase_helper`.

---

## Data formats

### `system-map` — embed a fenced block in Markdown

```markdown
```system-map
{
  "title": "My Pipeline",
  "nodes": [
    { "id": "ingest", "label": "Ingest", "type": "agent", "lane": "input", "status": "current", "summary": "Pulls raw data" },
    { "id": "process", "label": "Process", "type": "script", "lane": "core", "status": "current", "summary": "Transforms it" }
  ],
  "edges": [
    { "from": "ingest", "to": "process", "label": "raw data" }
  ]
}
```
```

### `arch-viz` — embed a fenced block in Markdown

```markdown
```arch-viz
{
  "project": { "title": "My Auth Architecture", "subtitle": "Who can read what" },
  "identities": [
    {
      "id": "agent",
      "name": "Automated Agent",
      "icon": "🤖",
      "authType": "AppRole",
      "description": "Machine identity with scoped read access",
      "steps": [ ... ],
      "policies": { "allow": ["shared/*"], "deny": ["admin/*"] },
      "auditLog": "role_name=agent | path=secret/data/shared/key | op=read"
    }
  ],
  "flows": [ ... ],
  "infrastructure": [ { "label": "Vault", "value": "https://vault.example.com" } ]
}
```
```

See `smoke/fixtures/arch-viz-sample.md` for a complete working example.

---

## Smoke test

```bash
bash smoke/smoke_preview_workflow.sh
```

Runs all renderers, validates output, restores any mutated files. Required before PRs.

---

## Adding a renderer

One script under `scripts/`, one row in `RENDERERS.md`, one kebab-case name. See `RENDERERS.md` for the full spec. Do not extend an existing renderer; add a new named one.
