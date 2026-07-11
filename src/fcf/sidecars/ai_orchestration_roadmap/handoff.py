"""Planning-only roadmap review packet and operator handoff."""

import re
from typing import Any, Mapping

from .contract import (
    REQUIRED_FALSE_FLAGS,
    REQUIRED_TRUE_FLAGS,
    ROADMAP_MODE,
)
from .role_plan import (
    HUMAN_OPERATOR_ROLE_ID,
    ROLE_PLAN_STATUSES,
    validate_role_responsibility_plan,
)


STAGE_ID = "AI-ORCHESTRATION-ROADMAP-D6"
HANDOFF_VERSION = "1.0.0"

COMPLETED_STAGES = (
    "AI-ORCHESTRATION-ROADMAP-D1",
    "AI-ORCHESTRATION-ROADMAP-D2",
    "AI-ORCHESTRATION-ROADMAP-D3",
    "AI-ORCHESTRATION-ROADMAP-D4",
    "AI-ORCHESTRATION-ROADMAP-D5",
    "AI-ORCHESTRATION-ROADMAP-D6",
)

REVIEW_PACKET_STATUSES = (
    "READY_FOR_OPERATOR_REVIEW",
    "REVIEW_REQUIRED",
    "BLOCKED",
    "INVALID",
)

REVIEW_PRIORITIES = (
    "STANDARD",
    "HIGH",
    "CRITICAL",
)

HANDOFF_STATUSES = (
    "READY_FOR_OPERATOR_DECISION",
    "REVIEW_REQUIRED",
    "BLOCKED",
    "INVALID",
)

SUMMARY_FIELDS = (
    "role_count",
    "planned_ai_role_count",
    "human_operator_role_count",
    "planned_output_count",
)

REQUIRED_REVIEW_PACKET_FIELDS = (
    "packet_id",
    "source_role_plan_id",
    "source_role_plan_status",
    "completed_stages",
    "role_ids",
    "planned_output_artifact_types",
    "human_operator_terminal_role_id",
    "review_summary",
    "review_reason_codes",
    "packet_status",
    "review_priority",
    "blocking_gate_required",
    "operator_decision_required",
    "runtime_implementation_authorized",
    "runtime_orchestrator_status",
    "model_invocation_status",
    "prompt_execution_status",
    "automatic_routing_status",
    "automatic_role_switching_status",
    "required_action",
    "operator_review_status",
    "roadmap_mode",
    "runtime_execution_status",
    "source_artifacts_preserved",
    "original_conclusions_preserved",
    "safety_flags",
)

REQUIRED_HANDOFF_FIELDS = (
    "handoff_id",
    "packet_id",
    "source_role_plan_id",
    "source_role_plan_status",
    "completed_stages",
    "role_ids",
    "planned_output_artifact_types",
    "human_operator_terminal_role_id",
    "review_summary",
    "review_reason_codes",
    "packet_status",
    "review_priority",
    "handoff_status",
    "required_action",
    "next_phase_status",
    "future_runtime_implementation_status",
    "separate_architecture_review_required",
    "separate_operator_approval_required",
    "runtime_orchestrator_status",
    "model_invocation_status",
    "prompt_execution_status",
    "automatic_routing_status",
    "automatic_role_switching_status",
    "operator_review_status",
    "roadmap_mode",
    "runtime_execution_status",
    "source_artifacts_preserved",
    "original_conclusions_preserved",
    "safety_flags",
)

_IDENTIFIER_PATTERN = re.compile(
    r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$"
)


class RoadmapHandoffViolation(ValueError):
    """Raised when a D6 roadmap packet or handoff is invalid."""


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


def _packet_status(source_role_plan_status: str) -> str:
    if source_role_plan_status == "READY_FOR_REVIEW_PACKET":
        return "READY_FOR_OPERATOR_REVIEW"

    if source_role_plan_status == "BLOCKED":
        return "BLOCKED"

    if source_role_plan_status == "INVALID":
        return "INVALID"

    return "REVIEW_REQUIRED"


