"""Paper-only review packet for governed AI version bundles."""

from __future__ import annotations

import copy
import hashlib
import json
from collections import Counter
from collections.abc import Mapping
from typing import Any

from .compatibility import validate_compatibility_report
from .contract import APP_ID, CONTRACT_VERSION

REVIEW_PACKET_STATUSES = (
    "REVIEW_REQUIRED",
    "ACKNOWLEDGED",
    "ARCHIVE_PENDING",
)

REQUIRED_PACKET_FIELDS = (
    "review_packet_id",
    "review_packet_hash",
    "app_id",
    "contract_version",
    "review_packet_status",
    "source_compatibility_report_id",
    "source_compatibility_report_hash",
    "compatibility_status",
    "compatible_for_paper_review",
    "record_count",
    "registry_entry_ids",
    "selected_versions",
    "finding_count",
    "open_finding_ids",
    "finding_class_summary",
    "severity_summary",
    "highest_severity",
    "compatibility_report_snapshot",
    "human_review_required",
    "operator_review_bypass_allowed",
    "automatic_approval_allowed",
    "automatic_activation_allowed",
    "automatic_promotion_allowed",
    "automatic_rollback_allowed",
    "model_execution_allowed",
    "archive_required",
    "source_mutation_allowed",
    "real_trading_allowed",
    "real_execution_allowed",
)

