"""Planning-only boundary contract for the FCF API Gateway."""

import re
from collections.abc import Mapping
from typing import Any

APP_ID = "FCF-API-GATEWAY-PLANNING-APP-1"
STAGE_ID = "FCF-API-GATEWAY-PLANNING-D1"
CONTRACT_VERSION = "1.0.0"
PLANNING_MODE = "PLANNING_ONLY"
GATEWAY_STATUS = "DESIGN_ONLY"

ARCHITECTURE_PATH = (
    "FCF_WEB_CONSOLE",
    "WORKFLOW_ORCHESTRATION_LAYER",
    "FCF_API_GATEWAY",
    "SIDECAR_APPLICATION_SERVICES",
    "FROZEN_DETERMINISTIC_CORE",
)

AUTHORITY_HIERARCHY = (
    "OPERATOR_POLICY",
    "FCF_HARD_POLICY",
    "DETERMINISTIC_ENGINE",
    "VALIDATED_DATA_AND_EVIDENCE",
    "ORCHESTRATOR",
    "AI_MODELS",
    "EXTERNAL_NARRATIVE",
)

ALLOWED_REQUEST_CLASSES = (
    "ARTIFACT_METADATA_READ",
    "EVIDENCE_REFERENCE_READ",
    "HEALTH_STATUS_READ",
    "OPERATOR_REVIEW_REQUEST",
    "POLICY_STATUS_READ",
    "REANALYSIS_REQUEST",
    "RESEARCH_WORKFLOW_STATUS_READ",
    "STOP_WORKFLOW_REQUEST",
)

PROHIBITED_REQUEST_CLASSES = (
    "ARCHIVE_WRITE",
    "AUTOMATIC_APPROVAL",
    "AUTOMATIC_ARCHIVE",
    "AUTOMATIC_MODEL_ROUTING",
    "BALANCE_ACCESS",
    "CORE_MUTATION",
    "CREDENTIAL_ACCESS",
    "DATABASE_WRITE",
    "DIRECT_MODEL_INVOCATION",
    "DIRECT_PROMPT_EXECUTION",
    "ORDER_CANCELLATION",
    "ORDER_PLACEMENT",
    "POSITION_ACCESS",
    "REAL_EXECUTION",
    "TRADING_API_ACCESS",
    "UNRESTRICTED_FILE_WRITE",
    "WALLET_ACCESS",
)

ALLOWED_RESPONSIBILITIES = (
    "CORRELATION_ID_PROPAGATION",
    "DETERMINISTIC_ERROR_NORMALIZATION",
    "GATEWAY_CONTRACT_VALIDATION",
    "HEALTH_AND_STATUS_READS",
    "OPERATOR_CONFIRMATION_BOUNDARY",
    "POLICY_GATE_ENFORCEMENT",
    "REGISTERED_ARTIFACT_REFERENCE_ONLY",
    "REQUEST_SCHEMA_VALIDATION",
)

PROHIBITED_RESPONSIBILITIES = (
    "ARCHIVE_AUTHORIZATION",
    "ARCHIVE_WRITING",
    "DETERMINISTIC_SCORE_MUTATION",
    "FINAL_TRUTH_SELECTION",
    "MODEL_INVOCATION",
    "POLICY_OWNERSHIP",
    "PROMPT_EXECUTION",
    "REAL_WORLD_EXECUTION",
    "RESEARCH_APPROVAL",
    "RISK_FLAG_DELETION",
)

REQUIRED_REQUEST_METADATA = (
    "config_snapshot_id",
    "correlation_id",
    "operator_action",
    "policy_version",
    "request_id",
    "requested_at_utc",
    "source_artifact_ids",
)

REQUIRED_RESPONSE_METADATA = (
    "correlation_id",
    "errors",
    "generated_at_utc",
    "operator_review_required",
    "policy_decision",
    "request_id",
    "source_artifact_ids",
    "status",
    "warnings",
)

REQUIRED_TRUE_FLAGS = (
    "correlation_id_required",
    "deterministic_authority_preserved",
    "operator_review_required",
    "paper_only",
    "planning_only",
    "policy_gate_required",
    "read_only",
    "registered_artifacts_only",
    "schema_validation_required",
    "sidecar_only",
)

