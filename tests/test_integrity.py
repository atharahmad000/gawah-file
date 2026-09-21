from copy import deepcopy
from uuid import uuid4
import pytest
from repos.db import connect, one, rows
from repos.ledger import find_first_credit_drain, find_cashout_after_failures
from repos.reviews import approve
from studio.desk_graph import local_graph


def test_later_credit_is_not_first_credit():
    with connect() as conn:
        conn.execute("INSERT INTO transactions VALUES (?,?,?,?,?,?,?,?,?)", ("earlier_credit", "w_bilal_khi", None, "2026-08-29 12:00:00", 100, "in", "cashin", "success", "Earlier receipt"))
    assert find_first_credit_drain("w_bilal_khi") == []


def test_cashout_must_follow_last_failure_within_two_hours():
    with connect() as conn:
        conn.execute("UPDATE transactions SET txn_ts='2026-09-01 09:00:00' WHERE txn_id='txn_imran_cashout'")
    assert find_cashout_after_failures("w_imran_isb") == []


def test_tampering_and_non_boolean_signature():
    before = rows("SELECT * FROM transactions ORDER BY txn_id")
    with local_graph() as graph:
        state = graph.invoke({"alert_id": "A1", "officer_id": "off_fraud_01"}, {"configurable": {"thread_id": str(uuid4())}})
        assert not approve({**state, "signed": "true", "human_decision": "freeze"})
        edited = deepcopy(state)
        edited.update(signed=True, human_decision="freeze")
        edited["pack"]["headline"] = "Changed after review"
        with pytest.raises(ValueError, match="changed after review"):
            approve(edited)
        assert one("SELECT COUNT(*) n FROM draft_actions")["n"] == 0
        assert approve({**state, "signed": True, "human_decision": "freeze"})
    assert rows("SELECT * FROM transactions ORDER BY txn_id") == before
    assert one("SELECT status FROM wallets WHERE wallet_id='w_bilal_khi'")["status"] == "active"


def test_reusing_thread_cannot_mix_two_case_files():
    with local_graph() as graph:
        config = {"configurable": {"thread_id": str(uuid4())}}
        graph.invoke({"alert_id": "A3", "officer_id": "off_fraud_01"}, config)
        with pytest.raises(ValueError, match="fresh thread"):
            graph.invoke({"alert_id": "A4", "officer_id": "off_fraud_01"}, config)


def test_memory_is_scoped_to_wallet_and_officer():
    from repos.reviews import read_memories
    rows_for_bilal = read_memories("w_bilal_khi", "off_fraud_01")
    assert all(r["wallet_id"] in (None, "w_bilal_khi") for r in rows_for_bilal)
    assert not any("Goodwill of PKR 800" in r["content"] for r in rows_for_bilal)


def test_audit_uses_saved_proposal_and_alert_cutoff():
    import json
    with local_graph() as graph:
        state = graph.invoke({"alert_id": "A1", "officer_id": "off_fraud_01"},
                             {"configurable": {"thread_id": str(uuid4())}})
    assert approve({**state, "signed": True, "human_decision": "watch",
                    "proposed_action": "close", "cutoff": "2099-01-01 00:00:00"})
    event = one("SELECT detail FROM case_events WHERE event_id=?", (state["review_id"] + ":approval",))
    detail = json.loads(event["detail"])
    assert detail["proposed"] == "freeze"
    assert detail["evidence_as_of"] == "2026-09-01 11:00:00"
