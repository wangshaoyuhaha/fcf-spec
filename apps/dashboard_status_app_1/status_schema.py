"""DASHBOARD-STATUS-D3 paper dashboard status schema."""

from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from apps.dashboard_status_app_1.contract import APP_ID


STAGE_ID = "DASHBOARD-STATUS-D3"
SCHEMA_VERSION = "1.0.0"

STATUS_LEVELS: List[str] = [
    "PRESENT",
    "MISSING",
    "REVIEW_REQUIRED",
    "BLOCKED",
]


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def create_dashboard_status_item(
    status_item_id: str,
    source_app_id: str,
    status_level: str,
    status_reason: str,
    observed_status: str,
    created_at_utc: Optional[str] = None,
) -> Dict[str, Any]:
    return {
        "app_id": APP_ID,
        "stage_id": STAGE_ID,
        "schema_version": SCHEMA_VERSION,
        "status_item_id": status_item_id,
        "source_app_id": source_app_id,
        "status_level": status_level,
        "status_reason": status_reason,
        "observed_status": observed_status,
        "operator_review_required": True,
        "operator_review_bypass_allowed": False,
        "live_trading_dashboard_allowed": False,
        "execution_ui_allowed": False,
        "buy_button_enabled": False,
        "sell_button_enabled": False,
        "order_button_enabled": False,
        "trade_action_allowed": False,
        "real_execution_allowed": False,
        "position_management_allowed": False,
        "automatic_position_sizing_allowed": False,
        "automatic_portfolio_action_allowed": False,
        "future_return_prediction_allowed": False,
        "guaranteed_performance_claim_allowed": False,
        "created_at_utc": created_at_utc or _utc_now(),
    }


def validate_dashboard_status_item(item: Dict[str, Any]) -> Dict[str, Any]:
    candidate = deepcopy(item)
    issues = []

    if candidate.get("app_id") != APP_ID:
        issues.append("app_id mismatch")

    if candidate.get("stage_id") != STAGE_ID:
        issues.append("stage_id mismatch")

    if candidate.get("status_level") not in STATUS_LEVELS:
        issues.append("status_level is not recognized")

    for field in ["status_item_id", "source_app_id", "status_reason", "observed_status"]:
        if not candidate.get(field):
            issues.append(field + " must not be empty")

    if candidate.get("operator_review_required") is not True:
        issues.append("operator_review_required must be true")

    for false_key in [
        "operator_review_bypass_allowed",
        "live_trading_dashboard_allowed",
        "execution_ui_allowed",
        "buy_button_enabled",
        "sell_button_enabled",
        "order_button_enabled",
        "trade_action_allowed",
        "real_execution_allowed",
        "position_management_allowed",
        "automatic_position_sizing_allowed",
        "automatic_portfolio_action_allowed",
        "future_return_prediction_allowed",
        "guaranteed_performance_claim_allowed",
    ]:
        if candidate.get(false_key) is not False:
            issues.append(false_key + " must be false")

    return {
        "valid": not issues,
        "issues": issues,
        "app_id": candidate.get("app_id"),
        "stage_id": candidate.get("stage_id"),
        "status_level": candidate.get("status_level"),
    }