def _review_priority(source_role_plan_status: str) -> str:
    if source_role_plan_status in ("BLOCKED", "INVALID"):
        return "CRITICAL"

    if source_role_plan_status == "REVIEW_REQUIRED":
        return "HIGH"

    return "STANDARD"


def _review_reason_codes(
    source_role_plan_status: str,
) -> list[str]:
    mapping = {
        "READY_FOR_REVIEW_PACKET": [
            "ROADMAP_PLAN_READY_FOR_OPERATOR_REVIEW"
        ],
        "REVIEW_REQUIRED": [
            "ROADMAP_PLAN_REQUIRES_ADDITIONAL_REVIEW"
        ],
        "BLOCKED": [
            "ROADMAP_PLAN_BLOCKED"
        ],
        "INVALID": [
            "ROADMAP_PLAN_INVALID"
        ],
    }

    return list(mapping[source_role_plan_status])


def _review_summary(
    role_plan: Mapping[str, Any],
) -> dict[str, int]:
    roles = role_plan["roles"]

    planned_ai_role_count = sum(
        1
        for role in roles
        if role["role_kind"] == "PLANNED_AI_ROLE"
    )

    human_operator_role_count = sum(
        1
        for role in roles
        if role["role_kind"] == "HUMAN_OPERATOR"
    )

    return {
        "role_count": len(roles),
        "planned_ai_role_count": planned_ai_role_count,
        "human_operator_role_count": (
            human_operator_role_count
        ),
        "planned_output_count": len(
            role_plan["output_ownership"]
        ),
    }


def _handoff_status(packet_status: str) -> str:
    if packet_status == "READY_FOR_OPERATOR_REVIEW":
        return "READY_FOR_OPERATOR_DECISION"

    return packet_status


def build_roadmap_review_packet(
    *,
    packet_id: str,
    role_plan: Mapping[str, Any],
) -> dict[str, Any]:
    """Build a deterministic non-executable roadmap review packet."""
    role_errors = validate_role_responsibility_plan(
        role_plan
    )

    if role_errors:
        raise RoadmapHandoffViolation(
            ";".join(role_errors)
        )

    source_status = str(role_plan["role_plan_status"])

    role_ids = sorted(
        {
            str(role["role_id"])
            for role in role_plan["roles"]
        }
    )

    planned_output_artifact_types = sorted(
        {
            str(item["output_artifact_type"])
            for item in role_plan["output_ownership"]
        }
    )

    return {
        "packet_id": packet_id,
        "source_role_plan_id": role_plan["role_plan_id"],
        "source_role_plan_status": source_status,
        "completed_stages": list(COMPLETED_STAGES),
        "role_ids": role_ids,
        "planned_output_artifact_types": (
            planned_output_artifact_types
        ),
        "human_operator_terminal_role_id": (
            role_plan["human_operator_terminal_role_id"]
        ),
        "review_summary": _review_summary(role_plan),
        "review_reason_codes": _review_reason_codes(
            source_status
        ),
        "packet_status": _packet_status(source_status),
        "review_priority": _review_priority(source_status),
        "blocking_gate_required": True,
        "operator_decision_required": True,
        "runtime_implementation_authorized": False,
        "runtime_orchestrator_status": "NOT_CREATED",
        "model_invocation_status": "NOT_ALLOWED",
        "prompt_execution_status": "NOT_ALLOWED",
        "automatic_routing_status": "NOT_ALLOWED",
        "automatic_role_switching_status": "NOT_ALLOWED",
        "required_action": (
            "human_operator_review_planning_only_roadmap"
        ),
        "operator_review_status": "REVIEW_REQUIRED",
        "roadmap_mode": ROADMAP_MODE,
        "runtime_execution_status": "NOT_ALLOWED",
        "source_artifacts_preserved": True,
        "original_conclusions_preserved": True,
        "safety_flags": _safety_flags(),
    }


