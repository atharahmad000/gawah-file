from uuid import uuid4
from studio.desk_graph import local_graph
from tools.registry import read_tools


def test_care_and_mid_review_message():
    with local_graph() as graph:
        config = {"configurable": {"thread_id": str(uuid4()), "desk_role": "care", "officer_id": "off_care_01"}}
        state = graph.invoke({"alert_id": "A1", "officer_id": "off_care_01"}, config)
        assert state["proposed_action"] == "watch"
        graph.update_state(config, {"messages": [{"role": "human", "content": "Please verify the destination."}]}, as_node="gate")
        updated = graph.get_state(config)
        assert updated.values["wallet_id"] == state["wallet_id"]
        assert updated.values["sql_findings"] == state["sql_findings"]
        assert updated.next == ("apply_action",)
    names = {tool.name for tool in read_tools()}
    assert len(names) == 11
    assert not names.intersection({"apply_freeze", "apply_action", "open_compliance_case", "run_sql", "save_memory"})
