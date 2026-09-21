from uuid import uuid4
from studio.desk_graph import local_graph
import json
from repos.db import one


def test_linked_map_reduce():
    with local_graph() as graph:
        result = graph.invoke({"alert_id": "A3", "officer_id": "off_fraud_01"}, {"configurable": {"thread_id": str(uuid4())}})
        expected = {"w_sara_lhr", "w_nadia_lhr"}
        assert {m["entity_wallet_id"] for m in result["evidence"]} == expected
        assert len(result["evidence"]) == 2
        assert set(result["pack"]["linked_wallets"]) == expected
        saved = one("SELECT json_body FROM evidence_packs WHERE pack_id=?", (result["review_id"],))
        memos = json.loads(saved["json_body"])["linked_evidence"]
        assert {memo["entity_wallet_id"] for memo in memos} == expected
        assert {tid for memo in memos for tid in memo["txn_ids"]} == {"txn_sara_payee", "txn_nadia_payee"}
        assert "investigate_entity" in graph.get_graph().draw_mermaid()
