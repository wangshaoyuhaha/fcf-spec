"""Governance review packet for the AI evaluation sample library."""

from __future__ import annotations

from collections.abc import Mapping
from datetime import datetime
from typing import Any

from .contract import APP_ID
from .coverage_checks import (
    validate_evaluation_sample_coverage_report,
)
from .registry_index import (
    validate_evaluation_sample_registry,
)


REVIEW_PACKET_STAGE_ID = "AI-EVALUATION-SAMPLE-LIBRARY-D5"
REVIEW_PACKET_SCHEMA_VERSION = "1.0.0"

GOVERNANCE_STATUSES = (
    "READY_FOR_OPERATOR_REVIEW",
    "REVIEW_REQUIRED",
    "BLOCKED",
)

REQUIRED_TRUE_FLAGS = (
    "paper_only",
    "local_only",
    "read_only",
    "sidecar_only",
    "operator_review_required",
)

REQUIRED_FALSE_FLAGS = (
    "operator_review_bypass_allowed",
    "automatic_approval_allowed",
    "model_invocation_allowed",
    "prompt_execution_allowed",
    "orchestrator_execution_allowed",
    "news_feed_connection_allowed",
    "trade_action_allowed",
    "real_execution_allowed",
    "core_mutation_allowed",
    "p48_core_expansion_allowed",
)


def _valid_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _valid_string_list(value: Any) -> bool:
    return (
        isinstance(value, list)
        and all(_valid_string(item) for item in value)
    )


def _valid_utc_timestamp(value: Any) -> bool:
    if not isinstance(value, str) or not value:
        return False

    try:
        parsed = datetime.fromisoformat(
            value.replace("Z", "+00:00")
        )
    except ValueError:
        return False

    return (
        parsed.tzinfo is not None
        and parsed.utcoffset() is not None
        and parsed.utcoffset().total_seconds() == 0
    )


def _governance_status(
    *,
    coverage_status: Any,
    source_validation_errors: list[str],
) -> str:
    if source_validation_errors or coverage_status == "FAIL":
        return "BLOCKED"

    if coverage_status == "REVIEW_REQUIRED":
        return "REVIEW_REQUIRED"

    return "READY_FOR_OPERATOR_REVIEW"


def build_evaluation_sample_review_packet(
    *,
    packet_id: str,
    registry: Mapping[str, Any],
    coverage_report: Mapping[str, Any],
    created_at_utc: str,
    reviewer_note: str = "",
) -> dict[str, Any]:
    """Build a paper-only operator governance review packet."""

    registry_errors = validate_evaluation_sample_registry(
        registry
    )
    coverage_errors = (
        validate_evaluation_sample_coverage_report(
            coverage_report
        )
    )

    source_validation_errors = [
        f"registry:{error}"
        for error in registry_errors
    ]
    source_validation_errors.extend(
        f"coverage:{error}"
        for error in coverage_errors
    )

    coverage_status = coverage_report.get(
        "coverage_status"
    )

    governance_status = _governance_status(
        coverage_status=coverage_status,
        source_validation_errors=source_validation_errors,
    )

    sample_keys = registry.get("sample_keys", [])

    if not isinstance(sample_keys, list):
        sample_keys = []

    return {
        "app_id": APP_ID,
        "stage_id": REVIEW_PACKET_STAGE_ID,
        "schema_version": REVIEW_PACKET_SCHEMA_VERSION,
        "packet_id": packet_id,
        "created_at_utc": created_at_utc,
        "source_registry_id": registry.get("registry_id"),
        "source_coverage_stage_id": coverage_report.get(
            "stage_id"
        ),
        "sample_count": registry.get("sample_count", 0),
        "sample_keys": list(sample_keys),
        "coverage_status": coverage_status,
        "governance_status": governance_status,
        "missing_dimensions": list(
            coverage_report.get("missing_dimensions", [])
        ),
        "duplicate_sample_keys": list(
            coverage_report.get(
                "duplicate_sample_keys",
                [],
            )
        ),
        "pending_review_keys": list(
            coverage_report.get("pending_review_keys", [])
        ),
        "evidence_missing_keys": list(
            coverage_report.get(
                "evidence_missing_keys",
                [],
            )
        ),
        "registry_reference_missing_keys": list(
            coverage_report.get(
                "registry_reference_missing_keys",
                [],
            )
        ),
        "source_validation_errors": source_validation_errors,
        "reviewer_note": reviewer_note,
        "paper_only": True,
        "local_only": True,
        "read_only": True,
        "sidecar_only": True,
        "operator_review_required": True,
        "operator_review_bypass_allowed": False,
        "automatic_approval_allowed": False,
        "model_invocation_allowed": False,
        "prompt_execution_allowed": False,
        "orchestrator_execution_allowed": False,
        "news_feed_connection_allowed": False,
        "trade_action_allowed": False,
        "real_execution_allowed": False,
        "core_mutation_allowed": False,
        "p48_core_expansion_allowed": False,
    }


