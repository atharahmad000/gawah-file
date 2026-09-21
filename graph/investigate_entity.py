import operator
from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from domain.state import EvidenceMemo
from repos.ledger import list_transactions


class EntityState(TypedDict, total=False):
    entity_wallet_id: str
    role: str
    cutoff: str
    transactions: list[dict]
    evidence: Annotated[list[dict], operator.add]


class EntityOutput(TypedDict):
    evidence: Annotated[list[dict], operator.add]


def load_transactions(state):
    return {"transactions": list_transactions(state["entity_wallet_id"], state["cutoff"])}


def summarise_entity(state):
    transactions = state["transactions"]
    memo = EvidenceMemo(entity_wallet_id=state["entity_wallet_id"], memo_type=state["role"],
        findings=[f"Reviewed {len(transactions)} transactions at or before {state['cutoff']}.",
                  f"Successful outward amount: PKR {sum(t['amount_pkr'] for t in transactions if t['status']=='success' and t['direction']=='out'):,}.",
                  "A shared payee warrants comparison; it does not establish common control."],
        txn_ids=[t["txn_id"] for t in transactions])
    return {"evidence": [memo.model_dump()]}


def build_entity_graph():
    builder = StateGraph(EntityState, output_schema=EntityOutput)
    builder.add_node("list_transactions", load_transactions)
    builder.add_node("summarise_entity", summarise_entity)
    builder.add_edge(START, "list_transactions")
    builder.add_edge("list_transactions", "summarise_entity")
    builder.add_edge("summarise_entity", END)
    return builder.compile()