FORBIDDEN_ACTION_FIELDS = (
    "buy",
    "sell",
    "order",
    "execute",
    "position_size",
    "portfolio_action",
    "trade_instruction",
    "deployment_instruction",
    "activation_instruction",
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


def build_version_governance_review_packet(
    compatibility_report: Mapping[str, Any],
    *,
    review_packet_status: str = "REVIEW_REQUIRED",
) -> dict[str, Any]:
    """Build a deterministic paper-only governance review packet."""
    if not isinstance(compatibility_report, Mapping):
        raise TypeError("compatibility_report_must_be_mapping")

    report_errors = validate_compatibility_report(
        compatibility_report
    )
    if report_errors:
        raise ValueError(
            "invalid_compatibility_report:"
            + ",".join(sorted(report_errors))
        )

    normalized_status = _require_text(
        review_packet_status,
        "review_packet_status",
    )
    if normalized_status not in REVIEW_PACKET_STATUSES:
        raise ValueError(
            f"unsupported_review_packet_status:{normalized_status}"
        )

    report_snapshot = copy.deepcopy(
        dict(compatibility_report)
    )

    findings = report_snapshot.get("findings")
    if not isinstance(findings, list):
        raise ValueError("invalid_findings")

    normalized_findings: list[dict[str, Any]] = []
    finding_ids: list[str] = []

    for finding in findings:
        if not isinstance(finding, Mapping):
            raise ValueError("invalid_finding_record")

        copied = copy.deepcopy(dict(finding))
        finding_id = _require_text(
            copied.get("finding_id"),
            "finding_id",
        )

        normalized_findings.append(copied)
        finding_ids.append(finding_id)

    if len(finding_ids) != len(set(finding_ids)):
        raise ValueError("duplicate_finding_id")

    normalized_findings.sort(
        key=lambda item: str(item["finding_id"])
    )

    open_finding_ids = sorted(
        str(finding["finding_id"])
        for finding in normalized_findings
        if finding.get("finding_status") == "OPEN"
    )

    finding_class_summary = dict(
        sorted(
            Counter(
                str(finding["finding_class"])
                for finding in normalized_findings
            ).items()
        )
    )

    severity_summary = dict(
        sorted(
            Counter(
                str(finding["severity"])
                for finding in normalized_findings
            ).items()
        )
    )

    report_id = _require_text(
        report_snapshot.get("compatibility_report_id"),
        "compatibility_report_id",
    )
    report_hash = _require_text(
        report_snapshot.get("compatibility_report_hash"),
        "compatibility_report_hash",
    )

    registry_entry_ids = report_snapshot.get(
        "registry_entry_ids"
    )
    if not isinstance(registry_entry_ids, list) or not (
        registry_entry_ids
    ):
        raise ValueError("invalid_registry_entry_ids")

    packet_basis = {
        "app_id": APP_ID,
        "contract_version": CONTRACT_VERSION,
        "review_packet_status": normalized_status,
        "source_compatibility_report_id": report_id,
        "source_compatibility_report_hash": report_hash,
        "registry_entry_ids": list(registry_entry_ids),
        "finding_ids": [
            str(finding["finding_id"])
            for finding in normalized_findings
        ],
        "finding_hashes": [
            str(finding["finding_hash"])
            for finding in normalized_findings
        ],
        "finding_class_summary": finding_class_summary,
        "severity_summary": severity_summary,
    }

    packet_hash = _canonical_hash(packet_basis)

    return {
        "review_packet_id": (
            f"version-review-{packet_hash[:20]}"
        ),
        "review_packet_hash": packet_hash,
        "app_id": APP_ID,
        "contract_version": CONTRACT_VERSION,
        "review_packet_status": normalized_status,
        "source_compatibility_report_id": report_id,
        "source_compatibility_report_hash": report_hash,
        "compatibility_status": report_snapshot[
            "compatibility_status"
        ],
        "compatible_for_paper_review": report_snapshot[
            "compatible"
        ],
        "record_count": report_snapshot["record_count"],
        "registry_entry_ids": copy.deepcopy(
            registry_entry_ids
        ),
        "selected_versions": copy.deepcopy(
            report_snapshot["selected_versions"]
        ),
        "finding_count": len(normalized_findings),
        "open_finding_ids": open_finding_ids,
        "finding_class_summary": finding_class_summary,
        "severity_summary": severity_summary,
        "highest_severity": report_snapshot[
            "highest_severity"
        ],
        "compatibility_report_snapshot": report_snapshot,
        "human_review_required": True,
        "operator_review_bypass_allowed": False,
        "automatic_approval_allowed": False,
        "automatic_activation_allowed": False,
        "automatic_promotion_allowed": False,
        "automatic_rollback_allowed": False,
        "model_execution_allowed": False,
        "archive_required": True,
        "source_mutation_allowed": False,
        "real_trading_allowed": False,
        "real_execution_allowed": False,
    }


def validate_version_governance_review_packet(
    packet: Mapping[str, Any],
) -> list[str]:
    """Validate a version governance review packet."""
    if not isinstance(packet, Mapping):
        return ["packet_must_be_mapping"]

    errors: list[str] = []

    for field in REQUIRED_PACKET_FIELDS:
        if field not in packet:
            errors.append(f"missing_field:{field}")

    if packet.get("app_id") != APP_ID:
        errors.append("invalid_app_id")

    if packet.get("contract_version") != CONTRACT_VERSION:
        errors.append("invalid_contract_version")

    if packet.get(
        "review_packet_status"
    ) not in REVIEW_PACKET_STATUSES:
        errors.append("invalid_review_packet_status")

    snapshot = packet.get("compatibility_report_snapshot")
    if not isinstance(snapshot, Mapping):
        errors.append("invalid_compatibility_report_snapshot")
    else:
        report_errors = validate_compatibility_report(
            snapshot
        )
        if report_errors:
            errors.append(
                "invalid_compatibility_report_snapshot"
            )

        if packet.get("record_count") != snapshot.get(
            "record_count"
        ):
            errors.append("record_count_mismatch")

        if packet.get("finding_count") != snapshot.get(
            "finding_count"
        ):
            errors.append("finding_count_mismatch")

        if packet.get(
            "source_compatibility_report_id"
        ) != snapshot.get("compatibility_report_id"):
            errors.append(
                "compatibility_report_id_mismatch"
            )

        if packet.get(
            "source_compatibility_report_hash"
        ) != snapshot.get("compatibility_report_hash"):
            errors.append(
                "compatibility_report_hash_mismatch"
            )

    finding_count = packet.get("finding_count")
    open_finding_ids = packet.get("open_finding_ids")

    if not isinstance(finding_count, int) or finding_count < 0:
        errors.append("invalid_finding_count")

    if not isinstance(open_finding_ids, list):
        errors.append("invalid_open_finding_ids")

    if packet.get("human_review_required") is not True:
        errors.append("human_review_not_required")

    if packet.get(
        "operator_review_bypass_allowed"
    ) is not False:
        errors.append("operator_review_bypass_not_blocked")

    if packet.get("automatic_approval_allowed") is not False:
        errors.append("automatic_approval_not_blocked")

    if packet.get(
        "automatic_activation_allowed"
    ) is not False:
        errors.append("automatic_activation_not_blocked")

    if packet.get(
        "automatic_promotion_allowed"
    ) is not False:
        errors.append("automatic_promotion_not_blocked")

    if packet.get(
        "automatic_rollback_allowed"
    ) is not False:
        errors.append("automatic_rollback_not_blocked")

    if packet.get("model_execution_allowed") is not False:
        errors.append("model_execution_not_blocked")

    if packet.get("archive_required") is not True:
        errors.append("archive_not_required")

    if packet.get("source_mutation_allowed") is not False:
        errors.append("source_mutation_not_blocked")

    if packet.get("real_trading_allowed") is not False:
        errors.append("real_trading_not_blocked")

    if packet.get("real_execution_allowed") is not False:
        errors.append("real_execution_not_blocked")

    for field in FORBIDDEN_ACTION_FIELDS:
        if field in packet:
            errors.append(f"forbidden_action_field:{field}")

    return errors
