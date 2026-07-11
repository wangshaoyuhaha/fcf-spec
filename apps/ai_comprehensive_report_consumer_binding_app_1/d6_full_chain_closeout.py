"""D6 deterministic full-chain validation and phase closeout."""

from __future__ import annotations

from copy import deepcopy
from typing import Any, Mapping

from apps.ai_comprehensive_report_integration_app_1 import (
    build_full_chain_closeout_packet,
    validate_full_chain_closeout_packet,
)

from .d1_binding_contract import (
    APP_ID,
    REQUIRED_IDENTITY_FIELDS,
)
from .d5_cross_consumer_consistency import (
    CHECKED_CONSUMERS,
    CONSISTENCY_PACKET_TYPE,
    build_cross_consumer_binding_bundle,
    validate_cross_consumer_binding_bundle,
)

STAGE = "D6"
CLOSEOUT_PACKET_TYPE = (
    "comprehensive_report_consumer_binding_full_chain_closeout_packet"
)

COMPLETED_STAGES = (
    "D1_BINDING_CONTRACT",
    "D2_OPERATOR_REVIEW_BINDING",
    "D3_UI_BINDING",
    "D4_REPORT_ARCHIVE_BINDING",
    "D5_CROSS_CONSUMER_CONSISTENCY",
    "D6_FULL_CHAIN_CLOSEOUT",
)


def _failure(errors: list[str]) -> dict[str, Any]:
    return {
        "app_id": APP_ID,
        "stage": STAGE,
        "ok": False,
        "errors": sorted(set(errors)),
        "packet": None,
        "closeout_status": "BLOCKED",
        "operator_review_required": True,
        "manual_archive_required": True,
        "automatic_approval_performed": False,
        "automatic_archive_performed": False,
        "archive_write_performed": False,
        "archive_record_created": False,
        "source_mutation_performed": False,
        "semantic_rewrite_performed": False,
        "visibility_suppression_performed": False,
        "runtime_execution_performed": False,
        "real_execution_performed": False,
    }


def _prefixed_errors(
    prefix: str,
    errors: object,
) -> list[str]:
    if not isinstance(errors, list):
        return [f"{prefix}_INVALID_ERRORS"]

    return [
        f"{prefix}_{str(error)}"
        for error in errors
    ]


