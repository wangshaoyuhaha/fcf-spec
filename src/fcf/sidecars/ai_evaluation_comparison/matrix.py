"""Deterministic registered evaluation comparison matrix."""

from __future__ import annotations

from collections import Counter
from collections.abc import Mapping, Sequence
from typing import Any

from .contract import APP_ID
from .schema import validate_comparison_record


MATRIX_VERSION = "1.0.0"

COMPARISON_AXES = (
    "model_id",
    "model_version",
    "prompt_id",
    "prompt_version",
)


def _safety_fields() -> dict[str, bool]:
    return {
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


def _invalid_matrix(errors: list[str]) -> dict[str, Any]:
    return {
        "app_id": APP_ID,
        "matrix_version": MATRIX_VERSION,
        "matrix_status": "INVALID",
        "result_status": "INVALID",
        "comparison_axes": list(COMPARISON_AXES),
        "record_count": 0,
        "sample_count": 0,
        "sample_groups": [],
        "errors": sorted(set(errors)),
        **_safety_fields(),
    }


def _blocked_matrix() -> dict[str, Any]:
    report = _invalid_matrix(["no_comparison_records"])
    report["matrix_status"] = "BLOCKED"
    report["result_status"] = "BLOCKED"
    return report


def _sorted_counts(values: Sequence[str]) -> dict[str, int]:
    counts = Counter(values)
    return {
        key: counts[key]
        for key in sorted(counts)
    }


def _has_cross_version(
    records: Sequence[Mapping[str, Any]],
    *,
    identifier_field: str,
    version_field: str,
) -> bool:
    versions_by_identifier: dict[str, set[str]] = {}

    for record in records:
        identifier = record[identifier_field]
        version = record[version_field]

        versions_by_identifier.setdefault(
            identifier,
            set(),
        ).add(version)

    return any(
        len(versions) > 1
        for versions in versions_by_identifier.values()
    )


def _record_sort_key(
    record: Mapping[str, Any],
) -> tuple[str, ...]:
    return (
        record["evaluation_sample_id"],
        record["model_id"],
        record["model_version"],
        record["prompt_id"],
        record["prompt_version"],
        record["comparison_id"],
    )


def build_registered_comparison_matrix(
    records: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    """Build a deterministic cross-model and cross-version matrix."""

    if isinstance(records, (str, bytes)):
        return _invalid_matrix(["records_invalid"])

    if not isinstance(records, Sequence):
        return _invalid_matrix(["records_invalid"])

    if not records:
        return _blocked_matrix()

    normalized_records: list[dict[str, Any]] = []
    errors: list[str] = []

    for index, record in enumerate(records):
        if not isinstance(record, Mapping):
            errors.append(f"record_not_mapping:{index}")
            continue

        record_errors = validate_comparison_record(record)

        for error in record_errors:
            errors.append(f"record[{index}]:{error}")

        normalized_records.append(dict(record))

    if errors:
        return _invalid_matrix(errors)

    comparison_ids = [
        record["comparison_id"]
        for record in normalized_records
    ]

    duplicate_ids = sorted(
        comparison_id
        for comparison_id, count in Counter(
            comparison_ids
        ).items()
        if count > 1
    )

    if duplicate_ids:
        return _invalid_matrix(
            [
                f"duplicate_comparison_id:{comparison_id}"
                for comparison_id in duplicate_ids
            ]
        )

    ordered_records = sorted(
        normalized_records,
        key=_record_sort_key,
    )

    records_by_sample: dict[str, list[dict[str, Any]]] = {}

    for record in ordered_records:
        sample_id = record["evaluation_sample_id"]
        records_by_sample.setdefault(sample_id, []).append(record)

    sample_groups: list[dict[str, Any]] = []

    for sample_id in sorted(records_by_sample):
        sample_records = records_by_sample[sample_id]

        model_ids = sorted(
            {
                record["model_id"]
                for record in sample_records
            }
        )
        model_versions = sorted(
            {
                record["model_version"]
                for record in sample_records
            }
        )
        prompt_ids = sorted(
            {
                record["prompt_id"]
                for record in sample_records
            }
        )
        prompt_versions = sorted(
            {
                record["prompt_version"]
                for record in sample_records
            }
        )

        members = [
            {
                "comparison_id": record["comparison_id"],
                "model_id": record["model_id"],
                "model_version": record["model_version"],
                "prompt_id": record["prompt_id"],
                "prompt_version": record["prompt_version"],
                "comparison_status": record[
                    "comparison_status"
                ],
                "result_status": record["result_status"],
                "operator_review_status": record[
                    "operator_review_status"
                ],
            }
            for record in sample_records
        ]

        sample_groups.append(
            {
                "evaluation_sample_id": sample_id,
                "record_count": len(sample_records),
                "comparison_ids": [
                    member["comparison_id"]
                    for member in members
                ],
                "model_ids": model_ids,
                "model_versions": model_versions,
                "prompt_ids": prompt_ids,
                "prompt_versions": prompt_versions,
                "cross_model_available": len(model_ids) > 1,
                "cross_model_version_available": (
                    _has_cross_version(
                        sample_records,
                        identifier_field="model_id",
                        version_field="model_version",
                    )
                ),
                "cross_prompt_available": len(prompt_ids) > 1,
                "cross_prompt_version_available": (
                    _has_cross_version(
                        sample_records,
                        identifier_field="prompt_id",
                        version_field="prompt_version",
                    )
                ),
                "comparison_status_counts": _sorted_counts(
                    [
                        record["comparison_status"]
                        for record in sample_records
                    ]
                ),
                "result_status_counts": _sorted_counts(
                    [
                        record["result_status"]
                        for record in sample_records
                    ]
                ),
                "members": members,
            }
        )

    return {
        "app_id": APP_ID,
        "matrix_version": MATRIX_VERSION,
        "matrix_status": "REVIEW_REQUIRED",
        "result_status": "RECORDED",
        "comparison_axes": list(COMPARISON_AXES),
        "record_count": len(ordered_records),
        "sample_count": len(sample_groups),
        "sample_groups": sample_groups,
        "errors": [],
        **_safety_fields(),
    }