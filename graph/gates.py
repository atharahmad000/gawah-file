from repos.reviews import approve, record_pack


def gate_reasons(state):
    reasons = []
    if any(f["flag_type"] == "watchlist" for f in state["sql_findings"]["get_risk_flags"]):
        reasons.append("active watchlist")
    if state["risk_hint"] == "high":
        reasons.append("high risk hint")
    if state["proposed_action"] in {"freeze", "file_compliance"}:
        reasons.append("restricted action proposed")
    if len(state.get("related_wallet_ids", [])) >= 2:
        reasons.append("linked-wallet investigation")
    return reasons or ["all investigation packs require human sign-off"]


def should_force_interrupt(state):
    return bool(gate_reasons(state))


def gate(state):
    record_pack(state)
    return {"gate_reason": "; ".join(gate_reasons(state))}


def apply_action(state):
    return {"applied": approve(state)}
