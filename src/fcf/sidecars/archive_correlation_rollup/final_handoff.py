"""Final handoff for ARCHIVE-CORRELATION-D6."""

from __future__ import annotations

from copy import deepcopy
from typing import Any, Dict, Mapping

from .contract import ARCHIVE_CORRELATION_ROLLUP_APP_ID


def build_final_handoff(
    *,
    rollup_packet: Mapping[str, Any],
) -> Dict[str, Any]:
    """Build final read-only handoff packet."""

    correlation_id = rollup_packet.get("correlation_id")
    if not correlation_id:
        raise ValueError("correlation_id is required")

    rollup_status = rollup_packet.get("rollup_status", "UNRESOLVED")

    return {
        "app_id": ARCHIVE_CORRELATION_ROLLUP_APP_ID,
        "stage": "D6",
        "handoff_type": "archive_correlation_rollup_final_handoff",
        "correlation_id": correlation_id,
        "rollup_status": rollup_status,
        "source_packet": deepcopy(dict(rollup_packet)),
        "final_gate": "OPERATOR_REVIEW_REQUIRED",
        "completion_state": "D6_CLOSEOUT_READY",
        "paper_only": True,
        "local_only": True,
        "read_only": True,
        "sidecar_only": True,
        "index_only": True,
        "source_mutation_allowed": False,
        "core_mutation_allowed": False,
        "p48_core_expansion_allowed": False,
        "evidence_backfill_allowed": False,
        "correlation_id_auto_fill_allowed": False,
        "placeholder_review_allowed": False,
        "auto_pass_allowed": False,
        "operator_review_required": True,
        "ui_dashboard_panel_allowed": False,
        "tag_allowed": False,
        "release_allowed": False,
        "deploy_allowed": False,
        "real_trade_allowed": False,
        "real_execution_allowed": False,
        "broker_connection_allowed": False,
        "exchange_connection_allowed": False,
        "api_key_allowed": False,
        "wallet_private_key_allowed": False,
        "real_account_allowed": False,
        "real_position_allowed": False,
        "buy_sell_order_allowed": False,
        "auto_position_allowed": False,
        "auto_portfolio_action_allowed": False,
    }


def classify_final_handoff(handoff: Mapping[str, Any]) -> Dict[str, Any]:
    """Classify final handoff without executing anything."""

    status = handoff.get("rollup_status", "UNRESOLVED")

    if status == "COMPLETE":
        final_action = "HANDOFF_TO_OPERATOR_REVIEW"
    elif status == "INCOMPLETE":
        final_action = "FINAL_MARK_INCOMPLETE"
    elif status == "STALE":
        final_action = "FINAL_MARK_STALE"
    else:
        final_action = "FINAL_MARK_UNRESOLVED"

    return {
        "correlation_id": handoff.get("correlation_id"),
        "rollup_status": status,
        "final_action": final_action,
        "final_gate": "OPERATOR_REVIEW_REQUIRED",
        "operator_review_required": True,
        "auto_pass_allowed": False,
        "auto_repair_allowed": False,
        "real_execution_allowed": False,
        "read_only": True,
        "sidecar_only": True,
    }
