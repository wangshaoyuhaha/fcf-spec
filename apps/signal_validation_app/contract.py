"""D1 contract for SIGNAL-VALIDATION-APP-1.

The contract defines a paper-only signal validation sidecar boundary.
It validates evidence consistency across existing local outputs without
changing scores, producing trade instructions, or enabling execution.
"""

from __future__ import annotations

from copy import deepcopy
from typing import Any, Dict, List

SIGNAL_VALIDATION_APP_ID = "SIGNAL-VALIDATION-APP-1"
SIGNAL_VALIDATION_STAGE_ID = "SIGNAL-VALIDATION-D1"

SOURCE_LAYERS: List[str] = [
    "DATA-APP-1",
    "STOCK-APP-1",
    "AI-CONTEXT-1",
    "UI-APP-1",
    "OPERATOR-REVIEW-APP-1",
    "REPORT-ARCHIVE-APP-1",
    "DATA-QUALITY-OPS-APP-1",
    "MARKET-SCENARIO-APP-1",
    "BACKTEST-REVIEW-APP-1",
]

READ_ONLY_INPUTS: List[str] = [
    "ranked_watchlist",
    "score_breakdown",
    "reason_codes",
    "risk_flags",
    "data_quality_issue_list",
    "market_scenario_review_packet",
    "backtest_review_packet",
    "operator_review_record",
    "report_archive_manifest",
]

OUTPUT_CONTRACTS: List[str] = [
    "signal_validation_contract",
    "signal_evidence_matrix",
    "signal_conflict_report",
    "signal_validation_status_packet",
    "operator_review_handoff",
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

VALIDATION_STATUS_VALUES: List[str] = [
    "NOT_EVALUATED",
    "EVIDENCE_COMPLETE",
    "EVIDENCE_PARTIAL",
    "CONFLICT_DETECTED",
    "REVIEW_REQUIRED",
    "VALIDATION_BLOCKED",
]


def build_signal_validation_contract() -> Dict[str, Any]:
    """Return the immutable D1 signal validation sidecar contract."""

    return {
        "app_id": SIGNAL_VALIDATION_APP_ID,
        "stage_id": SIGNAL_VALIDATION_STAGE_ID,
        "purpose": "paper_only_signal_evidence_validation",
        "contract_version": "1.0.0",
        "source_layers": deepcopy(SOURCE_LAYERS),
        "read_only_inputs": deepcopy(READ_ONLY_INPUTS),
        "output_contracts": deepcopy(OUTPUT_CONTRACTS),
        "required_boundary": deepcopy(REQUIRED_BOUNDARY),
        "forbidden_capabilities": deepcopy(FORBIDDEN_CAPABILITIES),
        "validation_status_values": deepcopy(VALIDATION_STATUS_VALUES),
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
            "validation_status_is_trade_instruction": False,
            "conflict_report_is_trade_instruction": False,
        },
    }


def summarize_signal_validation_contract() -> Dict[str, Any]:
    """Return a compact summary for reports and handoffs."""

    contract = build_signal_validation_contract()
    return {
        "app_id": contract["app_id"],
        "stage_id": contract["stage_id"],
        "source_layer_count": len(contract["source_layers"]),
        "read_only_input_count": len(contract["read_only_inputs"]),
        "output_contract_count": len(contract["output_contracts"]),
        "required_boundary": deepcopy(contract["required_boundary"]),
        "operator_review_required": contract["operator_boundary"]["operator_review_required"],
        "real_execution_allowed": contract["execution_boundary"]["real_execution_allowed"],
        "p1_p47_core_mutation_allowed": contract["core_boundary"]["p1_p47_core_mutation_allowed"],
        "source_content_mutation_allowed": contract["source_boundary"]["source_content_mutation_allowed"],
    }
