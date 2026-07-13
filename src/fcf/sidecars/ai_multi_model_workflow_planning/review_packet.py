"""Planning-only governance review packet for multi-model workflow."""

import re
from typing import Any, Mapping

from .assignment_profiles import (
    validate_assignment_profile_manifest,
)
from .contract import (
    APP_ID,
    MODEL_SLOT_TYPES,
    PLANNING_MODE,
    REQUIRED_FALSE_FLAGS,
    REQUIRED_TRUE_FLAGS,
    validate_multi_model_workflow_boundary_contract,
)
from .policy_eligibility import (
    validate_policy_eligibility_manifest,
)
from .slot_bindings import (
    validate_role_model_slot_binding_manifest,
)

STAGE_ID = "AI-MULTI-MODEL-WORKFLOW-PLANNING-D5"
REVIEW_PACKET_VERSION = "1.0.0"

OVERALL_STATUSES = (
    "READY_FOR_OPERATOR_REVIEW",
    "DEGRADED",
    "BLOCKED",
)

REQUIRED_REVIEW_PACKET_FIELDS = (
    "review_packet_id",
    "app_id",
    "stage_id",
    "review_packet_version",
    "planning_mode",
    "source_contract_id",
    "source_contract_version",
    "source_slot_manifest_id",
    "source_slot_binding_version",
    "source_policy_manifest_id",
    "source_policy_eligibility_version",
    "source_assignment_manifest_id",
    "source_assignment_profile_version",
    "role_ids",
    "model_slot_types",
    "assignment_count",
    "ready_count",
    "degraded_count",
    "blocked_count",
    "overall_status",
    "blocking_reasons",
    "warnings",
    "policy_authority",
    "operator_review_status",
    "operator_decision_status",
    "automatic_selection_status",
    "automatic_switching_status",
    "automatic_routing_status",
    "automatic_retry_status",
    "automatic_fallback_status",
    "model_invocation_status",
    "prompt_execution_status",
    "runtime_execution_status",
    "archive_writing_status",
    "real_execution_status",
    "safety_flags",
)

_IDENTIFIER_PATTERN = re.compile(
    r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$"
)


class WorkflowReviewPacketViolation(ValueError):
    """Raised when the D5 review packet is invalid."""


def _valid_identifier(value: Any) -> bool:
    return (
        isinstance(value, str)
        and _IDENTIFIER_PATTERN.fullmatch(value) is not None
    )


def _canonical_strings(values: list[str]) -> list[str]:
    return sorted(set(values))


def _safety_flags() -> dict[str, bool]:
    return {
        **{name: True for name in REQUIRED_TRUE_FLAGS},
        **{name: False for name in REQUIRED_FALSE_FLAGS},
    }


def _derive_overall_status(
    assignment_manifest: Mapping[str, Any],
) -> str:
    status = assignment_manifest["manifest_status"]

    if status == "BLOCKED":
        return "BLOCKED"

    if status == "DEGRADED":
        return "DEGRADED"

    return "READY_FOR_OPERATOR_REVIEW"


def _derive_reasons(
    assignment_manifest: Mapping[str, Any],
) -> tuple[list[str], list[str]]:
    blocking_reasons: list[str] = []
    warnings: list[str] = []

    for assignment in assignment_manifest["assignments"]:
        role_id = str(assignment["role_id"])
        slot_type = str(assignment["slot_type"])
        status = assignment["assignment_status"]

        if status == "BLOCKED":
            blocking_reasons.append(
                f"blocked:{role_id}:{slot_type}"
            )

        if status == "DEGRADED":
            warnings.append(
                f"degraded:{role_id}:{slot_type}"
            )

    return (
        _canonical_strings(blocking_reasons),
        _canonical_strings(warnings),
    )


