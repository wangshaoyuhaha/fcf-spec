"""Planning-only D6 final Operator handoff."""

import re
from typing import Any, Mapping

from .contract import APP_ID, PLANNING_MODE
from .review_packet import (
    validate_workflow_review_packet,
)

STAGE_ID = "AI-MULTI-MODEL-WORKFLOW-PLANNING-D6"
HANDOFF_VERSION = "1.0.0"

HANDOFF_STATUSES = (
    "READY_FOR_OPERATOR_MERGE_REVIEW",
    "DEGRADED_OPERATOR_REVIEW_REQUIRED_BEFORE_MERGE_REVIEW",
    "BLOCKED_REPAIR_REQUIRED",
)

REQUIRED_HANDOFF_FIELDS = (
    "handoff_id",
    "app_id",
    "stage_id",
    "handoff_version",
    "planning_mode",
    "branch_name",
    "source_review_packet_id",
    "source_overall_status",
    "source_contract_id",
    "source_slot_manifest_id",
    "source_policy_manifest_id",
    "source_assignment_manifest_id",
    "handoff_status",
    "allowed_operator_actions",
    "operator_action_required",
    "operator_decision_status",
    "main_merge_review_eligible",
    "main_merge_allowed_without_operator_confirmation",
    "repair_required",
    "automatic_selection_allowed",
    "automatic_switching_allowed",
    "automatic_routing_allowed",
    "automatic_retry_allowed",
    "automatic_fallback_allowed",
    "model_invocation_allowed",
    "prompt_execution_allowed",
    "runtime_execution_allowed",
    "archive_writing_allowed",
    "real_execution_allowed",
    "tag_allowed",
    "release_allowed",
    "deploy_allowed",
)

_IDENTIFIER_PATTERN = re.compile(
    r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$"
)


class WorkflowFinalHandoffViolation(ValueError):
    """Raised when the D6 final handoff is invalid."""


def _valid_identifier(value: Any) -> bool:
    return (
        isinstance(value, str)
        and _IDENTIFIER_PATTERN.fullmatch(value) is not None
    )


def _derive_handoff_state(
    source_status: str,
) -> tuple[str, bool, bool, list[str]]:
    if source_status == "READY_FOR_OPERATOR_REVIEW":
        return (
            "READY_FOR_OPERATOR_MERGE_REVIEW",
            True,
            False,
            [
                "ACKNOWLEDGE_PACKET",
                "APPROVE_MAIN_MERGE_REVIEW",
                "REJECT_PACKET",
                "REQUEST_REPAIR",
            ],
        )

    if source_status == "DEGRADED":
        return (
            "DEGRADED_OPERATOR_REVIEW_REQUIRED_BEFORE_MERGE_REVIEW",
            False,
            False,
            [
                "ACKNOWLEDGE_PACKET",
                "REJECT_PACKET",
                "REQUEST_REPAIR",
            ],
        )

    return (
        "BLOCKED_REPAIR_REQUIRED",
        False,
        True,
        [
            "REJECT_PACKET",
            "REQUEST_REPAIR",
        ],
    )


def build_workflow_final_handoff(
    *,
    handoff_id: str,
    review_packet: Mapping[str, Any],
    boundary_contract: Mapping[str, Any],
    slot_binding_manifest: Mapping[str, Any],
    policy_eligibility_manifest: Mapping[str, Any],
    assignment_profile_manifest: Mapping[str, Any],
    branch_name: str = (
        "sidecar-ai-multi-model-workflow-planning-app-1"
    ),
) -> dict[str, Any]:
    """Build deterministic D6 planning-only Operator handoff."""
    if not _valid_identifier(handoff_id):
        raise WorkflowFinalHandoffViolation(
            "handoff_id_invalid"
        )

    if not isinstance(branch_name, str) or not branch_name:
        raise WorkflowFinalHandoffViolation(
            "branch_name_invalid"
        )

    packet_errors = validate_workflow_review_packet(
        review_packet,
        boundary_contract=boundary_contract,
        slot_binding_manifest=slot_binding_manifest,
        policy_eligibility_manifest=(
            policy_eligibility_manifest
        ),
        assignment_profile_manifest=(
            assignment_profile_manifest
        ),
    )

    if packet_errors:
        raise WorkflowFinalHandoffViolation(
            ";".join(packet_errors)
        )

    source_status = str(
        review_packet["overall_status"]
    )

    (
        handoff_status,
        merge_review_eligible,
        repair_required,
        allowed_actions,
    ) = _derive_handoff_state(source_status)

    return {
        "handoff_id": handoff_id,
        "app_id": APP_ID,
        "stage_id": STAGE_ID,
        "handoff_version": HANDOFF_VERSION,
        "planning_mode": PLANNING_MODE,
        "branch_name": branch_name,
        "source_review_packet_id": (
            review_packet["review_packet_id"]
        ),
        "source_overall_status": source_status,
        "source_contract_id": (
            review_packet["source_contract_id"]
        ),
        "source_slot_manifest_id": (
            review_packet["source_slot_manifest_id"]
        ),
        "source_policy_manifest_id": (
            review_packet["source_policy_manifest_id"]
        ),
        "source_assignment_manifest_id": (
            review_packet[
                "source_assignment_manifest_id"
            ]
        ),
        "handoff_status": handoff_status,
        "allowed_operator_actions": list(
            allowed_actions
        ),
        "operator_action_required": True,
        "operator_decision_status": "PENDING",
        "main_merge_review_eligible": (
            merge_review_eligible
        ),
        "main_merge_allowed_without_operator_confirmation": (
            False
        ),
        "repair_required": repair_required,
        "automatic_selection_allowed": False,
        "automatic_switching_allowed": False,
        "automatic_routing_allowed": False,
        "automatic_retry_allowed": False,
        "automatic_fallback_allowed": False,
        "model_invocation_allowed": False,
        "prompt_execution_allowed": False,
        "runtime_execution_allowed": False,
        "archive_writing_allowed": False,
        "real_execution_allowed": False,
        "tag_allowed": False,
        "release_allowed": False,
        "deploy_allowed": False,
    }


