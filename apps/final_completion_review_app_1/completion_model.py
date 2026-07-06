"""FINAL-COMPLETION-REVIEW-D4 completion review model."""

from __future__ import annotations

from collections import Counter
from copy import deepcopy
from typing import Any, Dict, List

from apps.final_completion_review_app_1.contract import APP_ID
from apps.final_completion_review_app_1.completion_schema import (
    create_completion_review_item,
    validate_completion_review_item,
)


STAGE_ID = "FINAL-COMPLETION-REVIEW-D4"
MODEL_VERSION = "1.0.0"


def _completion_state(record: Dict[str, Any]) -> str:
    if str(record.get("status") or "").upper() == "PRESENT":
        return "COMPLETED_PRESENT"
    return "COMPLETED_SOURCE_MISSING"


def build_final_completion_review(source_manifest: Dict[str, Any]) -> Dict[str, Any]:
    source_records = list(source_manifest.get("source_records", []))
    completion_items: List[Dict[str, Any]] = []

    for index, record in enumerate(source_records, start=1):
        app_id = str(record.get("app_id") or "UNKNOWN")
        status = str(record.get("status") or "MISSING")
        state = _completion_state(record)

        item = create_completion_review_item(
            completion_item_id="completion-review-" + str(index).zfill(3),
            source_app_id=app_id,
            completion_state=state,
            completion_reason="paper final completion review only",
            observed_status=status,
            created_at_utc="2026-07-06T00:00:00+00:00",
        )
        completion_items.append(item)

    validations = [validate_completion_review_item(item) for item in completion_items]
    invalid_count = sum(1 for item in validations if not item["valid"])
    state_counts = Counter(item["completion_state"] for item in completion_items)

    return {
        "app_id": APP_ID,
        "stage_id": STAGE_ID,
        "model_version": MODEL_VERSION,
        "completion_item_count": len(completion_items),
        "completion_state_counts": dict(state_counts),
        "completion_items": completion_items,
        "completion_item_validations": validations,
        "invalid_completion_item_count": invalid_count,
        "source_manifest_id": source_manifest.get("stage_id", "FINAL-COMPLETION-REVIEW-D2"),
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
    }


def validate_final_completion_review(review: Dict[str, Any]) -> Dict[str, Any]:
    candidate = deepcopy(review)
    issues = []

    if candidate.get("app_id") != APP_ID:
        issues.append("app_id mismatch")

    if candidate.get("stage_id") != STAGE_ID:
        issues.append("stage_id mismatch")

    if candidate.get("completion_item_count") != len(candidate.get("completion_items", [])):
        issues.append("completion_item_count must match completion_items")

    if candidate.get("invalid_completion_item_count") != 0:
        issues.append("invalid_completion_item_count must be zero")

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
        "completion_item_count": candidate.get("completion_item_count"),
    }
