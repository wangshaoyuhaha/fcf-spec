"""Tests for causal reasoning D5 governance review packets."""

from copy import deepcopy

import pytest

from fcf.sidecars.ai_causal_reasoning_chain import (
    CausalReviewPacketViolation,
    build_causal_reasoning_assessment,
    build_causal_reasoning_review_packet,
    build_deterministic_causal_chain,
    build_registered_causal_claim_record,
    build_registered_causal_evidence_reference,
    build_registered_causal_premise_record,
    validate_causal_reasoning_review_packet,
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
    include_support: bool = True,
    support_status: str = "REGISTERED",
) -> dict:
    evidence = []

    if include_support:
        evidence.append(
            _evidence(
                claim_id,
                f"support-{claim_id}",
                "SUPPORTING",
                "REGISTERED_SUPPORTING_EVIDENCE_ARTIFACT",
                support_status,
            )
        )

    evidence.extend(
        [
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
    )

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


def _assessment(
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

    return build_causal_reasoning_assessment(
        assessment_id="assessment-001",
        source_chain=chain,
    )


def _packet(
    assessment: dict | None = None,
) -> dict:
    return build_causal_reasoning_review_packet(
        packet_id="review-packet-001",
        assessment=assessment or _assessment(),
    )


def test_valid_review_packet_passes_validation() -> None:
    assert validate_causal_reasoning_review_packet(
        _packet()
    ) == []


def test_clean_assessment_is_ready_for_operator_review() -> None:
    packet = _packet()

    assert packet["packet_status"] == (
        "READY_FOR_OPERATOR_REVIEW"
    )
    assert packet["review_priority"] == "STANDARD"


def test_informational_findings_remain_visible() -> None:
    packet = _packet()

    assert packet["severity_counts"]["INFO"] > 0
    assert packet["review_summary"][
        "non_info_finding_count"
    ] == 0


def test_review_summary_matches_source_chain() -> None:
    packet = _packet()
    summary = packet["review_summary"]

    assert summary["claim_count"] == 2
    assert summary["node_count"] == 3
    assert summary["edge_count"] == 2
    assert summary["component_count"] == 1


def test_disconnected_chain_creates_high_priority_packet() -> None:
    assessment = _assessment(
        [
            _claim(
                "claim-001",
                "factor-a",
                "factor-b",
            ),
            _claim(
                "claim-002",
                "factor-x",
                "outcome-y",
            ),
        ]
    )

    packet = _packet(assessment)

    assert packet["packet_status"] == "REVIEW_REQUIRED"
    assert packet["review_priority"] == "HIGH"
    assert (
        "REVIEW_DISCONNECTED_COMPONENTS"
        in packet["required_operator_actions"]
    )


def test_cycle_creates_critical_blocked_packet() -> None:
    assessment = _assessment(
        [
            _claim(
                "claim-001",
                "factor-a",
                "factor-b",
            ),
            _claim(
                "claim-002",
                "factor-b",
                "factor-a",
            ),
        ]
    )

    packet = _packet(assessment)

    assert packet["packet_status"] == "BLOCKED"
    assert packet["review_priority"] == "CRITICAL"
    assert "REVIEW_CYCLE_STRUCTURE" in (
        packet["required_operator_actions"]
    )


def test_missing_support_creates_operator_action() -> None:
    assessment = _assessment(
        [
            _claim(
                "claim-001",
                "factor-a",
                "factor-b",
                include_support=False,
            )
        ]
    )

    packet = _packet(assessment)

    assert (
        "REVIEW_MISSING_SUPPORTING_EVIDENCE"
        in packet["required_operator_actions"]
    )


def test_blocked_source_claim_creates_critical_packet() -> None:
    assessment = _assessment(
        [
            _claim(
                "claim-001",
                "factor-a",
                "factor-b",
                support_status="BLOCKED",
            )
        ]
    )

    packet = _packet(assessment)

    assert packet["packet_status"] == "BLOCKED"
    assert packet["review_priority"] == "CRITICAL"
    assert (
        "RESOLVE_BLOCKED_SOURCE_CLAIMS"
        in packet["required_operator_actions"]
    )


def test_truth_probability_and_winner_remain_unassigned() -> None:
    packet = _packet()

    assert packet["causal_truth_status"] == (
        "UNDETERMINED"
    )
    assert packet["probability_status"] == (
        "NOT_ASSIGNED"
    )
    assert packet["winner_status"] == "NOT_SELECTED"


def test_runtime_and_model_execution_remain_forbidden() -> None:
    packet = _packet()

    assert packet["runtime_execution_status"] == (
        "NOT_ALLOWED"
    )
    assert packet[
        "live_model_invocation_status"
    ] == "NOT_ALLOWED"
    assert packet["prompt_execution_status"] == (
        "NOT_ALLOWED"
    )


def test_invalid_assessment_is_rejected() -> None:
    assessment = _assessment()
    assessment["causal_truth_status"] = "CONFIRMED"

    with pytest.raises(
        CausalReviewPacketViolation,
        match="causal_truth_status_invalid",
    ):
        _packet(assessment)


def test_validation_detects_severity_count_mutation() -> None:
    packet = _packet()
    packet["severity_counts"]["INFO"] += 1

    assert "severity_counts_mismatch" in (
        validate_causal_reasoning_review_packet(
            packet
        )
    )


def test_validation_detects_action_mutation() -> None:
    packet = _packet()
    packet["required_operator_actions"].append(
        "AUTO_APPROVE_CAUSAL_CHAIN"
    )
    packet["required_operator_actions"].sort()

    assert "required_operator_actions_mismatch" in (
        validate_causal_reasoning_review_packet(
            packet
        )
    )


def test_validation_rejects_causal_truth_assignment() -> None:
    packet = _packet()
    packet["causal_truth_status"] = "CONFIRMED"

    assert "causal_truth_status_invalid" in (
        validate_causal_reasoning_review_packet(
            packet
        )
    )


def test_builder_returns_fresh_containers() -> None:
    first = _packet()
    second = _packet()

    mutated = deepcopy(first)
    mutated["finding_records"][0]["severity"] = (
        "CRITICAL"
    )
    mutated["source_assessment"]["source_chain"][
        "node_ids"
    ].append("invented-node")
    mutated["safety_flags"][
        "real_execution_allowed"
    ] = True

    assert second == _packet()
    assert mutated != second


def test_non_mapping_review_packet_is_rejected() -> None:
    assert validate_causal_reasoning_review_packet(
        []
    ) == ["review_packet_must_be_mapping"]
