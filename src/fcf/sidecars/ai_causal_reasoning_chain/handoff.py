"""Final operator-review and archive handoff for causal reasoning."""

from copy import deepcopy
import re
from typing import Any, Mapping, Sequence

from .contract import (
    REQUIRED_FALSE_FLAGS,
    REQUIRED_TRUE_FLAGS,
)
from .review_packet import (
    REVIEW_PACKET_STATUSES,
    REVIEW_PRIORITIES,
    REQUIRED_SUMMARY_FIELDS,
    validate_causal_reasoning_review_packet,
)


STAGE_ID = "AI-CAUSAL-REASONING-CHAIN-D6"
HANDOFF_VERSION = "1.0.0"

HANDOFF_STATUSES = (
    "READY_FOR_OPERATOR_DECISION",
    "REVIEW_REQUIRED",
    "BLOCKED",
)

ARCHIVE_HANDOFF_STATUSES = (
    "READY_FOR_MANUAL_ARCHIVE",
    "REVIEW_HOLD",
    "BLOCKED",
)

OPERATOR_DECISION_STATUSES = (
    "PENDING",
)

REQUIRED_HANDOFF_FIELDS = (
    "handoff_id",
    "source_review_packet",
    "source_packet_id",
    "source_packet_status",
    "source_assessment_id",
    "source_chain_id",
    "correlation_id",
    "research_run_id",
    "review_priority",
    "review_summary",
    "reason_codes",
    "required_operator_actions",
    "handoff_status",
    "archive_handoff_status",
    "archive_artifact_type",
    "archive_execution_status",
    "operator_decision_status",
    "operator_decision_required",
    "manual_archive_required",
    "next_phase_status",
    "causal_truth_status",
    "probability_status",
    "winner_status",
    "operator_review_status",
    "source_artifacts_preserved",
    "original_conclusions_preserved",
    "runtime_execution_status",
    "live_model_invocation_status",
    "prompt_execution_status",
    "automatic_approval_status",
    "safety_flags",
)

_IDENTIFIER_PATTERN = re.compile(
    r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$"
)


class CausalHandoffViolation(ValueError):
    """Raised when a D5 packet cannot form a safe final handoff."""


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
        not isinstance(item, str)
        or not item.strip()
        for item in value
    ):
        return False

    return value == sorted(set(value))


def _validate_safety_flags(value: Any) -> list[str]:
    if not isinstance(value, Mapping):
        return ["safety_flags_must_be_mapping"]

    errors: list[str] = []

    expected_names = set(
        REQUIRED_TRUE_FLAGS + REQUIRED_FALSE_FLAGS
    )

    if set(value.keys()) != expected_names:
        errors.append(
            "safety_flag_names_must_match_contract"
        )

    for name in REQUIRED_TRUE_FLAGS:
        if value.get(name) is not True:
            errors.append(f"{name}_must_be_true")

    for name in REQUIRED_FALSE_FLAGS:
        if value.get(name) is not False:
            errors.append(f"{name}_must_be_false")

    return errors


def _handoff_status(
    packet_status: str,
) -> str:
    mapping = {
        "READY_FOR_OPERATOR_REVIEW": (
            "READY_FOR_OPERATOR_DECISION"
        ),
        "REVIEW_REQUIRED": "REVIEW_REQUIRED",
        "BLOCKED": "BLOCKED",
    }

    return mapping[packet_status]


def _archive_handoff_status(
    packet_status: str,
) -> str:
    mapping = {
        "READY_FOR_OPERATOR_REVIEW": (
            "READY_FOR_MANUAL_ARCHIVE"
        ),
        "REVIEW_REQUIRED": "REVIEW_HOLD",
        "BLOCKED": "BLOCKED",
    }

    return mapping[packet_status]


