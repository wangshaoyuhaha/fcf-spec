"""WATCHLIST-LIFECYCLE-D6 final workflow handoff and closeout."""

from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from apps.watchlist_lifecycle_app_1.contract import APP_ID
from apps.watchlist_lifecycle_app_1.lifecycle_packet import (
    summarize_watchlist_lifecycle_packet,
    validate_watchlist_lifecycle_packet,
)


STAGE_ID = "WATCHLIST-LIFECYCLE-D6"
HANDOFF_VERSION = "1.0.0"

COMPLETED_STAGES: List[str] = [
    "WATCHLIST-LIFECYCLE-D1",
    "WATCHLIST-LIFECYCLE-D2",
    "WATCHLIST-LIFECYCLE-D3",
    "WATCHLIST-LIFECYCLE-D4",
    "WATCHLIST-LIFECYCLE-D5",
    "WATCHLIST-LIFECYCLE-D6",
]

COMPLETED_OUTPUTS: List[str] = [
    "watchlist_lifecycle_contract",
    "watchlist_lifecycle_source_manifest",
    "entry_review_stale_drop_schema",
    "watchlist_lifecycle_decision_model",
    "watchlist_lifecycle_packet",
    "watchlist_lifecycle_final_handoff",
]


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def build_watchlist_lifecycle_final_handoff(
    packet: Dict[str, Any],
    handoff_id: str,
    generated_at_utc: Optional[str] = None,
) -> Dict[str, Any]:
    packet_validation = validate_watchlist_lifecycle_packet(packet)
    packet_summary = summarize_watchlist_lifecycle_packet(packet)

    return {
        "app_id": APP_ID,
        "stage_id": STAGE_ID,
        "handoff_version": HANDOFF_VERSION,
        "handoff_id": handoff_id,
        "generated_at_utc": generated_at_utc or _utc_now(),
        "completed_stages": list(COMPLETED_STAGES),
        "completed_outputs": list(COMPLETED_OUTPUTS),
        "packet_summary": packet_summary,
        "packet_valid": packet_validation["valid"],
        "packet_issues": packet_validation["issues"],
        "final_closeout_ready": packet_validation["valid"],
        "branch_ready_for_merge_review": packet_validation["valid"],
        "operator_review_required": True,
        "operator_review_bypass_allowed": False,
        "paper_only": True,
        "local_only": True,
        "read_only": True,
        "sidecar_only": True,
        "core_freeze_preserved": True,
        "p48_core_expansion_allowed": False,
        "p1_p47_core_mutation_allowed": False,
        "source_content_mutation_allowed": False,
        "source_deletion_allowed": False,
        "source_overwrite_allowed": False,
        "score_mutation_allowed": False,
        "reason_code_mutation_allowed": False,
        "risk_flag_deletion_allowed": False,
        "trade_action_allowed": False,
        "buy_instruction_allowed": False,
        "sell_instruction_allowed": False,
        "order_ticket_allowed": False,
        "real_execution_allowed": False,
        "broker_connection_allowed": False,
        "exchange_connection_allowed": False,
        "api_key_storage_allowed": False,
        "wallet_private_key_access_allowed": False,
        "real_account_access_allowed": False,
        "real_position_access_allowed": False,
        "position_management_allowed": False,
        "automatic_position_sizing_allowed": False,
        "automatic_portfolio_action_allowed": False,
        "future_return_prediction_allowed": False,
        "guaranteed_performance_claim_allowed": False,
        "tag_allowed": False,
        "release_allowed": False,
        "deploy_allowed": False,
        "next_workflow_step": "Return to architecture review for merge-review decision. Do not auto-merge.",
    }


def build_watchlist_lifecycle_closeout_summary(handoff: Dict[str, Any]) -> Dict[str, Any]:
    candidate = deepcopy(handoff)

    return {
        "app_id": candidate.get("app_id"),
        "stage_id": candidate.get("stage_id"),
        "handoff_id": candidate.get("handoff_id"),
        "completed_stage_count": len(candidate.get("completed_stages", [])),
        "completed_output_count": len(candidate.get("completed_outputs", [])),
        "packet_valid": candidate.get("packet_valid"),
        "final_closeout_ready": candidate.get("final_closeout_ready"),
        "branch_ready_for_merge_review": candidate.get("branch_ready_for_merge_review"),
        "operator_review_required": candidate.get("operator_review_required"),
        "paper_only": candidate.get("paper_only"),
        "local_only": candidate.get("local_only"),
        "read_only": candidate.get("read_only"),
        "sidecar_only": candidate.get("sidecar_only"),
        "core_freeze_preserved": candidate.get("core_freeze_preserved"),
        "trade_action_allowed": candidate.get("trade_action_allowed"),
        "real_execution_allowed": candidate.get("real_execution_allowed"),
        "position_management_allowed": candidate.get("position_management_allowed"),
        "future_return_prediction_allowed": candidate.get("future_return_prediction_allowed"),
        "tag_allowed": candidate.get("tag_allowed"),
        "release_allowed": candidate.get("release_allowed"),
        "deploy_allowed": candidate.get("deploy_allowed"),
        "next_workflow_step": candidate.get("next_workflow_step"),
    }


def validate_watchlist_lifecycle_final_handoff(handoff: Dict[str, Any]) -> Dict[str, Any]:
    candidate = deepcopy(handoff)
    issues: List[str] = []

    if candidate.get("app_id") != APP_ID:
        issues.append("app_id mismatch")

    if candidate.get("stage_id") != STAGE_ID:
        issues.append("stage_id mismatch")

    if not candidate.get("handoff_id"):
        issues.append("handoff_id must not be empty")

    if candidate.get("completed_stages") != COMPLETED_STAGES:
        issues.append("completed_stages mismatch")

    for true_key in [
        "packet_valid",
        "final_closeout_ready",
        "branch_ready_for_merge_review",
        "operator_review_required",
        "paper_only",
        "local_only",
        "read_only",
        "sidecar_only",
        "core_freeze_preserved",
    ]:
        if candidate.get(true_key) is not True:
            issues.append(true_key + " must be true")

    for false_key in [
        "operator_review_bypass_allowed",
        "p48_core_expansion_allowed",
        "p1_p47_core_mutation_allowed",
        "source_content_mutation_allowed",
        "source_deletion_allowed",
        "source_overwrite_allowed",
        "score_mutation_allowed",
        "reason_code_mutation_allowed",
        "risk_flag_deletion_allowed",
        "trade_action_allowed",
        "buy_instruction_allowed",
        "sell_instruction_allowed",
        "order_ticket_allowed",
        "real_execution_allowed",
        "broker_connection_allowed",
        "exchange_connection_allowed",
        "api_key_storage_allowed",
        "wallet_private_key_access_allowed",
        "real_account_access_allowed",
        "real_position_access_allowed",
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
        "handoff_id": candidate.get("handoff_id"),
        "final_closeout_ready": candidate.get("final_closeout_ready"),
        "branch_ready_for_merge_review": candidate.get("branch_ready_for_merge_review"),
    }
