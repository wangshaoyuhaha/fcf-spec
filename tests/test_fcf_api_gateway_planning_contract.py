"""Tests for FCF API Gateway planning D1."""

from copy import deepcopy

import pytest

from fcf.sidecars.fcf_api_gateway_planning import (
    ALLOWED_REQUEST_CLASSES,
    APP_ID,
    ARCHITECTURE_PATH,
    AUTHORITY_HIERARCHY,
    PLANNING_MODE,
    PROHIBITED_REQUEST_CLASSES,
    REQUIRED_REQUEST_METADATA,
    REQUIRED_RESPONSE_METADATA,
    STAGE_ID,
    FcfApiGatewayBoundaryViolation,
    build_fcf_api_gateway_boundary_contract,
    validate_fcf_api_gateway_boundary_contract,
)


def _contract() -> dict[str, object]:
    return build_fcf_api_gateway_boundary_contract()


def test_valid_contract_passes_validation() -> None:
    assert validate_fcf_api_gateway_boundary_contract(
        _contract()
    ) == []


def test_identity_is_locked() -> None:
    contract = _contract()

    assert contract["app_id"] == APP_ID
    assert contract["stage_id"] == STAGE_ID
    assert contract["planning_mode"] == PLANNING_MODE


def test_architecture_path_preserves_sidecar_boundary() -> None:
    assert ARCHITECTURE_PATH == (
        "FCF_WEB_CONSOLE",
        "WORKFLOW_ORCHESTRATION_LAYER",
        "FCF_API_GATEWAY",
        "SIDECAR_APPLICATION_SERVICES",
        "FROZEN_DETERMINISTIC_CORE",
    )


def test_authority_hierarchy_preserves_deterministic_control() -> None:
    assert AUTHORITY_HIERARCHY[0] == "OPERATOR_POLICY"
    assert "DETERMINISTIC_ENGINE" in AUTHORITY_HIERARCHY
    assert AUTHORITY_HIERARCHY.index(
        "DETERMINISTIC_ENGINE"
    ) < AUTHORITY_HIERARCHY.index("AI_MODELS")


def test_allowed_requests_do_not_include_execution() -> None:
    assert "HEALTH_STATUS_READ" in ALLOWED_REQUEST_CLASSES
    assert "OPERATOR_REVIEW_REQUEST" in ALLOWED_REQUEST_CLASSES
    assert "ORDER_PLACEMENT" not in ALLOWED_REQUEST_CLASSES


def test_prohibited_requests_block_trading_and_writes() -> None:
    for request_class in (
        "DATABASE_WRITE",
        "ORDER_CANCELLATION",
        "ORDER_PLACEMENT",
        "REAL_EXECUTION",
        "TRADING_API_ACCESS",
    ):
        assert request_class in PROHIBITED_REQUEST_CLASSES


def test_request_metadata_is_traceable_and_policy_linked() -> None:
    for field in (
        "config_snapshot_id",
        "correlation_id",
        "policy_version",
        "request_id",
        "source_artifact_ids",
    ):
        assert field in REQUIRED_REQUEST_METADATA


def test_response_metadata_preserves_review_and_policy() -> None:
    for field in (
        "correlation_id",
        "operator_review_required",
        "policy_decision",
        "request_id",
        "status",
    ):
        assert field in REQUIRED_RESPONSE_METADATA


def test_safety_flags_keep_gateway_planning_only() -> None:
    flags = _contract()["safety_flags"]

    assert flags["planning_only"] is True
    assert flags["read_only"] is True
    assert flags["sidecar_only"] is True
    assert flags["http_server_active"] is False
    assert flags["port_listener_allowed"] is False
    assert flags["real_execution_allowed"] is False


def test_validation_rejects_http_server_activation() -> None:
    contract = _contract()
    contract["safety_flags"]["http_server_active"] = True

    assert "http_server_active_must_be_false" in (
        validate_fcf_api_gateway_boundary_contract(
            contract
        )
    )


def test_validation_rejects_model_invocation() -> None:
    contract = _contract()
    contract["safety_flags"]["model_invocation_allowed"] = True

    assert "model_invocation_allowed_must_be_false" in (
        validate_fcf_api_gateway_boundary_contract(
            contract
        )
    )


def test_validation_rejects_prohibited_request_tampering() -> None:
    contract = _contract()
    contract["prohibited_request_classes"].remove(
        "ORDER_PLACEMENT"
    )

    assert "prohibited_request_classes_invalid" in (
        validate_fcf_api_gateway_boundary_contract(
            contract
        )
    )


def test_builder_rejects_invalid_contract_id() -> None:
    with pytest.raises(FcfApiGatewayBoundaryViolation):
        build_fcf_api_gateway_boundary_contract(
            contract_id="invalid contract id"
        )


def test_builder_returns_fresh_nested_containers() -> None:
    first = _contract()
    second = _contract()
    mutated = deepcopy(first)

    mutated["safety_flags"]["http_server_active"] = True
    mutated["allowed_request_classes"].append(
        "ORDER_PLACEMENT"
    )

    assert second == _contract()
    assert mutated != second


def test_non_mapping_contract_is_rejected() -> None:
    assert validate_fcf_api_gateway_boundary_contract(
        []
    ) == ["contract_must_be_mapping"]