def _expected_governance_status(
    packet: Mapping[str, Any],
) -> str:
    source_errors = packet.get(
        "source_validation_errors",
        [],
    )

    coverage_status = packet.get("coverage_status")

    if source_errors or coverage_status == "FAIL":
        return "BLOCKED"

    if coverage_status == "REVIEW_REQUIRED":
        return "REVIEW_REQUIRED"

    return "READY_FOR_OPERATOR_REVIEW"


def validate_evaluation_sample_review_packet(
    packet: Mapping[str, Any],
) -> list[str]:
    """Return deterministic review packet validation errors."""

    if not isinstance(packet, Mapping):
        return ["packet_not_mapping"]

    errors: list[str] = []

    expected_identity = {
        "app_id": APP_ID,
        "stage_id": REVIEW_PACKET_STAGE_ID,
        "schema_version": REVIEW_PACKET_SCHEMA_VERSION,
    }

    for field, expected in expected_identity.items():
        if packet.get(field) != expected:
            errors.append(f"{field}_mismatch")

    for field in (
        "packet_id",
        "source_registry_id",
        "source_coverage_stage_id",
    ):
        if not _valid_string(packet.get(field)):
            errors.append(f"{field}_invalid")

    if not _valid_utc_timestamp(
        packet.get("created_at_utc")
    ):
        errors.append("created_at_utc_invalid")

    sample_count = packet.get("sample_count")

    if (
        not isinstance(sample_count, int)
        or isinstance(sample_count, bool)
        or sample_count < 0
    ):
        errors.append("sample_count_invalid")

    list_fields = (
        "sample_keys",
        "missing_dimensions",
        "duplicate_sample_keys",
        "pending_review_keys",
        "evidence_missing_keys",
        "registry_reference_missing_keys",
        "source_validation_errors",
    )

    for field in list_fields:
        if not _valid_string_list(packet.get(field)):
            errors.append(f"{field}_invalid")

    sample_keys = packet.get("sample_keys")

    if (
        isinstance(sample_keys, list)
        and isinstance(sample_count, int)
        and not isinstance(sample_count, bool)
        and sample_count != len(sample_keys)
    ):
        errors.append("sample_count_mismatch")

    reviewer_note = packet.get("reviewer_note")

    if not isinstance(reviewer_note, str):
        errors.append("reviewer_note_invalid")

    governance_status = packet.get("governance_status")

    if governance_status not in GOVERNANCE_STATUSES:
        errors.append("governance_status_invalid")
    elif governance_status != _expected_governance_status(
        packet
    ):
        errors.append("governance_status_mismatch")

    if packet.get("coverage_status") not in (
        "PASS",
        "REVIEW_REQUIRED",
        "FAIL",
    ):
        errors.append("coverage_status_invalid")

    for field in REQUIRED_TRUE_FLAGS:
        if packet.get(field) is not True:
            errors.append(f"{field}_must_be_true")

    for field in REQUIRED_FALSE_FLAGS:
        if packet.get(field) is not False:
            errors.append(f"{field}_must_be_false")

    return errors