def _validate_source_chain(
    *,
    boundary_contract: Mapping[str, Any],
    slot_binding_manifest: Mapping[str, Any],
    policy_eligibility_manifest: Mapping[str, Any],
    assignment_profile_manifest: Mapping[str, Any],
) -> None:
    contract_errors = (
        validate_multi_model_workflow_boundary_contract(
            boundary_contract
        )
    )
    if contract_errors:
        raise WorkflowReviewPacketViolation(
            "contract:" + ";".join(contract_errors)
        )

    slot_errors = (
        validate_role_model_slot_binding_manifest(
            slot_binding_manifest
        )
    )
    if slot_errors:
        raise WorkflowReviewPacketViolation(
            "slot_manifest:" + ";".join(slot_errors)
        )

    policy_errors = (
        validate_policy_eligibility_manifest(
            policy_eligibility_manifest
        )
    )
    if policy_errors:
        raise WorkflowReviewPacketViolation(
            "policy_manifest:" + ";".join(policy_errors)
        )

    assignment_errors = (
        validate_assignment_profile_manifest(
            assignment_profile_manifest
        )
    )
    if assignment_errors:
        raise WorkflowReviewPacketViolation(
            "assignment_manifest:"
            + ";".join(assignment_errors)
        )

    if slot_binding_manifest[
        "source_boundary_contract_id"
    ] != boundary_contract["contract_id"]:
        raise WorkflowReviewPacketViolation(
            "slot_contract_id_linkage_invalid"
        )

    if slot_binding_manifest[
        "source_boundary_contract_version"
    ] != boundary_contract["contract_version"]:
        raise WorkflowReviewPacketViolation(
            "slot_contract_version_linkage_invalid"
        )

    if policy_eligibility_manifest[
        "source_slot_manifest_id"
    ] != slot_binding_manifest["manifest_id"]:
        raise WorkflowReviewPacketViolation(
            "policy_slot_id_linkage_invalid"
        )

    if policy_eligibility_manifest[
        "source_slot_binding_version"
    ] != slot_binding_manifest["slot_binding_version"]:
        raise WorkflowReviewPacketViolation(
            "policy_slot_version_linkage_invalid"
        )

    if assignment_profile_manifest[
        "source_policy_manifest_id"
    ] != policy_eligibility_manifest["manifest_id"]:
        raise WorkflowReviewPacketViolation(
            "assignment_policy_id_linkage_invalid"
        )

    if assignment_profile_manifest[
        "source_policy_eligibility_version"
    ] != policy_eligibility_manifest[
        "policy_eligibility_version"
    ]:
        raise WorkflowReviewPacketViolation(
            "assignment_policy_version_linkage_invalid"
        )


def build_workflow_review_packet(
    *,
    review_packet_id: str,
    boundary_contract: Mapping[str, Any],
    slot_binding_manifest: Mapping[str, Any],
    policy_eligibility_manifest: Mapping[str, Any],
    assignment_profile_manifest: Mapping[str, Any],
) -> dict[str, Any]:
    """Build the deterministic non-executable D5 review packet."""
    if not _valid_identifier(review_packet_id):
        raise WorkflowReviewPacketViolation(
            "review_packet_id_invalid"
        )

    _validate_source_chain(
        boundary_contract=boundary_contract,
        slot_binding_manifest=slot_binding_manifest,
        policy_eligibility_manifest=(
            policy_eligibility_manifest
        ),
        assignment_profile_manifest=(
            assignment_profile_manifest
        ),
    )

    role_ids = _canonical_strings(
        [
            str(assignment["role_id"])
            for assignment in assignment_profile_manifest[
                "assignments"
            ]
        ]
    )

    blocking_reasons, warnings = _derive_reasons(
        assignment_profile_manifest
    )

    return {
        "review_packet_id": review_packet_id,
        "app_id": APP_ID,
        "stage_id": STAGE_ID,
        "review_packet_version": REVIEW_PACKET_VERSION,
        "planning_mode": PLANNING_MODE,
        "source_contract_id": (
            boundary_contract["contract_id"]
        ),
        "source_contract_version": (
            boundary_contract["contract_version"]
        ),
        "source_slot_manifest_id": (
            slot_binding_manifest["manifest_id"]
        ),
        "source_slot_binding_version": (
            slot_binding_manifest["slot_binding_version"]
        ),
        "source_policy_manifest_id": (
            policy_eligibility_manifest["manifest_id"]
        ),
        "source_policy_eligibility_version": (
            policy_eligibility_manifest[
                "policy_eligibility_version"
            ]
        ),
        "source_assignment_manifest_id": (
            assignment_profile_manifest["manifest_id"]
        ),
        "source_assignment_profile_version": (
            assignment_profile_manifest[
                "assignment_profile_version"
            ]
        ),
        "role_ids": role_ids,
        "model_slot_types": list(MODEL_SLOT_TYPES),
        "assignment_count": (
            assignment_profile_manifest[
                "assignment_count"
            ]
        ),
        "ready_count": (
            assignment_profile_manifest["ready_count"]
        ),
        "degraded_count": (
            assignment_profile_manifest[
                "degraded_count"
            ]
        ),
        "blocked_count": (
            assignment_profile_manifest["blocked_count"]
        ),
        "overall_status": _derive_overall_status(
            assignment_profile_manifest
        ),
        "blocking_reasons": blocking_reasons,
        "warnings": warnings,
        "policy_authority": "DETERMINISTIC_POLICY_ONLY",
        "operator_review_status": "REVIEW_REQUIRED",
        "operator_decision_status": "PENDING",
        "automatic_selection_status": "NOT_ALLOWED",
        "automatic_switching_status": "NOT_ALLOWED",
        "automatic_routing_status": "NOT_ALLOWED",
        "automatic_retry_status": "NOT_ALLOWED",
        "automatic_fallback_status": "NOT_ALLOWED",
        "model_invocation_status": "NOT_ALLOWED",
        "prompt_execution_status": "NOT_ALLOWED",
        "runtime_execution_status": "NOT_ALLOWED",
        "archive_writing_status": "NOT_ALLOWED",
        "real_execution_status": "NOT_ALLOWED",
        "safety_flags": _safety_flags(),
    }


