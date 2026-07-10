"""Comparison record schema for registered AI evaluation artifacts."""

from __future__ import annotations

from collections.abc import Mapping
from datetime import datetime
from typing import Any

from .contract import (
    APP_ID,
    COMPARISON_MODES,
    COMPARISON_STATUSES,
    FORBIDDEN_COMPARISON_STATUSES,
)


SCHEMA_VERSION = "1.0.0"

RESULT_STATUSES = (
    "RECORDED",
    "REVIEW_REQUIRED",
    "INVALID",
    "BLOCKED",
    "ARCHIVED",
)

OPERATOR_REVIEW_STATUSES = (
    "REVIEW_REQUIRED",
    "PENDING",
    "REVIEWED",
    "BLOCKED",
    "ARCHIVED",
)

REQUIRED_RECORD_FIELDS = (
    "app_id",
    "schema_version",
    "comparison_id",
    "comparison_mode",
    "evaluation_sample_id",
    "expected_result_reference",
    "observed_result_reference",
    "model_id",
    "model_version",
    "prompt_id",
    "prompt_version",
    "context_evidence_reference",
    "result_status",
    "comparison_status",
    "operator_review_status",
    "created_at_utc",
    "paper_only",
    "local_only",
    "read_only",
    "sidecar_only",
    "operator_review_required",
    "model_invocation_allowed",
    "prompt_execution_allowed",
    "automatic_acceptance_allowed",
    "trade_action_allowed",
    "real_execution_allowed",
    "core_mutation_allowed",
)

STRING_FIELDS = (
    "app_id",
    "schema_version",
    "comparison_id",
    "comparison_mode",
    "evaluation_sample_id",
    "expected_result_reference",
    "observed_result_reference",
    "model_id",
    "model_version",
    "prompt_id",
    "prompt_version",
    "context_evidence_reference",
    "result_status",
    "comparison_status",
    "operator_review_status",
    "created_at_utc",
)

REQUIRED_TRUE_FLAGS = (
    "paper_only",
    "local_only",
    "read_only",
    "sidecar_only",
    "operator_review_required",
)

REQUIRED_FALSE_FLAGS = (
    "model_invocation_allowed",
    "prompt_execution_allowed",
    "automatic_acceptance_allowed",
    "trade_action_allowed",
    "real_execution_allowed",
    "core_mutation_allowed",
)


def build_comparison_record(
    *,
    comparison_id: str,
    comparison_mode: str,
    evaluation_sample_id: str,
    expected_result_reference: str,
    observed_result_reference: str,
    model_id: str,
    model_version: str,
    prompt_id: str,
    prompt_version: str,
    context_evidence_reference: str,
    result_status: str,
    comparison_status: str,
    operator_review_status: str,
    created_at_utc: str,
) -> dict[str, Any]:
    """Build a deterministic local comparison record."""

    return {
        "app_id": APP_ID,
        "schema_version": SCHEMA_VERSION,
        "comparison_id": comparison_id,
        "comparison_mode": comparison_mode,
        "evaluation_sample_id": evaluation_sample_id,
        "expected_result_reference": expected_result_reference,
        "observed_result_reference": observed_result_reference,
        "model_id": model_id,
        "model_version": model_version,
        "prompt_id": prompt_id,
        "prompt_version": prompt_version,
        "context_evidence_reference": context_evidence_reference,
        "result_status": result_status,
        "comparison_status": comparison_status,
        "operator_review_status": operator_review_status,
        "created_at_utc": created_at_utc,
        "paper_only": True,
        "local_only": True,
        "read_only": True,
        "sidecar_only": True,
        "operator_review_required": True,
        "model_invocation_allowed": False,
        "prompt_execution_allowed": False,
        "automatic_acceptance_allowed": False,
        "trade_action_allowed": False,
        "real_execution_allowed": False,
        "core_mutation_allowed": False,
    }


def _is_non_empty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _is_timezone_aware_timestamp(value: Any) -> bool:
    if not _is_non_empty_string(value):
        return False

    normalized = value.replace("Z", "+00:00")

    try:
        parsed = datetime.fromisoformat(normalized)
    except ValueError:
        return False

    return parsed.tzinfo is not None


def validate_comparison_record(
    record: Mapping[str, Any],
) -> list[str]:
    """Return deterministic comparison record validation errors."""

    if not isinstance(record, Mapping):
        return ["record_not_mapping"]

    errors: list[str] = []

    missing_fields = [
        field
        for field in REQUIRED_RECORD_FIELDS
        if field not in record
    ]

    for field in missing_fields:
        errors.append(f"missing_field:{field}")

    unexpected_fields = sorted(
        set(record) - set(REQUIRED_RECORD_FIELDS)
    )

    for field in unexpected_fields:
        errors.append(f"unexpected_field:{field}")

    for field in STRING_FIELDS:
        if field in record and not _is_non_empty_string(record[field]):
            errors.append(f"{field}_invalid")

    if record.get("app_id") != APP_ID:
        errors.append("app_id_mismatch")

    if record.get("schema_version") != SCHEMA_VERSION:
        errors.append("schema_version_mismatch")

    comparison_mode = record.get("comparison_mode")

    if comparison_mode not in COMPARISON_MODES:
        errors.append("comparison_mode_invalid")

    result_status = record.get("result_status")

    if result_status not in RESULT_STATUSES:
        errors.append("result_status_invalid")

    comparison_status = record.get("comparison_status")

    if comparison_status not in COMPARISON_STATUSES:
        errors.append("comparison_status_invalid")

    if comparison_status in FORBIDDEN_COMPARISON_STATUSES:
        errors.append(
            f"forbidden_comparison_status:{comparison_status}"
        )

    operator_review_status = record.get(
        "operator_review_status"
    )

    if operator_review_status not in OPERATOR_REVIEW_STATUSES:
        errors.append("operator_review_status_invalid")

    if not _is_timezone_aware_timestamp(
        record.get("created_at_utc")
    ):
        errors.append("created_at_utc_invalid")

    for field in REQUIRED_TRUE_FLAGS:
        if record.get(field) is not True:
            errors.append(f"{field}_must_be_true")

    for field in REQUIRED_FALSE_FLAGS:
        if record.get(field) is not False:
            errors.append(f"{field}_must_be_false")

    return sorted(set(errors))