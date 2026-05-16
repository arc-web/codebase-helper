#!/usr/bin/env python3
"""Render a Markdown file through the repo-local MkDocs preview surface."""

from __future__ import annotations

import argparse
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


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Copy Markdown into docs, update nav, build, serve, and open it."
    )
    parser.add_argument("source", type=Path, help="Markdown file to preview.")
    parser.add_argument("--title", help="Navigation title. Defaults to the first H1.")
    parser.add_argument("--slug", help="Destination slug under docs/. Defaults to source stem.")
    parser.add_argument("--port", type=int, default=8012, help="Preferred localhost port.")
    parser.add_argument("--build-only", action="store_true", help="Build without serving or opening.")
    parser.add_argument("--no-open", action="store_true", help="Do not call macOS open.")
    return parser.parse_args()


def slugify(value: str) -> str:
    slug = re.sub(r"[^A-Za-z0-9]+", "-", value.strip()).strip("-").lower()
    return slug or "preview"


def first_h1(markdown: str) -> str | None:
    for line in markdown.splitlines():
        if line.startswith("# "):
            return line[2:].strip()
    return None


def copy_source(source: Path, slug: str | None) -> tuple[Path, str]:
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
        shutil.copyfile(source, destination)

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
        yaml.safe_dump(config, handle, sort_keys=False)


def run_build() -> None:
    subprocess.run(["mkdocs", "build", "--strict"], cwd=PROJECT_ROOT, check=True)


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
        destination, markdown = copy_source(args.source, args.slug)
        title = args.title or first_h1(markdown) or destination.stem.replace("-", " ").title()
        update_nav(destination, title)
        run_build()

        print(f"source={args.source.expanduser().resolve()}")
        print(f"docs_page={destination}")
        print(f"title={title}")

        if args.build_only:
            return 0

        url = start_or_reuse_server(args.port)
        page_url = f"{url}{destination.stem}/"
        print(f"preview_url={page_url}")
        if not args.no_open:
            open_url(page_url)
        return 0
    except Exception as error:
        print(f"error: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
