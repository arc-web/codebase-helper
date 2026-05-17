#!/usr/bin/env python3
"""
render_graphify.py

Render a Markdown file (or directory of docs) into an interactive HTML
knowledge graph via the graphify CLI.

Graphify extracts entities and relationships, builds clustered
communities, and emits an HTML graph + GRAPH_REPORT.md + graph.json.
This wrapper invokes the graphify CLI, then surfaces the resulting
graph.html on the Desktop.

Requires `graphify` on PATH (see ~/.claude/skills/graphify/SKILL.md).

Usage:
    python3 scripts/render_graphify.py PATH/TO/doc.md [--output-dir DIR]
                                                      [--no-open]
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

DESKTOP = Path.home() / "Desktop"


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("input", type=Path, help="Markdown file or directory")
    p.add_argument(
        "--output-dir",
        type=Path,
        default=None,
        help="graphify-out directory (default: ~/Desktop/<stem>-graphify)",
    )
    p.add_argument("--no-open", action="store_true")
    args = p.parse_args()

    if not args.input.exists():
        print(f"error: input not found: {args.input}", file=sys.stderr)
        return 2

    graphify = shutil.which("graphify")
    if not graphify:
        print(
            "error: graphify not on PATH. Install per ~/.claude/skills/graphify/SKILL.md",
            file=sys.stderr,
        )
        return 127

    stem = args.input.stem if args.input.is_file() else args.input.name
    out_dir = args.output_dir or (DESKTOP / f"{stem}-graphify")
    out_dir.mkdir(parents=True, exist_ok=True)

    cmd = [graphify, str(args.input), "--output", str(out_dir)]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(result.stderr, file=sys.stderr)
        return result.returncode

    graph_html = out_dir / "graph.html"
    if not graph_html.exists():
        print(f"warning: graphify did not produce graph.html in {out_dir}", file=sys.stderr)
        print(result.stdout)
        return 1

    print(f"wrote {graph_html}")

    if not args.no_open:
        subprocess.run(["open", str(graph_html)])

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
