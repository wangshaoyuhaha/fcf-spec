"""PORTFOLIO-REVIEW-D3 paper exposure review schema."""

from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from apps.portfolio_review_app_1.contract import APP_ID


STAGE_ID = "PORTFOLIO-REVIEW-D3"
SCHEMA_VERSION = "1.0.0"

EXPOSURE_REVIEW_STATES: List[str] = [
    "PAPER_EXPOSURE_REVIEW",
    "CONCENTRATION_REVIEW",
    "DIVERSIFICATION_REVIEW",
    "SOURCE_GAP_REVIEW",
    "DROP_REVIEW",
]

REQUIRED_RECORD_FIELDS: List[str] = [
    "exposure_record_id",
    "candidate_id",
    "symbol",
    "asset_class",
    "sector",
    "theme",
    "paper_exposure_state",
    "review_reason",
    "operator_review_required",
    "position_management_allowed",
    "automatic_position_sizing_allowed",
    "automatic_portfolio_action_allowed",
    "trade_action_allowed",
    "real_execution_allowed",
    "future_return_prediction_allowed",
    "created_at_utc",
]


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def create_paper_exposure_record(
    exposure_record_id: str,
    candidate_id: str,
    symbol: str,
    asset_class: str,
    sector: str,
    theme: str,
    paper_exposure_state: str,
    review_reason: str,
    created_at_utc: Optional[str] = None,
) -> Dict[str, Any]:
    return {
        "app_id": APP_ID,
        "stage_id": STAGE_ID,
        "schema_version": SCHEMA_VERSION,
        "exposure_record_id": exposure_record_id,
        "candidate_id": candidate_id,
        "symbol": symbol,
        "asset_class": asset_class,
        "sector": sector,
        "theme": theme,
        "paper_exposure_state": paper_exposure_state,
        "review_reason": review_reason,
        "operator_review_required": True,
        "operator_review_bypass_allowed": False,
        "position_management_allowed": False,
        "position_size_suggestion_allowed": False,
        "automatic_position_sizing_allowed": False,
        "automatic_portfolio_action_allowed": False,
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
        "created_at_utc": created_at_utc or _utc_now(),
    }


def validate_paper_exposure_record(record: Dict[str, Any]) -> Dict[str, Any]:
    candidate = deepcopy(record)
    issues: List[str] = []

    if candidate.get("app_id") != APP_ID:
        issues.append("app_id mismatch")

    if candidate.get("stage_id") != STAGE_ID:
        issues.append("stage_id mismatch")

    for field in REQUIRED_RECORD_FIELDS:
        if field not in candidate:
            issues.append("missing field: " + field)

    if candidate.get("paper_exposure_state") not in EXPOSURE_REVIEW_STATES:
        issues.append("paper_exposure_state is not recognized")

    if candidate.get("operator_review_required") is not True:
        issues.append("operator_review_required must be true")

    for false_key in [
        "operator_review_bypass_allowed",
        "position_management_allowed",
        "position_size_suggestion_allowed",
        "automatic_position_sizing_allowed",
        "automatic_portfolio_action_allowed",
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
    ]:
        if candidate.get(false_key) is not False:
            issues.append(false_key + " must be false")

    return {
        "valid": not issues,
        "issues": issues,
        "app_id": candidate.get("app_id"),
        "stage_id": candidate.get("stage_id"),
        "paper_exposure_state": candidate.get("paper_exposure_state"),
    }
