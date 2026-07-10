"""Governance review packet for AI evaluation comparisons."""

from __future__ import annotations

from collections import Counter
from collections.abc import Mapping
from typing import Any

from .contract import APP_ID
from .matrix import MATRIX_VERSION


REVIEW_PACKET_VERSION = "1.0.0"

REVIEW_PRIORITIES = (
    "LOW",
    "MEDIUM",
    "HIGH",
)

PROHIBITED_REVIEW_ACTIONS = (
    "automatic_evaluation_acceptance",
    "automatic_model_ranking",
    "automatic_model_selection",
    "automatic_prompt_selection",
    "automatic_winner_selection",
    "trade_action",
    "real_execution",
    "core_mutation",
)

REQUIRED_MATRIX_FIELDS = (
    "app_id",
    "matrix_version",
    "matrix_status",
    "result_status",
    "record_count",
    "sample_count",
    "sample_groups",
    "errors",
)


def _safety_fields() -> dict[str, bool]:
    return {
        "paper_only": True,
        "local_only": True,
        "read_only": True,
        "sidecar_only": True,
        "operator_review_required": True,
        "automatic_acceptance_allowed": False,
        "automatic_model_ranking_allowed": False,
        "automatic_model_selection_allowed": False,
        "automatic_prompt_selection_allowed": False,
        "automatic_winner_selection_allowed": False,
        "model_invocation_allowed": False,
        "prompt_execution_allowed": False,
        "trade_action_allowed": False,
        "real_execution_allowed": False,
        "core_mutation_allowed": False,
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
        "source_matrix_version": MATRIX_VERSION,
        "sample_count": 0,
        "review_item_count": 0,
        "priority_counts": {},
        "review_items": [],
        "required_action": (
            "human_operator_review_comparison_evidence"
        ),
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


def _validate_source_matrix(
    matrix: Mapping[str, Any],
) -> list[str]:
    errors: list[str] = []

    for field in REQUIRED_MATRIX_FIELDS:
        if field not in matrix:
            errors.append(f"missing_matrix_field:{field}")

    if matrix.get("app_id") != APP_ID:
        errors.append("matrix_app_id_mismatch")

    if matrix.get("matrix_version") != MATRIX_VERSION:
        errors.append("matrix_version_mismatch")

    if matrix.get("matrix_status") not in {
        "REVIEW_REQUIRED",
        "INVALID",
        "BLOCKED",
    }:
        errors.append("matrix_status_invalid")

    if not _is_non_negative_int(
        matrix.get("record_count")
    ):
        errors.append("matrix_record_count_invalid")

    if not _is_non_negative_int(
        matrix.get("sample_count")
    ):
        errors.append("matrix_sample_count_invalid")

    if not isinstance(matrix.get("sample_groups"), list):
        errors.append("matrix_sample_groups_invalid")

    if not isinstance(matrix.get("errors"), list):
        errors.append("matrix_errors_invalid")

    return sorted(set(errors))


def _validate_sample_group(
    group: Mapping[str, Any],
    *,
    index: int,
) -> list[str]:
    errors: list[str] = []

    sample_id = group.get("evaluation_sample_id")

    if not isinstance(sample_id, str) or not sample_id.strip():
        errors.append(
            f"sample_group[{index}]:sample_id_invalid"
        )

    record_count = group.get("record_count")

    if (
        not _is_non_negative_int(record_count)
        or record_count < 1
    ):
        errors.append(
            f"sample_group[{index}]:record_count_invalid"
        )

    comparison_ids = group.get("comparison_ids")

    if not isinstance(comparison_ids, list):
        errors.append(
            f"sample_group[{index}]:comparison_ids_invalid"
        )
    elif (
        not comparison_ids
        or any(
            not isinstance(item, str) or not item.strip()
            for item in comparison_ids
        )
    ):
        errors.append(
            f"sample_group[{index}]:comparison_ids_invalid"
        )

    for field in (
        "comparison_status_counts",
        "result_status_counts",
    ):
        counts = group.get(field)

        if not isinstance(counts, Mapping):
            errors.append(
                f"sample_group[{index}]:{field}_invalid"
            )
            continue

        if any(
            not isinstance(key, str)
            or not _is_non_negative_int(value)
            for key, value in counts.items()
        ):
            errors.append(
                f"sample_group[{index}]:{field}_invalid"
            )

    for field in (
        "cross_model_available",
        "cross_model_version_available",
        "cross_prompt_available",
        "cross_prompt_version_available",
    ):
        if not isinstance(group.get(field), bool):
            errors.append(
                f"sample_group[{index}]:{field}_invalid"
            )

    return errors


def _priority_and_reasons(
    group: Mapping[str, Any],
) -> tuple[str, list[str]]:
    comparison_counts = group[
        "comparison_status_counts"
    ]
    result_counts = group["result_status_counts"]

    invalid_or_blocked = (
        comparison_counts.get("INVALID", 0)
        + comparison_counts.get("BLOCKED", 0)
        + result_counts.get("INVALID", 0)
        + result_counts.get("BLOCKED", 0)
    )

    mismatch_count = comparison_counts.get(
        "MISMATCH",
        0,
    )
    partial_count = comparison_counts.get(
        "PARTIAL_MATCH",
        0,
    )

    cross_dimension = any(
        group[field]
        for field in (
            "cross_model_available",
            "cross_model_version_available",
            "cross_prompt_available",
            "cross_prompt_version_available",
        )
    )

    reasons: list[str] = []

    if invalid_or_blocked > 0:
        priority = "HIGH"
        reasons.append(
            "invalid_or_blocked_evaluation_evidence"
        )

    elif mismatch_count > 0:
        priority = "HIGH"
        reasons.append(
            "expected_observed_mismatch_detected"
        )

    elif partial_count > 0:
        priority = "MEDIUM"
        reasons.append(
            "partial_expected_observed_match_detected"
        )

    elif cross_dimension:
        priority = "MEDIUM"
        reasons.append(
            "cross_version_or_cross_model_review_required"
        )

    else:
        priority = "LOW"
        reasons.append(
            "registered_comparison_evidence_available"
        )

    if group["cross_model_available"]:
        reasons.append("cross_model_evidence_available")

    if group["cross_model_version_available"]:
        reasons.append(
            "cross_model_version_evidence_available"
        )

    if group["cross_prompt_available"]:
        reasons.append("cross_prompt_evidence_available")

    if group["cross_prompt_version_available"]:
        reasons.append(
            "cross_prompt_version_evidence_available"
        )

    return priority, sorted(set(reasons))


def build_comparison_review_packet(
    matrix: Mapping[str, Any],
) -> dict[str, Any]:
    """Build a deterministic operator-review-only packet."""

    if not isinstance(matrix, Mapping):
        return _invalid_packet(
            ["source_matrix_not_mapping"]
        )

    source_errors = _validate_source_matrix(matrix)

    if source_errors:
        return _invalid_packet(source_errors)

    matrix_status = matrix["matrix_status"]

    if matrix_status == "INVALID":
        matrix_errors = [
            f"source_matrix:{error}"
            for error in matrix["errors"]
        ]

        return _invalid_packet(
            ["source_matrix_invalid", *matrix_errors]
        )

    if matrix_status == "BLOCKED":
        matrix_errors = [
            f"source_matrix:{error}"
            for error in matrix["errors"]
        ]

        return _blocked_packet(
            ["source_matrix_blocked", *matrix_errors]
        )

    groups = matrix["sample_groups"]
    sample_group_errors: list[str] = []

    for index, group in enumerate(groups):
        if not isinstance(group, Mapping):
            sample_group_errors.append(
                f"sample_group_not_mapping:{index}"
            )
            continue

        sample_group_errors.extend(
            _validate_sample_group(
                group,
                index=index,
            )
        )

    if sample_group_errors:
        return _invalid_packet(sample_group_errors)

    if not groups:
        return _blocked_packet(
            ["no_sample_groups_for_review"]
        )

    review_items: list[dict[str, Any]] = []

    ordered_groups = sorted(
        groups,
        key=lambda item: item["evaluation_sample_id"],
    )

    for group in ordered_groups:
        priority, reasons = _priority_and_reasons(
            group
        )

        review_items.append(
            {
                "evaluation_sample_id": group[
                    "evaluation_sample_id"
                ],
                "priority": priority,
                "record_count": group["record_count"],
                "comparison_ids": list(
                    group["comparison_ids"]
                ),
                "comparison_status_counts": dict(
                    group["comparison_status_counts"]
                ),
                "result_status_counts": dict(
                    group["result_status_counts"]
                ),
                "cross_model_available": group[
                    "cross_model_available"
                ],
                "cross_model_version_available": group[
                    "cross_model_version_available"
                ],
                "cross_prompt_available": group[
                    "cross_prompt_available"
                ],
                "cross_prompt_version_available": group[
                    "cross_prompt_version_available"
                ],
                "review_reasons": reasons,
                "required_action": (
                    "operator_review_comparison_evidence"
                ),
                "automatic_acceptance_allowed": False,
                "automatic_winner_selection_allowed": False,
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
        "source_matrix_version": matrix[
            "matrix_version"
        ],
        "sample_count": len(ordered_groups),
        "review_item_count": len(review_items),
        "priority_counts": priority_counts,
        "review_items": review_items,
        "required_action": (
            "human_operator_review_comparison_evidence"
        ),
        "prohibited_actions": list(
            PROHIBITED_REVIEW_ACTIONS
        ),
        "errors": [],
        **_safety_fields(),
    }