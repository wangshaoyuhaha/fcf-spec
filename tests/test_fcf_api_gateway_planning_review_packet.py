"""Tests for FCF API Gateway planning D5."""

from copy import deepcopy

import pytest

from fcf.sidecars.fcf_api_gateway_planning import (
    REVIEW_PACKET_STAGE_ID,
    FcfApiGatewayReviewPacketViolation,
    build_fcf_api_gateway_boundary_contract,
    build_fcf_api_gateway_policy_gate_decision,
    build_fcf_api_gateway_request_envelope,
    build_fcf_api_gateway_response_envelope,
    build_fcf_api_gateway_review_packet,
    validate_fcf_api_gateway_review_packet,
)


def _chain(
    request_class: str = "HEALTH_STATUS_READ",
) -> tuple[
    dict[str, object],
    dict[str, object],
    dict[str, object],
    dict[str, object],
]:
    boundary = build_fcf_api_gateway_boundary_contract()

    request = build_fcf_api_gateway_request_envelope(
        boundary_contract=boundary,
        request_id="request-001",
        request_class=request_class,
        requested_at_utc="2026-07-13T12:00:00Z",
        correlation_id="correlation-001",
        policy_version="policy.v1",
        config_snapshot_id="config.snapshot.001",
        source_artifact_ids=[
            "artifact-002",
            "artifact-001",
        ],
        operator_action="REQUEST",
    )

    decision = build_fcf_api_gateway_policy_gate_decision(
        decision_id="decision-001",
        request_envelope=request,
    )

    response = build_fcf_api_gateway_response_envelope(
        response_id="response-001",
        request_envelope=request,
        policy_gate_decision=decision,
        generated_at_utc="2026-07-13T12:01:00Z",
    )

    return boundary, request, decision, response


def _packet(
    request_class: str = "HEALTH_STATUS_READ",
) -> dict[str, object]:
    boundary, request, decision, response = _chain(
        request_class
    )

    return build_fcf_api_gateway_review_packet(
        review_packet_id="review-packet-001",
        boundary_contract=boundary,
        request_envelope=request,
        policy_gate_decision=decision,
        response_envelope=response,
    )


def test_valid_review_packet_passes_validation() -> None:
    boundary, request, decision, response = _chain()
    packet = build_fcf_api_gateway_review_packet(
        review_packet_id="review-packet-001",
        boundary_contract=boundary,
        request_envelope=request,
        policy_gate_decision=decision,
        response_envelope=response,
    )

    assert validate_fcf_api_gateway_review_packet(
        packet,
        boundary,
        request,
        decision,
        response,
    ) == []


def test_stage_identity_is_locked() -> None:
    assert _packet()["stage_id"] == REVIEW_PACKET_STAGE_ID


def test_read_only_chain_is_ready_for_review() -> None:
    packet = _packet("HEALTH_STATUS_READ")

    assert packet["overall_status"] == (
        "READY_FOR_OPERATOR_REVIEW"
    )
    assert packet["blocking_reasons"] == []
    assert packet["warnings"] == []


def test_operator_control_chain_requires_confirmation() -> None:
    packet = _packet("OPERATOR_REVIEW_REQUEST")

    assert packet["overall_status"] == (
        "OPERATOR_CONFIRMATION_REQUIRED"
    )
    assert packet["warnings"] == [
        "operator_confirmation_required"
    ]


def test_blocked_chain_remains_blocked() -> None:
    packet = _packet("ORDER_PLACEMENT")

    assert packet["overall_status"] == "BLOCKED"
    assert packet["blocking_reasons"] == [
        "prohibited_request_class"
    ]


def test_traceability_is_preserved() -> None:
    packet = _packet()

    assert packet["source_request_id"] == "request-001"
    assert packet["source_policy_decision_id"] == (
        "decision-001"
    )
    assert packet["source_response_id"] == "response-001"
    assert packet["correlation_id"] == "correlation-001"
    assert packet["source_artifact_ids"] == [
        "artifact-001",
        "artifact-002",
    ]


