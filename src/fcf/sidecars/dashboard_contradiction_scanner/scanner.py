"""Deterministic contradiction scanning for governed dashboard artifacts."""

from __future__ import annotations

import copy
import hashlib
import json
from collections.abc import Mapping, Sequence
from typing import Any

from .finding_schema import build_contradiction_finding
from .source_loader import build_source_manifest

RISK_LEVELS = {
    "LOW": 1,
    "MEDIUM": 2,
    "HIGH": 3,
    "CRITICAL": 4,
}

STATE_COMPARISONS = (
    (
        "validation_state",
        "VALIDATION_STATE_MISMATCH",
        "HIGH",
    ),
    (
        "review_state",
        "REVIEW_STATE_MISMATCH",
        "HIGH",
    ),
    (
        "lifecycle_state",
        "LIFECYCLE_STATE_MISMATCH",
        "MEDIUM",
    ),
    (
        "archive_state",
        "ARCHIVE_STATE_MISMATCH",
        "MEDIUM",
    ),
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


def _trace_matches(
    dashboard: Mapping[str, Any],
    reference: Mapping[str, Any],
) -> bool:
    return (
        dashboard["correlation_id"] == reference["correlation_id"]
        and dashboard["research_run_id"] == reference["research_run_id"]
    )


def _payload(record: Mapping[str, Any]) -> Mapping[str, Any]:
    value = record.get("source_payload")
    return value if isinstance(value, Mapping) else {}


def _risk_levels(record: Mapping[str, Any]) -> dict[str, str]:
    value = _payload(record).get("risk_flag_levels")
    if not isinstance(value, Mapping):
        return {}

    normalized: dict[str, str] = {}
    for flag, level in value.items():
        if (
            isinstance(flag, str)
            and flag.strip()
            and isinstance(level, str)
            and level.strip().upper() in RISK_LEVELS
        ):
            normalized[flag.strip()] = level.strip().upper()

    return normalized


def _append_finding(
    findings: list[dict[str, Any]],
    *,
    dashboard: Mapping[str, Any],
    reference: Mapping[str, Any],
    contradiction_class: str,
    severity: str,
    evidence: Mapping[str, Any],
    summary: str,
) -> None:
    findings.append(
        build_contradiction_finding(
            contradiction_class=contradiction_class,
            severity=severity,
            correlation_id=dashboard["correlation_id"],
            research_run_id=dashboard["research_run_id"],
            validation_baseline_id=dashboard[
                "validation_baseline_id"
            ],
            source_artifact_ids=[
                dashboard["artifact_id"],
                reference["artifact_id"],
            ],
            evidence=evidence,
            summary=summary,
        )
    )


def _scan_pair(
    dashboard: Mapping[str, Any],
    reference: Mapping[str, Any],
) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []

    dashboard_flags = set(dashboard["risk_flags"])
    reference_flags = set(reference["risk_flags"])
    missing_flags = sorted(reference_flags - dashboard_flags)

    if missing_flags:
        _append_finding(
            findings,
            dashboard=dashboard,
            reference=reference,
            contradiction_class="RISK_FLAG_MISSING",
            severity="HIGH",
            evidence={
                "missing_risk_flags": missing_flags,
                "dashboard_risk_flags": sorted(dashboard_flags),
                "reference_risk_flags": sorted(reference_flags),
            },
            summary="Dashboard omitted governed risk flags.",
        )

    dashboard_levels = _risk_levels(dashboard)
    reference_levels = _risk_levels(reference)
    downgraded: list[dict[str, str]] = []

    for flag in sorted(set(dashboard_levels) & set(reference_levels)):
        dashboard_level = dashboard_levels[flag]
        reference_level = reference_levels[flag]

        if RISK_LEVELS[dashboard_level] < RISK_LEVELS[reference_level]:
            downgraded.append(
                {
                    "risk_flag": flag,
                    "dashboard_level": dashboard_level,
                    "reference_level": reference_level,
                }
            )

    if downgraded:
        _append_finding(
            findings,
            dashboard=dashboard,
            reference=reference,
            contradiction_class="RISK_FLAG_DOWNGRADED",
            severity="CRITICAL",
            evidence={"downgraded_risk_flags": downgraded},
            summary="Dashboard downgraded governed risk severity.",
        )

    dashboard_payload = _payload(dashboard)
    reference_payload = _payload(reference)
    summary_state = dashboard_payload.get("summary_state")
    raw_state = reference_payload.get("raw_state")

    if (
        isinstance(summary_state, str)
        and summary_state.strip()
        and isinstance(raw_state, str)
        and raw_state.strip()
        and summary_state.strip() != raw_state.strip()
    ):
        _append_finding(
            findings,
            dashboard=dashboard,
            reference=reference,
            contradiction_class="SUMMARY_RAW_CONFLICT",
            severity="HIGH",
            evidence={
                "dashboard_summary_state": summary_state.strip(),
                "reference_raw_state": raw_state.strip(),
            },
            summary="Dashboard summary conflicts with governed raw state.",
        )

    for field, contradiction_class, severity in STATE_COMPARISONS:
        dashboard_state = dashboard.get(field, "UNKNOWN")
        reference_state = reference.get(field, "UNKNOWN")

        if dashboard_state != reference_state:
            _append_finding(
                findings,
                dashboard=dashboard,
                reference=reference,
                contradiction_class=contradiction_class,
                severity=severity,
                evidence={
                    "state_field": field,
                    "dashboard_state": dashboard_state,
                    "reference_state": reference_state,
                },
                summary=f"Dashboard {field} conflicts with governed source.",
            )

    if (
        dashboard["validation_baseline_id"]
        != reference["validation_baseline_id"]
    ):
        _append_finding(
            findings,
            dashboard=dashboard,
            reference=reference,
            contradiction_class="VALIDATION_STATE_MISMATCH",
            severity="HIGH",
            evidence={
                "dashboard_validation_baseline_id": dashboard[
                    "validation_baseline_id"
                ],
                "reference_validation_baseline_id": reference[
                    "validation_baseline_id"
                ],
            },
            summary="Dashboard validation baseline differs from source.",
        )

    if reference["artifact_id"] not in dashboard["source_artifact_ids"]:
        _append_finding(
            findings,
            dashboard=dashboard,
            reference=reference,
            contradiction_class="SOURCE_LINEAGE_MISMATCH",
            severity="HIGH",
            evidence={
                "missing_source_artifact_id": reference["artifact_id"],
                "dashboard_source_artifact_ids": dashboard[
                    "source_artifact_ids"
                ],
            },
            summary="Dashboard lineage does not reference governed source.",
        )

    return findings


def scan_dashboard_contradictions(
    sources: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    """Scan dashboard records against matching governed source records."""
    source_copy = copy.deepcopy(list(sources))
    manifest = build_source_manifest(source_copy)

    dashboards = [
        item
        for item in manifest["sources"]
        if item["artifact_type"] == "DASHBOARD_STATUS_PACKET"
    ]
    references = [
        item
        for item in manifest["sources"]
        if item["artifact_type"] != "DASHBOARD_STATUS_PACKET"
    ]

    findings: list[dict[str, Any]] = []

    for dashboard in dashboards:
        for reference in references:
            if _trace_matches(dashboard, reference):
                findings.extend(_scan_pair(dashboard, reference))

    findings.sort(key=lambda item: item["finding_id"])

    report_basis = {
        "manifest_hash": manifest["manifest_hash"],
        "finding_ids": [item["finding_id"] for item in findings],
    }
    report_hash = _canonical_hash(report_basis)

    return {
        "scan_report_id": f"dashboard-scan-{report_hash[:20]}",
        "scan_report_hash": report_hash,
        "scan_status": (
            "CONTRADICTIONS_FOUND"
            if findings
            else "NO_CONTRADICTIONS"
        ),
        "source_manifest_hash": manifest["manifest_hash"],
        "source_count": manifest["source_count"],
        "dashboard_count": len(dashboards),
        "reference_count": len(references),
        "finding_count": len(findings),
        "findings": findings,
        "human_review_required": True,
        "archive_required": True,
        "execution_allowed": False,
        "source_mutation_allowed": False,
        "risk_flag_deletion_allowed": False,
        "risk_flag_downgrade_allowed": False,
    }
