"""Exercise a running local Studio server using fictional review decisions."""
import argparse
import json
from pathlib import Path
from urllib.request import Request, urlopen


def request(base, path, body=None):
    req = Request(base + path, data=json.dumps(body).encode() if body is not None else None,
                  headers={"Content-Type": "application/json"})
    with urlopen(req, timeout=90) as response:
        return json.load(response)


def run(base):
    assert request(base, "/ok")["ok"]
    desks = json.loads((Path(__file__).resolve().parents[1] / "studio/assistants.json").read_text())
    for name, desk in desks.items():
        assistant = request(base, "/assistants", {"graph_id": desk["graph_id"], "name": name + " demo", "config": desk["config"]})
        thread = request(base, "/threads", {})["thread_id"]
        run_input = {"assistant_id": assistant["assistant_id"], "input": desk["input"], "multitask_strategy": "interrupt"}
        result = request(base, f"/threads/{thread}/runs/wait", run_input)
        if "__error__" in result:
            raise RuntimeError(result["__error__"])
        state = request(base, f"/threads/{thread}/state")
        assert state["next"] == ["apply_action"], state
        assert state["values"]["proposed_action"] == ("watch" if name == "gawah_care" else "freeze")
        request(base, f"/threads/{thread}/runs/wait", {"assistant_id": assistant["assistant_id"], "input": None})
        state = request(base, f"/threads/{thread}/state")
        assert state["next"] == ["apply_action"] and not state["values"]["applied"]
        request(base, f"/threads/{thread}/state", {"values": {"signed": True, "human_decision": "watch", "human_comment": "Scripted synthetic smoke-test decision."}, "as_node": "gate"})
        result = request(base, f"/threads/{thread}/runs/wait", {"assistant_id": assistant["assistant_id"], "input": None})
        assert result["applied"], result
        print(f"PASS {name}: pause, unsigned refusal, signed watch; thread {thread}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--url", default="http://127.0.0.1:2024")
    run(parser.parse_args().url)
