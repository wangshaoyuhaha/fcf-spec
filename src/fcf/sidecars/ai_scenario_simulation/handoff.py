"""Operator-review and archive handoff for scenario simulation."""

import re
from typing import Any, Mapping

from .contract import REQUIRED_FALSE_FLAGS, REQUIRED_TRUE_FLAGS
from .review_packet import (
    validate_scenario_simulation_review_packet,
)


STAGE_ID = "AI-SCENARIO-SIMULATION-D6"
HANDOFF_VERSION = "1.0.0"

HANDOFF_STATUSES = (
    "READY_FOR_OPERATOR_AND_ARCHIVE_REVIEW",
    "REVIEW_REQUIRED",
    "BLOCKED",
    "ARCHIVED",
)

COMPLETED_STAGES = (
    "AI-SCENARIO-SIMULATION-D1",
    "AI-SCENARIO-SIMULATION-D2",
    "AI-SCENARIO-SIMULATION-D3",
    "AI-SCENARIO-SIMULATION-D4",
    "AI-SCENARIO-SIMULATION-D5",
    "AI-SCENARIO-SIMULATION-D6",
)

REQUIRED_HANDOFF_FIELDS = (
    "handoff_id",
    "packet_id",
    "assessment_id",
    "completed_stages",
    "branch_ids",
    "source_scenario_ids",
    "consequence_record_ids",
    "packet_status",
    "handoff_status",
    "review_priority",
    "reason_codes",
    "assessment_summary",
    "original_conclusion_references",
    "required_action",
    "next_required_review",
    "archive_registration_required",
    "archive_execution_allowed",
    "operator_review_status",
    "truth_status",
    "probability_status",
    "rank_status",
    "winner_status",
    "source_artifacts_preserved",
    "original_conclusions_preserved",
    "safety_flags",
)

_IDENTIFIER_PATTERN = re.compile(
    r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$"
)


class ScenarioHandoffViolation(ValueError):
    """Raised when a D6 source review packet is invalid."""


def _safety_flags() -> dict[str, bool]:
    return {
        **{name: True for name in REQUIRED_TRUE_FLAGS},
        **{name: False for name in REQUIRED_FALSE_FLAGS},
    }


def _valid_identifier(value: Any) -> bool:
    return (
        isinstance(value, str)
        and _IDENTIFIER_PATTERN.fullmatch(value) is not None
    )


def _valid_canonical_string_list(value: Any) -> bool:
    if not isinstance(value, list):
        return False

    if any(
        not isinstance(item, str) or not item.strip()
        for item in value
    ):
        return False

    return value == sorted(set(value))


def _validate_safety_flags(value: Any) -> list[str]:
    if not isinstance(value, Mapping):
        return ["safety_flags_must_be_mapping"]

    errors: list[str] = []

    for name in REQUIRED_TRUE_FLAGS:
        if value.get(name) is not True:
            errors.append(f"{name}_must_be_true")

    for name in REQUIRED_FALSE_FLAGS:
        if value.get(name) is not False:
            errors.append(f"{name}_must_be_false")

    expected_names = set(
        REQUIRED_TRUE_FLAGS + REQUIRED_FALSE_FLAGS
    )

    if set(value.keys()) != expected_names:
        errors.append("safety_flag_names_must_match_contract")

    return errors


def _derive_handoff_status(packet_status: str) -> str:
    if packet_status == "BLOCKED":
        return "BLOCKED"

    if packet_status == "ARCHIVED":
        return "ARCHIVED"

    if packet_status == "READY_FOR_OPERATOR_REVIEW":
        return "READY_FOR_OPERATOR_AND_ARCHIVE_REVIEW"

    return "REVIEW_REQUIRED"


