"""Deterministic policy gate for FCF API Gateway planning."""

import re
from collections.abc import Mapping
from typing import Any

from .request_envelope import (
    validate_fcf_api_gateway_request_envelope,
)

STAGE_ID = "FCF-API-GATEWAY-PLANNING-D3"
POLICY_GATE_VERSION = "1.0.0"

READ_ONLY_REQUEST_CLASSES = (
    "ARTIFACT_METADATA_READ",
    "EVIDENCE_REFERENCE_READ",
    "HEALTH_STATUS_READ",
    "POLICY_STATUS_READ",
    "RESEARCH_WORKFLOW_STATUS_READ",
)

OPERATOR_CONTROL_REQUEST_CLASSES = (
    "OPERATOR_REVIEW_REQUEST",
    "REANALYSIS_REQUEST",
    "STOP_WORKFLOW_REQUEST",
)

POLICY_GATE_STATUSES = (
    "READY_FOR_READ_ONLY_RESPONSE",
    "OPERATOR_CONFIRMATION_REQUIRED",
    "BLOCKED",
)

REQUIRED_POLICY_GATE_FIELDS = (
    "decision_id",
    "stage_id",
    "policy_gate_version",
    "source_request_id",
    "source_contract_id",
    "correlation_id",
    "request_class",
    "policy_version",
    "config_snapshot_id",
    "policy_gate_status",
    "operator_confirmation_required",
    "automatic_routing_allowed",
    "runtime_activation_allowed",
    "blocking_reasons",
    "operator_review_status",
)

_IDENTIFIER_PATTERN = re.compile(
    r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$"
)


class FcfApiGatewayPolicyGateViolation(ValueError):
    """Raised when a D3 policy gate cannot be built."""


def _valid_identifier(value: Any) -> bool:
    return (
        isinstance(value, str)
        and _IDENTIFIER_PATTERN.fullmatch(value) is not None
    )


def _derive_policy_gate(
    request_envelope: Mapping[str, Any],
) -> tuple[str, bool, list[str]]:
    request_status = request_envelope["request_status"]
    request_class = request_envelope["request_class"]

    if request_status == "BLOCKED":
        reasons = list(
            request_envelope["blocking_reasons"]
        )
        return "BLOCKED", True, sorted(set(reasons))

    if request_class in READ_ONLY_REQUEST_CLASSES:
        return "READY_FOR_READ_ONLY_RESPONSE", False, []

    if request_class in OPERATOR_CONTROL_REQUEST_CLASSES:
        return "OPERATOR_CONFIRMATION_REQUIRED", True, []

    return (
        "BLOCKED",
        True,
        ["request_class_not_policy_registered"],
    )


def build_fcf_api_gateway_policy_gate_decision(
    *,
    decision_id: str,
    request_envelope: Mapping[str, Any],
) -> dict[str, Any]:
    """Build a deterministic planning-only policy gate decision."""
    if not _valid_identifier(decision_id):
        raise FcfApiGatewayPolicyGateViolation(
            "decision_id_invalid"
        )

    request_errors = (
        validate_fcf_api_gateway_request_envelope(
            request_envelope
        )
    )
    if request_errors:
        raise FcfApiGatewayPolicyGateViolation(
            ";".join(request_errors)
        )

    (
        policy_gate_status,
        operator_confirmation_required,
        blocking_reasons,
    ) = _derive_policy_gate(request_envelope)

    return {
        "decision_id": decision_id,
        "stage_id": STAGE_ID,
        "policy_gate_version": POLICY_GATE_VERSION,
        "source_request_id": request_envelope["request_id"],
        "source_contract_id": (
            request_envelope["source_contract_id"]
        ),
        "correlation_id": request_envelope["correlation_id"],
        "request_class": request_envelope["request_class"],
        "policy_version": request_envelope["policy_version"],
        "config_snapshot_id": (
            request_envelope["config_snapshot_id"]
        ),
        "policy_gate_status": policy_gate_status,
        "operator_confirmation_required": (
            operator_confirmation_required
        ),
        "automatic_routing_allowed": False,
        "runtime_activation_allowed": False,
        "blocking_reasons": blocking_reasons,
        "operator_review_status": "REVIEW_REQUIRED",
    }


def validate_fcf_api_gateway_policy_gate_decision(
    decision: object,
    request_envelope: object,
) -> list[str]:
    """Return deterministic D3 policy-gate errors."""
    if not isinstance(decision, Mapping):
        return ["decision_must_be_mapping"]

    if not isinstance(request_envelope, Mapping):
        return ["request_envelope_must_be_mapping"]

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

    errors: list[str] = []

    if set(decision.keys()) != set(
        REQUIRED_POLICY_GATE_FIELDS
    ):
        errors.append(
            "decision_fields_must_match_schema"
        )

    decision_id = decision.get("decision_id")
    if not _valid_identifier(decision_id):
        errors.append("decision_id_invalid")
        decision_id = "validation.decision"

    expected = (
        build_fcf_api_gateway_policy_gate_decision(
            decision_id=decision_id,
            request_envelope=request_envelope,
        )
    )

    for field in (
        "stage_id",
        "policy_gate_version",
        "source_request_id",
        "source_contract_id",
        "correlation_id",
        "request_class",
        "policy_version",
        "config_snapshot_id",
        "operator_review_status",
    ):
        if decision.get(field) != expected[field]:
            errors.append(f"{field}_invalid")

    if decision.get("policy_gate_status") != (
        expected["policy_gate_status"]
    ):
        errors.append("policy_gate_status_mismatch")

    if decision.get(
        "operator_confirmation_required"
    ) is not expected["operator_confirmation_required"]:
        errors.append(
            "operator_confirmation_requirement_mismatch"
        )

    if decision.get("automatic_routing_allowed") is not False:
        errors.append(
            "automatic_routing_allowed_must_be_false"
        )

    if decision.get("runtime_activation_allowed") is not False:
        errors.append(
            "runtime_activation_allowed_must_be_false"
        )

    if decision.get("blocking_reasons") != (
        expected["blocking_reasons"]
    ):
        errors.append("blocking_reasons_mismatch")

    if decision.get("policy_gate_status") not in (
        POLICY_GATE_STATUSES
    ):
        errors.append("policy_gate_status_invalid")

    return errors
