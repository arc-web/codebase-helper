# Supabase Visual Reference Research

## Outcome

The best visual reference is the `arc-tables` database relationship output, not
the Supabase MCP presentation deck.

Use [schema_viz.html](file:///Users/home/ai/arc-tables/examples/sample-output/schema_viz.html)
as the primary reference for a future Codebase Helper `system-map` preset. Use
[leads_flow.html](file:///Users/home/ai/arc-tables/examples/sample-output/leads_flow.html)
as the lifecycle-flow reference. The Supabase MCP presentation at
[index.html](file:///Users/home/ai/platforms/supabase-mcp/docs/presentation/index.html)
is useful only for dark presentation polish, not for database relationship
layout.

## Search Scope

Pass 1 checked the known Supabase surfaces:

| Surface | Result |
| --- | --- |
| [supabase_agent](file:///Users/home/ai/agents/mcp/supabase_agent) | Current CLI-first agent docs and capabilities, but no HTML database-flow visual. |
| [supabase_mcp](file:///Users/home/ai/platforms/supabase_mcp) | Source-owned schema, relationship, and data-flow tools. No generated visual mockup. |
| [supabase-mcp](file:///Users/home/ai/platforms/supabase-mcp) | One presentation HTML candidate, visually polished but not a database-flow mockup. |

Pass 2 scanned `/Users/home/ai` for recent `.html`, `.md`, `.tsx`, `.ts`,
`.js`, `.svg`, and `.json` files whose names matched Supabase, database,
schema, relationship, flow, diagram, ERD, visual, mock, or presentation terms.
The strongest database-flow match was
[arc-tables](file:///Users/home/ai/arc-tables).

## Candidate Evidence

| Candidate | Modified | Git evidence | Purpose | Generated or source-owned | Fit |
| --- | --- | --- | --- | --- | --- |
| [arc-tables schema_viz.html](file:///Users/home/ai/arc-tables/examples/sample-output/schema_viz.html) | 2026-04-20 15:53:05 +0900 | `6319d35 feat: initial scaffold of arc-tables (v0.1)` | Full schema map with table cards, FK edges, clean versus legacy legend, hover affordances, and column-level relationship anchors. | Generated sample output backed by source templates. | Best visual match. |
| [arc-tables leads_flow.html](file:///Users/home/ai/arc-tables/examples/sample-output/leads_flow.html) | 2026-04-20 15:53:05 +0900 | `6319d35 feat: initial scaffold of arc-tables (v0.1)` | Lead to client lifecycle flow with cards, directional arrows, stage pills, shared-table context, and explanatory callouts. | Generated sample output backed by source templates. | Best lifecycle-flow match. |
| [arc-tables flow.ts](file:///Users/home/ai/arc-tables/src/render/templates/flow.ts) | 2026-04-20 15:49:50 +0900 | `6319d35 feat: initial scaffold of arc-tables (v0.1)` | Filters schema to selected `from`, `to`, and `through` tables, then renders through the map template. | Source-owned. | Best implementation source. |
| [arc-tables supabase.ts](file:///Users/home/ai/arc-tables/src/adapters/supabase.ts) | 2026-04-20 15:45:45 +0900 | `6319d35 feat: initial scaffold of arc-tables (v0.1)` | Supabase Management API adapter normalizing tables, columns, views, and foreign keys into a common schema model. | Source-owned. | Best Supabase provenance model. |
| [Supabase MCP presentation index.html](file:///Users/home/ai/platforms/supabase-mcp/docs/presentation/index.html) | 2026-04-18 22:54:20 +0900 | `dd79b18 docs: add presentation` | Four-slide animated dark presentation for Supabase MCP overview. | Source-owned single-file HTML. | Presentation shell only. |
| [knowledge_tools.ts](file:///Users/home/ai/platforms/supabase_mcp/src/tools/knowledge_tools.ts) | 2026-04-20 18:32:17 +0900 | `59f737a Fix MCP tools schema, knowledge manager, safety config, and tests` | Exposes `analyze_data_flow`, `get_relationship_map`, and table context tools. | Source-owned. | Strong data source, not visual. |
| [supabase_knowledge_manager.ts](file:///Users/home/ai/platforms/supabase_mcp/src/knowledge/supabase_knowledge_manager.ts) | 2026-04-20 18:32:51 +0900 | `59f737a Fix MCP tools schema, knowledge manager, safety config, and tests` | Reads public tables, policies, triggers, functions, and FK relationships for data-flow analysis. | Source-owned. | Strong relationship source, not visual. |

## Visual Notes

The `arc-tables` schema map gives Codebase Helper the strongest reusable visual
language:

| Pattern | Reuse in Codebase Helper |
| --- | --- |
| Dark dotted canvas | Good for dense system maps where white documentation pages flatten hierarchy. |
| Table cards | Use as source, adapter, service, table, or module cards with stable dimensions. |
| Column rows and FK highlights | Adapt to fields, methods, endpoints, config keys, or data contracts. |
| Curved animated connector paths | Use for dependencies, import flow, runtime calls, or data movement. |
| Clean versus legacy legend | Adapt to current, legacy, generated, risky, or manually verified states. |
| Hover focus and dimming | Useful for interactive inspection of one component and its neighbors. |

The `leads_flow` page adds patterns for workflow-specific pages:

| Pattern | Reuse in Codebase Helper |
| --- | --- |
| Horizontal lifecycle lanes | Use for request flow, data ingestion, CI, release, or client workflow stages. |
| Stage pills | Use for task states, table states, or pipeline steps. |
| Shared side cards | Use for common dependencies or single-source-of-truth objects. |
| Bottom callout panel | Use for evidence, caveats, cleanup notes, and next action. |

The Supabase MCP presentation is visually non-default and polished, but it is a
slide deck. Its reusable pieces are dark theme, gradient headline treatment,
short cards, code blocks, slide rhythm, and animated entry timing. It does not
show table relationships, ERD layout, lifecycle lanes, or source provenance.

Current Codebase Helper output uses Material for MkDocs plus
[artifacts.css](file:///Users/home/ai/agents/development/codebase_helper/docs/stylesheets/artifacts.css).
That is better for searchable long-form Markdown, but it lacks a graph canvas,
relationship edges, card coordinates, hover focus, and visual status legends.

## Recommendation

Add a new `system-map` preset rather than stretching `repo-walkthrough`.

`repo-walkthrough` should remain a text-first codebase tour. `system-map`
should render Markdown or a small structured sidecar into a database-flow style
page with:

| Element | Requirement |
| --- | --- |
| Cards | Stable-size cards for tables, modules, services, or artifacts. |
| Edges | Relationship lines between exact fields, paths, or APIs. |
| Lanes | Optional lifecycle lanes for workflows and state transitions. |
| Legend | Explicit current, legacy, generated, risky, and verified states. |
| Provenance | Source links for every card and relationship. |
| Fallback | Markdown table rendering when JavaScript is disabled or graph data is incomplete. |

Implementation should reuse the source ideas from
[arc-tables map.ts](file:///Users/home/ai/arc-tables/src/render/templates/map.ts),
[flow.ts](file:///Users/home/ai/arc-tables/src/render/templates/flow.ts),
[types.ts](file:///Users/home/ai/arc-tables/src/types.ts), and
[supabase.ts](file:///Users/home/ai/arc-tables/src/adapters/supabase.ts). The
sample HTML files should stay as visual references, not as copied generated
output.

## Verification

Evidence captured in this research pass:

| Check | Result |
| --- | --- |
| Last-month existence | All selected candidates above were modified on or after 2026-04-16. |
| Git provenance | `arc-tables`, `supabase-mcp`, and `supabase_mcp` each have commit evidence for the selected files. |
| Visual inspection | `schema_viz.html`, `leads_flow.html`, and the Supabase MCP presentation rendered locally with Playwright screenshots under `/tmp`. |
| Relevance | `schema_viz.html` and `leads_flow.html` are database-flow mockups. The Supabase MCP presentation is relevant to Supabase styling but not to database flow. |
| Codebase Helper comparison | Current Codebase Helper artifact mode is Markdown/MkDocs oriented and needs a separate `system-map` preset for graph-style pages. |

