GAWAH FILE
Project proposal and implementation specification
A permissioned investigation desk for synthetic digital-wallet alerts.Single source of truth for any engineer or coding agent. Do not invent a chatbot, a fraud platform, or a research-assistant clone.Document date: 12 September 2026  ·  Owner: Athar Ahmad  ·  Status: implementation-ready

Audience: Any engineer or coding agent building the repository
Stack constraint: Python 3.11+, LangGraph, SQLite, a small RAG index, optional scikit-learn
Non-negotiable product rule: The model may gather, cite, and propose. It may not freeze a wallet, unfreeze a wallet, or open a compliance case until a human signs the evidence pack.

0. How another AI must use this document
Read this section first. Then implement in the order in Section 18. Do not start with a UI, embeddings, or a multi-agent supervisor.
0.1 What “done” means
The project is done when all six golden alerts in Section 9 run end-to-end and every acceptance check in Section 16 passes. Extra features after that are out of scope.
0.2 What you must not invent
Real Jazz, JazzCash, NADRA, FIA, SBP, or bank data
A detector that auto-freezes
Free-form `run_sql` exposed to the LLM
LangGraph Supervisor, Swarm, Deep Agents, Functional API as the main app
Voice, WhatsApp, React, auth, Postgres clusters
Web search, email, Slack tools
Fine-tuned transformers or graph neural nets
0.3 Naming
Product name: **Gawah File**
Meaning: *gawah* = witness. The agent is a witness that prepares testimony. The officer is the judge.
Repo name: `gawah-file`
Ops database file: `data/gawah_ops.db`
Graph checkpoint database: `data/gawah_graph.db`
Playbook directory: `playbook/`
Never mix the two SQLite files.
0.4 Voice of the product
Outputs are an evidence pack, not a chat essay. Structured fields first. Short prose last. Every policy sentence in the pack must carry a clause id that was actually retrieved.

1. Purpose
When a digital-wallet alert fires, an officer must answer three questions before any irreversible action:
What money actually moved? (facts)
Which handbook pattern might this be — including patterns that say *do not freeze*? (rules)
Who is allowed to act? (permission)
Gawah File exists to assemble that file. It does not exist to “catch fraud,” “replace compliance,” or “automate freezes.”
Industry desks already have alerts. The bottleneck is assembling evidence and a rule citation that a human can stand behind. An LLM that only chats does not help. An agent that freezes alone is not allowed. This project copies the control layer in miniature: retrieve facts, retrieve rules, draft a recommendation, stop, human signs, then and only then write an action.

2. Objectives
Demonstrate a **decision system**, not a chatbot. Shared state is a case file.
Keep three planes separate and visible in the repo:
SQL = facts
RAG = handbook paragraphs
LangGraph = permission, parallelism, memory, pause
Make the dangerous step structurally impossible without a human: `apply_freeze` and `open_compliance_case` sit behind interrupts. They are nodes, not ReAct tools.
Use subgraphs and `Send` when an alert has more than one related wallet.
Persist short-term case state (checkpointer) and long-term wallet/officer memory (Store).
Include a tiny classical model only as a **risk hint** that can raise a gate, never open it.
Make behaviour testable with six golden alerts (SQL assertions + citation assertions + interrupt assertions).

3. Scope
3.1 In scope
Twelve synthetic wallets, a few hundred synthetic transactions
Six alerts in an inbox table
Ten to twelve playbook pages
Parent graph + one subgraph (`investigate_entity`)
Fixed SQL tools and one RAG tool
Freeze / watch / close / file-for-compliance as *draft* actions
Human-in-the-loop via `interrupt_before` and `NodeInterrupt`
Time travel for one recorded demo
Two Assistants (fraud desk, customer-care desk)
SQLite ops DB + LangGraph checkpoint DB
Local Studio via `langgraph dev`
Eight-ish eval scripts including the six alerts plus two extras (FAQ-style “what is this wallet’s city?” is optional; prefer keeping all six as investigations)
3.2 Out of scope
Production detection quality
Real-time streaming ingest
Device fingerprints, GPS, ID images, call recordings
Multi-user auth product
Cloud deployment as a requirement
Message-window trimming as a featured subsystem
Trustcall, unless profile writes become messy and time remains
Any claim that this is JazzCash, ReadyCash, or an official typology
3.3 Success metric
Not accuracy against real fraud. Success is: for each golden alert, the system finds the planted rows, cites the planted clause, pauses when required, and refuses to write a freeze without a signed state field.

