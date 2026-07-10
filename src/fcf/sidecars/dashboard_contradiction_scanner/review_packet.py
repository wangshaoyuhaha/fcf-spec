"""Paper-only contradiction review packet."""

from __future__ import annotations

import copy
import hashlib
import json
from collections import Counter
from collections.abc import Mapping
from typing import Any

from .finding_schema import validate_contradiction_finding

PACKET_STATUSES = (
    "REVIEW_REQUIRED",
    "ACKNOWLEDGED",
    "ARCHIVE_PENDING",
)

REQUIRED_PACKET_FIELDS = (
    "packet_id",
    "packet_hash",
    "packet_status",
    "source_scan_report_id",
    "source_scan_report_hash",
    "scan_status",
    "finding_count",
    "severity_summary",
    "contradiction_class_summary",
    "open_finding_ids",
    "findings",
    "human_review_required",
    "operator_review_bypass_allowed",
    "automatic_resolution_allowed",
    "archive_required",
    "execution_allowed",
    "source_mutation_allowed",
    "risk_flag_deletion_allowed",
    "risk_flag_downgrade_allowed",
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


def _validate_scan_report(scan_report: Mapping[str, Any]) -> list[dict[str, Any]]:
    if not isinstance(scan_report, Mapping):
        raise TypeError("scan_report_must_be_mapping")

    _require_text(scan_report.get("scan_report_id"), "scan_report_id")
    _require_text(scan_report.get("scan_report_hash"), "scan_report_hash")
    _require_text(scan_report.get("scan_status"), "scan_status")

    findings = scan_report.get("findings")
    if not isinstance(findings, list):
        raise ValueError("invalid_findings")

    finding_count = scan_report.get("finding_count")
    if finding_count != len(findings):
        raise ValueError("finding_count_mismatch")

    normalized: list[dict[str, Any]] = []
    finding_ids: list[str] = []

    for finding in findings:
        if not isinstance(finding, Mapping):
            raise ValueError("invalid_finding_record")

        errors = validate_contradiction_finding(finding)
        if errors:
            raise ValueError(
                "invalid_finding:" + ",".join(sorted(errors))
            )

        copied = copy.deepcopy(dict(finding))
        normalized.append(copied)
        finding_ids.append(str(copied["finding_id"]))

    if len(finding_ids) != len(set(finding_ids)):
        raise ValueError("duplicate_finding_id")

    expected_status = (
        "CONTRADICTIONS_FOUND"
        if normalized
        else "NO_CONTRADICTIONS"
    )
    if scan_report.get("scan_status") != expected_status:
        raise ValueError("scan_status_mismatch")

    normalized.sort(key=lambda item: str(item["finding_id"]))
    return normalized


def build_contradiction_review_packet(
    scan_report: Mapping[str, Any],
    *,
    packet_status: str = "REVIEW_REQUIRED",
) -> dict[str, Any]:
    """Build a deterministic review packet without resolving findings."""
    normalized_status = _require_text(
        packet_status,
        "packet_status",
    )
    if normalized_status not in PACKET_STATUSES:
        raise ValueError(
            f"unsupported_packet_status:{normalized_status}"
        )

    findings = _validate_scan_report(scan_report)

    severity_summary = dict(
        sorted(
            Counter(
                str(finding["severity"])
                for finding in findings
            ).items()
        )
    )
    contradiction_class_summary = dict(
        sorted(
            Counter(
                str(finding["contradiction_class"])
                for finding in findings
            ).items()
        )
    )
    open_finding_ids = sorted(
        str(finding["finding_id"])
        for finding in findings
        if finding["status"] == "OPEN"
    )

    packet_basis = {
        "source_scan_report_id": _require_text(
            scan_report.get("scan_report_id"),
            "scan_report_id",
        ),
        "source_scan_report_hash": _require_text(
            scan_report.get("scan_report_hash"),
            "scan_report_hash",
        ),
        "packet_status": normalized_status,
        "finding_ids": [
            str(finding["finding_id"])
            for finding in findings
        ],
        "finding_hashes": [
            str(finding["finding_hash"])
            for finding in findings
        ],
        "severity_summary": severity_summary,
        "contradiction_class_summary": contradiction_class_summary,
    }
    packet_hash = _canonical_hash(packet_basis)

    return {
        "packet_id": f"contradiction-packet-{packet_hash[:20]}",
        "packet_hash": packet_hash,
        "packet_status": normalized_status,
        "source_scan_report_id": packet_basis[
            "source_scan_report_id"
        ],
        "source_scan_report_hash": packet_basis[
            "source_scan_report_hash"
        ],
        "scan_status": scan_report["scan_status"],
        "finding_count": len(findings),
        "severity_summary": severity_summary,
        "contradiction_class_summary": contradiction_class_summary,
        "open_finding_ids": open_finding_ids,
        "findings": findings,
        "human_review_required": True,
        "operator_review_bypass_allowed": False,
        "automatic_resolution_allowed": False,
        "archive_required": True,
        "execution_allowed": False,
        "source_mutation_allowed": False,
        "risk_flag_deletion_allowed": False,
        "risk_flag_downgrade_allowed": False,
    }


def validate_contradiction_review_packet(
    packet: Mapping[str, Any],
) -> list[str]:
    """Validate the paper-only review packet."""
    if not isinstance(packet, Mapping):
        return ["packet_must_be_mapping"]

    errors: list[str] = []

    for field in REQUIRED_PACKET_FIELDS:
        if field not in packet:
            errors.append(f"missing_field:{field}")

    if packet.get("packet_status") not in PACKET_STATUSES:
        errors.append("invalid_packet_status")

    findings = packet.get("findings")
    if not isinstance(findings, list):
        errors.append("invalid_findings")
        findings = []

    if packet.get("finding_count") != len(findings):
        errors.append("finding_count_mismatch")

    if packet.get("human_review_required") is not True:
        errors.append("human_review_not_required")

    if packet.get("operator_review_bypass_allowed") is not False:
        errors.append("operator_review_bypass_not_blocked")

    if packet.get("automatic_resolution_allowed") is not False:
        errors.append("automatic_resolution_not_blocked")

    if packet.get("archive_required") is not True:
        errors.append("archive_not_required")

    if packet.get("execution_allowed") is not False:
        errors.append("execution_not_blocked")

    if packet.get("source_mutation_allowed") is not False:
        errors.append("source_mutation_not_blocked")

    if packet.get("risk_flag_deletion_allowed") is not False:
        errors.append("risk_flag_deletion_not_blocked")

    if packet.get("risk_flag_downgrade_allowed") is not False:
        errors.append("risk_flag_downgrade_not_blocked")

    return errors
