#!/usr/bin/env python3
"""Render a Markdown-owned system map into an interactive HTML diagram."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from html import escape
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:  # pragma: no cover - JSON still works without PyYAML.
    yaml = None


DEFAULT_OUT_DIR = Path.home() / "Desktop"
CARD_W = 286
CARD_H = 176
LANE_W = 340
ROW_H = 226
PAD_X = 44
PAD_Y = 92


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Render a Markdown system-map block to HTML.")
    parser.add_argument("input", type=Path, help="Markdown file containing a fenced system-map block.")
    parser.add_argument("--output", type=Path, help="Output HTML path. Defaults to ~/Desktop/<title>-system-map.html.")
    parser.add_argument("--title", help="Override map title.")
    parser.add_argument("--no-open", action="store_true", help="Do not open the generated HTML.")
    return parser.parse_args()


def slugify(value: str) -> str:
    value = re.sub(r"[^\w\s-]", "", value).strip().lower()
    return re.sub(r"[-\s]+", "-", value)[:90] or "system-map"


def first_h1(markdown: str) -> str | None:
    for line in markdown.splitlines():
        match = re.match(r"^#\s+(.+?)\s*$", line)
        if match:
            return match.group(1).strip()
    return None


def extract_map_block(markdown: str) -> tuple[str, str]:
    pattern = re.compile(r"```(?P<kind>system-map|system_map|json|yaml|yml)\s*\n(?P<body>.*?)\n```", re.DOTALL)
    for match in pattern.finditer(markdown):
        kind = match.group("kind")
        body = match.group("body").strip()
        if kind in {"system-map", "system_map", "json", "yaml", "yml"}:
            return kind, body
    raise ValueError("No fenced `system-map`, `json`, or `yaml` block found.")


def load_map(markdown: str) -> dict[str, Any]:
    kind, body = extract_map_block(markdown)
    if kind in {"json", "system-map", "system_map"}:
        try:
            data = json.loads(body)
        except json.JSONDecodeError:
            if yaml is None:
                raise
            data = yaml.safe_load(body)
    else:
        if yaml is None:
            raise ValueError("YAML system maps require PyYAML. Use JSON instead.")
        data = yaml.safe_load(body)

    if not isinstance(data, dict):
        raise ValueError("System map block must decode to an object.")
    return data


def normalize_map(data: dict[str, Any], fallback_title: str) -> dict[str, Any]:
    nodes = data.get("nodes")
    edges = data.get("edges", [])
    if not isinstance(nodes, list) or not nodes:
        raise ValueError("System map requires a non-empty `nodes` array.")
    if not isinstance(edges, list):
        raise ValueError("System map `edges` must be an array.")

    normalized_nodes: list[dict[str, Any]] = []
    seen: set[str] = set()
    for index, node in enumerate(nodes):
        if not isinstance(node, dict):
            raise ValueError("Each node must be an object.")
        node_id = str(node.get("id") or f"node-{index + 1}")
        if node_id in seen:
            raise ValueError(f"Duplicate node id: {node_id}")
        seen.add(node_id)
        normalized_nodes.append(
            {
                "id": node_id,
                "label": str(node.get("label") or node_id),
                "type": str(node.get("type") or "component"),
                "lane": str(node.get("lane") or "system"),
                "status": str(node.get("status") or "current"),
                "summary": str(node.get("summary") or ""),
                "details": list(node.get("details") or []),
                "source": str(node.get("source") or ""),
            }
        )

    normalized_edges: list[dict[str, Any]] = []
    for edge in edges:
        if not isinstance(edge, dict):
            raise ValueError("Each edge must be an object.")
        source = str(edge.get("from") or "")
        target = str(edge.get("to") or "")
        if source not in seen or target not in seen:
            raise ValueError(f"Edge references unknown node: {source} -> {target}")
        normalized_edges.append(
            {
                "from": source,
                "to": target,
                "label": str(edge.get("label") or ""),
                "type": str(edge.get("type") or "flow"),
            }
        )

    lanes = data.get("lanes")
    normalized_lanes: list[dict[str, str]] = []
    if isinstance(lanes, list) and lanes:
        for lane in lanes:
            if isinstance(lane, dict):
                lane_id = str(lane.get("id") or lane.get("label") or "lane")
                normalized_lanes.append({"id": lane_id, "label": str(lane.get("label") or lane_id)})
    else:
        for lane_id in dict.fromkeys(node["lane"] for node in normalized_nodes):
            normalized_lanes.append({"id": lane_id, "label": lane_id.replace("-", " ").title()})

    lane_ids = {lane["id"] for lane in normalized_lanes}
    for node in normalized_nodes:
        if node["lane"] not in lane_ids:
            normalized_lanes.append({"id": node["lane"], "label": node["lane"].replace("-", " ").title()})
            lane_ids.add(node["lane"])

    return {
        "title": str(data.get("title") or fallback_title),
        "subtitle": str(data.get("subtitle") or ""),
        "lanes": normalized_lanes,
        "nodes": normalized_nodes,
        "edges": normalized_edges,
    }


def compute_positions(map_data: dict[str, Any]) -> dict[str, dict[str, int]]:
    lanes = [lane["id"] for lane in map_data["lanes"]]
    lane_index = {lane_id: index for index, lane_id in enumerate(lanes)}
    row_counts: dict[str, int] = {lane_id: 0 for lane_id in lanes}
    positions: dict[str, dict[str, int]] = {}
    for node in map_data["nodes"]:
        lane = node["lane"]
        row = row_counts[lane]
        row_counts[lane] += 1
        positions[node["id"]] = {
            "x": PAD_X + lane_index[lane] * LANE_W,
            "y": PAD_Y + row * ROW_H,
        }
    return positions


def css(width: int, height: int) -> str:
    return f"""
