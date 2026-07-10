"""Boundary contract for AI prompt and model version governance."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

APP_ID = "AI-PROMPT-MODEL-VERSION-REGISTRY-APP-1"
CONTRACT_VERSION = "1.0.0"

REQUIRED_BOUNDARIES = {
    "paper_only": True,
    "local_only": True,
    "read_only": True,
    "sidecar_only": True,
    "operator_review_required": True,
    "core_mutation_allowed": False,
    "p48_core_expansion_allowed": False,
    "source_artifact_mutation_allowed": False,
    "prompt_content_mutation_allowed": False,
    "model_execution_allowed": False,
    "automatic_activation_allowed": False,
    "automatic_promotion_allowed": False,
    "automatic_rollback_allowed": False,
    "credential_storage_allowed": False,
    "api_key_access_allowed": False,
    "real_trading_allowed": False,
    "real_execution_allowed": False,
}

REQUIRED_VERSION_FIELDS = (
    "registry_entry_id",
    "prompt_version",
    "model_version",
    "contract_version",
    "registry_version",
)

REQUIRED_TRACE_FIELDS = (
    "correlation_id",
    "research_run_id",
    "source_artifact_ids",
    "validation_baseline_id",
)

VERSION_KINDS = (
    "PROMPT",
    "MODEL",
    "CONTRACT",
    "REGISTRY",
)

VERSION_STATUSES = (
    "DRAFT",
    "REVIEW_REQUIRED",
    "APPROVED_FOR_PAPER_RESEARCH",
    "DEPRECATED",
    "ARCHIVED",
    "BLOCKED",
)

FORBIDDEN_CAPABILITIES = (
    "MODEL_EXECUTION",
    "PROMPT_AUTO_DEPLOY",
    "MODEL_AUTO_DEPLOY",
    "AUTOMATIC_ACTIVATION",
    "AUTOMATIC_PROMOTION",
    "AUTOMATIC_ROLLBACK",
    "BROKER_CONNECTION",
    "EXCHANGE_CONNECTION",
    "API_KEY_ACCESS",
    "WALLET_PRIVATE_KEY_ACCESS",
    "REAL_ACCOUNT_ACCESS",
    "REAL_POSITION_ACCESS",
    "BUY",
    "SELL",
    "ORDER",
    "EXECUTE",
    "POSITION_SIZE",
    "PORTFOLIO_ACTION",
    "OPERATOR_REVIEW_BYPASS",
)


def build_contract() -> dict[str, Any]:
    """Return the immutable semantic boundary for the registry."""
    return {
        "app_id": APP_ID,
        "contract_version": CONTRACT_VERSION,
        "boundaries": dict(REQUIRED_BOUNDARIES),
        "required_version_fields": list(REQUIRED_VERSION_FIELDS),
        "required_trace_fields": list(REQUIRED_TRACE_FIELDS),
        "version_kinds": list(VERSION_KINDS),
        "version_statuses": list(VERSION_STATUSES),
        "forbidden_capabilities": list(FORBIDDEN_CAPABILITIES),
        "output_kind": "PAPER_ONLY_VERSION_REGISTRY_RECORDS",
        "human_review_required": True,
        "archive_required": True,
    }


def validate_contract(contract: Mapping[str, Any]) -> list[str]:
    """Validate the registry boundary without mutating input."""
    if not isinstance(contract, Mapping):
        return ["contract_must_be_mapping"]

    errors: list[str] = []

    if contract.get("app_id") != APP_ID:
        errors.append("invalid_app_id")

    if contract.get("contract_version") != CONTRACT_VERSION:
        errors.append("invalid_contract_version")

    boundaries = contract.get("boundaries")
    if not isinstance(boundaries, Mapping):
        errors.append("missing_boundaries")
    else:
        for name, expected in REQUIRED_BOUNDARIES.items():
            if boundaries.get(name) is not expected:
                errors.append(f"invalid_boundary:{name}")

    version_fields = contract.get("required_version_fields")
    if not isinstance(version_fields, list):
        errors.append("missing_required_version_fields")
    else:
        for field in REQUIRED_VERSION_FIELDS:
            if field not in version_fields:
                errors.append(f"missing_version_field:{field}")

    trace_fields = contract.get("required_trace_fields")
    if not isinstance(trace_fields, list):
        errors.append("missing_required_trace_fields")
    else:
        for field in REQUIRED_TRACE_FIELDS:
            if field not in trace_fields:
                errors.append(f"missing_trace_field:{field}")

    if contract.get("version_kinds") != list(VERSION_KINDS):
        errors.append("invalid_version_kinds")

    if contract.get("version_statuses") != list(VERSION_STATUSES):
        errors.append("invalid_version_statuses")

    if contract.get("human_review_required") is not True:
        errors.append("human_review_not_required")

    if contract.get("archive_required") is not True:
        errors.append("archive_not_required")

    return errors
