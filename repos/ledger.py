from repos.db import as_of, rows


def list_transactions(wallet_id: str, cutoff=None, limit=30):
    return rows("""SELECT t.*, m.merchant_name, m.category FROM transactions t
        LEFT JOIN merchants m USING (merchant_id)
        WHERE wallet_id=? AND txn_ts<=? ORDER BY txn_ts DESC, txn_id LIMIT ?""",
        (wallet_id, as_of(cutoff), limit))


def find_first_credit_drain(wallet_id: str, cutoff=None):
    return rows("""WITH first_credit AS (
        SELECT * FROM transactions WHERE wallet_id=? AND direction='in'
        AND status='success' AND txn_ts<=? ORDER BY txn_ts, txn_id LIMIT 1)
        SELECT f.txn_id in_id, o.txn_id out_id, f.amount_pkr in_amt,
        o.amount_pkr out_amt, f.txn_ts in_ts, o.txn_ts out_ts
        FROM first_credit f JOIN transactions o ON o.wallet_id=f.wallet_id
        WHERE o.direction='out' AND o.status='success'
        AND o.txn_type IN ('cashout','p2p_send') AND o.txn_ts>f.txn_ts
        AND o.txn_ts<=? AND unixepoch(o.txn_ts)-unixepoch(f.txn_ts)<=1800
        AND o.amount_pkr*100>=f.amount_pkr*80 ORDER BY o.txn_ts LIMIT 5""",
        (wallet_id, as_of(cutoff), as_of(cutoff)))


def find_night_failed_bills(wallet_id: str, cutoff=None):
    return rows("""SELECT txn_id, txn_ts, amount_pkr, status FROM transactions
        WHERE wallet_id=? AND txn_type IN ('bill','failed_bill') AND status='failed'
        AND CAST(strftime('%H',txn_ts) AS INTEGER) BETWEEN 1 AND 4
        AND txn_ts BETWEEN datetime(?,'-7 days') AND ? ORDER BY txn_ts""",
        (wallet_id, as_of(cutoff), as_of(cutoff)))


def find_cashout_after_failures(wallet_id: str, cutoff=None):
    failures = find_night_failed_bills(wallet_id, cutoff)
    if not failures:
        return []
    last = failures[-1]["txn_ts"]
    return rows("""SELECT * FROM transactions WHERE wallet_id=? AND txn_type='cashout'
        AND direction='out' AND status='success' AND txn_ts>?
        AND txn_ts<=datetime(?,'+2 hours') AND txn_ts<=? ORDER BY txn_ts""",
        (wallet_id, last, last, as_of(cutoff)))


def find_shared_payee(wallet_id: str, cutoff=None, payee_id=None):
    return rows("""SELECT a.wallet_id wallet_a, b.wallet_id wallet_b,
        a.merchant_id, a.amount_pkr amt_a, b.amount_pkr amt_b,
        a.txn_id txn_a, b.txn_id txn_b FROM transactions a
        JOIN transactions b ON a.merchant_id=b.merchant_id AND a.wallet_id<b.wallet_id
        JOIN merchants m ON a.merchant_id=m.merchant_id
        WHERE (a.wallet_id=? OR b.wallet_id=?) AND (? IS NULL OR a.merchant_id=?)
        AND m.category IN ('unknown','p2p')
        AND a.direction='out' AND b.direction='out'
        AND a.status='success' AND b.status='success'
        AND a.txn_ts BETWEEN datetime(?,'-24 hours') AND ?
        AND b.txn_ts BETWEEN datetime(?,'-24 hours') AND ?
        AND ABS(unixepoch(a.txn_ts)-unixepoch(b.txn_ts))<=86400""",
        (wallet_id, wallet_id, payee_id, payee_id, as_of(cutoff), as_of(cutoff), as_of(cutoff), as_of(cutoff)))


def wallet_links(wallet_id: str, cutoff=None):
    return rows("SELECT * FROM wallet_links WHERE (wallet_a=? OR wallet_b=?) AND linked_on<=?",
                (wallet_id, wallet_id, as_of(cutoff)))


def find_duplicate_merchant_debit(wallet_id: str, cutoff=None):
    return rows("""SELECT a.txn_id txn_1, b.txn_id txn_2, a.amount_pkr,
        a.merchant_id, a.txn_ts ts_1, b.txn_ts ts_2 FROM transactions a
        JOIN transactions b ON a.wallet_id=b.wallet_id AND a.merchant_id=b.merchant_id
        AND a.amount_pkr=b.amount_pkr AND a.txn_id<b.txn_id
        WHERE a.wallet_id=? AND a.txn_type='merchant_debit' AND b.txn_type='merchant_debit'
        AND a.status='success' AND b.status='success' AND a.direction='out' AND b.direction='out'
        AND a.txn_ts BETWEEN datetime(?,'-7 days') AND ?
        AND b.txn_ts BETWEEN datetime(?,'-7 days') AND ?
        AND ABS(unixepoch(b.txn_ts)-unixepoch(a.txn_ts))<=900""",
        (wallet_id, as_of(cutoff), as_of(cutoff), as_of(cutoff), as_of(cutoff)))
