"""Compatibility and conflict checks for governed AI versions."""

from __future__ import annotations

import copy
import hashlib
import json
from collections import Counter, defaultdict
from collections.abc import Mapping, Sequence
from typing import Any

from .contract import APP_ID, CONTRACT_VERSION, VERSION_KINDS
from .version_record import validate_version_record

REQUIRED_BUNDLE_KINDS = (
    "PROMPT",
    "MODEL",
    "CONTRACT",
    "REGISTRY",
)

VERSION_FIELD_BY_KIND = {
    "PROMPT": "prompt_version",
    "MODEL": "model_version",
    "CONTRACT": "contract_version",
    "REGISTRY": "registry_version",
}

COMPATIBILITY_FINDING_CLASSES = (
    "MISSING_REQUIRED_KIND",
    "DUPLICATE_KIND_SELECTION",
    "BLOCKED_VERSION_SELECTED",
    "DEPRECATED_VERSION_SELECTED",
    "ARCHIVED_VERSION_SELECTED",
    "REVIEW_REQUIRED_VERSION_SELECTED",
    "CONTRACT_REFERENCE_MISMATCH",
    "REGISTRY_REFERENCE_MISMATCH",
    "VALIDATION_BASELINE_MISMATCH",
    "CORRELATION_ID_MISMATCH",
    "DUPLICATE_CONTENT_DIFFERENT_VERSION",
)

SEVERITY_RANK = {
    "LOW": 1,
    "MEDIUM": 2,
    "HIGH": 3,
    "CRITICAL": 4,
}

