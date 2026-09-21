from uuid import uuid4
from studio.desk_graph import local_graph
from repos.db import one


def test_load_without_ledger_changes():
    count = one("SELECT COUNT(*) n FROM transactions")["n"]
    with local_graph() as graph:
        config = {"configurable": {"thread_id": str(uuid4())}}
        graph.invoke({"alert_id": "A1", "officer_id": "off_fraud_01"}, config)
        assert graph.get_state(config).values["wallet_id"] == "w_bilal_khi"
        assert "load_alert" in graph.get_graph().draw_mermaid()
    assert one("SELECT COUNT(*) n FROM transactions")["n"] == count
