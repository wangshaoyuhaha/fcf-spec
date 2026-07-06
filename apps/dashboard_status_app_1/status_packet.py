"""DASHBOARD-STATUS-D5 paper dashboard status packet."""

from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from apps.dashboard_status_app_1.contract import APP_ID
from apps.dashboard_status_app_1.source_loader import build_dashboard_status_source_manifest, validate_dashboard_status_source_manifest
from apps.dashboard_status_app_1.status_model import build_dashboard_status_review, validate_dashboard_status_review


STAGE_ID = "DASHBOARD-STATUS-D5"
PACKET_VERSION = "1.0.0"


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def build_dashboard_status_packet(
    packet_id: str,
    source_manifest: Optional[Dict[str, Any]] = None,
    generated_at_utc: Optional[str] = None,
) -> Dict[str, Any]:
    manifest = deepcopy(source_manifest) if source_manifest is not None else build_dashboard_status_source_manifest()
    manifest_validation = validate_dashboard_status_source_manifest(manifest)
    review = build_dashboard_status_review(source_manifest=manifest)
    review_validation = validate_dashboard_status_review(review)

    return {
        "app_id": APP_ID,
        "stage_id": STAGE_ID,
        "packet_version": PACKET_VERSION,
        "packet_id": packet_id,
        "generated_at_utc": generated_at_utc or _utc_now(),
        "source_manifest": manifest,
        "source_manifest_valid": manifest_validation["valid"],
        "source_manifest_issues": manifest_validation["issues"],
        "dashboard_status_review": review,
        "dashboard_status_review_valid": review_validation["valid"],
        "dashboard_status_review_issues": review_validation["issues"],
        "status_item_count": review["status_item_count"],
        "status_level_counts": deepcopy(review["status_level_counts"]),
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
        "archive_ready": manifest_validation["valid"] and review_validation["valid"],
    }


def validate_dashboard_status_packet(packet: Dict[str, Any]) -> Dict[str, Any]:
    candidate = deepcopy(packet)
    issues = []

    if candidate.get("app_id") != APP_ID:
        issues.append("app_id mismatch")

    if candidate.get("stage_id") != STAGE_ID:
        issues.append("stage_id mismatch")

    if not candidate.get("packet_id"):
        issues.append("packet_id must not be empty")

    if candidate.get("source_manifest_valid") is not True:
        issues.append("source_manifest_valid must be true")

    if candidate.get("dashboard_status_review_valid") is not True:
        issues.append("dashboard_status_review_valid must be true")

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
        "packet_id": candidate.get("packet_id"),
        "archive_ready": candidate.get("archive_ready"),
    }
