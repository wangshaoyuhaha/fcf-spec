"""Deterministic registry index for imported AI evaluation results."""

from __future__ import annotations

from collections import Counter
from collections.abc import Mapping, Sequence
from datetime import datetime
from typing import Any

from .contract import APP_ID, IMPORTED_RESULT_STATUSES
from .result_schema import validate_evaluation_result_record


REGISTRY_STAGE_ID = "AI-EVALUATION-RESULT-REGISTRY-D3"
REGISTRY_SCHEMA_VERSION = "1.0.0"

REQUIRED_TRUE_FLAGS = (
    "paper_only",
    "local_only",
    "read_only",
    "sidecar_only",
    "operator_review_required",
    "imported_artifacts_only",
)

REQUIRED_FALSE_FLAGS = (
    "operator_review_bypass_allowed",
    "automatic_evaluation_acceptance_allowed",
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
    return {
        "result_key": str(record["result_key"]),
        "result_id": str(record["result_id"]),
        "result_version": str(record["result_version"]),
        "sample_key": str(record["sample_key"]),
        "sample_id": str(record["sample_id"]),
        "sample_version": str(record["sample_version"]),
        "evaluation_dimension": str(
            record["evaluation_dimension"]
        ),
        "observed_outcome": str(record["observed_outcome"]),
        "result_status": str(record["result_status"]),
        "imported_output_ref": str(
            record["imported_output_ref"]
        ),
        "imported_output_sha256": str(
            record["imported_output_sha256"]
        ),
        "evidence_refs": list(record["evidence_refs"]),
        "prompt_model_registry_entry_ids": list(
            record["prompt_model_registry_entry_ids"]
        ),
        "context_evidence_entry_ids": list(
            record["context_evidence_entry_ids"]
        ),
        "imported_at_utc": str(record["imported_at_utc"]),
        "operator_review_required": True,
        "operator_review_bypass_allowed": False,
        "automatic_evaluation_acceptance_allowed": False,
        "model_invocation_allowed": False,
        "prompt_execution_allowed": False,
        "trade_action_allowed": False,
        "real_execution_allowed": False,
    }


def build_evaluation_result_registry(
    *,
    registry_id: str,
    records: Sequence[Mapping[str, Any]],
    created_at_utc: str,
) -> dict[str, Any]:
    """Build a sorted local imported evaluation result registry."""

    entries = [
        _build_registry_entry(record)
        for record in records
    ]
    entries.sort(key=lambda entry: entry["result_key"])

    result_keys = [
        entry["result_key"]
        for entry in entries
    ]

    sample_keys = sorted(
        {
            entry["sample_key"]
            for entry in entries
        }
    )

    status_counts = {
        status: 0
        for status in IMPORTED_RESULT_STATUSES
    }

    for entry in entries:
        status = entry["result_status"]

        if status in status_counts:
            status_counts[status] += 1

    sample_result_counts = dict(
        sorted(
            Counter(
                entry["sample_key"]
                for entry in entries
            ).items()
        )
    )

    return {
        "app_id": APP_ID,
        "stage_id": REGISTRY_STAGE_ID,
        "schema_version": REGISTRY_SCHEMA_VERSION,
        "registry_id": registry_id,
        "created_at_utc": created_at_utc,
        "result_count": len(entries),
        "sample_count": len(sample_keys),
        "result_keys": result_keys,
        "sample_keys": sample_keys,
        "status_counts": status_counts,
        "sample_result_counts": sample_result_counts,
        "entries": entries,
        "paper_only": True,
        "local_only": True,
        "read_only": True,
        "sidecar_only": True,
        "operator_review_required": True,
        "imported_artifacts_only": True,
        "operator_review_bypass_allowed": False,
        "automatic_evaluation_acceptance_allowed": False,
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
        "result_key",
        "result_id",
        "result_version",
        "sample_key",
        "sample_id",
        "sample_version",
        "evaluation_dimension",
        "observed_outcome",
        "result_status",
        "imported_output_ref",
        "imported_output_sha256",
        "imported_at_utc",
    )

    for field in required_strings:
        if not _valid_string(entry.get(field)):
            errors.append(f"entry_{field}_invalid:{index}")

    expected_result_key = (
        f"{entry.get('result_id')}@"
        f"{entry.get('result_version')}"
    )

    if entry.get("result_key") != expected_result_key:
        errors.append(f"entry_result_key_mismatch:{index}")

    expected_sample_key = (
        f"{entry.get('sample_id')}@"
        f"{entry.get('sample_version')}"
    )

    if entry.get("sample_key") != expected_sample_key:
        errors.append(f"entry_sample_key_mismatch:{index}")

    if entry.get("result_status") not in IMPORTED_RESULT_STATUSES:
        errors.append(f"entry_result_status_invalid:{index}")

    for field in (
        "evidence_refs",
        "prompt_model_registry_entry_ids",
        "context_evidence_entry_ids",
    ):
        if not _valid_string_list(
            entry.get(field),
            allow_empty=False,
        ):
            errors.append(f"entry_{field}_invalid:{index}")

    if entry.get("operator_review_required") is not True:
        errors.append(
            f"entry_operator_review_required_must_be_true:{index}"
        )

    for field in (
        "operator_review_bypass_allowed",
        "automatic_evaluation_acceptance_allowed",
        "model_invocation_allowed",
        "prompt_execution_allowed",
        "trade_action_allowed",
        "real_execution_allowed",
    ):
        if entry.get(field) is not False:
            errors.append(f"entry_{field}_must_be_false:{index}")

    return errors


def validate_evaluation_result_registry(
    registry: Mapping[str, Any],
) -> list[str]:
    """Return deterministic result registry validation errors."""

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

    actual_result_keys = [
        entry.get("result_key")
        for entry in entries
        if isinstance(entry, Mapping)
    ]

    actual_sample_keys = sorted(
        {
            entry.get("sample_key")
            for entry in entries
            if (
                isinstance(entry, Mapping)
                and _valid_string(entry.get("sample_key"))
            )
        }
    )

    if registry.get("result_keys") != actual_result_keys:
        errors.append("result_keys_mismatch")

    if registry.get("sample_keys") != actual_sample_keys:
        errors.append("sample_keys_mismatch")

    if actual_result_keys != sorted(actual_result_keys):
        errors.append("entries_not_sorted")

    if len(actual_result_keys) != len(set(actual_result_keys)):
        errors.append("duplicate_result_key")

    if registry.get("result_count") != len(entries):
        errors.append("result_count_mismatch")

    if registry.get("sample_count") != len(actual_sample_keys):
        errors.append("sample_count_mismatch")

    expected_status_counts = {
        status: 0
        for status in IMPORTED_RESULT_STATUSES
    }

    for entry in entries:
        if not isinstance(entry, Mapping):
            continue

        status = entry.get("result_status")

        if status in expected_status_counts:
            expected_status_counts[str(status)] += 1

    if registry.get("status_counts") != expected_status_counts:
        errors.append("status_counts_mismatch")

    expected_sample_result_counts = dict(
        sorted(
            Counter(
                entry.get("sample_key")
                for entry in entries
                if (
                    isinstance(entry, Mapping)
                    and _valid_string(entry.get("sample_key"))
                )
            ).items()
        )
    )

    if (
        registry.get("sample_result_counts")
        != expected_sample_result_counts
    ):
        errors.append("sample_result_counts_mismatch")

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
    """Validate result records before registry construction."""

    errors: list[str] = []

    for index, record in enumerate(records):
        record_errors = validate_evaluation_result_record(
            record
        )

        for error in record_errors:
            errors.append(f"source_record_{index}:{error}")

    return errors