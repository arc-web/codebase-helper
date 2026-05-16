#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."
mkdir -p .cache

tmp_config="$(mktemp)"
tmp_gallery="$(mktemp)"
tmp_manifest="$(mktemp)"
tmp_docs="$(mktemp -d)"
cp mkdocs.yml "$tmp_config"
cp docs/artifacts/index.md "$tmp_gallery"
for doc in smoke-preview.md handoff-sample.md repo-walkthrough-sample.md; do
  if [ -f "docs/$doc" ]; then
    cp "docs/$doc" "$tmp_docs/$doc"
  fi
done
if [ -f .cache/artifacts.json ]; then
  cp .cache/artifacts.json "$tmp_manifest"
else
  : > "$tmp_manifest"
fi
restore() {
  cp "$tmp_config" mkdocs.yml
  cp "$tmp_gallery" docs/artifacts/index.md
  if [ -s "$tmp_manifest" ]; then
    cp "$tmp_manifest" .cache/artifacts.json
  else
    rm -f .cache/artifacts.json
  fi
  rm -f "$tmp_config"
  rm -f "$tmp_gallery"
  rm -f "$tmp_manifest"
  for doc in smoke-preview.md handoff-sample.md repo-walkthrough-sample.md; do
    if [ -f "$tmp_docs/$doc" ]; then
      cp "$tmp_docs/$doc" "docs/$doc"
    else
      rm -f "docs/$doc"
    fi
  done
  rm -rf "$tmp_docs"
  rm -f docs/smoke-dirty-baseline.md
}
trap restore EXIT

mkdocs --version
mkdocs build --strict

printf '# Dirty Baseline Guard\n' > docs/smoke-dirty-baseline.md
if python3 scripts/preview_markdown.py smoke/fixtures/sample-preview.md --slug smoke-preview --title "Smoke Preview" --build-only 2> .cache/dirty-baseline-guard.err; then
  echo "expected dirty baseline guard to fail" >&2
  exit 1
fi
grep -q "dirty baseline detected" .cache/dirty-baseline-guard.err
grep -q "mkdocs.yml" .cache/dirty-baseline-guard.err
grep -q "docs/artifacts/index.md" .cache/dirty-baseline-guard.err
rm -f docs/smoke-dirty-baseline.md .cache/dirty-baseline-guard.err

python3 scripts/preview_markdown.py smoke/fixtures/sample-preview.md --slug smoke-preview --title "Smoke Preview" --build-only
python3 scripts/preview_markdown.py smoke/fixtures/handoff-sample.md --preset handoff --slug handoff-sample --title "Handoff Sample" --build-only --allow-dirty-baseline
python3 scripts/preview_markdown.py smoke/fixtures/repo-walkthrough-sample.md --preset repo-walkthrough --slug repo-walkthrough-sample --title "Repo Walkthrough Sample" --build-only --allow-dirty-baseline
test -f site/index.html
test -f site/learning-example/index.html
test -f site/smoke-preview/index.html
test -f site/handoff-sample/index.html
test -f site/repo-walkthrough-sample/index.html
