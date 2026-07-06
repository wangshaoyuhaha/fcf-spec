"""WATCHLIST-LIFECYCLE-D4 paper-only lifecycle decision model.

This module evaluates local paper watchlist lifecycle status from metadata.
It does not produce trade instructions, position sizing, portfolio actions,
future return predictions, or performance guarantees.
"""

from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
from typing import Any, Dict, Iterable, List, Optional

from apps.watchlist_lifecycle_app_1.contract import APP_ID
from apps.watchlist_lifecycle_app_1.lifecycle_schema import (
    ACTIVE_WATCH,
    DROP_REVIEW,
    ENTRY_REVIEW,
    REVIEW_REQUIRED,
    STALE_REVIEW,
    create_lifecycle_record,
    validate_lifecycle_record,
)


STAGE_ID = "WATCHLIST-LIFECYCLE-D4"
DECISION_MODEL_VERSION = "1.0.0"

BLOCKING_RISK_FLAGS = [
    "SOURCE_MISSING",
    "SOURCE_STALE",
    "GOVERNANCE_BLOCKED",
    "SIGNAL_VALIDATION_FAILED",
    "BACKTEST_REVIEW_BLOCKED",
    "OPERATOR_REVIEW_BLOCKED",
]

DROP_RISK_FLAGS = [
    "DROP_REQUESTED",
    "QUARANTINE_REQUIRED",
    "SYMBOL_REMOVED_FROM_SOURCE",
]


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _normalize_flags(values: Optional[Iterable[str]]) -> List[str]:
    return sorted({str(item).strip().upper() for item in values or [] if str(item).strip()})


def _manifest_source_health(source_manifest: Dict[str, Any]) -> Dict[str, Any]:
    source_record_count = int(source_manifest.get("source_record_count", 0) or 0)
    present_source_count = int(source_manifest.get("present_source_count", 0) or 0)
    missing_source_count = int(source_manifest.get("missing_source_count", 0) or 0)
    missing_upstream_sources = list(source_manifest.get("missing_upstream_sources", []) or [])

    return {
        "source_record_count": source_record_count,
        "present_source_count": present_source_count,
        "missing_source_count": missing_source_count,
        "missing_upstream_sources": missing_upstream_sources,
        "has_any_source_records": source_record_count > 0,
        "has_present_sources": present_source_count > 0,
        "has_missing_sources": missing_source_count > 0 or bool(missing_upstream_sources),
    }


