"""Final operator-review handoff for AI contrarian challenge findings."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from .contract import APP_ID
from .report import REPORT_STATUSES
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

REQUIRED_PACKET_FIELDS = (
    "app_id",
    "review_packet_version",
    "packet_status",
    "result_status",
    "operator_review_status",
    "source_report_version",
    "source_report_status",
    "source_record_count",
    "review_item_count",
    "priority_counts",
    "review_items",
    "required_action",
    "prohibited_actions",
    "errors",
)

REQUIRED_ITEM_FIELDS = (
    "challenge_evidence_id",
    "source_artifact_id",
    "source_artifact_type",
    "source_artifact_reference",
    "claim_reference",
    "source_conclusion",
    "priority",
    "challenge_category",
    "challenge_severity",
    "reason_code",
    "challenge_statement",
    "evidence_references",
    "risk_flags",
    "review_reasons",
    "required_action",
    "operator_review_status",
    "original_conclusion_preserved",
    "automatic_truth_decision_allowed",
    "automatic_winner_selection_allowed",
    "automatic_conclusion_replacement_allowed",
    "operator_review_bypass_allowed",
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
        "deterministic_only": True,
        "registered_artifacts_only": True,
        "operator_review_required": True,
        "original_conclusion_preserved": True,
        "core_mutation_allowed": False,
        "source_artifact_mutation_allowed": False,
        "model_invocation_allowed": False,
        "prompt_execution_allowed": False,
        "orchestrator_execution_allowed": False,
        "automatic_truth_decision_allowed": False,
        "automatic_winner_selection_allowed": False,
        "automatic_conclusion_replacement_allowed": False,
        "automatic_model_ranking_allowed": False,
        "automatic_model_selection_allowed": False,
        "automatic_prompt_selection_allowed": False,
        "automatic_model_switch_allowed": False,
        "automatic_prompt_switch_allowed": False,
        "operator_review_bypass_allowed": False,
        "automatic_next_phase_allowed": False,
        "trade_action_allowed": False,
        "real_execution_allowed": False,
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
        "source_report_status": None,
        "source_record_count": 0,
        "review_item_count": 0,
        "priority_counts": {},
        "review_queue": [],
        "required_action": "human_operator_review_only",
        "next_controlled_step": (
            "operator_review_contrarian_challenge_findings"
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


def _validate_priority_counts(value: Any) -> bool:
    if not isinstance(value, Mapping):
        return False

    return all(
        priority in REVIEW_PRIORITIES
        and _is_non_negative_int(count)
        for priority, count in value.items()
    )


def _validate_review_item(
    item: Mapping[str, Any],
    *,
    index: int,
) -> list[str]:
    errors: list[str] = []

    for field in REQUIRED_ITEM_FIELDS:
        if field not in item:
            errors.append(
                f"review_item[{index}]:missing_field:{field}"
            )

    for field in (
        "challenge_evidence_id",
        "source_artifact_id",
        "source_artifact_type",
        "source_artifact_reference",
        "claim_reference",
        "source_conclusion",
        "reason_code",
        "challenge_statement",
    ):
        if not _is_non_empty_string(item.get(field)):
            errors.append(
                f"review_item[{index}]:{field}_invalid"
            )

    if item.get("priority") not in REVIEW_PRIORITIES:
        errors.append(
            f"review_item[{index}]:priority_invalid"
        )

    for field in (
        "challenge_category",
        "challenge_severity",
    ):
        if not _is_non_empty_string(item.get(field)):
            errors.append(
                f"review_item[{index}]:{field}_invalid"
            )

    for field in (
        "evidence_references",
        "risk_flags",
    ):
        if not _is_string_list(
            item.get(field),
            allow_empty=True,
        ):
            errors.append(
                f"review_item[{index}]:{field}_invalid"
            )

    if not _is_string_list(
        item.get("review_reasons"),
        allow_empty=False,
    ):
        errors.append(
            f"review_item[{index}]:review_reasons_invalid"
        )

    if item.get("required_action") != (
        "operator_review_contrarian_finding"
    ):
        errors.append(
            f"review_item[{index}]:required_action_invalid"
        )

    if item.get("operator_review_status") != (
        "REVIEW_REQUIRED"
    ):
        errors.append(
            f"review_item[{index}]:"
            "operator_review_status_invalid"
        )

    if item.get(
        "original_conclusion_preserved"
    ) is not True:
        errors.append(
            f"review_item[{index}]:"
            "original_conclusion_preserved_must_be_true"
        )

    for field in (
        "automatic_truth_decision_allowed",
        "automatic_winner_selection_allowed",
        "automatic_conclusion_replacement_allowed",
        "operator_review_bypass_allowed",
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

    for field in REQUIRED_PACKET_FIELDS:
        if field not in packet:
            errors.append(f"missing_packet_field:{field}")

    if packet.get("app_id") != APP_ID:
        errors.append("packet_app_id_mismatch")

    if packet.get("review_packet_version") != (
        REVIEW_PACKET_VERSION
    ):
        errors.append("review_packet_version_mismatch")

    packet_status = packet.get("packet_status")

    if packet_status not in HANDOFF_STATUSES:
        errors.append("packet_status_invalid")

    if packet.get("operator_review_status") != (
        "REVIEW_REQUIRED"
    ):
        errors.append("operator_review_status_invalid")

    if (
        packet_status == "REVIEW_REQUIRED"
        and packet.get("source_report_status")
        not in REPORT_STATUSES
    ):
        errors.append("source_report_status_invalid")

    for field in (
        "source_record_count",
        "review_item_count",
    ):
        if not _is_non_negative_int(packet.get(field)):
            errors.append(f"{field}_invalid")

    priority_counts = packet.get("priority_counts")

    if not _validate_priority_counts(priority_counts):
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
        "human_operator_review_contrarian_findings"
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

    review_item_count = packet.get(
        "review_item_count"
    )

    if (
        isinstance(review_items, list)
        and _is_non_negative_int(review_item_count)
        and review_item_count != len(review_items)
    ):
        errors.append("review_item_count_mismatch")

    if (
        _validate_priority_counts(priority_counts)
        and _is_non_negative_int(review_item_count)
        and sum(priority_counts.values())
        != review_item_count
    ):
        errors.append("priority_count_total_mismatch")

    return sorted(set(errors))


def build_challenge_operator_handoff(
    review_packet: Mapping[str, Any],
) -> dict[str, Any]:
    """Build the deterministic final operator-review handoff."""

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

    ordered_items = sorted(
        review_packet["review_items"],
        key=lambda item: (
            _PRIORITY_ORDER[item["priority"]],
            item["source_artifact_id"],
            item["claim_reference"],
            item["challenge_evidence_id"],
        ),
    )

    review_queue = [
        {
            "queue_position": position,
            "challenge_evidence_id": item[
                "challenge_evidence_id"
            ],
            "source_artifact_id": item[
                "source_artifact_id"
            ],
            "source_artifact_type": item[
                "source_artifact_type"
            ],
            "source_artifact_reference": item[
                "source_artifact_reference"
            ],
            "claim_reference": item[
                "claim_reference"
            ],
            "source_conclusion": item[
                "source_conclusion"
            ],
            "priority": item["priority"],
            "challenge_category": item[
                "challenge_category"
            ],
            "challenge_severity": item[
                "challenge_severity"
            ],
            "reason_code": item["reason_code"],
            "challenge_statement": item[
                "challenge_statement"
            ],
            "evidence_references": list(
                item["evidence_references"]
            ),
            "risk_flags": list(item["risk_flags"]),
            "review_reasons": list(
                item["review_reasons"]
            ),
            "required_action": (
                "operator_review_contrarian_finding"
            ),
            "operator_review_status": (
                "REVIEW_REQUIRED"
            ),
            "original_conclusion_preserved": True,
            "automatic_truth_decision_allowed": False,
            "automatic_winner_selection_allowed": False,
            "automatic_conclusion_replacement_allowed": False,
            "operator_review_bypass_allowed": False,
            "trade_action_allowed": False,
        }
        for position, item in enumerate(
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
        "source_report_status": review_packet[
            "source_report_status"
        ],
        "source_record_count": review_packet[
            "source_record_count"
        ],
        "review_item_count": len(review_queue),
        "priority_counts": dict(
            review_packet["priority_counts"]
        ),
        "review_queue": review_queue,
        "required_action": "human_operator_review_only",
        "next_controlled_step": (
            "operator_review_contrarian_challenge_findings"
        ),
        "prohibited_actions": list(
            PROHIBITED_REVIEW_ACTIONS
        ),
        "errors": [],
        **_safety_fields(),
    }