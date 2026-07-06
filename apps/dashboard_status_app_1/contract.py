"""DASHBOARD-STATUS-APP-1 boundary contract."""

from __future__ import annotations

from copy import deepcopy
from typing import Any, Dict, List, Optional


APP_ID = "DASHBOARD-STATUS-APP-1"
STAGE_ID = "DASHBOARD-STATUS-D1"
CONTRACT_VERSION = "1.0.0"

UPSTREAM_READ_SOURCES: List[str] = [
    "RESEARCH-WORKFLOW-APP-1",
    "DECISION-AUDIT-APP-1",
    "RISK-EXPOSURE-APP-1",
    "PORTFOLIO-REVIEW-APP-1",
    "WATCHLIST-LIFECYCLE-APP-1",
    "MODEL-GOVERNANCE-APP-1",
    "SIGNAL-VALIDATION-APP-1",
    "BACKTEST-REVIEW-APP-1",
    "MARKET-SCENARIO-APP-1",
    "DATA-QUALITY-OPS-APP-1",
    "REPORT-ARCHIVE-APP-1",
    "OPERATOR-REVIEW-APP-1",
    "UI-APP-1",
    "AI-CONTEXT-1",
    "STOCK-APP-1",
    "DATA-APP-1",
]

MAY_GENERATE: List[str] = [
    "dashboard_status_contract",
    "dashboard_status_source_manifest",
    "dashboard_status_schema",
    "dashboard_status_review_model",
    "dashboard_status_packet",
    "dashboard_status_final_handoff",
]

BOUNDARY_FLAGS: Dict[str, bool] = {
    "paper_only": True,
    "local_only": True,
    "read_only": True,
    "sidecar_only": True,
    "operator_review_required": True,
    "operator_review_bypass_allowed": False,
    "live_trading_dashboard_allowed": False,
    "execution_ui_allowed": False,
    "buy_button_enabled": False,
    "sell_button_enabled": False,
    "order_button_enabled": False,
    "trade_action_allowed": False,
    "real_trading_allowed": False,
    "real_execution_allowed": False,
    "broker_connection_allowed": False,
    "exchange_connection_allowed": False,
    "api_key_storage_allowed": False,
    "wallet_private_key_access_allowed": False,
    "real_account_access_allowed": False,
    "real_position_access_allowed": False,
    "position_management_allowed": False,
    "automatic_position_sizing_allowed": False,
    "automatic_portfolio_action_allowed": False,
    "workflow_execution_allowed": False,
    "decision_auto_approval_allowed": False,
    "future_return_prediction_allowed": False,
    "guaranteed_performance_claim_allowed": False,
    "score_mutation_allowed": False,
    "reason_code_mutation_allowed": False,
    "risk_flag_deletion_allowed": False,
    "risk_flag_downgrade_allowed": False,
    "source_content_mutation_allowed": False,
    "source_deletion_allowed": False,
    "source_overwrite_allowed": False,
    "p48_core_expansion_allowed": False,
    "p1_p47_core_mutation_allowed": False,
    "tag_allowed": False,
    "release_allowed": False,
    "deploy_allowed": False,
}

CONTRACT: Dict[str, Any] = {
    "app_id": APP_ID,
    "stage_id": STAGE_ID,
    "contract_version": CONTRACT_VERSION,
    "purpose": "paper-only local dashboard status summary boundary",
    "upstream_read_sources": UPSTREAM_READ_SOURCES,
    "may_generate": MAY_GENERATE,
    "boundary_flags": BOUNDARY_FLAGS,
    "not_live_trading_dashboard": True,
    "not_execution_ui": True,
    "not_trade_instruction_engine": True,
    "not_position_management_system": True,
    "not_return_prediction_engine": True,
}


def get_dashboard_status_contract() -> Dict[str, Any]:
    return deepcopy(CONTRACT)


def validate_dashboard_status_contract(contract: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    candidate = deepcopy(contract if contract is not None else CONTRACT)
    issues: List[str] = []

    if candidate.get("app_id") != APP_ID:
        issues.append("app_id mismatch")

    if candidate.get("stage_id") != STAGE_ID:
        issues.append("stage_id mismatch")

    missing = sorted(set(UPSTREAM_READ_SOURCES) - set(candidate.get("upstream_read_sources", [])))
    if missing:
        issues.append("missing upstream sources: " + ",".join(missing))

    flags = candidate.get("boundary_flags", {})

    for true_key in ["paper_only", "local_only", "read_only", "sidecar_only", "operator_review_required"]:
        if flags.get(true_key) is not True:
            issues.append(true_key + " must be true")

    for false_key in [
        "operator_review_bypass_allowed",
        "live_trading_dashboard_allowed",
        "execution_ui_allowed",
        "buy_button_enabled",
        "sell_button_enabled",
        "order_button_enabled",
        "trade_action_allowed",
        "real_trading_allowed",
        "real_execution_allowed",
        "broker_connection_allowed",
        "exchange_connection_allowed",
        "api_key_storage_allowed",
        "wallet_private_key_access_allowed",
        "real_account_access_allowed",
        "real_position_access_allowed",
        "position_management_allowed",
        "automatic_position_sizing_allowed",
        "automatic_portfolio_action_allowed",
        "workflow_execution_allowed",
        "decision_auto_approval_allowed",
        "future_return_prediction_allowed",
        "guaranteed_performance_claim_allowed",
        "score_mutation_allowed",
        "reason_code_mutation_allowed",
        "risk_flag_deletion_allowed",
        "risk_flag_downgrade_allowed",
        "source_content_mutation_allowed",
        "source_deletion_allowed",
        "source_overwrite_allowed",
        "p48_core_expansion_allowed",
        "p1_p47_core_mutation_allowed",
        "tag_allowed",
        "release_allowed",
        "deploy_allowed",
    ]:
        if flags.get(false_key) is not False:
            issues.append(false_key + " must be false")

    return {
        "valid": not issues,
        "issues": issues,
        "app_id": candidate.get("app_id"),
        "stage_id": candidate.get("stage_id"),
    }