def _validate_summary(
    summary: Any,
    role_ids: Any,
    planned_outputs: Any,
) -> list[str]:
    if not isinstance(summary, Mapping):
        return ["review_summary_must_be_mapping"]

    errors: list[str] = []

    if set(summary.keys()) != set(SUMMARY_FIELDS):
        errors.append(
            "review_summary_fields_must_match_schema"
        )

    for field in SUMMARY_FIELDS:
        value = summary.get(field)

        if (
            not isinstance(value, int)
            or isinstance(value, bool)
            or value < 0
        ):
            errors.append(f"review_summary_{field}_invalid")

    if isinstance(role_ids, list):
        if summary.get("role_count") != len(role_ids):
            errors.append("review_summary_role_count_mismatch")

    if isinstance(planned_outputs, list):
        if summary.get("planned_output_count") != len(
            planned_outputs
        ):
            errors.append(
                "review_summary_planned_output_count_mismatch"
            )

    role_count = summary.get("role_count")
    planned_ai_count = summary.get(
        "planned_ai_role_count"
    )
    human_count = summary.get(
        "human_operator_role_count"
    )

    if (
        isinstance(role_count, int)
        and isinstance(planned_ai_count, int)
        and isinstance(human_count, int)
        and role_count
        != planned_ai_count + human_count
    ):
        errors.append("review_summary_role_type_count_mismatch")

    if human_count != 1:
        errors.append(
            "review_summary_human_operator_count_must_be_one"
        )

    return errors


def validate_roadmap_review_packet(
    packet: object,
) -> list[str]:
    """Return deterministic D6 review-packet validation errors."""
    if not isinstance(packet, Mapping):
        return ["review_packet_must_be_mapping"]

    errors: list[str] = []

    if set(packet.keys()) != set(
        REQUIRED_REVIEW_PACKET_FIELDS
    ):
        errors.append(
            "review_packet_fields_must_match_schema"
        )

    for field in (
        "packet_id",
        "source_role_plan_id",
        "human_operator_terminal_role_id",
    ):
        if not _valid_identifier(packet.get(field)):
            errors.append(f"{field}_invalid")

    source_status = packet.get("source_role_plan_status")

    if source_status not in ROLE_PLAN_STATUSES:
        errors.append("source_role_plan_status_invalid")
        source_status_for_validation = "REVIEW_REQUIRED"
    else:
        source_status_for_validation = str(source_status)

    for field in (
        "completed_stages",
        "role_ids",
        "planned_output_artifact_types",
        "review_reason_codes",
    ):
        if not _valid_canonical_string_list(
            packet.get(field)
        ):
            errors.append(f"{field}_invalid")

    if packet.get("completed_stages") != list(
        COMPLETED_STAGES
    ):
        errors.append("completed_stages_invalid")

    if packet.get(
        "human_operator_terminal_role_id"
    ) != HUMAN_OPERATOR_ROLE_ID:
        errors.append(
            "human_operator_terminal_role_id_invalid"
        )

    errors.extend(
        _validate_summary(
            packet.get("review_summary"),
            packet.get("role_ids"),
            packet.get("planned_output_artifact_types"),
        )
    )

    expected_reasons = _review_reason_codes(
        source_status_for_validation
    )

    if packet.get("review_reason_codes") != expected_reasons:
        errors.append("review_reason_codes_mismatch")

    expected_packet_status = _packet_status(
        source_status_for_validation
    )

    if packet.get("packet_status") not in (
        REVIEW_PACKET_STATUSES
    ):
        errors.append("packet_status_invalid")
    elif packet.get("packet_status") != expected_packet_status:
        errors.append("packet_status_mismatch")

    expected_priority = _review_priority(
        source_status_for_validation
    )

    if packet.get("review_priority") not in (
        REVIEW_PRIORITIES
    ):
        errors.append("review_priority_invalid")
    elif packet.get("review_priority") != expected_priority:
        errors.append("review_priority_mismatch")

    for field in (
        "blocking_gate_required",
        "operator_decision_required",
        "source_artifacts_preserved",
        "original_conclusions_preserved",
    ):
        if packet.get(field) is not True:
            errors.append(f"{field}_must_be_true")

    if packet.get(
        "runtime_implementation_authorized"
    ) is not False:
        errors.append(
            "runtime_implementation_authorized_must_be_false"
        )

    expected_not_allowed = (
        "model_invocation_status",
        "prompt_execution_status",
        "automatic_routing_status",
        "automatic_role_switching_status",
        "runtime_execution_status",
    )

    for field in expected_not_allowed:
        if packet.get(field) != "NOT_ALLOWED":
            errors.append(f"{field}_must_be_not_allowed")

    if packet.get("runtime_orchestrator_status") != (
        "NOT_CREATED"
    ):
        errors.append(
            "runtime_orchestrator_status_must_be_not_created"
        )

    if packet.get("required_action") != (
        "human_operator_review_planning_only_roadmap"
    ):
        errors.append("required_action_invalid")

    if packet.get("operator_review_status") != (
        "REVIEW_REQUIRED"
    ):
        errors.append("operator_review_status_invalid")

    if packet.get("roadmap_mode") != ROADMAP_MODE:
        errors.append("roadmap_mode_invalid")

    errors.extend(
        _validate_safety_flags(
            packet.get("safety_flags")
        )
    )

    return errors


