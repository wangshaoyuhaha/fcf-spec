"""Read-only rollup packet for ARCHIVE-CORRELATION-D5."""

from __future__ import annotations

from copy import deepcopy
from typing import Any, Dict, Iterable, List, Mapping

from .contract import (
    ALLOWED_ROLLUP_STATUSES,
    ARCHIVE_CORRELATION_ROLLUP_APP_ID,
    CORRELATION_ROLLUP_REQUIRED_LINKS,
)


def build_rollup_packet(
    *,
    trace_summary: Mapping[str, Any],
    artifact_references: Iterable[Mapping[str, Any]],
) -> Dict[str, Any]:
    """Build a read-only correlation rollup packet.

    The packet indexes existing evidence only.
    It must not create evidence, repair links, auto-fill correlation_id,
    generate placeholder review, or auto-pass operator review.
    """

    correlation_id = trace_summary.get("correlation_id")
    if not correlation_id:
        raise ValueError("correlation_id is required")

    rollup_status = trace_summary.get("rollup_status", "UNRESOLVED")
    if rollup_status not in ALLOWED_ROLLUP_STATUSES:
        raise ValueError(f"unsupported rollup_status: {rollup_status}")

    indexed_references: List[Dict[str, Any]] = []
    for reference in artifact_references:
        copied = deepcopy(dict(reference))
        indexed_references.append(
            {
                "link_type": copied.get("link_type"),
                "artifact_id": copied.get("artifact_id"),
                "artifact_path": copied.get("artifact_path"),
                "correlation_id": copied.get("correlation_id"),
                "status": copied.get("status"),
                "source_stage": copied.get("source_stage"),
                "checksum_sha256": copied.get("checksum_sha256"),
                "read_only": True,
                "source_mutation_allowed": False,
                "evidence_backfill_allowed": False,
                "correlation_id_auto_fill_allowed": False,
                "placeholder_generation_allowed": False,
            }
        )

    return {
        "app_id": ARCHIVE_CORRELATION_ROLLUP_APP_ID,
        "packet_type": "correlation_rollup_packet",
        "stage": "D5",
        "correlation_id": correlation_id,
        "rollup_status": rollup_status,
        "required_links": list(CORRELATION_ROLLUP_REQUIRED_LINKS),
        "trace_summary": deepcopy(dict(trace_summary)),
        "artifact_references": indexed_references,
        "artifact_reference_count": len(indexed_references),
        "review_gate": "OPERATOR_REVIEW_REQUIRED",
        "paper_only": True,
        "local_only": True,
        "read_only": True,
        "sidecar_only": True,
        "index_only": True,
        "source_mutation_allowed": False,
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


def classify_rollup_packet(packet: Mapping[str, Any]) -> Dict[str, Any]:
    """Classify a rollup packet without approving, repairing, or mutating."""

    status = packet.get("rollup_status", "UNRESOLVED")

    if status == "COMPLETE":
        packet_action = "QUEUE_OPERATOR_REVIEW"
    elif status == "INCOMPLETE":
        packet_action = "MARK_INCOMPLETE"
    elif status == "STALE":
        packet_action = "MARK_STALE"
    else:
        packet_action = "MARK_UNRESOLVED"

    return {
        "correlation_id": packet.get("correlation_id"),
        "rollup_status": status,
        "packet_action": packet_action,
        "review_gate": "OPERATOR_REVIEW_REQUIRED",
        "operator_review_required": True,
        "auto_pass_allowed": False,
        "auto_repair_allowed": False,
        "evidence_backfill_allowed": False,
        "correlation_id_auto_fill_allowed": False,
        "placeholder_review_allowed": False,
        "source_mutation_allowed": False,
        "read_only": True,
        "sidecar_only": True,
    }
