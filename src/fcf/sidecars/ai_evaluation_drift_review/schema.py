"""Registered evidence schema for AI evaluation drift review."""

from __future__ import annotations

from collections.abc import Mapping
from datetime import datetime
from typing import Any

from .contract import (
    APP_ID,
    DRIFT_STATUSES,
    FORBIDDEN_DRIFT_STATUSES,
)


SCHEMA_VERSION = "1.0.0"

SOURCE_COMPARISON_STATUSES = (
    "MATCHED",
    "PARTIAL_MATCH",
    "MISMATCH",
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

REQUIRED_EVIDENCE_FIELDS = (
    "app_id",
    "schema_version",
    "drift_evidence_id",
    "evaluation_sample_id",
    "baseline_reference",
    "candidate_reference",
    "baseline_created_at_utc",
    "candidate_created_at_utc",
    "model_id",
    "baseline_model_version",
    "candidate_model_version",
    "prompt_id",
    "baseline_prompt_version",
    "candidate_prompt_version",
    "baseline_comparison_status",
    "candidate_comparison_status",
    "drift_status",
    "operator_review_status",
    "created_at_utc",
    "paper_only",
    "local_only",
    "read_only",
    "sidecar_only",
    "operator_review_required",
    "deterministic_only",
    "registered_artifacts_only",
    "core_mutation_allowed",
    "model_invocation_allowed",
    "prompt_execution_allowed",
    "orchestrator_execution_allowed",
    "automatic_approval_allowed",
    "automatic_rejection_allowed",
    "automatic_rollback_allowed",
    "automatic_model_switch_allowed",
    "automatic_prompt_switch_allowed",
    "trade_action_allowed",
    "real_execution_allowed",
)

STRING_FIELDS = (
    "app_id",
    "schema_version",
    "drift_evidence_id",
    "evaluation_sample_id",
    "baseline_reference",
    "candidate_reference",
    "baseline_created_at_utc",
    "candidate_created_at_utc",
    "model_id",
    "baseline_model_version",
    "candidate_model_version",
    "prompt_id",
    "baseline_prompt_version",
    "candidate_prompt_version",
    "baseline_comparison_status",
    "candidate_comparison_status",
    "drift_status",
    "operator_review_status",
    "created_at_utc",
)

REQUIRED_TRUE_FLAGS = (
    "paper_only",
    "local_only",
    "read_only",
    "sidecar_only",
    "operator_review_required",
    "deterministic_only",
    "registered_artifacts_only",
)

REQUIRED_FALSE_FLAGS = (
    "core_mutation_allowed",
    "model_invocation_allowed",
    "prompt_execution_allowed",
    "orchestrator_execution_allowed",
    "automatic_approval_allowed",
    "automatic_rejection_allowed",
    "automatic_rollback_allowed",
    "automatic_model_switch_allowed",
    "automatic_prompt_switch_allowed",
    "trade_action_allowed",
    "real_execution_allowed",
)


def build_drift_evidence_record(
    *,
    drift_evidence_id: str,
    evaluation_sample_id: str,
    baseline_reference: str,
    candidate_reference: str,
    baseline_created_at_utc: str,
    candidate_created_at_utc: str,
    model_id: str,
    baseline_model_version: str,
    candidate_model_version: str,
    prompt_id: str,
    baseline_prompt_version: str,
    candidate_prompt_version: str,
    baseline_comparison_status: str,
    candidate_comparison_status: str,
    drift_status: str,
    operator_review_status: str,
    created_at_utc: str,
) -> dict[str, Any]:
    """Build a deterministic registered drift evidence record."""

    return {
        "app_id": APP_ID,
        "schema_version": SCHEMA_VERSION,
        "drift_evidence_id": drift_evidence_id,
        "evaluation_sample_id": evaluation_sample_id,
        "baseline_reference": baseline_reference,
        "candidate_reference": candidate_reference,
        "baseline_created_at_utc": baseline_created_at_utc,
        "candidate_created_at_utc": candidate_created_at_utc,
        "model_id": model_id,
        "baseline_model_version": baseline_model_version,
        "candidate_model_version": candidate_model_version,
        "prompt_id": prompt_id,
        "baseline_prompt_version": baseline_prompt_version,
        "candidate_prompt_version": candidate_prompt_version,
        "baseline_comparison_status": (
            baseline_comparison_status
        ),
        "candidate_comparison_status": (
            candidate_comparison_status
        ),
        "drift_status": drift_status,
        "operator_review_status": operator_review_status,
        "created_at_utc": created_at_utc,
        "paper_only": True,
        "local_only": True,
        "read_only": True,
        "sidecar_only": True,
        "operator_review_required": True,
        "deterministic_only": True,
        "registered_artifacts_only": True,
        "core_mutation_allowed": False,
        "model_invocation_allowed": False,
        "prompt_execution_allowed": False,
        "orchestrator_execution_allowed": False,
        "automatic_approval_allowed": False,
        "automatic_rejection_allowed": False,
        "automatic_rollback_allowed": False,
        "automatic_model_switch_allowed": False,
        "automatic_prompt_switch_allowed": False,
        "trade_action_allowed": False,
        "real_execution_allowed": False,
    }


def _is_non_empty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _parse_aware_timestamp(value: Any) -> datetime | None:
    if not _is_non_empty_string(value):
        return None

    normalized = value.replace("Z", "+00:00")

    try:
        parsed = datetime.fromisoformat(normalized)
    except ValueError:
        return None

    if parsed.tzinfo is None:
        return None

    return parsed


def validate_drift_evidence_record(
    record: Mapping[str, Any],
) -> list[str]:
    """Return deterministic drift evidence validation errors."""

    if not isinstance(record, Mapping):
        return ["record_not_mapping"]

    errors: list[str] = []

    for field in REQUIRED_EVIDENCE_FIELDS:
        if field not in record:
            errors.append(f"missing_field:{field}")

    unexpected_fields = sorted(
        set(record) - set(REQUIRED_EVIDENCE_FIELDS)
    )

    for field in unexpected_fields:
        errors.append(f"unexpected_field:{field}")

    for field in STRING_FIELDS:
        if field in record and not _is_non_empty_string(
            record[field]
        ):
            errors.append(f"{field}_invalid")

    if record.get("app_id") != APP_ID:
        errors.append("app_id_mismatch")

    if record.get("schema_version") != SCHEMA_VERSION:
        errors.append("schema_version_mismatch")

    baseline_reference = record.get("baseline_reference")
    candidate_reference = record.get("candidate_reference")

    if (
        _is_non_empty_string(baseline_reference)
        and baseline_reference == candidate_reference
    ):
        errors.append("baseline_candidate_reference_must_differ")

    baseline_time = _parse_aware_timestamp(
        record.get("baseline_created_at_utc")
    )
    candidate_time = _parse_aware_timestamp(
        record.get("candidate_created_at_utc")
    )
    created_time = _parse_aware_timestamp(
        record.get("created_at_utc")
    )

    if baseline_time is None:
        errors.append("baseline_created_at_utc_invalid")

    if candidate_time is None:
        errors.append("candidate_created_at_utc_invalid")

    if created_time is None:
        errors.append("created_at_utc_invalid")

    if (
        baseline_time is not None
        and candidate_time is not None
        and candidate_time <= baseline_time
    ):
        errors.append(
            "candidate_created_at_utc_must_follow_baseline"
        )

    if (
        candidate_time is not None
        and created_time is not None
        and created_time < candidate_time
    ):
        errors.append(
            "created_at_utc_must_not_precede_candidate"
        )

    for field in (
        "baseline_comparison_status",
        "candidate_comparison_status",
    ):
        if record.get(field) not in SOURCE_COMPARISON_STATUSES:
            errors.append(f"{field}_invalid")

    drift_status = record.get("drift_status")

    if drift_status not in DRIFT_STATUSES:
        errors.append("drift_status_invalid")

    if drift_status in FORBIDDEN_DRIFT_STATUSES:
        errors.append(
            f"forbidden_drift_status:{drift_status}"
        )

    if record.get(
        "operator_review_status"
    ) not in OPERATOR_REVIEW_STATUSES:
        errors.append("operator_review_status_invalid")

    for field in REQUIRED_TRUE_FLAGS:
        if record.get(field) is not True:
            errors.append(f"{field}_must_be_true")

    for field in REQUIRED_FALSE_FLAGS:
        if record.get(field) is not False:
            errors.append(f"{field}_must_be_false")

    return sorted(set(errors))