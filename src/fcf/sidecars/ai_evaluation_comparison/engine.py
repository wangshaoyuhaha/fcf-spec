"""Deterministic expected-versus-observed comparison engine."""

from __future__ import annotations

import math
from collections.abc import Mapping, Sequence
from typing import Any

from .contract import APP_ID


ENGINE_VERSION = "1.0.0"

FIELD_STATUSES = (
    "MATCH",
    "MISMATCH",
    "MISSING_EXPECTED",
    "MISSING_OBSERVED",
)

VALID_COMPARISON_STATUSES = (
    "MATCHED",
    "PARTIAL_MATCH",
    "MISMATCH",
    "INVALID",
    "BLOCKED",
)


def _is_json_value(value: Any) -> bool:
    if value is None or isinstance(value, (str, bool, int)):
        return True

    if isinstance(value, float):
        return math.isfinite(value)

    if isinstance(value, list):
        return all(_is_json_value(item) for item in value)

    if isinstance(value, Mapping):
        return all(
            isinstance(key, str) and _is_json_value(item)
            for key, item in value.items()
        )

    return False


def _canonicalize(value: Any) -> Any:
    if isinstance(value, Mapping):
        return tuple(
            (
                key,
                _canonicalize(value[key]),
            )
            for key in sorted(value)
        )

    if isinstance(value, list):
        return tuple(_canonicalize(item) for item in value)

    return value


def _validate_comparison_fields(
    comparison_fields: Sequence[str] | None,
) -> list[str]:
    if comparison_fields is None:
        return []

    if isinstance(comparison_fields, (str, bytes)):
        return ["comparison_fields_invalid"]

    if not isinstance(comparison_fields, Sequence):
        return ["comparison_fields_invalid"]

    if not comparison_fields:
        return ["comparison_fields_empty"]

    errors: list[str] = []

    for field in comparison_fields:
        if not isinstance(field, str) or not field.strip():
            errors.append("comparison_fields_invalid")

    if len(set(comparison_fields)) != len(comparison_fields):
        errors.append("comparison_fields_duplicate")

    return sorted(set(errors))


def _build_invalid_report(errors: list[str]) -> dict[str, Any]:
    return {
        "app_id": APP_ID,
        "engine_version": ENGINE_VERSION,
        "comparison_status": "INVALID",
        "result_status": "INVALID",
        "operator_review_status": "REVIEW_REQUIRED",
        "field_results": [],
        "matched_fields": [],
        "mismatched_fields": [],
        "missing_expected_fields": [],
        "missing_observed_fields": [],
        "compared_field_count": 0,
        "matched_field_count": 0,
        "difference_field_count": 0,
        "errors": sorted(set(errors)),
        "paper_only": True,
        "local_only": True,
        "read_only": True,
        "sidecar_only": True,
        "operator_review_required": True,
        "automatic_acceptance_allowed": False,
        "model_invocation_allowed": False,
        "prompt_execution_allowed": False,
        "trade_action_allowed": False,
        "real_execution_allowed": False,
        "core_mutation_allowed": False,
    }


def _build_blocked_report() -> dict[str, Any]:
    report = _build_invalid_report([])
    report["comparison_status"] = "BLOCKED"
    report["result_status"] = "BLOCKED"
    report["errors"] = ["no_comparison_fields"]
    return report


def compare_expected_observed(
    expected_result: Mapping[str, Any],
    observed_result: Mapping[str, Any],
    *,
    comparison_fields: Sequence[str] | None = None,
) -> dict[str, Any]:
    """Compare local registered expected and observed result mappings."""

    errors: list[str] = []

    if not isinstance(expected_result, Mapping):
        errors.append("expected_result_not_mapping")

    if not isinstance(observed_result, Mapping):
        errors.append("observed_result_not_mapping")

    errors.extend(_validate_comparison_fields(comparison_fields))

    if errors:
        return _build_invalid_report(errors)

    if not _is_json_value(expected_result):
        errors.append("expected_result_not_json_safe")

    if not _is_json_value(observed_result):
        errors.append("observed_result_not_json_safe")

    if errors:
        return _build_invalid_report(errors)

    if comparison_fields is None:
        fields = sorted(
            set(expected_result) | set(observed_result)
        )
    else:
        fields = sorted(comparison_fields)

    if not fields:
        return _build_blocked_report()

    field_results: list[dict[str, Any]] = []
    matched_fields: list[str] = []
    mismatched_fields: list[str] = []
    missing_expected_fields: list[str] = []
    missing_observed_fields: list[str] = []

    for field in fields:
        expected_present = field in expected_result
        observed_present = field in observed_result

        if expected_present and observed_present:
            expected_value = expected_result[field]
            observed_value = observed_result[field]

            if _canonicalize(expected_value) == _canonicalize(
                observed_value
            ):
                field_status = "MATCH"
                matched_fields.append(field)
            else:
                field_status = "MISMATCH"
                mismatched_fields.append(field)

        elif observed_present:
            expected_value = None
            observed_value = observed_result[field]
            field_status = "MISSING_EXPECTED"
            missing_expected_fields.append(field)

        else:
            expected_value = expected_result[field]
            observed_value = None
            field_status = "MISSING_OBSERVED"
            missing_observed_fields.append(field)

        field_results.append(
            {
                "field": field,
                "field_status": field_status,
                "expected_present": expected_present,
                "observed_present": observed_present,
                "expected_value": expected_value,
                "observed_value": observed_value,
            }
        )

    matched_count = len(matched_fields)
    difference_count = (
        len(mismatched_fields)
        + len(missing_expected_fields)
        + len(missing_observed_fields)
    )

    if difference_count == 0:
        comparison_status = "MATCHED"
    elif matched_count > 0:
        comparison_status = "PARTIAL_MATCH"
    else:
        comparison_status = "MISMATCH"

    return {
        "app_id": APP_ID,
        "engine_version": ENGINE_VERSION,
        "comparison_status": comparison_status,
        "result_status": "RECORDED",
        "operator_review_status": "REVIEW_REQUIRED",
        "field_results": field_results,
        "matched_fields": matched_fields,
        "mismatched_fields": mismatched_fields,
        "missing_expected_fields": missing_expected_fields,
        "missing_observed_fields": missing_observed_fields,
        "compared_field_count": len(fields),
        "matched_field_count": matched_count,
        "difference_field_count": difference_count,
        "errors": [],
        "paper_only": True,
        "local_only": True,
        "read_only": True,
        "sidecar_only": True,
        "operator_review_required": True,
        "automatic_acceptance_allowed": False,
        "model_invocation_allowed": False,
        "prompt_execution_allowed": False,
        "trade_action_allowed": False,
        "real_execution_allowed": False,
        "core_mutation_allowed": False,
    }