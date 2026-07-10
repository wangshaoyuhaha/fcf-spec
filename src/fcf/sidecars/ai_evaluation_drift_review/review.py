"""Governance review packet for registered AI evaluation drift."""

from __future__ import annotations

from collections import Counter
from collections.abc import Mapping
from typing import Any

from .classifier import DRIFT_SEVERITIES
from .contract import APP_ID
from .window import WINDOW_STATUSES, WINDOW_VERSION


REVIEW_PACKET_VERSION = "1.0.0"

REVIEW_PRIORITIES = (
    "LOW",
    "MEDIUM",
    "HIGH",
)

REVIEWABLE_DRIFT_STATUSES = (
    "NO_DRIFT",
    "POTENTIAL_DRIFT",
    "CONFIRMED_DRIFT",
    "INSUFFICIENT_EVIDENCE",
)

PROHIBITED_REVIEW_ACTIONS = (
    "automatic_drift_approval",
    "automatic_drift_rejection",
    "automatic_model_ranking",
    "automatic_model_selection",
    "automatic_prompt_selection",
    "automatic_model_switch",
    "automatic_prompt_switch",
    "automatic_rollback",
    "trade_action",
    "real_execution",
    "core_mutation",
)

REQUIRED_WINDOW_FIELDS = (
    "app_id",
    "window_version",
    "window_status",
    "result_status",
    "record_count",
    "sample_count",
    "review_required_count",
    "drift_status_counts",
    "drift_severity_counts",
    "items",
    "errors",
)

REQUIRED_ITEM_FIELDS = (
    "drift_evidence_id",
    "evaluation_sample_id",
    "baseline_reference",
    "candidate_reference",
    "baseline_created_at_utc",
    "candidate_created_at_utc",
    "drift_status",
    "drift_severity",
    "changed_dimensions",
    "reason_codes",
    "operator_review_status",
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
        "automatic_model_ranking_allowed": False,
        "automatic_model_selection_allowed": False,
        "automatic_prompt_selection_allowed": False,
        "automatic_model_switch_allowed": False,
        "automatic_prompt_switch_allowed": False,
        "trade_action_allowed": False,
        "real_execution_allowed": False,
    }


def _base_packet(
    *,
    packet_status: str,
    result_status: str,
    errors: list[str],
) -> dict[str, Any]:
    return {
        "app_id": APP_ID,
        "review_packet_version": REVIEW_PACKET_VERSION,
        "packet_status": packet_status,
        "result_status": result_status,
        "operator_review_status": "REVIEW_REQUIRED",
        "source_window_version": WINDOW_VERSION,
        "source_window_status": None,
        "sample_count": 0,
        "review_item_count": 0,
        "priority_counts": {},
        "review_items": [],
        "required_action": "human_operator_drift_review",
        "prohibited_actions": list(
            PROHIBITED_REVIEW_ACTIONS
        ),
        "errors": sorted(set(errors)),
        **_safety_fields(),
    }


def _invalid_packet(errors: list[str]) -> dict[str, Any]:
    return _base_packet(
        packet_status="INVALID",
        result_status="INVALID",
        errors=errors,
    )


def _blocked_packet(errors: list[str]) -> dict[str, Any]:
    return _base_packet(
        packet_status="BLOCKED",
        result_status="BLOCKED",
        errors=errors,
    )


def _is_non_negative_int(value: Any) -> bool:
    return (
        isinstance(value, int)
        and not isinstance(value, bool)
        and value >= 0
    )


def _is_non_empty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _is_string_list(
    value: Any,
    *,
    allow_empty: bool,
) -> bool:
    if not isinstance(value, list):
        return False

    if not allow_empty and not value:
        return False

    return all(
        _is_non_empty_string(item)
        for item in value
    )


def _validate_count_mapping(value: Any) -> bool:
    if not isinstance(value, Mapping):
        return False

    return all(
        _is_non_empty_string(key)
        and _is_non_negative_int(count)
        for key, count in value.items()
    )


