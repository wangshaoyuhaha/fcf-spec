"""Registry packet for ARTIFACT-LIFECYCLE-D5."""

from __future__ import annotations

from copy import deepcopy
from typing import Any, Dict, Mapping

from .contract import ARTIFACT_LIFECYCLE_REGISTRY_APP_ID


def build_lifecycle_registry_packet(
    *,
    registry_summary: Mapping[str, Any],
) -> Dict[str, Any]:
    """Build a read-only lifecycle registry packet."""

    if not isinstance(registry_summary, Mapping):
        raise ValueError("registry_summary is required")

    status = registry_summary.get("registry_summary_status", "UNRESOLVED")
    if status not in ("OBSERVED", "INCOMPLETE", "STALE", "UNRESOLVED"):
        status = "UNRESOLVED"

    return {
        "app_id": ARTIFACT_LIFECYCLE_REGISTRY_APP_ID,
        "stage": "D5",
        "packet_type": "artifact_lifecycle_registry_packet",
        "registry_packet_status": status,
        "registry_summary": deepcopy(dict(registry_summary)),
        "review_gate": "OPERATOR_REVIEW_REQUIRED",
        "paper_only": True,
        "local_only": True,
        "read_only": True,
        "sidecar_only": True,
        "index_only": True,
        "packet_only": True,
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


def classify_lifecycle_registry_packet(
    packet: Mapping[str, Any],
) -> Dict[str, Any]:
    """Classify packet state without approval, repair, or mutation."""

    status = packet.get("registry_packet_status", "UNRESOLVED")

    if status == "OBSERVED":
        action = "QUEUE_OPERATOR_REVIEW"
    elif status == "INCOMPLETE":
        action = "MARK_INCOMPLETE"
    elif status == "STALE":
        action = "MARK_STALE"
    else:
        action = "MARK_UNRESOLVED"

    return {
        "stage": "D5",
        "registry_packet_status": status,
        "packet_action": action,
        "review_gate": "OPERATOR_REVIEW_REQUIRED",
        "operator_review_required": True,
        "auto_pass_allowed": False,
        "auto_repair_allowed": False,
        "source_artifact_mutation_allowed": False,
        "artifact_status_auto_repair_allowed": False,
        "transition_applied": False,
        "evidence_backfill_allowed": False,
        "read_only": True,
        "sidecar_only": True,
    }
