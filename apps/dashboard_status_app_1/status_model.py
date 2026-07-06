"""DASHBOARD-STATUS-D4 paper dashboard status review model."""

from __future__ import annotations

from collections import Counter
from copy import deepcopy
from typing import Any, Dict, List

from apps.dashboard_status_app_1.contract import APP_ID
from apps.dashboard_status_app_1.status_schema import create_dashboard_status_item, validate_dashboard_status_item


STAGE_ID = "DASHBOARD-STATUS-D4"
MODEL_VERSION = "1.0.0"


def _level_from_record(record: Dict[str, Any]) -> str:
    status = str(record.get("status") or "MISSING").upper()
    if status == "PRESENT":
        return "PRESENT"
    return "MISSING"


def build_dashboard_status_review(source_manifest: Dict[str, Any]) -> Dict[str, Any]:
    source_records = list(source_manifest.get("source_records", []))
    status_items: List[Dict[str, Any]] = []

    for index, record in enumerate(source_records, start=1):
        app_id = str(record.get("app_id") or "UNKNOWN")
        observed_status = str(record.get("status") or "MISSING")
        level = _level_from_record(record)

        item = create_dashboard_status_item(
            status_item_id="dashboard-status-" + str(index).zfill(3),
            source_app_id=app_id,
            status_level=level,
            status_reason="paper dashboard status summary only",
            observed_status=observed_status,
            created_at_utc="2026-07-06T00:00:00+00:00",
        )
        status_items.append(item)

    validations = [validate_dashboard_status_item(item) for item in status_items]
    invalid_count = sum(1 for item in validations if not item["valid"])
    status_counts = Counter(item["status_level"] for item in status_items)

    return {
        "app_id": APP_ID,
        "stage_id": STAGE_ID,
        "model_version": MODEL_VERSION,
        "status_item_count": len(status_items),
        "status_level_counts": dict(status_counts),
        "status_items": status_items,
        "status_item_validations": validations,
        "invalid_status_item_count": invalid_count,
        "source_manifest_id": source_manifest.get("stage_id", "DASHBOARD-STATUS-D2"),
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
    }


def validate_dashboard_status_review(review: Dict[str, Any]) -> Dict[str, Any]:
    candidate = deepcopy(review)
    issues = []

    if candidate.get("app_id") != APP_ID:
        issues.append("app_id mismatch")

    if candidate.get("stage_id") != STAGE_ID:
        issues.append("stage_id mismatch")

    if candidate.get("status_item_count") != len(candidate.get("status_items", [])):
        issues.append("status_item_count must match status_items")

    if candidate.get("invalid_status_item_count") != 0:
        issues.append("invalid_status_item_count must be zero")

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
        "status_item_count": candidate.get("status_item_count"),
    }
