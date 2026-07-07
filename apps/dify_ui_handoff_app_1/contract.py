"""DIFY-UI-HANDOFF-D1 boundary contract.

This module defines a paper-only, local-only, read-only sidecar boundary for
connecting existing FCF artifacts to a manually configured local Dify/Ollama UI
workflow. It does not execute trades and does not connect to brokers or
exchanges.
"""

from __future__ import annotations

from copy import deepcopy
from typing import Any, Dict, List, Optional


APP_ID = "DIFY-UI-HANDOFF-APP-1"
STAGE_ID = "DIFY-UI-HANDOFF-D1"
CONTRACT_VERSION = "1.0.0"

PURPOSE = (
    "Paper-only local handoff contract for exposing FCF reports, UI artifacts, "
    "operator review packets, and workflow summaries to a manually configured "
    "Dify/Ollama assistant."
)

UPSTREAM_READ_SOURCES: List[Dict[str, str]] = [
    {
        "source_id": "runtime_operator_console_index",
        "source_kind": "local_static_ui",
        "relative_path": "runtime/operator_console/index.html",
    },
    {
        "source_id": "operator_console_static_export",
        "source_kind": "local_artifact_bundle",
        "relative_path": "artifacts/operator_console_static_export",
    },
    {
        "source_id": "operator_workflow_bundle",
        "source_kind": "local_artifact_bundle",
        "relative_path": "artifacts/operator_workflow_bundle",
    },
    {
        "source_id": "paper_readable_report",
        "source_kind": "local_report_bundle",
        "relative_path": "artifacts/paper_readable_report",
    },
    {
        "source_id": "paper_governance_report",
        "source_kind": "local_report_bundle",
        "relative_path": "artifacts/paper_governance_report",
    },
    {
        "source_id": "dashboard_status_final_state",
        "source_kind": "current_state_file",
        "relative_path": "FCF_CURRENT_STATE_DASHBOARD_STATUS_APP_1_FINAL.md",
    },
    {
        "source_id": "final_completion_review_state",
        "source_kind": "current_state_file",
        "relative_path": "FCF_CURRENT_STATE_FINAL_COMPLETION_REVIEW_APP_1_FINAL.md",
    },
]

PLANNED_OUTPUT_ARTIFACTS: List[str] = [
    "dify_input_contract",
    "dify_output_contract",
    "dify_prompt_template",
    "dify_workflow_manual_config",
    "dify_safety_boundary",
    "local_ui_entry_manifest",
    "operator_usage_quickstart",
]

SAFETY_FLAGS: Dict[str, Any] = {
    "paper_only": True,
    "local_only": True,
    "read_only": True,
    "sidecar_only": True,
    "operator_review_required": True,
    "operator_review_bypass_allowed": False,
    "core_mutation_allowed": False,
    "p48_core_expansion_allowed": False,
    "source_content_mutation_allowed": False,
    "source_deletion_allowed": False,
    "source_overwrite_allowed": False,
    "score_mutation_allowed": False,
    "reason_code_mutation_allowed": False,
    "risk_flag_deletion_allowed": False,
    "risk_flag_downgrade_allowed": False,
    "real_execution_allowed": False,
    "trade_action_enabled": False,
    "buy_button_enabled": False,
    "sell_button_enabled": False,
    "order_button_enabled": False,
    "broker_connection_allowed": False,
    "exchange_connection_allowed": False,
    "credential_storage_allowed": False,
    "api_key_storage_allowed": False,
    "wallet_private_key_access_allowed": False,
    "real_account_access_allowed": False,
    "real_position_access_allowed": False,
    "automatic_position_sizing_allowed": False,
    "automatic_portfolio_action_allowed": False,
    "workflow_execution_allowed": False,
    "workflow_auto_approval_allowed": False,
    "llm_trade_instruction_allowed": False,
    "llm_order_ticket_allowed": False,
    "llm_profit_guarantee_allowed": False,
    "future_return_prediction_allowed": False,
    "tag_created": False,
    "release_created": False,
    "deployed": False,
}

DIFY_LOCAL_ASSUMPTIONS: Dict[str, Any] = {
    "dify_runtime": "user_managed_local_deployment",
    "ollama_runtime": "user_managed_local_deployment",
    "docker_runtime": "user_managed_local_deployment",
    "internet_required_by_contract": False,
    "secrets_required_by_contract": False,
    "manual_configuration_required": True,
    "automated_dify_api_write_allowed": False,
    "automated_dify_app_creation_allowed": False,
}

FORBIDDEN_DIFY_OUTPUTS: List[str] = [
    "buy instruction",
    "sell instruction",
    "order instruction",
    "position sizing instruction",
    "portfolio rebalance instruction",
    "broker connection instruction",
    "exchange connection instruction",
    "api key request",
    "wallet private key request",
    "real account access request",
    "real position access request",
    "profit guarantee",
    "future return guarantee",
    "operator review bypass",
    "risk flag downgrade",
    "reason code deletion",
]


