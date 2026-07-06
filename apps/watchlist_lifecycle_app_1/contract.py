"""WATCHLIST-LIFECYCLE-D1 sidecar boundary contract.

This module is paper-only, local-only, read-only, and sidecar-only.
It defines the contract for local watchlist lifecycle review.
It does not manage positions, produce trade instructions, or connect to real accounts.
"""

from __future__ import annotations

from copy import deepcopy
from typing import Any, Dict, List, Optional


APP_ID = "WATCHLIST-LIFECYCLE-APP-1"
STAGE_ID = "WATCHLIST-LIFECYCLE-D1"
CONTRACT_VERSION = "1.0.0"

UPSTREAM_READ_SOURCES: List[str] = [
    "DATA-APP-1",
    "STOCK-APP-1",
    "AI-CONTEXT-1",
    "UI-APP-1",
    "OPERATOR-REVIEW-APP-1",
    "REPORT-ARCHIVE-APP-1",
    "DATA-QUALITY-OPS-APP-1",
    "MARKET-SCENARIO-APP-1",
    "BACKTEST-REVIEW-APP-1",
    "SIGNAL-VALIDATION-APP-1",
    "MODEL-GOVERNANCE-APP-1",
]

MAY_GENERATE: List[str] = [
    "watchlist_lifecycle_contract",
    "watchlist_lifecycle_source_manifest",
    "watchlist_lifecycle_state_schema",
    "watchlist_lifecycle_packet",
    "watchlist_lifecycle_final_handoff",
]

LIFECYCLE_STATE_CATALOG: List[Dict[str, Any]] = [
    {
        "state_id": "ENTRY_REVIEW",
        "meaning": "Candidate may enter a local paper watchlist after source and governance review.",
        "terminal": False,
        "operator_review_required": True,
        "trade_action_allowed": False,
    },
    {
        "state_id": "ACTIVE_WATCH",
        "meaning": "Candidate remains in local paper observation status.",
        "terminal": False,
        "operator_review_required": True,
        "trade_action_allowed": False,
    },
    {
        "state_id": "REVIEW_REQUIRED",
        "meaning": "Candidate requires manual review before any further paper workflow step.",
        "terminal": False,
        "operator_review_required": True,
        "trade_action_allowed": False,
    },
    {
        "state_id": "STALE_REVIEW",
        "meaning": "Candidate requires stale-data review because source age or context may be outdated.",
        "terminal": False,
        "operator_review_required": True,
        "trade_action_allowed": False,
    },
    {
        "state_id": "DROP_REVIEW",
        "meaning": "Candidate is marked for paper-only removal review from the local watchlist.",
        "terminal": True,
        "operator_review_required": True,
        "trade_action_allowed": False,
    },
]

BOUNDARY_FLAGS: Dict[str, bool] = {
    "paper_only": True,
    "local_only": True,
    "read_only": True,
    "sidecar_only": True,
    "operator_review_required": True,
    "operator_review_bypass_allowed": False,
    "p48_core_expansion_allowed": False,
    "p1_p47_core_mutation_allowed": False,
    "source_content_mutation_allowed": False,
    "source_deletion_allowed": False,
    "source_overwrite_allowed": False,
    "score_mutation_allowed": False,
    "reason_code_mutation_allowed": False,
    "risk_flag_deletion_allowed": False,
    "real_trading_allowed": False,
    "real_execution_allowed": False,
    "broker_connection_allowed": False,
    "exchange_connection_allowed": False,
    "api_key_storage_allowed": False,
    "wallet_private_key_access_allowed": False,
    "real_account_access_allowed": False,
    "real_position_access_allowed": False,
    "buy_button_enabled": False,
    "sell_button_enabled": False,
    "order_button_enabled": False,
    "automatic_position_sizing_allowed": False,
    "automatic_portfolio_action_allowed": False,
    "future_return_prediction_allowed": False,
    "guaranteed_performance_claim_allowed": False,
    "tag_allowed": False,
    "release_allowed": False,
    "deploy_allowed": False,
}

