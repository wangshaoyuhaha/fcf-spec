"""Tests for FCF API Gateway planning D4."""

from copy import deepcopy

import pytest

from fcf.sidecars.fcf_api_gateway_planning import (
    RESPONSE_ENVELOPE_STAGE_ID,
    FcfApiGatewayResponseEnvelopeViolation,
    build_fcf_api_gateway_boundary_contract,
    build_fcf_api_gateway_policy_gate_decision,
    build_fcf_api_gateway_request_envelope,
    build_fcf_api_gateway_response_envelope,
    validate_fcf_api_gateway_response_envelope,
)


def _request(
    request_class: str = "HEALTH_STATUS_READ",
) -> dict[str, object]:
    return build_fcf_api_gateway_request_envelope(
        boundary_contract=(
            build_fcf_api_gateway_boundary_contract()
        ),
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


def _decision(
    request: dict[str, object],
) -> dict[str, object]:
    return build_fcf_api_gateway_policy_gate_decision(
        decision_id="decision-001",
        request_envelope=request,
    )


def _response(
    request_class: str = "HEALTH_STATUS_READ",
) -> dict[str, object]:
    request = _request(request_class)
    decision = _decision(request)

    return build_fcf_api_gateway_response_envelope(
        response_id="response-001",
        request_envelope=request,
        policy_gate_decision=decision,
        generated_at_utc="2026-07-13T12:01:00Z",
    )


def test_valid_response_passes_validation() -> None:
    request = _request()
    decision = _decision(request)
    response = build_fcf_api_gateway_response_envelope(
        response_id="response-001",
        request_envelope=request,
        policy_gate_decision=decision,
        generated_at_utc="2026-07-13T12:01:00Z",
    )

    assert validate_fcf_api_gateway_response_envelope(
        response,
        request,
        decision,
    ) == []


def test_stage_identity_is_locked() -> None:
    assert _response()["stage_id"] == (
        RESPONSE_ENVELOPE_STAGE_ID
    )


def test_read_only_response_is_planned() -> None:
    response = _response("HEALTH_STATUS_READ")

    assert response["status"] == (
        "READ_ONLY_RESPONSE_PLANNED"
    )
    assert response["errors"] == []
    assert response["warnings"] == []


def test_operator_request_remains_pending() -> None:
    response = _response("OPERATOR_REVIEW_REQUEST")

    assert response["status"] == (
        "OPERATOR_CONFIRMATION_PENDING"
    )
    assert response["warnings"] == [
        "operator_confirmation_required"
    ]
    assert response[
        "operator_confirmation_required"
    ] is True


def test_blocked_request_propagates_errors() -> None:
    response = _response("ORDER_PLACEMENT")

    assert response["status"] == "BLOCKED"
    assert response["errors"] == [
        "prohibited_request_class"
    ]


def test_traceability_is_preserved() -> None:
    response = _response()

    assert response["source_request_id"] == "request-001"
    assert response["correlation_id"] == "correlation-001"
    assert response["source_artifact_ids"] == [
        "artifact-001",
        "artifact-002",
    ]


def test_runtime_capabilities_remain_disabled() -> None:
    response = _response()

    assert response["operator_review_required"] is True
    assert response["response_transport_active"] is False
    assert response["automatic_routing_allowed"] is False
    assert response["runtime_activation_allowed"] is False
    assert response["model_invocation_allowed"] is False
    assert response["archive_writing_allowed"] is False


def test_builder_rejects_invalid_response_id() -> None:
    request = _request()
    decision = _decision(request)

    with pytest.raises(
        FcfApiGatewayResponseEnvelopeViolation
    ):
        build_fcf_api_gateway_response_envelope(
            response_id="invalid response",
            request_envelope=request,
            policy_gate_decision=decision,
            generated_at_utc="2026-07-13T12:01:00Z",
        )


def test_builder_rejects_naive_timestamp() -> None:
    request = _request()
    decision = _decision(request)

    with pytest.raises(
        FcfApiGatewayResponseEnvelopeViolation
    ):
        build_fcf_api_gateway_response_envelope(
            response_id="response-001",
            request_envelope=request,
            policy_gate_decision=decision,
            generated_at_utc="2026-07-13T12:01:00",
        )


def test_builder_rejects_tampered_request() -> None:
    request = _request()
    request["request_status"] = "BLOCKED"
    decision = _decision(_request())

    with pytest.raises(
        FcfApiGatewayResponseEnvelopeViolation
    ):
        build_fcf_api_gateway_response_envelope(
            response_id="response-001",
            request_envelope=request,
            policy_gate_decision=decision,
            generated_at_utc="2026-07-13T12:01:00Z",
        )


def test_builder_rejects_tampered_policy_gate() -> None:
    request = _request()
    decision = _decision(request)
    decision["automatic_routing_allowed"] = True

    with pytest.raises(
        FcfApiGatewayResponseEnvelopeViolation
    ):
        build_fcf_api_gateway_response_envelope(
            response_id="response-001",
            request_envelope=request,
            policy_gate_decision=decision,
            generated_at_utc="2026-07-13T12:01:00Z",
        )


def test_validation_rejects_status_tampering() -> None:
    request = _request()
    decision = _decision(request)
    response = build_fcf_api_gateway_response_envelope(
        response_id="response-001",
        request_envelope=request,
        policy_gate_decision=decision,
        generated_at_utc="2026-07-13T12:01:00Z",
    )
    response["status"] = "BLOCKED"

    assert "status_mismatch" in (
        validate_fcf_api_gateway_response_envelope(
            response,
            request,
            decision,
        )
    )


def test_validation_rejects_transport_enablement() -> None:
    request = _request()
    decision = _decision(request)
    response = build_fcf_api_gateway_response_envelope(
        response_id="response-001",
        request_envelope=request,
        policy_gate_decision=decision,
        generated_at_utc="2026-07-13T12:01:00Z",
    )
    response["response_transport_active"] = True

    errors = validate_fcf_api_gateway_response_envelope(
        response,
        request,
        decision,
    )

    assert "response_transport_active_mismatch" in errors
    assert (
        "response_transport_active_must_be_false"
        in errors
    )


def test_builder_returns_fresh_containers() -> None:
    first = _response("ORDER_PLACEMENT")
    second = _response("ORDER_PLACEMENT")
    mutated = deepcopy(first)

    mutated["errors"].append("tampered")
    mutated["source_artifact_ids"].append(
        "artifact-003"
    )

    assert second == _response("ORDER_PLACEMENT")
    assert mutated != second


def test_non_mapping_response_is_rejected() -> None:
    request = _request()
    decision = _decision(request)

    assert validate_fcf_api_gateway_response_envelope(
        [],
        request,
        decision,
    ) == ["response_envelope_must_be_mapping"]
