"""WATCHLIST-LIFECYCLE-D3 lifecycle state schema.

This module defines entry, review, stale, and drop schemas for local paper
watchlist lifecycle management. It does not manage positions, size orders,
predict returns, mutate source scores, or create trade instructions.
"""

from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
from typing import Any, Dict, Iterable, List, Optional

from apps.watchlist_lifecycle_app_1.contract import APP_ID


STAGE_ID = "WATCHLIST-LIFECYCLE-D3"
SCHEMA_VERSION = "1.0.0"

ENTRY_REVIEW = "ENTRY_REVIEW"
ACTIVE_WATCH = "ACTIVE_WATCH"
REVIEW_REQUIRED = "REVIEW_REQUIRED"
STALE_REVIEW = "STALE_REVIEW"
DROP_REVIEW = "DROP_REVIEW"

LIFECYCLE_STATES: List[str] = [
    ENTRY_REVIEW,
    ACTIVE_WATCH,
    REVIEW_REQUIRED,
    STALE_REVIEW,
    DROP_REVIEW,
]

TERMINAL_STATES: List[str] = [
    DROP_REVIEW,
]

ALLOWED_TRANSITIONS: Dict[str, List[str]] = {
    ENTRY_REVIEW: [ACTIVE_WATCH, REVIEW_REQUIRED, DROP_REVIEW],
    ACTIVE_WATCH: [REVIEW_REQUIRED, STALE_REVIEW, DROP_REVIEW],
    REVIEW_REQUIRED: [ACTIVE_WATCH, STALE_REVIEW, DROP_REVIEW],
    STALE_REVIEW: [REVIEW_REQUIRED, DROP_REVIEW],
    DROP_REVIEW: [],
}

REQUIRED_RECORD_FIELDS: List[str] = [
    "lifecycle_record_id",
    "candidate_id",
    "symbol",
    "current_state",
    "previous_state",
    "state_reason",
    "source_app_ids",
    "source_manifest_id",
    "operator_review_required",
    "operator_review_bypass_allowed",
    "trade_action_allowed",
    "real_execution_allowed",
    "position_management_allowed",
    "automatic_position_sizing_allowed",
    "automatic_portfolio_action_allowed",
    "future_return_prediction_allowed",
    "score_mutation_allowed",
    "reason_code_mutation_allowed",
    "risk_flag_deletion_allowed",
    "created_at_utc",
]


STATE_SCHEMAS: Dict[str, Dict[str, Any]] = {
    ENTRY_REVIEW: {
        "state_id": ENTRY_REVIEW,
        "purpose": "paper candidate entry review before local watchlist observation",
        "required_reason_codes": ["ENTRY_SOURCE_AVAILABLE", "OPERATOR_REVIEW_REQUIRED"],
        "terminal": False,
        "allowed_next_states": ALLOWED_TRANSITIONS[ENTRY_REVIEW],
    },
    ACTIVE_WATCH: {
        "state_id": ACTIVE_WATCH,
        "purpose": "paper-only active observation state",
        "required_reason_codes": ["WATCHLIST_OBSERVATION_ONLY", "OPERATOR_REVIEW_REQUIRED"],
        "terminal": False,
        "allowed_next_states": ALLOWED_TRANSITIONS[ACTIVE_WATCH],
    },
    REVIEW_REQUIRED: {
        "state_id": REVIEW_REQUIRED,
        "purpose": "manual review is required before any further paper workflow step",
        "required_reason_codes": ["MANUAL_REVIEW_REQUIRED", "NO_AUTOMATED_ACTION"],
        "terminal": False,
        "allowed_next_states": ALLOWED_TRANSITIONS[REVIEW_REQUIRED],
    },
    STALE_REVIEW: {
        "state_id": STALE_REVIEW,
        "purpose": "source age or market context requires stale-data review",
        "required_reason_codes": ["STALE_CONTEXT_REVIEW", "NO_AUTOMATED_ACTION"],
        "terminal": False,
        "allowed_next_states": ALLOWED_TRANSITIONS[STALE_REVIEW],
    },
    DROP_REVIEW: {
        "state_id": DROP_REVIEW,
        "purpose": "paper-only review state for local watchlist removal",
        "required_reason_codes": ["DROP_REVIEW_ONLY", "NO_TRADE_ACTION"],
        "terminal": True,
        "allowed_next_states": ALLOWED_TRANSITIONS[DROP_REVIEW],
    },
}


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def get_lifecycle_state_schemas() -> Dict[str, Dict[str, Any]]:
    """Return defensive copies of lifecycle state schemas."""
    return deepcopy(STATE_SCHEMAS)


