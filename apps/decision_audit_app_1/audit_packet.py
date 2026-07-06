"""DECISION-AUDIT-D5 paper audit packet."""

from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
from typing import Any, Dict, Iterable, Optional

from apps.decision_audit_app_1.contract import APP_ID
from apps.decision_audit_app_1.audit_model import build_decision_audit_review, validate_decision_audit_review
from apps.decision_audit_app_1.source_loader import build_decision_audit_source_manifest, validate_decision_audit_source_manifest


STAGE_ID = "DECISION-AUDIT-D5"
PACKET_VERSION = "1.0.0"


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def build_decision_audit_packet(
    packet_id: str,
    candidates: Iterable[Dict[str, Any]],
    source_manifest: Optional[Dict[str, Any]] = None,
    generated_at_utc: Optional[str] = None,
) -> Dict[str, Any]:
    manifest = deepcopy(source_manifest) if source_manifest is not None else build_decision_audit_source_manifest()
    manifest_validation = validate_decision_audit_source_manifest(manifest)
    review = build_decision_audit_review(candidates=candidates, source_manifest=manifest)
    review_validation = validate_decision_audit_review(review)

    return {
        "app_id": APP_ID,
        "stage_id": STAGE_ID,
        "packet_version": PACKET_VERSION,
        "packet_id": packet_id,
        "generated_at_utc": generated_at_utc or _utc_now(),
        "source_manifest": manifest,
        "source_manifest_valid": manifest_validation["valid"],
        "source_manifest_issues": manifest_validation["issues"],
        "decision_audit_review": review,
        "decision_audit_review_valid": review_validation["valid"],
        "decision_audit_review_issues": review_validation["issues"],
        "candidate_count": review["candidate_count"],
        "audit_event_count": review["audit_event_count"],
        "audit_event_type_counts": deepcopy(review["audit_event_type_counts"]),
        "operator_review_required": True,
        "operator_review_bypass_allowed": False,
        "decision_auto_approval_allowed": False,
        "decision_override_allowed": False,
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
        "archive_ready": manifest_validation["valid"] and review_validation["valid"],
    }


def validate_decision_audit_packet(packet: Dict[str, Any]) -> Dict[str, Any]:
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

    if candidate.get("decision_audit_review_valid") is not True:
        issues.append("decision_audit_review_valid must be true")

    if candidate.get("operator_review_required") is not True:
        issues.append("operator_review_required must be true")

    for false_key in [
        "operator_review_bypass_allowed",
        "decision_auto_approval_allowed",
        "decision_override_allowed",
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
