"""RISK-EXPOSURE-D3 paper risk exposure schema."""

from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from apps.risk_exposure_app_1.contract import APP_ID


STAGE_ID = "RISK-EXPOSURE-D3"
SCHEMA_VERSION = "1.0.0"

RISK_EXPOSURE_STATES: List[str] = [
    "PAPER_RISK_REVIEW",
    "CONCENTRATION_RISK_REVIEW",
    "CORRELATION_RISK_REVIEW",
    "SOURCE_GAP_RISK_REVIEW",
    "GOVERNANCE_RISK_REVIEW",
    "DROP_RISK_REVIEW",
]

REQUIRED_RECORD_FIELDS: List[str] = [
    "risk_exposure_record_id",
    "candidate_id",
    "symbol",
    "asset_class",
    "sector",
    "theme",
    "risk_exposure_state",
    "risk_review_reason",
    "observed_risk_flags",
    "operator_review_required",
    "real_risk_management_allowed",
    "position_management_allowed",
    "automatic_position_sizing_allowed",
    "automatic_portfolio_action_allowed",
    "risk_based_rebalance_allowed",
    "trade_action_allowed",
    "real_execution_allowed",
    "future_return_prediction_allowed",
    "created_at_utc",
]


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def create_paper_risk_exposure_record(
    risk_exposure_record_id: str,
    candidate_id: str,
    symbol: str,
    asset_class: str,
    sector: str,
    theme: str,
    risk_exposure_state: str,
    risk_review_reason: str,
    observed_risk_flags: Optional[List[str]] = None,
    created_at_utc: Optional[str] = None,
) -> Dict[str, Any]:
    return {
        "app_id": APP_ID,
        "stage_id": STAGE_ID,
        "schema_version": SCHEMA_VERSION,
        "risk_exposure_record_id": risk_exposure_record_id,
        "candidate_id": candidate_id,
        "symbol": symbol,
        "asset_class": asset_class,
        "sector": sector,
        "theme": theme,
        "risk_exposure_state": risk_exposure_state,
        "risk_review_reason": risk_review_reason,
        "observed_risk_flags": list(observed_risk_flags or []),
        "operator_review_required": True,
        "operator_review_bypass_allowed": False,
        "real_risk_management_allowed": False,
        "position_management_allowed": False,
        "position_size_suggestion_allowed": False,
        "automatic_position_sizing_allowed": False,
        "automatic_portfolio_action_allowed": False,
        "risk_based_rebalance_allowed": False,
        "portfolio_rebalance_allowed": False,
        "trade_action_allowed": False,
        "buy_instruction_allowed": False,
        "sell_instruction_allowed": False,
        "order_ticket_allowed": False,
        "real_execution_allowed": False,
        "future_return_prediction_allowed": False,
        "guaranteed_performance_claim_allowed": False,
        "score_mutation_allowed": False,
        "reason_code_mutation_allowed": False,
        "risk_flag_deletion_allowed": False,
        "risk_flag_downgrade_allowed": False,
        "created_at_utc": created_at_utc or _utc_now(),
    }


def validate_paper_risk_exposure_record(record: Dict[str, Any]) -> Dict[str, Any]:
    candidate = deepcopy(record)
    issues: List[str] = []

    if candidate.get("app_id") != APP_ID:
        issues.append("app_id mismatch")

    if candidate.get("stage_id") != STAGE_ID:
        issues.append("stage_id mismatch")

    for field in REQUIRED_RECORD_FIELDS:
        if field not in candidate:
            issues.append("missing field: " + field)

    if candidate.get("risk_exposure_state") not in RISK_EXPOSURE_STATES:
        issues.append("risk_exposure_state is not recognized")

    if candidate.get("operator_review_required") is not True:
        issues.append("operator_review_required must be true")

    for false_key in [
        "operator_review_bypass_allowed",
        "real_risk_management_allowed",
        "position_management_allowed",
        "position_size_suggestion_allowed",
        "automatic_position_sizing_allowed",
        "automatic_portfolio_action_allowed",
        "risk_based_rebalance_allowed",
        "portfolio_rebalance_allowed",
        "trade_action_allowed",
        "buy_instruction_allowed",
        "sell_instruction_allowed",
        "order_ticket_allowed",
        "real_execution_allowed",
        "future_return_prediction_allowed",
        "guaranteed_performance_claim_allowed",
        "score_mutation_allowed",
        "reason_code_mutation_allowed",
        "risk_flag_deletion_allowed",
        "risk_flag_downgrade_allowed",
    ]:
        if candidate.get(false_key) is not False:
            issues.append(false_key + " must be false")

    return {
        "valid": not issues,
        "issues": issues,
        "app_id": candidate.get("app_id"),
        "stage_id": candidate.get("stage_id"),
        "risk_exposure_state": candidate.get("risk_exposure_state"),
    }
