"""Tests for final causal reasoning operator handoff."""

from copy import deepcopy

import pytest

from fcf.sidecars.ai_causal_reasoning_chain import (
    CausalHandoffViolation,
    build_causal_reasoning_assessment,
    build_causal_reasoning_operator_handoff,
    build_causal_reasoning_review_packet,
    build_deterministic_causal_chain,
    build_registered_causal_claim_record,
    build_registered_causal_evidence_reference,
    build_registered_causal_premise_record,
    validate_causal_reasoning_operator_handoff,
)


def _premise(claim_id: str) -> dict:
    return build_registered_causal_premise_record(
        premise_id=f"premise-{claim_id}",
        claim_id=claim_id,
        premise_text="Registered causal premise.",
        registration_status="REGISTERED",
        source_artifact_ids=[
            f"source-{claim_id}"
        ],
        correlation_id="correlation-001",
        research_run_id="research-run-001",
    )


def _evidence(
    claim_id: str,
    reference_id: str,
    role: str,
    artifact_type: str,
    status: str = "REGISTERED",
) -> dict:
    return build_registered_causal_evidence_reference(
        evidence_ref_id=reference_id,
        claim_id=claim_id,
        artifact_id=f"artifact-{reference_id}",
        artifact_type=artifact_type,
        evidence_role=role,
        registration_status=status,
        correlation_id="correlation-001",
        research_run_id="research-run-001",
    )


def _claim(
    claim_id: str,
    cause_id: str,
    effect_id: str,
    *,
    support_status: str = "REGISTERED",
) -> dict:
    evidence = [
        _evidence(
            claim_id,
            f"support-{claim_id}",
            "SUPPORTING",
            "REGISTERED_SUPPORTING_EVIDENCE_ARTIFACT",
            support_status,
        ),
        _evidence(
            claim_id,
            f"counter-{claim_id}",
            "COUNTEREVIDENCE",
            "REGISTERED_COUNTEREVIDENCE_ARTIFACT",
        ),
        _evidence(
            claim_id,
            f"alternative-{claim_id}",
            "ALTERNATIVE_EXPLANATION",
            "REGISTERED_ALTERNATIVE_EXPLANATION_ARTIFACT",
        ),
    ]

    return build_registered_causal_claim_record(
        claim_id=claim_id,
        claim_text=f"{cause_id} may contribute to {effect_id}.",
        cause_ref_id=cause_id,
        effect_ref_id=effect_id,
        claim_type="CONTRIBUTORY_CAUSAL_CLAIM",
        claim_registration_status="REGISTERED",
        premise_records=[_premise(claim_id)],
        evidence_references=evidence,
        counterevidence_review_status="REGISTERED_PRESENT",
        alternative_explanation_review_status=(
            "REGISTERED_PRESENT"
        ),
        correlation_id="correlation-001",
        research_run_id="research-run-001",
    )


def _packet(
    claims: list[dict] | None = None,
) -> dict:
    chain = build_deterministic_causal_chain(
        chain_id="chain-001",
        claim_records=(
            claims
            if claims is not None
            else [
                _claim(
                    "claim-001",
                    "factor-a",
                    "factor-b",
                ),
                _claim(
                    "claim-002",
                    "factor-b",
                    "outcome-c",
                ),
            ]
        ),
    )

    assessment = build_causal_reasoning_assessment(
        assessment_id="assessment-001",
        source_chain=chain,
    )

    return build_causal_reasoning_review_packet(
        packet_id="review-packet-001",
        assessment=assessment,
    )


def _handoff(
    packet: dict | None = None,
) -> dict:
    return build_causal_reasoning_operator_handoff(
        handoff_id="handoff-001",
        review_packet=packet or _packet(),
    )


def test_valid_handoff_passes_validation() -> None:
    assert validate_causal_reasoning_operator_handoff(
        _handoff()
    ) == []


def test_ready_packet_creates_operator_decision_handoff() -> None:
    handoff = _handoff()

    assert handoff["handoff_status"] == (
        "READY_FOR_OPERATOR_DECISION"
    )
    assert handoff["archive_handoff_status"] == (
        "READY_FOR_MANUAL_ARCHIVE"
    )


