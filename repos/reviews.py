"""Atomic approval records, with the review id as the replay boundary."""
import json
from datetime import datetime, timezone
from uuid import uuid4
from repos.db import connect, rows


def now():
    return datetime.now(timezone.utc).isoformat(timespec="microseconds")


def pack_json(pack):
    return json.dumps(pack, sort_keys=True, separators=(",", ":"))


def record_pack(state):
    with connect() as conn:
        conn.execute("INSERT INTO evidence_packs VALUES (?,?,?,?) ON CONFLICT(pack_id) DO NOTHING",
                     (state["review_id"], state["alert_id"], pack_json(state["pack"]), now()))


def record_refusal(state, reason):
    with connect() as conn:
        conn.execute("INSERT INTO case_events VALUES (?,?,?,?,?)", (str(uuid4()), state["alert_id"], now(), "refused_unsigned", reason))


def approve(state):
    if state.get("signed") is not True or state.get("human_decision") not in {"close", "watch", "freeze", "file_compliance"}:
        record_refusal(state, "A valid human decision and signed=True are required.")
        return False
    with connect() as conn:
        conn.execute("BEGIN IMMEDIATE")
        alert = conn.execute("SELECT * FROM alerts WHERE alert_id=?", (state["alert_id"],)).fetchone()
        officer = conn.execute("SELECT * FROM officers WHERE officer_id=?", (state["officer_id"],)).fetchone()
        saved = conn.execute("SELECT * FROM evidence_packs WHERE pack_id=?", (state["review_id"],)).fetchone()
        if not alert or alert["wallet_id"] != state["wallet_id"] or not officer or not saved:
            raise ValueError("Review identity does not match the operational record")
        if saved["alert_id"] != state["alert_id"] or saved["json_body"] != pack_json(state["pack"]):
            raise ValueError("The evidence pack changed after review; start a fresh investigation")
        existing = conn.execute("SELECT * FROM draft_actions WHERE action_id=?", (state["review_id"],)).fetchone()
        if existing:
            if existing["action"] != state["human_decision"] or existing["officer_id"] != state["officer_id"]:
                raise ValueError("This review already has a different signed decision")
            return True
        timestamp = now()
        conn.execute("INSERT INTO draft_actions VALUES (?,?,?,?,?,?,?,?)", (state["review_id"], state["alert_id"], state["wallet_id"], state["human_decision"], "approved", timestamp, timestamp, state["officer_id"]))
        saved_pack = json.loads(saved["json_body"])
        detail = json.dumps({"review_id": state["review_id"], "proposed": saved_pack["recommended_action"], "decision": state["human_decision"], "officer_id": state["officer_id"], "comment": state.get("human_comment", ""), "evidence_as_of": alert["opened_at"]})
        conn.execute("INSERT INTO case_events VALUES (?,?,?,?,?)", (state["review_id"] + ":approval", state["alert_id"], timestamp, "approved", detail))
    return True


def read_memories(wallet_id, officer_id):
    return rows("SELECT * FROM memories WHERE wallet_id=? OR (namespace='procedure' AND officer_id=?) ORDER BY created_at, memory_id", (wallet_id, officer_id))


def save_memory(memory_id, namespace, content, wallet_id=None, officer_id=None):
    with connect() as conn:
        conn.execute("INSERT INTO memories VALUES (?,?,?,?,?,?) ON CONFLICT(memory_id) DO NOTHING", (memory_id, namespace, wallet_id, officer_id, content, now()))
