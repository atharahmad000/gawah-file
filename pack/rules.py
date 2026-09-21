from datetime import datetime
from domain.state import EvidencePack


def write_pack_template(state):
    facts = state["sql_findings"]
    code = state["alert"]["alert_code"]
    action, headline, wanted = "watch", "The evidence needs an officer's review.", []
    questions = ["What additional customer or settlement evidence would resolve the open concern?"]
    why = "The file supports review; it does not establish intent."
    known = list(state.get("known_facts", []))
    age = (datetime.fromisoformat(state["cutoff"]) - datetime.fromisoformat(state["wallet"]["opened_on"])).days
    if code == "first_credit_drain" and facts["find_first_credit_drain"] and age <= 14:
        action = "freeze"
        headline = "A new wallet moved most of its first credit out within 30 minutes."
        wanted = ["T01_first_credit_drain"]
        why = "A draft freeze merits review because the first-credit timing and amount are corroborated."
    elif code == "night_bill_camouflage" and len(facts["find_night_failed_bills"]) >= 6 and facts["find_cashout_after_failures"]:
        action = "freeze" if state["risk_hint"] == "high" else "watch"
        headline = "Repeated night bill failures preceded a successful cash-out."
        wanted = ["T02_night_bill_camouflage"]
        questions = ["Was there a utility outage or another ordinary cause for the failures?"]
    elif code == "shared_payee" and facts["find_shared_payee"]:
        headline = "Two recently opened wallets sent funds to the same new payee."
        wanted = ["T03_shared_new_payee"]
        why = "Investigate both wallets; a shared payee alone does not establish coordination."
    elif code == "loyal_odd" and age > 90 and not facts["find_first_credit_drain"]:
        headline = "An established customer made one unusual personal transfer."
        wanted = ["T04_loyal_customer_one_odd", "T07_when_not_to_freeze"]
        why = "Ordinary spending history and no first-credit drain support restraint."
    elif code == "watchlist_repeat" and any(f["flag_type"] == "watchlist" for f in facts["get_risk_flags"]):
        action = "close"
        headline = "Flag remains; no new typology in the small grocery purchase."
        wanted = ["T05_already_reviewed_watchlist"]
        why = "Prior review closed. Closing this alert does not clear the active watchlist."
        closed = [case for case in facts["list_prior_cases"] if case["decision"] == "close"]
        if closed:
            known.append(f"Prior review {closed[0]['case_id']} closed; watchlist remains active.")
    elif code == "duplicate_debit" and facts["find_duplicate_merchant_debit"]:
        headline = "Two equal shop debits need a duplicate-payment investigation."
        wanted = ["T06_duplicate_merchant_debit", "T10_goodwill_and_care_desk"]
        why = "Investigate a one-leg reversal; the duplicate-debit pattern does not support a freeze."
        questions = ["Do receipts and settlement records establish a duplicate rather than two purchases?"]
        if facts["goodwill_this_quarter"]:
            known.append("Goodwill already used this quarter; do not propose another goodwill payment.")
    if state["desk_role"] == "care" and action in {"freeze", "file_compliance"}:
        action = "watch"
        why = "The care desk refers the concern for officer review while proposing watch."
    hits = {h["clause_id"]: h for h in state.get("policy_hits", [])}
    cited = [cid for cid in wanted if cid in hits]
    if not cited:
        action = "watch"
        headline = "No matching typology — escalate."
        why = "No applicable retrieved clause supports a stronger recommendation."
    else:
        why += " [" + ", ".join(cited) + "]"
    quotes = [{"clause_id": cid, "quote": hits[cid]["text"].split("\n\n")[1].split(". ")[0] + "."} for cid in cited]
    # The timeline is the repository's most recent 30 subject transactions.
    transactions = facts["list_transactions"]
    timeline = [{"ts": t["txn_ts"], "txn_id": t["txn_id"], "amount_pkr": t["amount_pkr"],
                 "description": f"{t['txn_type']} / {t['direction']} / {t['status']}"} for t in transactions]
    pack = EvidencePack(alert_id=state["alert_id"], wallet_id=state["wallet_id"], headline=headline,
        timeline=sorted(timeline, key=lambda t: (t["ts"],t["txn_id"])), sql_queries_relied_on=list(facts),
        linked_wallets=state.get("related_wallet_ids", []),
        linked_evidence=sorted(state.get("evidence", []), key=lambda memo: memo["entity_wallet_id"]),
        clause_ids_cited=cited, clause_quotes=quotes,
        risk_hint=state["risk_hint"], risk_hint_reasons=state.get("risk_hint_reasons", []),
        recommended_action=action, why_not_other_actions=why, open_questions=questions,
        known_facts=sorted(set(known)), brief_style=state["officer"]["brief_style"])
    return pack


def write_pack(state):
    pack = write_pack_template(state)
    return {"pack": pack.model_dump(mode="json"), "proposed_action": pack.recommended_action.value,
            "proposed_rationale": pack.why_not_other_actions}