4. Industry importance (honest framing)
Digital wallets settle in seconds. A false freeze harms a customer. A missed drain harms the institution and other customers.
The useful agent pattern in payments, lending exceptions, claims, and AML-lite is the same:
gather evidence from systems of record
retrieve written policy
recommend
stop on irreversible actions
record who overrode what
Gawah File is a teaching-sized copy of that pattern. It is relevant to a Jazz / JazzCash-style interview because wallet disputes, ReadyCash exceptions, insurance first notice, and fraud review all need the same permission split: the model proposes; the desk disposes.
Do not write README claims such as “production-grade AML” or “state-of-the-art fraud engine.”

5. Architecture
5.1 Three planes
Officer opens an alert        |        v+--------------------------------------+| CONTROL  LangGraph parent graph      || classify -> gather -> pack -> GATE   ||            -> act -> memory          |+--------------------------------------+        |              |              |        v              v              v   SQL facts      RAG playbook    Memory   ledger         clause pages    profile /   flags          with ids        prior cases /   links                          officer SOP        |        v   risk_hint (tiny logistic on SQL features)   may force interrupt; may never freeze
5.2 Two databases
File
Role
`data/gawah_ops.db`
Wallets, ledger, alerts, clauses audit copy, drafts, events
`data/gawah_graph.db`
Threads, checkpoints, time travel

Never store ledger rows in the graph DB. Never store checkpoints in the ops DB.
5.3 Process at runtime (happy path)
Load alert row from SQL.
Route: investigation (always, for the six goldens).
Fan-out in parallel: ledger, flags, prior cases, playbook retrieve, feature/hint.
If linked wallets exist, `Send` one `investigate_entity` subgraph per related wallet_id.
Reduce evidence memos into `evidence[]`.
Write structured `EvidencePack`.
Apply gate rules. Interrupt.
Human updates state (`human_decision`, optional edits).
Only if signed: insert draft action as approved and append `case_events`.
Write long-term memories.

6. Repository layout (mandatory)
gawah-file/  README.md  requirements.txt  langgraph.json                  # or studio/langgraph.json  .env.example                    # OPENAI_API_KEY, LANGSMITH optional  seeds/    schema.sql    seed_wallets.sql    seed_merchants.sql    seed_transactions.sql    seed_links_flags.sql    seed_alerts_cases.sql    seed_playbook_sql.sql    seed_labels.sql    build_db.py                   # runs schema + seeds + feature rebuild  playbook/    T01_first_credit_drain.md    T02_night_bill_camouflage.md    T03_shared_new_payee.md    T04_loyal_customer_one_odd.md    T05_already_reviewed_watchlist.md    T06_duplicate_merchant_debit.md    T07_when_not_to_freeze.md    T08_pass_through_mule.md    T09_velocity_cashout.md    T10_goodwill_and_care_desk.md  domain/    state.py                      # CaseState, EvidencePack, ProposedAction    enums.py  repos/    db.py                         # connection to gawah_ops.db only    wallets.py    ledger.py    alerts.py    cases.py    playbook_sql.py    features.py  retrieve/    playbook_index.py             # build/load vector index from playbook/    retriever.py                  # search_playbook(query) -> list[ClauseHit]  risk/    features_sql.py               # rebuild txn_features    train_hint.py                 # optional training script    hint.py                       # RiskHint.predict(wallet_id) -> low|med|high    hint_model.joblib             # committed or rebuilt by train_hint.py  tools/    registry.py                   # bindable tools; NO apply_freeze here  graph/    desk.py                       # parent StateGraph    investigate_entity.py         # subgraph    routing.py    gates.py                      # interrupt rules  studio/    langgraph.json    desk_graph.py                 # exports compiled graph  evals/    golden.yaml    test_goldens.py  scripts/    demo_alert.py                 # run one thread_id
Python OOP rule: SQL lives only in `repos/`. Vectors live only in `retrieve/`. The LLM never receives a connection string.

