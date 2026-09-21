from uuid import uuid4
from studio.desk_graph import local_graph
from repos.db import one


def test_memory_survives_new_process_store():
    with local_graph() as graph:
        config = {"configurable": {"thread_id": str(uuid4())}}
        graph.invoke({"alert_id": "A1", "officer_id": "off_fraud_01"}, config)
        graph.update_state(config, {"signed": True, "human_decision": "watch"})
        result = graph.invoke(None, config)
        rid = result["review_id"]
    assert one("SELECT COUNT(*) n FROM memories WHERE memory_id=?", (rid,))["n"] == 1
    with local_graph() as graph:
        state = graph.invoke({"alert_id": "A1", "officer_id": "off_fraud_01"}, {"configurable": {"thread_id": str(uuid4())}})
        assert any(rid in fact for fact in state["known_facts"])
        a6 = graph.invoke({"alert_id": "A6", "officer_id": "off_care_01"}, {"configurable": {"thread_id": str(uuid4())}})
        assert any("Goodwill" in f or "goodwill" in f for f in a6["pack"]["known_facts"])
        assert a6["pack"]["brief_style"] == "paragraph"
