"""D4 deterministic Report Archive production consumer binding."""

from __future__ import annotations

from copy import deepcopy
from typing import Any, Mapping

from apps.ai_comprehensive_report_integration_app_1 import (
    CLOSEOUT_PACKET_TYPE,
    validate_full_chain_closeout_packet,
)

from .d1_binding_contract import (
    APP_ID,
    REQUIRED_IDENTITY_FIELDS,
    build_consumer_binding_contract,
    validate_consumer_binding_contract,
)

STAGE = "D4"
ARCHIVE_CONSUMER_APP_ID = "REPORT-ARCHIVE-APP-1"
ARCHIVE_BINDING_PACKET_TYPE = (
    "comprehensive_report_archive_consumer_binding_packet"
)

REQUIRED_ARCHIVE_FIELDS = (
    "review_banner",
    "decision_state",
    "sections",
    "visibility_counts",
    "visibility_order",
    "risk_flags",
    "counterevidence",
    "alternative_explanations",
    "uncertainty_states",
    "manual_archive_checklist",
)


def _failure(errors: list[str]) -> dict[str, Any]:
    return {
        "app_id": APP_ID,
        "stage": STAGE,
        "ok": False,
        "errors": sorted(set(errors)),
        "packet": None,
        "operator_review_required": True,
        "manual_archive_required": True,
        "automatic_archive_performed": False,
        "archive_write_performed": False,
        "archive_record_created": False,
        "source_mutation_performed": False,
        "semantic_rewrite_performed": False,
        "runtime_execution_performed": False,
        "real_execution_performed": False,
    }


def build_report_archive_consumer_binding(
    closeout_packet: Mapping[str, Any],
    source_envelope: Mapping[str, Any],
) -> dict[str, Any]:
    """Bind the validated closeout packet to Report Archive."""

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

    archive_packet = closeout_packet.get(
        "manual_archive_candidate_packet"
    )

    if not isinstance(archive_packet, Mapping):
        errors.append("MISSING_MANUAL_ARCHIVE_CANDIDATE_PACKET")
        return _failure(errors)

    for field in REQUIRED_IDENTITY_FIELDS:
        if field not in closeout_packet:
            errors.append(f"MISSING_IDENTITY_FIELD_{field.upper()}")

    for field in REQUIRED_ARCHIVE_FIELDS:
        if field not in archive_packet:
            errors.append(f"MISSING_ARCHIVE_FIELD_{field.upper()}")

    expected_states = {
        "archive_status": "PENDING_MANUAL_ARCHIVE",
        "archive_handoff_state": (
            "AWAITING_OPERATOR_ARCHIVE_AUTHORIZATION"
        ),
        "operator_archive_decision": "PENDING",
        "archive_destination": "UNASSIGNED",
        "retention_label": "UNASSIGNED",
        "archive_record_id": "UNASSIGNED",
        "operator_review_required": True,
        "manual_archive_required": True,
    }

    for field, expected in expected_states.items():
        if archive_packet.get(field) != expected:
            errors.append(f"INVALID_ARCHIVE_STATE_{field.upper()}")

    false_fields = (
        "automatic_archive_allowed",
        "archive_execution_allowed",
        "archive_write_allowed",
        "archive_record_creation_allowed",
        "source_mutation_allowed",
        "semantic_rewrite_allowed",
        "visibility_suppression_allowed",
        "runtime_execution_allowed",
        "real_execution_allowed",
    )

    for field in false_fields:
        if archive_packet.get(field) is not False:
            errors.append(f"UNSAFE_ARCHIVE_SOURCE_{field.upper()}")

    checklist = archive_packet.get("manual_archive_checklist")

    if not isinstance(checklist, list):
        errors.append("INVALID_MANUAL_ARCHIVE_CHECKLIST")
    else:
        for item in checklist:
            if not isinstance(item, Mapping):
                errors.append("INVALID_ARCHIVE_CHECKLIST_ITEM")
                continue

            if item.get("status") != "PENDING":
                errors.append("INVALID_ARCHIVE_CHECKLIST_STATUS")

            if item.get("operator_action_required") is not True:
                errors.append(
                    "ARCHIVE_OPERATOR_REQUIREMENT_REMOVED"
                )

            if item.get("automatic_completion_allowed") is not False:
                errors.append(
                    "ARCHIVE_AUTO_COMPLETION_ENABLED"
                )

    if errors:
        return _failure(errors)

    packet = {
        "packet_type": ARCHIVE_BINDING_PACKET_TYPE,
        "producer_app_id": APP_ID,
        "consumer_app_id": ARCHIVE_CONSUMER_APP_ID,
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
        "manual_archive_candidate_packet": deepcopy(
            dict(archive_packet)
        ),
        "review_banner": deepcopy(archive_packet["review_banner"]),
        "decision_state": deepcopy(archive_packet["decision_state"]),
        "sections": deepcopy(archive_packet["sections"]),
        "visibility_counts": deepcopy(
            archive_packet["visibility_counts"]
        ),
        "visibility_order": deepcopy(
            archive_packet["visibility_order"]
        ),
        "risk_flags": deepcopy(archive_packet["risk_flags"]),
        "counterevidence": deepcopy(
            archive_packet["counterevidence"]
        ),
        "alternative_explanations": deepcopy(
            archive_packet["alternative_explanations"]
        ),
        "uncertainty_states": deepcopy(
            archive_packet["uncertainty_states"]
        ),
        "manual_archive_checklist": deepcopy(
            archive_packet["manual_archive_checklist"]
        ),
        "archive_status": "PENDING_MANUAL_ARCHIVE",
        "archive_handoff_state": (
            "AWAITING_OPERATOR_ARCHIVE_AUTHORIZATION"
        ),
        "operator_archive_decision": "PENDING",
        "archive_destination": "UNASSIGNED",
        "retention_label": "UNASSIGNED",
        "archive_record_id": "UNASSIGNED",
        "binding_status": "BOUND_READ_ONLY",
        "operator_review_required": True,
        "manual_archive_required": True,
        "registered_artifact_required": True,
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
    }

    return {
        "app_id": APP_ID,
        "stage": STAGE,
        "ok": True,
        "errors": [],
        "packet": packet,
        "operator_review_required": True,
        "manual_archive_required": True,
        "automatic_archive_performed": False,
        "archive_write_performed": False,
        "archive_record_created": False,
        "source_mutation_performed": False,
        "semantic_rewrite_performed": False,
        "runtime_execution_performed": False,
        "real_execution_performed": False,
    }


