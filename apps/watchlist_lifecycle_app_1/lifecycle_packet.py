"""WATCHLIST-LIFECYCLE-D5 paper-only lifecycle packet.

This module packages source metadata and lifecycle evaluations into a local
paper-only review packet. It does not create trade instructions, position
sizing, portfolio actions, future return predictions, or performance claims.
"""

from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
from typing import Any, Dict, Iterable, List, Optional

from apps.watchlist_lifecycle_app_1.contract import APP_ID
from apps.watchlist_lifecycle_app_1.decision_model import (
    evaluate_watchlist_lifecycle_batch,
    validate_watchlist_lifecycle_evaluation,
)
from apps.watchlist_lifecycle_app_1.source_loader import (
    build_watchlist_lifecycle_source_manifest,
    validate_watchlist_lifecycle_source_manifest,
)


STAGE_ID = "WATCHLIST-LIFECYCLE-D5"
PACKET_VERSION = "1.0.0"


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def build_watchlist_lifecycle_packet(
    packet_id: str,
    candidates: Iterable[Dict[str, Any]],
    source_manifest: Optional[Dict[str, Any]] = None,
    generated_at_utc: Optional[str] = None,
) -> Dict[str, Any]:
    """Build a paper-only local watchlist lifecycle packet."""
    manifest = deepcopy(source_manifest) if source_manifest is not None else build_watchlist_lifecycle_source_manifest()
    manifest_validation = validate_watchlist_lifecycle_source_manifest(manifest)

    batch = evaluate_watchlist_lifecycle_batch(
        candidates=list(candidates),
        source_manifest=manifest,
    )

    evaluations = batch["evaluations"]
    evaluation_validations = [
        validate_watchlist_lifecycle_evaluation(item)
        for item in evaluations
    ]

    invalid_evaluation_count = sum(1 for item in evaluation_validations if not item["valid"])
    selected_states = [item["selected_state"] for item in evaluations]
    candidate_symbols = [item["symbol"] for item in evaluations]

    return {
        "app_id": APP_ID,
        "stage_id": STAGE_ID,
        "packet_version": PACKET_VERSION,
        "packet_id": packet_id,
        "generated_at_utc": generated_at_utc or _utc_now(),
        "source_manifest": manifest,
        "source_manifest_valid": manifest_validation["valid"],
        "source_manifest_issues": manifest_validation["issues"],
        "candidate_count": batch["candidate_count"],
        "candidate_symbols": candidate_symbols,
        "state_counts": batch["state_counts"],
        "selected_states": selected_states,
        "evaluations": evaluations,
        "evaluation_validations": evaluation_validations,
        "invalid_evaluation_count": invalid_evaluation_count,
        "operator_review_required": True,
        "operator_review_bypass_allowed": False,
        "paper_only": True,
        "local_only": True,
        "read_only": True,
        "sidecar_only": True,
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
        "score_mutation_allowed": False,
        "reason_code_mutation_allowed": False,
        "risk_flag_deletion_allowed": False,
        "source_content_mutation_allowed": False,
        "source_deletion_allowed": False,
        "source_overwrite_allowed": False,
        "archive_ready": manifest_validation["valid"] and invalid_evaluation_count == 0,
    }


def summarize_watchlist_lifecycle_packet(packet: Dict[str, Any]) -> Dict[str, Any]:
    """Create a compact paper-only packet summary."""
    candidate = deepcopy(packet)

    return {
        "app_id": candidate.get("app_id"),
        "stage_id": candidate.get("stage_id"),
        "packet_id": candidate.get("packet_id"),
        "candidate_count": candidate.get("candidate_count", 0),
        "state_counts": deepcopy(candidate.get("state_counts", {})),
        "source_manifest_valid": candidate.get("source_manifest_valid"),
        "invalid_evaluation_count": candidate.get("invalid_evaluation_count"),
        "archive_ready": candidate.get("archive_ready"),
        "operator_review_required": candidate.get("operator_review_required"),
        "trade_action_allowed": candidate.get("trade_action_allowed"),
        "real_execution_allowed": candidate.get("real_execution_allowed"),
        "position_management_allowed": candidate.get("position_management_allowed"),
        "future_return_prediction_allowed": candidate.get("future_return_prediction_allowed"),
        "guaranteed_performance_claim_allowed": candidate.get("guaranteed_performance_claim_allowed"),
    }


def validate_watchlist_lifecycle_packet(packet: Dict[str, Any]) -> Dict[str, Any]:
    """Validate a D5 paper-only lifecycle packet."""
    candidate = deepcopy(packet)
    issues: List[str] = []

    if candidate.get("app_id") != APP_ID:
        issues.append("app_id mismatch")

    if candidate.get("stage_id") != STAGE_ID:
        issues.append("stage_id mismatch")

    if not candidate.get("packet_id"):
        issues.append("packet_id must not be empty")

    if candidate.get("source_manifest_valid") is not True:
        issues.append("source_manifest must be valid")

    if candidate.get("invalid_evaluation_count") != 0:
        issues.append("invalid_evaluation_count must be zero")

    if candidate.get("candidate_count") != len(candidate.get("evaluations", [])):
        issues.append("candidate_count must match evaluations")

    for true_key in [
        "operator_review_required",
        "paper_only",
        "local_only",
        "read_only",
        "sidecar_only",
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
        "score_mutation_allowed",
        "reason_code_mutation_allowed",
        "risk_flag_deletion_allowed",
        "source_content_mutation_allowed",
        "source_deletion_allowed",
        "source_overwrite_allowed",
    ]:
        if candidate.get(false_key) is not False:
            issues.append(false_key + " must be false")

    for evaluation in candidate.get("evaluations", []):
        validation = validate_watchlist_lifecycle_evaluation(evaluation)
        if not validation["valid"]:
            issues.append("invalid evaluation: " + ",".join(validation["issues"]))

    return {
        "valid": not issues,
        "issues": issues,
        "app_id": candidate.get("app_id"),
        "stage_id": candidate.get("stage_id"),
        "packet_id": candidate.get("packet_id"),
        "candidate_count": candidate.get("candidate_count"),
        "archive_ready": candidate.get("archive_ready"),
    }
