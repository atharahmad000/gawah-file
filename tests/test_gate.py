from uuid import uuid4
import pytest
from studio.desk_graph import local_graph
from repos.db import one
from repos.reviews import approve


def test_unsigned_then_signed_override_and_replay():
    with local_graph() as graph:
        config = {"configurable": {"thread_id": str(uuid4())}}
        state = graph.invoke({"alert_id": "A1", "officer_id": "off_fraud_01"}, config)
        assert graph.get_state(config).next == ("apply_action",)
        assert not state.get("signed")
        graph.invoke(None, config)
        assert graph.get_state(config).next == ("apply_action",)
        assert one("SELECT COUNT(*) n FROM draft_actions WHERE action_id=?", (state["review_id"],))["n"] == 0
        graph.update_state(config, {"signed": True, "human_decision": "watch", "human_comment": "Check destination before restricting the wallet."})
        result = graph.invoke(None, config)
        assert result["applied"]
        assert approve(result)
        assert one("SELECT COUNT(*) n FROM draft_actions WHERE action_id=?", (state["review_id"],))["n"] == 1
        assert one("SELECT action FROM draft_actions WHERE action_id=?", (state["review_id"],))["action"] == "watch"
        with pytest.raises(ValueError, match="different signed decision"):
            approve({**result, "human_decision": "freeze"})


def test_presigned_input_is_ignored():
    with local_graph() as graph:
        state = graph.invoke({"alert_id": "A5", "officer_id": "off_fraud_01", "signed": True, "human_decision": "freeze"}, {"configurable": {"thread_id": str(uuid4())}})
        assert state["signed"] is False
        assert "watchlist" in state["gate_reason"]
        assert state["pack"]["recommended_action"] == "close"
