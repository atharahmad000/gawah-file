from langgraph.types import Send


def plan_sends(state):
    wallets = state.get("related_wallet_ids", [])
    if not wallets:
        return "write_pack"
    return [Send("investigate_entity", {"entity_wallet_id": wid,
        "role": "subject" if wid == state["wallet_id"] else "counterparty",
        "cutoff": state["cutoff"]}) for wid in wallets]
