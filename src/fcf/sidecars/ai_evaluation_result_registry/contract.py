"""Boundary contract for imported AI evaluation result governance."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any


APP_ID = "AI-EVALUATION-RESULT-REGISTRY-APP-1"
STAGE_ID = "AI-EVALUATION-RESULT-REGISTRY-D1"
CONTRACT_VERSION = "1.0.0"

IMPORTED_RESULT_STATUSES = (
    "RECORDED",
    "REVIEW_REQUIRED",
    "INVALID",
    "BLOCKED",
    "ARCHIVED",
)

FORBIDDEN_RESULT_STATUSES = (
    "AUTO_APPROVED",
    "TRADE_READY",
    "EXECUTION_READY",
    "LIVE_READY",
)

REQUIRED_TRUE_FLAGS = (
    "paper_only",
    "local_only",
    "read_only",
    "sidecar_only",
    "operator_review_required",
    "imported_artifacts_only",
)

REQUIRED_FALSE_FLAGS = (
    "operator_review_bypass_allowed",
    "automatic_evaluation_acceptance_allowed",
    "source_artifact_mutation_allowed",
    "model_invocation_allowed",
    "prompt_execution_allowed",
    "orchestrator_execution_allowed",
    "news_feed_connection_allowed",
    "trade_instruction_generation_allowed",
    "trade_action_allowed",
    "real_trading_allowed",
    "real_execution_allowed",
    "broker_connection_allowed",
    "exchange_connection_allowed",
    "api_key_storage_allowed",
    "wallet_private_key_access_allowed",
    "real_account_access_allowed",
    "real_position_access_allowed",
    "automatic_position_sizing_allowed",
    "automatic_portfolio_action_allowed",
    "core_mutation_allowed",
    "p48_core_expansion_allowed",
)

REQUIRED_FORBIDDEN_CAPABILITIES = (
    "p48_core_expansion",
    "core_mutation",
    "source_artifact_mutation",
    "live_model_invocation",
    "prompt_execution",
    "ai_orchestrator_execution",
    "news_feed_connection",
    "automatic_evaluation_acceptance",
    "operator_review_bypass",
    "trade_instruction_generation",
    "real_trading",
    "real_execution",
    "broker_or_exchange_connection",
    "credential_storage",
    "wallet_private_key_access",
    "real_account_or_position_access",
    "automatic_position_or_portfolio_action",
)


def build_boundary_contract() -> dict[str, Any]:
    """Build a fresh D1 imported-result boundary contract."""

    return {
        "app_id": APP_ID,
        "stage_id": STAGE_ID,
        "contract_version": CONTRACT_VERSION,
        "purpose": (
            "Register local operator-imported AI evaluation result "
            "artifacts without invoking a model or executing a prompt."
        ),
        "allowed_inputs": [
            "local_evaluation_sample_reference",
            "local_prompt_model_version_registry_reference",
            "local_context_evidence_reference",
            "operator_imported_evaluation_output_reference",
            "local_validation_metadata",
        ],
        "allowed_outputs": [
            "imported_evaluation_result_contract",
            "evaluation_result_record_metadata",
            "result_registry_handoff_metadata",
            "operator_review_governance_metadata",
        ],
        "imported_result_statuses": list(
            IMPORTED_RESULT_STATUSES
        ),
        "forbidden_result_statuses": list(
            FORBIDDEN_RESULT_STATUSES
        ),
        "forbidden_capabilities": list(
            REQUIRED_FORBIDDEN_CAPABILITIES
        ),
        "paper_only": True,
        "local_only": True,
        "read_only": True,
        "sidecar_only": True,
        "operator_review_required": True,
        "imported_artifacts_only": True,
        "operator_review_bypass_allowed": False,
        "automatic_evaluation_acceptance_allowed": False,
        "source_artifact_mutation_allowed": False,
        "model_invocation_allowed": False,
        "prompt_execution_allowed": False,
        "orchestrator_execution_allowed": False,
        "news_feed_connection_allowed": False,
        "trade_instruction_generation_allowed": False,
        "trade_action_allowed": False,
        "real_trading_allowed": False,
        "real_execution_allowed": False,
        "broker_connection_allowed": False,
        "exchange_connection_allowed": False,
        "api_key_storage_allowed": False,
        "wallet_private_key_access_allowed": False,
        "real_account_access_allowed": False,
        "real_position_access_allowed": False,
        "automatic_position_sizing_allowed": False,
        "automatic_portfolio_action_allowed": False,
        "core_mutation_allowed": False,
        "p48_core_expansion_allowed": False,
    }


def _valid_string_list(
    value: Any,
    *,
    allow_empty: bool = False,
) -> bool:
    if not isinstance(value, list):
        return False

    if not allow_empty and not value:
        return False

    return all(
        isinstance(item, str) and bool(item.strip())
        for item in value
    )


def validate_boundary_contract(
    contract: Mapping[str, Any],
) -> list[str]:
    """Return deterministic boundary contract validation errors."""

    if not isinstance(contract, Mapping):
        return ["contract_not_mapping"]

    errors: list[str] = []

    expected_identity = {
        "app_id": APP_ID,
        "stage_id": STAGE_ID,
        "contract_version": CONTRACT_VERSION,
    }

    for field, expected in expected_identity.items():
        if contract.get(field) != expected:
            errors.append(f"{field}_mismatch")

    for field in REQUIRED_TRUE_FLAGS:
        if contract.get(field) is not True:
            errors.append(f"{field}_must_be_true")

    for field in REQUIRED_FALSE_FLAGS:
        if contract.get(field) is not False:
            errors.append(f"{field}_must_be_false")

    for field in (
        "allowed_inputs",
        "allowed_outputs",
        "imported_result_statuses",
        "forbidden_result_statuses",
        "forbidden_capabilities",
    ):
        if not _valid_string_list(contract.get(field)):
            errors.append(f"{field}_invalid")

    imported_statuses = contract.get(
        "imported_result_statuses",
        [],
    )

    if isinstance(imported_statuses, list):
        if imported_statuses != list(IMPORTED_RESULT_STATUSES):
            errors.append("imported_result_statuses_mismatch")

        for forbidden_status in FORBIDDEN_RESULT_STATUSES:
            if forbidden_status in imported_statuses:
                errors.append(
                    f"forbidden_status_enabled:{forbidden_status}"
                )

    forbidden_statuses = contract.get(
        "forbidden_result_statuses",
        [],
    )

    if (
        isinstance(forbidden_statuses, list)
        and forbidden_statuses
        != list(FORBIDDEN_RESULT_STATUSES)
    ):
        errors.append("forbidden_result_statuses_mismatch")

    forbidden_capabilities = contract.get(
        "forbidden_capabilities",
        [],
    )

    if isinstance(forbidden_capabilities, list):
        for capability in REQUIRED_FORBIDDEN_CAPABILITIES:
            if capability not in forbidden_capabilities:
                errors.append(
                    f"missing_forbidden_capability:{capability}"
                )

    return errors