def validate_report_archive_consumer_binding(
    binding_packet: Mapping[str, Any],
    closeout_packet: Mapping[str, Any],
    source_envelope: Mapping[str, Any],
) -> dict[str, Any]:
    """Validate exact archive identity and content preservation."""

    errors: list[str] = []

    rebuilt = build_report_archive_consumer_binding(
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
        "manual_archive_candidate_packet",
        *REQUIRED_ARCHIVE_FIELDS,
    )

    for field in preserved_fields:
        if binding_packet.get(field) != expected.get(field):
            errors.append(f"ARCHIVE_CONTENT_MISMATCH_{field.upper()}")

    expected_states = {
        "archive_status": "PENDING_MANUAL_ARCHIVE",
        "archive_handoff_state": (
            "AWAITING_OPERATOR_ARCHIVE_AUTHORIZATION"
        ),
        "operator_archive_decision": "PENDING",
        "archive_destination": "UNASSIGNED",
        "retention_label": "UNASSIGNED",
        "archive_record_id": "UNASSIGNED",
        "binding_status": "BOUND_READ_ONLY",
        "operator_review_required": True,
        "manual_archive_required": True,
        "registered_artifact_required": True,
    }

    for field, expected_value in expected_states.items():
        if binding_packet.get(field) != expected_value:
            errors.append(f"INVALID_{field.upper()}")

    false_fields = (
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
    )

    for field in false_fields:
        if binding_packet.get(field) is not False:
            errors.append(f"UNSAFE_{field.upper()}")

    checklist = binding_packet.get("manual_archive_checklist")

    if not isinstance(checklist, list):
        errors.append("INVALID_BOUND_ARCHIVE_CHECKLIST")
    else:
        for item in checklist:
            if not isinstance(item, Mapping):
                errors.append("INVALID_BOUND_CHECKLIST_ITEM")
                continue

            if item.get("status") != "PENDING":
                errors.append("INVALID_BOUND_CHECKLIST_STATUS")

            if item.get("operator_action_required") is not True:
                errors.append(
                    "BOUND_OPERATOR_REQUIREMENT_REMOVED"
                )

            if item.get("automatic_completion_allowed") is not False:
                errors.append(
                    "BOUND_AUTO_COMPLETION_ENABLED"
                )

    return {
        "app_id": APP_ID,
        "stage": STAGE,
        "ok": not errors,
        "errors": sorted(set(errors)),
        "operator_review_required": True,
        "manual_archive_required": True,
        "automatic_archive_performed": False,
        "archive_write_performed": False,
        "archive_record_created": False,
        "source_mutation_performed": False,
        "semantic_rewrite_performed": False,
        "runtime_execution_performed": False,
        "real_execution_performed": False,
    }
