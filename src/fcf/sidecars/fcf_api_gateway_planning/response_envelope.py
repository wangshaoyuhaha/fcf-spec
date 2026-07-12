"""Planning-only response envelope for the FCF API Gateway."""

import re
from collections.abc import Mapping
from datetime import datetime
from typing import Any

from .policy_gate import (
    validate_fcf_api_gateway_policy_gate_decision,
)
from .request_envelope import (
    validate_fcf_api_gateway_request_envelope,
)

STAGE_ID = "FCF-API-GATEWAY-PLANNING-D4"
RESPONSE_ENVELOPE_VERSION = "1.0.0"

RESPONSE_STATUSES = (
    "READ_ONLY_RESPONSE_PLANNED",
    "OPERATOR_CONFIRMATION_PENDING",
    "BLOCKED",
)

REQUIRED_RESPONSE_ENVELOPE_FIELDS = (
    "response_id",
    "stage_id",
    "response_envelope_version",
    "source_request_id",
    "source_policy_decision_id",
    "correlation_id",
    "source_artifact_ids",
    "status",
    "policy_decision",
    "errors",
    "warnings",
    "generated_at_utc",
    "operator_review_required",
    "operator_confirmation_required",
    "response_transport_active",
    "automatic_routing_allowed",
    "runtime_activation_allowed",
    "model_invocation_allowed",
    "archive_writing_allowed",
)

_IDENTIFIER_PATTERN = re.compile(
    r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$"
)


class FcfApiGatewayResponseEnvelopeViolation(ValueError):
    """Raised when a D4 response envelope cannot be built."""


def _valid_identifier(value: Any) -> bool:
    return (
        isinstance(value, str)
        and _IDENTIFIER_PATTERN.fullmatch(value) is not None
    )


def _valid_timestamp(value: Any) -> bool:
    if not isinstance(value, str):
        return False

    try:
        parsed = datetime.fromisoformat(
            value.replace("Z", "+00:00")
        )
    except ValueError:
        return False

    return parsed.tzinfo is not None


def _derive_response_state(
    policy_gate_decision: Mapping[str, Any],
) -> tuple[str, list[str], list[str]]:
    policy_status = policy_gate_decision[
        "policy_gate_status"
    ]

    if policy_status == "READY_FOR_READ_ONLY_RESPONSE":
        return "READ_ONLY_RESPONSE_PLANNED", [], []

    if policy_status == "OPERATOR_CONFIRMATION_REQUIRED":
        return (
            "OPERATOR_CONFIRMATION_PENDING",
            [],
            ["operator_confirmation_required"],
        )

    return (
        "BLOCKED",
        sorted(
            set(policy_gate_decision["blocking_reasons"])
        ),
        [],
    )


def build_fcf_api_gateway_response_envelope(
    *,
    response_id: str,
    request_envelope: Mapping[str, Any],
    policy_gate_decision: Mapping[str, Any],
    generated_at_utc: str,
) -> dict[str, Any]:
    """Build deterministic planning-only response metadata."""
    if not _valid_identifier(response_id):
        raise FcfApiGatewayResponseEnvelopeViolation(
            "response_id_invalid"
        )

    if not _valid_timestamp(generated_at_utc):
        raise FcfApiGatewayResponseEnvelopeViolation(
            "generated_at_utc_invalid"
        )

    request_errors = (
        validate_fcf_api_gateway_request_envelope(
            request_envelope
        )
    )
    if request_errors:
        raise FcfApiGatewayResponseEnvelopeViolation(
            "request:" + ";".join(request_errors)
        )

    decision_errors = (
        validate_fcf_api_gateway_policy_gate_decision(
            policy_gate_decision,
            request_envelope,
        )
    )
    if decision_errors:
        raise FcfApiGatewayResponseEnvelopeViolation(
            "policy_gate:" + ";".join(decision_errors)
        )

    status, errors, warnings = _derive_response_state(
        policy_gate_decision
    )

    return {
        "response_id": response_id,
        "stage_id": STAGE_ID,
        "response_envelope_version": (
            RESPONSE_ENVELOPE_VERSION
        ),
        "source_request_id": request_envelope["request_id"],
        "source_policy_decision_id": (
            policy_gate_decision["decision_id"]
        ),
        "correlation_id": request_envelope["correlation_id"],
        "source_artifact_ids": list(
            request_envelope["source_artifact_ids"]
        ),
        "status": status,
        "policy_decision": (
            policy_gate_decision["policy_gate_status"]
        ),
        "errors": errors,
        "warnings": warnings,
        "generated_at_utc": generated_at_utc,
        "operator_review_required": True,
        "operator_confirmation_required": (
            policy_gate_decision[
                "operator_confirmation_required"
            ]
        ),
        "response_transport_active": False,
        "automatic_routing_allowed": False,
        "runtime_activation_allowed": False,
        "model_invocation_allowed": False,
        "archive_writing_allowed": False,
    }


def validate_fcf_api_gateway_response_envelope(
    response: object,
    request_envelope: object,
    policy_gate_decision: object,
) -> list[str]:
    """Return deterministic D4 response-envelope errors."""
    if not isinstance(response, Mapping):
        return ["response_envelope_must_be_mapping"]

    if not isinstance(request_envelope, Mapping):
        return ["request_envelope_must_be_mapping"]

    if not isinstance(policy_gate_decision, Mapping):
        return ["policy_gate_decision_must_be_mapping"]

    request_errors = (
        validate_fcf_api_gateway_request_envelope(
            request_envelope
        )
    )
    if request_errors:
        return [
            f"source_request_{error}"
            for error in request_errors
        ]

    decision_errors = (
        validate_fcf_api_gateway_policy_gate_decision(
            policy_gate_decision,
            request_envelope,
        )
    )
    if decision_errors:
        return [
            f"source_policy_gate_{error}"
            for error in decision_errors
        ]

    errors: list[str] = []

    if set(response.keys()) != set(
        REQUIRED_RESPONSE_ENVELOPE_FIELDS
    ):
        errors.append(
            "response_envelope_fields_must_match_schema"
        )

    response_id = response.get("response_id")
    if not _valid_identifier(response_id):
        errors.append("response_id_invalid")
        response_id = "validation.response"

    generated_at_utc = response.get("generated_at_utc")
    if not _valid_timestamp(generated_at_utc):
        errors.append("generated_at_utc_invalid")
        generated_at_utc = "2000-01-01T00:00:00Z"

    expected = build_fcf_api_gateway_response_envelope(
        response_id=response_id,
        request_envelope=request_envelope,
        policy_gate_decision=policy_gate_decision,
        generated_at_utc=generated_at_utc,
    )

    for field in REQUIRED_RESPONSE_ENVELOPE_FIELDS:
        if field in ("response_id", "generated_at_utc"):
            continue

        if response.get(field) != expected[field]:
            errors.append(f"{field}_mismatch")

    if response.get("status") not in RESPONSE_STATUSES:
        errors.append("status_invalid")

    for field in (
        "response_transport_active",
        "automatic_routing_allowed",
        "runtime_activation_allowed",
        "model_invocation_allowed",
        "archive_writing_allowed",
    ):
        if response.get(field) is not False:
            errors.append(f"{field}_must_be_false")

    return errors
