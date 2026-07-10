"""Final paper-only handoff for dashboard contradiction findings."""

from __future__ import annotations

import copy
import hashlib
import json
from collections.abc import Mapping
from typing import Any

from .review_packet import validate_contradiction_review_packet

APP_ID = "DASHBOARD-CONTRADICTION-SCANNER-APP-1"
CONTRACT_VERSION = "1.0.0"

HANDOFF_TARGETS = (
    "OPERATOR-REVIEW-APP-1",
    "REPORT-ARCHIVE-APP-1",
    "MODEL-GOVERNANCE-APP-1",
    "DASHBOARD-STATUS-APP-1",
)

REQUIRED_HANDOFF_FIELDS = (
    "handoff_id",
    "handoff_hash",
    "app_id",
    "contract_version",
    "handoff_status",
    "source_packet_id",
    "source_packet_hash",
    "source_scan_report_id",
    "source_scan_report_hash",
    "finding_count",
    "open_finding_ids",
    "severity_summary",
    "contradiction_class_summary",
    "target_consumers",
    "review_packet_snapshot",
    "human_review_required",
    "operator_review_bypass_allowed",
    "automatic_resolution_allowed",
    "archive_required",
    "execution_allowed",
    "source_mutation_allowed",
    "risk_flag_deletion_allowed",
    "risk_flag_downgrade_allowed",
)

FORBIDDEN_ACTION_FIELDS = (
    "buy",
    "sell",
    "order",
    "execute",
    "position_size",
    "portfolio_action",
    "trade_instruction",
)


def _canonical_hash(value: Mapping[str, Any]) -> str:
    encoded = json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
        default=str,
    ).encode("ascii")
    return hashlib.sha256(encoded).hexdigest()


def _require_text(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"missing_or_invalid_field:{field}")
    return value.strip()


def build_final_handoff(
    review_packet: Mapping[str, Any],
) -> dict[str, Any]:
    """Build the immutable final governance handoff."""
    if not isinstance(review_packet, Mapping):
        raise TypeError("review_packet_must_be_mapping")

    packet_errors = validate_contradiction_review_packet(
        review_packet
    )
    if packet_errors:
        raise ValueError(
            "invalid_review_packet:"
            + ",".join(sorted(packet_errors))
        )

    packet_snapshot = copy.deepcopy(dict(review_packet))

    packet_id = _require_text(
        packet_snapshot.get("packet_id"),
        "packet_id",
    )
    packet_hash = _require_text(
        packet_snapshot.get("packet_hash"),
        "packet_hash",
    )
    scan_report_id = _require_text(
        packet_snapshot.get("source_scan_report_id"),
        "source_scan_report_id",
    )
    scan_report_hash = _require_text(
        packet_snapshot.get("source_scan_report_hash"),
        "source_scan_report_hash",
    )

    handoff_basis = {
        "app_id": APP_ID,
        "contract_version": CONTRACT_VERSION,
        "source_packet_id": packet_id,
        "source_packet_hash": packet_hash,
        "source_scan_report_id": scan_report_id,
        "source_scan_report_hash": scan_report_hash,
        "finding_count": packet_snapshot["finding_count"],
        "open_finding_ids": packet_snapshot["open_finding_ids"],
        "target_consumers": list(HANDOFF_TARGETS),
    }
    handoff_hash = _canonical_hash(handoff_basis)

    return {
        "handoff_id": f"contradiction-handoff-{handoff_hash[:20]}",
        "handoff_hash": handoff_hash,
        "app_id": APP_ID,
        "contract_version": CONTRACT_VERSION,
        "handoff_status": "WAITING_FOR_OPERATOR_REVIEW",
        "source_packet_id": packet_id,
        "source_packet_hash": packet_hash,
        "source_scan_report_id": scan_report_id,
        "source_scan_report_hash": scan_report_hash,
        "finding_count": packet_snapshot["finding_count"],
        "open_finding_ids": copy.deepcopy(
            packet_snapshot["open_finding_ids"]
        ),
        "severity_summary": copy.deepcopy(
            packet_snapshot["severity_summary"]
        ),
        "contradiction_class_summary": copy.deepcopy(
            packet_snapshot["contradiction_class_summary"]
        ),
        "target_consumers": list(HANDOFF_TARGETS),
        "review_packet_snapshot": packet_snapshot,
        "human_review_required": True,
        "operator_review_bypass_allowed": False,
        "automatic_resolution_allowed": False,
        "archive_required": True,
        "execution_allowed": False,
        "source_mutation_allowed": False,
        "risk_flag_deletion_allowed": False,
        "risk_flag_downgrade_allowed": False,
        "core_mutation_allowed": False,
        "p48_core_expansion_allowed": False,
        "real_trading_allowed": False,
        "real_execution_allowed": False,
    }


def validate_final_handoff(
    handoff: Mapping[str, Any],
) -> list[str]:
    """Validate a final handoff without changing it."""
    if not isinstance(handoff, Mapping):
        return ["handoff_must_be_mapping"]

    errors: list[str] = []

    for field in REQUIRED_HANDOFF_FIELDS:
        if field not in handoff:
            errors.append(f"missing_field:{field}")

    if handoff.get("app_id") != APP_ID:
        errors.append("invalid_app_id")

    if handoff.get("contract_version") != CONTRACT_VERSION:
        errors.append("invalid_contract_version")

    if handoff.get("handoff_status") != (
        "WAITING_FOR_OPERATOR_REVIEW"
    ):
        errors.append("invalid_handoff_status")

    targets = handoff.get("target_consumers")
    if targets != list(HANDOFF_TARGETS):
        errors.append("invalid_target_consumers")

    snapshot = handoff.get("review_packet_snapshot")
    if not isinstance(snapshot, Mapping):
        errors.append("invalid_review_packet_snapshot")
    else:
        packet_errors = validate_contradiction_review_packet(
            snapshot
        )
        if packet_errors:
            errors.append("invalid_review_packet_snapshot")

        if handoff.get("finding_count") != snapshot.get(
            "finding_count"
        ):
            errors.append("finding_count_mismatch")

    if handoff.get("human_review_required") is not True:
        errors.append("human_review_not_required")

    if handoff.get("operator_review_bypass_allowed") is not False:
        errors.append("operator_review_bypass_not_blocked")

    if handoff.get("automatic_resolution_allowed") is not False:
        errors.append("automatic_resolution_not_blocked")

    if handoff.get("archive_required") is not True:
        errors.append("archive_not_required")

    if handoff.get("execution_allowed") is not False:
        errors.append("execution_not_blocked")

    if handoff.get("source_mutation_allowed") is not False:
        errors.append("source_mutation_not_blocked")

    if handoff.get("risk_flag_deletion_allowed") is not False:
        errors.append("risk_flag_deletion_not_blocked")

    if handoff.get("risk_flag_downgrade_allowed") is not False:
        errors.append("risk_flag_downgrade_not_blocked")

    if handoff.get("core_mutation_allowed") is not False:
        errors.append("core_mutation_not_blocked")

    if handoff.get("p48_core_expansion_allowed") is not False:
        errors.append("p48_core_expansion_not_blocked")

    if handoff.get("real_trading_allowed") is not False:
        errors.append("real_trading_not_blocked")

    if handoff.get("real_execution_allowed") is not False:
        errors.append("real_execution_not_blocked")

    for field in FORBIDDEN_ACTION_FIELDS:
        if field in handoff:
            errors.append(f"forbidden_action_field:{field}")

    return errors
