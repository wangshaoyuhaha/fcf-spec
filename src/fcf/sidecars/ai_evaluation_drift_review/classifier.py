"""Deterministic classifier for registered AI evaluation drift evidence."""

from __future__ import annotations

from collections.abc import Mapping
from datetime import datetime
from typing import Any

from .contract import APP_ID
from .schema import validate_drift_evidence_record


CLASSIFIER_VERSION = "1.0.0"

DRIFT_SEVERITIES = (
    "NONE",
    "LOW",
    "MEDIUM",
    "HIGH",
)

COMPARABLE_STATUSES = (
    "MATCHED",
    "PARTIAL_MATCH",
    "MISMATCH",
)

DRIFT_REASON_CODES = (
    "NO_MATERIAL_CHANGE",
    "MODEL_VERSION_CHANGED",
    "PROMPT_VERSION_CHANGED",
    "COMPARISON_STATUS_CHANGED",
    "CANDIDATE_WORSE_THAN_BASELINE",
    "CANDIDATE_IMPROVED_FROM_BASELINE",
    "SOURCE_COMPARISON_NOT_COMPARABLE",
)

_STATUS_RANK = {
    "MATCHED": 0,
    "PARTIAL_MATCH": 1,
    "MISMATCH": 2,
}


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


def _parse_timestamp(value: str) -> datetime:
    return datetime.fromisoformat(
        value.replace("Z", "+00:00")
    )


def _base_report(
    record: Mapping[str, Any] | None,
) -> dict[str, Any]:
    source = record or {}

    return {
        "app_id": APP_ID,
        "classifier_version": CLASSIFIER_VERSION,
        "drift_evidence_id": source.get(
            "drift_evidence_id"
        ),
        "evaluation_sample_id": source.get(
            "evaluation_sample_id"
        ),
        "baseline_reference": source.get(
            "baseline_reference"
        ),
        "candidate_reference": source.get(
            "candidate_reference"
        ),
        "baseline_comparison_status": source.get(
            "baseline_comparison_status"
        ),
        "candidate_comparison_status": source.get(
            "candidate_comparison_status"
        ),
        "changed_dimensions": [],
        "reason_codes": [],
        "drift_status": "INVALID",
        "drift_severity": "NONE",
        "result_status": "INVALID",
        "operator_review_status": "REVIEW_REQUIRED",
        "elapsed_seconds": None,
        "errors": [],
        **_safety_fields(),
    }


def _invalid_report(
    record: Mapping[str, Any] | None,
    errors: list[str],
) -> dict[str, Any]:
    report = _base_report(record)
    report["errors"] = sorted(set(errors))
    return report


def _insufficient_report(
    record: Mapping[str, Any],
    *,
    elapsed_seconds: int,
) -> dict[str, Any]:
    report = _base_report(record)
    report.update(
        {
            "drift_status": "INSUFFICIENT_EVIDENCE",
            "drift_severity": "MEDIUM",
            "result_status": "RECORDED",
            "elapsed_seconds": elapsed_seconds,
            "reason_codes": [
                "SOURCE_COMPARISON_NOT_COMPARABLE"
            ],
            "errors": [],
        }
    )
    return report


def classify_drift_evidence(
    record: Mapping[str, Any],
) -> dict[str, Any]:
    """Classify registered drift evidence without source mutation."""

    if not isinstance(record, Mapping):
        return _invalid_report(
            None,
            ["record_not_mapping"],
        )

    validation_errors = validate_drift_evidence_record(
        record
    )

    if validation_errors:
        return _invalid_report(
            record,
            validation_errors,
        )

    baseline_time = _parse_timestamp(
        record["baseline_created_at_utc"]
    )
    candidate_time = _parse_timestamp(
        record["candidate_created_at_utc"]
    )
    elapsed_seconds = int(
        (candidate_time - baseline_time).total_seconds()
    )

    baseline_status = record[
        "baseline_comparison_status"
    ]
    candidate_status = record[
        "candidate_comparison_status"
    ]

    if (
        baseline_status not in COMPARABLE_STATUSES
        or candidate_status not in COMPARABLE_STATUSES
    ):
        return _insufficient_report(
            record,
            elapsed_seconds=elapsed_seconds,
        )

    changed_dimensions: list[str] = []
    reason_codes: list[str] = []

    model_version_changed = (
        record["baseline_model_version"]
        != record["candidate_model_version"]
    )
    prompt_version_changed = (
        record["baseline_prompt_version"]
        != record["candidate_prompt_version"]
    )
    comparison_status_changed = (
        baseline_status != candidate_status
    )

    if model_version_changed:
        changed_dimensions.append("model_version")
        reason_codes.append("MODEL_VERSION_CHANGED")

    if prompt_version_changed:
        changed_dimensions.append("prompt_version")
        reason_codes.append("PROMPT_VERSION_CHANGED")

    if comparison_status_changed:
        changed_dimensions.append("comparison_status")
        reason_codes.append("COMPARISON_STATUS_CHANGED")

    baseline_rank = _STATUS_RANK[baseline_status]
    candidate_rank = _STATUS_RANK[candidate_status]
    rank_delta = candidate_rank - baseline_rank

    if rank_delta > 0:
        drift_status = "CONFIRMED_DRIFT"
        drift_severity = (
            "HIGH"
            if rank_delta > 1
            else "MEDIUM"
        )
        reason_codes.append(
            "CANDIDATE_WORSE_THAN_BASELINE"
        )

    elif rank_delta < 0:
        drift_status = "POTENTIAL_DRIFT"
        drift_severity = (
            "MEDIUM"
            if model_version_changed
            and prompt_version_changed
            else "LOW"
        )
        reason_codes.append(
            "CANDIDATE_IMPROVED_FROM_BASELINE"
        )

    elif model_version_changed or prompt_version_changed:
        drift_status = "POTENTIAL_DRIFT"
        drift_severity = (
            "MEDIUM"
            if model_version_changed
            and prompt_version_changed
            else "LOW"
        )

    else:
        drift_status = "NO_DRIFT"
        drift_severity = "NONE"
        reason_codes.append("NO_MATERIAL_CHANGE")

    report = _base_report(record)
    report.update(
        {
            "changed_dimensions": sorted(
                changed_dimensions
            ),
            "reason_codes": sorted(
                set(reason_codes)
            ),
            "drift_status": drift_status,
            "drift_severity": drift_severity,
            "result_status": "RECORDED",
            "elapsed_seconds": elapsed_seconds,
            "errors": [],
        }
    )

    return report