def build_roadmap_operator_handoff(
    *,
    handoff_id: str,
    review_packet: Mapping[str, Any],
) -> dict[str, Any]:
    """Build the final non-executable operator handoff."""
    packet_errors = validate_roadmap_review_packet(
        review_packet
    )

    if packet_errors:
        raise RoadmapHandoffViolation(
            ";".join(packet_errors)
        )

    return {
        "handoff_id": handoff_id,
        "packet_id": review_packet["packet_id"],
        "source_role_plan_id": review_packet[
            "source_role_plan_id"
        ],
        "source_role_plan_status": review_packet[
            "source_role_plan_status"
        ],
        "completed_stages": list(
            review_packet["completed_stages"]
        ),
        "role_ids": list(review_packet["role_ids"]),
        "planned_output_artifact_types": list(
            review_packet[
                "planned_output_artifact_types"
            ]
        ),
        "human_operator_terminal_role_id": (
            review_packet[
                "human_operator_terminal_role_id"
            ]
        ),
        "review_summary": dict(
            review_packet["review_summary"]
        ),
        "review_reason_codes": list(
            review_packet["review_reason_codes"]
        ),
        "packet_status": review_packet["packet_status"],
        "review_priority": review_packet[
            "review_priority"
        ],
        "handoff_status": _handoff_status(
            review_packet["packet_status"]
        ),
        "required_action": (
            "human_operator_review_roadmap_before_any_"
            "future_implementation"
        ),
        "next_phase_status": "NOT_SELECTED",
        "future_runtime_implementation_status": (
            "NOT_AUTHORIZED"
        ),
        "separate_architecture_review_required": True,
        "separate_operator_approval_required": True,
        "runtime_orchestrator_status": "NOT_CREATED",
        "model_invocation_status": "NOT_ALLOWED",
        "prompt_execution_status": "NOT_ALLOWED",
        "automatic_routing_status": "NOT_ALLOWED",
        "automatic_role_switching_status": "NOT_ALLOWED",
        "operator_review_status": "REVIEW_REQUIRED",
        "roadmap_mode": ROADMAP_MODE,
        "runtime_execution_status": "NOT_ALLOWED",
        "source_artifacts_preserved": True,
        "original_conclusions_preserved": True,
        "safety_flags": _safety_flags(),
    }


