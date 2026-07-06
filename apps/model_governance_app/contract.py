"""D1 contract for MODEL-GOVERNANCE-APP-1.

The contract defines a paper-only model governance sidecar boundary.
It records scoring policy, reason code, risk flag, validation, and review
governance metadata without changing any score or enabling execution.
"""

from __future__ import annotations

from copy import deepcopy
from typing import Any, Dict, List

MODEL_GOVERNANCE_APP_ID = "MODEL-GOVERNANCE-APP-1"
MODEL_GOVERNANCE_STAGE_ID = "MODEL-GOVERNANCE-D1"

SOURCE_LAYERS: List[str] = [
    "DATA-APP-1",
    "STOCK-APP-1",
    "AI-CONTEXT-1",
    "OPERATOR-REVIEW-APP-1",
    "REPORT-ARCHIVE-APP-1",
    "DATA-QUALITY-OPS-APP-1",
    "MARKET-SCENARIO-APP-1",
    "BACKTEST-REVIEW-APP-1",
    "SIGNAL-VALIDATION-APP-1",
]

READ_ONLY_INPUTS: List[str] = [
    "score_breakdown",
    "reason_codes",
    "risk_flags",
    "data_quality_state",
    "confidence_level",
    "signal_validation_report_packet",
    "signal_conflict_report",
    "operator_review_record",
    "archive_manifest",
]

OUTPUT_CONTRACTS: List[str] = [
    "model_governance_contract",
    "model_rule_registry",
    "scoring_policy_snapshot",
    "reason_code_coverage_report",
    "risk_flag_coverage_report",
    "governance_review_packet",
    "final_workflow_handoff",
]

REQUIRED_BOUNDARY: List[str] = [
    "paper_only",
    "local_only",
    "read_only",
    "sidecar_only",
    "operator_review_required",
]

FORBIDDEN_CAPABILITIES: List[str] = [
    "p48_core_expansion",
    "p1_p47_core_mutation",
    "score_mutation",
    "reason_code_mutation",
    "risk_flag_deletion",
    "source_content_mutation",
    "source_deletion",
    "source_overwrite",
    "real_trading",
    "real_execution",
    "broker_connection",
    "exchange_connection",
    "api_key_storage",
    "wallet_private_key_access",
    "real_account_access",
    "real_position_access",
    "buy_button",
    "sell_button",
    "order_button",
    "automatic_position_sizing",
    "automatic_portfolio_action",
    "future_return_prediction",
    "guaranteed_performance_claim",
    "tag_creation",
    "release_creation",
    "deploy_action",
]


def build_model_governance_contract() -> Dict[str, Any]:
    """Return the immutable D1 model governance sidecar contract."""

    return {
        "app_id": MODEL_GOVERNANCE_APP_ID,
        "stage_id": MODEL_GOVERNANCE_STAGE_ID,
        "purpose": "paper_only_model_rule_governance",
        "contract_version": "1.0.0",
        "source_layers": deepcopy(SOURCE_LAYERS),
        "read_only_inputs": deepcopy(READ_ONLY_INPUTS),
        "output_contracts": deepcopy(OUTPUT_CONTRACTS),
        "required_boundary": deepcopy(REQUIRED_BOUNDARY),
        "forbidden_capabilities": deepcopy(FORBIDDEN_CAPABILITIES),
        "governance_scope": {
            "scoring_policy_snapshot_allowed": True,
            "model_rule_registry_allowed": True,
            "reason_code_coverage_allowed": True,
            "risk_flag_coverage_allowed": True,
            "governance_review_packet_allowed": True,
            "score_mutation_allowed": False,
            "reason_code_mutation_allowed": False,
            "risk_flag_deletion_allowed": False,
        },
        "core_boundary": {
            "p1_p47_core_mutation_allowed": False,
            "p48_core_expansion_allowed": False,
            "core_imports_sidecar": False,
            "sidecar_imports_core_for_mutation": False,
        },
        "source_boundary": {
            "source_content_mutation_allowed": False,
            "source_deletion_allowed": False,
            "source_overwrite_allowed": False,
            "source_loader_mode": "metadata_and_payload_read_only",
        },
        "execution_boundary": {
            "real_trading_allowed": False,
            "real_execution_allowed": False,
            "broker_connection_allowed": False,
            "exchange_connection_allowed": False,
            "credential_storage_allowed": False,
            "wallet_private_key_access_allowed": False,
            "real_account_access_allowed": False,
            "real_position_access_allowed": False,
            "trade_action_enabled": False,
            "buy_button_enabled": False,
            "sell_button_enabled": False,
            "order_button_enabled": False,
            "automatic_position_sizing_allowed": False,
            "automatic_portfolio_action_allowed": False,
        },
        "claim_boundary": {
            "future_return_prediction_allowed": False,
            "guaranteed_performance_claim_allowed": False,
            "profit_guarantee_allowed": False,
        },
        "operator_boundary": {
            "operator_review_required": True,
            "operator_review_bypass_allowed": False,
            "governance_status_is_trade_instruction": False,
            "model_rule_registry_is_trade_instruction": False,
        },
    }


def summarize_model_governance_contract() -> Dict[str, Any]:
    """Return a compact D1 summary for handoffs and reports."""

    contract = build_model_governance_contract()
    return {
        "app_id": contract["app_id"],
        "stage_id": contract["stage_id"],
        "source_layer_count": len(contract["source_layers"]),
        "read_only_input_count": len(contract["read_only_inputs"]),
        "output_contract_count": len(contract["output_contracts"]),
        "operator_review_required": contract["operator_boundary"]["operator_review_required"],
        "score_mutation_allowed": contract["governance_scope"]["score_mutation_allowed"],
        "risk_flag_deletion_allowed": contract["governance_scope"]["risk_flag_deletion_allowed"],
        "real_execution_allowed": contract["execution_boundary"]["real_execution_allowed"],
        "p1_p47_core_mutation_allowed": contract["core_boundary"]["p1_p47_core_mutation_allowed"],
        "source_content_mutation_allowed": contract["source_boundary"]["source_content_mutation_allowed"],
    }