7. Domain objects
7.1 Enums
AlertStatus: open | investigating | waiting_human | closedCaseType: first_credit_drain | night_bill_camouflage | shared_payee | loyal_odd | watchlist_repeat | duplicate_debitActionType: close | watch | freeze | file_complianceActionStatus: draft | approved | rejected | executedRiskHint: low | medium | highDeskRole: fraud | careWalletStatus: active | frozen | closedKycTier: basic | fullTxnType: merchant_debit | bill | p2p_send | p2p_receive | cashin | cashout | reversal | failed_billTxnStatus: success | failed | pending | reversedFlagType: watchlist | frozen_related | prior_review | velocitySeverity: low | high
7.2 CaseState (graph state)
Required keys:
messages                 # add_messages reduceralert_id                 strwallet_id                strofficer_id               strdesk_role                DeskRolerelated_wallet_ids       list[str]          # reducer: unique unionevidence                 list[EvidenceMemo] # reducer: operator.addpolicy_hits              list[ClauseHit]    # reducer: operator.addsql_findings             dict               # overwrite with latest gatherrisk_hint                RiskHintrisk_hint_reasons        list[str]pack                     EvidencePack | Noneproposed_action          ActionType | Noneproposed_rationale       strhuman_decision           ActionType | Nonehuman_comment            strgate_reason              str                # why interruptedsigned                   bool               # True only after human update_state
Private / internal-only keys (do not put in output schema):
raw_tool_dumps           dict
7.3 EvidencePack (structured output)
alert_idwallet_idheadline                 # one sentencetimeline                 # list of {ts, txn_id, amount_pkr, description}sql_queries_relied_on    # list of tool names actually calledlinked_wallets           # list of wallet_idclause_ids_cited         # subset of policy_hits idsclause_quotes            # short quotes only from retrieved textrisk_hintrisk_hint_reasonsrecommended_action       # ActionTypewhy_not_other_actions    # shortopen_questions           # list
Validation rule: every id in `clause_ids_cited` must exist in `policy_hits` from this run. If the writer cites an id that was not retrieved, the pack node must strip it or fail the node and escalate (“no valid citation”).
7.4 EvidenceMemo (subgraph output)
entity_wallet_idmemo_type                # subject | counterpartyfindings                 # 3-8 bullets maxtxn_ids                  # ids touched

8. Data sources and types
All customer data is synthetic. Identifiers look fake: `w_ayesha_lhr`, phone `03xx-1111111`. README must say: “No production wallet data was used.”
Source
Purpose
Authoring format
System of record
Wallet master
Who is this?
Excel optional, then SQL
`wallets`
Wallet notes
Habits, language
Excel optional, then SQL
`wallet_profiles`
Merchants / payees
Category of destination
Excel optional, then SQL
`merchants`
Ledger
What moved
Excel draft, then SQL
`transactions`
Wallet links
Shared new payee
SQL
`wallet_links`
Risk flags
Watch / frozen / prior review
SQL
`risk_flags`
Alert queue
Demo inbox
SQL
`alerts`
Historical cases
Memory of prior decisions
SQL
`cases`
Playbook pages
Typology handbook
Markdown files
`playbook/*.md` + SQL `policy_clauses` audit copy
RAG index
Retrieve clauses
Built at startup from Markdown
Chroma or FAISS local folder `data/playbook_index/`
Feature table
Numeric hint inputs
Computed by script
`txn_features`
Hint labels
Train tiny model
CSV/Excel then SQL
`alert_labels`
Officers + prefs
Two desks
SQL
`officers`, `officer_prefs`
Evidence packs
Written file
SQL + optional .md export
`evidence_packs`
Draft actions
Unsigned then signed
SQL
`draft_actions`
Case events
Audit timeline
SQL
`case_events`
Memories mirror
Optional SQL copy of Store
SQL
`memories`
Graph checkpoints
Pause / time travel
LangGraph
`gawah_graph.db`
Golden tests
Expected behaviour
YAML
`evals/golden.yaml`
Trained hint
Coefficients
joblib
`risk/hint_model.joblib`

Excel is only a kitchen counter for typing rows. Runtime reads SQL and Markdown.

