# Learning Example

## Concept

!!! note "Core idea"
    Markdown stays readable in source form, while MkDocs Material upgrades the
    HTML output into a searchable, navigable learning interface.

## Study Checklist

- [x] Convert Markdown headings into an outline.
- [x] Add search and navigation.
- [x] Add collapsible explanations.
- [ ] Add domain-specific quizzes or diagrams.

## Compare Modes

=== "Raw Markdown"

    ```markdown
    # Topic

    !!! tip "Remember"
        Use headings to structure the lesson.
    ```

=== "Rendered HTML5"

    The same content becomes a styled page with navigation, syntax highlighting,
    search, and responsive layout.

## Expandable Explanation

??? question "Why is this lossy?"
    The rendered HTML preserves the learning meaning, but it does not preserve
    every original Markdown byte. For example, two different Markdown spellings
    for bold text render to the same HTML intent.

## Mini Reference

Term
:   A named idea from the note.

Learning interface
:   The searchable HTML site produced from the Markdown source.

## Data Table

| Source pattern | Rendered affordance |
| --- | --- |
| `# Heading` | Page title and table of contents entry |
| `!!! note` | Callout box |
| `??? question` | Collapsible section |
| `- [ ] task` | Interactive-looking checklist |

## Code Example

```python
def convert_note(path: str) -> str:
    return f"Rendered {path} as HTML5"
```