def validate_roadmap_operator_handoff(
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
        "source_role_plan_id",
        "human_operator_terminal_role_id",
    ):
        if not _valid_identifier(handoff.get(field)):
            errors.append(f"{field}_invalid")

    source_status = handoff.get(
        "source_role_plan_status"
    )

    if source_status not in ROLE_PLAN_STATUSES:
        errors.append("source_role_plan_status_invalid")
        source_status_for_validation = "REVIEW_REQUIRED"
    else:
        source_status_for_validation = str(source_status)

    for field in (
        "completed_stages",
        "role_ids",
        "planned_output_artifact_types",
        "review_reason_codes",
    ):
        if not _valid_canonical_string_list(
            handoff.get(field)
        ):
            errors.append(f"{field}_invalid")

    if handoff.get("completed_stages") != list(
        COMPLETED_STAGES
    ):
        errors.append("completed_stages_invalid")

    if handoff.get(
        "human_operator_terminal_role_id"
    ) != HUMAN_OPERATOR_ROLE_ID:
        errors.append(
            "human_operator_terminal_role_id_invalid"
        )

    errors.extend(
        _validate_summary(
            handoff.get("review_summary"),
            handoff.get("role_ids"),
            handoff.get(
                "planned_output_artifact_types"
            ),
        )
    )

    expected_reasons = _review_reason_codes(
        source_status_for_validation
    )

    if handoff.get("review_reason_codes") != expected_reasons:
        errors.append("review_reason_codes_mismatch")

    expected_packet_status = _packet_status(
        source_status_for_validation
    )

    if handoff.get("packet_status") not in (
        REVIEW_PACKET_STATUSES
    ):
        errors.append("packet_status_invalid")
    elif handoff.get("packet_status") != expected_packet_status:
        errors.append("packet_status_mismatch")

    expected_priority = _review_priority(
        source_status_for_validation
    )

    if handoff.get("review_priority") not in (
        REVIEW_PRIORITIES
    ):
        errors.append("review_priority_invalid")
    elif handoff.get("review_priority") != expected_priority:
        errors.append("review_priority_mismatch")

    expected_handoff_status = _handoff_status(
        expected_packet_status
    )

    if handoff.get("handoff_status") not in (
        HANDOFF_STATUSES
    ):
        errors.append("handoff_status_invalid")
    elif handoff.get("handoff_status") != (
        expected_handoff_status
    ):
        errors.append("handoff_status_mismatch")

    if handoff.get("required_action") != (
        "human_operator_review_roadmap_before_any_"
        "future_implementation"
    ):
        errors.append("required_action_invalid")

    if handoff.get("next_phase_status") != "NOT_SELECTED":
        errors.append("next_phase_status_must_be_not_selected")

    if handoff.get(
        "future_runtime_implementation_status"
    ) != "NOT_AUTHORIZED":
        errors.append(
            "future_runtime_implementation_must_not_be_authorized"
        )

    for field in (
        "separate_architecture_review_required",
        "separate_operator_approval_required",
        "source_artifacts_preserved",
        "original_conclusions_preserved",
    ):
        if handoff.get(field) is not True:
            errors.append(f"{field}_must_be_true")

    if handoff.get("runtime_orchestrator_status") != (
        "NOT_CREATED"
    ):
        errors.append(
            "runtime_orchestrator_status_must_be_not_created"
        )

    for field in (
        "model_invocation_status",
        "prompt_execution_status",
        "automatic_routing_status",
        "automatic_role_switching_status",
        "runtime_execution_status",
    ):
        if handoff.get(field) != "NOT_ALLOWED":
            errors.append(f"{field}_must_be_not_allowed")

    if handoff.get("operator_review_status") != (
        "REVIEW_REQUIRED"
    ):
        errors.append("operator_review_status_invalid")

    if handoff.get("roadmap_mode") != ROADMAP_MODE:
        errors.append("roadmap_mode_invalid")

    errors.extend(
        _validate_safety_flags(
            handoff.get("safety_flags")
        )
    )

    return errors
