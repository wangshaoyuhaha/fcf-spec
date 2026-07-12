"""Planning-only D6 final Operator handoff."""

import re
from collections.abc import Mapping
from copy import deepcopy
from typing import Any

from .review_packet import (
    validate_governance_review_packet,
)

APP_ID = "READ-ONLY-DATA-GATEWAY-PLANNING-APP-1"
STAGE_ID = "READ-ONLY-DATA-GATEWAY-PLANNING-D6"
HANDOFF_VERSION = "1.0.0"
PLANNING_MODE = "PLANNING_ONLY"

_IDENTIFIER_PATTERN = re.compile(
    r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$"
)


class FinalOperatorHandoffViolation(ValueError):
    """Raised when D6 handoff input is invalid."""


def _valid_identifier(value: Any) -> bool:
    return (
        isinstance(value, str)
        and _IDENTIFIER_PATTERN.fullmatch(value) is not None
    )


def build_final_operator_handoff(
    *,
    handoff_id: str,
    review_packet: Mapping[str, Any],
    normalized_envelope: Mapping[str, Any],
    source_policy_decision: Mapping[str, Any],
    credential_isolation_contract: Mapping[str, Any],
    branch_name: str = (
        "sidecar-read-only-data-gateway-planning-app-1"
    ),
) -> dict[str, Any]:
    """Build deterministic D6 Operator handoff."""
    if not _valid_identifier(handoff_id):
        raise FinalOperatorHandoffViolation(
            "handoff_id_invalid"
        )

    if not isinstance(branch_name, str) or not branch_name:
        raise FinalOperatorHandoffViolation(
            "branch_name_invalid"
        )

    inputs = (
        review_packet,
        normalized_envelope,
        source_policy_decision,
        credential_isolation_contract,
    )

    if not all(isinstance(item, Mapping) for item in inputs):
        raise FinalOperatorHandoffViolation(
            "handoff_inputs_must_be_mappings"
        )

    packet = deepcopy(dict(review_packet))
    envelope = deepcopy(dict(normalized_envelope))
    decision = deepcopy(dict(source_policy_decision))
    credential_contract = deepcopy(
        dict(credential_isolation_contract)
    )

    packet_errors = validate_governance_review_packet(
        packet,
        envelope,
        decision,
        credential_contract,
    )

    if packet_errors:
        raise FinalOperatorHandoffViolation(
            ";".join(packet_errors)
        )

    source_status = packet["overall_status"]

    if source_status == "READY_FOR_OPERATOR_REVIEW":
        handoff_status = (
            "READY_FOR_OPERATOR_MERGE_REVIEW"
        )
        merge_review_eligible = True
        repair_required = False
        allowed_actions = [
            "ACKNOWLEDGE_PACKET",
            "APPROVE_MAIN_MERGE_REVIEW",
            "REJECT_PACKET",
            "REQUEST_REPAIR",
        ]

    if source_status == "DEGRADED":
        handoff_status = (
            "DEGRADED_OPERATOR_REVIEW_REQUIRED"
        )
        merge_review_eligible = False
        repair_required = True
        allowed_actions = [
            "ACKNOWLEDGE_PACKET",
            "REJECT_PACKET",
            "REQUEST_REPAIR",
        ]

    if source_status == "BLOCKED":
        handoff_status = "BLOCKED_REPAIR_REQUIRED"
        merge_review_eligible = False
        repair_required = True
        allowed_actions = [
            "REJECT_PACKET",
            "REQUEST_REPAIR",
        ]

    return {
        "handoff_id": handoff_id,
        "app_id": APP_ID,
        "stage_id": STAGE_ID,
        "handoff_version": HANDOFF_VERSION,
        "planning_mode": PLANNING_MODE,
        "branch_name": branch_name,
        "source_review_packet_id": (
            packet["review_packet_id"]
        ),
        "source_overall_status": source_status,
        "handoff_status": handoff_status,
        "allowed_operator_actions": list(
            allowed_actions
        ),
        "operator_action_required": True,
        "operator_decision_status": "PENDING",
        "main_merge_review_eligible": (
            merge_review_eligible
        ),
        "main_merge_allowed_without_operator_confirmation": False,
        "repair_required": repair_required,
        "model_invocation_allowed": False,
        "prompt_execution_allowed": False,
        "automatic_routing_allowed": False,
        "runtime_activation_allowed": False,
        "archive_writing_allowed": False,
        "tag_allowed": False,
        "release_allowed": False,
        "deploy_allowed": False,
    }

REQUIRED_HANDOFF_FIELDS = (
    "handoff_id",
    "app_id",
    "stage_id",
    "handoff_version",
    "planning_mode",
    "branch_name",
    "source_review_packet_id",
    "source_overall_status",
    "handoff_status",
    "allowed_operator_actions",
    "operator_action_required",
    "operator_decision_status",
    "main_merge_review_eligible",
    "main_merge_allowed_without_operator_confirmation",
    "repair_required",
    "model_invocation_allowed",
    "prompt_execution_allowed",
    "automatic_routing_allowed",
    "runtime_activation_allowed",
    "archive_writing_allowed",
    "tag_allowed",
    "release_allowed",
    "deploy_allowed",
)


def validate_final_operator_handoff(
    handoff: object,
    review_packet: object,
    normalized_envelope: object,
    source_policy_decision: object,
    credential_isolation_contract: object,
) -> list[str]:
    """Return deterministic D6 handoff validation errors."""
    if not isinstance(handoff, Mapping):
        return ["handoff_must_be_mapping"]

    if not isinstance(review_packet, Mapping):
        return ["review_packet_must_be_mapping"]

    if not isinstance(normalized_envelope, Mapping):
        return ["normalized_envelope_must_be_mapping"]

    if not isinstance(source_policy_decision, Mapping):
        return ["source_policy_decision_must_be_mapping"]

    if not isinstance(credential_isolation_contract, Mapping):
        return ["credential_isolation_contract_must_be_mapping"]

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
            "sidecar-read-only-data-gateway-planning-app-1"
        )

    try:
        expected = build_final_operator_handoff(
            handoff_id=handoff_id,
            review_packet=review_packet,
            normalized_envelope=normalized_envelope,
            source_policy_decision=source_policy_decision,
            credential_isolation_contract=(
                credential_isolation_contract
            ),
            branch_name=branch_name,
        )
    except FinalOperatorHandoffViolation:
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
        "model_invocation_allowed",
        "prompt_execution_allowed",
        "automatic_routing_allowed",
        "runtime_activation_allowed",
        "archive_writing_allowed",
        "tag_allowed",
        "release_allowed",
        "deploy_allowed",
    )

    for field in false_fields:
        if handoff.get(field) is not False:
            errors.append(f"{field}_must_be_false")

    return errors