9. Six golden alerts (plant these exactly)
Implement seeds so the listed queries return the listed ids. Do not randomise these stories away.
9.1 Alert A1 — First credit then drain (`w_bilal_khi`)
Story. New wallet. First inbound credit Rs 25,000. Within 18 minutes, cash-out Rs 24,200 to a new payee.
Must find SQL. Inbound cashin/p2p_receive then cashout/p2p_send, gap ≤ 30 minutes, cash-out ≥ 80% of first inbound.
Must cite. `T01_first_credit_drain`
Must not cite. `T04_loyal_customer_one_odd`
Hint. high
Gate. Interrupt. Recommend `freeze` or `file_compliance` (fraud desk) as draft only.
Human demo. Officer may change to `watch` via `update_state`.
9.2 Alert A2 — Night bill camouflage then cash-out (`w_imran_isb`)
Story. Between 01:00 and 05:00, ≥ 6 failed utility bills of small amounts, then at 05:12 a successful cash-out Rs 18,000.
Must find SQL. Failed bill count in that window ≥ 6 and a cash-out after the last fail within 2 hours.
Must cite. `T02_night_bill_camouflage`
Gate. Interrupt. Recommend `watch` or `freeze` depending on hint; default propose `watch` if no watchlist, `freeze` if hint high.
9.3 Alert A3 — Shared new payee (`w_sara_lhr` and `w_nadia_lhr`)
Story. Two wallets, both opened recently, send Rs 9,500 and Rs 9,800 the same day to payee `p_new_unknown_1`.
Must find SQL. `wallet_links` row connecting the two, or a query that discovers the shared merchant/payee in 24h.
Must Send. Two `investigate_entity` workers (subject + counterparty).
Must cite. `T03_shared_new_payee`
Gate. Interrupt. Recommend `watch` both or `file_compliance`. Do not freeze both automatically as a recommendation without saying why.
9.4 Alert A4 — Loyal customer, one odd send (`w_ayesha_lhr`)
Story. Eighteen months of grocery and bills. One odd P2P send Rs 12,000 to a cousin-named payee. No night burst. No first-credit pattern.
Must find SQL. Long history of small merchant_debit/bill; single outlier send.
Must cite. `T04_loyal_customer_one_odd` and/or `T07_when_not_to_freeze`
Must not recommend freeze as first recommendation.
Gate. Interrupt still, because amount > demo care threshold of Rs 10,000 *or* because all investigation packs pause. Recommendation: `close` or `watch`.
This alert exists so the system can look *restrained*. It is as important as A1.
9.5 Alert A5 — Already reviewed watchlist (`w_hamza_rwp`)
Story. Wallet is on watchlist with `prior_review`. New txn is a Rs 400 grocery debit, success.
Must find SQL. Active flag `watchlist` plus prior case `decision=close` last month.
Must cite. `T05_already_reviewed_watchlist`
Gate. `NodeInterrupt` because watchlist is active, even though amount is tiny. Recommendation: `close` with note “flag remains; no new typology.”
9.6 Alert A6 — Duplicate merchant debit (`w_ayesha_lhr` second alert)
Story. Two successful Rs 4,500 merchant debits at `m_hussain_general` 11 minutes apart. Prior approved goodwill Rs 800 this quarter exists in `cases`.
Must find SQL. Pair of equal-amount same-merchant success debits within 15 minutes.
Must cite. `T06_duplicate_merchant_debit`
Must use memory. Prior goodwill this quarter → do not propose goodwill; propose investigate one-leg reversal *as a watch/close recommendation*, not freeze.
Gate. Interrupt. Recommended action `close` or `watch` (this is a dispute pattern, not a freeze pattern). Fraud desk still pauses; it does not freeze a duplicate shop debit.

