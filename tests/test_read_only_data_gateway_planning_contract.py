"""Tests for Read-Only Data Gateway planning D1."""

from copy import deepcopy

import pytest

from fcf.sidecars.read_only_data_gateway_planning import (
    ALLOWED_OPERATIONS,
    APP_ID,
    PLANNING_MODE,
    PROHIBITED_OPERATIONS,
    REQUIRED_METADATA_FIELDS,
    STAGE_ID,
    ReadOnlyGatewayBoundaryViolation,
    build_read_only_data_gateway_boundary_contract,
    validate_read_only_data_gateway_boundary_contract,
)


def _contract() -> dict[str, object]:
    return build_read_only_data_gateway_boundary_contract()


def test_valid_contract_passes_validation() -> None:
    assert validate_read_only_data_gateway_boundary_contract(
        _contract()
    ) == []


def test_identity_is_locked() -> None:
    contract = _contract()

    assert contract["app_id"] == APP_ID
    assert contract["stage_id"] == STAGE_ID
    assert contract["planning_mode"] == PLANNING_MODE


def test_allowed_operations_are_read_only() -> None:
    assert "DATABASE_SELECT" in ALLOWED_OPERATIONS
    assert "FILE_UPLOAD" in ALLOWED_OPERATIONS
    assert "DATABASE_INSERT" not in ALLOWED_OPERATIONS


def test_prohibited_operations_block_writes_and_trading() -> None:
    assert "DATABASE_INSERT" in PROHIBITED_OPERATIONS
    assert "DATABASE_UPDATE" in PROHIBITED_OPERATIONS
    assert "DATABASE_DELETE" in PROHIBITED_OPERATIONS
    assert "ORDER_PLACEMENT" in PROHIBITED_OPERATIONS


def test_required_metadata_covers_evidence_governance() -> None:
    for field in (
        "source_id",
        "source_class",
        "trust_level",
        "evidence_id",
        "checksum",
        "freshness_status",
        "license_type",
        "cloud_processing_allowed",
    ):
        assert field in REQUIRED_METADATA_FIELDS


def test_unknown_license_defaults_fail_closed() -> None:
    defaults = _contract()["unknown_license_default"]

    assert defaults["cloud_processing_allowed"] is False
    assert defaults["training_allowed"] is False
    assert defaults["redistribution_allowed"] is False
    assert defaults["operator_review_required"] is True


def test_unknown_freshness_is_not_treated_as_fresh() -> None:
    defaults = _contract()["unknown_freshness_default"]

    assert defaults["classification"] == "UNKNOWN"
    assert defaults["workflow_effect"] == (
        "DEGRADED_OR_BLOCKED_BY_POLICY"
    )


def test_safety_flags_preserve_gateway_boundary() -> None:
    flags = _contract()["safety_flags"]

    assert flags["read_only"] is True
    assert flags["credential_isolation_required"] is True
    assert flags["database_write_allowed"] is False
    assert flags["trading_api_allowed"] is False
    assert flags["real_execution_allowed"] is False


def test_validation_rejects_database_write_enablement() -> None:
    contract = _contract()
    contract["safety_flags"]["database_write_allowed"] = True

    assert "database_write_allowed_must_be_false" in (
        validate_read_only_data_gateway_boundary_contract(
            contract
        )
    )


def test_validation_rejects_model_invocation_enablement() -> None:
    contract = _contract()
    contract["safety_flags"]["model_invocation_allowed"] = True

    assert "model_invocation_allowed_must_be_false" in (
        validate_read_only_data_gateway_boundary_contract(
            contract
        )
    )


def test_validation_rejects_missing_metadata_requirement() -> None:
    contract = _contract()
    contract["required_metadata_fields"].remove("checksum")

    assert "required_metadata_fields_invalid" in (
        validate_read_only_data_gateway_boundary_contract(
            contract
        )
    )


def test_validation_rejects_prohibited_operation_tampering() -> None:
    contract = _contract()
    contract["prohibited_operations"].remove(
        "ORDER_PLACEMENT"
    )

    assert "prohibited_operations_invalid" in (
        validate_read_only_data_gateway_boundary_contract(
            contract
        )
    )


def test_builder_rejects_invalid_contract_id() -> None:
    with pytest.raises(ReadOnlyGatewayBoundaryViolation):
        build_read_only_data_gateway_boundary_contract(
            contract_id="invalid contract id"
        )


def test_builder_returns_fresh_nested_containers() -> None:
    first = _contract()
    second = _contract()
    mutated = deepcopy(first)

    mutated["safety_flags"]["database_write_allowed"] = True
    mutated["allowed_operations"].append("DATABASE_INSERT")

    assert second == _contract()
    assert mutated != second


def test_non_mapping_contract_is_rejected() -> None:
    assert validate_read_only_data_gateway_boundary_contract(
        []
    ) == ["contract_must_be_mapping"]
