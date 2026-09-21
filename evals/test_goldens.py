from pathlib import Path
import pytest
import yaml
from repos.db import one
from studio.desk_graph import local_graph

GOLDENS = yaml.safe_load(Path(__file__).with_name("golden.yaml").read_text(encoding="utf-8"))


@pytest.mark.parametrize("golden", GOLDENS, ids=lambda row: row["alert_id"])
def test_golden(golden):
    with local_graph() as graph:
        config = {"configurable": {"thread_id": golden["alert_id"]}}
        state = graph.invoke({"alert_id": golden["alert_id"], "officer_id": "off_fraud_01"}, config)
        pack = state["pack"]
        assert state["wallet_id"] == golden["wallet_id"]
        if golden["must_interrupt"]:
            assert graph.get_state(config).next == ("apply_action",)
        for tool in golden["must_sql_tool_hits"]:
            assert state["sql_findings"][tool]
            assert tool in pack["sql_queries_relied_on"]
        cited = set(pack["clause_ids_cited"])
        assert cited.intersection(golden["must_cite_any"])
        assert cited <= {h["clause_id"] for h in state["policy_hits"]}
        assert not cited.intersection(golden["must_not_cite"])
        assert pack["recommended_action"] not in golden["must_not_recommend"]
        if golden["alert_id"] == "A3":
            assert len(state["evidence"]) == 2
        if golden["alert_id"] == "A5":
            assert pack["timeline"][-1]["amount_pkr"] == 400
            assert "watchlist" in state["gate_reason"]
        if golden["forbid_unsigned_freeze"]:
            graph.invoke(None, config)
            assert one("SELECT COUNT(*) n FROM draft_actions")["n"] == 0
            assert graph.get_state(config).next == ("apply_action",)
        decision = "watch" if golden["alert_id"] != "A5" else "close"
        graph.update_state(config, {"signed": True, "human_decision": decision, "human_comment": "Reviewed synthetic evidence."})
        result = graph.invoke(None, config)
        assert result["applied"]
        assert not graph.get_state(config).next
        action = one("SELECT * FROM draft_actions WHERE action_id=?", (state["review_id"],))
        assert action["action"] == decision and action["status"] == "approved"
        assert one("SELECT COUNT(*) n FROM case_events WHERE event_type='approved'")["n"] == 1
        assert one("SELECT COUNT(*) n FROM memories WHERE memory_id=?", (state["review_id"],))["n"] == 1
