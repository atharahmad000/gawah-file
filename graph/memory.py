from langgraph.store.base import BaseStore
from repos.reviews import read_memories, save_memory


def known_facts(wallet_id, officer_id, store):
    # SQL is the durable mirror; hydrate only the subject and officer namespaces.
    for row in read_memories(wallet_id, officer_id):
        owner = row["officer_id"] if row["namespace"] == "procedure" else row["wallet_id"]
        store.put((row["namespace"], owner), row["memory_id"], {"content": row["content"]})
    facts = []
    for namespace in [("profile", wallet_id), ("cases", wallet_id), ("procedure", officer_id)]:
        facts.extend(item.value["content"] for item in store.search(namespace, limit=100))
    return sorted(set(facts))


def write_memory(state, *, store: BaseStore):
    if not state.get("applied"):
        return {}
    content = f"Review {state['review_id']} for {state['alert_id']}: officer approved {state['human_decision']}; evidence cutoff {state['cutoff']}."
    save_memory(state["review_id"], "cases", content, wallet_id=state["wallet_id"], officer_id=state["officer_id"])
    store.put(("cases", state["wallet_id"]), state["review_id"], {"content": content})
    return {}
