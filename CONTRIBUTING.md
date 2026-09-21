# Contributing

Start with the [quick start](README.md#run-it-locally), then read the [implementation guide](docs/GUIDE.md). Keep contributions focused on the six documented investigation stories and their permission boundary.

## Development checks

From the repository root, with dependencies installed:

```bash
python scripts/check_repository.py
python -m pytest -q -p no:langsmith
```

Tests create isolated databases and retrieval indexes. Do not commit a virtual environment, `.env`, database, checkpoint, provider key or local review export. All customer data must remain fictional.

When changing seed facts, run `python scripts/check_seeds.py` against a rebuilt demo. When changing handbook pages, rebuild the index and check the retrieval tests. Regenerate published examples with `python scripts/export_demo.py`; it creates its own disposable data so local review memory cannot enter the documents. Edit `scripts/render_docs.py` and regenerate when changing the SVG illustrations.

## Design constraints

- Keep operational SQL in `repos/`; bind query parameters.
- Keep model tools read-only. Approval belongs behind the human gate.
- Preserve the fixed evidence clock and distinguish failed attempts from settled movement.
- Cite only clauses retrieved for the current investigation.
- Preserve atomic approval, saved-pack comparison and replay protection.
- A4 and A6 must retain their non-freeze recommendations.

Use short, factual explanations in evidence packs and comments that explain why a control exists. Include a meaningful test when changing financial evidence or approval behavior. Describe test limitations in the pull request.

The repository is intended to run from a source checkout. Building and distributing it as a standalone Python wheel is not currently supported because the application resolves SQL and handbook resources relative to that checkout.
