#!/usr/bin/env python3
"""
render_deck.py

Render a Markdown file into an animated HTML presentation via gsap-deck.

The Markdown source must contain a fenced ```json or ```deck block with
the deck JSON (slides, theme, etc.) as documented in the deck skill at
~/.claude/skills/deck/SKILL.md. If no JSON block is found a stub deck
is built from H1/H2 headings as a fallback.

Requires `gsap-deck` on PATH (installed at /opt/homebrew/bin/gsap-deck).

Usage:
    python3 scripts/render_deck.py PATH/TO/doc.md [--output OUT.html]
                                                  [--theme THEME]
                                                  [--no-open]
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

DESKTOP = Path.home() / "Desktop"

FENCE_RE = re.compile(r"```(?:json|deck)\s*\n(.*?)\n```", re.DOTALL)


def extract_deck_json(md_text: str) -> dict | None:
    m = FENCE_RE.search(md_text)
    if not m:
        return None
    try:
        return json.loads(m.group(1))
    except json.JSONDecodeError as e:
        print(f"error: deck JSON block found but invalid: {e}", file=sys.stderr)
        sys.exit(2)


def stub_deck_from_headings(md_text: str, title: str) -> dict:
    slides = [{"type": "title", "title": title, "subtitle": "Auto-generated stub deck"}]
    for line in md_text.splitlines():
        if line.startswith("# ") or line.startswith("## "):
            slides.append({"type": "section", "title": line.lstrip("# ").strip()})
    return {"title": title, "theme": "midnight", "slides": slides}


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("input", type=Path)
    p.add_argument("--output", type=Path, default=None)
    p.add_argument("--theme", default=None, help="Override theme name")
    p.add_argument("--no-open", action="store_true")
    args = p.parse_args()

    if not args.input.exists():
        print(f"error: input not found: {args.input}", file=sys.stderr)
        return 2

    gsap = shutil.which("gsap-deck")
    if not gsap:
        print("error: gsap-deck not on PATH. See ~/.claude/skills/deck/SKILL.md", file=sys.stderr)
        return 127

    md_text = args.input.read_text()
    deck = extract_deck_json(md_text) or stub_deck_from_headings(md_text, args.input.stem)
    if args.theme:
        deck["theme"] = args.theme

    out = args.output or (DESKTOP / f"{args.input.stem}-deck.html")
    out.parent.mkdir(parents=True, exist_ok=True)

    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as tf:
        json.dump(deck, tf)
        deck_json_path = Path(tf.name)

    cmd = [gsap, "build", str(deck_json_path), "-o", str(out)]
    if not args.no_open:
        cmd.append("--open")

    result = subprocess.run(cmd, capture_output=True, text=True)
    deck_json_path.unlink(missing_ok=True)

    if result.returncode != 0:
        print(result.stderr, file=sys.stderr)
        return result.returncode

    print(f"wrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
