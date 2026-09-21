# Documentation

Gawah File prepares a reviewable investigation pack from synthetic wallet evidence. These pages explain how to run it, why each case behaves as it does, and where its controls end.

![Facts, policy and workflow meet at the human review boundary.](assets/architecture.svg)

## Choose a starting point

| Your goal | Read this | What you will learn |
|---|---|---|
| Understand the project quickly | [Project overview](../README.md) | Purpose, capabilities and a first run |
| Run it in Git Bash, PowerShell or a Unix shell | [Getting started](GETTING_STARTED.md) | Environment setup, signatures, Studio and troubleshooting |
| Follow the money in each case | [Case studies](CASE_STUDIES.md) | Evidence, applicable clauses, restraint and unanswered questions |
| Review the engineering | [Implementation guide](GUIDE.md) | State transitions, fan-out, persistence, approval and tradeoffs |
| Inspect the data | [Data sources](DATA_SOURCES.md) | Tables, identifiers, monetary units, clocks and provenance |
| Read actual outputs | [Evidence examples](examples/README.md) | Six fraud packs and a care-desk rendering in JSON/Markdown |
| Assess the checks | [Validation record](VALIDATION.md) | Tested guarantees, regression coverage and limits |
| Present the project | [Demo walkthrough](DEMO.md) | A short story from evidence to officer override |
| Change or publish it | [Contributing](../CONTRIBUTING.md), [publishing](PUBLISHING.md) | Development workflow and GitHub handover |
| Compare scope with the original brief | [Specifications](specifications/README.md) | Original Word documents and searchable extractions |

## A useful reading order

Start with **A1** in the [case studies](CASE_STUDIES.md#a1--bilal-first-credit-then-drain), then compare **A4**. That contrast explains why this project includes restraint cases alongside suspicious patterns. Read the [approval boundary](GUIDE.md#the-approval-boundary) next: evidence quality and permission are separate concerns.

For code review, follow `graph/desk.py` into `repos/ledger.py`, `pack/rules.py` and `repos/reviews.py`. Those four files show how a transaction finding becomes a cited recommendation and then an approved draft.

## How these pages are maintained

Hand-written guides explain the design. `scripts/export_demo.py` rebuilds the example packs and graph from disposable seed data. `scripts/render_docs.py` draws the [SVG illustrations](assets/README.md). Each illustration has descriptive alternative text and the same facts are explained in the surrounding Markdown.

All case evidence is fictional. The repository contains no live customer records, real regulatory policy, paid-model performance claims or financial execution integration.
