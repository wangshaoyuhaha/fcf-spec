"""RISK-EXPOSURE-D5 paper review packet."""

from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
from typing import Any, Dict, Iterable, Optional

from apps.risk_exposure_app_1.contract import APP_ID
from apps.risk_exposure_app_1.review_model import build_paper_risk_exposure_review, validate_paper_risk_exposure_review
from apps.risk_exposure_app_1.source_loader import (
    build_risk_exposure_source_manifest,
    validate_risk_exposure_source_manifest,
)


STAGE_ID = "RISK-EXPOSURE-D5"
PACKET_VERSION = "1.0.0"


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def build_risk_exposure_packet(
    packet_id: str,
    candidates: Iterable[Dict[str, Any]],
    source_manifest: Optional[Dict[str, Any]] = None,
    generated_at_utc: Optional[str] = None,
) -> Dict[str, Any]:
    manifest = deepcopy(source_manifest) if source_manifest is not None else build_risk_exposure_source_manifest()
    manifest_validation = validate_risk_exposure_source_manifest(manifest)
    review = build_paper_risk_exposure_review(candidates=candidates, source_manifest=manifest)
    review_validation = validate_paper_risk_exposure_review(review)

    return {
        "app_id": APP_ID,
        "stage_id": STAGE_ID,
        "packet_version": PACKET_VERSION,
        "packet_id": packet_id,
        "generated_at_utc": generated_at_utc or _utc_now(),
        "source_manifest": manifest,
        "source_manifest_valid": manifest_validation["valid"],
        "source_manifest_issues": manifest_validation["issues"],
        "paper_risk_exposure_review": review,
        "paper_risk_exposure_review_valid": review_validation["valid"],
        "paper_risk_exposure_review_issues": review_validation["issues"],
        "candidate_count": review["candidate_count"],
        "state_counts": deepcopy(review["state_counts"]),
        "operator_review_required": True,
        "operator_review_bypass_allowed": False,
        "paper_only": True,
        "local_only": True,
        "read_only": True,
        "sidecar_only": True,
        "real_risk_management_allowed": False,
        "position_management_allowed": False,
        "position_size_suggestion_allowed": False,
        "automatic_position_sizing_allowed": False,
        "automatic_portfolio_action_allowed": False,
        "risk_based_rebalance_allowed": False,
        "trade_action_allowed": False,
        "buy_instruction_allowed": False,
        "sell_instruction_allowed": False,
        "order_ticket_allowed": False,
        "real_execution_allowed": False,
        "future_return_prediction_allowed": False,
        "guaranteed_performance_claim_allowed": False,
        "risk_flag_deletion_allowed": False,
        "risk_flag_downgrade_allowed": False,
        "archive_ready": manifest_validation["valid"] and review_validation["valid"],
    }


def validate_risk_exposure_packet(packet: Dict[str, Any]) -> Dict[str, Any]:
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

    if candidate.get("paper_risk_exposure_review_valid") is not True:
        issues.append("paper_risk_exposure_review_valid must be true")

    for true_key in ["operator_review_required", "paper_only", "local_only", "read_only", "sidecar_only"]:
        if candidate.get(true_key) is not True:
            issues.append(true_key + " must be true")

    for false_key in [
        "operator_review_bypass_allowed",
        "real_risk_management_allowed",
        "position_management_allowed",
        "position_size_suggestion_allowed",
        "automatic_position_sizing_allowed",
        "automatic_portfolio_action_allowed",
        "risk_based_rebalance_allowed",
        "trade_action_allowed",
        "buy_instruction_allowed",
        "sell_instruction_allowed",
        "order_ticket_allowed",
        "real_execution_allowed",
        "future_return_prediction_allowed",
        "guaranteed_performance_claim_allowed",
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
        "packet_id": candidate.get("packet_id"),
        "archive_ready": candidate.get("archive_ready"),
    }
