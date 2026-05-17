#!/Users/home/.local/pipx/venvs/mkdocs-material/bin/python
"""
render_styled.py

Render a Markdown file into a standalone styled HTML doc (optionally PDF)
matching the aesthetic of client-facing review docs produced by
~/ai/agents/ppc/google_ads_agent/shared/presentation/.

Why this exists: codebase_helper's preview_markdown.py (MkDocs Material)
is great for searchable preview sites but produces theme chrome that
doesn't read like a finished document. render_styled.py produces a
single self-contained file that does.

CSS source of truth:
  - page_break_rules.css + section_header.css vendored from
    ~/ai/agents/ppc/google_ads_agent/shared/presentation/
  - base.css authored locally for typography + variables

Usage:
    python3 scripts/render_styled.py PATH/TO/doc.md [--output OUT.html]
                                                   [--title "Doc Title"]
                                                   [--subtitle "..."]
                                                   [--pdf]
                                                   [--no-open]

PDF requires Chrome at /Applications/Google Chrome.app.
"""

from __future__ import annotations

import argparse
import os
import re
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"
CHROME_BIN = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

PDF_FLAGS = [
    "--headless=new",
    "--print-to-pdf-no-header",
    "--no-pdf-header-footer",
    "--no-margins",
    "--disable-gpu",
    "--run-all-compositor-stages-before-draw",
]

DEFAULT_OUT_DIR = Path.home() / "Desktop"


def reexec_with_mkdocs_python() -> None:
    mkdocs = shutil.which("mkdocs")
    if not mkdocs:
        return

    first_line = Path(mkdocs).read_text(encoding="utf-8", errors="ignore").splitlines()[0]
    if not first_line.startswith("#!"):
        return

    interpreter = Path(first_line[2:].strip())
    if not interpreter.is_file() or interpreter == Path(sys.executable):
        return

    os.execv(interpreter.as_posix(), [interpreter.as_posix(), __file__, *sys.argv[1:]])


def import_markdown_module():
    try:
        import markdown as markdown_module

        return markdown_module
    except ImportError:
        reexec_with_mkdocs_python()
        print(
            "ERROR: Python package `markdown` is not available and the MkDocs "
            "runtime could not be reused.",
            file=sys.stderr,
        )
        sys.exit(1)


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Render markdown to styled HTML/PDF.")
    p.add_argument("input", type=Path, help="Markdown source file")
    p.add_argument("--output", type=Path, help="Output HTML path (default: ~/Desktop/<slug>.html)")
    p.add_argument("--title", help="Override doc title (default: first H1 or filename)")
    p.add_argument("--subtitle", help="Optional subtitle below the title")
    p.add_argument("--pdf", action="store_true", help="Also export PDF via Chrome headless")
    p.add_argument("--no-open", action="store_true", help="Do not open the output in browser")
    return p.parse_args()


def slugify(value: str) -> str:
    value = re.sub(r"[^\w\s-]", "", value).strip().lower()
    return re.sub(r"[-\s]+", "-", value)[:80] or "doc"


def extract_first_h1(text: str) -> str | None:
    for line in text.splitlines():
        m = re.match(r"^#\s+(.+?)\s*$", line)
        if m:
            return m.group(1).strip()
    return None


def strip_first_h1(text: str) -> str:
    """Remove the first H1 line (we render it as doc title instead)."""
    lines = text.splitlines()
    for i, line in enumerate(lines):
        if re.match(r"^#\s+", line):
            del lines[i]
            # Drop any immediately-following blank line
            if i < len(lines) and lines[i].strip() == "":
                del lines[i]
            break
    return "\n".join(lines)


def render_markdown(text: str) -> str:
    markdown_module = import_markdown_module()
    return markdown_module.markdown(
        text,
        extensions=[
            "extra",
            "tables",
            "fenced_code",
            "sane_lists",
            "toc",
        ],
        output_format="html5",
    )


def load_css() -> str:
    parts = []
    for name in ("base.css", "section_header.css", "page_break_rules.css"):
        path = ASSETS / name
        if not path.is_file():
            print(f"ERROR: missing CSS asset {path}", file=sys.stderr)
            sys.exit(1)
        parts.append(f"/* === {name} === */\n" + path.read_text(encoding="utf-8"))
    return "\n\n".join(parts)


def build_html(*, title: str, subtitle: str | None, body_html: str, source_label: str) -> str:
    today = datetime.now().strftime("%Y-%m-%d")
    css = load_css()
    sub = f'<p class="doc-subtitle">{subtitle}</p>' if subtitle else ""
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<style>
{css}
</style>
</head>
<body>
<div class="doc-meta">
  <span>{source_label}</span>
  <span>{today}</span>
</div>
<h1 class="doc-title">{title}</h1>
{sub}
{body_html}
</body>
</html>
"""


def export_pdf(html_path: Path, pdf_path: Path) -> Path:
    if not shutil.which(CHROME_BIN) and not Path(CHROME_BIN).exists():
        print(f"ERROR: Chrome not found at {CHROME_BIN}", file=sys.stderr)
        sys.exit(1)
    pdf_path.parent.mkdir(parents=True, exist_ok=True)
    cmd = [CHROME_BIN, f"--print-to-pdf={pdf_path}", *PDF_FLAGS, f"file://{html_path}"]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
    if r.returncode != 0 or not pdf_path.is_file():
        print(f"ERROR: chrome exit {r.returncode}\n{r.stderr}", file=sys.stderr)
        sys.exit(1)
    return pdf_path


def main() -> int:
    args = parse_args()

    src = args.input.resolve()
    if not src.is_file():
        print(f"ERROR: input not found: {src}", file=sys.stderr)
        return 1

    raw = src.read_text(encoding="utf-8")

    first_h1 = extract_first_h1(raw)
    title = args.title or first_h1 or src.stem.replace("_", " ").title()

    body_md = strip_first_h1(raw) if first_h1 and not args.title else raw
    body_html = render_markdown(body_md)

    html = build_html(
        title=title,
        subtitle=args.subtitle,
        body_html=body_html,
        source_label=src.name,
    )

    out = args.output.resolve() if args.output else DEFAULT_OUT_DIR / f"{slugify(title)}.html"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(html, encoding="utf-8")
    print(f"html={out}")

    if args.pdf:
        pdf_out = out.with_suffix(".pdf")
        export_pdf(out, pdf_out)
        print(f"pdf={pdf_out}")

    if not args.no_open:
        subprocess.run(["open", str(out)], check=False)

    return 0


if __name__ == "__main__":
    sys.exit(main())
