"""Boundary contract for DASHBOARD-CONTRADICTION-SCANNER-APP-1."""

from __future__ import annotations

from typing import Any

APP_ID = "DASHBOARD-CONTRADICTION-SCANNER-APP-1"
CONTRACT_VERSION = "1.0.0"

REQUIRED_BOUNDARIES = {
    "paper_only": True,
    "local_only": True,
    "read_only": True,
    "sidecar_only": True,
    "operator_review_required": True,
    "core_mutation_allowed": False,
    "p48_core_expansion_allowed": False,
    "source_mutation_allowed": False,
    "risk_flag_deletion_allowed": False,
    "risk_flag_downgrade_allowed": False,
    "automatic_review_pass_allowed": False,
    "ui_action_creation_allowed": False,
    "real_trading_allowed": False,
    "real_execution_allowed": False,
    "credential_access_allowed": False,
}

ALLOWED_SOURCE_TYPES = (
    "DASHBOARD_STATUS_PACKET",
    "OPERATOR_REVIEW_PACKET",
    "MODEL_GOVERNANCE_PACKET",
    "VALIDATION_BASELINE_SNAPSHOT",
    "ARTIFACT_LIFECYCLE_RECORD",
    "AI_EVIDENCE_PACKAGE",
)

REQUIRED_TRACE_FIELDS = (
    "correlation_id",
    "research_run_id",
    "source_artifact_ids",
    "validation_baseline_id",
)

CONTRADICTION_CLASSES = (
    "RISK_FLAG_MISSING",
    "RISK_FLAG_DOWNGRADED",
    "SUMMARY_RAW_CONFLICT",
    "REVIEW_STATE_MISMATCH",
    "LIFECYCLE_STATE_MISMATCH",
    "VALIDATION_STATE_MISMATCH",
    "ARCHIVE_STATE_MISMATCH",
    "SOURCE_LINEAGE_MISMATCH",
)

FORBIDDEN_CAPABILITIES = (
    "BUY",
    "SELL",
    "ORDER",
    "EXECUTE",
    "POSITION_SIZE",
    "PORTFOLIO_ACTION",
    "BROKER_CONNECTION",
    "EXCHANGE_CONNECTION",
    "API_KEY_ACCESS",
    "WALLET_PRIVATE_KEY_ACCESS",
    "REAL_ACCOUNT_ACCESS",
    "REAL_POSITION_ACCESS",
    "OPERATOR_REVIEW_BYPASS",
)


def build_contract() -> dict[str, Any]:
    """Return the immutable semantic boundary for the scanner sidecar."""
    return {
        "app_id": APP_ID,
        "contract_version": CONTRACT_VERSION,
        "boundaries": dict(REQUIRED_BOUNDARIES),
        "allowed_source_types": list(ALLOWED_SOURCE_TYPES),
        "required_trace_fields": list(REQUIRED_TRACE_FIELDS),
        "contradiction_classes": list(CONTRADICTION_CLASSES),
        "forbidden_capabilities": list(FORBIDDEN_CAPABILITIES),
        "output_kind": "PAPER_ONLY_CONTRADICTION_FINDINGS",
        "human_review_required": True,
        "archive_required": True,
    }


def validate_contract(contract: dict[str, Any]) -> list[str]:
    """Return contract validation errors without mutating the contract."""
    errors: list[str] = []

    if contract.get("app_id") != APP_ID:
        errors.append("invalid_app_id")

    if contract.get("contract_version") != CONTRACT_VERSION:
        errors.append("invalid_contract_version")

    boundaries = contract.get("boundaries")
    if not isinstance(boundaries, dict):
        errors.append("missing_boundaries")
        return errors

    for name, expected in REQUIRED_BOUNDARIES.items():
        if boundaries.get(name) is not expected:
            errors.append(f"invalid_boundary:{name}")

    trace_fields = contract.get("required_trace_fields")
    if not isinstance(trace_fields, list):
        errors.append("missing_required_trace_fields")
    else:
        for field in REQUIRED_TRACE_FIELDS:
            if field not in trace_fields:
                errors.append(f"missing_trace_field:{field}")

    if contract.get("human_review_required") is not True:
        errors.append("human_review_not_required")

    if contract.get("archive_required") is not True:
        errors.append("archive_not_required")

    return errors
