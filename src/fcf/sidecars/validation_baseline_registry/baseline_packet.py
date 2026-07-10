"""Validation baseline packet for VALIDATION-BASELINE-D5."""

from __future__ import annotations

from copy import deepcopy
from typing import Any, Dict, Mapping

from .contract import VALIDATION_BASELINE_REGISTRY_APP_ID


def build_validation_baseline_packet(
    *,
    baseline_summary: Mapping[str, Any],
) -> Dict[str, Any]:
    """Build a read-only validation baseline packet."""

    if not isinstance(baseline_summary, Mapping):
        raise ValueError("baseline_summary is required")

    status = baseline_summary.get("summary_status", "UNRESOLVED")
    if status not in ("VERIFIED", "REGISTERED", "INCOMPLETE", "STALE", "UNRESOLVED"):
        status = "UNRESOLVED"

    return {
        "app_id": VALIDATION_BASELINE_REGISTRY_APP_ID,
        "stage": "D5",
        "packet_type": "validation_baseline_registry_packet",
        "baseline_packet_status": status,
        "baseline_summary": deepcopy(dict(baseline_summary)),
        "review_gate": "OPERATOR_REVIEW_REQUIRED",
        "paper_only": True,
        "local_only": True,
        "read_only": True,
        "sidecar_only": True,
        "index_only": True,
        "packet_only": True,
        "validation_result_fabrication_allowed": False,
        "pass_count_fabrication_allowed": False,
        "source_artifact_mutation_allowed": False,
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


def classify_validation_baseline_packet(
    packet: Mapping[str, Any],
) -> Dict[str, Any]:
    """Classify packet state without fabrication, repair, or auto-pass."""

    status = packet.get("baseline_packet_status", "UNRESOLVED")

    if status in ("VERIFIED", "REGISTERED"):
        action = "QUEUE_OPERATOR_REVIEW"
    elif status == "INCOMPLETE":
        action = "MARK_INCOMPLETE"
    elif status == "STALE":
        action = "MARK_STALE"
    else:
        action = "MARK_UNRESOLVED"

    return {
        "stage": "D5",
        "baseline_packet_status": status,
        "packet_action": action,
        "review_gate": "OPERATOR_REVIEW_REQUIRED",
        "operator_review_required": True,
        "auto_pass_allowed": False,
        "auto_repair_allowed": False,
        "validation_result_fabrication_allowed": False,
        "pass_count_fabrication_allowed": False,
        "source_artifact_mutation_allowed": False,
        "evidence_backfill_allowed": False,
        "read_only": True,
        "sidecar_only": True,
    }
