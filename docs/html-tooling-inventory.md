# HTML Tooling Inventory

## Scope

This inventory covers reusable source and configuration surfaces under
`/Users/home/ai/agents` plus the older `/Users/home/markdown_html5_lab`
prototype. It excludes generated client output and machine state, including
`clients/**`, `site/**`, `reports/**`, `campaign_data/**`, `node_modules/**`,
`venv/**`, `.venv/**`, `__pycache__/**`, CSVs, logs, and generated HTML
snapshots unless a snapshot demonstrates a reusable pattern.

## Candidate Inventory

| Candidate | Classification | Source surface | Reusable pattern |
| --- | --- | --- | --- |
| Codebase Helper MkDocs preview | Markdown docs | `/Users/home/ai/agents/development/codebase_helper/mkdocs.yml`, `/Users/home/ai/agents/development/codebase_helper/scripts/preview_markdown.py` | Strict MkDocs build, Material theme, source Markdown copy, local server reuse check. |
| Obsolete Markdown HTML5 Lab | Markdown docs, Generated artifact | `/Users/home/markdown_html5_lab/mkdocs.yml`, `/Users/home/markdown_html5_lab/docs/index.md` | Earlier MkDocs prototype. Keep documented as obsolete until cleanup is approved. |
| PPC new campaign report builder | Report builder, Template engine | `/Users/home/ai/agents/ppc/google_ads_agent/shared/presentation/build_new_campaign_report.py` | Dataclass inputs, HTML escaping, structured report sections, inline CSS, quality audit hooks. |
| PPC Chrome PDF export wrapper | PDF export | `/Users/home/ai/agents/ppc/google_ads_agent/shared/presentation/build_review_doc.py` | Canonical Chrome headless flags, timeout handling, deterministic output path, optional desktop mirror. |
| PPC presentation quality docs | Visual QA | `/Users/home/ai/agents/ppc/google_ads_agent/presentations/docs/DEVELOPER_GUIDE.md` | Static HTML audit, rendered PDF density audit, contact-sheet inspection, no-footer-only-page checks. |
| PPC animated static presentation | Static presentation | `/Users/home/ai/agents/ppc/google_ads_agent/docs/presentation/index.html` | Single-file static presentation, custom CSS, keyboard navigation, slide sections, animated polish. |
| Dyad React Vite app | Frontend app | `/Users/home/ai/agents/web/dyad_agent/apps/serene-starfish-skip/package.json` | Vite, React, TypeScript, shadcn-style component dependencies, Tailwind typography candidate. |
| Music agent Flask app | Template engine | `/Users/home/ai/agents/creative/music_agent/apps/web_interface_app/app.py` | Flask routes, Jinja templates, API endpoints, server-rendered web interface pattern. |

## Evaluation Matrix

Scores use 1 low to 5 high. Lower effort, maintenance risk, and local
dependency scores are better. Higher reuse value, visual quality, and handoff
fit scores are better.

| Candidate | Reuse value | Effort | Visual quality | Maintenance risk | Local dependencies | Agent handoff fit | Decision |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| Codebase Helper MkDocs preview | 5 | 1 | 3 | 1 | 1 | 5 | Keep as the default fast renderer. |
| Obsolete Markdown HTML5 Lab | 2 | 1 | 3 | 2 | 1 | 2 | Reference only. Do not revive before cleanup approval. |
| PPC new campaign report builder | 5 | 3 | 5 | 3 | 2 | 4 | Adapt ideas into helper presets and checks. |
| PPC Chrome PDF export wrapper | 4 | 2 | 4 | 2 | 3 | 3 | Add later as optional verification, not default preview. |
| PPC presentation quality docs | 5 | 2 | 4 | 2 | 2 | 5 | Reuse quality-gate concepts in static checks. |
| PPC animated static presentation | 3 | 4 | 5 | 4 | 2 | 2 | Keep as inspiration for presentation-style pages only. |
| Dyad React Vite app | 3 | 5 | 5 | 4 | 5 | 2 | Optional later track for interactive apps. |
| Music agent Flask app | 2 | 4 | 3 | 4 | 4 | 2 | Optional later track for dynamic template apps. |

## Recommendation

Keep MkDocs as the default Markdown renderer because it is already local,
strict, searchable, and easy for agents to operate. Add a richer artifact mode
inside the existing helper before introducing Vite, React, Flask, or Jinja.

The strongest reusable ideas come from the PPC presentation and report tooling:
structured presets, a shared visual layer, deterministic source paths, strict
quality gates, optional Chrome rendering, and visual QA only when the task asks
for it.

## v2 Capability Plan

Implemented first:

- Artifact presets: `note`, `handoff`, `repo-walkthrough`,
  `implementation-summary`, and `review-packet`.
- Shared visual layer through `docs/stylesheets/artifacts.css`.
- Local gallery page at `docs/artifacts/index.md`.
- Static checks for missing titles, missing or tiny generated pages, broken
  local source links, and wrong server reuse.
- Existing quick path preserved through `python3 scripts/preview_markdown.py
  <file.md>`.

Later optional tracks:

- Chrome PDF export using the PPC fixed-flag pattern.
- Screenshot or density checks for visual verification on request.
- Presentation-style pages for curated walkthroughs.
- React or Flask surfaces only if a future artifact requires live
  interactivity that MkDocs cannot provide.

## Verification Commands

```bash
mkdocs build --strict
python3 scripts/preview_markdown.py docs/html-tooling-inventory.md --slug html-tooling-inventory --title "HTML Tooling Inventory" --build-only
test -f site/html-tooling-inventory/index.html
python3 scripts/preview_markdown.py smoke/fixtures/handoff-sample.md --preset handoff --slug handoff-sample --title "Handoff Sample" --build-only
python3 scripts/preview_markdown.py smoke/fixtures/repo-walkthrough-sample.md --preset repo-walkthrough --slug repo-walkthrough-sample --title "Repo Walkthrough Sample" --build-only
```

<div class="artifact-meta" markdown="1">

**Preset:** Note
**Source:** `ai/agents/development/codebase_helper/docs/html-tooling-inventory.md`
**Use:** Fast Markdown preview with source provenance.

</div>
