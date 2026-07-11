"""D2 deterministic Operator Review production consumer binding."""

from __future__ import annotations

from copy import deepcopy
from typing import Any, Mapping

from apps.ai_comprehensive_report_integration_app_1 import (
    CLOSEOUT_PACKET_TYPE,
    validate_full_chain_closeout_packet,
)

from .d1_binding_contract import (
    APP_ID,
    REQUIRED_CONTENT_FIELDS,
    REQUIRED_IDENTITY_FIELDS,
    build_consumer_binding_contract,
    validate_consumer_binding_contract,
)

STAGE = "D2"
CONSUMER_APP_ID = "OPERATOR-REVIEW-APP-1"
BINDING_PACKET_TYPE = (
    "comprehensive_report_operator_review_consumer_binding_packet"
)


def _failure(errors: list[str]) -> dict[str, Any]:
    return {
        "app_id": APP_ID,
        "stage": STAGE,
        "ok": False,
        "errors": sorted(set(errors)),
        "packet": None,
        "operator_review_required": True,
        "automatic_approval_performed": False,
        "source_mutation_performed": False,
        "semantic_rewrite_performed": False,
        "runtime_execution_performed": False,
        "real_execution_performed": False,
    }


def build_operator_review_consumer_binding(
    closeout_packet: Mapping[str, Any],
    source_envelope: Mapping[str, Any],
) -> dict[str, Any]:
    """Bind a validated closeout packet to Operator Review."""

    contract = build_consumer_binding_contract()
    contract_validation = validate_consumer_binding_contract(contract)

    if not contract_validation["ok"]:
        return _failure(list(contract_validation["errors"]))

    closeout_validation = validate_full_chain_closeout_packet(
        closeout_packet,
        source_envelope,
    )

    if not closeout_validation["ok"]:
        return _failure(list(closeout_validation["errors"]))

    errors: list[str] = []

    if closeout_packet.get("packet_type") != CLOSEOUT_PACKET_TYPE:
        errors.append("INVALID_CLOSEOUT_PACKET_TYPE")

    review_packet = closeout_packet.get("operator_review_packet")

    if not isinstance(review_packet, Mapping):
        errors.append("MISSING_OPERATOR_REVIEW_PACKET")
        return _failure(errors)

    for field in REQUIRED_IDENTITY_FIELDS:
        if field not in closeout_packet:
            errors.append(f"MISSING_IDENTITY_FIELD_{field.upper()}")

    for field in REQUIRED_CONTENT_FIELDS:
        if field not in review_packet:
            errors.append(f"MISSING_REVIEW_CONTENT_{field.upper()}")

    if review_packet.get("operator_review_required") is not True:
        errors.append("OPERATOR_REVIEW_REQUIREMENT_REMOVED")

    if review_packet.get("operator_decision") != "PENDING":
        errors.append("INVALID_OPERATOR_DECISION")

    if errors:
        return _failure(errors)

    packet = {
        "packet_type": BINDING_PACKET_TYPE,
        "producer_app_id": APP_ID,
        "consumer_app_id": CONSUMER_APP_ID,
        "source_packet_type": closeout_packet["packet_type"],
        "source_app_id": closeout_packet["source_app_id"],
        "source_module": closeout_packet["source_module"],
        "source_artifact_type": closeout_packet[
            "source_artifact_type"
        ],
        "source_artifact_ref": closeout_packet[
            "source_artifact_ref"
        ],
        "source_artifact_version": closeout_packet[
            "source_artifact_version"
        ],
        "source_sha256": closeout_packet["source_sha256"],
        "correlation_id": closeout_packet["correlation_id"],
        "operator_review_packet": deepcopy(dict(review_packet)),
        "source_statements": deepcopy(
            review_packet["source_statements"]
        ),
        "original_conclusions": deepcopy(
            review_packet["original_conclusions"]
        ),
        "risk_flags": deepcopy(review_packet["risk_flags"]),
        "counterevidence": deepcopy(
            review_packet["counterevidence"]
        ),
        "alternative_explanations": deepcopy(
            review_packet["alternative_explanations"]
        ),
        "uncertainty_states": deepcopy(
            review_packet["uncertainty_states"]
        ),
        "review_status": "REVIEW_REQUIRED",
        "operator_decision": "PENDING",
        "binding_status": "BOUND_READ_ONLY",
        "operator_review_required": True,
        "registered_artifact_required": True,
        "automatic_approval_allowed": False,
        "source_mutation_allowed": False,
        "semantic_rewrite_allowed": False,
        "risk_suppression_allowed": False,
        "runtime_model_invocation_allowed": False,
        "prompt_execution_allowed": False,
        "automatic_routing_allowed": False,
        "real_execution_allowed": False,
    }

    return {
        "app_id": APP_ID,
        "stage": STAGE,
        "ok": True,
        "errors": [],
        "packet": packet,
        "operator_review_required": True,
        "automatic_approval_performed": False,
        "source_mutation_performed": False,
        "semantic_rewrite_performed": False,
        "runtime_execution_performed": False,
        "real_execution_performed": False,
    }


def validate_operator_review_consumer_binding(
    binding_packet: Mapping[str, Any],
    closeout_packet: Mapping[str, Any],
    source_envelope: Mapping[str, Any],
) -> dict[str, Any]:
    """Validate exact identity and review-content preservation."""

    errors: list[str] = []

    rebuilt = build_operator_review_consumer_binding(
        closeout_packet,
        source_envelope,
    )

    if not rebuilt["ok"]:
        return _failure(list(rebuilt["errors"]))

    expected = rebuilt["packet"]

    identity_fields = (
        "packet_type",
        "producer_app_id",
        "consumer_app_id",
        "source_packet_type",
        *REQUIRED_IDENTITY_FIELDS,
    )

    for field in identity_fields:
        if binding_packet.get(field) != expected.get(field):
            errors.append(f"IDENTITY_MISMATCH_{field.upper()}")

    preserved_fields = (
        "operator_review_packet",
        *REQUIRED_CONTENT_FIELDS,
    )

    for field in preserved_fields:
        if binding_packet.get(field) != expected.get(field):
            errors.append(f"CONTENT_MISMATCH_{field.upper()}")

    expected_states = {
        "review_status": "REVIEW_REQUIRED",
        "operator_decision": "PENDING",
        "binding_status": "BOUND_READ_ONLY",
        "operator_review_required": True,
        "registered_artifact_required": True,
    }

    for field, expected_value in expected_states.items():
        if binding_packet.get(field) != expected_value:
            errors.append(f"INVALID_{field.upper()}")

    false_fields = (
        "automatic_approval_allowed",
        "source_mutation_allowed",
        "semantic_rewrite_allowed",
        "risk_suppression_allowed",
        "runtime_model_invocation_allowed",
        "prompt_execution_allowed",
        "automatic_routing_allowed",
        "real_execution_allowed",
    )

    for field in false_fields:
        if binding_packet.get(field) is not False:
            errors.append(f"UNSAFE_{field.upper()}")

    return {
        "app_id": APP_ID,
        "stage": STAGE,
        "ok": not errors,
        "errors": sorted(set(errors)),
        "operator_review_required": True,
        "automatic_approval_performed": False,
        "source_mutation_performed": False,
        "semantic_rewrite_performed": False,
        "runtime_execution_performed": False,
        "real_execution_performed": False,
    }