def validate_workflow_review_packet(
    packet: object,
    *,
    boundary_contract: object,
    slot_binding_manifest: object,
    policy_eligibility_manifest: object,
    assignment_profile_manifest: object,
) -> list[str]:
    """Return deterministic D5 review packet errors."""
    if not isinstance(packet, Mapping):
        return ["review_packet_must_be_mapping"]

    sources = (
        boundary_contract,
        slot_binding_manifest,
        policy_eligibility_manifest,
        assignment_profile_manifest,
    )

    if any(not isinstance(item, Mapping) for item in sources):
        return ["review_packet_source_must_be_mapping"]

    errors: list[str] = []

    if set(packet.keys()) != set(
        REQUIRED_REVIEW_PACKET_FIELDS
    ):
        errors.append(
            "review_packet_fields_must_match_schema"
        )

    packet_id = packet.get("review_packet_id")

    if not _valid_identifier(packet_id):
        errors.append("review_packet_id_invalid")
        packet_id = "validation.review.packet"

    try:
        expected = build_workflow_review_packet(
            review_packet_id=packet_id,
            boundary_contract=boundary_contract,
            slot_binding_manifest=slot_binding_manifest,
            policy_eligibility_manifest=(
                policy_eligibility_manifest
            ),
            assignment_profile_manifest=(
                assignment_profile_manifest
            ),
        )
    except WorkflowReviewPacketViolation:
        return errors + [
            "review_packet_input_validation_failed"
        ]

    for field in REQUIRED_REVIEW_PACKET_FIELDS:
        if field == "review_packet_id":
            continue

        if packet.get(field) != expected[field]:
            errors.append(f"{field}_mismatch")

    if packet.get("overall_status") not in OVERALL_STATUSES:
        errors.append("overall_status_invalid")

    for field in (
        "automatic_selection_status",
        "automatic_switching_status",
        "automatic_routing_status",
        "automatic_retry_status",
        "automatic_fallback_status",
        "model_invocation_status",
        "prompt_execution_status",
        "runtime_execution_status",
        "archive_writing_status",
        "real_execution_status",
    ):
        if packet.get(field) != "NOT_ALLOWED":
            errors.append(f"{field}_invalid")

    if packet.get("operator_review_status") != (
        "REVIEW_REQUIRED"
    ):
        errors.append("operator_review_status_invalid")

    if packet.get("operator_decision_status") != "PENDING":
        errors.append("operator_decision_status_invalid")

    return errors