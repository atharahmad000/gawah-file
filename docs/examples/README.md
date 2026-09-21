# Example evidence packs

These snapshots were generated from the fictional seed data in offline mode. They show unsigned recommendations, not completed financial actions.

| Alert | Readable pack | Structured pack |
|---|---|---|
| A1: First-credit drain | [Markdown](A1.md) | [JSON](A1.json) |
| A2: Night bill failures | [Markdown](A2.md) | [JSON](A2.json) |
| A3: Shared new payee | [Markdown](A3.md) | [JSON](A3.json) |
| A4: One unusual transfer | [Markdown](A4.md) | [JSON](A4.json) |
| A5: Prior watchlist review | [Markdown](A5.md) | [JSON](A5.json) |
| A6: Duplicate shop debit | [Markdown](A6.md) | [JSON](A6.json) |
| A6: Care-desk presentation | [Markdown](A6-care.md) | [JSON](A6-care.json) |

To regenerate, use `python scripts/export_demo.py` from the repository root with dependencies installed. The script builds fresh temporary databases and an index, forces offline mode, and leaves your operational review history out of the published examples. Keep personal thread-specific exports in the ignored `data/` directory.

Each Markdown file is rendered from its accompanying structured pack. It includes transaction ids and statuses, policy quotations, open questions, previous context and repository-function provenance. A3 also preserves both linked-wallet memos. The A6 care version demonstrates a prose summary with expandable ledger detail.

Start with A1 and A4 to compare a first-credit drain with an established customer's unusual payment. Then read A3 for linked evidence and A6 for complaint handling. The [case studies](../CASE_STUDIES.md) explain why each recommendation follows from the supplied facts.