10. SQL schema (implement exactly unless a column is clearly redundant)
CREATE TABLE wallets (  wallet_id     TEXT PRIMARY KEY,  display_phone TEXT NOT NULL,  full_name     TEXT NOT NULL,  city          TEXT NOT NULL,  kyc_tier      TEXT NOT NULL,  status        TEXT NOT NULL,  opened_on     DATE NOT NULL);CREATE TABLE wallet_profiles (  wallet_id          TEXT PRIMARY KEY,  preferred_language TEXT NOT NULL,  typical_use        TEXT,  notes              TEXT,  FOREIGN KEY (wallet_id) REFERENCES wallets(wallet_id));CREATE TABLE merchants (  merchant_id   TEXT PRIMARY KEY,  merchant_name TEXT NOT NULL,  category      TEXT NOT NULL);CREATE TABLE transactions (  txn_id      TEXT PRIMARY KEY,  wallet_id   TEXT NOT NULL,  merchant_id TEXT,  txn_ts      TEXT NOT NULL,  amount_pkr  INTEGER NOT NULL,  direction   TEXT NOT NULL,  txn_type    TEXT NOT NULL,  status      TEXT NOT NULL,  description TEXT,  FOREIGN KEY (wallet_id) REFERENCES wallets(wallet_id),  FOREIGN KEY (merchant_id) REFERENCES merchants(merchant_id));CREATE TABLE wallet_links (  link_id     TEXT PRIMARY KEY,  wallet_a    TEXT NOT NULL,  wallet_b    TEXT NOT NULL,  payee_id    TEXT NOT NULL,  reason      TEXT NOT NULL,  linked_on   TEXT NOT NULL);CREATE TABLE risk_flags (  flag_id   TEXT PRIMARY KEY,  wallet_id TEXT NOT NULL,  flag_type TEXT NOT NULL,  severity  TEXT NOT NULL,  active    INTEGER NOT NULL,  reason    TEXT);CREATE TABLE alerts (  alert_id     TEXT PRIMARY KEY,  wallet_id    TEXT NOT NULL,  opened_at    TEXT NOT NULL,  alert_code   TEXT NOT NULL,  status       TEXT NOT NULL,  seed_story   TEXT NOT NULL);CREATE TABLE cases (  case_id        TEXT PRIMARY KEY,  wallet_id      TEXT NOT NULL,  opened_at      TEXT NOT NULL,  case_type      TEXT NOT NULL,  complaint_text TEXT,  status         TEXT NOT NULL,  decision       TEXT,  amount_pkr     INTEGER,  officer_id     TEXT);CREATE TABLE policy_docs (  policy_id TEXT PRIMARY KEY,  title     TEXT NOT NULL,  topic     TEXT NOT NULL,  md_path   TEXT NOT NULL);CREATE TABLE policy_clauses (  clause_id TEXT PRIMARY KEY,  policy_id TEXT NOT NULL,  rule_text TEXT NOT NULL);CREATE TABLE officers (  officer_id TEXT PRIMARY KEY,  full_name  TEXT NOT NULL,  desk       TEXT NOT NULL);CREATE TABLE officer_prefs (  officer_id      TEXT PRIMARY KEY,  brief_style     TEXT NOT NULL,  language        TEXT NOT NULL,  allow_goodwill  INTEGER NOT NULL);CREATE TABLE txn_features (  wallet_id                 TEXT PRIMARY KEY,  failed_bills_night_7d     INTEGER,  minutes_first_in_to_out   INTEGER,  inout_ratio_6h            REAL,  shared_payee_24h          INTEGER,  prior_goodwill_quarter    INTEGER,  active_watchlist          INTEGER,  txn_count_30d             INTEGER,  updated_at                TEXT);CREATE TABLE alert_labels (  label_id   TEXT PRIMARY KEY,  wallet_id  TEXT,  story_tag  TEXT NOT NULL,  y_freeze_propose INTEGER NOT NULL);CREATE TABLE evidence_packs (  pack_id    TEXT PRIMARY KEY,  alert_id   TEXT NOT NULL,  json_body  TEXT NOT NULL,  created_at TEXT NOT NULL);CREATE TABLE draft_actions (  action_id  TEXT PRIMARY KEY,  alert_id   TEXT NOT NULL,  wallet_id  TEXT NOT NULL,  action     TEXT NOT NULL,  status     TEXT NOT NULL,  created_at TEXT NOT NULL,  signed_at  TEXT,  officer_id TEXT);CREATE TABLE case_events (  event_id   TEXT PRIMARY KEY,  alert_id   TEXT NOT NULL,  event_ts   TEXT NOT NULL,  event_type TEXT NOT NULL,  detail     TEXT);CREATE TABLE memories (  memory_id  TEXT PRIMARY KEY,  namespace  TEXT NOT NULL,  wallet_id  TEXT,  officer_id TEXT,  content    TEXT NOT NULL,  created_at TEXT NOT NULL);CREATE INDEX ix_txn_wallet_ts ON transactions(wallet_id, txn_ts);CREATE INDEX ix_flags_wallet ON risk_flags(wallet_id, active);CREATE INDEX ix_cases_wallet ON cases(wallet_id, opened_at);
Minimum seed counts: 12 wallets, ~20 merchants/payees, 200–400 transactions, 6 alerts, ~10 historical cases, 2 officers (`off_fraud_01`, `off_care_01`), 100 synthetic `alert_labels` rows generated from rule tags not from production.