def test_runtime_capabilities_remain_disabled() -> None:
    packet = _packet()

    assert packet["operator_review_status"] == (
        "REVIEW_REQUIRED"
    )
    assert packet["operator_decision_status"] == "PENDING"
    assert packet["response_transport_active"] is False
    assert packet["automatic_routing_allowed"] is False
    assert packet["runtime_activation_allowed"] is False
    assert packet["model_invocation_allowed"] is False
    assert packet["archive_writing_allowed"] is False
    assert packet["real_execution_allowed"] is False


def test_builder_rejects_invalid_packet_id() -> None:
    boundary, request, decision, response = _chain()

    with pytest.raises(FcfApiGatewayReviewPacketViolation):
        build_fcf_api_gateway_review_packet(
            review_packet_id="invalid packet",
            boundary_contract=boundary,
            request_envelope=request,
            policy_gate_decision=decision,
            response_envelope=response,
        )


def test_builder_rejects_contract_linkage_mismatch() -> None:
    boundary, request, decision, response = _chain()
    request["source_contract_id"] = "other.contract"

    with pytest.raises(FcfApiGatewayReviewPacketViolation):
        build_fcf_api_gateway_review_packet(
            review_packet_id="review-packet-001",
            boundary_contract=boundary,
            request_envelope=request,
            policy_gate_decision=decision,
            response_envelope=response,
        )


def test_builder_rejects_tampered_policy_gate() -> None:
    boundary, request, decision, response = _chain()
    decision["runtime_activation_allowed"] = True

    with pytest.raises(FcfApiGatewayReviewPacketViolation):
        build_fcf_api_gateway_review_packet(
            review_packet_id="review-packet-001",
            boundary_contract=boundary,
            request_envelope=request,
            policy_gate_decision=decision,
            response_envelope=response,
        )


def test_builder_rejects_tampered_response() -> None:
    boundary, request, decision, response = _chain()
    response["response_transport_active"] = True

    with pytest.raises(FcfApiGatewayReviewPacketViolation):
        build_fcf_api_gateway_review_packet(
            review_packet_id="review-packet-001",
            boundary_contract=boundary,
            request_envelope=request,
            policy_gate_decision=decision,
            response_envelope=response,
        )


def test_validation_rejects_overall_status_tampering() -> None:
    boundary, request, decision, response = _chain()
    packet = build_fcf_api_gateway_review_packet(
        review_packet_id="review-packet-001",
        boundary_contract=boundary,
        request_envelope=request,
        policy_gate_decision=decision,
        response_envelope=response,
    )
    packet["overall_status"] = "BLOCKED"

    assert "overall_status_mismatch" in (
        validate_fcf_api_gateway_review_packet(
            packet,
            boundary,
            request,
            decision,
            response,
        )
    )


def test_validation_rejects_execution_enablement() -> None:
    boundary, request, decision, response = _chain()
    packet = build_fcf_api_gateway_review_packet(
        review_packet_id="review-packet-001",
        boundary_contract=boundary,
        request_envelope=request,
        policy_gate_decision=decision,
        response_envelope=response,
    )
    packet["real_execution_allowed"] = True

    errors = validate_fcf_api_gateway_review_packet(
        packet,
        boundary,
        request,
        decision,
        response,
    )

    assert "real_execution_allowed_mismatch" in errors
    assert "real_execution_allowed_must_be_false" in errors


def test_builder_returns_fresh_containers() -> None:
    first = _packet("ORDER_PLACEMENT")
    second = _packet("ORDER_PLACEMENT")
    mutated = deepcopy(first)

    mutated["blocking_reasons"].append("tampered")
    mutated["source_artifact_ids"].append(
        "artifact-003"
    )

    assert second == _packet("ORDER_PLACEMENT")
    assert mutated != second


def test_non_mapping_packet_is_rejected() -> None:
    boundary, request, decision, response = _chain()

    assert validate_fcf_api_gateway_review_packet(
        [],
        boundary,
        request,
        decision,
        response,
    ) == ["review_packet_must_be_mapping"]