def _build_from_valid_packet(
    *,
    handoff_id: str,
    review_packet: Mapping[str, Any],
) -> dict[str, Any]:
    packet_status = str(
        review_packet["packet_status"]
    )

    return {
        "handoff_id": handoff_id,
        "source_review_packet": deepcopy(
            dict(review_packet)
        ),
        "source_packet_id": review_packet[
            "packet_id"
        ],
        "source_packet_status": packet_status,
        "source_assessment_id": review_packet[
            "source_assessment_id"
        ],
        "source_chain_id": review_packet[
            "source_chain_id"
        ],
        "correlation_id": review_packet[
            "correlation_id"
        ],
        "research_run_id": review_packet[
            "research_run_id"
        ],
        "review_priority": review_packet[
            "review_priority"
        ],
        "review_summary": deepcopy(
            dict(review_packet["review_summary"])
        ),
        "reason_codes": list(
            review_packet["reason_codes"]
        ),
        "required_operator_actions": list(
            review_packet[
                "required_operator_actions"
            ]
        ),
        "handoff_status": _handoff_status(
            packet_status
        ),
        "archive_handoff_status": (
            _archive_handoff_status(
                packet_status
            )
        ),
        "archive_artifact_type": (
            "CAUSAL_REASONING_OPERATOR_ARCHIVE_PACKET"
        ),
        "archive_execution_status": "NOT_PERFORMED",
        "operator_decision_status": "PENDING",
        "operator_decision_required": True,
        "manual_archive_required": True,
        "next_phase_status": "NOT_SELECTED",
        "causal_truth_status": "UNDETERMINED",
        "probability_status": "NOT_ASSIGNED",
        "winner_status": "NOT_SELECTED",
        "operator_review_status": "REQUIRED",
        "source_artifacts_preserved": True,
        "original_conclusions_preserved": True,
        "runtime_execution_status": "NOT_ALLOWED",
        "live_model_invocation_status": "NOT_ALLOWED",
        "prompt_execution_status": "NOT_ALLOWED",
        "automatic_approval_status": "NOT_ALLOWED",
        "safety_flags": _safety_flags(),
    }


def build_causal_reasoning_operator_handoff(
    *,
    handoff_id: str,
    review_packet: Mapping[str, Any],
) -> dict[str, Any]:
    """Build a final paper-only manual operator handoff."""
    packet_errors = (
        validate_causal_reasoning_review_packet(
            review_packet
        )
    )

    if packet_errors:
        raise CausalHandoffViolation(
            ";".join(packet_errors)
        )

    return _build_from_valid_packet(
        handoff_id=handoff_id,
        review_packet=review_packet,
    )


def _validate_review_summary(
    value: Any,
) -> list[str]:
    if not isinstance(value, Mapping):
        return ["review_summary_must_be_mapping"]

    errors: list[str] = []

    if set(value.keys()) != set(
        REQUIRED_SUMMARY_FIELDS
    ):
        errors.append(
            "review_summary_fields_must_match_schema"
        )

    for field in REQUIRED_SUMMARY_FIELDS:
        count = value.get(field)

        if (
            not isinstance(count, int)
            or isinstance(count, bool)
            or count < 0
        ):
            errors.append(
                f"review_summary_{field}_invalid"
            )

    return errors


