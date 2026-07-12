"""Planning-only boundary contract for the Read-Only Data Gateway."""

import re
from collections.abc import Mapping
from typing import Any

APP_ID = "READ-ONLY-DATA-GATEWAY-PLANNING-APP-1"
STAGE_ID = "READ-ONLY-DATA-GATEWAY-PLANNING-D1"
CONTRACT_VERSION = "1.0.0"
PLANNING_MODE = "PLANNING_ONLY"

ALLOWED_OPERATIONS = (
    "APPROVED_ARCHIVE_LOOKUP",
    "APPROVED_EVIDENCE_LOOKUP",
    "APPROVED_MARKET_DATA_RETRIEVAL",
    "APPROVED_RESEARCH_RETRIEVAL",
    "DATABASE_SELECT",
    "FILE_UPLOAD",
    "PUBLIC_DATA_RETRIEVAL",
)

PROHIBITED_OPERATIONS = (
    "BALANCE_RETRIEVAL",
    "CREDENTIAL_EXPOSURE_TO_MODEL",
    "DATABASE_DELETE",
    "DATABASE_INSERT",
    "DATABASE_UPDATE",
    "MODEL_RAW_API_KEY_ACCESS",
    "ORDER_PLACEMENT",
    "POSITION_RETRIEVAL",
    "PRIVATE_KEY_ACCESS",
    "UNRESTRICTED_FILE_WRITING",
    "WALLET_ACCESS",
)

REQUIRED_METADATA_FIELDS = (
    "allowed_use",
    "checksum",
    "cloud_processing_allowed",
    "evidence_id",
    "freshness_status",
    "license_type",
    "published_at",
    "redistribution_allowed",
    "retention_period",
    "retrieved_at",
    "source_class",
    "source_id",
    "training_allowed",
    "trust_level",
)

BLOCKED_CONDITIONS = (
    "credential_detected",
    "prohibited_operation_requested",
    "required_metadata_missing",
    "source_license_blocks_use",
    "write_operation_requested",
)

DEGRADED_CONDITIONS = (
    "freshness_unknown",
    "license_unknown",
    "source_class_unknown",
    "source_trust_unknown",
)

READINESS_STATES = (
    "READY_FOR_D2_NORMALIZED_ENVELOPE",
    "BLOCKED",
    "DEGRADED",
)

REQUIRED_TRUE_FLAGS = (
    "checksum_required",
    "credential_isolation_required",
    "evidence_registration_required",
    "local_only",
    "operator_review_required",
    "paper_only",
    "read_only",
    "sidecar_only",
)

REQUIRED_FALSE_FLAGS = (
    "archive_writing_allowed",
    "automatic_routing_allowed",
    "core_mutation_allowed",
    "credential_access_allowed",
    "database_write_allowed",
    "model_invocation_allowed",
    "prompt_execution_allowed",
    "real_execution_allowed",
    "trading_api_allowed",
    "unrestricted_file_write_allowed",
)

REQUIRED_CONTRACT_FIELDS = (
    "contract_id",
    "app_id",
    "stage_id",
    "contract_version",
    "planning_mode",
    "gateway_status",
    "allowed_operations",
    "prohibited_operations",
    "required_metadata_fields",
    "unknown_license_default",
    "unknown_freshness_default",
    "blocked_conditions",
    "degraded_conditions",
    "operator_review_status",
    "safety_flags",
)

_IDENTIFIER_PATTERN = re.compile(
    r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$"
)


class ReadOnlyGatewayBoundaryViolation(ValueError):
    """Raised when the D1 planning contract is invalid."""


def _safety_flags() -> dict[str, bool]:
    return {
        **{name: True for name in REQUIRED_TRUE_FLAGS},
        **{name: False for name in REQUIRED_FALSE_FLAGS},
    }


def _unknown_license_default() -> dict[str, Any]:
    return {
        "cloud_processing_allowed": False,
        "training_allowed": False,
        "redistribution_allowed": False,
        "retention_status": "RESTRICTED",
        "operator_review_required": True,
    }


