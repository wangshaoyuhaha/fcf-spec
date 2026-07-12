"""Tests for FCF API Gateway planning D2."""

from copy import deepcopy

import pytest

from fcf.sidecars.fcf_api_gateway_planning import (
    APP_ID,
    PLANNING_MODE,
    REQUEST_ENVELOPE_STAGE_ID,
    FcfApiGatewayRequestEnvelopeViolation,
    build_fcf_api_gateway_boundary_contract,
    build_fcf_api_gateway_request_envelope,
    validate_fcf_api_gateway_request_envelope,
)


def _boundary() -> dict[str, object]:
    return build_fcf_api_gateway_boundary_contract()


def _request(
    *,
    request_class: str = "HEALTH_STATUS_READ",
) -> dict[str, object]:
    return build_fcf_api_gateway_request_envelope(
        boundary_contract=_boundary(),
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


def test_valid_request_envelope_passes_validation() -> None:
    assert validate_fcf_api_gateway_request_envelope(
        _request()
    ) == []


def test_identity_is_locked() -> None:
    request = _request()

    assert request["app_id"] == APP_ID
    assert request["stage_id"] == REQUEST_ENVELOPE_STAGE_ID
    assert request["planning_mode"] == PLANNING_MODE


def test_allowed_request_is_validated() -> None:
    request = _request(
        request_class="HEALTH_STATUS_READ"
    )

    assert request["request_status"] == "VALIDATED"
    assert request["blocking_reasons"] == []


def test_prohibited_request_is_blocked() -> None:
    request = _request(
        request_class="ORDER_PLACEMENT"
    )

    assert request["request_status"] == "BLOCKED"
    assert request["blocking_reasons"] == [
        "prohibited_request_class"
    ]


def test_unknown_request_is_blocked() -> None:
    request = _request(
        request_class="UNREGISTERED_REQUEST"
    )

    assert request["request_status"] == "BLOCKED"
    assert request["blocking_reasons"] == [
        "request_class_unregistered"
    ]


def test_metadata_links_contract_policy_and_config() -> None:
    request = _request()

    assert request["source_contract_id"] == (
        _boundary()["contract_id"]
    )
    assert request["policy_version"] == "policy.v1"
    assert request["config_snapshot_id"] == (
        "config.snapshot.001"
    )


def test_source_artifact_ids_are_canonical() -> None:
    assert _request()["source_artifact_ids"] == [
        "artifact-001",
        "artifact-002",
    ]


def test_safety_flags_keep_request_planning_only() -> None:
    flags = _request()["safety_flags"]

    assert flags["planning_only"] is True
    assert flags["read_only"] is True
    assert flags["http_server_active"] is False
    assert flags["real_execution_allowed"] is False


def test_builder_rejects_invalid_boundary() -> None:
    boundary = _boundary()
    boundary["safety_flags"]["http_server_active"] = True

    with pytest.raises(
        FcfApiGatewayRequestEnvelopeViolation
    ):
        build_fcf_api_gateway_request_envelope(
            boundary_contract=boundary,
            request_id="request-001",
            request_class="HEALTH_STATUS_READ",
            requested_at_utc="2026-07-13T12:00:00Z",
            correlation_id="correlation-001",
            policy_version="policy.v1",
            config_snapshot_id="config.snapshot.001",
            source_artifact_ids=[],
            operator_action="REQUEST",
        )


def test_builder_rejects_naive_timestamp() -> None:
    with pytest.raises(
        FcfApiGatewayRequestEnvelopeViolation
    ):
        build_fcf_api_gateway_request_envelope(
            boundary_contract=_boundary(),
            request_id="request-001",
            request_class="HEALTH_STATUS_READ",
            requested_at_utc="2026-07-13T12:00:00",
            correlation_id="correlation-001",
            policy_version="policy.v1",
            config_snapshot_id="config.snapshot.001",
            source_artifact_ids=[],
            operator_action="REQUEST",
        )


def test_builder_rejects_duplicate_artifact_ids() -> None:
    with pytest.raises(
        FcfApiGatewayRequestEnvelopeViolation
    ):
        build_fcf_api_gateway_request_envelope(
            boundary_contract=_boundary(),
            request_id="request-001",
            request_class="HEALTH_STATUS_READ",
            requested_at_utc="2026-07-13T12:00:00Z",
            correlation_id="correlation-001",
            policy_version="policy.v1",
            config_snapshot_id="config.snapshot.001",
            source_artifact_ids=[
                "artifact-001",
                "artifact-001",
            ],
            operator_action="REQUEST",
        )


def test_builder_rejects_invalid_operator_action() -> None:
    with pytest.raises(
        FcfApiGatewayRequestEnvelopeViolation
    ):
        build_fcf_api_gateway_request_envelope(
            boundary_contract=_boundary(),
            request_id="request-001",
            request_class="HEALTH_STATUS_READ",
            requested_at_utc="2026-07-13T12:00:00Z",
            correlation_id="correlation-001",
            policy_version="policy.v1",
            config_snapshot_id="config.snapshot.001",
            source_artifact_ids=[],
            operator_action="invalid action",
        )


def test_validation_rejects_status_tampering() -> None:
    request = _request()
    request["request_status"] = "BLOCKED"

    assert "request_status_invalid" in (
        validate_fcf_api_gateway_request_envelope(
            request
        )
    )


def test_validation_rejects_request_class_tampering() -> None:
    request = _request()
    request["request_class"] = "ORDER_PLACEMENT"

    errors = validate_fcf_api_gateway_request_envelope(
        request
    )

    assert "request_status_invalid" in errors
    assert "blocking_reasons_invalid" in errors


def test_builder_returns_fresh_nested_containers() -> None:
    first = _request()
    second = _request()
    mutated = deepcopy(first)

    mutated["safety_flags"]["http_server_active"] = True
    mutated["source_artifact_ids"].append(
        "artifact-003"
    )

    assert second == _request()
    assert mutated != second


def test_non_mapping_request_is_rejected() -> None:
    assert validate_fcf_api_gateway_request_envelope(
        []
    ) == ["request_envelope_must_be_mapping"]
