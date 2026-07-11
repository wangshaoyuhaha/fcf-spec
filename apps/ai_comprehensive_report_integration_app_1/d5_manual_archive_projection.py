"""D5 deterministic manual-only report archive projection."""

from __future__ import annotations

from copy import deepcopy
from typing import Any, Mapping

from .d1_boundary_contract import APP_ID
from .d4_ui_visibility_projection import (
    UI_PACKET_TYPE,
    validate_ui_visibility_packet,
)

STAGE = "D5"
ARCHIVE_CONSUMER_APP_ID = "REPORT-ARCHIVE-APP-1"
ARCHIVE_PACKET_TYPE = (
    "comprehensive_report_manual_archive_candidate_packet"
)

PRESERVED_ARCHIVE_FIELDS = (
    "review_banner",
    "decision_state",
    "sections",
    "visibility_counts",
    "visibility_order",
    "risk_flags",
    "counterevidence",
    "alternative_explanations",
    "uncertainty_states",
)

ARCHIVE_CHECKLIST_IDS = (
    "VERIFY_SOURCE_CHAIN",
    "VERIFY_REVIEW_STATUS",
    "VERIFY_VISIBLE_RISK_CONTENT",
    "ASSIGN_ARCHIVE_DESTINATION",
    "ASSIGN_RETENTION_LABEL",
    "RECORD_OPERATOR_AUTHORIZATION",
    "RECORD_ARCHIVE_DECISION",
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
        "archive_execution_performed": False,
        "archive_write_performed": False,
        "archive_record_created": False,
        "source_mutation_performed": False,
        "semantic_rewrite_performed": False,
        "visibility_suppression_performed": False,
        "runtime_execution_performed": False,
        "real_execution_performed": False,
    }


def _manual_archive_checklist() -> list[dict[str, Any]]:
    return [
        {
            "check_id": check_id,
            "status": "PENDING",
            "operator_action_required": True,
            "automatic_completion_allowed": False,
        }
        for check_id in ARCHIVE_CHECKLIST_IDS
    ]


def build_manual_archive_candidate_packet(
    ui_packet: Mapping[str, Any],
    review_packet: Mapping[str, Any],
    source_envelope: Mapping[str, Any],
) -> dict[str, Any]:
    """Build a non-executing manual archive candidate packet."""

    ui_validation = validate_ui_visibility_packet(
        ui_packet,
        review_packet,
        source_envelope,
    )

    if not ui_validation["ok"]:
        return _failure(list(ui_validation["errors"]))

    errors: list[str] = []

    if ui_packet.get("packet_type") != UI_PACKET_TYPE:
        errors.append("INVALID_UI_PACKET_TYPE")

    if ui_packet.get("operator_review_required") is not True:
        errors.append("OPERATOR_REVIEW_REQUIREMENT_REMOVED")

    review_banner = ui_packet.get("review_banner")

    if not isinstance(review_banner, Mapping):
        errors.append("INVALID_REVIEW_BANNER")
    else:
        if review_banner.get("review_status") != "REVIEW_REQUIRED":
            errors.append("INVALID_REVIEW_STATUS")

        if review_banner.get("operator_decision") != "PENDING":
            errors.append("INVALID_OPERATOR_DECISION")

        if review_banner.get("operator_review_required") is not True:
            errors.append("REVIEW_BANNER_REQUIREMENT_REMOVED")

    decision_state = ui_packet.get("decision_state")

    if not isinstance(decision_state, Mapping):
        errors.append("INVALID_DECISION_STATE")
    else:
        if decision_state.get("causal_truth") != "UNDETERMINED":
            errors.append("INVALID_CAUSAL_TRUTH")

        if decision_state.get("probability") != "NOT_ASSIGNED":
            errors.append("INVALID_PROBABILITY")

        if decision_state.get("winner") != "NOT_SELECTED":
            errors.append("INVALID_WINNER")

        if decision_state.get("operator_decision") != "PENDING":
            errors.append("INVALID_DECISION_OPERATOR_STATUS")

    for field in PRESERVED_ARCHIVE_FIELDS:
        if field not in ui_packet:
            errors.append(f"MISSING_UI_FIELD_{field.upper()}")

    if errors:
        return _failure(errors)

    packet = {
        "packet_type": ARCHIVE_PACKET_TYPE,
        "producer_app_id": APP_ID,
        "consumer_app_id": ARCHIVE_CONSUMER_APP_ID,
        "source_ui_packet_type": ui_packet["packet_type"],
        "source_review_packet_type": ui_packet[
            "source_review_packet_type"
        ],
        "source_app_id": ui_packet["source_app_id"],
        "source_module": ui_packet["source_module"],
        "source_artifact_type": ui_packet[
            "source_artifact_type"
        ],
        "source_artifact_ref": ui_packet[
            "source_artifact_ref"
        ],
        "source_artifact_version": ui_packet[
            "source_artifact_version"
        ],
        "source_sha256": ui_packet["source_sha256"],
        "correlation_id": ui_packet["correlation_id"],
        "archive_status": "PENDING_MANUAL_ARCHIVE",
        "archive_handoff_state": (
            "AWAITING_OPERATOR_ARCHIVE_AUTHORIZATION"
        ),
        "operator_archive_decision": "PENDING",
        "archive_destination": "UNASSIGNED",
        "retention_label": "UNASSIGNED",
        "archive_record_id": "UNASSIGNED",
        "review_banner": deepcopy(ui_packet["review_banner"]),
        "decision_state": deepcopy(ui_packet["decision_state"]),
        "sections": deepcopy(ui_packet["sections"]),
        "visibility_counts": deepcopy(
            ui_packet["visibility_counts"]
        ),
        "visibility_order": deepcopy(
            ui_packet["visibility_order"]
        ),
        "risk_flags": deepcopy(ui_packet["risk_flags"]),
        "counterevidence": deepcopy(ui_packet["counterevidence"]),
        "alternative_explanations": deepcopy(
            ui_packet["alternative_explanations"]
        ),
        "uncertainty_states": deepcopy(
            ui_packet["uncertainty_states"]
        ),
        "manual_archive_checklist": _manual_archive_checklist(),
        "operator_review_required": True,
        "manual_archive_required": True,
        "automatic_archive_allowed": False,
        "archive_execution_allowed": False,
        "archive_write_allowed": False,
        "archive_record_creation_allowed": False,
        "source_mutation_allowed": False,
        "semantic_rewrite_allowed": False,
        "visibility_suppression_allowed": False,
        "runtime_execution_allowed": False,
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
        "archive_execution_performed": False,
        "archive_write_performed": False,
        "archive_record_created": False,
        "source_mutation_performed": False,
        "semantic_rewrite_performed": False,
        "visibility_suppression_performed": False,
        "runtime_execution_performed": False,
        "real_execution_performed": False,
    }