:root {{
  color-scheme: dark;
  --bg: #0b1020;
  --panel: #111827;
  --panel-2: #172033;
  --text: #e5edf7;
  --muted: #94a3b8;
  --line: rgba(148, 163, 184, 0.34);
  --cyan: #38bdf8;
  --green: #34d399;
  --amber: #f59e0b;
  --rose: #fb7185;
  --violet: #a78bfa;
}}
* {{ box-sizing: border-box; }}
body {{
  margin: 0;
  min-height: 100vh;
  font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
  background:
    radial-gradient(circle at top left, rgba(56, 189, 248, 0.13), transparent 30rem),
    linear-gradient(135deg, #080c18 0%, #0f172a 58%, #111827 100%);
  color: var(--text);
}}
header {{
  max-width: {width}px;
  margin: 0 auto;
  padding: 34px 44px 14px;
}}
h1 {{
  margin: 0 0 8px;
  font-size: 32px;
  font-weight: 760;
  letter-spacing: 0;
}}
.subtitle {{
  margin: 0;
  color: var(--muted);
  font-size: 15px;
  line-height: 1.6;
  max-width: 920px;
}}
.canvas-wrap {{
  overflow: auto;
  padding: 12px 22px 42px;
}}
#canvas {{
  position: relative;
  width: {width}px;
  height: {height}px;
  margin: 0 auto;
  border: 1px solid rgba(148, 163, 184, 0.22);
  border-radius: 18px;
  background-color: rgba(15, 23, 42, 0.74);
  background-image: radial-gradient(rgba(148, 163, 184, 0.22) 1px, transparent 1px);
  background-size: 20px 20px;
  box-shadow: 0 24px 80px rgba(0, 0, 0, 0.34);
}}
#edges {{
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
  overflow: visible;
}}
.lane {{
  position: absolute;
  top: 24px;
  height: calc(100% - 48px);
  width: {CARD_W}px;
  border-left: 1px solid rgba(148, 163, 184, 0.14);
  border-right: 1px solid rgba(148, 163, 184, 0.08);
}}
.lane-title {{
  position: absolute;
  top: 44px;
  color: #cbd5e1;
  font-size: 12px;
  font-weight: 780;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}}
