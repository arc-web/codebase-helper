# Smoke Preview

This fixture verifies that the preview helper can render a real Markdown input,
add it to MkDocs navigation, and produce generated HTML during a strict build.

!!! note "Smoke scope"
    The smoke script restores `mkdocs.yml` and removes the copied docs page
    after verification.

