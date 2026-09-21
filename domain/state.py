import operator
from typing import Annotated, Literal
from typing_extensions import TypedDict
from langgraph.graph.message import add_messages
from pydantic import BaseModel, ConfigDict, Field
from domain.enums import ActionType, RiskHint


def union(left, right):
    return sorted(set(left or []) | set(right or []))


class TimelineEntry(BaseModel):
    ts: str
    txn_id: str
    amount_pkr: int = Field(ge=0)
    description: str


class ClauseQuote(BaseModel):
    clause_id: str
    quote: str


class EvidenceMemo(BaseModel):
    entity_wallet_id: str
    memo_type: Literal["subject", "counterparty"]
    findings: list[str] = Field(min_length=3, max_length=8)
    txn_ids: list[str]


class EvidencePack(BaseModel):
    model_config = ConfigDict(extra="forbid")
    alert_id: str
    wallet_id: str
    headline: str
    timeline: list[TimelineEntry]
    sql_queries_relied_on: list[str]
    linked_wallets: list[str]
    linked_evidence: list[EvidenceMemo] = Field(default_factory=list)
    clause_ids_cited: list[str]
    clause_quotes: list[ClauseQuote]
    risk_hint: RiskHint
    risk_hint_reasons: list[str]
    recommended_action: ActionType
    why_not_other_actions: str
    open_questions: list[str]
    known_facts: list[str] = Field(default_factory=list)
    brief_style: str = "tables"
    writer: str = "template"


class ProposedAction(BaseModel):
    action: ActionType
    rationale: str


class CaseInput(TypedDict):
    alert_id: str
    officer_id: str


class CaseState(TypedDict, total=False):
    messages: Annotated[list, add_messages]
    alert_id: str
    wallet_id: str
    officer_id: str
    desk_role: str
    alert: dict
    wallet: dict
    officer: dict
    cutoff: str
    review_id: str
    related_wallet_ids: Annotated[list[str], union]
    evidence: Annotated[list[dict], operator.add]
    policy_hits: Annotated[list[dict], operator.add]
    sql_findings: dict
    risk_hint: str
    risk_hint_reasons: list[str]
    pack: dict
    proposed_action: str
    proposed_rationale: str
    human_decision: str | None
    human_comment: str
    gate_reason: str
    signed: bool
    applied: bool
    known_facts: list[str]
    writer_error: str