11. Required SQL tool queries
Implement these as repository functions with bound parameters. Never string-format user text into SQL.
11.1 get_wallet
SELECT w.*, p.preferred_language, p.typical_use, p.notesFROM wallets wJOIN wallet_profiles p ON p.wallet_id = w.wallet_idWHERE w.wallet_id = :wallet_id;
11.2 list_transactions
SELECT t.*, m.merchant_name, m.categoryFROM transactions tLEFT JOIN merchants m ON m.merchant_id = t.merchant_idWHERE t.wallet_id = :wallet_idORDER BY t.txn_ts DESCLIMIT 30;
11.3 find_first_credit_drain
SELECT first.txn_id AS in_id, outt.txn_id AS out_id,       first.amount_pkr AS in_amt, outt.amount_pkr AS out_amt,       first.txn_ts AS in_ts, outt.txn_ts AS out_tsFROM transactions firstJOIN transactions outt  ON first.wallet_id = outt.wallet_id AND outt.txn_ts > first.txn_ts AND first.direction = 'in' AND outt.direction = 'out' AND first.status = 'success' AND outt.status = 'success'WHERE first.wallet_id = :wallet_id  AND ABS(strftime('%s', outt.txn_ts) - strftime('%s', first.txn_ts)) <= 30*60  AND outt.amount_pkr >= 0.8 * first.amount_pkrORDER BY first.txn_tsLIMIT 5;
11.4 find_night_failed_bills
SELECT txn_id, txn_ts, amount_pkr, statusFROM transactionsWHERE wallet_id = :wallet_id  AND txn_type IN ('bill','failed_bill')  AND status = 'failed'  AND CAST(strftime('%H', txn_ts) AS INTEGER) >= 1  AND CAST(strftime('%H', txn_ts) AS INTEGER) < 5  AND txn_ts >= datetime('now', '-7 days')ORDER BY txn_ts;
(For seed data, use fixed timestamps in a demo “as-of” date, e.g. 2026-09-01, and filter against that as-of clock rather than true `now` so tests are deterministic. Implement an `as_of` parameter defaulting to `2026-09-01 12:00:00`.)
11.5 find_shared_payee
SELECT a.wallet_id AS wallet_a, b.wallet_id AS wallet_b,       a.merchant_id, a.amount_pkr AS amt_a, b.amount_pkr AS amt_b,       a.txn_id AS txn_a, b.txn_id AS txn_bFROM transactions aJOIN transactions b  ON a.merchant_id = b.merchant_id AND a.wallet_id < b.wallet_id AND a.direction = 'out' AND b.direction = 'out' AND a.status = 'success' AND b.status = 'success'WHERE a.merchant_id = :payee_id OR a.wallet_id = :wallet_id  AND ABS(strftime('%s', a.txn_ts) - strftime('%s', b.txn_ts)) <= 24*3600;
Also read `wallet_links` for the planted A3 pair.
11.6 get_risk_flags
SELECT flag_type, severity, reasonFROM risk_flagsWHERE wallet_id = :wallet_id AND active = 1;
11.7 list_prior_cases
SELECT case_id, opened_at, case_type, decision, amount_pkr, complaint_textFROM casesWHERE wallet_id = :wallet_idORDER BY opened_at DESCLIMIT 5;
11.8 goodwill_this_quarter
SELECT COUNT(*) AS nFROM casesWHERE wallet_id = :wallet_id  AND decision = 'approved'  AND case_type = 'goodwill'  AND opened_at >= '2026-07-01';
Use the fixed demo calendar: quarter starting 2026-07-01.
11.9 find_duplicate_merchant_debit
SELECT a.txn_id AS txn_1, b.txn_id AS txn_2, a.amount_pkr, a.merchant_id,       a.txn_ts AS ts_1, b.txn_ts AS ts_2FROM transactions aJOIN transactions b  ON a.wallet_id = b.wallet_id AND a.merchant_id = b.merchant_id AND a.amount_pkr = b.amount_pkr AND a.txn_id < b.txn_id AND a.txn_type = 'merchant_debit' AND b.txn_type = 'merchant_debit' AND a.status = 'success' AND b.status = 'success'WHERE a.wallet_id = :wallet_id  AND ABS(strftime('%s', b.txn_ts) - strftime('%s', a.txn_ts)) <= 15*60;

12. Playbook (RAG corpus)
Each file is one clause. First line is title. Second line is `clause_id: T0X_...`. Body is 120–250 words, written as an internal handbook, not as marketing.
Required files and when they should retrieve:
File
Retrieve for
T01_first_credit_drain.md
A1
T02_night_bill_camouflage.md
A2
T03_shared_new_payee.md
A3
T04_loyal_customer_one_odd.md
A4
T05_already_reviewed_watchlist.md
A5
T06_duplicate_merchant_debit.md
A6
T07_when_not_to_freeze.md
A4 primarily; also negative control
T08_pass_through_mule.md
distractor; must NOT be top-1 on A4 or A6
T09_velocity_cashout.md
A1/A2 supporting
T10_goodwill_and_care_desk.md
A6 supporting

Retriever behaviour:
Embed each file as **one chunk** (do not split mid-page)
Return top 3 hits with `clause_id`, title, text, score
`search_playbook` query is built from alert_code + a short SQL findings digest, not from the raw customer message alone
If top score is below a conservative threshold, set `policy_hits=[]` and pack must say “no matching typology — escalate”
Copy clause text into `policy_clauses` so `get_clause(clause_id)` can audit.

13. Risk hint (tiny ML, optional but specified)
13.1 Features (from `txn_features`)
failed_bills_night_7d
minutes_first_in_to_out (null → large sentinel 9999)
inout_ratio_6h
shared_payee_24h
prior_goodwill_quarter
active_watchlist
txn_count_30d
13.2 Model
Logistic regression, class `y_freeze_propose` on synthetic `alert_labels`. Train in `risk/train_hint.py`. Persist `risk/hint_model.joblib`.
If training is skipped, implement an explicit scored rule with the same output space:
high if active_watchlist and (minutes_first_in_to_out <= 30 or shared_payee_24h >= 1)high if minutes_first_in_to_out <= 20 and inout_ratio_6h >= 0.8medium if failed_bills_night_7d >= 6low otherwise
Document which path is active in README.
13.3 Use
`high` → `NodeInterrupt` even if recommended action is watch
Never maps directly to `apply_freeze`
Reasons must be feature names, not “the model is concerned”