def is_transition_allowed(previous_state: Optional[str], current_state: str) -> bool:
    """Return whether a paper lifecycle transition is allowed."""
    if current_state not in LIFECYCLE_STATES:
        return False

    if previous_state is None:
        return current_state == ENTRY_REVIEW

    if previous_state not in LIFECYCLE_STATES:
        return False

    return current_state in ALLOWED_TRANSITIONS[previous_state]


def create_lifecycle_record(
    lifecycle_record_id: str,
    candidate_id: str,
    symbol: str,
    current_state: str,
    state_reason: str,
    source_app_ids: Iterable[str],
    source_manifest_id: str,
    previous_state: Optional[str] = None,
    created_at_utc: Optional[str] = None,
) -> Dict[str, Any]:
    """Create a paper-only lifecycle record."""
    source_list = list(source_app_ids)

    return {
        "app_id": APP_ID,
        "stage_id": STAGE_ID,
        "schema_version": SCHEMA_VERSION,
        "lifecycle_record_id": lifecycle_record_id,
        "candidate_id": candidate_id,
        "symbol": symbol,
        "current_state": current_state,
        "previous_state": previous_state,
        "transition_allowed": is_transition_allowed(previous_state, current_state),
        "state_reason": state_reason,
        "source_app_ids": source_list,
        "source_manifest_id": source_manifest_id,
        "operator_review_required": True,
        "operator_review_bypass_allowed": False,
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
        "score_mutation_allowed": False,
        "reason_code_mutation_allowed": False,
        "risk_flag_deletion_allowed": False,
        "source_content_mutation_allowed": False,
        "source_deletion_allowed": False,
        "source_overwrite_allowed": False,
        "created_at_utc": created_at_utc or _utc_now(),
    }


def validate_lifecycle_record(record: Dict[str, Any]) -> Dict[str, Any]:
    """Validate a paper-only lifecycle record."""
    candidate = deepcopy(record)
    issues: List[str] = []

    if candidate.get("app_id") != APP_ID:
        issues.append("app_id mismatch")

    if candidate.get("stage_id") != STAGE_ID:
        issues.append("stage_id mismatch")

    for field in REQUIRED_RECORD_FIELDS:
        if field not in candidate:
            issues.append("missing field: " + field)

    current_state = candidate.get("current_state")
    previous_state = candidate.get("previous_state")

    if current_state not in LIFECYCLE_STATES:
        issues.append("current_state is not recognized")

    if previous_state is not None and previous_state not in LIFECYCLE_STATES:
        issues.append("previous_state is not recognized")

    if not is_transition_allowed(previous_state, current_state):
        issues.append("transition is not allowed")

    if candidate.get("transition_allowed") is not is_transition_allowed(previous_state, current_state):
        issues.append("transition_allowed does not match schema")

    if not candidate.get("source_app_ids"):
        issues.append("source_app_ids must not be empty")

    for true_key in [
        "operator_review_required",
    ]:
        if candidate.get(true_key) is not True:
            issues.append(true_key + " must be true")

    for false_key in [
        "operator_review_bypass_allowed",
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
        "score_mutation_allowed",
        "reason_code_mutation_allowed",
        "risk_flag_deletion_allowed",
        "source_content_mutation_allowed",
        "source_deletion_allowed",
        "source_overwrite_allowed",
    ]:
        if candidate.get(false_key) is not False:
            issues.append(false_key + " must be false")

    return {
        "valid": not issues,
        "issues": issues,
        "app_id": candidate.get("app_id"),
        "stage_id": candidate.get("stage_id"),
        "current_state": current_state,
        "previous_state": previous_state,
    }


def validate_state_schema_catalog(
    schemas: Optional[Dict[str, Dict[str, Any]]] = None,
) -> Dict[str, Any]:
    """Validate the D3 lifecycle schema catalog."""
    candidate = deepcopy(schemas if schemas is not None else STATE_SCHEMAS)
    issues: List[str] = []

    if set(candidate.keys()) != set(LIFECYCLE_STATES):
        issues.append("schema states mismatch")

    for state_id, schema in candidate.items():
        if state_id not in LIFECYCLE_STATES:
            issues.append("unknown schema state: " + state_id)
            continue

        if schema.get("state_id") != state_id:
            issues.append(state_id + " state_id mismatch")

        if schema.get("terminal") is not (state_id in TERMINAL_STATES):
            issues.append(state_id + " terminal flag mismatch")

        expected_next = ALLOWED_TRANSITIONS[state_id]
        if schema.get("allowed_next_states") != expected_next:
            issues.append(state_id + " allowed_next_states mismatch")

        if not schema.get("required_reason_codes"):
            issues.append(state_id + " required_reason_codes must not be empty")

    return {
        "valid": not issues,
        "issues": issues,
        "stage_id": STAGE_ID,
        "schema_count": len(candidate),
    }
