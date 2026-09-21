CREATE TABLE wallets (  wallet_id     TEXT PRIMARY KEY,  display_phone TEXT NOT NULL,  full_name     TEXT NOT NULL,  city          TEXT NOT NULL,  kyc_tier      TEXT NOT NULL,  status        TEXT NOT NULL,  opened_on     DATE NOT NULL);

CREATE TABLE wallet_profiles (  wallet_id          TEXT PRIMARY KEY,  preferred_language TEXT NOT NULL,  typical_use        TEXT,  notes              TEXT,  FOREIGN KEY (wallet_id) REFERENCES wallets(wallet_id));

CREATE TABLE merchants (  merchant_id   TEXT PRIMARY KEY,  merchant_name TEXT NOT NULL,  category      TEXT NOT NULL);

CREATE TABLE transactions (  txn_id      TEXT PRIMARY KEY,  wallet_id   TEXT NOT NULL,  merchant_id TEXT,  txn_ts      TEXT NOT NULL,  amount_pkr  INTEGER NOT NULL,  direction   TEXT NOT NULL,  txn_type    TEXT NOT NULL,  status      TEXT NOT NULL,  description TEXT,  FOREIGN KEY (wallet_id) REFERENCES wallets(wallet_id),  FOREIGN KEY (merchant_id) REFERENCES merchants(merchant_id));

CREATE TABLE wallet_links (  link_id     TEXT PRIMARY KEY,  wallet_a    TEXT NOT NULL,  wallet_b    TEXT NOT NULL,  payee_id    TEXT NOT NULL,  reason      TEXT NOT NULL,  linked_on   TEXT NOT NULL);

CREATE TABLE risk_flags (  flag_id   TEXT PRIMARY KEY,  wallet_id TEXT NOT NULL,  flag_type TEXT NOT NULL,  severity  TEXT NOT NULL,  active    INTEGER NOT NULL,  reason    TEXT);

CREATE TABLE alerts (  alert_id     TEXT PRIMARY KEY,  wallet_id    TEXT NOT NULL,  opened_at    TEXT NOT NULL,  alert_code   TEXT NOT NULL,  status       TEXT NOT NULL,  seed_story   TEXT NOT NULL);

CREATE TABLE cases (  case_id        TEXT PRIMARY KEY,  wallet_id      TEXT NOT NULL,  opened_at      TEXT NOT NULL,  case_type      TEXT NOT NULL,  complaint_text TEXT,  status         TEXT NOT NULL,  decision       TEXT,  amount_pkr     INTEGER,  officer_id     TEXT);

CREATE TABLE policy_docs (  policy_id TEXT PRIMARY KEY,  title     TEXT NOT NULL,  topic     TEXT NOT NULL,  md_path   TEXT NOT NULL);

CREATE TABLE policy_clauses (  clause_id TEXT PRIMARY KEY,  policy_id TEXT NOT NULL,  rule_text TEXT NOT NULL);

CREATE TABLE officers (  officer_id TEXT PRIMARY KEY,  full_name  TEXT NOT NULL,  desk       TEXT NOT NULL);

CREATE TABLE officer_prefs (  officer_id      TEXT PRIMARY KEY,  brief_style     TEXT NOT NULL,  language        TEXT NOT NULL,  allow_goodwill  INTEGER NOT NULL);

CREATE TABLE txn_features (  wallet_id                 TEXT PRIMARY KEY,  failed_bills_night_7d     INTEGER,  minutes_first_in_to_out   INTEGER,  inout_ratio_6h            REAL,  shared_payee_24h          INTEGER,  prior_goodwill_quarter    INTEGER,  active_watchlist          INTEGER,  txn_count_30d             INTEGER,  updated_at                TEXT);

CREATE TABLE alert_labels (  label_id   TEXT PRIMARY KEY,  wallet_id  TEXT,  story_tag  TEXT NOT NULL,  y_freeze_propose INTEGER NOT NULL);

CREATE TABLE evidence_packs (  pack_id    TEXT PRIMARY KEY,  alert_id   TEXT NOT NULL,  json_body  TEXT NOT NULL,  created_at TEXT NOT NULL);

CREATE TABLE draft_actions (  action_id  TEXT PRIMARY KEY,  alert_id   TEXT NOT NULL,  wallet_id  TEXT NOT NULL,  action     TEXT NOT NULL,  status     TEXT NOT NULL,  created_at TEXT NOT NULL,  signed_at  TEXT,  officer_id TEXT);

CREATE TABLE case_events (  event_id   TEXT PRIMARY KEY,  alert_id   TEXT NOT NULL,  event_ts   TEXT NOT NULL,  event_type TEXT NOT NULL,  detail     TEXT);

CREATE TABLE memories (  memory_id  TEXT PRIMARY KEY,  namespace  TEXT NOT NULL,  wallet_id  TEXT,  officer_id TEXT,  content    TEXT NOT NULL,  created_at TEXT NOT NULL);

CREATE INDEX ix_txn_wallet_ts ON transactions(wallet_id, txn_ts);

CREATE INDEX ix_flags_wallet ON risk_flags(wallet_id, active);

CREATE INDEX ix_cases_wallet ON cases(wallet_id, opened_at);
