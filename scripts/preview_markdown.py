#!/usr/bin/env python3
"""Render a Markdown file through the repo-local MkDocs preview surface."""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import socket
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

import yaml


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DOCS_DIR = PROJECT_ROOT / "docs"
MKDOCS_CONFIG = PROJECT_ROOT / "mkdocs.yml"
CACHE_DIR = PROJECT_ROOT / ".cache"
GALLERY_PATH = DOCS_DIR / "artifacts" / "index.md"
MANIFEST_PATH = CACHE_DIR / "artifacts.json"
PRESETS = {
    "note": {
        "label": "Note",
        "summary": "Fast Markdown preview with source provenance.",
    },
    "handoff": {
        "label": "Handoff",
        "summary": "Decision, context, and next-action packet for another agent or human.",
    },
    "repo-walkthrough": {
        "label": "Repo Walkthrough",
        "summary": "Navigable codebase tour with exact paths and commands.",
    },
    "implementation-summary": {
        "label": "Implementation Summary",
        "summary": "Change summary with affected files, commands, and verification evidence.",
    },
    "review-packet": {
        "label": "Review Packet",
        "summary": "Review-ready findings, risks, and evidence for sign-off.",
    },
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Copy Markdown into docs, update nav, build, serve, and open it."
    )
    parser.add_argument("source", type=Path, help="Markdown file to preview.")
    parser.add_argument("--title", help="Navigation title. Defaults to the first H1.")
    parser.add_argument("--slug", help="Destination slug under docs/. Defaults to source stem.")
    parser.add_argument(
        "--preset",
        choices=sorted(PRESETS),
        default="note",
        help="Artifact preset metadata and gallery grouping.",
    )
    parser.add_argument("--port", type=int, default=8012, help="Preferred localhost port.")
    parser.add_argument("--build-only", action="store_true", help="Build without serving or opening.")
    parser.add_argument("--no-open", action="store_true", help="Do not call macOS open.")
    parser.add_argument(
        "--skip-gallery",
        action="store_true",
        help="Do not update docs/artifacts/index.md or the artifact manifest.",
    )
    parser.add_argument(
        "--skip-checks",
        action="store_true",
        help="Skip static checks after MkDocs build.",
    )
    parser.add_argument(
        "--allow-dirty-baseline",
        action="store_true",
        help="Allow preview mutations when the Git worktree is already dirty.",
    )
    return parser.parse_args()


def slugify(value: str) -> str:
    slug = re.sub(r"[^A-Za-z0-9]+", "-", value.strip()).strip("-").lower()
    return slug or "preview"


def first_h1(markdown: str) -> str | None:
    for line in markdown.splitlines():
        if line.startswith("# "):
            return line[2:].strip()
    return None


def source_label(source: Path) -> str:
    try:
        return source.resolve().relative_to(Path.home()).as_posix()
    except ValueError:
        return source.resolve().as_posix()


def artifact_header(source: Path, preset: str) -> str:
    preset_info = PRESETS[preset]
    return "\n".join(
        [
            '<div class="artifact-meta" markdown="1">',
            "",
            f"**Preset:** {preset_info['label']}",
            f"**Source:** `{source_label(source)}`",
            f"**Use:** {preset_info['summary']}",
            "",
            "</div>",
            "",
        ]
    )


def prepare_markdown(markdown: str, source: Path, preset: str) -> str:
    header = artifact_header(source, preset)
    return f"{markdown.rstrip()}\n\n{header}"


def copy_source(source: Path, slug: str | None, preset: str) -> tuple[Path, str]:
    source = source.expanduser().resolve()
    if not source.exists():
        raise FileNotFoundError(f"Markdown source does not exist: {source}")
    if source.suffix.lower() != ".md":
        raise ValueError(f"Expected a .md file, got: {source}")

    markdown = source.read_text(encoding="utf-8")
    destination_name = f"{slugify(slug or source.stem)}.md"
    destination = DOCS_DIR / destination_name
    DOCS_DIR.mkdir(parents=True, exist_ok=True)

    if source != destination.resolve():
        destination.write_text(prepare_markdown(markdown, source, preset), encoding="utf-8")

    return destination, markdown


def load_config() -> dict:
    with MKDOCS_CONFIG.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle) or {}
    if not isinstance(data, dict):
        raise ValueError(f"Expected mapping in {MKDOCS_CONFIG}")
    return data


def nav_entry_path(entry: object) -> str | None:
    if isinstance(entry, str):
        return entry
    if isinstance(entry, dict):
        for value in entry.values():
            if isinstance(value, str):
                return value
    return None


