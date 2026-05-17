# Renderers

Codebase Helper supports multiple named renderers. Each turns Markdown into a
different interactive or finished artifact for visual review. Source of truth
stays Markdown; renderers are downstream views.

When asking a renderer by name, use the **name** column below.

| Name              | Script                          | Output                                              | Use when                                                                |
|-------------------|---------------------------------|-----------------------------------------------------|--------------------------------------------------------------------------|
| `mkdocs-preview`  | `scripts/preview_markdown.py`   | Local MkDocs Material site (`127.0.0.1:8012`)       | Default. Interactive review of complex topics: search, nav, multi-page. |
| `styled-doc`      | `scripts/render_styled.py`      | Single-file styled HTML (+ optional PDF) on Desktop | Finished doc to send or print. One self-contained file.                 |
| `system-map`      | `scripts/render_system_map.py`  | Interactive graph HTML on Desktop                   | Visual maps for schemas, project flows, agents, scripts, triggers, and if/then logic. |

## Default

When user says "open in html" with no other qualifier, use `mkdocs-preview`.
That is the original mission: interactive websites for visual review of
complex topics.

## Naming convention for future renderers

Add a row to this table whenever you add a new renderer. Pick a short
kebab-case name (`reveal-deck`, `observable-notebook`, `d3-graph`, etc.).
Keep one renderer = one script under `scripts/`. Shared CSS lives in
`assets/`; shared utilities in `scripts/_lib/` if and when needed.

A new renderer must:

- Take a Markdown path as its first positional argument.
- Default output to `~/Desktop/` (per global rule `feedback_documents_to_desktop`).
- Support `--no-open` to skip opening the result.
- Preserve the source Markdown - never write back into the user's source file.
- Document its row here before merging.

## `system-map` data shape

The `system-map` renderer reads a fenced `system-map`, `json`, or `yaml` block
from Markdown. Use it when the user wants a visual layout like `arc-tables`
for non-database systems.

Required fields:

- `nodes`: cards to render. Each node should have `id`, `label`, `type`,
  `lane`, `status`, `summary`, optional `details`, and optional `source`.
- `edges`: relationships to render. Each edge should have `from`, `to`,
  optional `label`, and optional `type`.

Optional fields:

- `title`: page title.
- `subtitle`: short context line.
- `lanes`: ordered columns with `id` and `label`.

Supported node meanings include `agent`, `script`, `trigger`, `table`,
`service`, `condition`, `gate`, `data`, `project`, and `output`. Supported
edge meanings include `flow`, `trigger`, `condition`, and `failure`.