def _validate_window_item(
    item: Mapping[str, Any],
    *,
    index: int,
) -> list[str]:
    errors: list[str] = []

    for field in REQUIRED_ITEM_FIELDS:
        if field not in item:
            errors.append(
                f"window_item[{index}]:missing_field:{field}"
            )

    for field in (
        "drift_evidence_id",
        "evaluation_sample_id",
        "baseline_reference",
        "candidate_reference",
        "baseline_created_at_utc",
        "candidate_created_at_utc",
    ):
        if not _is_non_empty_string(item.get(field)):
            errors.append(
                f"window_item[{index}]:{field}_invalid"
            )

    if item.get("drift_status") not in (
        REVIEWABLE_DRIFT_STATUSES
    ):
        errors.append(
            f"window_item[{index}]:drift_status_invalid"
        )

    if item.get("drift_severity") not in DRIFT_SEVERITIES:
        errors.append(
            f"window_item[{index}]:drift_severity_invalid"
        )

    if not _is_string_list(
        item.get("changed_dimensions"),
        allow_empty=True,
    ):
        errors.append(
            f"window_item[{index}]:"
            "changed_dimensions_invalid"
        )

    if not _is_string_list(
        item.get("reason_codes"),
        allow_empty=False,
    ):
        errors.append(
            f"window_item[{index}]:reason_codes_invalid"
        )

    if item.get("operator_review_status") != (
        "REVIEW_REQUIRED"
    ):
        errors.append(
            f"window_item[{index}]:"
            "operator_review_status_invalid"
        )

    return errors


def _validate_source_window(
    window: Mapping[str, Any],
) -> list[str]:
    errors: list[str] = []

    for field in REQUIRED_WINDOW_FIELDS:
        if field not in window:
            errors.append(f"missing_window_field:{field}")

    if window.get("app_id") != APP_ID:
        errors.append("window_app_id_mismatch")

    if window.get("window_version") != WINDOW_VERSION:
        errors.append("window_version_mismatch")

    if window.get("window_status") not in WINDOW_STATUSES:
        errors.append("window_status_invalid")

    for field in (
        "record_count",
        "sample_count",
        "review_required_count",
    ):
        if not _is_non_negative_int(window.get(field)):
            errors.append(f"{field}_invalid")

    if not _validate_count_mapping(
        window.get("drift_status_counts")
    ):
        errors.append("drift_status_counts_invalid")

    if not _validate_count_mapping(
        window.get("drift_severity_counts")
    ):
        errors.append("drift_severity_counts_invalid")

    items = window.get("items")

    if not isinstance(items, list):
        errors.append("window_items_invalid")
    else:
        for index, item in enumerate(items):
            if not isinstance(item, Mapping):
                errors.append(
                    f"window_item_not_mapping:{index}"
                )
                continue

            errors.extend(
                _validate_window_item(
                    item,
                    index=index,
                )
            )

    if not _is_string_list(
        window.get("errors"),
        allow_empty=True,
    ):
        errors.append("window_errors_invalid")

    record_count = window.get("record_count")
    review_required_count = window.get(
        "review_required_count"
    )

    if (
        isinstance(items, list)
        and _is_non_negative_int(record_count)
        and record_count != len(items)
    ):
        errors.append("window_record_count_mismatch")

    if (
        _is_non_negative_int(record_count)
        and _is_non_negative_int(review_required_count)
        and review_required_count > record_count
    ):
        errors.append(
            "review_required_count_exceeds_record_count"
        )

    if (
        window.get("window_status") == "NO_DRIFT"
        and review_required_count != 0
    ):
        errors.append(
            "no_drift_window_has_review_required_count"
        )

    if (
        window.get("window_status") == "REVIEW_REQUIRED"
        and review_required_count == 0
    ):
        errors.append(
            "review_required_window_has_zero_review_count"
        )

    return sorted(set(errors))