def validate_causal_reasoning_operator_handoff(
    handoff: object,
) -> list[str]:
    """Return deterministic D6 handoff validation errors."""
    if not isinstance(handoff, Mapping):
        return ["handoff_must_be_mapping"]

    errors: list[str] = []

    if set(handoff.keys()) != set(
        REQUIRED_HANDOFF_FIELDS
    ):
        errors.append(
            "handoff_fields_must_match_schema"
        )

    for field in (
        "handoff_id",
        "source_packet_id",
        "source_assessment_id",
        "source_chain_id",
        "correlation_id",
        "research_run_id",
    ):
        if not _valid_identifier(
            handoff.get(field)
        ):
            errors.append(f"{field}_invalid")

    source_packet = handoff.get(
        "source_review_packet"
    )

    if not isinstance(source_packet, Mapping):
        errors.append(
            "source_review_packet_must_be_mapping"
        )
        source_errors = [
            "source_review_packet_must_be_mapping"
        ]
    else:
        source_errors = (
            validate_causal_reasoning_review_packet(
                source_packet
            )
        )

        for source_error in source_errors:
            errors.append(
                f"source_review_packet:{source_error}"
            )

    if handoff.get(
        "source_packet_status"
    ) not in REVIEW_PACKET_STATUSES:
        errors.append(
            "source_packet_status_invalid"
        )

    if handoff.get(
        "review_priority"
    ) not in REVIEW_PRIORITIES:
        errors.append("review_priority_invalid")

    errors.extend(
        _validate_review_summary(
            handoff.get("review_summary")
        )
    )

    for field in (
        "reason_codes",
        "required_operator_actions",
    ):
        if not _valid_canonical_string_list(
            handoff.get(field)
        ):
            errors.append(f"{field}_invalid")

    if handoff.get(
        "handoff_status"
    ) not in HANDOFF_STATUSES:
        errors.append("handoff_status_invalid")

    if handoff.get(
        "archive_handoff_status"
    ) not in ARCHIVE_HANDOFF_STATUSES:
        errors.append(
            "archive_handoff_status_invalid"
        )

    if handoff.get("archive_artifact_type") != (
        "CAUSAL_REASONING_OPERATOR_ARCHIVE_PACKET"
    ):
        errors.append("archive_artifact_type_invalid")

    if handoff.get(
        "archive_execution_status"
    ) != "NOT_PERFORMED":
        errors.append(
            "archive_execution_status_must_be_not_performed"
        )

    if handoff.get(
        "operator_decision_status"
    ) not in OPERATOR_DECISION_STATUSES:
        errors.append(
            "operator_decision_status_invalid"
        )

    for field in (
        "operator_decision_required",
        "manual_archive_required",
        "source_artifacts_preserved",
        "original_conclusions_preserved",
    ):
        if handoff.get(field) is not True:
            errors.append(f"{field}_must_be_true")

    if handoff.get(
        "next_phase_status"
    ) != "NOT_SELECTED":
        errors.append(
            "next_phase_status_must_be_not_selected"
        )

    if handoff.get(
        "causal_truth_status"
    ) != "UNDETERMINED":
        errors.append(
            "causal_truth_status_invalid"
        )

    if handoff.get(
        "probability_status"
    ) != "NOT_ASSIGNED":
        errors.append(
            "probability_status_invalid"
        )

    if handoff.get(
        "winner_status"
    ) != "NOT_SELECTED":
        errors.append("winner_status_invalid")

    if handoff.get(
        "operator_review_status"
    ) != "REQUIRED":
        errors.append(
            "operator_review_status_invalid"
        )

    for field in (
        "runtime_execution_status",
        "live_model_invocation_status",
        "prompt_execution_status",
        "automatic_approval_status",
    ):
        if handoff.get(field) != "NOT_ALLOWED":
            errors.append(
                f"{field}_must_be_not_allowed"
            )

    errors.extend(
        _validate_safety_flags(
            handoff.get("safety_flags")
        )
    )

    if (
        isinstance(source_packet, Mapping)
        and not source_errors
        and _valid_identifier(
            handoff.get("handoff_id")
        )
    ):
        expected = _build_from_valid_packet(
            handoff_id=str(
                handoff["handoff_id"]
            ),
            review_packet=source_packet,
        )

        comparison_fields = (
            "source_packet_id",
            "source_packet_status",
            "source_assessment_id",
            "source_chain_id",
            "correlation_id",
            "research_run_id",
            "review_priority",
            "review_summary",
            "reason_codes",
            "required_operator_actions",
            "handoff_status",
            "archive_handoff_status",
        )

        for field in comparison_fields:
            if handoff.get(field) != expected[field]:
                errors.append(f"{field}_mismatch")

    return sorted(set(errors))
