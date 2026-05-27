# Agent Collaboration Lineage Template

Use this template when you want to explain how a user-agent collaboration moved
from an initial request to a shipped outcome. It is designed for training,
senior-agent review, and prompt-engineering retrospectives.

## Reuse Pattern

1. Replace the node labels with the real user asks, agent actions, friction
   points, and shipped outcomes.
2. Keep the lanes stable unless the story needs a different structure.
3. Preserve one or two friction nodes. The point is to show where the workflow
   improved, not to make the agent look perfect.
4. Render with:

```bash
python3 scripts/render_system_map.py docs/agent-lineage-template.md --output /tmp/agent-lineage-template.html --no-open
```

## Source Map

```system-map
{
  "title": "Agent Collaboration Lineage",
  "subtitle": "A reusable map for showing what the user needed, what the agent did, where the process drifted, and how the final feature shipped.",
  "lanes": [
    {"id": "user-need", "label": "User Need"},
    {"id": "agent-action", "label": "Agent Action"},
    {"id": "friction", "label": "Friction"},
    {"id": "resolution", "label": "Resolution"},
    {"id": "senior-review", "label": "Senior Review"}
  ],
  "nodes": [
    {
      "id": "initial-need",
      "label": "Initial Operating Need",
      "type": "trigger",
      "lane": "user-need",
      "status": "current",
      "summary": "The user states the behavior they need from the agent system.",
      "details": [
        "Capture the real workflow need in plain language.",
        "List required fields, systems, and handoff expectations."
      ]
    },
    {
      "id": "first-agent-action",
      "label": "First Agent Implementation",
      "type": "agent",
      "lane": "agent-action",
      "status": "draft",
      "summary": "The agent makes the first implementation choice.",
      "details": [
        "Identify what was correct.",
        "Identify what missed the user's operational target."
      ]
    },
    {
      "id": "user-correction",
      "label": "User Correction",
      "type": "condition",
      "lane": "user-need",
      "status": "current",
      "summary": "The user redirects the agent toward the actual source of truth.",
      "details": [
        "Use this node for repo, task, runtime, or workflow corrections.",
        "Quote the corrected target when it matters."
      ]
    },
    {
      "id": "scoped-build",
      "label": "Scoped Build",
      "type": "script",
      "lane": "agent-action",
      "status": "verified",
      "summary": "The agent implements the change in the owning workflow surface.",
      "details": [
        "Name files changed.",
        "Name tests or checks that protect the behavior."
      ]
    },
    {
      "id": "policy-or-gate",
      "label": "Policy Or Delivery Gate",
      "type": "gate",
      "lane": "friction",
      "status": "blocked",
      "summary": "The workflow hits a branch policy, missing check, approval gate, or tool limitation.",
      "details": [
        "Do not stop here.",
        "Describe the exact unmet requirement."
      ]
    },
    {
      "id": "user-escalation",
      "label": "User Escalation",
      "type": "trigger",
      "lane": "user-need",
      "status": "current",
      "summary": "The user clarifies that the agent must find the path through the gate.",
      "details": [
        "This is often the point where prompt pressure improves the result.",
        "Capture the difference between explanation and execution."
      ]
    },
    {
      "id": "gate-resolution",
      "label": "Gate Resolution",
      "type": "condition",
      "lane": "resolution",
      "status": "verified",
      "summary": "The agent satisfies the exact delivery condition with evidence.",
      "details": [
        "Examples: passing check, approval receipt, reviewed diff, or verified live state.",
        "Link the proof artifact when available."
      ]
    },
    {
      "id": "shipped-outcome",
      "label": "Shipped Outcome",
      "type": "output",
      "lane": "resolution",
      "status": "current",
      "summary": "The final behavior is live in the source-of-truth system.",
      "details": [
        "Record commit, PR, task, deployed URL, or runtime proof.",
        "State the effective rule in one sentence."
      ]
    },
    {
      "id": "review-packet",
      "label": "Senior Review Packet",
      "type": "output",
      "lane": "senior-review",
      "status": "current",
      "summary": "The collaboration is summarized for review and reuse.",
      "details": [
        "What went well.",
        "What went wrong.",
        "What prompt would have reached the outcome faster."
      ]
    },
    {
      "id": "next-system-change",
      "label": "Next System Change",
      "type": "project",
      "lane": "senior-review",
      "status": "draft",
      "summary": "The team decides whether the lesson should become automation, policy, or training material.",
      "details": [
        "Convert repeated failures into checks or templates.",
        "Keep one-off frustration as training context, not permanent process noise."
      ]
    }
  ],
  "edges": [
    {"from": "initial-need", "to": "first-agent-action", "label": "agent interprets", "type": "flow"},
    {"from": "first-agent-action", "to": "user-correction", "label": "missed target", "type": "failure"},
    {"from": "user-correction", "to": "scoped-build", "label": "correct source", "type": "flow"},
    {"from": "scoped-build", "to": "policy-or-gate", "label": "delivery attempt", "type": "condition"},
    {"from": "policy-or-gate", "to": "user-escalation", "label": "blocked too early", "type": "failure"},
    {"from": "user-escalation", "to": "gate-resolution", "label": "find exact gate", "type": "trigger"},
    {"from": "gate-resolution", "to": "shipped-outcome", "label": "merge or deploy", "type": "flow"},
    {"from": "shipped-outcome", "to": "review-packet", "label": "explain lineage", "type": "flow"},
    {"from": "review-packet", "to": "next-system-change", "label": "turn lesson into system", "type": "flow"}
  ]
}
```

## Case Study Notes

For the client-email-to-Discord rule, the shipped outcome was PR #64 in
`arc-web/google-ads-agent`: an approved client email send now requires a
Discord update with sender mailbox, all recipients, subject, purpose, concise
summary, notable details or commitments, and sent-message or thread link when
available.

The useful teaching point is not only that the rule shipped. The useful point
is that the user had to redirect the agent from broad config capture, through a
repo PR, through a missing GitHub check, and into a live source-of-truth change.
