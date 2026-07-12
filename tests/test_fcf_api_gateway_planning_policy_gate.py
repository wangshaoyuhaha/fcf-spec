"""Tests for FCF API Gateway planning D3."""

from copy import deepcopy

import pytest

from fcf.sidecars.fcf_api_gateway_planning import (
    POLICY_GATE_STAGE_ID,
    FcfApiGatewayPolicyGateViolation,
    build_fcf_api_gateway_boundary_contract,
    build_fcf_api_gateway_policy_gate_decision,
    build_fcf_api_gateway_request_envelope,
    validate_fcf_api_gateway_policy_gate_decision,
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
        source_artifact_ids=["artifact-001"],
        operator_action="REQUEST",
    )


def _decision(
    request_class: str = "HEALTH_STATUS_READ",
) -> dict[str, object]:
    return build_fcf_api_gateway_policy_gate_decision(
        decision_id="decision-001",
        request_envelope=_request(request_class),
    )


def test_valid_policy_gate_passes_validation() -> None:
    request = _request()
    decision = build_fcf_api_gateway_policy_gate_decision(
        decision_id="decision-001",
        request_envelope=request,
    )

    assert validate_fcf_api_gateway_policy_gate_decision(
        decision,
        request,
    ) == []


def test_stage_identity_is_locked() -> None:
    assert _decision()["stage_id"] == POLICY_GATE_STAGE_ID


def test_read_only_request_is_ready() -> None:
    decision = _decision("HEALTH_STATUS_READ")

    assert decision["policy_gate_status"] == (
        "READY_FOR_READ_ONLY_RESPONSE"
    )
    assert decision[
        "operator_confirmation_required"
    ] is False


def test_operator_review_request_requires_confirmation() -> None:
    decision = _decision("OPERATOR_REVIEW_REQUEST")

    assert decision["policy_gate_status"] == (
        "OPERATOR_CONFIRMATION_REQUIRED"
    )
    assert decision[
        "operator_confirmation_required"
    ] is True


def test_reanalysis_request_requires_confirmation() -> None:
    decision = _decision("REANALYSIS_REQUEST")

    assert decision["policy_gate_status"] == (
        "OPERATOR_CONFIRMATION_REQUIRED"
    )


def test_stop_request_requires_confirmation() -> None:
    decision = _decision("STOP_WORKFLOW_REQUEST")

    assert decision["policy_gate_status"] == (
        "OPERATOR_CONFIRMATION_REQUIRED"
    )


def test_prohibited_request_remains_blocked() -> None:
    decision = _decision("ORDER_PLACEMENT")

    assert decision["policy_gate_status"] == "BLOCKED"
    assert decision["blocking_reasons"] == [
        "prohibited_request_class"
    ]


def test_unknown_request_remains_blocked() -> None:
    decision = _decision("UNKNOWN_REQUEST")

    assert decision["policy_gate_status"] == "BLOCKED"
    assert decision["blocking_reasons"] == [
        "request_class_unregistered"
    ]


def test_traceability_fields_are_preserved() -> None:
    decision = _decision()

    assert decision["source_request_id"] == "request-001"
    assert decision["correlation_id"] == "correlation-001"
    assert decision["policy_version"] == "policy.v1"
    assert decision["config_snapshot_id"] == (
        "config.snapshot.001"
    )


def test_runtime_and_routing_remain_disabled() -> None:
    decision = _decision()

    assert decision["automatic_routing_allowed"] is False
    assert decision["runtime_activation_allowed"] is False


def test_builder_rejects_invalid_decision_id() -> None:
    with pytest.raises(FcfApiGatewayPolicyGateViolation):
        build_fcf_api_gateway_policy_gate_decision(
            decision_id="invalid decision",
            request_envelope=_request(),
        )


def test_builder_rejects_tampered_request() -> None:
    request = _request()
    request["request_status"] = "BLOCKED"

    with pytest.raises(FcfApiGatewayPolicyGateViolation):
        build_fcf_api_gateway_policy_gate_decision(
            decision_id="decision-001",
            request_envelope=request,
        )


def test_validation_rejects_gate_status_tampering() -> None:
    request = _request()
    decision = build_fcf_api_gateway_policy_gate_decision(
        decision_id="decision-001",
        request_envelope=request,
    )
    decision["policy_gate_status"] = "BLOCKED"

    assert "policy_gate_status_mismatch" in (
        validate_fcf_api_gateway_policy_gate_decision(
            decision,
            request,
        )
    )


def test_validation_rejects_routing_enablement() -> None:
    request = _request()
    decision = build_fcf_api_gateway_policy_gate_decision(
        decision_id="decision-001",
        request_envelope=request,
    )
    decision["automatic_routing_allowed"] = True

    assert "automatic_routing_allowed_must_be_false" in (
        validate_fcf_api_gateway_policy_gate_decision(
            decision,
            request,
        )
    )


def test_builder_returns_fresh_containers() -> None:
    first = _decision("ORDER_PLACEMENT")
    second = _decision("ORDER_PLACEMENT")
    mutated = deepcopy(first)

    mutated["blocking_reasons"].append("tampered")

    assert second == _decision("ORDER_PLACEMENT")
    assert mutated != second


def test_non_mapping_decision_is_rejected() -> None:
    assert validate_fcf_api_gateway_policy_gate_decision(
        [],
        _request(),
    ) == ["decision_must_be_mapping"]
