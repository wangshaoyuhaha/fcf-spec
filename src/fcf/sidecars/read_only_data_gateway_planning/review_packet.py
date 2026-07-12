"""Planning-only D5 governance review packet."""

import re
from collections.abc import Mapping
from copy import deepcopy
from typing import Any

from .credential_isolation import (
    validate_credential_isolation_contract,
)
from .normalized_envelope import (
    validate_normalized_data_envelope,
)
from .source_policy import (
    validate_source_policy_decision,
)

APP_ID = "READ-ONLY-DATA-GATEWAY-PLANNING-APP-1"
STAGE_ID = "READ-ONLY-DATA-GATEWAY-PLANNING-D5"
PACKET_VERSION = "1.0.0"
PLANNING_MODE = "PLANNING_ONLY"

OVERALL_STATUSES = (
    "READY_FOR_OPERATOR_REVIEW",
    "DEGRADED",
    "BLOCKED",
)

_IDENTIFIER_PATTERN = re.compile(
    r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$"
)


class GovernanceReviewPacketViolation(ValueError):
    """Raised when D5 review packet input is invalid."""


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


def build_governance_review_packet(
    *,
    review_packet_id: str,
    normalized_envelope: Mapping[str, Any],
    source_policy_decision: Mapping[str, Any],
    credential_isolation_contract: Mapping[str, Any],
) -> dict[str, Any]:
    """Build a deterministic review-only D5 packet."""
    if not _valid_identifier(review_packet_id):
        raise GovernanceReviewPacketViolation(
            "review_packet_id_invalid"
        )

    inputs = (
        normalized_envelope,
        source_policy_decision,
        credential_isolation_contract,
    )

    if not all(isinstance(item, Mapping) for item in inputs):
        raise GovernanceReviewPacketViolation(
            "review_packet_inputs_must_be_mappings"
        )

    envelope = deepcopy(dict(normalized_envelope))
    decision = deepcopy(dict(source_policy_decision))
    credential_contract = deepcopy(
        dict(credential_isolation_contract)
    )

    envelope_errors = validate_normalized_data_envelope(
        envelope
    )

    if envelope_errors:
        raise GovernanceReviewPacketViolation(
            "envelope:" + ";".join(envelope_errors)
        )

    decision_errors = validate_source_policy_decision(
        decision,
        envelope,
    )

    if decision_errors:
        raise GovernanceReviewPacketViolation(
            "source_policy:" + ";".join(decision_errors)
        )

    credential_errors = (
        validate_credential_isolation_contract(
            credential_contract
        )
    )

    if credential_errors:
        raise GovernanceReviewPacketViolation(
            "credential_isolation:"
            + ";".join(credential_errors)
        )

    source_status = decision["source_policy_status"]

    blocking_reasons = _canonical_reasons(
        decision["blocking_reasons"]
    )
    degradation_reasons = _canonical_reasons(
        decision["degradation_reasons"]
    )

    if source_status == "BLOCKED":
        overall_status = "BLOCKED"
    elif source_status == "DEGRADED":
        overall_status = "DEGRADED"
    else:
        overall_status = "READY_FOR_OPERATOR_REVIEW"

    return {
        "review_packet_id": review_packet_id,
        "app_id": APP_ID,
        "stage_id": STAGE_ID,
        "packet_version": PACKET_VERSION,
        "planning_mode": PLANNING_MODE,
        "source_envelope_id": envelope["envelope_id"],
        "source_evidence_id": envelope["evidence_id"],
        "source_policy_decision_id": decision["decision_id"],
        "source_policy_status": source_status,
        "credential_isolation_contract_id": (
            credential_contract["contract_id"]
        ),
        "credential_isolation_status": "VALIDATED",
        "overall_status": overall_status,
        "blocking_reasons": list(blocking_reasons),
        "degradation_reasons": list(
            degradation_reasons
        ),
        "operator_review_status": "REVIEW_REQUIRED",
        "operator_decision_status": "PENDING",
        "model_invocation_allowed": False,
        "automatic_routing_allowed": False,
        "runtime_activation_allowed": False,
        "archive_writing_allowed": False,
    }

REQUIRED_PACKET_FIELDS = (
    "review_packet_id",
    "app_id",
    "stage_id",
    "packet_version",
    "planning_mode",
    "source_envelope_id",
    "source_evidence_id",
    "source_policy_decision_id",
    "source_policy_status",
    "credential_isolation_contract_id",
    "credential_isolation_status",
    "overall_status",
    "blocking_reasons",
    "degradation_reasons",
    "operator_review_status",
    "operator_decision_status",
    "model_invocation_allowed",
    "automatic_routing_allowed",
    "runtime_activation_allowed",
    "archive_writing_allowed",
)


def validate_governance_review_packet(
    packet: object,
    normalized_envelope: object,
    source_policy_decision: object,
    credential_isolation_contract: object,
) -> list[str]:
    """Return deterministic D5 review-packet validation errors."""
    if not isinstance(packet, Mapping):
        return ["packet_must_be_mapping"]

    if not isinstance(normalized_envelope, Mapping):
        return ["normalized_envelope_must_be_mapping"]

    if not isinstance(source_policy_decision, Mapping):
        return ["source_policy_decision_must_be_mapping"]

    if not isinstance(credential_isolation_contract, Mapping):
        return ["credential_isolation_contract_must_be_mapping"]

    errors: list[str] = []

    if set(packet.keys()) != set(REQUIRED_PACKET_FIELDS):
        errors.append(
            "packet_fields_must_match_schema"
        )

    packet_id = packet.get("review_packet_id")

    if not _valid_identifier(packet_id):
        errors.append("review_packet_id_invalid")
        packet_id = "validation.review.packet"

    try:
        expected = build_governance_review_packet(
            review_packet_id=packet_id,
            normalized_envelope=normalized_envelope,
            source_policy_decision=source_policy_decision,
            credential_isolation_contract=(
                credential_isolation_contract
            ),
        )
    except GovernanceReviewPacketViolation:
        return errors + [
            "review_packet_input_validation_failed"
        ]

    for field in REQUIRED_PACKET_FIELDS:
        if field == "review_packet_id":
            continue

        if packet.get(field) != expected[field]:
            errors.append(f"{field}_mismatch")

    if packet.get("model_invocation_allowed") is not False:
        errors.append(
            "model_invocation_allowed_must_be_false"
        )

    if packet.get("automatic_routing_allowed") is not False:
        errors.append(
            "automatic_routing_allowed_must_be_false"
        )

    if packet.get("runtime_activation_allowed") is not False:
        errors.append(
            "runtime_activation_allowed_must_be_false"
        )

    if packet.get("archive_writing_allowed") is not False:
        errors.append(
            "archive_writing_allowed_must_be_false"
        )

    return errors