import sqlite3
import pytest
from repos.db import connect, one
from repos.wallets import get_wallet
from repos.ledger import find_first_credit_drain, find_shared_payee, find_duplicate_merchant_debit
from scripts.check_seeds import check


def test_stories():
    check()
    assert get_wallet("w_bilal_khi")["city"] == "Karachi"
    assert one("SELECT COUNT(*) n FROM transactions")["n"] in range(200,401)


def test_identifiers_are_bound():
    assert get_wallet("'; DROP TABLE wallets; --") is None
    assert one("SELECT COUNT(*) n FROM wallets")["n"] == 12


def test_foreign_keys():
    with pytest.raises(sqlite3.IntegrityError), connect() as conn:
        conn.execute("INSERT INTO wallet_profiles VALUES ('missing','en','','')")


def test_cutoff_and_both_shared_sides():
    assert not find_first_credit_drain("w_bilal_khi", "2026-08-31 14:10:00")
    assert find_shared_payee("w_sara_lhr") == find_shared_payee("w_nadia_lhr")
    assert not find_shared_payee("w_ayesha_lhr")
    assert not find_duplicate_merchant_debit("w_ayesha_lhr", "2026-08-31 11:05:00")