def get_dify_ui_handoff_contract() -> Dict[str, Any]:
    """Return the DIFY-UI-HANDOFF-D1 boundary contract."""
    return {
        "app_id": APP_ID,
        "stage_id": STAGE_ID,
        "contract_version": CONTRACT_VERSION,
        "purpose": PURPOSE,
        "upstream_read_sources": deepcopy(UPSTREAM_READ_SOURCES),
        "planned_output_artifacts": list(PLANNED_OUTPUT_ARTIFACTS),
        "safety_flags": deepcopy(SAFETY_FLAGS),
        "dify_local_assumptions": deepcopy(DIFY_LOCAL_ASSUMPTIONS),
        "forbidden_dify_outputs": list(FORBIDDEN_DIFY_OUTPUTS),
        "allowed_use": [
            "read local FCF reports",
            "read local UI manifests",
            "summarize paper-only findings",
            "explain risk flags without downgrading them",
            "explain reason codes without deleting them",
            "guide manual operator review",
            "guide manual Dify workflow configuration",
        ],
        "forbidden_use": list(FORBIDDEN_DIFY_OUTPUTS),
    }


def validate_dify_ui_handoff_contract(
    contract: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Validate D1 contract safety and completeness."""
    candidate = deepcopy(contract) if contract is not None else get_dify_ui_handoff_contract()
    issues: List[str] = []

    if candidate.get("app_id") != APP_ID:
        issues.append("app_id mismatch")
    if candidate.get("stage_id") != STAGE_ID:
        issues.append("stage_id mismatch")
    if not candidate.get("upstream_read_sources"):
        issues.append("upstream_read_sources must not be empty")
    if not candidate.get("planned_output_artifacts"):
        issues.append("planned_output_artifacts must not be empty")

    flags = candidate.get("safety_flags", {})
    required_true_flags = [
        "paper_only",
        "local_only",
        "read_only",
        "sidecar_only",
        "operator_review_required",
    ]
    required_false_flags = [
        "operator_review_bypass_allowed",
        "core_mutation_allowed",
        "p48_core_expansion_allowed",
        "source_content_mutation_allowed",
        "source_deletion_allowed",
        "source_overwrite_allowed",
        "score_mutation_allowed",
        "reason_code_mutation_allowed",
        "risk_flag_deletion_allowed",
        "risk_flag_downgrade_allowed",
        "real_execution_allowed",
        "trade_action_enabled",
        "buy_button_enabled",
        "sell_button_enabled",
        "order_button_enabled",
        "broker_connection_allowed",
        "exchange_connection_allowed",
        "credential_storage_allowed",
        "api_key_storage_allowed",
        "wallet_private_key_access_allowed",
        "real_account_access_allowed",
        "real_position_access_allowed",
        "automatic_position_sizing_allowed",
        "automatic_portfolio_action_allowed",
        "workflow_execution_allowed",
        "workflow_auto_approval_allowed",
        "llm_trade_instruction_allowed",
        "llm_order_ticket_allowed",
        "llm_profit_guarantee_allowed",
        "future_return_prediction_allowed",
        "tag_created",
        "release_created",
        "deployed",
    ]

    for flag in required_true_flags:
        if flags.get(flag) is not True:
            issues.append(flag + " must be true")

    for flag in required_false_flags:
        if flags.get(flag) is not False:
            issues.append(flag + " must be false")

    assumptions = candidate.get("dify_local_assumptions", {})
    if assumptions.get("manual_configuration_required") is not True:
        issues.append("manual_configuration_required must be true")
    if assumptions.get("automated_dify_api_write_allowed") is not False:
        issues.append("automated_dify_api_write_allowed must be false")
    if assumptions.get("secrets_required_by_contract") is not False:
        issues.append("secrets_required_by_contract must be false")

    forbidden = candidate.get("forbidden_dify_outputs", [])
    for phrase in ["buy instruction", "sell instruction", "order instruction", "api key request"]:
        if phrase not in forbidden:
            issues.append("missing forbidden Dify output: " + phrase)

    return {
        "valid": not issues,
        "issues": issues,
        "app_id": candidate.get("app_id"),
        "stage_id": candidate.get("stage_id"),
        "contract_version": candidate.get("contract_version"),
        "source_count": len(candidate.get("upstream_read_sources", [])),
        "planned_output_count": len(candidate.get("planned_output_artifacts", [])),
    }


def summarize_dify_ui_handoff_contract(contract: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Return a compact D1 summary for reports and future handoffs."""
    candidate = deepcopy(contract) if contract is not None else get_dify_ui_handoff_contract()
    validation = validate_dify_ui_handoff_contract(candidate)
    return {
        "app_id": candidate.get("app_id"),
        "stage_id": candidate.get("stage_id"),
        "valid": validation["valid"],
        "source_count": validation["source_count"],
        "planned_output_count": validation["planned_output_count"],
        "paper_only": candidate["safety_flags"]["paper_only"],
        "local_only": candidate["safety_flags"]["local_only"],
        "read_only": candidate["safety_flags"]["read_only"],
        "operator_review_required": candidate["safety_flags"]["operator_review_required"],
        "manual_dify_configuration_required": candidate["dify_local_assumptions"]["manual_configuration_required"],
        "real_execution_allowed": candidate["safety_flags"]["real_execution_allowed"],
        "trade_action_enabled": candidate["safety_flags"]["trade_action_enabled"],
    }
