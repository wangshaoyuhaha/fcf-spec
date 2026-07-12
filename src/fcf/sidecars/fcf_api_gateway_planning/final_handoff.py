"""Planning-only D6 final Operator handoff."""

import re
from collections.abc import Mapping
from typing import Any

from .contract import APP_ID, PLANNING_MODE
from .review_packet import (
    validate_fcf_api_gateway_review_packet,
)

STAGE_ID = "FCF-API-GATEWAY-PLANNING-D6"
HANDOFF_VERSION = "1.0.0"

REQUIRED_HANDOFF_FIELDS = (
    "handoff_id",
    "app_id",
    "stage_id",
    "handoff_version",
    "planning_mode",
    "branch_name",
    "source_review_packet_id",
    "source_overall_status",
    "correlation_id",
    "handoff_status",
    "allowed_operator_actions",
    "operator_action_required",
    "operator_decision_status",
    "main_merge_review_eligible",
    "main_merge_allowed_without_operator_confirmation",
    "repair_required",
    "http_server_active",
    "port_listener_active",
    "response_transport_active",
    "model_invocation_allowed",
    "prompt_execution_allowed",
    "automatic_routing_allowed",
    "runtime_activation_allowed",
    "archive_writing_allowed",
    "real_execution_allowed",
    "tag_allowed",
    "release_allowed",
    "deploy_allowed",
)

_IDENTIFIER_PATTERN = re.compile(
    r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$"
)


class FcfApiGatewayFinalHandoffViolation(ValueError):
    """Raised when the D6 final handoff cannot be built."""


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

    if source_status == "OPERATOR_CONFIRMATION_REQUIRED":
        return (
            "OPERATOR_CONFIRMATION_REQUIRED_BEFORE_MERGE_REVIEW",
            False,
            False,
            [
                "ACKNOWLEDGE_PACKET",
                "CONFIRM_OPERATOR_CONTROL_REQUEST",
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


def build_fcf_api_gateway_final_handoff(
    *,
    handoff_id: str,
    review_packet: Mapping[str, Any],
    boundary_contract: Mapping[str, Any],
    request_envelope: Mapping[str, Any],
    policy_gate_decision: Mapping[str, Any],
    response_envelope: Mapping[str, Any],
    branch_name: str = (
        "sidecar-fcf-api-gateway-planning-app-1"
    ),
) -> dict[str, Any]:
    """Build deterministic D6 planning-only Operator handoff."""
    if not _valid_identifier(handoff_id):
        raise FcfApiGatewayFinalHandoffViolation(
            "handoff_id_invalid"
        )

    if not isinstance(branch_name, str) or not branch_name:
        raise FcfApiGatewayFinalHandoffViolation(
            "branch_name_invalid"
        )

    packet_errors = (
        validate_fcf_api_gateway_review_packet(
            review_packet,
            boundary_contract,
            request_envelope,
            policy_gate_decision,
            response_envelope,
        )
    )
    if packet_errors:
        raise FcfApiGatewayFinalHandoffViolation(
            ";".join(packet_errors)
        )

    source_status = review_packet["overall_status"]

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
        "correlation_id": review_packet["correlation_id"],
        "handoff_status": handoff_status,
        "allowed_operator_actions": list(allowed_actions),
        "operator_action_required": True,
        "operator_decision_status": "PENDING",
        "main_merge_review_eligible": merge_review_eligible,
        "main_merge_allowed_without_operator_confirmation": False,
        "repair_required": repair_required,
        "http_server_active": False,
        "port_listener_active": False,
        "response_transport_active": False,
        "model_invocation_allowed": False,
        "prompt_execution_allowed": False,
        "automatic_routing_allowed": False,
        "runtime_activation_allowed": False,
        "archive_writing_allowed": False,
        "real_execution_allowed": False,
        "tag_allowed": False,
        "release_allowed": False,
        "deploy_allowed": False,
    }


def validate_fcf_api_gateway_final_handoff(
    handoff: object,
    review_packet: object,
    boundary_contract: object,
    request_envelope: object,
    policy_gate_decision: object,
    response_envelope: object,
) -> list[str]:
    """Return deterministic D6 final-handoff errors."""
    if not isinstance(handoff, Mapping):
        return ["handoff_must_be_mapping"]

    if not isinstance(review_packet, Mapping):
        return ["review_packet_must_be_mapping"]

    inputs = (
        boundary_contract,
        request_envelope,
        policy_gate_decision,
        response_envelope,
    )
    if not all(isinstance(item, Mapping) for item in inputs):
        return ["handoff_source_inputs_must_be_mappings"]

    errors: list[str] = []

    if set(handoff.keys()) != set(REQUIRED_HANDOFF_FIELDS):
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
            "sidecar-fcf-api-gateway-planning-app-1"
        )

    try:
        expected = build_fcf_api_gateway_final_handoff(
            handoff_id=handoff_id,
            review_packet=review_packet,
            boundary_contract=boundary_contract,
            request_envelope=request_envelope,
            policy_gate_decision=policy_gate_decision,
            response_envelope=response_envelope,
            branch_name=branch_name,
        )
    except FcfApiGatewayFinalHandoffViolation:
        return errors + [
            "handoff_input_validation_failed"
        ]

    for field in REQUIRED_HANDOFF_FIELDS:
        if field == "handoff_id":
            continue

        if handoff.get(field) != expected[field]:
            errors.append(f"{field}_mismatch")

    if handoff.get("operator_action_required") is not True:
        errors.append(
            "operator_action_required_must_be_true"
        )

    false_fields = (
        "main_merge_allowed_without_operator_confirmation",
        "http_server_active",
        "port_listener_active",
        "response_transport_active",
        "model_invocation_allowed",
        "prompt_execution_allowed",
        "automatic_routing_allowed",
        "runtime_activation_allowed",
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
