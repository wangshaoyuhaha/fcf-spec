"""Tests for FCF API Gateway planning D6."""

from copy import deepcopy

import pytest

from fcf.sidecars.fcf_api_gateway_planning import (
    FINAL_HANDOFF_STAGE_ID,
    FcfApiGatewayFinalHandoffViolation,
    build_fcf_api_gateway_boundary_contract,
    build_fcf_api_gateway_final_handoff,
    build_fcf_api_gateway_policy_gate_decision,
    build_fcf_api_gateway_request_envelope,
    build_fcf_api_gateway_response_envelope,
    build_fcf_api_gateway_review_packet,
    validate_fcf_api_gateway_final_handoff,
)


def _chain(
    request_class: str = "HEALTH_STATUS_READ",
) -> tuple[
    dict[str, object],
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
        source_artifact_ids=["artifact-001"],
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

    packet = build_fcf_api_gateway_review_packet(
        review_packet_id="review-packet-001",
        boundary_contract=boundary,
        request_envelope=request,
        policy_gate_decision=decision,
        response_envelope=response,
    )

    return boundary, request, decision, response, packet


def _handoff(
    request_class: str = "HEALTH_STATUS_READ",
) -> dict[str, object]:
    boundary, request, decision, response, packet = _chain(
        request_class
    )

    return build_fcf_api_gateway_final_handoff(
        handoff_id="handoff-001",
        review_packet=packet,
        boundary_contract=boundary,
        request_envelope=request,
        policy_gate_decision=decision,
        response_envelope=response,
    )


def test_valid_handoff_passes_validation() -> None:
    boundary, request, decision, response, packet = _chain()

    handoff = build_fcf_api_gateway_final_handoff(
        handoff_id="handoff-001",
        review_packet=packet,
        boundary_contract=boundary,
        request_envelope=request,
        policy_gate_decision=decision,
        response_envelope=response,
    )

    assert validate_fcf_api_gateway_final_handoff(
        handoff,
        packet,
        boundary,
        request,
        decision,
        response,
    ) == []


def test_stage_identity_is_locked() -> None:
    assert _handoff()["stage_id"] == FINAL_HANDOFF_STAGE_ID


def test_ready_chain_is_merge_review_eligible() -> None:
    handoff = _handoff("HEALTH_STATUS_READ")

    assert handoff["handoff_status"] == (
        "READY_FOR_OPERATOR_MERGE_REVIEW"
    )
    assert handoff["main_merge_review_eligible"] is True
    assert handoff["repair_required"] is False


def test_operator_control_chain_requires_confirmation() -> None:
    handoff = _handoff("OPERATOR_REVIEW_REQUEST")

    assert handoff["handoff_status"] == (
        "OPERATOR_CONFIRMATION_REQUIRED_BEFORE_MERGE_REVIEW"
    )
    assert handoff["main_merge_review_eligible"] is False
    assert handoff["repair_required"] is False


def test_blocked_chain_requires_repair() -> None:
    handoff = _handoff("ORDER_PLACEMENT")

    assert handoff["handoff_status"] == (
        "BLOCKED_REPAIR_REQUIRED"
    )
    assert handoff["main_merge_review_eligible"] is False
    assert handoff["repair_required"] is True


def test_traceability_is_preserved() -> None:
    handoff = _handoff()

    assert handoff["source_review_packet_id"] == (
        "review-packet-001"
    )
    assert handoff["correlation_id"] == "correlation-001"
    assert handoff["branch_name"] == (
        "sidecar-fcf-api-gateway-planning-app-1"
    )


def test_operator_action_is_required() -> None:
    handoff = _handoff()

    assert handoff["operator_action_required"] is True
    assert handoff["operator_decision_status"] == "PENDING"
    assert (
        "APPROVE_MAIN_MERGE_REVIEW"
        in handoff["allowed_operator_actions"]
    )


def test_runtime_and_release_capabilities_are_disabled() -> None:
    handoff = _handoff()

    for field in (
        "main_merge_allowed_without_operator_confirmation",
        "http_server_active",
        "port_listener_active",
        "response_transport_active",
        "model_invocation_allowed",
        "prompt_execution_allowed",
        "automatic_routing_allowed",
        "runtime_activation_allowed",
        "archive_writing_allowed",
        "real_execution_allowed",
        "tag_allowed",
        "release_allowed",
        "deploy_allowed",
    ):
        assert handoff[field] is False


def test_builder_rejects_invalid_handoff_id() -> None:
    boundary, request, decision, response, packet = _chain()

    with pytest.raises(FcfApiGatewayFinalHandoffViolation):
        build_fcf_api_gateway_final_handoff(
            handoff_id="invalid handoff",
            review_packet=packet,
            boundary_contract=boundary,
            request_envelope=request,
            policy_gate_decision=decision,
            response_envelope=response,
        )


def test_builder_rejects_empty_branch_name() -> None:
    boundary, request, decision, response, packet = _chain()

    with pytest.raises(FcfApiGatewayFinalHandoffViolation):
        build_fcf_api_gateway_final_handoff(
            handoff_id="handoff-001",
            review_packet=packet,
            boundary_contract=boundary,
            request_envelope=request,
            policy_gate_decision=decision,
            response_envelope=response,
            branch_name="",
        )


def test_builder_rejects_tampered_review_packet() -> None:
    boundary, request, decision, response, packet = _chain()
    packet["real_execution_allowed"] = True

    with pytest.raises(FcfApiGatewayFinalHandoffViolation):
        build_fcf_api_gateway_final_handoff(
            handoff_id="handoff-001",
            review_packet=packet,
            boundary_contract=boundary,
            request_envelope=request,
            policy_gate_decision=decision,
            response_envelope=response,
        )


def test_validation_rejects_merge_without_operator() -> None:
    boundary, request, decision, response, packet = _chain()
    handoff = build_fcf_api_gateway_final_handoff(
        handoff_id="handoff-001",
        review_packet=packet,
        boundary_contract=boundary,
        request_envelope=request,
        policy_gate_decision=decision,
        response_envelope=response,
    )
    handoff[
        "main_merge_allowed_without_operator_confirmation"
    ] = True

    errors = validate_fcf_api_gateway_final_handoff(
        handoff,
        packet,
        boundary,
        request,
        decision,
        response,
    )

    assert (
        "main_merge_allowed_without_operator_confirmation_mismatch"
        in errors
    )
    assert (
        "main_merge_allowed_without_operator_confirmation_must_be_false"
        in errors
    )


def test_validation_rejects_deploy_enablement() -> None:
    boundary, request, decision, response, packet = _chain()
    handoff = build_fcf_api_gateway_final_handoff(
        handoff_id="handoff-001",
        review_packet=packet,
        boundary_contract=boundary,
        request_envelope=request,
        policy_gate_decision=decision,
        response_envelope=response,
    )
    handoff["deploy_allowed"] = True

    errors = validate_fcf_api_gateway_final_handoff(
        handoff,
        packet,
        boundary,
        request,
        decision,
        response,
    )

    assert "deploy_allowed_mismatch" in errors
    assert "deploy_allowed_must_be_false" in errors


def test_builder_returns_fresh_action_list() -> None:
    first = _handoff()
    second = _handoff()
    mutated = deepcopy(first)

    mutated["allowed_operator_actions"].append(
        "AUTOMATIC_MERGE"
    )

    assert second == _handoff()
    assert mutated != second


def test_non_mapping_handoff_is_rejected() -> None:
    boundary, request, decision, response, packet = _chain()

    assert validate_fcf_api_gateway_final_handoff(
        [],
        packet,
        boundary,
        request,
        decision,
        response,
    ) == ["handoff_must_be_mapping"]