FORBIDDEN_ACTION_SURFACE: List[str] = [
    "buy_instruction",
    "sell_instruction",
    "order_ticket",
    "broker_connection",
    "exchange_connection",
    "real_execution",
    "real_account_access",
    "real_position_access",
    "automatic_position_sizing",
    "automatic_portfolio_action",
    "future_return_prediction",
    "guaranteed_performance_claim",
    "score_mutation",
    "reason_code_mutation",
    "risk_flag_deletion",
    "source_content_mutation",
    "source_deletion",
    "source_overwrite",
    "p48_core_expansion",
    "p1_p47_core_mutation",
]

CONTRACT: Dict[str, Any] = {
    "app_id": APP_ID,
    "stage_id": STAGE_ID,
    "contract_version": CONTRACT_VERSION,
    "purpose": "paper-only local watchlist lifecycle management boundary",
    "upstream_read_sources": UPSTREAM_READ_SOURCES,
    "may_generate": MAY_GENERATE,
    "lifecycle_state_catalog": LIFECYCLE_STATE_CATALOG,
    "boundary_flags": BOUNDARY_FLAGS,
    "forbidden_action_surface": FORBIDDEN_ACTION_SURFACE,
    "not_position_management": True,
    "not_trading_system": True,
    "not_return_prediction_engine": True,
}


def get_watchlist_lifecycle_contract() -> Dict[str, Any]:
    """Return a defensive copy of the D1 contract."""
    return deepcopy(CONTRACT)


def validate_watchlist_lifecycle_contract(
    contract: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Validate the D1 watchlist lifecycle sidecar boundary."""
    candidate = deepcopy(contract if contract is not None else CONTRACT)
    issues: List[str] = []

    if candidate.get("app_id") != APP_ID:
        issues.append("app_id mismatch")

    if candidate.get("stage_id") != STAGE_ID:
        issues.append("stage_id mismatch")

    missing_sources = sorted(set(UPSTREAM_READ_SOURCES) - set(candidate.get("upstream_read_sources", [])))
    if missing_sources:
        issues.append("missing upstream sources: " + ",".join(missing_sources))

    flags = candidate.get("boundary_flags", {})

    for required_true in [
        "paper_only",
        "local_only",
        "read_only",
        "sidecar_only",
        "operator_review_required",
    ]:
        if flags.get(required_true) is not True:
            issues.append(required_true + " must be true")

    for required_false in [
        "operator_review_bypass_allowed",
        "p48_core_expansion_allowed",
        "p1_p47_core_mutation_allowed",
        "source_content_mutation_allowed",
        "source_deletion_allowed",
        "source_overwrite_allowed",
        "score_mutation_allowed",
        "reason_code_mutation_allowed",
        "risk_flag_deletion_allowed",
        "real_trading_allowed",
        "real_execution_allowed",
        "broker_connection_allowed",
        "exchange_connection_allowed",
        "api_key_storage_allowed",
        "wallet_private_key_access_allowed",
        "real_account_access_allowed",
        "real_position_access_allowed",
        "buy_button_enabled",
        "sell_button_enabled",
        "order_button_enabled",
        "automatic_position_sizing_allowed",
        "automatic_portfolio_action_allowed",
        "future_return_prediction_allowed",
        "guaranteed_performance_claim_allowed",
        "tag_allowed",
        "release_allowed",
        "deploy_allowed",
    ]:
        if flags.get(required_false) is not False:
            issues.append(required_false + " must be false")

    for state in candidate.get("lifecycle_state_catalog", []):
        if state.get("operator_review_required") is not True:
            issues.append(state.get("state_id", "unknown") + " must require operator review")
        if state.get("trade_action_allowed") is not False:
            issues.append(state.get("state_id", "unknown") + " must not allow trade action")

    return {
        "valid": not issues,
        "issues": issues,
        "app_id": candidate.get("app_id"),
        "stage_id": candidate.get("stage_id"),
    }
