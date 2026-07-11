"""D6 tests for narrative operator and archive handoff."""

from dataclasses import replace

import pytest

from fcf.sidecars.market_narrative_context.assessment import (
    NarrativeAssessmentInput,
    NarrativeClaimPolarity,
    assess_narrative_context,
)
from fcf.sidecars.market_narrative_context.handoff import (
    NarrativeHandoffState,
    NarrativeHandoffViolation,
    assert_valid_narrative_review_handoff,
    build_narrative_review_handoff,
    validate_narrative_review_handoff,
)
from fcf.sidecars.market_narrative_context.review_packet import (
    build_narrative_review_packet,
)


def _assessment_input() -> NarrativeAssessmentInput:
    return NarrativeAssessmentInput(
        narrative_artifact_id="artifact:narrative:001",
        target_artifact_id="artifact:research:001",
        narrative_polarity=NarrativeClaimPolarity.SUPPORTS,
        target_polarity=NarrativeClaimPolarity.SUPPORTS,
        narrative_observed_at_utc="2026-07-11T04:00:00Z",
        target_observed_at_utc="2026-07-11T03:00:00Z",
        reference_time_utc="2026-07-11T06:00:00Z",
        max_age_hours=24,
        narrative_evidence_reference_ids=(
            "evidence:company:001",
        ),
        target_evidence_reference_ids=(
            "evidence:company:001",
            "evidence:price:001",
        ),
    )


def _packet(source: NarrativeAssessmentInput | None = None):
    assessment = assess_narrative_context(
        source or _assessment_input()
    )

    return build_narrative_review_packet(
        packet_id="packet:narrative:001",
        correlation_id="correlation:001",
        research_run_id="research-run:001",
        assessment=assessment,
    )


def _handoff():
    return build_narrative_review_handoff(
        handoff_id="handoff:narrative:001",
        packet=_packet(),
    )


def test_ready_packet_maps_to_archive_review() -> None:
    handoff = _handoff()

    assert (
        handoff.handoff_state
        is NarrativeHandoffState.READY_FOR_ARCHIVE_REVIEW
    )
    assert handoff.source_packet_state == (
        "READY_FOR_OPERATOR_REVIEW"
    )
    assert validate_narrative_review_handoff(handoff) == ()


def test_contradiction_maps_to_review_required() -> None:
    source = replace(
        _assessment_input(),
        target_polarity=NarrativeClaimPolarity.OPPOSES,
    )

    handoff = build_narrative_review_handoff(
        handoff_id="handoff:narrative:002",
        packet=_packet(source),
    )

    assert (
        handoff.handoff_state
        is NarrativeHandoffState.REVIEW_REQUIRED
    )
    assert handoff.risk_flags == ("CONTRADICTION_DETECTED",)


def test_stale_packet_maps_to_blocked_handoff() -> None:
    source = replace(
        _assessment_input(),
        narrative_observed_at_utc="2026-07-01T04:00:00Z",
    )

    handoff = build_narrative_review_handoff(
        handoff_id="handoff:narrative:003",
        packet=_packet(source),
    )

    assert (
        handoff.handoff_state
        is NarrativeHandoffState.BLOCKED_PENDING_EVIDENCE
    )
    assert handoff.risk_flags == ("NARRATIVE_STALE",)


def test_handoff_preserves_packet_evidence_and_identity() -> None:
    packet = _packet()

    handoff = build_narrative_review_handoff(
        handoff_id="handoff:narrative:004",
        packet=packet,
    )

    assert handoff.packet_id == packet.packet_id
    assert handoff.correlation_id == packet.correlation_id
    assert handoff.research_run_id == packet.research_run_id
    assert handoff.reason_codes == packet.reason_codes
    assert handoff.risk_flags == packet.risk_flags


def test_handoff_preserves_permanent_safety_boundary() -> None:
    handoff = _handoff()

    assert handoff.review_status == "PENDING_OPERATOR_REVIEW"
    assert handoff.truth_status == "UNDETERMINED"
    assert handoff.operator_review_required is True
    assert handoff.operator_review_bypass_allowed is False
    assert handoff.archive_required is True
    assert handoff.source_packet_preserved is True
    assert handoff.original_conclusions_preserved is True
    assert handoff.no_execution_receipt is True
    assert handoff.automatic_truth_decision_allowed is False
    assert handoff.automatic_conclusion_replacement_allowed is False
    assert handoff.trade_action_allowed is False
    assert handoff.real_execution_allowed is False


def test_invalid_state_mapping_is_rejected() -> None:
    handoff = replace(
        _handoff(),
        handoff_state=NarrativeHandoffState.REVIEW_REQUIRED,
    )

    assert validate_narrative_review_handoff(handoff) == (
        "HANDOFF_STATE_MAPPING_MISMATCH",
        "NON_READY_HANDOFF_REQUIRES_RISK_FLAG",
    )


def test_review_bypass_is_rejected() -> None:
    handoff = replace(
        _handoff(),
        operator_review_bypass_allowed=True,
    )

    with pytest.raises(
        NarrativeHandoffViolation,
        match="REQUIRED_FALSE:operator_review_bypass_allowed",
    ):
        assert_valid_narrative_review_handoff(handoff)


def test_serialization_is_deterministic() -> None:
    first = _handoff().to_dict()
    second = _handoff().to_dict()

    assert first == second
    assert first["handoff_state"] == "READY_FOR_ARCHIVE_REVIEW"
    assert first["archive_required"] is True
    assert first["truth_status"] == "UNDETERMINED"
    assert first["trade_action_allowed"] is False
