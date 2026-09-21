"""The documented rule path. This hint can raise a gate, never authorize an action."""
from repos.features import calculate_features


def score(features):
    minutes = features["minutes_first_in_to_out"]
    minutes = 9999 if minutes is None else minutes
    if features["active_watchlist"] and (minutes <= 30 or features["shared_payee_24h"] >= 1):
        return "high", ["active_watchlist", "minutes_first_in_to_out", "shared_payee_24h"]
    if minutes <= 20 and features["inout_ratio_6h"] >= 0.8:
        return "high", ["minutes_first_in_to_out", "inout_ratio_6h"]
    if features["failed_bills_night_7d"] >= 6:
        return "medium", ["failed_bills_night_7d"]
    if features["active_watchlist"]:
        return "medium", ["active_watchlist"]
    return "low", []


class RiskHint:
    def predict(self, wallet_id, cutoff=None):
        return score(calculate_features(wallet_id, cutoff))[0]
