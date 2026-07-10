"""Deterministic registry index for local AI evaluation samples."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from datetime import datetime
from typing import Any

from .contract import APP_ID
from .sample_schema import validate_evaluation_sample_record


REGISTRY_STAGE_ID = "AI-EVALUATION-SAMPLE-LIBRARY-D3"
REGISTRY_SCHEMA_VERSION = "1.0.0"

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


def _valid_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


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


def _build_registry_entry(
    record: Mapping[str, Any],
) -> dict[str, Any]:
    sample_id = str(record["sample_id"])
    sample_version = str(record["sample_version"])

    return {
        "sample_key": f"{sample_id}@{sample_version}",
        "sample_id": sample_id,
        "sample_version": sample_version,
        "title": str(record["title"]),
        "evaluation_dimension": str(
            record["evaluation_dimension"]
        ),
        "expected_outcome": str(record["expected_outcome"]),
        "review_status": str(record["review_status"]),
        "input_payload_ref": str(record["input_payload_ref"]),
        "evidence_refs": list(record["evidence_refs"]),
        "prompt_model_registry_entry_ids": list(
            record["registry_entry_ids"]
        ),
        "operator_review_required": True,
        "operator_review_bypass_allowed": False,
        "model_invocation_allowed": False,
        "trade_action_allowed": False,
        "real_execution_allowed": False,
    }


def build_evaluation_sample_registry(
    *,
    registry_id: str,
    records: Sequence[Mapping[str, Any]],
    created_at_utc: str,
) -> dict[str, Any]:
    """Build a sorted local read-only evaluation sample registry."""

    entries = [
        _build_registry_entry(record)
        for record in records
    ]
    entries.sort(key=lambda entry: entry["sample_key"])

    return {
        "app_id": APP_ID,
        "stage_id": REGISTRY_STAGE_ID,
        "schema_version": REGISTRY_SCHEMA_VERSION,
        "registry_id": registry_id,
        "created_at_utc": created_at_utc,
        "sample_count": len(entries),
        "sample_keys": [
            entry["sample_key"]
            for entry in entries
        ],
        "entries": entries,
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


def _validate_registry_entry(
    entry: Any,
    index: int,
) -> list[str]:
    if not isinstance(entry, Mapping):
        return [f"entry_not_mapping:{index}"]

    errors: list[str] = []

    required_strings = (
        "sample_key",
        "sample_id",
        "sample_version",
        "title",
        "evaluation_dimension",
        "expected_outcome",
        "review_status",
        "input_payload_ref",
    )

    for field in required_strings:
        if not _valid_string(entry.get(field)):
            errors.append(f"entry_{field}_invalid:{index}")

    expected_key = (
        f"{entry.get('sample_id')}@"
        f"{entry.get('sample_version')}"
    )

    if entry.get("sample_key") != expected_key:
        errors.append(f"entry_sample_key_mismatch:{index}")

    for field in (
        "evidence_refs",
        "prompt_model_registry_entry_ids",
    ):
        value = entry.get(field)

        if (
            not isinstance(value, list)
            or not value
            or not all(_valid_string(item) for item in value)
        ):
            errors.append(f"entry_{field}_invalid:{index}")

    if entry.get("operator_review_required") is not True:
        errors.append(
            f"entry_operator_review_required_must_be_true:{index}"
        )

    for field in (
        "operator_review_bypass_allowed",
        "model_invocation_allowed",
        "trade_action_allowed",
        "real_execution_allowed",
    ):
        if entry.get(field) is not False:
            errors.append(f"entry_{field}_must_be_false:{index}")

    return errors


def validate_evaluation_sample_registry(
    registry: Mapping[str, Any],
) -> list[str]:
    """Return deterministic registry validation errors."""

    if not isinstance(registry, Mapping):
        return ["registry_not_mapping"]

    errors: list[str] = []

    expected_identity = {
        "app_id": APP_ID,
        "stage_id": REGISTRY_STAGE_ID,
        "schema_version": REGISTRY_SCHEMA_VERSION,
    }

    for field, expected in expected_identity.items():
        if registry.get(field) != expected:
            errors.append(f"{field}_mismatch")

    if not _valid_string(registry.get("registry_id")):
        errors.append("registry_id_invalid")

    if not _valid_utc_timestamp(
        registry.get("created_at_utc")
    ):
        errors.append("created_at_utc_invalid")

    entries = registry.get("entries")

    if not isinstance(entries, list):
        errors.append("entries_invalid")
        entries = []

    for index, entry in enumerate(entries):
        errors.extend(_validate_registry_entry(entry, index))

    sample_keys = registry.get("sample_keys")

    if not isinstance(sample_keys, list):
        errors.append("sample_keys_invalid")
        sample_keys = []

    actual_keys = [
        entry.get("sample_key")
        for entry in entries
        if isinstance(entry, Mapping)
    ]

    if sample_keys != actual_keys:
        errors.append("sample_keys_mismatch")

    if actual_keys != sorted(actual_keys):
        errors.append("entries_not_sorted")

    if len(actual_keys) != len(set(actual_keys)):
        errors.append("duplicate_sample_key")

    if registry.get("sample_count") != len(entries):
        errors.append("sample_count_mismatch")

    for field in REQUIRED_TRUE_FLAGS:
        if registry.get(field) is not True:
            errors.append(f"{field}_must_be_true")

    for field in REQUIRED_FALSE_FLAGS:
        if registry.get(field) is not False:
            errors.append(f"{field}_must_be_false")

    return errors


def validate_registry_source_records(
    records: Sequence[Mapping[str, Any]],
) -> list[str]:
    """Validate source records before registry construction."""

    errors: list[str] = []

    for index, record in enumerate(records):
        record_errors = validate_evaluation_sample_record(record)

        for error in record_errors:
            errors.append(f"source_record_{index}:{error}")

    return errors