def _unknown_freshness_default() -> dict[str, Any]:
    return {
        "classification": "UNKNOWN",
        "workflow_effect": "DEGRADED_OR_BLOCKED_BY_POLICY",
        "operator_review_required": True,
    }


def _valid_identifier(value: Any) -> bool:
    return (
        isinstance(value, str)
        and _IDENTIFIER_PATTERN.fullmatch(value) is not None
    )


def build_read_only_data_gateway_boundary_contract(
    *,
    contract_id: str = "fcf.read_only_data_gateway.planning.v1",
) -> dict[str, Any]:
    """Build the deterministic D1 planning-only boundary contract."""
    if not _valid_identifier(contract_id):
        raise ReadOnlyGatewayBoundaryViolation(
            "contract_id_invalid"
        )

    return {
        "contract_id": contract_id,
        "app_id": APP_ID,
        "stage_id": STAGE_ID,
        "contract_version": CONTRACT_VERSION,
        "planning_mode": PLANNING_MODE,
        "gateway_status": "READY_FOR_D2_NORMALIZED_ENVELOPE",
        "allowed_operations": list(ALLOWED_OPERATIONS),
        "prohibited_operations": list(PROHIBITED_OPERATIONS),
        "required_metadata_fields": list(REQUIRED_METADATA_FIELDS),
        "unknown_license_default": _unknown_license_default(),
        "unknown_freshness_default": _unknown_freshness_default(),
        "blocked_conditions": list(BLOCKED_CONDITIONS),
        "degraded_conditions": list(DEGRADED_CONDITIONS),
        "operator_review_status": "REVIEW_REQUIRED",
        "safety_flags": _safety_flags(),
    }


def _validate_safety_flags(value: Any) -> list[str]:
    if not isinstance(value, Mapping):
        return ["safety_flags_must_be_mapping"]

    errors: list[str] = []

    for name in REQUIRED_TRUE_FLAGS:
        if value.get(name) is not True:
            errors.append(f"{name}_must_be_true")

    for name in REQUIRED_FALSE_FLAGS:
        if value.get(name) is not False:
            errors.append(f"{name}_must_be_false")

    expected = set(
        REQUIRED_TRUE_FLAGS + REQUIRED_FALSE_FLAGS
    )
    if set(value.keys()) != expected:
        errors.append(
            "safety_flag_names_must_match_contract"
        )

    return errors


def validate_read_only_data_gateway_boundary_contract(
    contract: object,
) -> list[str]:
    """Return deterministic D1 validation errors."""
    if not isinstance(contract, Mapping):
        return ["contract_must_be_mapping"]

    errors: list[str] = []

    if set(contract.keys()) != set(REQUIRED_CONTRACT_FIELDS):
        errors.append("contract_fields_must_match_schema")

    expected_scalars = {
        "app_id": APP_ID,
        "stage_id": STAGE_ID,
        "contract_version": CONTRACT_VERSION,
        "planning_mode": PLANNING_MODE,
        "gateway_status": "READY_FOR_D2_NORMALIZED_ENVELOPE",
        "operator_review_status": "REVIEW_REQUIRED",
    }

    for field, expected in expected_scalars.items():
        if contract.get(field) != expected:
            errors.append(f"{field}_invalid")

    if not _valid_identifier(contract.get("contract_id")):
        errors.append("contract_id_invalid")

    expected_lists = {
        "allowed_operations": list(ALLOWED_OPERATIONS),
        "prohibited_operations": list(PROHIBITED_OPERATIONS),
        "required_metadata_fields": list(REQUIRED_METADATA_FIELDS),
        "blocked_conditions": list(BLOCKED_CONDITIONS),
        "degraded_conditions": list(DEGRADED_CONDITIONS),
    }

    for field, expected in expected_lists.items():
        if contract.get(field) != expected:
            errors.append(f"{field}_invalid")

    if contract.get("unknown_license_default") != (
        _unknown_license_default()
    ):
        errors.append("unknown_license_default_invalid")

    if contract.get("unknown_freshness_default") != (
        _unknown_freshness_default()
    ):
        errors.append("unknown_freshness_default_invalid")

    errors.extend(
        _validate_safety_flags(contract.get("safety_flags"))
    )

    return errors
