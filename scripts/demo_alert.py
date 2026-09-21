"""Open a case, inspect a checkpoint, or explicitly sign a local demo review."""
import argparse
import json
import sys
from pathlib import Path
from uuid import uuid4
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from studio.desk_graph import local_graph
from pack.render import render_markdown


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("alert", choices=[f"A{i}" for i in range(1,7)])
    parser.add_argument("--desk", choices=["fraud", "care"], default="fraud")
    parser.add_argument("--thread")
    parser.add_argument("--inspect", action="store_true")
    parser.add_argument("--sign", choices=["watch", "close", "freeze", "file_compliance"])
    parser.add_argument("--comment", default="")
    parser.add_argument("--export", type=Path)
    parser.add_argument("--format", choices=["json", "markdown"], default="json")
    args = parser.parse_args()
    if (args.sign or args.inspect) and not args.thread:
        parser.error("--sign and --inspect require an existing --thread")
    config = {"configurable": {"thread_id": args.thread or str(uuid4())}}
    with local_graph() as graph:
        previous = graph.get_state(config)
        if args.sign or args.inspect:
            if not previous.values or previous.values.get("alert_id") != args.alert:
                parser.error("This thread does not belong to the requested alert")
            if args.sign:
                if previous.next != ("apply_action",):
                    parser.error("This thread is not waiting for a decision")
                graph.update_state(config, {"signed": True, "human_decision": args.sign, "human_comment": args.comment})
                graph.invoke(None, config)
        else:
            if previous.values:
                parser.error("Thread already exists. Use --inspect or --sign, or choose a new thread")
            graph.invoke({"alert_id": args.alert, "officer_id": "off_fraud_01" if args.desk == "fraud" else "off_care_01"}, config)
        snapshot = graph.get_state(config)
        output = {"thread_id": config["configurable"]["thread_id"], "next": snapshot.next,
                  "gate_reason": snapshot.values.get("gate_reason"), "pack": snapshot.values["pack"],
                  "human_decision": snapshot.values.get("human_decision"), "applied": snapshot.values.get("applied")}
        if args.format == "markdown":
            text = render_markdown(output["pack"], gate_reason=output["gate_reason"],
                                   human_decision=output["human_decision"], applied=output["applied"])
            text += f"\nThread: `{output['thread_id']}`\n"
        else:
            text = json.dumps(output, indent=2, ensure_ascii=True)
        print(text)
        if args.export:
            args.export.parent.mkdir(parents=True, exist_ok=True)
            args.export.write_text(text+"\n", encoding="utf-8")


if __name__ == "__main__":
    main()