REQUIRED_REPORT_FIELDS = (
    "compatibility_report_id",
    "compatibility_report_hash",
    "app_id",
    "contract_version",
    "compatibility_status",
    "compatible",
    "record_count",
    "registry_entry_ids",
    "selected_versions",
    "kind_summary",
    "status_summary",
    "finding_count",
    "findings",
    "highest_severity",
    "human_review_required",
    "archive_required",
    "model_execution_allowed",
    "automatic_activation_allowed",
    "automatic_promotion_allowed",
    "automatic_rollback_allowed",
    "source_mutation_allowed",
    "real_trading_allowed",
    "real_execution_allowed",
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


def _version_key(record: Mapping[str, Any]) -> str:
    kind = str(record["record_kind"])
    version_field = VERSION_FIELD_BY_KIND[kind]
    return f"{kind}:{record[version_field]}"


def _build_finding(
    *,
    finding_class: str,
    severity: str,
    registry_entry_ids: Sequence[str],
    evidence: Mapping[str, Any],
    summary: str,
) -> dict[str, Any]:
    finding_basis = {
        "finding_class": finding_class,
        "severity": severity,
        "registry_entry_ids": sorted(registry_entry_ids),
        "evidence": copy.deepcopy(dict(evidence)),
        "summary": summary,
    }
    finding_hash = _canonical_hash(finding_basis)

    return {
        "finding_id": (
            f"version-conflict-{finding_hash[:20]}"
        ),
        "finding_hash": finding_hash,
        **finding_basis,
        "finding_status": "OPEN",
        "human_review_required": True,
        "automatic_resolution_allowed": False,
        "execution_allowed": False,
    }


def _validate_records(
    records: Sequence[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    if isinstance(records, (str, bytes)) or not isinstance(
        records,
        Sequence,
    ):
        raise TypeError("records_must_be_sequence")

    if not records:
        raise ValueError("empty_compatibility_records")

    normalized: list[dict[str, Any]] = []

    for record in records:
        if not isinstance(record, Mapping):
            raise ValueError("invalid_version_record")

        errors = validate_version_record(record)
        if errors:
            raise ValueError(
                "invalid_version_record:"
                + ",".join(sorted(errors))
            )

        normalized.append(copy.deepcopy(dict(record)))

    normalized.sort(
        key=lambda item: str(item["registry_entry_id"])
    )

    entry_ids = [
        str(record["registry_entry_id"])
        for record in normalized
    ]
    if len(entry_ids) != len(set(entry_ids)):
        raise ValueError("duplicate_registry_entry_id")

    return normalized


def evaluate_version_compatibility(
    records: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    """Evaluate a version bundle without activating any version."""
    normalized = _validate_records(records)
    findings: list[dict[str, Any]] = []

    records_by_kind: dict[str, list[dict[str, Any]]] = defaultdict(
        list
    )
    for record in normalized:
        records_by_kind[str(record["record_kind"])].append(record)

    for kind in REQUIRED_BUNDLE_KINDS:
        selected = records_by_kind.get(kind, [])

        if not selected:
            findings.append(
                _build_finding(
                    finding_class="MISSING_REQUIRED_KIND",
                    severity="HIGH",
                    registry_entry_ids=[],
                    evidence={"missing_record_kind": kind},
                    summary=(
                        f"Version bundle is missing required {kind} record."
                    ),
                )
            )
        elif len(selected) > 1:
            findings.append(
                _build_finding(
                    finding_class="DUPLICATE_KIND_SELECTION",
                    severity="HIGH",
                    registry_entry_ids=[
                        str(item["registry_entry_id"])
                        for item in selected
                    ],
                    evidence={
                        "record_kind": kind,
                        "selected_count": len(selected),
                    },
                    summary=(
                        f"Version bundle selected multiple {kind} records."
                    ),
                )
            )

    for record in normalized:
        status = str(record["record_status"])
        entry_id = str(record["registry_entry_id"])

        status_finding = {
            "BLOCKED": (
                "BLOCKED_VERSION_SELECTED",
                "CRITICAL",
            ),
            "DEPRECATED": (
                "DEPRECATED_VERSION_SELECTED",
                "HIGH",
            ),
            "ARCHIVED": (
                "ARCHIVED_VERSION_SELECTED",
                "HIGH",
            ),
            "REVIEW_REQUIRED": (
                "REVIEW_REQUIRED_VERSION_SELECTED",
                "MEDIUM",
            ),
        }.get(status)

        if status_finding is not None:
            finding_class, severity = status_finding
            findings.append(
                _build_finding(
                    finding_class=finding_class,
                    severity=severity,
                    registry_entry_ids=[entry_id],
                    evidence={
                        "record_kind": record["record_kind"],
                        "record_status": status,
                        "version_key": _version_key(record),
                    },
                    summary=(
                        f"Selected version has governed status {status}."
                    ),
                )
            )

    contract_records = records_by_kind.get("CONTRACT", [])
    if contract_records:
        canonical_contract_version = str(
            contract_records[0]["contract_version"]
        )

        mismatched = [
            record
            for record in normalized
            if str(record["contract_version"])
            != canonical_contract_version
        ]

        if mismatched:
            findings.append(
                _build_finding(
                    finding_class="CONTRACT_REFERENCE_MISMATCH",
                    severity="HIGH",
                    registry_entry_ids=[
                        str(record["registry_entry_id"])
                        for record in mismatched
                    ]
                    + [
                        str(
                            contract_records[0][
                                "registry_entry_id"
                            ]
                        )
                    ],
                    evidence={
                        "expected_contract_version": (
                            canonical_contract_version
                        ),
                        "mismatched_contract_versions": {
                            str(record["registry_entry_id"]): str(
                                record["contract_version"]
                            )
                            for record in mismatched
                        },
                    },
                    summary=(
                        "Selected records reference incompatible "
                        "contract versions."
                    ),
                )
            )

    registry_records = records_by_kind.get("REGISTRY", [])
    if registry_records:
        canonical_registry_version = str(
            registry_records[0]["registry_version"]
        )

        mismatched = [
            record
            for record in normalized
            if str(record["registry_version"])
            != canonical_registry_version
        ]

        if mismatched:
            findings.append(
                _build_finding(
                    finding_class="REGISTRY_REFERENCE_MISMATCH",
                    severity="HIGH",
                    registry_entry_ids=[
                        str(record["registry_entry_id"])
                        for record in mismatched
                    ]
                    + [
                        str(
                            registry_records[0][
                                "registry_entry_id"
                            ]
                        )
                    ],
                    evidence={
                        "expected_registry_version": (
                            canonical_registry_version
                        ),
                        "mismatched_registry_versions": {
                            str(record["registry_entry_id"]): str(
                                record["registry_version"]
                            )
                            for record in mismatched
                        },
                    },
                    summary=(
                        "Selected records reference incompatible "
                        "registry versions."
                    ),
                )
            )

    baseline_ids = sorted(
        {
            str(record["validation_baseline_id"])
            for record in normalized
        }
    )
    if len(baseline_ids) > 1:
        findings.append(
            _build_finding(
                finding_class="VALIDATION_BASELINE_MISMATCH",
                severity="HIGH",
                registry_entry_ids=[
                    str(record["registry_entry_id"])
                    for record in normalized
                ],
                evidence={
                    "validation_baseline_ids": baseline_ids,
                },
                summary=(
                    "Selected versions do not share one validation baseline."
                ),
            )
        )

    correlation_ids = sorted(
        {
            str(record["correlation_id"])
            for record in normalized
        }
    )
    if len(correlation_ids) > 1:
        findings.append(
            _build_finding(
                finding_class="CORRELATION_ID_MISMATCH",
                severity="HIGH",
                registry_entry_ids=[
                    str(record["registry_entry_id"])
                    for record in normalized
                ],
                evidence={"correlation_ids": correlation_ids},
                summary=(
                    "Selected versions do not share one correlation id."
                ),
            )
        )

    content_groups: dict[str, list[dict[str, Any]]] = defaultdict(
        list
    )
    for record in normalized:
        content_groups[str(record["content_hash"])].append(record)

    for content_hash, grouped_records in sorted(
        content_groups.items()
    ):
        version_keys = sorted(
            {_version_key(record) for record in grouped_records}
        )

        if len(version_keys) > 1:
            findings.append(
                _build_finding(
                    finding_class=(
                        "DUPLICATE_CONTENT_DIFFERENT_VERSION"
                    ),
                    severity="MEDIUM",
                    registry_entry_ids=[
                        str(record["registry_entry_id"])
                        for record in grouped_records
                    ],
                    evidence={
                        "content_hash": content_hash,
                        "version_keys": version_keys,
                    },
                    summary=(
                        "Identical governed content is registered under "
                        "multiple version keys."
                    ),
                )
            )

    findings.sort(key=lambda item: str(item["finding_id"]))

    highest_severity = "NONE"
    if findings:
        highest_severity = max(
            (
                str(finding["severity"])
                for finding in findings
            ),
            key=lambda severity: SEVERITY_RANK[severity],
        )

    blocking_findings = [
        finding
        for finding in findings
        if SEVERITY_RANK[str(finding["severity"])] >= (
            SEVERITY_RANK["HIGH"]
        )
    ]

    compatible = not blocking_findings

    selected_versions = {
        kind: sorted(
            {
                str(record[VERSION_FIELD_BY_KIND[kind]])
                for record in records_by_kind.get(kind, [])
            }
        )
        for kind in VERSION_KINDS
    }

    kind_summary = dict(
        sorted(
            Counter(
                str(record["record_kind"])
                for record in normalized
            ).items()
        )
    )
    status_summary = dict(
        sorted(
            Counter(
                str(record["record_status"])
                for record in normalized
            ).items()
        )
    )

    report_basis = {
        "registry_entry_ids": [
            str(record["registry_entry_id"])
            for record in normalized
        ],
        "registry_entry_hashes": [
            str(record["registry_entry_hash"])
            for record in normalized
        ],
        "finding_ids": [
            str(finding["finding_id"])
            for finding in findings
        ],
        "compatible": compatible,
    }
    report_hash = _canonical_hash(report_basis)

    return {
        "compatibility_report_id": (
            f"version-compatibility-{report_hash[:20]}"
        ),
        "compatibility_report_hash": report_hash,
        "app_id": APP_ID,
        "contract_version": CONTRACT_VERSION,
        "compatibility_status": (
            "COMPATIBLE_FOR_PAPER_REVIEW"
            if compatible
            else "INCOMPATIBLE_REVIEW_REQUIRED"
        ),
        "compatible": compatible,
        "record_count": len(normalized),
        "registry_entry_ids": [
            str(record["registry_entry_id"])
            for record in normalized
        ],
        "selected_versions": selected_versions,
        "kind_summary": kind_summary,
        "status_summary": status_summary,
        "finding_count": len(findings),
        "findings": findings,
        "highest_severity": highest_severity,
        "human_review_required": True,
        "operator_review_bypass_allowed": False,
        "archive_required": True,
        "model_execution_allowed": False,
        "automatic_activation_allowed": False,
        "automatic_promotion_allowed": False,
        "automatic_rollback_allowed": False,
        "source_mutation_allowed": False,
        "real_trading_allowed": False,
        "real_execution_allowed": False,
    }


def validate_compatibility_report(
    report: Mapping[str, Any],
) -> list[str]:
    """Validate a compatibility report without changing it."""
    if not isinstance(report, Mapping):
        return ["report_must_be_mapping"]

    errors: list[str] = []

    for field in REQUIRED_REPORT_FIELDS:
        if field not in report:
            errors.append(f"missing_field:{field}")

    if report.get("app_id") != APP_ID:
        errors.append("invalid_app_id")

    if report.get("contract_version") != CONTRACT_VERSION:
        errors.append("invalid_contract_version")

    records = report.get("registry_entry_ids")
    if not isinstance(records, list) or not records:
        errors.append("invalid_registry_entry_ids")

    findings = report.get("findings")
    if not isinstance(findings, list):
        errors.append("invalid_findings")
        findings = []

    if report.get("finding_count") != len(findings):
        errors.append("finding_count_mismatch")

    compatible = report.get("compatible")
    if not isinstance(compatible, bool):
        errors.append("invalid_compatible_state")

    expected_status = (
        "COMPATIBLE_FOR_PAPER_REVIEW"
        if compatible is True
        else "INCOMPATIBLE_REVIEW_REQUIRED"
    )
    if report.get("compatibility_status") != expected_status:
        errors.append("compatibility_status_mismatch")

    if report.get("human_review_required") is not True:
        errors.append("human_review_not_required")

    if report.get("operator_review_bypass_allowed") is not False:
        errors.append("operator_review_bypass_not_blocked")

    if report.get("archive_required") is not True:
        errors.append("archive_not_required")

    if report.get("model_execution_allowed") is not False:
        errors.append("model_execution_not_blocked")

    if report.get("automatic_activation_allowed") is not False:
        errors.append("automatic_activation_not_blocked")

    if report.get("automatic_promotion_allowed") is not False:
        errors.append("automatic_promotion_not_blocked")

    if report.get("automatic_rollback_allowed") is not False:
        errors.append("automatic_rollback_not_blocked")

    if report.get("source_mutation_allowed") is not False:
        errors.append("source_mutation_not_blocked")

    if report.get("real_trading_allowed") is not False:
        errors.append("real_trading_not_blocked")

    if report.get("real_execution_allowed") is not False:
        errors.append("real_execution_not_blocked")

    return errors
