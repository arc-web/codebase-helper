# Agent System Map Sample

```system-map
{
  "title": "Agent Runtime Flow",
  "subtitle": "A generalized visual layout for prompts, agents, scripts, triggers, data stores, approvals, and if/then branches.",
  "lanes": [
    {"id": "intake", "label": "Intake"},
    {"id": "reasoning", "label": "Reasoning"},
    {"id": "execution", "label": "Execution"},
    {"id": "verification", "label": "Verification"},
    {"id": "handoff", "label": "Handoff"}
  ],
  "nodes": [
    {
      "id": "user-request",
      "label": "User Request",
      "type": "trigger",
      "lane": "intake",
      "status": "current",
      "summary": "A natural-language request starts the workflow.",
      "details": ["Scope, constraints, and target artifact are captured.", "Relative dates and paths must be resolved."]
    },
    {
      "id": "router",
      "label": "Renderer Router",
      "type": "condition",
      "lane": "reasoning",
      "status": "verified",
      "summary": "Choose the named renderer or default MkDocs preview.",
      "details": ["open in html -> mkdocs-preview", "render with system-map -> this renderer", "standalone doc -> styled-doc"]
    },
    {
      "id": "system-map",
      "label": "System Map Renderer",
      "type": "script",
      "lane": "execution",
      "status": "generated",
      "summary": "Reads a Markdown-owned data block and renders a diagram.",
      "details": ["Nodes represent agents, scripts, tables, services, or decisions.", "Edges represent calls, triggers, data flow, or if/then branches."],
      "source": "scripts/render_system_map.py"
    },
    {
      "id": "approval",
      "label": "Human Approval",
      "type": "gate",
      "lane": "verification",
      "status": "current",
      "summary": "Required before risky live mutations or external publication.",
      "details": ["Can be omitted for local preview rendering.", "Must be explicit for production writes."]
    },
    {
      "id": "artifact",
      "label": "Interactive HTML Map",
      "type": "output",
      "lane": "handoff",
      "status": "current",
      "summary": "A dark graph canvas with cards, lanes, relationship edges, and hover focus.",
      "details": ["Useful for Supabase schemas, project flows, script chains, triggers, and agent collaboration maps."]
    }
  ],
  "edges": [
    {"from": "user-request", "to": "router", "label": "intent", "type": "trigger"},
    {"from": "router", "to": "system-map", "label": "if system-map", "type": "condition"},
    {"from": "system-map", "to": "approval", "label": "if live action", "type": "condition"},
    {"from": "system-map", "to": "artifact", "label": "render", "type": "flow"},
    {"from": "approval", "to": "artifact", "label": "approved path", "type": "flow"}
  ]
}
```

This sample is intentionally not Supabase-specific. The same shape can describe
database tables, Plane project plans, agent collaboration, shell scripts,
schedulers, webhooks, CLI calls, policy gates, and failure paths.
