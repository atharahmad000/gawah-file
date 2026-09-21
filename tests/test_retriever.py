from retrieve.playbook_index import build_index
from retrieve.retriever import search_playbook
from repos.playbook_sql import get_clause


def test_queries():
    build_index()
    assert build_index() == build_index()
    checks = [
        ("first inbound credit then cash-out within 30 minutes 80 percent", {"T01_first_credit_drain"}),
        ("loyal long customer single odd p2p send do not freeze", {"T04_loyal_customer_one_odd", "T07_when_not_to_freeze"}),
        ("two equal merchant debits same shop eleven minutes", {"T06_duplicate_merchant_debit"}),
    ]
    for query, wanted in checks:
        hits = search_playbook(query)
        assert wanted.intersection(h["clause_id"] for h in hits)
        if "loyal" in query or "merchant" in query:
            assert hits[0]["clause_id"] != "T08_pass_through_mule"
        if "loyal" in query:
            assert hits[0]["clause_id"] != "T01_first_credit_drain"
    assert search_playbook("hospital cash waiting period") == []
    assert "30 minutes" in get_clause("T01_first_credit_drain")["rule_text"]
