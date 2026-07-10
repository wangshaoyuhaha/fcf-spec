"""Final operator-review handoff for AI evaluation comparisons."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from .contract import APP_ID
from .review import (
    PROHIBITED_REVIEW_ACTIONS,
    REVIEW_PACKET_VERSION,
    REVIEW_PRIORITIES,
)


HANDOFF_VERSION = "1.0.0"

HANDOFF_STATUSES = (
    "REVIEW_REQUIRED",
    "BLOCKED",
    "INVALID",
)

REQUIRED_REVIEW_PACKET_FIELDS = (
    "app_id",
    "review_packet_version",
    "packet_status",
    "result_status",
    "operator_review_status",
    "sample_count",
    "review_item_count",
    "priority_counts",
    "review_items",
    "required_action",
    "prohibited_actions",
    "errors",
)

REQUIRED_REVIEW_ITEM_FIELDS = (
    "evaluation_sample_id",
    "priority",
    "record_count",
    "comparison_ids",
    "review_reasons",
    "required_action",
    "automatic_acceptance_allowed",
    "automatic_winner_selection_allowed",
    "trade_action_allowed",
)

_PRIORITY_ORDER = {
    "HIGH": 0,
    "MEDIUM": 1,
    "LOW": 2,
}


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
        "orchestrator_execution_allowed": False,
        "drift_review_auto_start_allowed": False,
        "trade_action_allowed": False,
        "real_execution_allowed": False,
        "core_mutation_allowed": False,
    }


def _base_handoff(
    *,
    handoff_status: str,
    result_status: str,
    errors: list[str],
) -> dict[str, Any]:
    return {
        "app_id": APP_ID,
        "handoff_version": HANDOFF_VERSION,
        "handoff_status": handoff_status,
        "result_status": result_status,
        "operator_review_status": "REVIEW_REQUIRED",
        "source_review_packet_version": REVIEW_PACKET_VERSION,
        "sample_count": 0,
        "review_item_count": 0,
        "priority_counts": {},
        "review_queue": [],
        "required_action": "human_operator_review_only",
        "next_controlled_step": (
            "operator_review_comparison_evidence"
        ),
        "deferred_next_candidate": (
            "AI-EVALUATION-DRIFT-REVIEW-APP-1"
        ),
        "prohibited_actions": list(
            PROHIBITED_REVIEW_ACTIONS
        ),
        "errors": sorted(set(errors)),
        **_safety_fields(),
    }


def _invalid_handoff(errors: list[str]) -> dict[str, Any]:
    return _base_handoff(
        handoff_status="INVALID",
        result_status="INVALID",
        errors=errors,
    )


def _blocked_handoff(errors: list[str]) -> dict[str, Any]:
    return _base_handoff(
        handoff_status="BLOCKED",
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


def _validate_review_item(
    item: Mapping[str, Any],
    *,
    index: int,
) -> list[str]:
    errors: list[str] = []

    for field in REQUIRED_REVIEW_ITEM_FIELDS:
        if field not in item:
            errors.append(
                f"review_item[{index}]:missing_field:{field}"
            )

    if not _is_non_empty_string(
        item.get("evaluation_sample_id")
    ):
        errors.append(
            f"review_item[{index}]:sample_id_invalid"
        )

    if item.get("priority") not in REVIEW_PRIORITIES:
        errors.append(
            f"review_item[{index}]:priority_invalid"
        )

    record_count = item.get("record_count")

    if (
        not _is_non_negative_int(record_count)
        or record_count < 1
    ):
        errors.append(
            f"review_item[{index}]:record_count_invalid"
        )

    if not _is_string_list(
        item.get("comparison_ids"),
        allow_empty=False,
    ):
        errors.append(
            f"review_item[{index}]:comparison_ids_invalid"
        )

    if not _is_string_list(
        item.get("review_reasons"),
        allow_empty=False,
    ):
        errors.append(
            f"review_item[{index}]:review_reasons_invalid"
        )

    if item.get("required_action") != (
        "operator_review_comparison_evidence"
    ):
        errors.append(
            f"review_item[{index}]:required_action_invalid"
        )

    for field in (
        "automatic_acceptance_allowed",
        "automatic_winner_selection_allowed",
        "trade_action_allowed",
    ):
        if item.get(field) is not False:
            errors.append(
                f"review_item[{index}]:{field}_must_be_false"
            )

    return errors


def _validate_review_packet(
    packet: Mapping[str, Any],
) -> list[str]:
    errors: list[str] = []

    for field in REQUIRED_REVIEW_PACKET_FIELDS:
        if field not in packet:
            errors.append(f"missing_packet_field:{field}")

    if packet.get("app_id") != APP_ID:
        errors.append("packet_app_id_mismatch")

    if packet.get("review_packet_version") != (
        REVIEW_PACKET_VERSION
    ):
        errors.append("review_packet_version_mismatch")

    if packet.get("packet_status") not in {
        "REVIEW_REQUIRED",
        "BLOCKED",
        "INVALID",
    }:
        errors.append("packet_status_invalid")

    if packet.get("operator_review_status") != (
        "REVIEW_REQUIRED"
    ):
        errors.append("operator_review_status_invalid")

    sample_count = packet.get("sample_count")
    review_item_count = packet.get("review_item_count")

    if not _is_non_negative_int(sample_count):
        errors.append("sample_count_invalid")

    if not _is_non_negative_int(review_item_count):
        errors.append("review_item_count_invalid")

    priority_counts = packet.get("priority_counts")

    if not isinstance(priority_counts, Mapping):
        errors.append("priority_counts_invalid")
    else:
        for priority, count in priority_counts.items():
            if (
                priority not in REVIEW_PRIORITIES
                or not _is_non_negative_int(count)
            ):
                errors.append("priority_counts_invalid")

    review_items = packet.get("review_items")

    if not isinstance(review_items, list):
        errors.append("review_items_invalid")
    else:
        for index, item in enumerate(review_items):
            if not isinstance(item, Mapping):
                errors.append(
                    f"review_item_not_mapping:{index}"
                )
                continue

            errors.extend(
                _validate_review_item(
                    item,
                    index=index,
                )
            )

    if packet.get("required_action") != (
        "human_operator_review_comparison_evidence"
    ):
        errors.append("packet_required_action_invalid")

    prohibited_actions = packet.get(
        "prohibited_actions"
    )

    if not _is_string_list(
        prohibited_actions,
        allow_empty=False,
    ):
        errors.append("prohibited_actions_invalid")
    else:
        for action in PROHIBITED_REVIEW_ACTIONS:
            if action not in prohibited_actions:
                errors.append(
                    f"missing_prohibited_action:{action}"
                )

    if not _is_string_list(
        packet.get("errors"),
        allow_empty=True,
    ):
        errors.append("packet_errors_invalid")

    if isinstance(review_items, list):
        if (
            _is_non_negative_int(review_item_count)
            and review_item_count != len(review_items)
        ):
            errors.append("review_item_count_mismatch")

        if (
            packet.get("packet_status")
            == "REVIEW_REQUIRED"
            and _is_non_negative_int(sample_count)
            and sample_count != len(review_items)
        ):
            errors.append("sample_count_mismatch")

    return sorted(set(errors))


def build_comparison_operator_handoff(
    review_packet: Mapping[str, Any],
) -> dict[str, Any]:
    """Build the final deterministic operator-review handoff."""

    if not isinstance(review_packet, Mapping):
        return _invalid_handoff(
            ["source_review_packet_not_mapping"]
        )

    validation_errors = _validate_review_packet(
        review_packet
    )

    if validation_errors:
        return _invalid_handoff(validation_errors)

    packet_status = review_packet["packet_status"]

    if packet_status == "INVALID":
        source_errors = [
            f"source_review_packet:{error}"
            for error in review_packet["errors"]
        ]

        return _invalid_handoff(
            [
                "source_review_packet_invalid",
                *source_errors,
            ]
        )

    if packet_status == "BLOCKED":
        source_errors = [
            f"source_review_packet:{error}"
            for error in review_packet["errors"]
        ]

        return _blocked_handoff(
            [
                "source_review_packet_blocked",
                *source_errors,
            ]
        )

    review_items = review_packet["review_items"]

    if not review_items:
        return _blocked_handoff(
            ["no_review_items_for_operator_handoff"]
        )

    ordered_items = sorted(
        review_items,
        key=lambda item: (
            _PRIORITY_ORDER[item["priority"]],
            item["evaluation_sample_id"],
        ),
    )

    review_queue = [
        {
            "queue_position": index,
            "evaluation_sample_id": item[
                "evaluation_sample_id"
            ],
            "priority": item["priority"],
            "record_count": item["record_count"],
            "comparison_ids": list(
                item["comparison_ids"]
            ),
            "review_reasons": list(
                item["review_reasons"]
            ),
            "required_action": (
                "operator_review_comparison_evidence"
            ),
            "operator_review_status": (
                "REVIEW_REQUIRED"
            ),
            "automatic_acceptance_allowed": False,
            "automatic_winner_selection_allowed": False,
            "trade_action_allowed": False,
        }
        for index, item in enumerate(
            ordered_items,
            start=1,
        )
    ]

    return {
        "app_id": APP_ID,
        "handoff_version": HANDOFF_VERSION,
        "handoff_status": "REVIEW_REQUIRED",
        "result_status": "RECORDED",
        "operator_review_status": "REVIEW_REQUIRED",
        "source_review_packet_version": (
            review_packet["review_packet_version"]
        ),
        "sample_count": review_packet["sample_count"],
        "review_item_count": len(review_queue),
        "priority_counts": dict(
            review_packet["priority_counts"]
        ),
        "review_queue": review_queue,
        "required_action": "human_operator_review_only",
        "next_controlled_step": (
            "operator_review_comparison_evidence"
        ),
        "deferred_next_candidate": (
            "AI-EVALUATION-DRIFT-REVIEW-APP-1"
        ),
        "prohibited_actions": list(
            PROHIBITED_REVIEW_ACTIONS
        ),
        "errors": [],
        **_safety_fields(),
    }