def build_consumer_binding_full_chain_closeout(
    source_envelope: Mapping[str, Any],
) -> dict[str, Any]:
    """Build the final deterministic consumer-binding closeout."""

    integration_result = build_full_chain_closeout_packet(
        source_envelope
    )

    if not integration_result["ok"]:
        return _failure(
            _prefixed_errors(
                "INTEGRATION_BUILD",
                integration_result["errors"],
            )
        )

    integration_packet = integration_result["packet"]

    integration_validation = validate_full_chain_closeout_packet(
        integration_packet,
        source_envelope,
    )

    if not integration_validation["ok"]:
        return _failure(
            _prefixed_errors(
                "INTEGRATION_VALIDATE",
                integration_validation["errors"],
            )
        )

    bundle_result = build_cross_consumer_binding_bundle(
        integration_packet,
        source_envelope,
    )

    if not bundle_result["ok"]:
        return _failure(
            _prefixed_errors(
                "CONSUMER_BUNDLE_BUILD",
                bundle_result["errors"],
            )
        )

    bundle_packet = bundle_result["packet"]

    bundle_validation = validate_cross_consumer_binding_bundle(
        bundle_packet,
        integration_packet,
        source_envelope,
    )

    if not bundle_validation["ok"]:
        return _failure(
            _prefixed_errors(
                "CONSUMER_BUNDLE_VALIDATE",
                bundle_validation["errors"],
            )
        )

    identity = {
        field: deepcopy(integration_packet[field])
        for field in REQUIRED_IDENTITY_FIELDS
    }

    validation_summary = {
        "integration_closeout_valid": True,
        "operator_review_binding_valid": True,
        "ui_binding_valid": True,
        "report_archive_binding_valid": True,
        "cross_consumer_consistency_valid": True,
        "identity_consistent": True,
        "source_sha256_consistent": True,
        "correlation_id_consistent": True,
        "risk_flags_preserved": True,
        "counterevidence_preserved": True,
        "alternative_explanations_preserved": True,
        "uncertainty_states_preserved": True,
        "operator_decision_pending": True,
        "archive_decision_pending": True,
        "automatic_approval_blocked": True,
        "automatic_archive_blocked": True,
        "archive_write_blocked": True,
        "runtime_execution_blocked": True,
        "real_execution_blocked": True,
    }

    packet = {
        "packet_type": CLOSEOUT_PACKET_TYPE,
        "producer_app_id": APP_ID,
        "phase_id": APP_ID,
        "stage": STAGE,
        "source_integration_packet_type": integration_packet[
            "packet_type"
        ],
        "source_consistency_packet_type": CONSISTENCY_PACKET_TYPE,
        "completed_stages": list(COMPLETED_STAGES),
        "completed_consumers": list(CHECKED_CONSUMERS),
        "identity": identity,
        "integration_closeout_packet": deepcopy(
            integration_packet
        ),
        "cross_consumer_bundle": deepcopy(bundle_packet),
        "validation_summary": validation_summary,
        "closeout_status": "COMPLETE_VALIDATED",
        "consistency_status": "CONSISTENT",
        "operator_review_status": "REVIEW_REQUIRED",
        "operator_decision": "PENDING",
        "archive_status": "PENDING_MANUAL_ARCHIVE",
        "operator_archive_decision": "PENDING",
        "binding_status": "BOUND_READ_ONLY",
        "operator_review_required": True,
        "manual_archive_required": True,
        "registered_artifact_required": True,
        "phase_ready_for_final_current_state": True,
        "automatic_approval_allowed": False,
        "automatic_archive_allowed": False,
        "archive_execution_allowed": False,
        "archive_write_allowed": False,
        "archive_record_creation_allowed": False,
        "source_mutation_allowed": False,
        "semantic_rewrite_allowed": False,
        "visibility_suppression_allowed": False,
        "runtime_model_invocation_allowed": False,
        "prompt_execution_allowed": False,
        "automatic_routing_allowed": False,
        "real_execution_allowed": False,
        "tag_allowed": False,
        "release_allowed": False,
        "deployment_allowed": False,
    }

    return {
        "app_id": APP_ID,
        "stage": STAGE,
        "ok": True,
        "errors": [],
        "packet": packet,
        "closeout_status": "COMPLETE_VALIDATED",
        "operator_review_required": True,
        "manual_archive_required": True,
        "automatic_approval_performed": False,
        "automatic_archive_performed": False,
        "archive_write_performed": False,
        "archive_record_created": False,
        "source_mutation_performed": False,
        "semantic_rewrite_performed": False,
        "visibility_suppression_performed": False,
        "runtime_execution_performed": False,
        "real_execution_performed": False,
    }


