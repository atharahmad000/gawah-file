from uuid import uuid4
from studio.desk_graph import local_graph


def test_six_template_packs():
    expected = ["T01_first_credit_drain", "T02_night_bill_camouflage", "T03_shared_new_payee", "T04_loyal_customer_one_odd", "T05_already_reviewed_watchlist", "T06_duplicate_merchant_debit"]
    with local_graph() as graph:
        for i, clause in enumerate(expected, 1):
            config = {"configurable": {"thread_id": str(uuid4())}}
            state = graph.invoke({"alert_id": f"A{i}", "officer_id": "off_fraud_01"}, config)
            pack = state["pack"]
            assert clause in pack["clause_ids_cited"]
            assert set(pack["clause_ids_cited"]) <= {h["clause_id"] for h in state["policy_hits"]}
            if i in (4,6):
                assert pack["recommended_action"] in ("watch", "close")
            if i == 1:
                assert pack["recommended_action"] == "freeze"
            if i == 5:
                assert pack["recommended_action"] == "close"
