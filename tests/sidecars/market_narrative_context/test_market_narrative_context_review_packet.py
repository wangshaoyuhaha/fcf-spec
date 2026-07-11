"""D5 tests for the paper-only narrative review packet."""

from dataclasses import replace

import pytest

from fcf.sidecars.market_narrative_context.assessment import (
    NarrativeAssessmentInput,
    NarrativeClaimPolarity,
    assess_narrative_context,
)
from fcf.sidecars.market_narrative_context.review_packet import (
    NarrativeReviewPacketState,
    NarrativeReviewPacketViolation,
    assert_valid_narrative_review_packet,
    build_narrative_review_packet,
    validate_narrative_review_packet,
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


def _packet():
    assessment = assess_narrative_context(_assessment_input())

    return build_narrative_review_packet(
        packet_id="packet:narrative:001",
        correlation_id="correlation:001",
        research_run_id="research-run:001",
        assessment=assessment,
    )


def test_ready_assessment_builds_operator_review_packet() -> None:
    packet = _packet()

    assert (
        packet.packet_state
        is NarrativeReviewPacketState.READY_FOR_OPERATOR_REVIEW
    )
    assert packet.assessment_disposition == "READY_FOR_REVIEW"
    assert packet.review_status == "PENDING_OPERATOR_REVIEW"
    assert validate_narrative_review_packet(packet) == ()


def test_contradiction_builds_review_required_packet() -> None:
    source = replace(
        _assessment_input(),
        target_polarity=NarrativeClaimPolarity.OPPOSES,
    )
    assessment = assess_narrative_context(source)

    packet = build_narrative_review_packet(
        packet_id="packet:narrative:002",
        correlation_id="correlation:002",
        research_run_id="research-run:002",
        assessment=assessment,
    )

    assert (
        packet.packet_state
        is NarrativeReviewPacketState.REVIEW_REQUIRED
    )
    assert packet.risk_flags == ("CONTRADICTION_DETECTED",)


def test_stale_assessment_builds_blocked_packet() -> None:
    source = replace(
        _assessment_input(),
        narrative_observed_at_utc="2026-07-01T04:00:00Z",
    )
    assessment = assess_narrative_context(source)

    packet = build_narrative_review_packet(
        packet_id="packet:narrative:003",
        correlation_id="correlation:003",
        research_run_id="research-run:003",
        assessment=assessment,
    )

    assert (
        packet.packet_state
        is NarrativeReviewPacketState.BLOCKED_PENDING_EVIDENCE
    )
    assert packet.risk_flags == ("NARRATIVE_STALE",)


def test_packet_preserves_assessment_reason_codes_and_risk_flags() -> None:
    source = replace(
        _assessment_input(),
        narrative_polarity=NarrativeClaimPolarity.UNKNOWN,
    )
    assessment = assess_narrative_context(source)

    packet = build_narrative_review_packet(
        packet_id="packet:narrative:004",
        correlation_id="correlation:004",
        research_run_id="research-run:004",
        assessment=assessment,
    )

    assert packet.reason_codes == assessment.reason_codes
    assert packet.risk_flags == assessment.risk_flags


def test_packet_preserves_permanent_safety_boundary() -> None:
    packet = _packet()

    assert packet.truth_status == "UNDETERMINED"
    assert packet.operator_review_required is True
    assert packet.operator_review_bypass_allowed is False
    assert packet.original_conclusions_preserved is True
    assert packet.no_execution_receipt is True
    assert packet.automatic_truth_decision_allowed is False
    assert packet.automatic_conclusion_replacement_allowed is False
    assert packet.trade_action_allowed is False
    assert packet.real_execution_allowed is False


def test_invalid_packet_identifier_is_rejected() -> None:
    packet = replace(
        _packet(),
        packet_id="",
    )

    with pytest.raises(
        NarrativeReviewPacketViolation,
        match="INVALID_IDENTIFIER:packet_id",
    ):
        assert_valid_narrative_review_packet(packet)


def test_review_bypass_is_rejected() -> None:
    packet = replace(
        _packet(),
        operator_review_bypass_allowed=True,
    )

    assert validate_narrative_review_packet(packet) == (
        "REQUIRED_FALSE:operator_review_bypass_allowed",
    )


def test_serialization_is_deterministic() -> None:
    first = _packet().to_dict()
    second = _packet().to_dict()

    assert first == second
    assert first["packet_state"] == "READY_FOR_OPERATOR_REVIEW"
    assert first["review_status"] == "PENDING_OPERATOR_REVIEW"
    assert first["truth_status"] == "UNDETERMINED"
    assert first["trade_action_allowed"] is False
