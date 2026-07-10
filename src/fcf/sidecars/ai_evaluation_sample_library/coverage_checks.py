"""Coverage and consistency checks for evaluation sample registries."""

from __future__ import annotations

from collections import Counter
from collections.abc import Mapping
from typing import Any

from .contract import APP_ID
from .sample_schema import EVALUATION_DIMENSIONS


COVERAGE_STAGE_ID = "AI-EVALUATION-SAMPLE-LIBRARY-D4"
COVERAGE_SCHEMA_VERSION = "1.0.0"

COVERAGE_STATUSES = (
    "PASS",
    "REVIEW_REQUIRED",
    "FAIL",
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


def _valid_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _entry_key(entry: Mapping[str, Any], index: int) -> str:
    value = entry.get("sample_key")

    if _valid_string(value):
        return str(value)

    return f"invalid-entry-{index}"


def build_evaluation_sample_coverage_report(
    registry: Mapping[str, Any],
) -> dict[str, Any]:
    """Build deterministic coverage checks without model execution."""

    raw_entries = registry.get("entries", [])

    entries = (
        raw_entries
        if isinstance(raw_entries, list)
        else []
    )

    dimension_counts = {
        dimension: 0
        for dimension in EVALUATION_DIMENSIONS
    }

    sample_keys: list[str] = []
    invalid_dimension_keys: list[str] = []
    pending_review_keys: list[str] = []
    evidence_missing_keys: list[str] = []
    registry_reference_missing_keys: list[str] = []

    for index, raw_entry in enumerate(entries):
        if not isinstance(raw_entry, Mapping):
            key = f"invalid-entry-{index}"
            sample_keys.append(key)
            invalid_dimension_keys.append(key)
            evidence_missing_keys.append(key)
            registry_reference_missing_keys.append(key)
            continue

        key = _entry_key(raw_entry, index)
        sample_keys.append(key)

        dimension = raw_entry.get("evaluation_dimension")

        if dimension in dimension_counts:
            dimension_counts[str(dimension)] += 1
        else:
            invalid_dimension_keys.append(key)

        if raw_entry.get("review_status") != "APPROVED":
            pending_review_keys.append(key)

        evidence_refs = raw_entry.get("evidence_refs")

        if (
            not isinstance(evidence_refs, list)
            or not evidence_refs
            or not all(_valid_string(item) for item in evidence_refs)
        ):
            evidence_missing_keys.append(key)

        registry_refs = raw_entry.get(
            "prompt_model_registry_entry_ids"
        )

        if (
            not isinstance(registry_refs, list)
            or not registry_refs
            or not all(_valid_string(item) for item in registry_refs)
        ):
            registry_reference_missing_keys.append(key)

    missing_dimensions = [
        dimension
        for dimension, count in dimension_counts.items()
        if count == 0
    ]

    key_counts = Counter(sample_keys)

    duplicate_sample_keys = sorted(
        key
        for key, count in key_counts.items()
        if count > 1
    )

    hard_failures = any(
        (
            missing_dimensions,
            invalid_dimension_keys,
            duplicate_sample_keys,
            evidence_missing_keys,
            registry_reference_missing_keys,
        )
    )

    if hard_failures:
        coverage_status = "FAIL"
    elif pending_review_keys:
        coverage_status = "REVIEW_REQUIRED"
    else:
        coverage_status = "PASS"

    return {
        "app_id": APP_ID,
        "stage_id": COVERAGE_STAGE_ID,
        "schema_version": COVERAGE_SCHEMA_VERSION,
        "source_registry_id": registry.get("registry_id"),
        "sample_count": len(entries),
        "sample_keys": sample_keys,
        "dimension_counts": dimension_counts,
        "missing_dimensions": missing_dimensions,
        "invalid_dimension_keys": sorted(
            invalid_dimension_keys
        ),
        "duplicate_sample_keys": duplicate_sample_keys,
        "pending_review_keys": sorted(pending_review_keys),
        "evidence_missing_keys": sorted(
            evidence_missing_keys
        ),
        "registry_reference_missing_keys": sorted(
            registry_reference_missing_keys
        ),
        "coverage_status": coverage_status,
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


def _valid_string_list(value: Any) -> bool:
    return (
        isinstance(value, list)
        and all(_valid_string(item) for item in value)
    )


def _expected_coverage_status(
    report: Mapping[str, Any],
) -> str:
    hard_failure_fields = (
        "missing_dimensions",
        "invalid_dimension_keys",
        "duplicate_sample_keys",
        "evidence_missing_keys",
        "registry_reference_missing_keys",
    )

    if any(report.get(field) for field in hard_failure_fields):
        return "FAIL"

    if report.get("pending_review_keys"):
        return "REVIEW_REQUIRED"

    return "PASS"


def validate_evaluation_sample_coverage_report(
    report: Mapping[str, Any],
) -> list[str]:
    """Return deterministic coverage report validation errors."""

    if not isinstance(report, Mapping):
        return ["report_not_mapping"]

    errors: list[str] = []

    expected_identity = {
        "app_id": APP_ID,
        "stage_id": COVERAGE_STAGE_ID,
        "schema_version": COVERAGE_SCHEMA_VERSION,
    }

    for field, expected in expected_identity.items():
        if report.get(field) != expected:
            errors.append(f"{field}_mismatch")

    if not _valid_string(report.get("source_registry_id")):
        errors.append("source_registry_id_invalid")

    sample_keys = report.get("sample_keys")

    if not _valid_string_list(sample_keys):
        errors.append("sample_keys_invalid")
        sample_keys = []

    if report.get("sample_count") != len(sample_keys):
        errors.append("sample_count_mismatch")

    dimension_counts = report.get("dimension_counts")

    if not isinstance(dimension_counts, Mapping):
        errors.append("dimension_counts_invalid")
    else:
        if set(dimension_counts) != set(EVALUATION_DIMENSIONS):
            errors.append("dimension_count_keys_mismatch")

        for value in dimension_counts.values():
            if (
                not isinstance(value, int)
                or isinstance(value, bool)
                or value < 0
            ):
                errors.append("dimension_count_value_invalid")
                break

    list_fields = (
        "missing_dimensions",
        "invalid_dimension_keys",
        "duplicate_sample_keys",
        "pending_review_keys",
        "evidence_missing_keys",
        "registry_reference_missing_keys",
    )

    for field in list_fields:
        if not _valid_string_list(report.get(field)):
            errors.append(f"{field}_invalid")

    status = report.get("coverage_status")

    if status not in COVERAGE_STATUSES:
        errors.append("coverage_status_invalid")
    elif status != _expected_coverage_status(report):
        errors.append("coverage_status_mismatch")

    for field in REQUIRED_TRUE_FLAGS:
        if report.get(field) is not True:
            errors.append(f"{field}_must_be_true")

    for field in REQUIRED_FALSE_FLAGS:
        if report.get(field) is not False:
            errors.append(f"{field}_must_be_false")

    return errors