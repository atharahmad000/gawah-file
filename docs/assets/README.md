# Documentation illustrations

These original SVG diagrams are explanatory illustrations of the implementation and synthetic cases. They are not application screenshots or a claim that a separate dashboard exists.

| Asset | Purpose |
|---|---|
| [gawah-cover.svg](gawah-cover.svg) | Project identity and the A1 credit/cash-out sequence |
| [architecture.svg](architecture.svg) | The responsibilities of SQL, retrieval and graph control |
| [restraint.svg](restraint.svg) | A1 and A4 reach different recommendations but share the signature gate |

Regenerate with `python scripts/render_docs.py` from the repository root. The script uses Python's standard library; each SVG embeds its colors, shapes, text, title and description. There are no external fonts, scripts, remote resources or image-generation dependencies.

The images use a fixed light paper background with navy, teal and amber accents, so their labels remain readable in both GitHub themes. All evidence and numerical claims also appear in text and the example packs.

License: [MIT](../../LICENSE), like the project.
