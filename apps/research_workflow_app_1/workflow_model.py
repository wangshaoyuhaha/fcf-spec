"""RESEARCH-WORKFLOW-D4 paper workflow review model."""

from __future__ import annotations

from collections import Counter
from copy import deepcopy
from typing import Any, Dict, Iterable, List

from apps.research_workflow_app_1.contract import APP_ID
from apps.research_workflow_app_1.workflow_schema import create_research_workflow_step, validate_research_workflow_step


STAGE_ID = "RESEARCH-WORKFLOW-D4"
MODEL_VERSION = "1.0.0"

STATE_BY_SOURCE = {
    "DATA-APP-1": "SOURCE_REVIEW",
    "STOCK-APP-1": "ANALYSIS_REVIEW",
    "AI-CONTEXT-1": "ANALYSIS_REVIEW",
    "UI-APP-1": "OPERATOR_REVIEW_REQUIRED",
    "OPERATOR-REVIEW-APP-1": "OPERATOR_REVIEW_REQUIRED",
    "REPORT-ARCHIVE-APP-1": "RESEARCH_PACKET_READY",
    "DATA-QUALITY-OPS-APP-1": "SOURCE_REVIEW",
    "MARKET-SCENARIO-APP-1": "ANALYSIS_REVIEW",
    "BACKTEST-REVIEW-APP-1": "ANALYSIS_REVIEW",
    "SIGNAL-VALIDATION-APP-1": "GOVERNANCE_REVIEW",
    "MODEL-GOVERNANCE-APP-1": "GOVERNANCE_REVIEW",
    "WATCHLIST-LIFECYCLE-APP-1": "RISK_REVIEW",
    "PORTFOLIO-REVIEW-APP-1": "RISK_REVIEW",
    "RISK-EXPOSURE-APP-1": "RISK_REVIEW",
    "DECISION-AUDIT-APP-1": "DECISION_AUDIT_REVIEW",
}


def build_research_workflow_review(source_manifest: Dict[str, Any]) -> Dict[str, Any]:
    source_records = list(source_manifest.get("source_records", []))
    workflow_steps: List[Dict[str, Any]] = []

    for index, record in enumerate(source_records, start=1):
        app_id = str(record.get("app_id") or "UNKNOWN")
        status = str(record.get("status") or "MISSING")
        state = STATE_BY_SOURCE.get(app_id, "SOURCE_REVIEW")

        step = create_research_workflow_step(
            workflow_step_id="workflow-step-" + str(index).zfill(3),
            source_app_id=app_id,
            workflow_state=state,
            workflow_reason="paper research workflow review only",
            observed_status=status,
            created_at_utc="2026-07-06T00:00:00+00:00",
        )
        workflow_steps.append(step)

    validations = [validate_research_workflow_step(step) for step in workflow_steps]
    invalid_count = sum(1 for item in validations if not item["valid"])
    state_counts = Counter(step["workflow_state"] for step in workflow_steps)

    return {
        "app_id": APP_ID,
        "stage_id": STAGE_ID,
        "model_version": MODEL_VERSION,
        "workflow_step_count": len(workflow_steps),
        "workflow_state_counts": dict(state_counts),
        "workflow_steps": workflow_steps,
        "workflow_step_validations": validations,
        "invalid_workflow_step_count": invalid_count,
        "source_manifest_id": source_manifest.get("stage_id", "RESEARCH-WORKFLOW-D2"),
        "operator_review_required": True,
        "operator_review_bypass_allowed": False,
        "workflow_auto_approval_allowed": False,
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
    }


def validate_research_workflow_review(review: Dict[str, Any]) -> Dict[str, Any]:
    candidate = deepcopy(review)
    issues = []

    if candidate.get("app_id") != APP_ID:
        issues.append("app_id mismatch")

    if candidate.get("stage_id") != STAGE_ID:
        issues.append("stage_id mismatch")

    if candidate.get("workflow_step_count") != len(candidate.get("workflow_steps", [])):
        issues.append("workflow_step_count must match workflow_steps")

    if candidate.get("invalid_workflow_step_count") != 0:
        issues.append("invalid_workflow_step_count must be zero")

    if candidate.get("operator_review_required") is not True:
        issues.append("operator_review_required must be true")

    for false_key in [
        "operator_review_bypass_allowed",
        "workflow_auto_approval_allowed",
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
    ]:
        if candidate.get(false_key) is not False:
            issues.append(false_key + " must be false")

    return {
        "valid": not issues,
        "issues": issues,
        "app_id": candidate.get("app_id"),
        "stage_id": candidate.get("stage_id"),
        "workflow_step_count": candidate.get("workflow_step_count"),
    }
