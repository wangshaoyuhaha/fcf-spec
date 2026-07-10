"""Boundary contract for the local AI evaluation sample library."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any


APP_ID = "AI-EVALUATION-SAMPLE-LIBRARY-APP-1"
STAGE_ID = "AI-EVALUATION-SAMPLE-LIBRARY-D1"
CONTRACT_VERSION = "1.0.0"

REQUIRED_TRUE_FLAGS = (
    "paper_only",
    "local_only",
    "read_only",
    "sidecar_only",
    "operator_review_required",
)

REQUIRED_FALSE_FLAGS = (
    "operator_review_bypass_allowed",
    "core_mutation_allowed",
    "p48_core_expansion_allowed",
    "source_content_mutation_allowed",
    "prompt_execution_allowed",
    "model_invocation_allowed",
    "orchestrator_execution_allowed",
    "news_feed_connection_allowed",
    "expected_result_auto_approval_allowed",
    "sample_trade_instruction_allowed",
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
    "trade_action_allowed",
    "buy_button_enabled",
    "sell_button_enabled",
    "order_button_enabled",
)

REQUIRED_FORBIDDEN_CAPABILITIES = (
    "p48_core_expansion",
    "core_mutation",
    "source_content_mutation",
    "live_model_invocation",
    "prompt_execution",
    "ai_orchestrator_execution",
    "news_feed_connection",
    "operator_review_bypass",
    "trade_instruction_generation",
    "real_trading",
    "real_execution",
    "broker_or_exchange_connection",
    "credential_storage",
    "real_account_or_position_access",
    "automatic_position_or_portfolio_action",
)


def build_boundary_contract() -> dict[str, Any]:
    """Build a fresh paper-only D1 boundary contract."""

    return {
        "app_id": APP_ID,
        "stage_id": STAGE_ID,
        "contract_version": CONTRACT_VERSION,
        "purpose": (
            "Govern local structured AI evaluation sample definitions "
            "without invoking or executing an AI model."
        ),
        "allowed_inputs": [
            "local_prompt_model_version_registry_reference",
            "local_context_evidence_reference",
            "local_evaluation_sample_metadata",
            "operator_review_metadata",
        ],
        "allowed_outputs": [
            "evaluation_sample_boundary_contract",
            "local_sample_definition_metadata",
            "paper_only_governance_handoff",
        ],
        "forbidden_capabilities": list(
            REQUIRED_FORBIDDEN_CAPABILITIES
        ),
        "paper_only": True,
        "local_only": True,
        "read_only": True,
        "sidecar_only": True,
        "operator_review_required": True,
        "operator_review_bypass_allowed": False,
        "core_mutation_allowed": False,
        "p48_core_expansion_allowed": False,
        "source_content_mutation_allowed": False,
        "prompt_execution_allowed": False,
        "model_invocation_allowed": False,
        "orchestrator_execution_allowed": False,
        "news_feed_connection_allowed": False,
        "expected_result_auto_approval_allowed": False,
        "sample_trade_instruction_allowed": False,
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
        "trade_action_allowed": False,
        "buy_button_enabled": False,
        "sell_button_enabled": False,
        "order_button_enabled": False,
    }


def _valid_string_list(value: Any) -> bool:
    return (
        isinstance(value, list)
        and bool(value)
        and all(
            isinstance(item, str) and bool(item.strip())
            for item in value
        )
    )


def validate_boundary_contract(
    contract: Mapping[str, Any],
) -> list[str]:
    """Return deterministic boundary validation errors."""

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

    for field in ("allowed_inputs", "allowed_outputs"):
        if not _valid_string_list(contract.get(field)):
            errors.append(f"{field}_invalid")

    forbidden = contract.get("forbidden_capabilities")

    if not _valid_string_list(forbidden):
        errors.append("forbidden_capabilities_invalid")
    else:
        for capability in REQUIRED_FORBIDDEN_CAPABILITIES:
            if capability not in forbidden:
                errors.append(
                    f"missing_forbidden_capability:{capability}"
                )

    return errors