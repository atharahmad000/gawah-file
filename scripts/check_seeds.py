import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from repos import ledger
from repos.cases import goodwill_this_quarter
from repos.flags import get_risk_flags
from repos.db import rows


def check():
    findings = {
        "A1": ledger.find_first_credit_drain("w_bilal_khi"),
        "A2": ledger.find_night_failed_bills("w_imran_isb"),
        "A3": ledger.find_shared_payee("w_sara_lhr"),
        "A4": ledger.list_transactions("w_ayesha_lhr"),
        "A5": get_risk_flags("w_hamza_rwp"),
        "A6": ledger.find_duplicate_merchant_debit("w_ayesha_lhr"),
    }
    assert all(findings.values()), "A planted story is missing"
    assert len(findings["A2"]) >= 6
    assert ledger.find_cashout_after_failures("w_imran_isb")
    assert not ledger.find_first_credit_drain("w_ayesha_lhr")
    assert goodwill_this_quarter("w_ayesha_lhr") >= 1
    assert any(f["flag_type"] == "watchlist" for f in findings["A5"])
    assert [r["alert_id"] for r in rows("SELECT alert_id FROM alerts ORDER BY alert_id")] == [f"A{i}" for i in range(1,7)]
    for alert, result in findings.items():
        print(f"PASS {alert}: {result if alert != 'A4' else str(len(result)) + ' history rows; no drain'}")


if __name__ == "__main__":
    check()
