"""Deterministic time and version windows for AI evaluation drift."""

from __future__ import annotations

from collections import Counter
from collections.abc import Mapping, Sequence
from datetime import datetime
from typing import Any

from .classifier import classify_drift_evidence
from .contract import APP_ID
from .schema import validate_drift_evidence_record


WINDOW_VERSION = "1.0.0"

WINDOW_STATUSES = (
    "NO_DRIFT",
    "REVIEW_REQUIRED",
    "BLOCKED",
    "INVALID",
)

REVIEW_DRIFT_STATUSES = (
    "POTENTIAL_DRIFT",
    "CONFIRMED_DRIFT",
    "INSUFFICIENT_EVIDENCE",
)


def _safety_fields() -> dict[str, bool]:
    return {
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


def _base_window(
    *,
    window_status: str,
    result_status: str,
    errors: list[str],
) -> dict[str, Any]:
    return {
        "app_id": APP_ID,
        "window_version": WINDOW_VERSION,
        "window_status": window_status,
        "result_status": result_status,
        "operator_review_status": "REVIEW_REQUIRED",
        "window_start_utc": None,
        "window_end_utc": None,
        "window_span_seconds": 0,
        "record_count": 0,
        "sample_count": 0,
        "review_required_count": 0,
        "cross_model_version_available": False,
        "cross_prompt_version_available": False,
        "drift_status_counts": {},
        "drift_severity_counts": {},
        "reason_code_counts": {},
        "changed_dimension_counts": {},
        "sample_windows": [],
        "items": [],
        "errors": sorted(set(errors)),
        **_safety_fields(),
    }


def _invalid_window(errors: list[str]) -> dict[str, Any]:
    return _base_window(
        window_status="INVALID",
        result_status="INVALID",
        errors=errors,
    )


def _blocked_window() -> dict[str, Any]:
    return _base_window(
        window_status="BLOCKED",
        result_status="BLOCKED",
        errors=["no_drift_evidence_records"],
    )


def _parse_timestamp(value: str) -> datetime:
    return datetime.fromisoformat(
        value.replace("Z", "+00:00")
    )


def _sorted_counts(values: Sequence[str]) -> dict[str, int]:
    counter = Counter(values)

    return {
        key: counter[key]
        for key in sorted(counter)
    }


def _record_sort_key(
    record: Mapping[str, Any],
) -> tuple[str, str, str]:
    return (
        record["candidate_created_at_utc"],
        record["evaluation_sample_id"],
        record["drift_evidence_id"],
    )


def build_drift_comparison_window(
    records: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    """Build deterministic time and version drift windows."""

    if isinstance(records, (str, bytes)):
        return _invalid_window(["records_invalid"])

    if not isinstance(records, Sequence):
        return _invalid_window(["records_invalid"])

    if not records:
        return _blocked_window()

    normalized_records: list[dict[str, Any]] = []
    errors: list[str] = []

    for index, record in enumerate(records):
        if not isinstance(record, Mapping):
            errors.append(f"record_not_mapping:{index}")
            continue

        record_errors = validate_drift_evidence_record(
            record
        )

        for error in record_errors:
            errors.append(f"record[{index}]:{error}")

        normalized_records.append(dict(record))

    if errors:
        return _invalid_window(errors)

    evidence_ids = [
        record["drift_evidence_id"]
        for record in normalized_records
    ]

    duplicate_ids = sorted(
        evidence_id
        for evidence_id, count in Counter(
            evidence_ids
        ).items()
        if count > 1
    )

    if duplicate_ids:
        return _invalid_window(
            [
                f"duplicate_drift_evidence_id:{evidence_id}"
                for evidence_id in duplicate_ids
            ]
        )

    ordered_records = sorted(
        normalized_records,
        key=_record_sort_key,
    )

    items: list[dict[str, Any]] = []

    for record in ordered_records:
        classification = classify_drift_evidence(
            record
        )

        items.append(
            {
                "drift_evidence_id": record[
                    "drift_evidence_id"
                ],
                "evaluation_sample_id": record[
                    "evaluation_sample_id"
                ],
                "baseline_reference": record[
                    "baseline_reference"
                ],
                "candidate_reference": record[
                    "candidate_reference"
                ],
                "baseline_created_at_utc": record[
                    "baseline_created_at_utc"
                ],
                "candidate_created_at_utc": record[
                    "candidate_created_at_utc"
                ],
                "model_id": record["model_id"],
                "baseline_model_version": record[
                    "baseline_model_version"
                ],
                "candidate_model_version": record[
                    "candidate_model_version"
                ],
                "prompt_id": record["prompt_id"],
                "baseline_prompt_version": record[
                    "baseline_prompt_version"
                ],
                "candidate_prompt_version": record[
                    "candidate_prompt_version"
                ],
                "drift_status": classification[
                    "drift_status"
                ],
                "drift_severity": classification[
                    "drift_severity"
                ],
                "changed_dimensions": list(
                    classification["changed_dimensions"]
                ),
                "reason_codes": list(
                    classification["reason_codes"]
                ),
                "operator_review_status": (
                    "REVIEW_REQUIRED"
                ),
            }
        )

    window_start = min(
        _parse_timestamp(
            record["baseline_created_at_utc"]
        )
        for record in ordered_records
    )
    window_end = max(
        _parse_timestamp(
            record["candidate_created_at_utc"]
        )
        for record in ordered_records
    )

    drift_status_counts = _sorted_counts(
        [item["drift_status"] for item in items]
    )
    drift_severity_counts = _sorted_counts(
        [item["drift_severity"] for item in items]
    )

    reason_codes = [
        reason
        for item in items
        for reason in item["reason_codes"]
    ]

    changed_dimensions = [
        dimension
        for item in items
        for dimension in item["changed_dimensions"]
    ]

    review_required_count = sum(
        item["drift_status"] in REVIEW_DRIFT_STATUSES
        for item in items
    )

    window_status = (
        "REVIEW_REQUIRED"
        if review_required_count > 0
        else "NO_DRIFT"
    )

    records_by_sample: dict[
        str,
        list[dict[str, Any]],
    ] = {}

    for item in items:
        sample_id = item["evaluation_sample_id"]
        records_by_sample.setdefault(
            sample_id,
            [],
        ).append(item)

    sample_windows: list[dict[str, Any]] = []

    for sample_id in sorted(records_by_sample):
        sample_items = records_by_sample[sample_id]

        sample_start = min(
            _parse_timestamp(
                item["baseline_created_at_utc"]
            )
            for item in sample_items
        )
        sample_end = max(
            _parse_timestamp(
                item["candidate_created_at_utc"]
            )
            for item in sample_items
        )

        sample_windows.append(
            {
                "evaluation_sample_id": sample_id,
                "record_count": len(sample_items),
                "window_start_utc": sample_start.isoformat(),
                "window_end_utc": sample_end.isoformat(),
                "window_span_seconds": int(
                    (sample_end - sample_start).total_seconds()
                ),
                "drift_evidence_ids": [
                    item["drift_evidence_id"]
                    for item in sample_items
                ],
                "drift_status_counts": _sorted_counts(
                    [
                        item["drift_status"]
                        for item in sample_items
                    ]
                ),
                "drift_severity_counts": _sorted_counts(
                    [
                        item["drift_severity"]
                        for item in sample_items
                    ]
                ),
                "review_required": any(
                    item["drift_status"]
                    in REVIEW_DRIFT_STATUSES
                    for item in sample_items
                ),
            }
        )

    return {
        "app_id": APP_ID,
        "window_version": WINDOW_VERSION,
        "window_status": window_status,
        "result_status": "RECORDED",
        "operator_review_status": "REVIEW_REQUIRED",
        "window_start_utc": window_start.isoformat(),
        "window_end_utc": window_end.isoformat(),
        "window_span_seconds": int(
            (window_end - window_start).total_seconds()
        ),
        "record_count": len(items),
        "sample_count": len(sample_windows),
        "review_required_count": review_required_count,
        "cross_model_version_available": any(
            item["baseline_model_version"]
            != item["candidate_model_version"]
            for item in items
        ),
        "cross_prompt_version_available": any(
            item["baseline_prompt_version"]
            != item["candidate_prompt_version"]
            for item in items
        ),
        "drift_status_counts": drift_status_counts,
        "drift_severity_counts": drift_severity_counts,
        "reason_code_counts": _sorted_counts(
            reason_codes
        ),
        "changed_dimension_counts": _sorted_counts(
            changed_dimensions
        ),
        "sample_windows": sample_windows,
        "items": items,
        "errors": [],
        **_safety_fields(),
    }