def test_blocked_packet_remains_blocked() -> None:
    packet = _packet(
        [
            _claim(
                "claim-001",
                "factor-a",
                "factor-b",
                support_status="BLOCKED",
            )
        ]
    )

    handoff = _handoff(packet)

    assert handoff["handoff_status"] == "BLOCKED"
    assert handoff["archive_handoff_status"] == (
        "BLOCKED"
    )


def test_operator_decision_remains_pending() -> None:
    handoff = _handoff()

    assert handoff["operator_decision_status"] == (
        "PENDING"
    )
    assert handoff["operator_decision_required"] is True


def test_archive_execution_is_not_automatic() -> None:
    handoff = _handoff()

    assert handoff["manual_archive_required"] is True
    assert handoff["archive_execution_status"] == (
        "NOT_PERFORMED"
    )


def test_next_phase_is_not_selected() -> None:
    assert _handoff()["next_phase_status"] == (
        "NOT_SELECTED"
    )


def test_truth_probability_and_winner_remain_unassigned() -> None:
    handoff = _handoff()

    assert handoff["causal_truth_status"] == (
        "UNDETERMINED"
    )
    assert handoff["probability_status"] == (
        "NOT_ASSIGNED"
    )
    assert handoff["winner_status"] == (
        "NOT_SELECTED"
    )


def test_execution_and_automatic_approval_are_forbidden() -> None:
    handoff = _handoff()

    assert handoff["runtime_execution_status"] == (
        "NOT_ALLOWED"
    )
    assert handoff[
        "live_model_invocation_status"
    ] == "NOT_ALLOWED"
    assert handoff["prompt_execution_status"] == (
        "NOT_ALLOWED"
    )
    assert handoff["automatic_approval_status"] == (
        "NOT_ALLOWED"
    )


def test_source_packet_and_conclusions_are_preserved() -> None:
    handoff = _handoff()

    assert handoff["source_artifacts_preserved"] is True
    assert handoff[
        "original_conclusions_preserved"
    ] is True
    assert handoff["source_review_packet"] == (
        _packet()
    )


def test_invalid_review_packet_is_rejected() -> None:
    packet = _packet()
    packet["causal_truth_status"] = "CONFIRMED"

    with pytest.raises(
        CausalHandoffViolation,
        match="causal_truth_status_invalid",
    ):
        _handoff(packet)


def test_validation_detects_handoff_status_mutation() -> None:
    handoff = _handoff()
    handoff["handoff_status"] = "BLOCKED"

    assert "handoff_status_mismatch" in (
        validate_causal_reasoning_operator_handoff(
            handoff
        )
    )


def test_validation_rejects_archive_execution() -> None:
    handoff = _handoff()
    handoff["archive_execution_status"] = "COMPLETED"

    assert (
        "archive_execution_status_must_be_not_performed"
        in validate_causal_reasoning_operator_handoff(
            handoff
        )
    )


def test_validation_rejects_selected_next_phase() -> None:
    handoff = _handoff()
    handoff["next_phase_status"] = (
        "AI-COMPREHENSIVE-REPORT-SYNTHESIS-APP-1"
    )

    assert (
        "next_phase_status_must_be_not_selected"
        in validate_causal_reasoning_operator_handoff(
            handoff
        )
    )


def test_validation_rejects_automatic_approval() -> None:
    handoff = _handoff()
    handoff["automatic_approval_status"] = "ALLOWED"

    assert (
        "automatic_approval_status_must_be_not_allowed"
        in validate_causal_reasoning_operator_handoff(
            handoff
        )
    )


def test_builder_returns_fresh_containers() -> None:
    first = _handoff()
    second = _handoff()

    mutated = deepcopy(first)
    mutated["source_review_packet"][
        "reason_codes"
    ].append("INVENTED_REASON")
    mutated["review_summary"]["claim_count"] = 999
    mutated["safety_flags"][
        "real_execution_allowed"
    ] = True

    assert second == _handoff()
    assert mutated != second


def test_non_mapping_handoff_is_rejected() -> None:
    assert validate_causal_reasoning_operator_handoff(
        []
    ) == ["handoff_must_be_mapping"]
