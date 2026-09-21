from repos.db import rows


def get_risk_flags(wallet_id: str):
    return rows("SELECT flag_type, severity, reason FROM risk_flags WHERE wallet_id=? AND active=1", (wallet_id,))