.node {{
  position: absolute;
  width: {CARD_W}px;
  min-height: {CARD_H}px;
  padding: 15px 16px 14px;
  border: 1px solid rgba(148, 163, 184, 0.26);
  border-radius: 14px;
  background: linear-gradient(180deg, rgba(30, 41, 59, 0.94), rgba(15, 23, 42, 0.96));
  box-shadow: 0 14px 36px rgba(0, 0, 0, 0.26);
  transition: opacity 140ms ease, border-color 140ms ease, transform 140ms ease;
}}
.node:hover {{
  transform: translateY(-2px);
  border-color: rgba(56, 189, 248, 0.72);
}}
.node.dim {{ opacity: 0.34; }}
.node.active {{ border-color: rgba(56, 189, 248, 0.9); }}
.node-top {{
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 10px;
}}
.type {{
  color: #dbeafe;
  border: 1px solid rgba(148, 163, 184, 0.28);
  border-radius: 999px;
  padding: 4px 8px;
  font-size: 11px;
  font-weight: 740;
  text-transform: uppercase;
}}
.status {{
  border-radius: 999px;
  padding: 4px 8px;
  font-size: 11px;
  font-weight: 720;
  color: #07111f;
  background: var(--green);
}}
.status.risky {{ background: var(--amber); }}
.status.legacy {{ background: var(--rose); }}
.status.generated {{ background: var(--violet); }}
.status.blocked {{ background: #f87171; }}
.label {{
  font-size: 18px;
  line-height: 1.18;
  font-weight: 780;
  margin: 0 0 8px;
}}
.summary {{
  color: #cbd5e1;
  font-size: 13px;
  line-height: 1.45;
  margin: 0 0 10px;
}}
.details {{
  margin: 0;
  padding: 0;
  list-style: none;
  color: var(--muted);
  font-size: 12px;
  line-height: 1.42;
}}
.details li {{ margin-top: 4px; }}
.source {{
  display: block;
  margin-top: 10px;
  color: #7dd3fc;
  font-size: 11px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}}
path.edge {{
  fill: none;
  stroke: rgba(125, 211, 252, 0.66);
  stroke-width: 2.4;
  stroke-linecap: round;
}}
path.edge.condition {{ stroke: var(--amber); stroke-dasharray: 7 7; }}
path.edge.trigger {{ stroke: var(--green); }}
path.edge.failure {{ stroke: var(--rose); stroke-dasharray: 4 7; }}
text.edge-label {{
  fill: #dbeafe;
  font-size: 12px;
  paint-order: stroke;
  stroke: rgba(8, 12, 24, 0.9);
  stroke-width: 4px;
  stroke-linejoin: round;
}}
.legend {{
  max-width: {width}px;
  margin: 0 auto 34px;
  padding: 0 44px;
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  color: var(--muted);
  font-size: 12px;
}}
.legend span {{
  border: 1px solid rgba(148, 163, 184, 0.22);
  border-radius: 999px;
  padding: 7px 10px;
  background: rgba(15, 23, 42, 0.76);
}}
"""


def render_node(node: dict[str, Any], pos: dict[str, int]) -> str:
    details = "\n".join(f"<li>{escape(str(item))}</li>" for item in node["details"][:4])
    detail_html = f'<ul class="details">{details}</ul>' if details else ""
    source_html = f'<span class="source">{escape(node["source"])}</span>' if node["source"] else ""
    status_class = re.sub(r"[^a-z0-9-]+", "-", node["status"].lower())
    return f"""
<article class="node" id="node-{escape(node['id'])}" data-node="{escape(node['id'])}" style="left:{pos['x']}px; top:{pos['y']}px;">
  <div class="node-top">
    <span class="type">{escape(node['type'])}</span>
    <span class="status {escape(status_class)}">{escape(node['status'])}</span>
  </div>
  <h2 class="label">{escape(node['label'])}</h2>
  <p class="summary">{escape(node['summary'])}</p>
  {detail_html}
  {source_html}
</article>"""


def render_html(map_data: dict[str, Any]) -> str:
    positions = compute_positions(map_data)
    max_rows = 1
    for lane in map_data["lanes"]:
        count = len([node for node in map_data["nodes"] if node["lane"] == lane["id"]])
        max_rows = max(max_rows, count)
    width = PAD_X * 2 + max(1, len(map_data["lanes"])) * LANE_W - (LANE_W - CARD_W)
    height = PAD_Y + max_rows * ROW_H + 86

    lanes = []
    for index, lane in enumerate(map_data["lanes"]):
        left = PAD_X + index * LANE_W
        lanes.append(f'<section class="lane" style="left:{left}px;"></section>')
        lanes.append(f'<div class="lane-title" style="left:{left}px;">{escape(lane["label"])}</div>')

    nodes = "\n".join(render_node(node, positions[node["id"]]) for node in map_data["nodes"])
    edge_data = json.dumps(map_data["edges"])
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{escape(map_data['title'])}</title>
<style>{css(width, height)}</style>
</head>
<body>
<header>
  <h1>{escape(map_data['title'])}</h1>
  <p class="subtitle">{escape(map_data['subtitle'])}</p>
</header>
<main class="canvas-wrap">
  <div id="canvas">
    <svg id="edges" viewBox="0 0 {width} {height}" aria-hidden="true"></svg>
    {''.join(lanes)}
    {nodes}
  </div>
</main>
<aside class="legend">
  <span>Solid edge: direct flow</span>
  <span>Dashed amber edge: condition or if/then branch</span>
  <span>Cards: agents, scripts, triggers, data, decisions, services, tables</span>
  <span>Hover: focus a component and its neighbors</span>
</aside>
<script>
const EDGES = {edge_data};
const svg = document.getElementById("edges");
const canvas = document.getElementById("canvas");
function center(id) {{
  const el = document.querySelector('[data-node="' + CSS.escape(id) + '"]');
  const c = canvas.getBoundingClientRect();
  const r = el.getBoundingClientRect();
  return {{ x: r.left - c.left + r.width / 2, y: r.top - c.top + r.height / 2, el }};
}}
function drawEdges() {{
  svg.innerHTML = "";
  EDGES.forEach((edge, index) => {{
    const a = center(edge.from);
    const b = center(edge.to);
    const dx = Math.max(90, Math.abs(b.x - a.x) * 0.44);
    const dir = a.x <= b.x ? 1 : -1;
    const path = document.createElementNS("http://www.w3.org/2000/svg", "path");
    path.setAttribute("class", "edge " + (edge.type || "flow"));
    path.setAttribute("id", "edge-" + index);
    path.setAttribute("d", "M" + a.x + "," + a.y + " C" + (a.x + dir * dx) + "," + a.y + " " + (b.x - dir * dx) + "," + b.y + " " + b.x + "," + b.y);
    svg.appendChild(path);
    if (edge.label) {{
      const label = document.createElementNS("http://www.w3.org/2000/svg", "text");
      label.setAttribute("class", "edge-label");
      label.setAttribute("x", String((a.x + b.x) / 2));
      label.setAttribute("y", String((a.y + b.y) / 2 - 10));
      label.setAttribute("text-anchor", "middle");
      label.textContent = edge.label;
      svg.appendChild(label);
    }}
  }});
}}
function focusNode(id) {{
  const neighbors = new Set([id]);
  EDGES.forEach((edge) => {{
    if (edge.from === id) neighbors.add(edge.to);
    if (edge.to === id) neighbors.add(edge.from);
  }});
  document.querySelectorAll(".node").forEach((node) => {{
    const active = neighbors.has(node.dataset.node);
    node.classList.toggle("dim", !active);
    node.classList.toggle("active", node.dataset.node === id);
  }});
}}
document.querySelectorAll(".node").forEach((node) => {{
  node.addEventListener("mouseenter", () => focusNode(node.dataset.node));
}});
canvas.addEventListener("mouseleave", () => {{
  document.querySelectorAll(".node").forEach((node) => node.classList.remove("dim", "active"));
}});
requestAnimationFrame(drawEdges);
window.addEventListener("resize", drawEdges);
</script>
</body>
</html>
"""


def main() -> int:
    args = parse_args()
    source = args.input.expanduser().resolve()
    if not source.is_file():
        print(f"ERROR: input not found: {source}", file=sys.stderr)
        return 1

    markdown = source.read_text(encoding="utf-8")
    fallback_title = args.title or first_h1(markdown) or source.stem.replace("-", " ").title()
    map_data = normalize_map(load_map(markdown), fallback_title)
    if args.title:
        map_data["title"] = args.title

    output = args.output.expanduser().resolve() if args.output else DEFAULT_OUT_DIR / f"{slugify(map_data['title'])}-system-map.html"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(render_html(map_data), encoding="utf-8")
    print(f"html={output}")
    if not args.no_open:
        subprocess.run(["open", str(output)], check=False)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
