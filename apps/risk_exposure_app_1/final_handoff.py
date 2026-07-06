"""RISK-EXPOSURE-D6 final handoff."""

from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from apps.risk_exposure_app_1.contract import APP_ID
from apps.risk_exposure_app_1.review_packet import validate_risk_exposure_packet


STAGE_ID = "RISK-EXPOSURE-D6"
HANDOFF_VERSION = "1.0.0"

COMPLETED_STAGES: List[str] = [
    "RISK-EXPOSURE-D1",
    "RISK-EXPOSURE-D2",
    "RISK-EXPOSURE-D3",
    "RISK-EXPOSURE-D4",
    "RISK-EXPOSURE-D5",
    "RISK-EXPOSURE-D6",
]


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def build_risk_exposure_final_handoff(
    packet: Dict[str, Any],
    handoff_id: str,
    generated_at_utc: Optional[str] = None,
) -> Dict[str, Any]:
    packet_validation = validate_risk_exposure_packet(packet)

    return {
        "app_id": APP_ID,
        "stage_id": STAGE_ID,
        "handoff_version": HANDOFF_VERSION,
        "handoff_id": handoff_id,
        "generated_at_utc": generated_at_utc or _utc_now(),
        "completed_stages": list(COMPLETED_STAGES),
        "packet_id": packet.get("packet_id"),
        "packet_valid": packet_validation["valid"],
        "packet_issues": packet_validation["issues"],
        "candidate_count": packet.get("candidate_count", 0),
        "state_counts": deepcopy(packet.get("state_counts", {})),
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
        "broker_connection_allowed": False,
        "exchange_connection_allowed": False,
        "api_key_storage_allowed": False,
        "wallet_private_key_access_allowed": False,
        "real_account_access_allowed": False,
        "real_position_access_allowed": False,
        "future_return_prediction_allowed": False,
        "guaranteed_performance_claim_allowed": False,
        "risk_flag_deletion_allowed": False,
        "risk_flag_downgrade_allowed": False,
        "tag_allowed": False,
        "release_allowed": False,
        "deploy_allowed": False,
        "next_workflow_step": "Return to architecture review for merge-review decision. Do not auto-merge.",
    }


def validate_risk_exposure_final_handoff(handoff: Dict[str, Any]) -> Dict[str, Any]:
    candidate = deepcopy(handoff)
    issues = []

    if candidate.get("app_id") != APP_ID:
        issues.append("app_id mismatch")

    if candidate.get("stage_id") != STAGE_ID:
        issues.append("stage_id mismatch")

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
        "broker_connection_allowed",
        "exchange_connection_allowed",
        "api_key_storage_allowed",
        "wallet_private_key_access_allowed",
        "real_account_access_allowed",
        "real_position_access_allowed",
        "future_return_prediction_allowed",
        "guaranteed_performance_claim_allowed",
        "risk_flag_deletion_allowed",
        "risk_flag_downgrade_allowed",
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
    }