def update_nav(destination: Path, title: str) -> None:
    config = load_config()
    nav = config.setdefault("nav", [])
    if not isinstance(nav, list):
        raise ValueError("mkdocs.yml nav must be a list")

    rel_path = destination.relative_to(DOCS_DIR).as_posix()
    for index, entry in enumerate(nav):
        if nav_entry_path(entry) == rel_path:
            nav[index] = {title: rel_path}
            break
    else:
        nav.append({title: rel_path})

    with MKDOCS_CONFIG.open("w", encoding="utf-8") as handle:
        yaml.safe_dump(config, handle, sort_keys=False, allow_unicode=True)


def run_build() -> None:
    subprocess.run(["mkdocs", "build", "--strict"], cwd=PROJECT_ROOT, check=True)


def site_path_for_doc(destination: Path) -> Path:
    rel_path = destination.relative_to(DOCS_DIR)
    if rel_path.name == "index.md":
        return PROJECT_ROOT / "site" / rel_path.parent / "index.html"
    return PROJECT_ROOT / "site" / rel_path.with_suffix("") / "index.html"


def preview_path_for_doc(destination: Path) -> str:
    rel_path = destination.relative_to(DOCS_DIR)
    if rel_path.name == "index.md":
        return rel_path.parent.as_posix().strip("/")
    return rel_path.with_suffix("").as_posix().strip("/")


def iter_markdown_links(markdown: str) -> list[str]:
    links: list[str] = []
    for match in re.finditer(r"(?<!!)\[[^\]]+\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)", markdown):
        links.append(match.group(1))
    return links


def is_external_link(target: str) -> bool:
    return bool(re.match(r"^[a-z][a-z0-9+.-]*:", target, flags=re.IGNORECASE))


def run_static_checks(source: Path, markdown: str, destination: Path, title: str) -> None:
    errors: list[str] = []
    if not title.strip():
        errors.append("missing page title")

    rendered = site_path_for_doc(destination)
    if not rendered.is_file():
        errors.append(f"missing generated HTML: {rendered}")
    elif rendered.stat().st_size < 500:
        errors.append(f"generated HTML is unexpectedly small: {rendered}")
    else:
        html = rendered.read_text(encoding="utf-8", errors="replace")
        if title not in html:
            errors.append(f"generated HTML does not contain title: {title}")

    for target in iter_markdown_links(markdown):
        target = target.split("#", 1)[0]
        if not target or target.startswith("#") or is_external_link(target):
            continue
        candidate = Path(target).expanduser()
        if not candidate.is_absolute():
            candidate = source.parent / candidate
        if not candidate.exists():
            errors.append(f"broken source link in {source}: {target}")

    if errors:
        joined = "\n".join(f"- {error}" for error in errors)
        raise RuntimeError(f"static checks failed:\n{joined}")


def read_manifest() -> list[dict[str, str]]:
    if not MANIFEST_PATH.exists():
        return []
    data = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    if not isinstance(data, list):
        return []
    return [normalize_manifest_item(item) for item in data if isinstance(item, dict)]


def normalize_manifest_item(item: dict[str, str]) -> dict[str, str]:
    normalized = dict(item)
    source = normalized.get("source")
    docs_page = normalized.get("docs_page")
    if not source or not docs_page:
        return normalized

    source_path = Path(source)
    try:
        source_path.relative_to(PROJECT_ROOT)
    except ValueError:
        return normalized

    if source_path.exists():
        return normalized

    docs_source = DOCS_DIR / docs_page
    if docs_source.exists():
        normalized["source"] = docs_source.resolve().as_posix()
    return normalized


