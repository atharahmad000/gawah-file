"""Recreate the checked-in, fictional SQL source files without random data."""
from datetime import datetime, timedelta
from pathlib import Path

HERE = Path(__file__).resolve().parent


def literal(value):
    if value is None:
        return "NULL"
    if isinstance(value, int):
        return str(value)
    return "'" + str(value).replace("'", "''") + "'"


def insert(table, values):
    return f"INSERT INTO {table} VALUES ({', '.join(map(literal, values))});"


def generate():
    wallets = [
        ("w_ayesha_lhr", "Ayesha", "Lahore", "full", "2025-01-15", "Groceries and household bills", "Longstanding customer; occasional family transfers."),
        ("w_bilal_khi", "Bilal", "Karachi", "basic", "2026-08-28", "New wallet", "No established spending history."),
        ("w_imran_isb", "Imran", "Islamabad", "full", "2025-11-02", "Utility bills", "Usually pays during the day."),
        ("w_sara_lhr", "Sara", "Lahore", "basic", "2026-08-20", "Personal transfers", "Recently opened."),
        ("w_nadia_lhr", "Nadia", "Lahore", "basic", "2026-08-21", "Personal transfers", "Recently opened."),
        ("w_hamza_rwp", "Hamza", "Rawalpindi", "full", "2024-06-01", "Groceries", "Prior review closed; watchlist remains active."),
    ]
    wallets += [(f"w_filler_{i:02}", f"Example Customer {i}", ["Lahore", "Karachi"][i % 2], "full", "2025-02-01", "Routine household spending", "Synthetic padding only.") for i in range(1, 7)]
    lines = []
    for i, (wid, name, city, tier, opened, use, note) in enumerate(wallets):
        lines.append(insert("wallets", (wid, f"03xx-{i:07}", name + " (fictional)", city, tier, "active", opened)))
        lines.append(insert("wallet_profiles", (wid, "ur" if i % 2 == 0 else "en", use, note)))
    lines += [insert("officers", ("off_fraud_01", "Farah (demo)", "fraud")), insert("officers", ("off_care_01", "Omar (demo)", "care")), insert("officer_prefs", ("off_fraud_01", "tables", "en", 0)), insert("officer_prefs", ("off_care_01", "paragraph", "en", 1))]
    write("seed_wallets.sql", lines)
    merchants = [("m_hussain_general", "Hussain General (fictional)", "grocery"), ("m_kelectric", "Example utility", "utility"), ("p_new_unknown_1", "Unverified payee (fictional)", "unknown"), ("p_cashout_desk_1", "Demo cash-out desk", "cashout"), ("p_cousin_umair", "Cousin Umair (fictional)", "p2p")]
    merchants += [(f"m_filler_{i:02}", f"Example merchant {i}", ["grocery", "utility", "p2p"][i % 3]) for i in range(1, 16)]
    write("seed_merchants.sql", [insert("merchants", m) for m in merchants])
    txns = []

    def txn(tid, wid, mid, ts, amount, kind, direction="out", status="success", description="Synthetic ledger entry"):
        txns.append(insert("transactions", (tid, wid, mid, ts, amount, direction, kind, status, description)))

    txn("txn_bilal_credit", "w_bilal_khi", None, "2026-08-31 14:00:00", 25000, "cashin", "in")
    txn("txn_bilal_drain", "w_bilal_khi", "p_cashout_desk_1", "2026-08-31 14:18:00", 24200, "cashout")
    for i in range(6):
        ts = datetime(2026, 9, 1, 1) + timedelta(minutes=i * 40)
        txn(f"txn_imran_fail_{i+1}", "w_imran_isb", "m_kelectric", str(ts), 100 + i * 10, "failed_bill", status="failed")
    txn("txn_imran_cashout", "w_imran_isb", "p_cashout_desk_1", "2026-09-01 05:12:00", 18000, "cashout")
    for i in range(8):
        txn(f"txn_imran_bill_{i}", "w_imran_isb", "m_kelectric", f"2026-08-{i+2:02} 12:00:00", 900+i*23, "bill")
    txn("txn_sara_payee", "w_sara_lhr", "p_new_unknown_1", "2026-08-31 16:00:00", 9500, "p2p_send")
    txn("txn_nadia_payee", "w_nadia_lhr", "p_new_unknown_1", "2026-08-31 16:40:00", 9800, "p2p_send")
    for i in range(30):
        ts = datetime(2026, 7, 2, 13) + timedelta(days=i*2)
        txn(f"txn_ayesha_normal_{i:02}", "w_ayesha_lhr", "m_hussain_general" if i%2 else "m_kelectric", str(ts), 250+i*17, "merchant_debit" if i%2 else "bill")
    txn("txn_ayesha_cousin", "w_ayesha_lhr", "p_cousin_umair", "2026-08-31 19:10:00", 12000, "p2p_send")
    for i, minute in enumerate(["00", "11"], 1):
        txn(f"txn_ayesha_duplicate_{i}", "w_ayesha_lhr", "m_hussain_general", f"2026-08-31 11:{minute}:00", 4500, "merchant_debit")
    txn("txn_hamza_grocery", "w_hamza_rwp", "m_hussain_general", "2026-09-01 10:00:00", 400, "merchant_debit")
    for i in range(1, 7):
        for j in range(40):
            ts = datetime(2026, 7, 10, 12) + timedelta(days=j, minutes=i*7)
            txn(f"txn_filler_{i}_{j:02}", f"w_filler_{i:02}", f"m_filler_{i:02}", str(ts), 300+i*21+j*13, "merchant_debit")
    write("seed_transactions.sql", txns)
    write("seed_links_flags.sql", [insert("wallet_links", ("link_sara_nadia", "w_sara_lhr", "w_nadia_lhr", "p_new_unknown_1", "Shared new payee", "2026-08-31 16:40:00")), insert("risk_flags", ("flag_hamza_watch", "w_hamza_rwp", "watchlist", "high", 1, "Synthetic review marker; remains active")), insert("risk_flags", ("flag_hamza_review", "w_hamza_rwp", "prior_review", "low", 1, "Closed review in August"))])
    stories = [("w_bilal_khi", "first_credit_drain"), ("w_imran_isb", "night_bill_camouflage"), ("w_sara_lhr", "shared_payee"), ("w_ayesha_lhr", "loyal_odd"), ("w_hamza_rwp", "watchlist_repeat"), ("w_ayesha_lhr", "duplicate_debit")]
    lines = [insert("alerts", (f"A{i}", wid, "2026-09-01 11:00:00", code, "open", code)) for i, (wid, code) in enumerate(stories, 1)]
    lines += [insert("cases", ("case_goodwill_ayesha_q3", "w_ayesha_lhr", "2026-08-10 10:00:00", "goodwill", "Example service complaint", "closed", "approved", 800, "off_care_01")), insert("cases", ("case_hamza_review_aug", "w_hamza_rwp", "2026-08-15 10:00:00", "review", "Synthetic prior review", "closed", "close", 0, "off_fraud_01"))]
    lines += [insert("cases", (f"case_padding_{i}", f"w_filler_{i%6+1:02}", f"2026-08-{i+1:02} 10:00:00", "review", "Example closed enquiry", "closed", "close", 0, "off_care_01")) for i in range(8)]
    write("seed_alerts_cases.sql", lines)
    write("seed_labels.sql", [insert("alert_labels", (f"label_{i:03}", stories[i%6][0], stories[i%6][1], int(i%6 == 0))) for i in range(100)])


def write(name, lines):
    (HERE / name).write_text("-- Fictional demonstration data. Amounts are whole PKR.\n" + "\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    generate()
