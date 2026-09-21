from repos import ledger
from repos.cases import list_prior_cases, goodwill_this_quarter
from repos.flags import get_risk_flags
from retrieve.retriever import search_playbook

QUERIES = {
    "first_credit_drain": "first inbound credit then cash-out within 30 minutes 80 percent",
    "night_bill_camouflage": "six failed utility bills night 01:00 05:00 followed by successful cash-out two hours",
    "shared_payee": "two recently opened wallets sending same new payee within 24 hours linked investigation",
    "loyal_odd": "loyal long customer single odd P2P send do not freeze grocery household bill history",
    "watchlist_repeat": "already reviewed watchlist active flag tiny grocery purchase prior closed case no new typology",
    "duplicate_debit": "two equal merchant debits same shop eleven minutes goodwill already approved this quarter",
}


def gather_sql(state):
    wallet, cutoff = state["wallet_id"], state["cutoff"]
    findings = {
        "get_wallet": state["wallet"],
        "list_transactions": ledger.list_transactions(wallet, cutoff),
        "find_first_credit_drain": ledger.find_first_credit_drain(wallet, cutoff),
        "find_night_failed_bills": ledger.find_night_failed_bills(wallet, cutoff),
        "find_cashout_after_failures": ledger.find_cashout_after_failures(wallet, cutoff),
        "find_shared_payee": ledger.find_shared_payee(wallet, cutoff),
        "wallet_links": ledger.wallet_links(wallet, cutoff),
        "find_duplicate_merchant_debit": ledger.find_duplicate_merchant_debit(wallet, cutoff),
        "get_risk_flags": get_risk_flags(wallet),
        "list_prior_cases": list_prior_cases(wallet, cutoff),
        "goodwill_this_quarter": goodwill_this_quarter(wallet, cutoff),
    }
    related = sorted({row[key] for row in findings["find_shared_payee"] + findings["wallet_links"] for key in ("wallet_a", "wallet_b")})
    return {"sql_findings": findings, "related_wallet_ids": related}


def retrieve_playbook(state):
    findings = state["sql_findings"]
    query = QUERIES.get(state["alert"]["alert_code"], "unknown typology")
    digest = f" drain pairs {len(findings['find_first_credit_drain'])}; night failures {len(findings['find_night_failed_bills'])}; linked wallets {len(state.get('related_wallet_ids', []))}"
    return {"policy_hits": search_playbook(query + digest)}


def score_hint(state):
    from repos.features import calculate_features
    from risk.hint import score
    hint, reasons = score(calculate_features(state["wallet_id"], state["cutoff"]))
    return {"risk_hint": hint, "risk_hint_reasons": reasons}