def validate_workflow_final_handoff(
    handoff: object,
    *,
    review_packet: object,
    boundary_contract: object,
    slot_binding_manifest: object,
    policy_eligibility_manifest: object,
    assignment_profile_manifest: object,
) -> list[str]:
    """Return deterministic D6 final-handoff errors."""
    if not isinstance(handoff, Mapping):
        return ["handoff_must_be_mapping"]

    if not isinstance(review_packet, Mapping):
        return ["review_packet_must_be_mapping"]

    sources = (
        boundary_contract,
        slot_binding_manifest,
        policy_eligibility_manifest,
        assignment_profile_manifest,
    )

    if any(not isinstance(item, Mapping) for item in sources):
        return ["handoff_source_inputs_must_be_mappings"]

    errors: list[str] = []

    if set(handoff.keys()) != set(
        REQUIRED_HANDOFF_FIELDS
    ):
        errors.append(
            "handoff_fields_must_match_schema"
        )

    handoff_id = handoff.get("handoff_id")

    if not _valid_identifier(handoff_id):
        errors.append("handoff_id_invalid")
        handoff_id = "validation.handoff.final"

    branch_name = handoff.get("branch_name")

    if not isinstance(branch_name, str) or not branch_name:
        errors.append("branch_name_invalid")
        branch_name = (
            "sidecar-ai-multi-model-workflow-planning-app-1"
        )

    try:
        expected = build_workflow_final_handoff(
            handoff_id=handoff_id,
            review_packet=review_packet,
            boundary_contract=boundary_contract,
            slot_binding_manifest=slot_binding_manifest,
            policy_eligibility_manifest=(
                policy_eligibility_manifest
            ),
            assignment_profile_manifest=(
                assignment_profile_manifest
            ),
            branch_name=branch_name,
        )
    except WorkflowFinalHandoffViolation:
        return errors + [
            "handoff_input_validation_failed"
        ]

    for field in REQUIRED_HANDOFF_FIELDS:
        if field == "handoff_id":
            continue

        if handoff.get(field) != expected[field]:
            errors.append(f"{field}_mismatch")

    if handoff.get("handoff_status") not in (
        HANDOFF_STATUSES
    ):
        errors.append("handoff_status_invalid")

    if handoff.get("operator_action_required") is not True:
        errors.append(
            "operator_action_required_must_be_true"
        )

    if handoff.get("operator_decision_status") != "PENDING":
        errors.append(
            "operator_decision_status_invalid"
        )

    false_fields = (
        "main_merge_allowed_without_operator_confirmation",
        "automatic_selection_allowed",
        "automatic_switching_allowed",
        "automatic_routing_allowed",
        "automatic_retry_allowed",
        "automatic_fallback_allowed",
        "model_invocation_allowed",
        "prompt_execution_allowed",
        "runtime_execution_allowed",
        "archive_writing_allowed",
        "real_execution_allowed",
        "tag_allowed",
        "release_allowed",
        "deploy_allowed",
    )

    for field in false_fields:
        if handoff.get(field) is not False:
            errors.append(f"{field}_must_be_false")

    return errors