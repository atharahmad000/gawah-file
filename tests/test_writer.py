from uuid import uuid4
from domain.state import EvidencePack
from pack.writer import guard_model_pack, write_pack
from studio.desk_graph import local_graph


def test_hallucinated_citations_and_financial_fields(monkeypatch):
    with local_graph() as graph:
        state = graph.invoke({"alert_id": "A4", "officer_id": "off_fraud_01"}, {"configurable": {"thread_id": str(uuid4())}})
    baseline = EvidencePack.model_validate(state["pack"])
    candidate = baseline.model_dump(mode="json")
    candidate.update(clause_ids_cited=["T08_pass_through_mule"], recommended_action="freeze", wallet_id="invented")
    result = guard_model_pack(candidate, baseline, state["policy_hits"])
    assert "T08_pass_through_mule" not in result.clause_ids_cited
    assert result.recommended_action == "watch"
    assert result.wallet_id == "w_ayesha_lhr"
    monkeypatch.setenv("GAWAH_OFFLINE", "0")
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    fallback = write_pack(state)
    assert fallback["proposed_action"] == "watch"
    assert fallback["writer_error"] == "ValueError"


def test_model_cannot_remove_support_for_retained_rationale():
    with local_graph() as graph:
        state = graph.invoke({"alert_id": "A4", "officer_id": "off_fraud_01"},
                             {"configurable": {"thread_id": str(uuid4())}})
    baseline = EvidencePack.model_validate(state["pack"])
    assert len(baseline.clause_ids_cited) == 2
    candidate = baseline.model_dump(mode="json")
    candidate.update(clause_ids_cited=[baseline.clause_ids_cited[0]],
                     clause_quotes=[{"clause_id": baseline.clause_ids_cited[0], "quote": "Invented policy text"}])
    result = guard_model_pack(candidate, baseline, state["policy_hits"])
    assert result.clause_ids_cited == baseline.clause_ids_cited
    assert result.clause_quotes == baseline.clause_quotes
