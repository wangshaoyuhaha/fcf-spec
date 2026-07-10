"""Final handoff for ARTIFACT-LIFECYCLE-D6."""

from __future__ import annotations

from copy import deepcopy
from typing import Any, Dict, Mapping

from .contract import ARTIFACT_LIFECYCLE_REGISTRY_APP_ID


def build_lifecycle_final_handoff(
    *,
    registry_packet: Mapping[str, Any],
) -> Dict[str, Any]:
    """Build final read-only lifecycle registry handoff."""

    if not isinstance(registry_packet, Mapping):
        raise ValueError("registry_packet is required")

    status = registry_packet.get("registry_packet_status", "UNRESOLVED")
    if status not in ("OBSERVED", "INCOMPLETE", "STALE", "UNRESOLVED"):
        status = "UNRESOLVED"

    return {
        "app_id": ARTIFACT_LIFECYCLE_REGISTRY_APP_ID,
        "stage": "D6",
        "handoff_type": "artifact_lifecycle_registry_final_handoff",
        "registry_handoff_status": status,
        "source_packet": deepcopy(dict(registry_packet)),
        "final_gate": "OPERATOR_REVIEW_REQUIRED",
        "completion_state": "D6_CLOSEOUT_READY",
        "paper_only": True,
        "local_only": True,
        "read_only": True,
        "sidecar_only": True,
        "index_only": True,
        "handoff_only": True,
        "source_artifact_mutation_allowed": False,
        "artifact_status_auto_repair_allowed": False,
        "transition_applied": False,
        "evidence_backfill_allowed": False,
        "correlation_id_auto_fill_allowed": False,
        "placeholder_review_allowed": False,
        "auto_pass_allowed": False,
        "operator_review_required": True,
        "ui_dashboard_panel_allowed": False,
        "core_mutation_allowed": False,
        "p48_core_expansion_allowed": False,
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


def classify_lifecycle_final_handoff(
    handoff: Mapping[str, Any],
) -> Dict[str, Any]:
    """Classify final handoff without execution, repair, or auto-pass."""

    status = handoff.get("registry_handoff_status", "UNRESOLVED")

    if status == "OBSERVED":
        action = "HANDOFF_TO_OPERATOR_REVIEW"
    elif status == "INCOMPLETE":
        action = "FINAL_MARK_INCOMPLETE"
    elif status == "STALE":
        action = "FINAL_MARK_STALE"
    else:
        action = "FINAL_MARK_UNRESOLVED"

    return {
        "stage": "D6",
        "registry_handoff_status": status,
        "final_action": action,
        "final_gate": "OPERATOR_REVIEW_REQUIRED",
        "operator_review_required": True,
        "auto_pass_allowed": False,
        "auto_repair_allowed": False,
        "source_artifact_mutation_allowed": False,
        "artifact_status_auto_repair_allowed": False,
        "transition_applied": False,
        "evidence_backfill_allowed": False,
        "real_execution_allowed": False,
        "read_only": True,
        "sidecar_only": True,
    }
