from repos.db import as_of, connect, one, rows
from repos.ledger import find_night_failed_bills, find_shared_payee
from repos.cases import goodwill_this_quarter
from repos.flags import get_risk_flags


def calculate_features(wallet_id, cutoff=None):
    cutoff = as_of(cutoff)
    timing = one("""WITH credit AS (
        SELECT txn_ts FROM transactions WHERE wallet_id=? AND direction='in'
        AND status='success' AND txn_ts<=? ORDER BY txn_ts, txn_id LIMIT 1)
        SELECT MIN((unixepoch(t.txn_ts)-unixepoch(c.txn_ts))/60.0) minutes
        FROM transactions t CROSS JOIN credit c WHERE t.wallet_id=?
        AND t.direction='out' AND t.status='success' AND t.txn_ts>c.txn_ts AND t.txn_ts<=?""",
        (wallet_id, cutoff, wallet_id, cutoff))
    ratio = one("""WITH credit AS (
        SELECT txn_ts FROM transactions WHERE wallet_id=? AND direction='in'
        AND status='success' AND txn_ts<=? ORDER BY txn_ts, txn_id LIMIT 1)
        SELECT COALESCE(SUM(CASE WHEN t.direction='out' THEN t.amount_pkr ELSE 0 END)*1.0 /
        NULLIF(SUM(CASE WHEN t.direction='in' THEN t.amount_pkr ELSE 0 END),0),0) ratio
        FROM transactions t CROSS JOIN credit c WHERE t.wallet_id=? AND t.status='success'
        AND t.txn_ts BETWEEN c.txn_ts AND datetime(c.txn_ts,'+6 hours') AND t.txn_ts<=?""",
        (wallet_id, cutoff, wallet_id, cutoff))
    return dict(wallet_id=wallet_id, failed_bills_night_7d=len(find_night_failed_bills(wallet_id, cutoff)),
        minutes_first_in_to_out=timing["minutes"], inout_ratio_6h=ratio["ratio"],
        shared_payee_24h=len(find_shared_payee(wallet_id, cutoff)),
        prior_goodwill_quarter=goodwill_this_quarter(wallet_id, cutoff),
        active_watchlist=int(any(f["flag_type"] == "watchlist" for f in get_risk_flags(wallet_id))),
        txn_count_30d=one("SELECT COUNT(*) n FROM transactions WHERE wallet_id=? AND txn_ts BETWEEN datetime(?,'-30 days') AND ?", (wallet_id, cutoff, cutoff))["n"],
        updated_at=cutoff)


def rebuild_features(cutoff=None):
    for wallet in rows("SELECT wallet_id FROM wallets"):
        feature = calculate_features(wallet["wallet_id"], cutoff)
        with connect() as conn:
            conn.execute("""INSERT INTO txn_features VALUES (?,?,?,?,?,?,?,?,?)
                ON CONFLICT(wallet_id) DO UPDATE SET
                failed_bills_night_7d=excluded.failed_bills_night_7d,
                minutes_first_in_to_out=excluded.minutes_first_in_to_out,
                inout_ratio_6h=excluded.inout_ratio_6h,shared_payee_24h=excluded.shared_payee_24h,
                prior_goodwill_quarter=excluded.prior_goodwill_quarter,
                active_watchlist=excluded.active_watchlist,txn_count_30d=excluded.txn_count_30d,
                updated_at=excluded.updated_at""", tuple(feature.values()))


def get_features(wallet_id):
    return one("SELECT * FROM txn_features WHERE wallet_id=?", (wallet_id,))
