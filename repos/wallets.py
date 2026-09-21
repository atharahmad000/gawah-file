from repos.db import one


def get_wallet(wallet_id: str):
    return one("SELECT w.*, p.preferred_language, p.typical_use, p.notes FROM wallets w JOIN wallet_profiles p USING(wallet_id) WHERE wallet_id=?", (wallet_id,))


def get_officer(officer_id: str):
    return one("SELECT o.*, p.brief_style, p.language, p.allow_goodwill FROM officers o JOIN officer_prefs p USING(officer_id) WHERE officer_id=?", (officer_id,))
