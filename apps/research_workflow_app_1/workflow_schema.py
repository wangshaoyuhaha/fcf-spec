"""RESEARCH-WORKFLOW-D3 paper workflow state schema."""

from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from apps.research_workflow_app_1.contract import APP_ID


STAGE_ID = "RESEARCH-WORKFLOW-D3"
SCHEMA_VERSION = "1.0.0"

WORKFLOW_STATES: List[str] = [
    "SOURCE_REVIEW",
    "ANALYSIS_REVIEW",
    "GOVERNANCE_REVIEW",
    "RISK_REVIEW",
    "DECISION_AUDIT_REVIEW",
    "OPERATOR_REVIEW_REQUIRED",
    "RESEARCH_PACKET_READY",
]


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def create_research_workflow_step(
    workflow_step_id: str,
    source_app_id: str,
    workflow_state: str,
    workflow_reason: str,
    observed_status: str,
    created_at_utc: Optional[str] = None,
) -> Dict[str, Any]:
    return {
        "app_id": APP_ID,
        "stage_id": STAGE_ID,
        "schema_version": SCHEMA_VERSION,
        "workflow_step_id": workflow_step_id,
        "source_app_id": source_app_id,
        "workflow_state": workflow_state,
        "workflow_reason": workflow_reason,
        "observed_status": observed_status,
        "operator_review_required": True,
        "operator_review_bypass_allowed": False,
        "workflow_auto_approval_allowed": False,
        "workflow_execution_allowed": False,
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
        "created_at_utc": created_at_utc or _utc_now(),
    }


def validate_research_workflow_step(step: Dict[str, Any]) -> Dict[str, Any]:
    candidate = deepcopy(step)
    issues = []

    if candidate.get("app_id") != APP_ID:
        issues.append("app_id mismatch")

    if candidate.get("stage_id") != STAGE_ID:
        issues.append("stage_id mismatch")

    if candidate.get("workflow_state") not in WORKFLOW_STATES:
        issues.append("workflow_state is not recognized")

    for field in ["workflow_step_id", "source_app_id", "workflow_reason", "observed_status"]:
        if not candidate.get(field):
            issues.append(field + " must not be empty")

    if candidate.get("operator_review_required") is not True:
        issues.append("operator_review_required must be true")

    for false_key in [
        "operator_review_bypass_allowed",
        "workflow_auto_approval_allowed",
        "workflow_execution_allowed",
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
        "workflow_state": candidate.get("workflow_state"),
    }