def _priority_and_reasons(
    item: Mapping[str, Any],
) -> tuple[str, list[str]]:
    drift_status = item["drift_status"]
    severity = item["drift_severity"]
    changed_dimensions = item["changed_dimensions"]

    reasons: list[str] = []

    if drift_status == "CONFIRMED_DRIFT":
        if severity == "HIGH":
            priority = "HIGH"
            reasons.append(
                "confirmed_drift_high_severity"
            )
        else:
            priority = "MEDIUM"
            reasons.append("confirmed_drift_detected")

    elif drift_status == "INSUFFICIENT_EVIDENCE":
        priority = "HIGH"
        reasons.append(
            "insufficient_evidence_requires_review"
        )

    elif drift_status == "POTENTIAL_DRIFT":
        if severity == "MEDIUM":
            priority = "MEDIUM"
            reasons.append(
                "potential_drift_multi_dimension"
            )
        else:
            priority = "LOW"
            reasons.append("potential_drift_detected")

    else:
        priority = "LOW"
        reasons.append(
            "no_drift_evidence_registered"
        )

    if "model_version" in changed_dimensions:
        reasons.append("model_version_change_registered")

    if "prompt_version" in changed_dimensions:
        reasons.append("prompt_version_change_registered")

    if "comparison_status" in changed_dimensions:
        reasons.append(
            "comparison_status_change_registered"
        )

    return priority, sorted(set(reasons))


def build_drift_review_packet(
    window: Mapping[str, Any],
) -> dict[str, Any]:
    """Build a deterministic operator-only drift review packet."""

    if not isinstance(window, Mapping):
        return _invalid_packet(
            ["source_window_not_mapping"]
        )

    validation_errors = _validate_source_window(window)

    if validation_errors:
        return _invalid_packet(validation_errors)

    window_status = window["window_status"]

    if window_status == "INVALID":
        source_errors = [
            f"source_window:{error}"
            for error in window["errors"]
        ]

        return _invalid_packet(
            [
                "source_window_invalid",
                *source_errors,
            ]
        )

    if window_status == "BLOCKED":
        source_errors = [
            f"source_window:{error}"
            for error in window["errors"]
        ]

        return _blocked_packet(
            [
                "source_window_blocked",
                *source_errors,
            ]
        )

    items = window["items"]

    if not items:
        return _blocked_packet(
            ["no_window_items_for_drift_review"]
        )

    ordered_items = sorted(
        items,
        key=lambda item: (
            item["evaluation_sample_id"],
            item["drift_evidence_id"],
        ),
    )

    review_items: list[dict[str, Any]] = []

    for item in ordered_items:
        priority, review_reasons = (
            _priority_and_reasons(item)
        )

        review_items.append(
            {
                "drift_evidence_id": item[
                    "drift_evidence_id"
                ],
                "evaluation_sample_id": item[
                    "evaluation_sample_id"
                ],
                "priority": priority,
                "drift_status": item["drift_status"],
                "drift_severity": item[
                    "drift_severity"
                ],
                "baseline_reference": item[
                    "baseline_reference"
                ],
                "candidate_reference": item[
                    "candidate_reference"
                ],
                "changed_dimensions": list(
                    item["changed_dimensions"]
                ),
                "reason_codes": list(
                    item["reason_codes"]
                ),
                "review_reasons": review_reasons,
                "required_action": (
                    "operator_review_drift_evidence"
                ),
                "operator_review_status": (
                    "REVIEW_REQUIRED"
                ),
                "automatic_approval_allowed": False,
                "automatic_rejection_allowed": False,
                "automatic_rollback_allowed": False,
                "automatic_model_switch_allowed": False,
                "automatic_prompt_switch_allowed": False,
                "trade_action_allowed": False,
            }
        )

    priority_counter = Counter(
        item["priority"]
        for item in review_items
    )

    priority_counts = {
        priority: priority_counter[priority]
        for priority in REVIEW_PRIORITIES
        if priority_counter[priority] > 0
    }

    return {
        "app_id": APP_ID,
        "review_packet_version": REVIEW_PACKET_VERSION,
        "packet_status": "REVIEW_REQUIRED",
        "result_status": "RECORDED",
        "operator_review_status": "REVIEW_REQUIRED",
        "source_window_version": window[
            "window_version"
        ],
        "source_window_status": window_status,
        "sample_count": window["sample_count"],
        "review_item_count": len(review_items),
        "priority_counts": priority_counts,
        "review_items": review_items,
        "required_action": "human_operator_drift_review",
        "prohibited_actions": list(
            PROHIBITED_REVIEW_ACTIONS
        ),
        "errors": [],
        **_safety_fields(),
    }