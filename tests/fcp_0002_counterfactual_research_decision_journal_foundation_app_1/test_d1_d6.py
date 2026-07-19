from types import MappingProxyType

import pytest

from apps.fcp_0002_counterfactual_research_decision_journal_foundation_app_1 import (
    CandidateDisposition,
    CounterfactualDecisionJournal,
    DecisionAlternative,
    RegisteredOutcome,
    ResearchDecisionSnapshot,
    build_counterfactual_review_packet,
    evaluate_counterfactuals,
    validate_counterfactual_acceptance,
)


H1, H2, H3 = "a" * 64, "b" * 64, "c" * 64


def _alternative(candidate_id, disposition, expected=10):
    return DecisionAlternative(candidate_id, disposition, ("registered-reason",), (H1,), expected)


def _decision(predecessor=None, decision_id="decision-1", decided="2026-07-19T10:00:00Z"):
    return ResearchDecisionSnapshot(
        "journal-1",
        decision_id,
        decided,
        decided,
        (
            _alternative("candidate-a", CandidateDisposition.SELECTED),
            _alternative("candidate-b", CandidateDisposition.REJECTED),
            _alternative("candidate-c", CandidateDisposition.EXPIRED),
        ),
        predecessor_hash=predecessor,
    )


def test_snapshot_is_deterministic_and_pre_outcome() -> None:
    left, right = _decision(), _decision()
    assert left.decision_hash == right.decision_hash
    with pytest.raises(ValueError, match="information cutoff"):
        ResearchDecisionSnapshot(
            "journal-1", "bad", "2026-07-19T10:00:00Z", "2026-07-19T10:00:01Z",
            (_alternative("candidate-a", CandidateDisposition.ABSTAINED),),
        )


def test_decision_requires_selection_or_abstention() -> None:
    with pytest.raises(ValueError, match="selection or an abstention"):
        ResearchDecisionSnapshot(
            "journal-1", "bad", "2026-07-19T10:00:00Z", "2026-07-19T10:00:00Z",
            (_alternative("candidate-a", CandidateDisposition.REJECTED),),
        )


def test_append_only_hash_chain() -> None:
    first = _decision()
    second = _decision(first.decision_hash, "decision-2", "2026-07-19T11:00:00Z")
    journal = CounterfactualDecisionJournal((first, second))
    assert journal.head_hash == second.decision_hash
    with pytest.raises(ValueError, match="hash chain"):
        CounterfactualDecisionJournal((first, _decision(H3, "decision-3", "2026-07-19T12:00:00Z")))


def test_outcome_must_follow_decision() -> None:
    decision = _decision()
    early = RegisteredOutcome("outcome-1", decision.decision_hash, "candidate-a", "2026-07-19T09:00:00Z", 5, (H2,))
    with pytest.raises(ValueError, match="observed after"):
        evaluate_counterfactuals(decision, (early,))


def test_counterfactual_comparison_preserves_all_alternatives() -> None:
    decision = _decision()
    outcomes = (
        RegisteredOutcome("outcome-a", decision.decision_hash, "candidate-a", "2026-07-20T10:00:00Z", 10, (H2,)),
        RegisteredOutcome("outcome-b", decision.decision_hash, "candidate-b", "2026-07-20T10:00:00Z", 25, (H2,)),
        RegisteredOutcome("outcome-c", decision.decision_hash, "candidate-c", "2026-07-20T10:00:00Z", -20, (H3,)),
    )
    findings = evaluate_counterfactuals(decision, outcomes)
    assert [item.candidate_id for item in findings] == ["candidate-a", "candidate-b", "candidate-c"]
    assert [item.classification for item in findings] == ["NEUTRAL", "MISSED_UPSIDE", "AVOIDED_DOWNSIDE"]
    assert decision.alternatives[1].disposition is CandidateDisposition.REJECTED


def test_missing_outcome_is_visible_not_comparable() -> None:
    decision = _decision()
    findings = evaluate_counterfactuals(decision, ())
    assert all(item.classification == "NOT_COMPARABLE" for item in findings)


def test_review_packet_is_read_only_and_research_only() -> None:
    decision = _decision()
    packet = build_counterfactual_review_packet(decision, evaluate_counterfactuals(decision, ()))
    assert isinstance(packet.payload, MappingProxyType)
    assert packet.payload["proposal_status"] == "NEEDS_RESEARCH"
    assert packet.payload["phase_authorization_allowed"] is False
    assert all(validate_counterfactual_acceptance(packet).values())
    with pytest.raises(TypeError):
        packet.payload["proposal_status"] = "IMPLEMENTED"  # type: ignore[index]
