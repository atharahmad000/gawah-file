GAWAH FILE
Phase-wise implementation plan
Prerequisites, work, pass/fail checks, and debug notes for every phase. Do not start Phase N until Phase N-1 is green. Companion to Gawah_File_Project_Proposal.docx. 12 September 2026.
Companion to Gawah_File_Project_Proposal.docx.
Follow phases in order. Do not start Phase N until Phase N-1 checks are green.
Do not start a UI, embeddings, or an LLM pack-writer before the planted SQL stories exist.
Non-negotiable: the model may gather, cite, and propose. It may not freeze, unfreeze, or open a compliance case until a human sets signed=True.
As-of clock for all time filters: 2026-09-01T12:00:00 (env GAWAH_AS_OF). Never use datetime('now') in golden tests.
How to use this plan
Each phase has the same shape:
Goal
Prerequisites (what must already exist)
Work (exact files and actions)
Checks (pass/fail)
Debug if a check fails
Exit criteria (you may proceed only after this)
If a check fails, stop. Fix that phase. Do not “make progress” by adding the next plane.
Suggested calendar if working evenings: Phases 0–2 (days 1–2), 3–5 (days 3–4), 6–8 (days 5–7), 9–11 (days 8–10), 12–15 (days 11–14).
Phase 0 — Machine and empty repo
Goal
A Python environment that can import LangGraph and create two SQLite files. No product logic yet.
Prerequisites
Python 3.11, 3.12, or 3.13 (`python3 --version`)
pip and venv
Git optional
An OpenAI-compatible key is NOT required until Phase 10
Work
Create folder `gawah-file/` with the tree from the proposal (empty packages with `__init__.py` are allowed).
Create `venv` and install at least: `langgraph`, `langchain-core`, `pydantic`, `python-dotenv`, `pytest`.
Create `.env` from `.env.example` with `GAWAH_AS_OF`, `GAWAH_OPS_DB=data/gawah_ops.db`, `GAWAH_GRAPH_DB=data/gawah_graph.db`.
Create empty directories `data/`, `seeds/`, `playbook/`, `evals/`.
Write `repos/db.py` that opens `gawah_ops.db` only.
Checks
`python3 --version` prints 3.11+
`python -c "import langgraph, pydantic; print('ok')"` prints ok
`data/` exists and is writable
`repos/db.py` can `connect()` and `SELECT 1`
Debug
Wrong Python: recreate venv with `python3.12 -m venv .venv`
Import error: `pip install -r requirements.txt` inside the activated venv
Cannot write data/: you are in the wrong working directory
Exit criteria
Imports work. Ops DB connection works. Graph DB file does not exist yet (or is empty). No wallets table required.
Phase 1 — Schema
Goal
`gawah_ops.db` contains every table from the proposal schema. No rows except what SQLite creates.
Prerequisites
Phase 0 green.
Work
Write `seeds/schema.sql` exactly as specified (wallets, wallet_profiles, merchants, transactions, wallet_links, risk_flags, alerts, cases, policy_docs, policy_clauses, officers, officer_prefs, txn_features, alert_labels, evidence_packs, draft_actions, case_events, memories + indexes).
Write `seeds/build_db.py` that deletes `data/gawah_ops.db` if present, applies schema.sql, prints table names.
Run `python seeds/build_db.py`.
Checks
sqlite3 data/gawah_ops.db ".tables"
Must list all tables above.
sqlite3 data/gawah_ops.db "PRAGMA table_info(transactions);"
Must include txn_id, wallet_id, merchant_id, txn_ts, amount_pkr, direction, txn_type, status, description.
Foreign keys: enable `PRAGMA foreign_keys=ON;` in db.py for every connection.
Debug
Missing table: schema.sql not fully executed; print each statement’s error
Duplicate table on rerun: build_db must drop/recreate the file, not “CREATE IF NOT EXISTS” forever
FK ignored: connection did not set foreign_keys=ON
Exit criteria
Fresh DB from one command. Schema matches the proposal. Zero seed stories yet.
Phase 2 — Identity seeds (wallets, merchants, officers)
Goal
The people and shops exist. No transactions yet.
Prerequisites
Phase 1 green.
Work
Insert exactly these identities (do not rename; goldens depend on ids):
Wallets:
w_ayesha_lhr — Ayesha, Lahore, full KYC, active, opened 2025-01-15
w_bilal_khi — Bilal, Karachi, basic KYC, active, opened 2026-08-28
w_imran_isb — Imran, Islamabad, full KYC, active, opened 2025-11-02
w_sara_lhr — Sara, Lahore, basic, active, opened 2026-08-20
w_nadia_lhr — Nadia, Lahore, basic, active, opened 2026-08-21
w_hamza_rwp — Hamza, Rawalpindi, full, active, opened 2024-06-01
w_filler_01 to w_filler_06 — padding, active, mixed cities
Profiles: language ur/en, typical_use, notes as in the proposal (Ayesha grocery+bills; Bilal new wallet; Hamza prior review note).
Merchants/payees:
m_hussain_general — grocery
m_kelectric — utility
p_new_unknown_1 — unknown
p_cashout_desk_1 — cashout
p_cousin_umair — p2p
plus ~15 fillers (grocery, utility, p2p)
Officers:
off_fraud_01 Farah desk=fraud brief_style=tables allow_goodwill=0
off_care_01 Omar desk=care brief_style=paragraph allow_goodwill=1
Checks
SELECT COUNT(*) FROM wallets;          -- >= 12SELECT COUNT(*) FROM merchants;        -- >= 20SELECT wallet_id FROM wallets WHERE wallet_id='w_ayesha_lhr';SELECT desk FROM officers WHERE officer_id='off_fraud_01';  -- fraud
FK check: inserting a profile for a missing wallet_id must fail.
Debug
Count short: seed file not executed after schema
FK fail on good rows: you inserted profiles before wallets — order must be wallets → profiles → merchants → officers → prefs
Exit criteria
All canonical ids exist. You can explain each hero wallet in one sentence.
Phase 3 — Plant the six stories in the ledger
Goal
Transactions, links, flags, historical cases, and alerts make A1–A6 discoverable by the specified SQL.
Prerequisites
Phase 2 green. Keep GAWAH_AS_OF = 2026-09-01T12:00:00.
Work
Write seeds so these facts are true. Use ISO timestamps on 2026-08-31 / 2026-09-01.
A1 w_bilal_khi
First inbound success Rs 25000 at 2026-08-31 14:00:00 (cashin or p2p_receive, direction in)
Outbound Rs 24200 at 2026-08-31 14:18:00 to p_cashout_desk_1 (direction out)
Almost no earlier history
A2 w_imran_isb
At least 6 failed bills between 01:00 and 05:00 on 2026-09-01, small amounts
Cash-out success Rs 18000 at 2026-09-01 05:12:00
Some normal daytime bills earlier in August so the wallet is not brand new
A3 w_sara_lhr and w_nadia_lhr
Sara sends 9500 to p_new_unknown_1 on 2026-08-31 16:00 success out
Nadia sends 9800 to p_new_unknown_1 on 2026-08-31 16:40 success out
Row in wallet_links connecting them with that payee
A4 w_ayesha_lhr
~30 small grocery/bill txns across 2026-07 and 2026-08
One p2p out Rs 12000 to p_cousin_umair on 2026-08-31 19:10
No night-fail burst, no first-credit drain
A5 w_hamza_rwp
Active risk_flags watchlist + prior_review
One grocery debit Rs 400 success 2026-09-01 10:00 m_hussain_general
Historical case closed last month (2026-08-15, decision close)
A6 same wallet w_ayesha_lhr
Two merchant_debit success Rs 4500 at m_hussain_general at 2026-08-31 11:00 and 11:11
Historical case goodwill approved 800 on 2026-08-10 case_type=goodwill
Alerts table rows A1–A6 with wallet_id, alert_code, seed_story, status=open, opened_at 2026-09-01 11:00.
Padding: extra txns for fillers so the DB does not look like six isolated rows. Padding must not accidentally create a second first-credit-drain on Ayesha or Hamza.
Checks — run these exact queries after seed (scripts/check_seeds.py)
A1 first-credit drain query for w_bilal_khi returns at least one row pairing the 25000 and 24200 txns.
A2 night failed bills for w_imran_isb with as_of 2026-09-01 returns count >= 6. A later cash-out exists after the last fail.
A3 shared payee or wallet_links returns sara+nadia+p_new_unknown_1.
A4 duplicate-debit query for Ayesha still reserved for A6; first-credit drain query for Ayesha returns ZERO rows.
A5 SELECT from risk_flags where wallet_id=w_hamza_rwp and active=1 returns watchlist.
A6 duplicate merchant debit query returns the two 4500 ids. goodwill_this_quarter for Ayesha returns >= 1.
SELECT alert_id, wallet_id FROM alerts ORDER BY alert_id;
Must be A1..A6 with the wallets above.
check_seeds.py must exit non-zero if any golden query is empty (except A4 drain which must be empty).
Debug
Drain query empty: direction/type/status mismatch (in vs out, success vs pending), or gap > 30 minutes, or out amount < 80%
Night bills empty: hours not 01–04 inclusive; you stored local strings that sqlite strftime cannot parse — use `YYYY-MM-DD HH:MM:SS`
Ayesha accidentally matches drain: you gave her a large inbound immediately before the cousin send — change times or amounts
Duplicate pair missing: types not merchant_debit, or one status failed, or gap 16+ minutes
Goodwill count 0: opened_at before 2026-07-01 or case_type not exactly goodwill or decision not approved
Shared payee miss: different merchant_ids (typo p_new_unknown1)
Exit criteria
`python scripts/check_seeds.py` prints PASS for A1–A6 story queries. This is the most important gate in the project. Do not proceed if it is amber.
Phase 4 — Repository layer (SQL behind functions)
Goal
Python functions that run the proposal queries with bound parameters. No LLM. No raw SQL strings built from user text.
Prerequisites
Phase 3 check_seeds green.
Work
Implement:
repos/db.py — get_conn(), as_of()
repos/wallets.py — get_wallet
repos/ledger.py — list_transactions, find_first_credit_drain, find_night_failed_bills, find_shared_payee, find_duplicate_merchant_debit
repos/alerts.py — get_alert, list_open_alerts
repos/cases.py — list_prior_cases, goodwill_this_quarter
repos/flags.py — get_risk_flags
repos/playbook_sql.py — get_clause (may be empty until Phase 5)
Every function returns plain dicts/lists. None of them call an LLM.
Checks
Write `tests/test_repos.py` (or run a small script):
get_wallet("w_bilal_khi")["city"] == "Karachi"len(find_first_credit_drain("w_bilal_khi")) >= 1len(find_first_credit_drain("w_ayesha_lhr")) == 0len(find_duplicate_merchant_debit("w_ayesha_lhr")) >= 1len(get_risk_flags("w_hamza_rwp")) >= 1goodwill_this_quarter("w_ayesha_lhr") >= 1get_alert("A1")["wallet_id"] == "w_bilal_khi"
Pass a malicious string as wallet_id and assert no crash / no extra tables dropped (parameter binding).
Debug
Functions work in sqlite CLI but not Python: you opened a different db path
Empty lists: as_of clock not applied; night query used datetime('now')
Integrity error on later writes: you reused connections across threads without check_same_thread handling
Exit criteria
Repo tests pass. Graph code does not exist yet except perhaps unused imports.
Phase 5 — Playbook files and SQL audit copy
Goal
Ten markdown clauses on disk and mirrored into policy_docs / policy_clauses.
Prerequisites
Phase 4 green.
Work
Create playbook/T01_... through T10_... using the proposal template (title, clause_id line, 120–250 words).
T07 must say long-good + one odd P2P is not freeze-first.
T08 is a distractor mule page.
Write seeds/seed_playbook_sql.py that reads the markdown and upserts policy_docs + policy_clauses.
Checks
SELECT clause_id FROM policy_clauses ORDER BY 1;
Contains T01_first_credit_drain … T10_goodwill_and_care_desk.
`get_clause("T01_first_credit_drain")` returns text containing “30 minutes” or equivalent rule.
Each file’s second line matches clause_id in SQL.
Debug
Missing T0X: filename vs clause_id mismatch
Duplicate ids: upsert not insert-or-replace
Garbled text: encoding; save utf-8
Exit criteria
Handbook exists as files AND as SQL rows. RAG index not required yet.
Phase 6 — RAG retriever
Goal
search_playbook(query) returns top 3 clause hits with ids. A1-style query retrieves T01 in top 3. A4-style query retrieves T04 or T07, not T01 as top-1.
Prerequisites
Phase 5 green. Now you may add chromadb or faiss + embeddings. API key optional if using sentence-transformers locally.
Work
retrieve/playbook_index.py — build index from playbook/*.md, one chunk per file, persist under data/playbook_index/
retrieve/retriever.py — search_playbook(query, k=3) -> [{clause_id, title, text, score}]
scripts/build_index.py
tests/test_retriever.py with fixed queries
Query construction for tests (do not yet wire the graph):
A1 query: "first inbound credit then cash-out within 30 minutes 80 percent"
A4 query: "loyal long customer single odd p2p send do not freeze"
A6 query: "two equal merchant debits same shop eleven minutes"
Checks
Rebuild index from scratch twice; second build does not duplicate ids
A1 query: T01 in top 3
A4 query: T01 is not rank 1; T04 or T07 in top 3
A6 query: T06 in top 3
Unknown query “hospital cash waiting period” may return weak scores; document threshold behaviour
Debug
Always T01: query text too similar; add distinctive sentences to T04/T07; do not chunk files into tiny overlapping windows
Empty index: build script pointed at wrong folder
clause_id missing on hits: parse the `clause_id:` line when indexing, do not guess from filename only (do both as a sanity check; they must match)
Exit criteria
Unit tests for three queries pass without any LangGraph import.
Phase 7 — Domain models and empty graph
Goal
CaseState compiles. A graph loads A1 and ends without tools. Checkpointer writes to gawah_graph.db only.
Prerequisites
Phases 4 and 6 exist (retriever need not be called yet).
Work
domain/enums.py
domain/state.py — CaseState with reducers on messages, evidence, policy_hits, related_wallet_ids
graph/desk.py — nodes: load_alert -> END
studio/desk_graph.py exports `graph = builder.compile(checkpointer=SqliteSaver(gawah_graph.db))`
Invoke with config thread_id=A1 and input {alert_id: A1, officer_id: off_fraud_01}
Checks
After invoke, get_state(thread).values["wallet_id"] == w_bilal_khi
data/gawah_graph.db exists and grew
data/gawah_ops.db row counts unchanged (graph did not write ledger)
Visual: graph.get_graph().draw_mermaid() contains load_alert
Debug
Reducer error on compile: Annotated import / add_messages missing
wallet_id empty: load_alert did not call get_alert
Checkpointer wrote into ops db: wrong path
“no current event loop” / thread errors: run invoke in a plain script first, not inside a broken notebook kernel
Exit criteria
One alert loads into state. No gather, no LLM, no interrupt yet.
Phase 8 — Deterministic gather (no LLM)
Goal
Parent graph fills sql_findings, policy_hits, related_wallet_ids, risk_hint placeholder by calling repos + retriever directly.
Prerequisites
Phase 7 green. Prefer one node `gather_sql` plus one node `retrieve_playbook` plus merge. Do not add ReAct yet.
Work
Nodes:
gather_sql: run get_wallet, list_transactions, all find_* for that wallet, flags, prior cases, goodwill. Put compact results in sql_findings. If shared payee hits, set related_wallet_ids.
retrieve_playbook: build query from alert_code + a short digest of sql_findings (template string, no LLM). Call search_playbook. Store policy_hits.
merge: no-op join after parallel edges.
score_hint_stub: write risk_hint="low" always (real model is Phase 13).
Parallel: gather_sql and retrieve_playbook can run after load_alert if reducers are correct. If parallel update of the same keys is painful, run them sequentially first. Sequential is acceptable for this phase.
Checks
Invoke A1:
sql_findings contains the drain pair txn ids
policy_hits contains T01
related_wallet_ids empty (or only subject)
Invoke A3:
related_wallet_ids contains w_sara_lhr and w_nadia_lhr (or the counterpart of the subject)
Invoke A5:
sql_findings flags include watchlist
Invoke A6:
duplicate pair present
goodwill count >= 1
Print state after each invoke. Save outputs under /tmp if needed; do not commit secrets.
Debug
InvalidUpdateError: two nodes wrote the same key without a reducer — make gather write sql_findings only, retriever write policy_hits only
policy_hits empty: digest query too vague; reuse the Phase 6 test query strings keyed by alert_code as a fallback map
related wallets empty on A3: gather did not call find_shared_payee / wallet_links
Parallel flake: switch to sequential edges until stable
Exit criteria
For all six alerts, state after gather has the planted facts. Still no EvidencePack LLM. Still no freeze node.
Phase 9 — Template EvidencePack (still no LLM)
Goal
write_pack_template builds EvidencePack from state with deterministic rules. This proves the product voice before you spend tokens.
Prerequisites
Phase 8 green.
Work
Implement pack/rules.py:
If drain hit and wallet opened within 14 days of as_of -> recommend freeze (draft only), cite T01 if present
If night fails >=6 and later cashout -> recommend watch or freeze if hint high, cite T02
If shared payee -> recommend watch or file_compliance, cite T03
If Ayesha-like long history + one odd p2p and no drain -> recommend watch or close, cite T04/T07, never freeze
If watchlist + tiny grocery -> recommend close, cite T05
If duplicate debit -> recommend watch/close, cite T06, never freeze
clause_ids_cited = intersection of desired ids and policy_hits ids only
Node write_pack writes pack + proposed_action.
Checks
A1 proposed_action in {freeze, file_compliance}
A4 proposed_action in {close, watch}
A5 proposed_action == close
A6 proposed_action in {close, watch}
A1 clause_ids_cited includes T01
A4 clause_ids_cited does not include T01 unless it was retrieved AND rules require it — it should not
Every cited id ∈ policy_hits
Debug
A4 wants freeze: your drain query is matching Ayesha; go back to Phase 3
Cited id not in hits: writer used a hardcoded id; filter it
Pack None: node returned wrong key name vs state schema
Exit criteria
Six packs look right with zero LLM cost. Keep this template as a fallback if the LLM is down.
Phase 10 — Gate and human sign-off
Goal
Graph always stops before apply_action. Unsigned resume cannot write an approved freeze. Signed update_state can.
Prerequisites
Phase 9 green.
Work
graph/gates.py — should_force_interrupt(state) from proposal rules
compile interrupt_before=["apply_action"]
gate node may raise NodeInterrupt when watchlist or hint high or recommended freeze/file or linked wallets >= 2
apply_action node:
  - if not state.signed: write case_event "refused_unsigned" and return
  - if human_decision is freeze: insert draft_actions approved/executed only then (still: you may insert as approved and not literally freeze a wallet row unless you also set wallets.status; prefer draft_actions.status=approved and a case_event; optionally set wallet status frozen for A1 after sign-off)
  - never bind apply_action as a tool
Script scripts/demo_gate.py:
  1. invoke A1 until interrupt
  2. try stream(None) without signed -> no approved freeze row
  3. update_state signed=True human_decision=watch
  4. resume -> draft_actions watch approved, freeze not executed
Checks
After first A1 invoke, get_state().next includes apply_action or the interrupt is visible in tasks
draft_actions has no approved freeze before step 3
After signed watch, freeze still not approved
Repeat A5: interrupt happens despite Rs 400
wallets.status for Bilal remains active until/unless you explicitly implement freeze-on-sign and the human chose freeze
Debug
Graph does not stop: compile() missing interrupt_before; or you named the node apply_actions
Resume with None applies freeze: apply_action ignored signed flag
update_state wiped messages: set as_node correctly; pass only the keys you mean to change
Checkpointer missing: interrupt cannot persist; compile with SqliteSaver
Exit criteria
You can demonstrate the product sentence: it prepares a pack and will not commit a freeze without a signature.
Phase 11 — Subgraph and Send (Alert A3)
Goal
When related_wallet_ids has more than the subject, fan out investigate_entity workers and append EvidenceMemos.
Prerequisites
Phase 10 green. A3 related_wallet_ids already populated.
Work
graph/investigate_entity.py subgraph: load entity txns (repo), write EvidenceMemo via template (no LLM required)
plan_sends node returns list of Send("investigate_entity", {entity_wallet_id, role})
evidence reducer appends
write_pack includes linked wallet memos
Checks
A3 invoke:
at least two evidence memos
pack.linked_wallets includes both sara and nadia
Studio/mermaid shows fan-out
A1 invoke:
zero or one memo; no crash if Send list empty
A4 invoke:
no spurious second wallet
Debug
InvalidUpdateError on evidence: reducer not Annotated add
Send payload missing required subgraph state keys — give the subgraph its own schema or overlapping keys as in the course
Infinite loop: subgraph ends at END; do not Send back to plan_sends without a guard
Only one worker: related_wallet_ids not a list of unique ids
Exit criteria
A3 is visibly map-reduce. Other alerts still pass Phase 10 checks.
Phase 12 — LLM pack writer with citation filter
Goal
Replace or wrap the template writer with structured output, without allowing hallucinated clause ids.
Prerequisites
Phase 11 green. OPENAI_API_KEY (or equivalent) now required.
Temperature 0.
Work
write_pack_llm node: prompt contains only retrieved clause texts + sql_findings + memory block
with_structured_output(EvidencePack)
Post-filter: drop any clause_ids_cited not in policy_hits; if recommended freeze on A4/A6, override to watch and record "policy_guard"
Keep template writer as fallback if API fails
Do not put raw_tool_dumps in the prompt
Checks
A1 LLM pack still cites T01 (or T09), still pauses
A4 still not freeze after guard
Force a unit test: feed a fake model output citing T08 when T08 was not retrieved; filter removes T08
Token use is small (prompt should not include full 30-txn dumps; cap list_transactions to 15 in the prompt)
Debug
Hallucinated ids: filter missing; tighten prompt “cite only ids in this list: [...]”
JSON parse errors: use with_structured_output, reduce optional fields
A4 freeze again: guard not applied after LLM
Slow/expensive: you sent whole ledger; truncate
Exit criteria
LLM improves prose. Guards keep A4/A6 honest. Goldens still pass if API is mocked with the template.
Phase 13 — Risk hint
Goal
txn_features filled. hint.py returns low|medium|high. High forces NodeInterrupt even on small amounts.
Prerequisites
Phase 10–11 green. scikit-learn optional.
Work
features_sql.py rebuilds txn_features for all wallets using as_of
Implement rule path from the proposal first (always available)
Optional: train logistic on alert_labels; if model file missing, use rules
score_hint node overwrites stub
gates.py: hint==high => NodeInterrupt
Checks
SELECT * FROM txn_features WHERE wallet_id='w_bilal_khi';
minutes_first_in_to_out should be ~18.
Bilal hint is high.
Ayesha A4 hint is low or medium, not high because of drain.
Hamza hint high or medium because watchlist — interrupt already required.
Unit test: active_watchlist=1 and tiny amount => high or at least interrupt.
Debug
Features all null: rebuild not run after seed
minutes 9999 on Bilal: inbound not marked direction=in
Everyone high: thresholds too tight; print feature rows
Model file unpickle error: fall back to rules and document in README
Exit criteria
Hint is visible on the pack. It never writes draft freeze by itself.
Phase 14 — Long-term memory
Goal
Second thread on Ayesha sees goodwill-already-used. Hamza sees prior review. Officer prefs affect pack style.
Prerequisites
Phase 12 green.
Work
Store (InMemoryStore is fine for demo; mirror writes to memories table)
Namespaces: (profile, wallet_id), (cases, wallet_id), (procedure, officer_id)
load_alert reads store and puts a short known_facts string into state
write_memory after signed apply
Seed initial memories for Ayesha goodwill and Hamza prior review so the first demo thread already shows memory (do not wait for a previous run)
Checks
Invoke A6 with officer off_fraud_01: pack mentions goodwill already used this quarter (from SQL and/or memory)
Invoke A5: pack mentions prior review
Invoke A1 twice on different thread_ids after first was signed watch: second load sees a case memory
memories table rows increase after signed apply
Ops ledger row count unchanged except draft_actions/events/packs/memories
Debug
Memory empty: write_memory not reached because you never signed
Wrong wallet memory: namespace tuple order
Store lost on process restart: expected for InMemoryStore; either seed on startup or switch to a file-backed store later
Exit criteria
A5 and A6 packs show cross-case facts without the officer pasting them.
Phase 15 — Assistants and one double-text behaviour
Goal
Same graph, two configs. A second message mid-run does not corrupt sql_findings.
Prerequisites
Phase 14 green. langgraph.json points at studio/desk_graph.py:graph
Work
Assistants conceptually: gawah_fraud vs gawah_care via configurable desk_role
Care desk prompt/guard: never recommend freeze as first choice; prefer watch/close
Fraud desk may recommend freeze on A1 only as draft
Double-text: document multitask_strategy=interrupt; add a test that starts A1 then updates with extra human message while waiting at gate; state still has original drain findings
Checks
A1 + fraud config: proposed freeze allowed
A1 + care config: proposed watch/close (guard)
langgraph dev starts; Studio shows the graph
Double-text test does not drop wallet_id
Debug
Studio cannot find graph: langgraph.json graph path wrong; cwd not studio/
Care still freezes: guard only in template, not LLM path
Double-text error 409: expected if you chose reject; switch to interrupt as specified
Exit criteria
Two desks visible. Studio runs locally. One documented double-text path.
Phase 16 — Golden suite (project definition of done)
Goal
evals/test_goldens.py is the only “done” signal.
Prerequisites
Phases 3, 6, 10, 11, 12, 13, 14.
Work
Implement evals/golden.yaml exactly from the proposal.
test_goldens.py rebuilds DB + index, runs each alert, asserts:
must_interrupt
planted SQL tool/repo hits
must_cite_any ⊆ pack.clause_ids_cited ⊆ policy_hits ids
must_not_cite not present
must_not_recommend respected
unsigned freeze absent
after signed decision, case_events has approved/rejected as expected
Run: `pytest evals/test_goldens.py -q`
Checks
All six alerts green in one command on a clean DB.
Debug
Order-dependent tests: always rebuild DB in fixture
Time-dependent: as_of not injected
LLM flake: allow template fallback in CI, or record structured outputs; goldens must not require a live model if GAWAH_OFFLINE=1
Exit criteria
pytest green twice in a row. This is the project finish line.
Phase 17 — Demo artifacts only after goldens
Goal
README, architecture paragraph, 90-second script. No new features.
Prerequisites
Phase 16 green.
Work
README sections from the proposal.
Record Studio on A1 (gate) and A4 (restraint).
Optional time-travel: get_state_history on A1, fork before apply, choose watch.
Checks
A stranger can clone, create venv, run build_db, build_index, pytest, langgraph dev using README only
README states synthetic data and “not a detector”
No API keys committed
Debug
Clone fail: seeds assume absolute paths — use paths relative to repo root
Studio fail: missing langgraph.json dependencies
Exit criteria
Portfolio-ready. Stop building.
Cross-phase debugging map
Symptom
Go back to
Drain/duplicate/night query empty
Phase 3 seeds
Repo functions empty but CLI sqlite works
Phase 4 db path
Retriever always same clause
Phase 6 chunking/queries
InvalidUpdateError
Phase 8 reducers
Graph does not pause
Phase 10 interrupt_before + checkpointer
Unsigned freeze written
Phase 10 apply_action guard
A3 no fan-out
Phase 11 Send + related_wallet_ids
LLM cites missing clause
Phase 12 filter
Everyone risk=high
Phase 13 features
Second ticket forgets goodwill
Phase 14 Store seed/write
pytest flakes
Phase 16 offline mode + rebuild fixture
Want a React app
Do not. Phase 17 only

What you never do in any phase
Mix gawah_ops.db and gawah_graph.db
Let the model write SQL
Bind freeze as a tool
Train a “real fraud model” on public datasets
Add Supervisor/Swarm/Deep Agents
Start Phase 12 before Phase 3 and Phase 10 are green
One-page sequence
0 env → 1 schema → 2 identities → 3 planted stories + check_seeds
→ 4 repos → 5 playbook files → 6 retriever tests
→ 7 empty graph loads A1 → 8 deterministic gather
→ 9 template pack → 10 gate + unsigned freeze fails
→ 11 Send on A3 → 12 LLM + citation filter
→ 13 hint → 14 memory → 15 assistants/Studio
→ 16 pytest goldens → 17 README/demo → stop