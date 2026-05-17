#!/usr/bin/env python3
"""
render_pandoc.py

Generic one-shot Markdown -> single-file HTML via pandoc. Standalone
output with embedded resources so the file is fully portable.

Use when you want a plain, no-framework HTML rendering of a Markdown
file. For themed previews use mkdocs-preview; for styled finished docs
use styled-doc.

Usage:
    python3 scripts/render_pandoc.py PATH/TO/doc.md [--output OUT.html]
                                                    [--title "Doc Title"]
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
    p.add_argument("input", type=Path, help="Source Markdown file")
    p.add_argument("--output", type=Path, default=None, help="Output HTML path (default: ~/Desktop/<stem>.html)")
    p.add_argument("--title", default=None, help="Document title")
    p.add_argument("--no-open", action="store_true", help="Do not open the result")
    args = p.parse_args()

    if not args.input.exists():
        print(f"error: input not found: {args.input}", file=sys.stderr)
        return 2

    pandoc = shutil.which("pandoc")
    if not pandoc:
        print("error: pandoc not on PATH. Install with: brew install pandoc", file=sys.stderr)
        return 127

    out = args.output or (DESKTOP / f"{args.input.stem}.html")
    out.parent.mkdir(parents=True, exist_ok=True)

    cmd = [
        pandoc,
        str(args.input),
        "-f", "gfm",
        "-t", "html5",
        "--standalone",
        "--embed-resources",
        "-o", str(out),
    ]
    if args.title:
        cmd += ["--metadata", f"title={args.title}"]

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(result.stderr, file=sys.stderr)
        return result.returncode

    print(f"wrote {out}")

    if not args.no_open:
        subprocess.run(["open", str(out)])

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
