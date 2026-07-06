"""FINAL-COMPLETION-REVIEW-D3 completion review schema."""

from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from apps.final_completion_review_app_1.contract import APP_ID


STAGE_ID = "FINAL-COMPLETION-REVIEW-D3"
SCHEMA_VERSION = "1.0.0"

COMPLETION_STATES: List[str] = [
    "COMPLETED_PRESENT",
    "COMPLETED_SOURCE_MISSING",
    "REVIEW_REQUIRED",
]


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def create_completion_review_item(
    completion_item_id: str,
    source_app_id: str,
    completion_state: str,
    completion_reason: str,
    observed_status: str,
    created_at_utc: Optional[str] = None,
) -> Dict[str, Any]:
    return {
        "app_id": APP_ID,
        "stage_id": STAGE_ID,
        "schema_version": SCHEMA_VERSION,
        "completion_item_id": completion_item_id,
        "source_app_id": source_app_id,
        "completion_state": completion_state,
        "completion_reason": completion_reason,
        "observed_status": observed_status,
        "operator_review_required": True,
        "operator_review_bypass_allowed": False,
        "auto_completion_approval_allowed": False,
        "workflow_execution_allowed": False,
        "decision_auto_approval_allowed": False,
        "trade_action_allowed": False,
        "buy_instruction_allowed": False,
        "sell_instruction_allowed": False,
        "order_ticket_allowed": False,
        "real_execution_allowed": False,
        "position_management_allowed": False,
        "automatic_position_sizing_allowed": False,
        "automatic_portfolio_action_allowed": False,
        "future_return_prediction_allowed": False,
        "guaranteed_performance_claim_allowed": False,
        "tag_allowed": False,
        "release_allowed": False,
        "deploy_allowed": False,
        "created_at_utc": created_at_utc or _utc_now(),
    }


def validate_completion_review_item(item: Dict[str, Any]) -> Dict[str, Any]:
    candidate = deepcopy(item)
    issues = []

    if candidate.get("app_id") != APP_ID:
        issues.append("app_id mismatch")

    if candidate.get("stage_id") != STAGE_ID:
        issues.append("stage_id mismatch")

    if candidate.get("completion_state") not in COMPLETION_STATES:
        issues.append("completion_state is not recognized")

    for field in ["completion_item_id", "source_app_id", "completion_reason", "observed_status"]:
        if not candidate.get(field):
            issues.append(field + " must not be empty")

    if candidate.get("operator_review_required") is not True:
        issues.append("operator_review_required must be true")

    for false_key in [
        "operator_review_bypass_allowed",
        "auto_completion_approval_allowed",
        "workflow_execution_allowed",
        "decision_auto_approval_allowed",
        "trade_action_allowed",
        "buy_instruction_allowed",
        "sell_instruction_allowed",
        "order_ticket_allowed",
        "real_execution_allowed",
        "position_management_allowed",
        "automatic_position_sizing_allowed",
        "automatic_portfolio_action_allowed",
        "future_return_prediction_allowed",
        "guaranteed_performance_claim_allowed",
        "tag_allowed",
        "release_allowed",
        "deploy_allowed",
    ]:
        if candidate.get(false_key) is not False:
            issues.append(false_key + " must be false")

    return {
        "valid": not issues,
        "issues": issues,
        "app_id": candidate.get("app_id"),
        "stage_id": candidate.get("stage_id"),
        "completion_state": candidate.get("completion_state"),
    }