14. LangGraph design
14.1 Framework pieces IN
StateGraph, state schema, reducers, nodes, normal edges, conditional edges, START/END, compile, invoke, stream, MessagesState/add_messages, ToolNode, tools_condition, bind_tools, SqliteSaver checkpointer, thread_id, interrupt_before, NodeInterrupt, update_state, get_state, get_state_history, time travel, subgraph investigate_entity, Send, InMemoryStore or Sqlite-backed Store if available, streaming values/updates, LangSmith Studio, langgraph.json, two Assistants, one double-text strategy (`interrupt`).
14.2 Framework pieces OUT
Functional API as main app, create_agent/create_react_agent as the product, Deep Agents, supervisor/swarm packages, LangGraph Cloud as required, Postgres/Redis platform, Store semantic search, MCP, LangGraph.js, free-form SQL tool, freeze as a ReAct tool.
14.3 Parent graph nodes
`load_alert` — SQL load alert + wallet
`gather_sql` — may be one node that calls repo functions deterministically (preferred for reliability) OR an analyst LLM + ToolNode limited to read tools
`retrieve_playbook`
`score_hint`
`plan_sends` — conditional: if related_wallet_ids else skip
`investigate_entity` — subgraph, targeted by Send
`write_pack` — structured output
`gate` — sets gate_reason; may raise NodeInterrupt
`await_human` — interrupt_before this or before apply nodes
`apply_action` — only if state.signed and human_decision in allowed set
`write_memory`
`persist_pack` — write evidence_packs + case_events
Recommended topology:
START -> load_alert -> [gather_sql | retrieve_playbook | score_hint] in parallel      -> merge      -> plan_sends --Send--> investigate_entity --> merge evidence      -> write_pack      -> gate      -> interrupt      -> apply_action      -> persist_pack      -> write_memory      -> END
Parallel gather requires reducers on `policy_hits` and a merge node that builds `sql_findings`.
14.4 Subgraph `investigate_entity`
Input: `{entity_wallet_id, role}`.
Nodes: list_transactions, summarise_entity (LLM or template).
Output: EvidenceMemo.
Do not freeze from inside the subgraph.
14.5 Interrupt rules (implement in `graph/gates.py`)
Always `interrupt_before=["apply_action"]`.
Raise `NodeInterrupt` when any of:
active watchlist
risk_hint == high
recommended_action in {freeze, file_compliance}
any linked wallet count ≥ 2
A1, A2, A3, A5 must interrupt. A4 and A6 must also interrupt (global pause before apply), but recommendation must not be freeze.
14.6 Signing protocol
`apply_action` runs only if:
state.signed is Trueand state.human_decision is not Noneand state.human_decision == the action being applied
`update_state` from the officer must set `signed=True`, `human_decision`, optional `human_comment`. Passing `None` to resume without those fields must refuse to apply freeze.
14.7 Assistants
Same compiled graph, different config:
Assistant
desk_role
allow_goodwill language
default propose freeze?
gawah_fraud
fraud
no
yes when A1-like
gawah_care
care
yes in prose only
no; prefer watch/close

Config keys: `officer_id`, `desk_role`, `user_id` for Store namespace.
14.8 Memory namespaces
`("profile", wallet_id)` — facts: language, already reviewed, goodwill used
`("cases", wallet_id)` — one memory per closed alert
`("procedure", officer_id)` — brief_style
Write after persist. Read in `load_alert` and inject a short “known facts” block into pack writing.

15. Application tools vs gated nodes
Bind to the model (read-only):
get_wallet
list_transactions
find_first_credit_drain
find_night_failed_bills
find_shared_payee
get_risk_flags
list_prior_cases
goodwill_this_quarter
find_duplicate_merchant_debit
search_playbook
get_clause
Not bound to the model:
apply_freeze
open_compliance_case
mark_watch
save_memory (graph node may call repo directly)
Preferred implementation for v1: deterministic gather nodes that call repos, not an open ReAct loop. Add a small ReAct analyst only if deterministic gather is working. Reliability beats agent theatrics.

16. Evaluation (mandatory)
File `evals/golden.yaml` with one record per alert:
alert_id: A1wallet_id: w_bilal_khimust_interrupt: truemust_sql_tool_hits:  - find_first_credit_drainmust_cite_any:  - T01_first_credit_drainmust_not_cite:  - T04_loyal_customer_one_oddmust_not_recommend:  - closeforbid_unsigned_freeze: true
`evals/test_goldens.py` must:
Build a fresh DB from seeds
Rebuild features
For each alert, invoke graph with a thread_id
Assert `next` node is the interrupt / apply_action pending
Assert cited ids ⊆ retrieved ids
Invoke apply_action without signed=True and assert no `draft_actions` row with status executed/approved freeze
update_state signed + decision, resume, assert event written
A4 assertion: `recommended_action` in {close, watch}.
A5 assertion: interrupt despite amount 400.

