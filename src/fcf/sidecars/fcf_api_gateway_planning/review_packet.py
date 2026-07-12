"""Planning-only governance review packet for the FCF API Gateway."""

import re
from collections.abc import Mapping
from typing import Any

from .contract import (
    APP_ID,
    PLANNING_MODE,
    validate_fcf_api_gateway_boundary_contract,
)
from .policy_gate import (
    validate_fcf_api_gateway_policy_gate_decision,
)
from .request_envelope import (
    validate_fcf_api_gateway_request_envelope,
)
from .response_envelope import (
    validate_fcf_api_gateway_response_envelope,
)

STAGE_ID = "FCF-API-GATEWAY-PLANNING-D5"
REVIEW_PACKET_VERSION = "1.0.0"

OVERALL_STATUSES = (
    "READY_FOR_OPERATOR_REVIEW",
    "OPERATOR_CONFIRMATION_REQUIRED",
    "BLOCKED",
)

REQUIRED_REVIEW_PACKET_FIELDS = (
    "review_packet_id",
    "app_id",
    "stage_id",
    "review_packet_version",
    "planning_mode",
    "source_contract_id",
    "source_request_id",
    "source_policy_decision_id",
    "source_response_id",
    "correlation_id",
    "request_class",
    "policy_version",
    "config_snapshot_id",
    "source_artifact_ids",
    "policy_gate_status",
    "response_status",
    "overall_status",
    "blocking_reasons",
    "warnings",
    "operator_review_status",
    "operator_decision_status",
    "response_transport_active",
    "automatic_routing_allowed",
    "runtime_activation_allowed",
    "model_invocation_allowed",
    "archive_writing_allowed",
    "real_execution_allowed",
)

_IDENTIFIER_PATTERN = re.compile(
    r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$"
)


class FcfApiGatewayReviewPacketViolation(ValueError):
    """Raised when a D5 review packet cannot be built."""


def _valid_identifier(value: Any) -> bool:
    return (
        isinstance(value, str)
        and _IDENTIFIER_PATTERN.fullmatch(value) is not None
    )


def _canonical_reasons(value: object) -> list[str]:
    if not isinstance(value, list):
        return []

    return sorted(
        {
            item
            for item in value
            if isinstance(item, str) and item
        }
    )


def _derive_overall_status(
    policy_gate_decision: Mapping[str, Any],
    response_envelope: Mapping[str, Any],
) -> str:
    if (
        policy_gate_decision["policy_gate_status"] == "BLOCKED"
        or response_envelope["status"] == "BLOCKED"
    ):
        return "BLOCKED"

    if response_envelope["status"] == (
        "OPERATOR_CONFIRMATION_PENDING"
    ):
        return "OPERATOR_CONFIRMATION_REQUIRED"

    return "READY_FOR_OPERATOR_REVIEW"


def build_fcf_api_gateway_review_packet(
    *,
    review_packet_id: str,
    boundary_contract: Mapping[str, Any],
    request_envelope: Mapping[str, Any],
    policy_gate_decision: Mapping[str, Any],
    response_envelope: Mapping[str, Any],
) -> dict[str, Any]:
    """Build a deterministic planning-only D5 review packet."""
    if not _valid_identifier(review_packet_id):
        raise FcfApiGatewayReviewPacketViolation(
            "review_packet_id_invalid"
        )

    contract_errors = (
        validate_fcf_api_gateway_boundary_contract(
            boundary_contract
        )
    )
    if contract_errors:
        raise FcfApiGatewayReviewPacketViolation(
            "contract:" + ";".join(contract_errors)
        )

    request_errors = (
        validate_fcf_api_gateway_request_envelope(
            request_envelope
        )
    )
    if request_errors:
        raise FcfApiGatewayReviewPacketViolation(
            "request:" + ";".join(request_errors)
        )

    if request_envelope["source_contract_id"] != (
        boundary_contract["contract_id"]
    ):
        raise FcfApiGatewayReviewPacketViolation(
            "request_contract_linkage_invalid"
        )

    policy_errors = (
        validate_fcf_api_gateway_policy_gate_decision(
            policy_gate_decision,
            request_envelope,
        )
    )
    if policy_errors:
        raise FcfApiGatewayReviewPacketViolation(
            "policy_gate:" + ";".join(policy_errors)
        )

    response_errors = (
        validate_fcf_api_gateway_response_envelope(
            response_envelope,
            request_envelope,
            policy_gate_decision,
        )
    )
    if response_errors:
        raise FcfApiGatewayReviewPacketViolation(
            "response:" + ";".join(response_errors)
        )

    overall_status = _derive_overall_status(
        policy_gate_decision,
        response_envelope,
    )

    blocking_reasons = _canonical_reasons(
        response_envelope["errors"]
    )
    warnings = _canonical_reasons(
        response_envelope["warnings"]
    )

    return {
        "review_packet_id": review_packet_id,
        "app_id": APP_ID,
        "stage_id": STAGE_ID,
        "review_packet_version": REVIEW_PACKET_VERSION,
        "planning_mode": PLANNING_MODE,
        "source_contract_id": boundary_contract["contract_id"],
        "source_request_id": request_envelope["request_id"],
        "source_policy_decision_id": (
            policy_gate_decision["decision_id"]
        ),
        "source_response_id": response_envelope["response_id"],
        "correlation_id": request_envelope["correlation_id"],
        "request_class": request_envelope["request_class"],
        "policy_version": request_envelope["policy_version"],
        "config_snapshot_id": (
            request_envelope["config_snapshot_id"]
        ),
        "source_artifact_ids": list(
            request_envelope["source_artifact_ids"]
        ),
        "policy_gate_status": (
            policy_gate_decision["policy_gate_status"]
        ),
        "response_status": response_envelope["status"],
        "overall_status": overall_status,
        "blocking_reasons": blocking_reasons,
        "warnings": warnings,
        "operator_review_status": "REVIEW_REQUIRED",
        "operator_decision_status": "PENDING",
        "response_transport_active": False,
        "automatic_routing_allowed": False,
        "runtime_activation_allowed": False,
        "model_invocation_allowed": False,
        "archive_writing_allowed": False,
        "real_execution_allowed": False,
    }


def validate_fcf_api_gateway_review_packet(
    packet: object,
    boundary_contract: object,
    request_envelope: object,
    policy_gate_decision: object,
    response_envelope: object,
) -> list[str]:
    """Return deterministic D5 review-packet errors."""
    if not isinstance(packet, Mapping):
        return ["review_packet_must_be_mapping"]

    if not isinstance(boundary_contract, Mapping):
        return ["boundary_contract_must_be_mapping"]

    if not isinstance(request_envelope, Mapping):
        return ["request_envelope_must_be_mapping"]

    if not isinstance(policy_gate_decision, Mapping):
        return ["policy_gate_decision_must_be_mapping"]

    if not isinstance(response_envelope, Mapping):
        return ["response_envelope_must_be_mapping"]

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
        expected = build_fcf_api_gateway_review_packet(
            review_packet_id=packet_id,
            boundary_contract=boundary_contract,
            request_envelope=request_envelope,
            policy_gate_decision=policy_gate_decision,
            response_envelope=response_envelope,
        )
    except FcfApiGatewayReviewPacketViolation:
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
        "response_transport_active",
        "automatic_routing_allowed",
        "runtime_activation_allowed",
        "model_invocation_allowed",
        "archive_writing_allowed",
        "real_execution_allowed",
    ):
        if packet.get(field) is not False:
            errors.append(f"{field}_must_be_false")

    return errors
