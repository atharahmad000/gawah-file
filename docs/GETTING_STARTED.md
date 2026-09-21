# Getting started

[Documentation](README.md) · [Project overview](../README.md) · [Architecture](GUIDE.md)

The quickest useful result is an unsigned evidence pack for A1. You can inspect its transactions and policy support before making a separate, explicit decision. The default workflow needs no API key.

## Install and prepare the data

Use Python 3.11 or later. Open a terminal in the repository directory containing `pyproject.toml`. On Windows with Git Bash:

```bash
python -m venv .venv
source .venv/Scripts/activate
python -m pip install -r requirements.txt
cp .env.example .env
export PYTHONUTF8=1
python seeds/build_db.py
python scripts/check_seeds.py
python scripts/build_index.py
```

On Linux or macOS, create the environment with `python3` and activate `.venv/bin/activate`. In PowerShell, use `.venv/Scripts/python.exe` instead of `python`, `Copy-Item .env.example .env` instead of `cp`, and `$env:PYTHONUTF8 = '1'`. Activation is optional when you use the environment's executable directly.

| Step | What it creates or checks |
|---|---|
| Install requirements | The Python graph, database, validation and retrieval dependencies |
| Copy `.env.example` | Local settings; keep the default offline mode for the first run |
| Build database | `data/gawah_ops.db`, populated from the checked-in synthetic SQL |
| Check seeds | The six planted investigation stories; expect `PASS A1` through `PASS A6` |
| Build index | A local handbook index used by TF-IDF retrieval |

These are first-install commands. Keep an existing `.env` and operational database when returning to the project. `requirements-lock.txt` records the verified Windows/Python 3.12 environment; `requirements.txt` is the portable installation entry point.

## Open a review

The remaining commands assume the virtual environment is active:

```bash
python scripts/demo_alert.py A1 --thread first-review --format markdown
```

Read the output in this order:

1. **Status:** awaiting a human signature. Opening the alert has not approved anything.
2. **Transactions:** PKR 25,000 received, followed by PKR 24,200 cashed out 18 minutes later.
3. **Policy:** T01 supports investigating a first-credit drain.
4. **Recommendation:** the fraud desk proposes freeze, with questions still requiring an officer's judgment.

The graph saves the pack and checkpoint before the review pause. Omit `--format markdown` to see JSON, including the thread id and next node. Inspecting the same thread does not start another investigation:

```bash
python scripts/demo_alert.py A1 --thread first-review --inspect --format markdown
```

Every new investigation needs a new thread id. If you omit `--thread` when opening a case, the runner generates one and prints it. Keep that id if you want to inspect or sign later.

## Record a decision

The officer can accept the recommendation or override it. This example records watch while retaining the original freeze proposal in the audit event:

```bash
python scripts/demo_alert.py A1 --thread first-review --sign watch --comment "Verify the destination before restricting the wallet." --format markdown
```

The permitted decisions are `watch`, `close`, `freeze` and `file_compliance`. The saved review and approved draft share a review id. Approval and its audit event are written together; changed evidence or an incompatible replay is refused.