17. Demo script for LinkedIn (90 seconds)
Open Studio on A1. Show parallel gather.
Show pack with T01 citation and txn ids.
Show graph sitting on the gate.
Officer changes freeze → watch. Resume.
Switch to A4. Show T07 / T04 and recommendation watch/close.
Optional: time-travel A1 from pre-gate checkpoint.
README title line:
> SQL shows what moved. The playbook shows which pattern might apply. LangGraph will not freeze a wallet until a human signs the pack.

18. Implementation order (do not reorder)
`schema.sql` + seeds until queries in Section 11 return planted rows for A1–A6
Playbook markdown + retriever unit test (A1 query retrieves T01 in top 3)
Domain objects + empty graph that loads an alert and ENDs
Deterministic gather + write_pack template (no LLM yet)
Interrupts + unsigned freeze refusal test
Subgraph + Send for A3
LLM pack writer with citation filter
Store memory for A5/A6
Risk hint
Two assistants
Golden test file green
README + Loom
Do not start step 7 before step 1 queries work.

19. Dependencies (suggested)
langgraphlangchainlangchain-openailangchain-corelanggraph-checkpoint-sqlitechromadb          # or faiss-cpusentence-transformers   # optional local embeddingsscikit-learnpydanticpython-dotenvpytest
Chat model: whatever the implementer has keys for (OpenAI gpt-4o-mini is enough). Temperature 0 for pack writer.

20. Configuration
`.env.example`:
OPENAI_API_KEY=LANGSMITH_API_KEY=LANGSMITH_TRACING=trueLANGSMITH_PROJECT=gawah-fileGAWAH_AS_OF=2026-09-01T12:00:00GAWAH_OPS_DB=data/gawah_ops.dbGAWAH_GRAPH_DB=data/gawah_graph.db
`langgraph.json` graphs key points at `studio/desk_graph.py:graph`.

21. Seed identity table (use these ids)
Wallets:
w_ayesha_lhr — loyal customer, A4 and A6
w_bilal_khi — new, A1
w_imran_isb — night bills, A2
w_sara_lhr — shared payee, A3
w_nadia_lhr — shared payee, A3
w_hamza_rwp — watchlist, A5
w_filler_01..06 — padding history only
Payees/merchants:
m_hussain_general — grocery
m_kelectric — utility
p_new_unknown_1 — unknown payee for A3
p_cashout_desk_1 — cash-out
p_cousin_umair — A4 odd send
Officers:
off_fraud_01 — Farah, fraud, brief_style=tables
off_care_01 — Omar, care, brief_style=paragraph, allow_goodwill=1
Alerts:
A1..A6 as specified
Historical case for Ayesha: case_goodwill_ayesha_q3, approved goodwill 800, opened_at 2026-08-10.
Historical case for Hamza: case_hamza_review_aug, decision close, opened_at 2026-08-15.

22. Playbook page template
# First credit then drainclause_id: T01_first_credit_draintopic: first_credit_drainWhen a wallet’s first successful inbound credit is followed within 30 minutesby an outbound cash-out or send of 80% or more of that credit, treat thepattern as a possible first-credit drain.The desk may propose freeze or compliance filing only as a draft.A human must sign.Do not use this clause for long-tenured wallets with mixed grocery and billhistory and a single odd send.
Write the other nine pages in the same shape. T07 must explicitly say long-good customers with one odd P2P are not freeze-first.

23. README contents (required sections)
What this is / what this is not
Three-plane diagram
How to seed the DB
How to run Studio
The six alerts and expected pauses
LangGraph pieces used
LangGraph pieces refused
Synthetic data disclaimer

24. Interview talking points (do not put as code comments everywhere)
Decision system, not a chatbot
Leakage: features use only data at alert time; do not include the eventual human decision as a feature
Accuracy trap: a fluent pack can still be blocked by a watchlist row
RAG without citation is a failed retrieve
HITL is the product
Map-reduce is for linked wallets, not decoration

25. Explicit instructions to a coding agent
You are implementing Gawah File from this specification.
Create the repo tree in Section 6.
Implement schema and seeds so Section 11 queries return rows for A1–A6. Print those query results in a script `scripts/check_seeds.py` and stop if any golden query is empty.
Implement retriever unit test next.
Implement the graph with deterministic gather first.
Do not expose apply_freeze to bind_tools.
Do not add FastAPI or Streamlit until goldens pass. Studio is the UI.
If a choice is unspecified, pick the simpler option and document it in README.
If you add a table or node not in this spec, you must justify it in README under “Deviations.”
Keep all customer strings obviously fake.
Temperature 0 on any node that writes the EvidencePack.
End of specification.