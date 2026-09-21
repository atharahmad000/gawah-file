"""Fork an unsigned checkpoint, then sign the fork with a demo watch decision."""
import sys
from pathlib import Path
from uuid import uuid4
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from studio.desk_graph import local_graph


def main():
    with local_graph() as graph:
        config = {"configurable": {"thread_id": "time-travel-" + str(uuid4())}}
        graph.invoke({"alert_id": "A1", "officer_id": "off_fraud_01"}, config)
        history = list(graph.get_state_history(config))
        checkpoint = next(s for s in history if s.next == ("apply_action",))
        fork = graph.update_state(checkpoint.config, {"signed": True, "human_decision": "watch", "human_comment": "Scripted unsigned-checkpoint fork."}, as_node="gate")
        result = graph.invoke(None, fork)
        assert result["applied"]
        print(f"Forked unsigned checkpoint; signed watch. {len(history)} checkpoints retained.")
        print("An already-approved review cannot be changed by replaying its old checkpoint.")


if __name__ == "__main__":
    main()
