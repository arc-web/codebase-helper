#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

tmp_config="$(mktemp)"
cp mkdocs.yml "$tmp_config"
restore() {
  cp "$tmp_config" mkdocs.yml
  rm -f "$tmp_config"
  rm -f docs/smoke-preview.md
}
trap restore EXIT

mkdocs --version
mkdocs build --strict
python3 scripts/preview_markdown.py smoke/fixtures/sample-preview.md --slug smoke-preview --title "Smoke Preview" --build-only
test -f site/index.html
test -f site/learning-example/index.html
test -f site/smoke-preview/index.html