def validate_manual_archive_candidate_packet(
    archive_packet: Mapping[str, Any],
    ui_packet: Mapping[str, Any],
    review_packet: Mapping[str, Any],
    source_envelope: Mapping[str, Any],
) -> dict[str, Any]:
    """Validate the manual-only archive candidate boundary."""

    errors: list[str] = []

    ui_validation = validate_ui_visibility_packet(
        ui_packet,
        review_packet,
        source_envelope,
    )

    if not ui_validation["ok"]:
        errors.extend(ui_validation["errors"])

    identity_fields = {
        "packet_type": ARCHIVE_PACKET_TYPE,
        "producer_app_id": APP_ID,
        "consumer_app_id": ARCHIVE_CONSUMER_APP_ID,
        "source_ui_packet_type": ui_packet.get("packet_type"),
        "source_review_packet_type": ui_packet.get(
            "source_review_packet_type"
        ),
        "source_app_id": ui_packet.get("source_app_id"),
        "source_module": ui_packet.get("source_module"),
        "source_artifact_type": ui_packet.get(
            "source_artifact_type"
        ),
        "source_artifact_ref": ui_packet.get(
            "source_artifact_ref"
        ),
        "source_artifact_version": ui_packet.get(
            "source_artifact_version"
        ),
        "source_sha256": ui_packet.get("source_sha256"),
        "correlation_id": ui_packet.get("correlation_id"),
    }

    for field, expected in identity_fields.items():
        if archive_packet.get(field) != expected:
            errors.append(f"IDENTITY_MISMATCH_{field.upper()}")

    for field in PRESERVED_ARCHIVE_FIELDS:
        if archive_packet.get(field) != ui_packet.get(field):
            errors.append(
                f"ARCHIVE_PRESERVATION_MISMATCH_{field.upper()}"
            )

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
            errors.append(f"INVALID_{field.upper()}")

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
            errors.append(f"UNSAFE_{field.upper()}")

    checklist = archive_packet.get("manual_archive_checklist")

    if not isinstance(checklist, list):
        errors.append("INVALID_MANUAL_ARCHIVE_CHECKLIST")
    else:
        checklist_ids = tuple(
            item.get("check_id")
            for item in checklist
            if isinstance(item, Mapping)
        )

        if checklist_ids != ARCHIVE_CHECKLIST_IDS:
            errors.append("INVALID_MANUAL_ARCHIVE_CHECKLIST_IDS")

        for item in checklist:
            if not isinstance(item, Mapping):
                errors.append("INVALID_ARCHIVE_CHECKLIST_ITEM")
                continue

            if item.get("status") != "PENDING":
                errors.append("INVALID_ARCHIVE_CHECKLIST_STATUS")

            if item.get("operator_action_required") is not True:
                errors.append(
                    "ARCHIVE_CHECKLIST_OPERATOR_REQUIREMENT_REMOVED"
                )

            if item.get("automatic_completion_allowed") is not False:
                errors.append(
                    "ARCHIVE_CHECKLIST_AUTO_COMPLETION_ENABLED"
                )

    return {
        "app_id": APP_ID,
        "stage": STAGE,
        "ok": not errors,
        "errors": sorted(set(errors)),
        "operator_review_required": True,
        "manual_archive_required": True,
        "archive_execution_performed": False,
        "archive_write_performed": False,
        "archive_record_created": False,
        "source_mutation_performed": False,
        "semantic_rewrite_performed": False,
        "visibility_suppression_performed": False,
        "runtime_execution_performed": False,
        "real_execution_performed": False,
    }
