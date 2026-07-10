"""Contradiction finding schema for governed dashboard review."""

from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping, Sequence
from typing import Any

from .contract import CONTRADICTION_CLASSES

CONTRADICTION_SEVERITIES = (
    "LOW",
    "MEDIUM",
    "HIGH",
    "CRITICAL",
)

FINDING_STATUSES = (
    "OPEN",
    "ACKNOWLEDGED",
    "RESOLVED",
    "ARCHIVED",
)

REQUIRED_FINDING_FIELDS = (
    "finding_id",
    "contradiction_class",
    "severity",
    "status",
    "correlation_id",
    "research_run_id",
    "validation_baseline_id",
    "source_artifact_ids",
    "evidence",
    "summary",
    "human_review_required",
    "archive_required",
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


def _normalize_artifact_ids(
    source_artifact_ids: Sequence[str],
) -> list[str]:
    if isinstance(source_artifact_ids, (str, bytes)):
        raise ValueError("invalid_source_artifact_ids")

    if not isinstance(source_artifact_ids, Sequence):
        raise ValueError("invalid_source_artifact_ids")

    normalized: list[str] = []
    for artifact_id in source_artifact_ids:
        normalized.append(
            _require_text(artifact_id, "source_artifact_ids")
        )

    if not normalized:
        raise ValueError("empty_source_artifact_ids")

    if len(normalized) != len(set(normalized)):
        raise ValueError("duplicate_source_artifact_ids")

    return sorted(normalized)


def build_contradiction_finding(
    *,
    contradiction_class: str,
    severity: str,
    correlation_id: str,
    research_run_id: str,
    validation_baseline_id: str,
    source_artifact_ids: Sequence[str],
    evidence: Mapping[str, Any],
    summary: str,
    status: str = "OPEN",
) -> dict[str, Any]:
    """Build one deterministic paper-only contradiction finding."""
    normalized_class = _require_text(
        contradiction_class,
        "contradiction_class",
    )
    normalized_severity = _require_text(severity, "severity")
    normalized_status = _require_text(status, "status")

    if normalized_class not in CONTRADICTION_CLASSES:
        raise ValueError(
            f"unsupported_contradiction_class:{normalized_class}"
        )

    if normalized_severity not in CONTRADICTION_SEVERITIES:
        raise ValueError(
            f"unsupported_severity:{normalized_severity}"
        )

    if normalized_status not in FINDING_STATUSES:
        raise ValueError(
            f"unsupported_status:{normalized_status}"
        )

    if not isinstance(evidence, Mapping) or not evidence:
        raise ValueError("missing_or_invalid_evidence")

    normalized_artifact_ids = _normalize_artifact_ids(
        source_artifact_ids
    )

    finding_basis = {
        "contradiction_class": normalized_class,
        "severity": normalized_severity,
        "correlation_id": _require_text(
            correlation_id,
            "correlation_id",
        ),
        "research_run_id": _require_text(
            research_run_id,
            "research_run_id",
        ),
        "validation_baseline_id": _require_text(
            validation_baseline_id,
            "validation_baseline_id",
        ),
        "source_artifact_ids": normalized_artifact_ids,
        "evidence": dict(evidence),
        "summary": _require_text(summary, "summary"),
    }

    finding_hash = _canonical_hash(finding_basis)

    finding = {
        "finding_id": f"contradiction-{finding_hash[:20]}",
        **finding_basis,
        "status": normalized_status,
        "finding_hash": finding_hash,
        "human_review_required": True,
        "archive_required": True,
        "execution_allowed": False,
        "source_mutation_allowed": False,
        "risk_flag_deletion_allowed": False,
        "risk_flag_downgrade_allowed": False,
    }

    return finding


def validate_contradiction_finding(
    finding: Mapping[str, Any],
) -> list[str]:
    """Validate one finding without modifying its contents."""
    errors: list[str] = []

    if not isinstance(finding, Mapping):
        return ["finding_must_be_mapping"]

    for field in REQUIRED_FINDING_FIELDS:
        if field not in finding:
            errors.append(f"missing_field:{field}")

    contradiction_class = finding.get("contradiction_class")
    if contradiction_class not in CONTRADICTION_CLASSES:
        errors.append("invalid_contradiction_class")

    if finding.get("severity") not in CONTRADICTION_SEVERITIES:
        errors.append("invalid_severity")

    if finding.get("status") not in FINDING_STATUSES:
        errors.append("invalid_status")

    source_artifact_ids = finding.get("source_artifact_ids")
    if (
        not isinstance(source_artifact_ids, list)
        or not source_artifact_ids
    ):
        errors.append("invalid_source_artifact_ids")

    evidence = finding.get("evidence")
    if not isinstance(evidence, Mapping) or not evidence:
        errors.append("invalid_evidence")

    if finding.get("human_review_required") is not True:
        errors.append("human_review_not_required")

    if finding.get("archive_required") is not True:
        errors.append("archive_not_required")

    if finding.get("execution_allowed") is not False:
        errors.append("execution_not_blocked")

    if finding.get("source_mutation_allowed") is not False:
        errors.append("source_mutation_not_blocked")

    if finding.get("risk_flag_deletion_allowed") is not False:
        errors.append("risk_flag_deletion_not_blocked")

    if finding.get("risk_flag_downgrade_allowed") is not False:
        errors.append("risk_flag_downgrade_not_blocked")

    for field in FORBIDDEN_ACTION_FIELDS:
        if field in finding:
            errors.append(f"forbidden_action_field:{field}")

    return errors