def write_manifest(items: list[dict[str, str]]) -> None:
    CACHE_DIR.mkdir(exist_ok=True)
    MANIFEST_PATH.write_text(
        json.dumps(items, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def update_gallery(source: Path, destination: Path, title: str, preset: str) -> None:
    rel_path = destination.relative_to(DOCS_DIR).as_posix()
    items = [item for item in read_manifest() if item.get("docs_page") != rel_path]
    items.append(
        {
            "title": title,
            "preset": preset,
            "docs_page": rel_path,
            "source": source.resolve().as_posix(),
        }
    )
    items.sort(key=lambda item: (item.get("preset", ""), item.get("title", "")))
    write_manifest(items)

    GALLERY_PATH.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Artifact Gallery",
        "",
        "Rendered Markdown artifacts tracked by `scripts/preview_markdown.py`.",
        "",
        "| Preset | Artifact | Source Markdown |",
        "| --- | --- | --- |",
    ]
    for item in items:
        page = item.get("docs_page", "")
        label = item.get("title", page)
        if page:
            page_link = f"[{label}](../{page})"
        else:
            page_link = label
        lines.append(
            f"| {PRESETS.get(item.get('preset', ''), {}).get('label', item.get('preset', ''))} "
            f"| {page_link} | `{source_label(Path(item.get('source', '')) if item.get('source') else Path('.'))}` |"
        )
    GALLERY_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


def dirty_worktree_entries() -> list[str]:
    result = subprocess.run(
        ["git", "status", "--porcelain=v1", "--untracked-files=all"],
        cwd=PROJECT_ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return [line for line in result.stdout.splitlines() if line.strip()]


def assert_clean_baseline(allow_dirty_baseline: bool) -> None:
    if allow_dirty_baseline:
        return

    dirty_entries = dirty_worktree_entries()
    if not dirty_entries:
        return

    dirty_files = "\n".join(f"- {entry}" for entry in dirty_entries)
    raise RuntimeError(
        "dirty baseline detected; refusing to run a mutating Markdown preview.\n"
        "This command can update `mkdocs.yml`, "
        "`docs/artifacts/index.md`, `.cache/artifacts.json`, and copied pages "
        "under `docs/`.\n"
        "Commit, stash, or clean the existing changes, or rerun with "
        "`--allow-dirty-baseline` when those changes are intentional.\n"
        f"Dirty files:\n{dirty_files}"
    )


def fetch_text(url: str) -> str | None:
    try:
        with urllib.request.urlopen(url, timeout=1.5) as response:
            if not 200 <= response.status < 500:
                return None
            return response.read().decode("utf-8", errors="replace")
    except (urllib.error.URLError, TimeoutError):
        return None


def http_ok(url: str) -> bool:
    return fetch_text(url) is not None


def server_serves_project(url: str) -> bool:
    html = fetch_text(url)
    if html is None:
        return False
    site_name = str(load_config().get("site_name", ""))
    return site_name in html


def port_available(port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            sock.bind(("127.0.0.1", port))
        except OSError:
            return False
    return True


def pick_port(preferred: int) -> int:
    if port_available(preferred):
        return preferred
    for port in range(preferred + 1, preferred + 50):
        if port_available(port):
            return port
    raise RuntimeError(f"No available port found starting at {preferred}")


def start_or_reuse_server(preferred_port: int) -> str:
    preferred_url = f"http://127.0.0.1:{preferred_port}/"
    if server_serves_project(preferred_url):
        return preferred_url

    port = pick_port(preferred_port)
    url = f"http://127.0.0.1:{port}/"
    CACHE_DIR.mkdir(exist_ok=True)
    log_path = CACHE_DIR / f"mkdocs-serve-{port}.log"
    log_handle = log_path.open("ab")
    process = subprocess.Popen(
        ["mkdocs", "serve", "-a", f"127.0.0.1:{port}"],
        cwd=PROJECT_ROOT,
        stdout=log_handle,
        stderr=subprocess.STDOUT,
        start_new_session=True,
    )
    (CACHE_DIR / "mkdocs-preview.pid").write_text(str(process.pid), encoding="utf-8")

    for _ in range(40):
        if process.poll() is not None:
            raise RuntimeError(f"mkdocs serve exited early. See {log_path}")
        if server_serves_project(url):
            return url
        time.sleep(0.25)

    raise TimeoutError(f"Timed out waiting for MkDocs server at {url}. See {log_path}")


def open_url(url: str) -> None:
    subprocess.run(["open", url], check=True)


def main() -> int:
    args = parse_args()
    try:
        assert_clean_baseline(args.allow_dirty_baseline)
        source = args.source.expanduser().resolve()
        destination, markdown = copy_source(source, args.slug, args.preset)
        title = args.title or first_h1(markdown) or destination.stem.replace("-", " ").title()
        update_nav(destination, title)
        if not args.skip_gallery:
            update_gallery(source, destination, title, args.preset)
            update_nav(GALLERY_PATH, "Artifact Gallery")
        run_build()
        if not args.skip_checks:
            run_static_checks(source, markdown, destination, title)

        print(f"source={source}")
        print(f"docs_page={destination}")
        print(f"preset={args.preset}")
        print(f"title={title}")

        if args.build_only:
            return 0

        url = start_or_reuse_server(args.port)
        page_path = preview_path_for_doc(destination)
        page_url = f"{url}{page_path}/" if page_path else url
        print(f"preview_url={page_url}")
        if not args.no_open:
            open_url(page_url)
        return 0
    except Exception as error:
        print(f"error: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