def validate_consumer_binding_full_chain_closeout(
    closeout_packet: Mapping[str, Any],
    source_envelope: Mapping[str, Any],
) -> dict[str, Any]:
    """Validate the complete D1-D6 consumer binding chain."""

    errors: list[str] = []

    if closeout_packet.get("packet_type") != CLOSEOUT_PACKET_TYPE:
        errors.append("INVALID_CLOSEOUT_PACKET_TYPE")

    if closeout_packet.get("producer_app_id") != APP_ID:
        errors.append("INVALID_PRODUCER_APP_ID")

    if closeout_packet.get("phase_id") != APP_ID:
        errors.append("INVALID_PHASE_ID")

    if closeout_packet.get("stage") != STAGE:
        errors.append("INVALID_STAGE")

    if tuple(
        closeout_packet.get("completed_stages") or ()
    ) != COMPLETED_STAGES:
        errors.append("INVALID_COMPLETED_STAGES")

    if tuple(
        closeout_packet.get("completed_consumers") or ()
    ) != CHECKED_CONSUMERS:
        errors.append("INVALID_COMPLETED_CONSUMERS")

    integration_packet = closeout_packet.get(
        "integration_closeout_packet"
    )
    bundle_packet = closeout_packet.get(
        "cross_consumer_bundle"
    )

    if not isinstance(integration_packet, Mapping):
        errors.append("MISSING_INTEGRATION_CLOSEOUT_PACKET")

    if not isinstance(bundle_packet, Mapping):
        errors.append("MISSING_CROSS_CONSUMER_BUNDLE")

    if errors:
        return _failure(errors)

    integration_validation = validate_full_chain_closeout_packet(
        integration_packet,
        source_envelope,
    )

    if not integration_validation["ok"]:
        errors.extend(
            _prefixed_errors(
                "INTEGRATION",
                integration_validation["errors"],
            )
        )

    bundle_validation = validate_cross_consumer_binding_bundle(
        bundle_packet,
        integration_packet,
        source_envelope,
    )

    if not bundle_validation["ok"]:
        errors.extend(
            _prefixed_errors(
                "BUNDLE",
                bundle_validation["errors"],
            )
        )

    identity = closeout_packet.get("identity")

    if not isinstance(identity, Mapping):
        errors.append("MISSING_IDENTITY")
    else:
        for field in REQUIRED_IDENTITY_FIELDS:
            if identity.get(field) != integration_packet.get(field):
                errors.append(
                    f"IDENTITY_MISMATCH_{field.upper()}"
                )

    expected_states = {
        "closeout_status": "COMPLETE_VALIDATED",
        "consistency_status": "CONSISTENT",
        "operator_review_status": "REVIEW_REQUIRED",
        "operator_decision": "PENDING",
        "archive_status": "PENDING_MANUAL_ARCHIVE",
        "operator_archive_decision": "PENDING",
        "binding_status": "BOUND_READ_ONLY",
        "operator_review_required": True,
        "manual_archive_required": True,
        "registered_artifact_required": True,
        "phase_ready_for_final_current_state": True,
    }

    for field, expected_value in expected_states.items():
        if closeout_packet.get(field) != expected_value:
            errors.append(f"INVALID_{field.upper()}")

    false_fields = (
        "automatic_approval_allowed",
        "automatic_archive_allowed",
        "archive_execution_allowed",
        "archive_write_allowed",
        "archive_record_creation_allowed",
        "source_mutation_allowed",
        "semantic_rewrite_allowed",
        "visibility_suppression_allowed",
        "runtime_model_invocation_allowed",
        "prompt_execution_allowed",
        "automatic_routing_allowed",
        "real_execution_allowed",
        "tag_allowed",
        "release_allowed",
        "deployment_allowed",
    )

    for field in false_fields:
        if closeout_packet.get(field) is not False:
            errors.append(f"UNSAFE_{field.upper()}")

    expected_result = build_consumer_binding_full_chain_closeout(
        source_envelope
    )

    if not expected_result["ok"]:
        errors.extend(
            _prefixed_errors(
                "EXPECTED_BUILD",
                expected_result["errors"],
            )
        )
    else:
        expected = expected_result["packet"]

        for field in (
            "source_integration_packet_type",
            "source_consistency_packet_type",
            "completed_stages",
            "completed_consumers",
            "identity",
            "integration_closeout_packet",
            "cross_consumer_bundle",
            "validation_summary",
        ):
            if closeout_packet.get(field) != expected.get(field):
                errors.append(f"CLOSEOUT_MISMATCH_{field.upper()}")

    return {
        "app_id": APP_ID,
        "stage": STAGE,
        "ok": not errors,
        "errors": sorted(set(errors)),
        "closeout_status": (
            "COMPLETE_VALIDATED"
            if not errors
            else "BLOCKED"
        ),
        "operator_review_required": True,
        "manual_archive_required": True,
        "automatic_approval_performed": False,
        "automatic_archive_performed": False,
        "archive_write_performed": False,
        "archive_record_created": False,
        "source_mutation_performed": False,
        "semantic_rewrite_performed": False,
        "visibility_suppression_performed": False,
        "runtime_execution_performed": False,
        "real_execution_performed": False,
    }
