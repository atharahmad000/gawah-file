from repos.features import calculate_features, rebuild_features, get_features
from risk.hint import score


def test_features_and_hint():
    rebuild_features()
    bilal = get_features("w_bilal_khi")
    assert bilal["minutes_first_in_to_out"] == 18
    assert abs(bilal["inout_ratio_6h"] - 0.968) < 0.0001
    assert score(bilal)[0] == "high"
    assert score(calculate_features("w_ayesha_lhr"))[0] == "low"
    assert score(calculate_features("w_hamza_rwp"))[0] == "medium"
    assert score(calculate_features("w_bilal_khi", "2026-08-31 14:10:00"))[0] == "low"
