# Handoff Sample

## Context

This sample proves the handoff preset can render headings, source paths, tables,
code blocks, and callouts through the same MkDocs workflow.

!!! note "State"
    Markdown remains the source of truth. The rendered page adds navigation,
    styling, and provenance metadata.

## Decisions

| Topic | Current choice | Evidence |
| --- | --- | --- |
| Renderer | MkDocs Material | `mkdocs.yml` |
| Entrypoint | Preview script | `scripts/preview_markdown.py` |

## Next Command

```bash
python3 scripts/preview_markdown.py smoke/fixtures/handoff-sample.md --preset handoff --build-only
```

<div class="artifact-meta" markdown="1">

**Preset:** Handoff
**Source:** `ai/agents/development/codebase_helper/smoke/fixtures/handoff-sample.md`
**Use:** Decision, context, and next-action packet for another agent or human.

</div>
