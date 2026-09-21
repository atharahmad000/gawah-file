"""Scripted human decision for the synthetic demo, never a live approval service."""
import sys
from pathlib import Path
from uuid import uuid4
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from studio.desk_graph import local_graph
from repos.db import one


def main():
    with local_graph() as graph:
        config = {"configurable": {"thread_id": "gate-demo-" + str(uuid4())}}
        state = graph.invoke({"alert_id": "A1", "officer_id": "off_fraud_01"}, config)
        print("Draft recommendation:", state["proposed_action"])
        print("Paused at:", graph.get_state(config).next)
        graph.invoke(None, config)
        assert one("SELECT COUNT(*) n FROM draft_actions WHERE action_id=?", (state["review_id"],))["n"] == 0
        print("Unsigned resume refused.")
        graph.update_state(config, {"signed": True, "human_decision": "watch", "human_comment": "Scripted demonstration: verify the destination first."})
        result = graph.invoke(None, config)
        assert result["applied"]
        print("Recorded signed watch. No wallet status was changed.")


if __name__ == "__main__":
    main()
