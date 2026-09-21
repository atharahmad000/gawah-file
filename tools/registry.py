"""Optional model-facing tools. There is deliberately no mutation tool here."""
from langchain_core.tools import StructuredTool
from repos.wallets import get_wallet
from repos.ledger import list_transactions, find_first_credit_drain, find_night_failed_bills, find_shared_payee, find_duplicate_merchant_debit
from repos.flags import get_risk_flags
from repos.cases import list_prior_cases, goodwill_this_quarter
from repos.playbook_sql import get_clause
from retrieve.retriever import search_playbook

READ_FUNCTIONS = [get_wallet, list_transactions, find_first_credit_drain,
    find_night_failed_bills, find_shared_payee, find_duplicate_merchant_debit,
    get_risk_flags, list_prior_cases, goodwill_this_quarter, get_clause, search_playbook]


def read_tools():
    return [StructuredTool.from_function(fn, description=f"Read-only evidence lookup: {fn.__name__}. Identifiers must match the supplied case.") for fn in READ_FUNCTIONS]
