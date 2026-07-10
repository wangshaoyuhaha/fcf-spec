"""Structured record schema for local AI evaluation samples."""

from __future__ import annotations

import re
from collections.abc import Mapping
from datetime import datetime
from typing import Any

from .contract import APP_ID


SAMPLE_STAGE_ID = "AI-EVALUATION-SAMPLE-LIBRARY-D2"
SAMPLE_SCHEMA_VERSION = "1.0.0"

EVALUATION_DIMENSIONS = (
    "faithfulness",
    "risk_preservation",
    "reason_code_alignment",
    "evidence_grounding",
    "operator_review_readiness",
)

EXPECTED_OUTCOMES = (
    "PASS",
    "FAIL",
    "REVIEW_REQUIRED",
)

REVIEW_STATUSES = (
    "DRAFT",
    "REVIEW_REQUIRED",
    "APPROVED",
    "REJECTED",
)

REQUIRED_TRUE_FLAGS = (
    "operator_review_required",
)

REQUIRED_FALSE_FLAGS = (
    "operator_review_bypass_allowed",
    "model_invocation_allowed",
    "prompt_execution_allowed",
    "orchestrator_execution_allowed",
    "news_feed_connection_allowed",
    "trade_action_allowed",
    "real_execution_allowed",
    "core_mutation_allowed",
    "p48_core_expansion_allowed",
)


def build_evaluation_sample_record(
    *,
    sample_id: str,
    sample_version: str,
    title: str,
    evaluation_dimension: str,
    input_payload_ref: str,
    expected_outcome: str,
    expected_summary: str,
    expected_reason_codes: tuple[str, ...] = (),
    expected_risk_flags: tuple[str, ...] = (),
    evidence_refs: tuple[str, ...],
    registry_entry_ids: tuple[str, ...],
    created_at_utc: str,
    review_status: str = "REVIEW_REQUIRED",
) -> dict[str, Any]:
    """Build a fresh local paper-only evaluation sample record."""

    return {
        "app_id": APP_ID,
        "stage_id": SAMPLE_STAGE_ID,
        "schema_version": SAMPLE_SCHEMA_VERSION,
        "sample_id": sample_id,
        "sample_version": sample_version,
        "title": title,
        "evaluation_dimension": evaluation_dimension,
        "input_payload_ref": input_payload_ref,
        "expected_outcome": expected_outcome,
        "expected_summary": expected_summary,
        "expected_reason_codes": list(expected_reason_codes),
        "expected_risk_flags": list(expected_risk_flags),
        "evidence_refs": list(evidence_refs),
        "registry_entry_ids": list(registry_entry_ids),
        "created_at_utc": created_at_utc,
        "review_status": review_status,
        "operator_review_required": True,
        "operator_review_bypass_allowed": False,
        "model_invocation_allowed": False,
        "prompt_execution_allowed": False,
        "orchestrator_execution_allowed": False,
        "news_feed_connection_allowed": False,
        "trade_action_allowed": False,
        "real_execution_allowed": False,
        "core_mutation_allowed": False,
        "p48_core_expansion_allowed": False,
    }


def _valid_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _valid_string_list(
    value: Any,
    *,
    allow_empty: bool,
) -> bool:
    if not isinstance(value, list):
        return False

    if not allow_empty and not value:
        return False

    return all(_valid_string(item) for item in value)


def _valid_semantic_version(value: Any) -> bool:
    return (
        isinstance(value, str)
        and re.fullmatch(r"\d+\.\d+\.\d+", value) is not None
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


def validate_evaluation_sample_record(
    record: Mapping[str, Any],
) -> list[str]:
    """Return deterministic sample record validation errors."""

    if not isinstance(record, Mapping):
        return ["record_not_mapping"]

    errors: list[str] = []

    expected_identity = {
        "app_id": APP_ID,
        "stage_id": SAMPLE_STAGE_ID,
        "schema_version": SAMPLE_SCHEMA_VERSION,
    }

    for field, expected in expected_identity.items():
        if record.get(field) != expected:
            errors.append(f"{field}_mismatch")

    for field in (
        "sample_id",
        "title",
        "input_payload_ref",
        "expected_summary",
    ):
        if not _valid_string(record.get(field)):
            errors.append(f"{field}_invalid")

    if not _valid_semantic_version(record.get("sample_version")):
        errors.append("sample_version_invalid")

    if (
        record.get("evaluation_dimension")
        not in EVALUATION_DIMENSIONS
    ):
        errors.append("evaluation_dimension_invalid")

    if record.get("expected_outcome") not in EXPECTED_OUTCOMES:
        errors.append("expected_outcome_invalid")

    if record.get("review_status") not in REVIEW_STATUSES:
        errors.append("review_status_invalid")

    if not _valid_utc_timestamp(record.get("created_at_utc")):
        errors.append("created_at_utc_invalid")

    optional_lists = (
        "expected_reason_codes",
        "expected_risk_flags",
    )

    for field in optional_lists:
        if not _valid_string_list(
            record.get(field),
            allow_empty=True,
        ):
            errors.append(f"{field}_invalid")

    required_lists = (
        "evidence_refs",
        "registry_entry_ids",
    )

    for field in required_lists:
        if not _valid_string_list(
            record.get(field),
            allow_empty=False,
        ):
            errors.append(f"{field}_invalid")

    for field in REQUIRED_TRUE_FLAGS:
        if record.get(field) is not True:
            errors.append(f"{field}_must_be_true")

    for field in REQUIRED_FALSE_FLAGS:
        if record.get(field) is not False:
            errors.append(f"{field}_must_be_false")

    return errors