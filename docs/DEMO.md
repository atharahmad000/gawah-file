# Ninety-second walkthrough

Before recording, run the golden suite and start Studio. Keep two fresh threads ready: A1 with `off_fraud_01`, A4 with `off_fraud_01`. Use fictional data only.

The presentation should answer three questions: what evidence was gathered, why the recommendation follows, and who can authorize the next step. The [cover illustration](assets/gawah-cover.svg) works as an opening slide; the [architecture illustration](assets/architecture.svg) explains responsibilities without requiring the audience to read graph internals.

**0–15 seconds:** “Gawah File assembles an investigation file. SQL supplies the payment facts, the handbook supplies cited patterns, and the graph controls when a decision may be recorded.” Show the graph.

**15–40 seconds:** Open A1. Show `txn_bilal_credit` (PKR 25,000) and `txn_bilal_drain` (PKR 24,200), 18 minutes apart. Point to `T01_first_credit_drain`. Explain that the high hint requires attention, not permission to act.

**40–60 seconds:** Show the pause before `apply_action`. Resume unsigned once and show it returns to review. Set `signed=true`, `human_decision=watch` and comment “Verify the destination first.” Resume. Show the approved watch and the preserved original recommendation in the audit event.

**60–80 seconds:** Open A4. Show the ordinary spending history, the odd cousin transfer and T04/T07 citations. “An unusual payment does not erase established context. The draft is watch, and the officer still reviews it.”

**80–90 seconds:** Show the passing golden suite. “The test is whether evidence, citations and permission agree. These are synthetic cases; this is not a production fraud detector.”

Optional extensions: A3 shows two subgraph memos. A6 shows duplicate-payment restraint and prior goodwill. `scripts/demo_time_travel.py` forks an unsigned checkpoint; replay cannot rewrite an already-approved review.

If Studio's hosted interface is unavailable, use `scripts/demo_alert.py` and the Markdown exports in `docs/examples`. A video recording is a manual presentation step.

## Terminal presentation

With the virtual environment active, run these commands one at a time. Use new thread names on a repeat presentation:

```bash
python scripts/demo_alert.py A1 --thread presentation-a1 --format markdown
python scripts/demo_alert.py A1 --thread presentation-a1 --inspect --format markdown
python scripts/demo_alert.py A1 --thread presentation-a1 --sign watch --comment "Verify the destination first." --format markdown
python scripts/demo_alert.py A4 --thread presentation-a4 --format markdown
```

The third command is the explicit demonstration signature. Show the change from awaiting review to a recorded watch draft, and explain that no wallet status or money movement changes. The CLI walkthrough does not itself demonstrate an unsigned resume; use Studio or `scripts/demo_gate.py` for that check.

## Longer walkthrough

| Add two minutes for | Show | Explain |
|---|---|---|
| Linked-wallet evidence | [A3](examples/A3.md) | Two separate entity memos survive in the portable saved pack |
| Customer-service context | [A6 care](examples/A6-care.md) | The same evidence can be presented more briefly without omitting ledger detail |
| Auditability | The read-only review query in [data sources](DATA_SOURCES.md#read-only-inspection-examples) | The original proposal and signed override remain distinct |
| Engineering review | [Validation](VALIDATION.md) | Golden cases are backed by cutoff, citation, memory and replay checks |

For a static GitHub walkthrough, start at the README and open the linked packs. The illustrations are explanatory graphics, not screenshots of a product UI. A useful closing question for reviewers is: which additional evidence would you require before accepting this draft?