def evaluate_watchlist_lifecycle_state(
    candidate: Dict[str, Any],
    source_manifest: Dict[str, Any],
    previous_state: Optional[str] = None,
) -> Dict[str, Any]:
    """Evaluate the next paper-only lifecycle state for a candidate."""
    candidate_id = str(candidate.get("candidate_id") or candidate.get("symbol") or "UNKNOWN")
    symbol = str(candidate.get("symbol") or candidate_id)
    source_manifest_id = str(source_manifest.get("manifest_id") or source_manifest.get("stage_id") or "D2_MANIFEST")

    risk_flags = _normalize_flags(candidate.get("risk_flags"))
    governance_status = str(candidate.get("governance_status", "REVIEW_REQUIRED")).upper()
    signal_validation_status = str(candidate.get("signal_validation_status", "REVIEW_REQUIRED")).upper()
    operator_review_status = str(candidate.get("operator_review_status", "REVIEW_REQUIRED")).upper()
    source_health = _manifest_source_health(source_manifest)

    decision_reasons: List[str] = []
    selected_state = ENTRY_REVIEW

    if any(flag in risk_flags for flag in DROP_RISK_FLAGS):
        selected_state = DROP_REVIEW
        decision_reasons.append("drop risk flag present")
    elif governance_status in {"BLOCKED", "FAILED"}:
        selected_state = REVIEW_REQUIRED
        decision_reasons.append("governance status requires review")
    elif signal_validation_status in {"FAILED", "BLOCKED"}:
        selected_state = REVIEW_REQUIRED
        decision_reasons.append("signal validation requires review")
    elif operator_review_status in {"BLOCKED", "REJECTED"}:
        selected_state = REVIEW_REQUIRED
        decision_reasons.append("operator review requires review")
    elif "SOURCE_STALE" in risk_flags or source_health["has_missing_sources"]:
        selected_state = STALE_REVIEW
        decision_reasons.append("source context requires stale review")
    elif previous_state in {ENTRY_REVIEW, REVIEW_REQUIRED, STALE_REVIEW}:
        selected_state = ACTIVE_WATCH
        decision_reasons.append("paper candidate may remain under active watch")
    else:
        selected_state = ENTRY_REVIEW
        decision_reasons.append("new paper candidate requires entry review")

    blocking_flags = sorted(set(risk_flags).intersection(BLOCKING_RISK_FLAGS))
    if blocking_flags and selected_state == ACTIVE_WATCH:
        selected_state = REVIEW_REQUIRED
        decision_reasons.append("blocking risk flag prevents active watch")

    lifecycle_record = create_lifecycle_record(
        lifecycle_record_id=str(candidate.get("lifecycle_record_id") or "life-" + candidate_id),
        candidate_id=candidate_id,
        symbol=symbol,
        current_state=selected_state,
        previous_state=previous_state,
        state_reason="; ".join(decision_reasons),
        source_app_ids=candidate.get("source_app_ids") or source_manifest.get("represented_upstream_sources") or [],
        source_manifest_id=source_manifest_id,
        created_at_utc=str(candidate.get("created_at_utc") or _utc_now()),
    )

    validation = validate_lifecycle_record(lifecycle_record)

    return {
        "app_id": APP_ID,
        "stage_id": STAGE_ID,
        "decision_model_version": DECISION_MODEL_VERSION,
        "candidate_id": candidate_id,
        "symbol": symbol,
        "selected_state": selected_state,
        "previous_state": previous_state,
        "decision_reasons": decision_reasons,
        "risk_flags_observed": risk_flags,
        "blocking_risk_flags_observed": blocking_flags,
        "source_health": source_health,
        "lifecycle_record": lifecycle_record,
        "lifecycle_record_valid": validation["valid"],
        "lifecycle_record_issues": validation["issues"],
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
    }


def evaluate_watchlist_lifecycle_batch(
    candidates: Iterable[Dict[str, Any]],
    source_manifest: Dict[str, Any],
) -> Dict[str, Any]:
    """Evaluate a batch of paper-only lifecycle candidates."""
    evaluations = [
        evaluate_watchlist_lifecycle_state(
            candidate=item,
            source_manifest=source_manifest,
            previous_state=item.get("previous_state"),
        )
        for item in candidates
    ]

    state_counts: Dict[str, int] = {}
    for item in evaluations:
        state_counts[item["selected_state"]] = state_counts.get(item["selected_state"], 0) + 1

    return {
        "app_id": APP_ID,
        "stage_id": STAGE_ID,
        "decision_model_version": DECISION_MODEL_VERSION,
        "candidate_count": len(evaluations),
        "state_counts": state_counts,
        "evaluations": evaluations,
        "operator_review_required": True,
        "trade_action_allowed": False,
        "real_execution_allowed": False,
        "position_management_allowed": False,
        "automatic_position_sizing_allowed": False,
        "automatic_portfolio_action_allowed": False,
        "future_return_prediction_allowed": False,
        "guaranteed_performance_claim_allowed": False,
    }


def validate_watchlist_lifecycle_evaluation(evaluation: Dict[str, Any]) -> Dict[str, Any]:
    """Validate one D4 lifecycle evaluation."""
    candidate = deepcopy(evaluation)
    issues: List[str] = []

    if candidate.get("app_id") != APP_ID:
        issues.append("app_id mismatch")

    if candidate.get("stage_id") != STAGE_ID:
        issues.append("stage_id mismatch")

    if candidate.get("lifecycle_record_valid") is not True:
        issues.append("lifecycle record must be valid")

    if not candidate.get("decision_reasons"):
        issues.append("decision_reasons must not be empty")

    for true_key in ["operator_review_required"]:
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
        "selected_state": candidate.get("selected_state"),
    }