REQUIRED_FALSE_FLAGS = (
    "archive_writing_allowed",
    "automatic_approval_allowed",
    "automatic_archive_allowed",
    "automatic_routing_allowed",
    "balance_access_allowed",
    "core_mutation_allowed",
    "credential_access_allowed",
    "database_write_allowed",
    "http_server_active",
    "model_invocation_allowed",
    "port_listener_allowed",
    "position_access_allowed",
    "prompt_execution_allowed",
    "real_execution_allowed",
    "trading_api_allowed",
    "wallet_access_allowed",
)

REQUIRED_CONTRACT_FIELDS = (
    "allowed_request_classes",
    "allowed_responsibilities",
    "app_id",
    "architecture_path",
    "authority_hierarchy",
    "contract_id",
    "contract_version",
    "gateway_status",
    "operator_review_status",
    "planning_mode",
    "prohibited_request_classes",
    "prohibited_responsibilities",
    "required_request_metadata",
    "required_response_metadata",
    "safety_flags",
    "stage_id",
)

_IDENTIFIER_PATTERN = re.compile(
    r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$"
)


class FcfApiGatewayBoundaryViolation(ValueError):
    """Raised when the planning-only gateway contract is invalid."""


def _valid_identifier(value: Any) -> bool:
    return (
        isinstance(value, str)
        and _IDENTIFIER_PATTERN.fullmatch(value) is not None
    )


def _safety_flags() -> dict[str, bool]:
    return {
        **{name: True for name in REQUIRED_TRUE_FLAGS},
        **{name: False for name in REQUIRED_FALSE_FLAGS},
    }


def build_fcf_api_gateway_boundary_contract(
    *,
    contract_id: str = "fcf.api_gateway.planning.v1",
) -> dict[str, Any]:
    """Build the deterministic D1 planning-only gateway contract."""
    if not _valid_identifier(contract_id):
        raise FcfApiGatewayBoundaryViolation(
            "contract_id_invalid"
        )

    return {
        "contract_id": contract_id,
        "app_id": APP_ID,
        "stage_id": STAGE_ID,
        "contract_version": CONTRACT_VERSION,
        "planning_mode": PLANNING_MODE,
        "gateway_status": GATEWAY_STATUS,
        "architecture_path": list(ARCHITECTURE_PATH),
        "authority_hierarchy": list(AUTHORITY_HIERARCHY),
        "allowed_request_classes": list(ALLOWED_REQUEST_CLASSES),
        "prohibited_request_classes": list(
            PROHIBITED_REQUEST_CLASSES
        ),
        "allowed_responsibilities": list(
            ALLOWED_RESPONSIBILITIES
        ),
        "prohibited_responsibilities": list(
            PROHIBITED_RESPONSIBILITIES
        ),
        "required_request_metadata": list(
            REQUIRED_REQUEST_METADATA
        ),
        "required_response_metadata": list(
            REQUIRED_RESPONSE_METADATA
        ),
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

    expected_names = set(
        REQUIRED_TRUE_FLAGS + REQUIRED_FALSE_FLAGS
    )
    if set(value.keys()) != expected_names:
        errors.append("safety_flag_names_must_match_contract")

    return errors


def validate_fcf_api_gateway_boundary_contract(
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
        "gateway_status": GATEWAY_STATUS,
        "operator_review_status": "REVIEW_REQUIRED",
    }

    for field, expected in expected_scalars.items():
        if contract.get(field) != expected:
            errors.append(f"{field}_invalid")

    if not _valid_identifier(contract.get("contract_id")):
        errors.append("contract_id_invalid")

    expected_lists = {
        "architecture_path": list(ARCHITECTURE_PATH),
        "authority_hierarchy": list(AUTHORITY_HIERARCHY),
        "allowed_request_classes": list(
            ALLOWED_REQUEST_CLASSES
        ),
        "prohibited_request_classes": list(
            PROHIBITED_REQUEST_CLASSES
        ),
        "allowed_responsibilities": list(
            ALLOWED_RESPONSIBILITIES
        ),
        "prohibited_responsibilities": list(
            PROHIBITED_RESPONSIBILITIES
        ),
        "required_request_metadata": list(
            REQUIRED_REQUEST_METADATA
        ),
        "required_response_metadata": list(
            REQUIRED_RESPONSE_METADATA
        ),
    }

    for field, expected in expected_lists.items():
        if contract.get(field) != expected:
            errors.append(f"{field}_invalid")

    errors.extend(
        _validate_safety_flags(contract.get("safety_flags"))
    )

    return errors