**A signed draft does not execute a financial action.** Wallet status, balances and alert status are not changed by this approval. The local `signed` field is a demonstration control, not identity authentication. Read [the approval boundary](GUIDE.md#the-approval-boundary) before extending this workflow.

To compare different kinds of evidence:

```bash
python scripts/demo_alert.py A3 --thread linked-review --format markdown
python scripts/demo_alert.py A4 --thread established-customer --format markdown
python scripts/demo_alert.py A6 --desk care --thread duplicate-payment --format markdown
```

A3 includes two linked-wallet memos. A4 demonstrates restraint despite an unusual transfer. A6's care presentation uses a prose summary with expandable transaction evidence. The [case studies](CASE_STUDIES.md) explain all six outcomes.

## Studio

Start the development server from the activated environment:

```bash
langgraph dev --no-browser --no-reload --port 2024
```

In PowerShell without activation, run `.venv/Scripts/langgraph.exe` instead. Open [Studio](https://smith.langchain.com/studio/?baseUrl=http://127.0.0.1:2024) or the [local API documentation](http://127.0.0.1:2024/docs). The hosted Studio interface may require a LangSmith account. Keep the local server bound to `127.0.0.1`.

Select `gawah_fraud` and open a fresh thread with:

```json
{"alert_id": "A1", "officer_id": "off_fraud_01"}
```

For the care desk, select `gawah_care` and use `off_care_01`. The officer's SQL record determines the desk and preferences; an arbitrary input field cannot replace that identity.

At the pause, inspect `pack`, `sql_findings`, `policy_hits`, `evidence` and `gate_reason`. To perform the explicit local sign-off, update the paused state with:

```json
{
  "signed": true,
  "human_decision": "watch",
  "human_comment": "Review the destination before restricting the wallet."
}
```

Then resume the thread. A resume without a true Boolean signature and a permitted decision is refused and returns to the pause. Adding `signed` to the original case input cannot preapprove the investigation.

Studio and the command-line runner use different checkpoints. Agent Server manages Studio state under `.langgraph_api`; the standalone runner uses `data/gawah_graph.db`. Both read and write the configured operational database. A CLI thread cannot inspect a Studio checkpoint. See [the implementation guide](GUIDE.md#studio) for message updates and server behavior.

## Configuration

Keep local settings in the ignored `.env`. The checked-in example contains no credentials.

| Setting | Default or purpose |
|---|---|
| `GAWAH_OFFLINE` | `1`: deterministic templates; no chat-model request |
| `GAWAH_AS_OF` | `2026-09-01T12:00:00`: fixed demonstration clock |
| `GAWAH_OPS_DB` | `data/gawah_ops.db`: evidence, reviews and durable memories |
| `GAWAH_GRAPH_DB` | `data/gawah_graph.db`: standalone checkpoints; use a different file from the operational database |
| `GAWAH_CHAT_MODEL` | Optional provider model identifier from `.env.example` |
| `OPENAI_API_KEY` | Only needed to try the optional online headline writer |
| `LANGSMITH_TRACING` | `false`: tracing disabled by default |
| `LANGSMITH_API_KEY` / `LANGSMITH_PROJECT` | Optional tracing configuration |

To try the optional writer, set offline mode to `0` and configure a valid provider key and model. Provider availability depends on your account. The model can supply a headline; it cannot replace the deterministic facts, rationale, policy quotations or recommendation. Its prose still needs human review. Missing credentials and provider errors fall back to the template. Live paid-provider responses have not been validated for this repository.

The demonstration clock and actual approval time are different: the case uses historical evidence bounded by the alert's opening time, while the audit records when approval actually occurred. See [data and clocks](GUIDE.md#data-and-clocks).

## Export documents and check your setup

```bash
python -m pytest -q -p no:langsmith
python scripts/check_repository.py
python scripts/export_demo.py
python scripts/render_docs.py
```

The export script builds fresh temporary databases, forces offline mode and generates six fraud packs plus one care pack under `docs/examples/`. It does not use your local review history. The SVG script regenerates the three illustrations from editable code. Run both when updating their underlying content.

For a private review export, use an ignored local path:

```bash
python scripts/demo_alert.py A3 --thread linked-review --inspect --format markdown --export data/reviews/A3.md
```

## Troubleshooting

| Symptom | Explanation and next step |
|---|---|
| Database already exists | The builder protects saved reviews. Use the existing database, or stop Studio and use `seeds/build_db.py --reset` only when you intend to discard disposable operational data. Use fresh thread ids afterward. |
| Thread already exists | Use `--inspect` or `--sign` for that review; choose another id for a new investigation. |
| Thread does not belong to the alert | Check both the alert and thread id. Also check whether you opened the review in Studio or the standalone runner. |
| No suitable handbook result | Rebuild the index after changing policy Markdown. A weak match deliberately produces an escalation/watch pack instead of invented policy support. |
| Python or a package is not found | Activate the correct environment, or call its Python executable directly. Install dependencies with that same executable. |
| Unicode output fails in a Windows terminal | Set `PYTHONUTF8=1` before starting Python, or use the default JSON output. |
| Online writer still uses a template | Check offline mode and credentials. A missing key or provider error intentionally falls back; offline behavior remains available. |
| Git reports dubious ownership | Follow the scoped ownership note in [publishing](PUBLISHING.md); do not disable ownership checks globally. |

For a short presentation, continue with [the demo walkthrough](DEMO.md). For tested behavior and known limits, read [validation](VALIDATION.md).
