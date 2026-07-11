"""D4 tests for deterministic narrative assessment."""

from dataclasses import replace

import pytest

from fcf.sidecars.market_narrative_context.assessment import (
    NarrativeAssessmentDisposition,
    NarrativeAssessmentInput,
    NarrativeAssessmentViolation,
    NarrativeClaimPolarity,
    NarrativeFreshnessState,
    assess_narrative_context,
    assert_valid_assessment_input,
    validate_assessment_input,
)


def _assessment() -> NarrativeAssessmentInput:
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


def test_valid_assessment_input_passes() -> None:
    assessment = _assessment()

    assert validate_assessment_input(assessment) == ()
    assert_valid_assessment_input(assessment)


def test_clear_fresh_supported_context_is_ready_for_review() -> None:
    result = assess_narrative_context(_assessment())

    assert (
        result.disposition
        is NarrativeAssessmentDisposition.READY_FOR_REVIEW
    )
    assert result.contradiction_detected is False
    assert result.uncertainty_detected is False
    assert result.evidence_gap_detected is False
    assert result.risk_flags == ()


def test_opposite_polarity_requires_review() -> None:
    assessment = replace(
        _assessment(),
        target_polarity=NarrativeClaimPolarity.OPPOSES,
    )

    result = assess_narrative_context(assessment)

    assert (
        result.disposition
        is NarrativeAssessmentDisposition.REVIEW_REQUIRED
    )
    assert result.contradiction_detected is True
    assert result.risk_flags == (
        "CONTRADICTION_DETECTED",
    )


def test_unknown_polarity_requires_review() -> None:
    assessment = replace(
        _assessment(),
        narrative_polarity=NarrativeClaimPolarity.UNKNOWN,
    )

    result = assess_narrative_context(assessment)

    assert (
        result.disposition
        is NarrativeAssessmentDisposition.REVIEW_REQUIRED
    )
    assert result.uncertainty_detected is True
    assert result.risk_flags == ("UNCERTAINTY_PRESENT",)


def test_stale_narrative_blocks_assessment() -> None:
    assessment = replace(
        _assessment(),
        narrative_observed_at_utc="2026-07-01T04:00:00Z",
    )

    result = assess_narrative_context(assessment)

    assert (
        result.disposition
        is NarrativeAssessmentDisposition.BLOCKED
    )
    assert (
        result.narrative_freshness_state
        is NarrativeFreshnessState.STALE
    )
    assert result.risk_flags == ("NARRATIVE_STALE",)


def test_missing_narrative_evidence_blocks_assessment() -> None:
    assessment = replace(
        _assessment(),
        narrative_evidence_reference_ids=(),
    )

    result = assess_narrative_context(assessment)

    assert (
        result.disposition
        is NarrativeAssessmentDisposition.BLOCKED
    )
    assert result.evidence_gap_detected is True
    assert result.risk_flags == (
        "NARRATIVE_EVIDENCE_MISSING",
    )


def test_no_shared_evidence_blocks_assessment() -> None:
    assessment = replace(
        _assessment(),
        target_evidence_reference_ids=(
            "evidence:price:001",
        ),
    )

    result = assess_narrative_context(assessment)

    assert (
        result.disposition
        is NarrativeAssessmentDisposition.BLOCKED
    )
    assert result.risk_flags == (
        "NO_SHARED_EVIDENCE_REFERENCE",
    )


def test_future_observation_is_rejected() -> None:
    assessment = replace(
        _assessment(),
        narrative_observed_at_utc="2026-07-12T04:00:00Z",
    )

    with pytest.raises(
        NarrativeAssessmentViolation,
        match="NARRATIVE_OBSERVED_AFTER_REFERENCE",
    ):
        assert_valid_assessment_input(assessment)


def test_result_preserves_permanent_safety_boundary() -> None:
    result = assess_narrative_context(_assessment())

    assert result.truth_status == "UNDETERMINED"
    assert result.operator_review_required is True
    assert result.original_conclusions_preserved is True
    assert result.automatic_truth_decision_allowed is False
    assert result.automatic_conclusion_replacement_allowed is False
    assert result.trade_action_allowed is False


def test_serialization_is_deterministic() -> None:
    first = assess_narrative_context(_assessment()).to_dict()
    second = assess_narrative_context(_assessment()).to_dict()

    assert first == second
    assert first["disposition"] == "READY_FOR_REVIEW"
    assert first["truth_status"] == "UNDETERMINED"
    assert first["operator_review_required"] is True