def build_scenario_simulation_handoff(
    *,
    handoff_id: str,
    review_packet: Mapping[str, Any],
) -> dict[str, Any]:
    """Build the deterministic final operator and archive handoff."""
    errors = validate_scenario_simulation_review_packet(
        review_packet
    )

    if errors:
        raise ScenarioHandoffViolation(";".join(errors))

    return {
        "handoff_id": handoff_id,
        "packet_id": review_packet["packet_id"],
        "assessment_id": review_packet["assessment_id"],
        "completed_stages": list(COMPLETED_STAGES),
        "branch_ids": list(review_packet["branch_ids"]),
        "source_scenario_ids": list(
            review_packet["source_scenario_ids"]
        ),
        "consequence_record_ids": list(
            review_packet["consequence_record_ids"]
        ),
        "packet_status": review_packet["packet_status"],
        "handoff_status": _derive_handoff_status(
            review_packet["packet_status"]
        ),
        "review_priority": review_packet["review_priority"],
        "reason_codes": list(review_packet["reason_codes"]),
        "assessment_summary": dict(
            review_packet["assessment_summary"]
        ),
        "original_conclusion_references": list(
            review_packet[
                "original_conclusion_references"
            ]
        ),
        "required_action": (
            "human_operator_review_scenario_simulation_packet"
        ),
        "next_required_review": (
            "operator_review_before_local_archive_registration"
        ),
        "archive_registration_required": True,
        "archive_execution_allowed": False,
        "operator_review_status": "REVIEW_REQUIRED",
        "truth_status": "UNDETERMINED",
        "probability_status": "NOT_ASSIGNED",
        "rank_status": "NOT_ASSIGNED",
        "winner_status": "NOT_SELECTED",
        "source_artifacts_preserved": True,
        "original_conclusions_preserved": True,
        "safety_flags": _safety_flags(),
    }


def validate_scenario_simulation_handoff(
    handoff: object,
) -> list[str]:
    """Return deterministic final handoff validation errors."""
    if not isinstance(handoff, Mapping):
        return ["handoff_must_be_mapping"]

    errors: list[str] = []

    if set(handoff.keys()) != set(REQUIRED_HANDOFF_FIELDS):
        errors.append("handoff_fields_must_match_schema")

    for field in (
        "handoff_id",
        "packet_id",
        "assessment_id",
    ):
        if not _valid_identifier(handoff.get(field)):
            errors.append(f"{field}_invalid")

    for field in (
        "completed_stages",
        "branch_ids",
        "source_scenario_ids",
        "consequence_record_ids",
        "reason_codes",
        "original_conclusion_references",
    ):
        if not _valid_canonical_string_list(
            handoff.get(field)
        ):
            errors.append(f"{field}_invalid")

    if handoff.get("completed_stages") != list(
        COMPLETED_STAGES
    ):
        errors.append("completed_stages_invalid")

    if handoff.get("handoff_status") not in (
        HANDOFF_STATUSES
    ):
        errors.append("handoff_status_invalid")

    if handoff.get("packet_status") not in (
        "READY_FOR_OPERATOR_REVIEW",
        "REVIEW_REQUIRED",
        "BLOCKED",
        "ARCHIVED",
    ):
        errors.append("packet_status_invalid")

    if handoff.get("review_priority") not in (
        "STANDARD",
        "MEDIUM",
        "HIGH",
        "CRITICAL",
    ):
        errors.append("review_priority_invalid")

    summary = handoff.get("assessment_summary")

    if not isinstance(summary, Mapping):
        errors.append(
            "assessment_summary_must_be_mapping"
        )

    if handoff.get("required_action") != (
        "human_operator_review_scenario_simulation_packet"
    ):
        errors.append("required_action_invalid")

    if handoff.get("next_required_review") != (
        "operator_review_before_local_archive_registration"
    ):
        errors.append("next_required_review_invalid")

    if handoff.get("archive_registration_required") is not True:
        errors.append(
            "archive_registration_required_must_be_true"
        )

    if handoff.get("archive_execution_allowed") is not False:
        errors.append(
            "archive_execution_allowed_must_be_false"
        )

    if handoff.get("operator_review_status") != (
        "REVIEW_REQUIRED"
    ):
        errors.append("operator_review_status_invalid")

    if handoff.get("truth_status") != "UNDETERMINED":
        errors.append(
            "truth_status_must_remain_undetermined"
        )

    if handoff.get("probability_status") != "NOT_ASSIGNED":
        errors.append(
            "probability_must_not_be_assigned"
        )

    if handoff.get("rank_status") != "NOT_ASSIGNED":
        errors.append("rank_must_not_be_assigned")

    if handoff.get("winner_status") != "NOT_SELECTED":
        errors.append("winner_must_not_be_selected")

    if handoff.get("source_artifacts_preserved") is not True:
        errors.append(
            "source_artifacts_preserved_must_be_true"
        )

    if (
        handoff.get("original_conclusions_preserved")
        is not True
    ):
        errors.append(
            "original_conclusions_preserved_must_be_true"
        )

    errors.extend(
        _validate_safety_flags(
            handoff.get("safety_flags")
        )
    )

    return errors
