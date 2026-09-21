from datetime import datetime
from repos.db import as_of, one, rows


def list_prior_cases(wallet_id: str, cutoff=None):
    return rows("SELECT * FROM cases WHERE wallet_id=? AND opened_at<=? ORDER BY opened_at DESC LIMIT 5", (wallet_id, as_of(cutoff)))


def goodwill_this_quarter(wallet_id: str, cutoff=None):
    date = datetime.fromisoformat(as_of(cutoff))
    start = date.replace(month=((date.month-1)//3)*3+1, day=1, hour=0, minute=0, second=0)
    return one("""SELECT COUNT(*) n FROM cases WHERE wallet_id=? AND decision='approved'
        AND case_type='goodwill' AND opened_at BETWEEN ? AND ?""", (wallet_id, str(start), as_of(cutoff)))["n"]
