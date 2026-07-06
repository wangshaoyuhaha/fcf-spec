"""DECISION-AUDIT-D4 paper decision audit review model."""

from __future__ import annotations

from collections import Counter
from copy import deepcopy
from typing import Any, Dict, Iterable, List

from apps.decision_audit_app_1.contract import APP_ID
from apps.decision_audit_app_1.audit_schema import create_decision_audit_event, validate_decision_audit_event


STAGE_ID = "DECISION-AUDIT-D4"
MODEL_VERSION = "1.0.0"


def _clean(value: Any, fallback: str) -> str:
    text = str(value or "").strip()
    return text if text else fallback


def build_decision_audit_review(candidates: Iterable[Dict[str, Any]], source_manifest: Dict[str, Any]) -> Dict[str, Any]:
    candidate_list = list(candidates)
    events: List[Dict[str, Any]] = []

    for index, item in enumerate(candidate_list, start=1):
        candidate_id = _clean(item.get("candidate_id"), "candidate-" + str(index).zfill(3))
        symbol = _clean(item.get("symbol"), candidate_id)
        source_app_id = _clean(item.get("source_app_id"), "RISK-EXPOSURE-APP-1")
        observed_status = _clean(item.get("observed_status"), "REVIEW_REQUIRED")

        event_type = _clean(item.get("audit_event_type"), "OPERATOR_REVIEW_REQUIRED")
        event = create_decision_audit_event(
            audit_event_id="audit-" + candidate_id,
            candidate_id=candidate_id,
            symbol=symbol,
            audit_event_type=event_type,
            source_app_id=source_app_id,
            audit_reason="paper decision audit trail only",
            observed_status=observed_status,
            created_at_utc=str(item.get("created_at_utc") or "2026-07-06T00:00:00+00:00"),
        )
        events.append(event)

    validations = [validate_decision_audit_event(event) for event in events]
    invalid_count = sum(1 for item in validations if not item["valid"])
    event_counts = Counter(event["audit_event_type"] for event in events)

    return {
        "app_id": APP_ID,
        "stage_id": STAGE_ID,
        "model_version": MODEL_VERSION,
        "candidate_count": len(candidate_list),
        "audit_event_count": len(events),
        "audit_event_type_counts": dict(event_counts),
        "audit_events": events,
        "audit_event_validations": validations,
        "invalid_audit_event_count": invalid_count,
        "source_manifest_id": source_manifest.get("stage_id", "DECISION-AUDIT-D2"),
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
    }


def validate_decision_audit_review(review: Dict[str, Any]) -> Dict[str, Any]:
    candidate = deepcopy(review)
    issues = []

    if candidate.get("app_id") != APP_ID:
        issues.append("app_id mismatch")

    if candidate.get("stage_id") != STAGE_ID:
        issues.append("stage_id mismatch")

    if candidate.get("audit_event_count") != len(candidate.get("audit_events", [])):
        issues.append("audit_event_count must match audit_events")

    if candidate.get("invalid_audit_event_count") != 0:
        issues.append("invalid_audit_event_count must be zero")

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
        "audit_event_count": candidate.get("audit_event_count"),
    }
