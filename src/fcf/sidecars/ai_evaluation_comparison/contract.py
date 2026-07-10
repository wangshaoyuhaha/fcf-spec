"""Boundary contract for deterministic AI evaluation comparison."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any


APP_ID = "AI-EVALUATION-COMPARISON-APP-1"
STAGE_ID = "AI-EVALUATION-COMPARISON-D1"
CONTRACT_VERSION = "1.0.0"


ALLOWED_INPUTS = (
    "local_evaluation_sample_registry_reference",
    "local_evaluation_result_registry_reference",
    "local_prompt_model_version_registry_reference",
    "local_context_evidence_reference",
    "local_validation_metadata",
)


ALLOWED_OUTPUTS = (
    "evaluation_comparison_boundary_contract",
    "evaluation_comparison_record_metadata",
    "comparison_registry_handoff_metadata",
    "operator_review_governance_metadata",
)


COMPARISON_MODES = (
    "expected_vs_observed",
    "cross_model",
    "cross_model_version",
    "cross_prompt_version",
)


REQUIRED_COMPARISON_DIMENSIONS = (
    "evaluation_sample_id",
    "expected_result_reference",
    "observed_result_reference",
    "model_id",
    "model_version",
    "prompt_id",
    "prompt_version",
    "context_evidence_reference",
    "result_status",
    "comparison_status",
    "operator_review_status",
)


COMPARISON_STATUSES = (
    "MATCHED",
    "PARTIAL_MATCH",
    "MISMATCH",
    "REVIEW_REQUIRED",
    "INVALID",
    "BLOCKED",
    "ARCHIVED",
)


FORBIDDEN_COMPARISON_STATUSES = (
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
    "deterministic_comparison_only",
    "registered_artifacts_only",
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
    """Build a fresh D1 evaluation comparison boundary contract."""

    return {
        "app_id": APP_ID,
        "stage_id": STAGE_ID,
        "contract_version": CONTRACT_VERSION,
        "purpose": (
            "Compare registered expected and observed AI evaluation "
            "artifacts deterministically without invoking a model."
        ),
        "allowed_inputs": list(ALLOWED_INPUTS),
        "allowed_outputs": list(ALLOWED_OUTPUTS),
        "comparison_modes": list(COMPARISON_MODES),
        "required_comparison_dimensions": list(
            REQUIRED_COMPARISON_DIMENSIONS
        ),
        "comparison_statuses": list(COMPARISON_STATUSES),
        "forbidden_comparison_statuses": list(
            FORBIDDEN_COMPARISON_STATUSES
        ),
        "forbidden_capabilities": list(
            REQUIRED_FORBIDDEN_CAPABILITIES
        ),
        "paper_only": True,
        "local_only": True,
        "read_only": True,
        "sidecar_only": True,
        "operator_review_required": True,
        "deterministic_comparison_only": True,
        "registered_artifacts_only": True,
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


def _validate_exact_list(
    contract: Mapping[str, Any],
    field: str,
    expected: tuple[str, ...],
    errors: list[str],
) -> None:
    value = contract.get(field)

    if not _valid_string_list(value):
        errors.append(f"{field}_invalid")
        return

    if value != list(expected):
        errors.append(f"{field}_mismatch")


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

    purpose = contract.get("purpose")

    if not isinstance(purpose, str) or not purpose.strip():
        errors.append("purpose_invalid")

    for field in REQUIRED_TRUE_FLAGS:
        if contract.get(field) is not True:
            errors.append(f"{field}_must_be_true")

    for field in REQUIRED_FALSE_FLAGS:
        if contract.get(field) is not False:
            errors.append(f"{field}_must_be_false")

    _validate_exact_list(
        contract,
        "allowed_inputs",
        ALLOWED_INPUTS,
        errors,
    )
    _validate_exact_list(
        contract,
        "allowed_outputs",
        ALLOWED_OUTPUTS,
        errors,
    )
    _validate_exact_list(
        contract,
        "comparison_modes",
        COMPARISON_MODES,
        errors,
    )
    _validate_exact_list(
        contract,
        "required_comparison_dimensions",
        REQUIRED_COMPARISON_DIMENSIONS,
        errors,
    )
    _validate_exact_list(
        contract,
        "comparison_statuses",
        COMPARISON_STATUSES,
        errors,
    )
    _validate_exact_list(
        contract,
        "forbidden_comparison_statuses",
        FORBIDDEN_COMPARISON_STATUSES,
        errors,
    )

    comparison_statuses = contract.get(
        "comparison_statuses",
        [],
    )

    if isinstance(comparison_statuses, list):
        for forbidden_status in FORBIDDEN_COMPARISON_STATUSES:
            if forbidden_status in comparison_statuses:
                errors.append(
                    "forbidden_status_enabled:"
                    f"{forbidden_status}"
                )

    forbidden_capabilities = contract.get(
        "forbidden_capabilities",
        [],
    )

    if not _valid_string_list(forbidden_capabilities):
        errors.append("forbidden_capabilities_invalid")
    else:
        for capability in REQUIRED_FORBIDDEN_CAPABILITIES:
            if capability not in forbidden_capabilities:
                errors.append(
                    "missing_forbidden_capability:"
                    f"{capability}"
                )

    return sorted(set(errors))