from uuid import uuid4
from langgraph.graph import StateGraph, START, END
from domain.state import CaseInput, CaseState
from repos.alerts import get_alert
from repos.wallets import get_wallet, get_officer
from graph.gather import gather_sql, retrieve_playbook, score_hint
from pack.writer import write_pack
from graph.gates import gate, apply_action
from graph.investigate_entity import build_entity_graph
from graph.routing import plan_sends
from graph.memory import known_facts, write_memory
from langgraph.store.base import BaseStore
from repos.reviews import record_pack


def load_alert(state, config, *, store: BaseStore):
    if state.get("review_id"):
        raise ValueError("Use a fresh thread for a new investigation; update the existing review to add an officer message")
    alert = get_alert(state["alert_id"])
    officer_id = state.get("officer_id") or config.get("configurable", {}).get("officer_id")
    officer = get_officer(officer_id)
    if not alert or not officer:
        raise ValueError("Unknown alert or officer")
    return dict(alert=alert, wallet=get_wallet(alert["wallet_id"]), wallet_id=alert["wallet_id"],
                officer_id=officer_id, officer=officer, desk_role=officer["desk"],
                cutoff=alert["opened_at"], review_id=str(uuid4()), signed=False,
                human_decision=None, applied=False, known_facts=known_facts(alert["wallet_id"], officer_id, store))


def make_builder():
    builder = StateGraph(CaseState, input_schema=CaseInput)
    builder.add_node("load_alert", load_alert)
    builder.add_edge(START, "load_alert")
    for name, node in [("gather_sql", gather_sql), ("retrieve_playbook", retrieve_playbook), ("score_hint", score_hint), ("write_pack", write_pack)]:
        builder.add_node(name, node)
    builder.add_edge("load_alert", "gather_sql")
    builder.add_edge("gather_sql", "retrieve_playbook")
    builder.add_edge("gather_sql", "score_hint")
    builder.add_node("merge", lambda state: {})
    builder.add_node("investigate_entity", build_entity_graph())
    builder.add_edge(["retrieve_playbook", "score_hint"], "merge")
    builder.add_conditional_edges("merge", plan_sends, ["investigate_entity", "write_pack"])
    builder.add_edge("investigate_entity", "write_pack")
    builder.add_node("gate", gate)
    builder.add_node("apply_action", apply_action)
    builder.add_edge("write_pack", "gate")
    builder.add_edge("gate", "apply_action")
    builder.add_node("persist_pack", lambda state: (record_pack(state) or {}))
    builder.add_node("write_memory", write_memory)
    builder.add_conditional_edges("apply_action", lambda state: "persist_pack" if state.get("applied") else "gate", ["persist_pack", "gate"])
    builder.add_edge("persist_pack", "write_memory")
    builder.add_edge("write_memory", END)
    return builder
