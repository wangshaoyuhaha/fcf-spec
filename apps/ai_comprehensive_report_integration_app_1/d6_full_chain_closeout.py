"""D6 deterministic full-chain integration validation and closeout."""

from __future__ import annotations

from copy import deepcopy
from typing import Any, Mapping

from .d1_boundary_contract import APP_ID
from .d2_registered_source_loader import (
    validate_registered_source_envelope,
)
from .d3_operator_review_adapter import (
    build_operator_review_packet,
    validate_operator_review_packet,
)
from .d4_ui_visibility_projection import (
    build_ui_visibility_packet,
    validate_ui_visibility_packet,
)
from .d5_manual_archive_projection import (
    build_manual_archive_candidate_packet,
    validate_manual_archive_candidate_packet,
)

STAGE = "D6"
CLOSEOUT_PACKET_TYPE = (
    "comprehensive_report_integration_full_chain_closeout_packet"
)

CHAIN_STAGE_IDS = (
    "D1_BOUNDARY_CONTRACT",
    "D2_REGISTERED_SOURCE",
    "D3_OPERATOR_REVIEW",
    "D4_UI_VISIBILITY",
    "D5_MANUAL_ARCHIVE",
    "D6_FULL_CHAIN_CLOSEOUT",
)

CLOSEOUT_CHECKLIST_IDS = (
    "VERIFY_D1_BOUNDARY_TEST_SUITE",
    "VERIFY_D2_REGISTERED_SOURCE",
    "VERIFY_D3_OPERATOR_REVIEW_PACKET",
    "VERIFY_D4_UI_VISIBILITY_PACKET",
    "VERIFY_D5_MANUAL_ARCHIVE_PACKET",
    "VERIFY_SOURCE_IDENTITY_CHAIN",
    "VERIFY_CORRELATION_ID_CHAIN",
    "VERIFY_OPERATOR_REVIEW_REQUIRED",
    "VERIFY_NO_AUTOMATIC_ARCHIVE",
    "VERIFY_NO_RUNTIME_EXECUTION",
    "VERIFY_NO_REAL_EXECUTION",
    "RECORD_MANUAL_MERGE_REVIEW",
)


def _failure(
    failed_stage: str,
    errors: list[str],
) -> dict[str, Any]:
    return {
        "app_id": APP_ID,
        "stage": STAGE,
        "ok": False,
        "failed_stage": failed_stage,
        "errors": sorted(set(errors)),
        "packet": None,
        "operator_review_required": True,
        "manual_merge_review_required": True,
        "automatic_merge_performed": False,
        "automatic_archive_performed": False,
        "archive_write_performed": False,
        "source_mutation_performed": False,
        "semantic_rewrite_performed": False,
        "visibility_suppression_performed": False,
        "runtime_execution_performed": False,
        "real_execution_performed": False,
        "tag_created": False,
        "release_created": False,
        "deployment_performed": False,
    }


def _closeout_checklist() -> list[dict[str, Any]]:
    return [
        {
            "check_id": check_id,
            "status": "PENDING_OPERATOR_CONFIRMATION",
            "operator_action_required": True,
            "automatic_completion_allowed": False,
        }
        for check_id in CLOSEOUT_CHECKLIST_IDS
    ]


def build_full_chain_closeout_packet(
    source_envelope: Mapping[str, Any],
) -> dict[str, Any]:
    """Build a non-executing D1-D6 integration closeout packet."""

    source_validation = validate_registered_source_envelope(
        source_envelope
    )

    if not source_validation["ok"]:
        return _failure(
            "D2_REGISTERED_SOURCE",
            list(source_validation["errors"]),
        )

    review_result = build_operator_review_packet(source_envelope)

    if not review_result["ok"]:
        return _failure(
            "D3_OPERATOR_REVIEW",
            list(review_result["errors"]),
        )

    review_packet = review_result["packet"]

    review_validation = validate_operator_review_packet(
        review_packet,
        source_envelope,
    )

    if not review_validation["ok"]:
        return _failure(
            "D3_OPERATOR_REVIEW",
            list(review_validation["errors"]),
        )

    ui_result = build_ui_visibility_packet(
        review_packet,
        source_envelope,
    )

    if not ui_result["ok"]:
        return _failure(
            "D4_UI_VISIBILITY",
            list(ui_result["errors"]),
        )

    ui_packet = ui_result["packet"]

    ui_validation = validate_ui_visibility_packet(
        ui_packet,
        review_packet,
        source_envelope,
    )

    if not ui_validation["ok"]:
        return _failure(
            "D4_UI_VISIBILITY",
            list(ui_validation["errors"]),
        )

    archive_result = build_manual_archive_candidate_packet(
        ui_packet,
        review_packet,
        source_envelope,
    )

    if not archive_result["ok"]:
        return _failure(
            "D5_MANUAL_ARCHIVE",
            list(archive_result["errors"]),
        )

    archive_packet = archive_result["packet"]

    archive_validation = validate_manual_archive_candidate_packet(
        archive_packet,
        ui_packet,
        review_packet,
        source_envelope,
    )

    if not archive_validation["ok"]:
        return _failure(
            "D5_MANUAL_ARCHIVE",
            list(archive_validation["errors"]),
        )

    stage_validations = {
        "D1_BOUNDARY_CONTRACT": {
            "ok": True,
            "evidence": (
                "D1 contract tests are required in the D6 "
                "targeted validation suite"
            ),
        },
        "D2_REGISTERED_SOURCE": deepcopy(source_validation),
        "D3_OPERATOR_REVIEW": deepcopy(review_validation),
        "D4_UI_VISIBILITY": deepcopy(ui_validation),
        "D5_MANUAL_ARCHIVE": deepcopy(archive_validation),
        "D6_FULL_CHAIN_CLOSEOUT": {
            "ok": True,
            "evidence": "full deterministic chain constructed",
        },
    }

    packet = {
        "packet_type": CLOSEOUT_PACKET_TYPE,
        "producer_app_id": APP_ID,
        "phase_id": "AI-COMPREHENSIVE-REPORT-INTEGRATION-APP-1",
        "phase_stage": STAGE,
        "phase_status": "D1_D6_COMPLETE_PENDING_MANUAL_MERGE",
        "chain_stage_ids": list(CHAIN_STAGE_IDS),
        "source_app_id": source_envelope["source_app_id"],
        "source_module": source_envelope["source_module"],
        "source_artifact_type": source_envelope[
            "source_artifact_type"
        ],
        "source_artifact_ref": source_envelope[
            "source_artifact_ref"
        ],
        "source_artifact_version": source_envelope[
            "source_artifact_version"
        ],
        "source_sha256": source_envelope["source_sha256"],
        "correlation_id": source_envelope["correlation_id"],
        "stage_validations": stage_validations,
        "registered_source": deepcopy(dict(source_envelope)),
        "operator_review_packet": deepcopy(review_packet),
        "ui_visibility_packet": deepcopy(ui_packet),
        "manual_archive_candidate_packet": deepcopy(
            archive_packet
        ),
        "final_review_status": "REVIEW_REQUIRED",
        "final_operator_decision": "PENDING",
        "final_archive_status": "PENDING_MANUAL_ARCHIVE",
        "merge_readiness": "READY_FOR_MANUAL_MERGE_REVIEW",
        "closeout_checklist": _closeout_checklist(),
        "operator_review_required": True,
        "manual_merge_review_required": True,
        "manual_archive_required": True,
        "automatic_merge_allowed": False,
        "automatic_archive_allowed": False,
        "archive_write_allowed": False,
        "source_mutation_allowed": False,
        "semantic_rewrite_allowed": False,
        "visibility_suppression_allowed": False,
        "runtime_execution_allowed": False,
        "real_execution_allowed": False,
        "tag_allowed": False,
        "release_allowed": False,
        "deployment_allowed": False,
    }

    return {
        "app_id": APP_ID,
        "stage": STAGE,
        "ok": True,
        "failed_stage": None,
        "errors": [],
        "packet": packet,
        "operator_review_required": True,
        "manual_merge_review_required": True,
        "automatic_merge_performed": False,
        "automatic_archive_performed": False,
        "archive_write_performed": False,
        "source_mutation_performed": False,
        "semantic_rewrite_performed": False,
        "visibility_suppression_performed": False,
        "runtime_execution_performed": False,
        "real_execution_performed": False,
        "tag_created": False,
        "release_created": False,
        "deployment_performed": False,
    }


def validate_full_chain_closeout_packet(
    closeout_packet: Mapping[str, Any],
    source_envelope: Mapping[str, Any],
) -> dict[str, Any]:
    """Validate the complete deterministic integration closeout."""

    errors: list[str] = []

    rebuilt = build_full_chain_closeout_packet(source_envelope)

    if not rebuilt["ok"]:
        return _failure(
            rebuilt["failed_stage"] or "UNKNOWN",
            list(rebuilt["errors"]),
        )

    expected_packet = rebuilt["packet"]

    identity_fields = (
        "packet_type",
        "producer_app_id",
        "phase_id",
        "phase_stage",
        "source_app_id",
        "source_module",
        "source_artifact_type",
        "source_artifact_ref",
        "source_artifact_version",
        "source_sha256",
        "correlation_id",
    )

    for field in identity_fields:
        if closeout_packet.get(field) != expected_packet.get(field):
            errors.append(f"IDENTITY_MISMATCH_{field.upper()}")

    exact_fields = (
        "chain_stage_ids",
        "stage_validations",
        "registered_source",
        "operator_review_packet",
        "ui_visibility_packet",
        "manual_archive_candidate_packet",
    )

    for field in exact_fields:
        if closeout_packet.get(field) != expected_packet.get(field):
            errors.append(f"CHAIN_MISMATCH_{field.upper()}")

    expected_states = {
        "phase_status": "D1_D6_COMPLETE_PENDING_MANUAL_MERGE",
        "final_review_status": "REVIEW_REQUIRED",
        "final_operator_decision": "PENDING",
        "final_archive_status": "PENDING_MANUAL_ARCHIVE",
        "merge_readiness": "READY_FOR_MANUAL_MERGE_REVIEW",
        "operator_review_required": True,
        "manual_merge_review_required": True,
        "manual_archive_required": True,
    }

    for field, expected in expected_states.items():
        if closeout_packet.get(field) != expected:
            errors.append(f"INVALID_{field.upper()}")

    false_fields = (
        "automatic_merge_allowed",
        "automatic_archive_allowed",
        "archive_write_allowed",
        "source_mutation_allowed",
        "semantic_rewrite_allowed",
        "visibility_suppression_allowed",
        "runtime_execution_allowed",
        "real_execution_allowed",
        "tag_allowed",
        "release_allowed",
        "deployment_allowed",
    )

    for field in false_fields:
        if closeout_packet.get(field) is not False:
            errors.append(f"UNSAFE_{field.upper()}")

    checklist = closeout_packet.get("closeout_checklist")

    if not isinstance(checklist, list):
        errors.append("INVALID_CLOSEOUT_CHECKLIST")
    else:
        checklist_ids = tuple(
            item.get("check_id")
            for item in checklist
            if isinstance(item, Mapping)
        )

        if checklist_ids != CLOSEOUT_CHECKLIST_IDS:
            errors.append("INVALID_CLOSEOUT_CHECKLIST_IDS")

        for item in checklist:
            if not isinstance(item, Mapping):
                errors.append("INVALID_CLOSEOUT_CHECKLIST_ITEM")
                continue

            if (
                item.get("status")
                != "PENDING_OPERATOR_CONFIRMATION"
            ):
                errors.append("INVALID_CLOSEOUT_CHECKLIST_STATUS")

            if item.get("operator_action_required") is not True:
                errors.append(
                    "CLOSEOUT_OPERATOR_REQUIREMENT_REMOVED"
                )

            if item.get("automatic_completion_allowed") is not False:
                errors.append(
                    "CLOSEOUT_AUTO_COMPLETION_ENABLED"
                )

    return {
        "app_id": APP_ID,
        "stage": STAGE,
        "ok": not errors,
        "failed_stage": None if not errors else STAGE,
        "errors": sorted(set(errors)),
        "operator_review_required": True,
        "manual_merge_review_required": True,
        "automatic_merge_performed": False,
        "automatic_archive_performed": False,
        "archive_write_performed": False,
        "source_mutation_performed": False,
        "semantic_rewrite_performed": False,
        "visibility_suppression_performed": False,
        "runtime_execution_performed": False,
        "real_execution_performed": False,
        "tag_created": False,
        "release_created": False,
        "deployment_performed": False,
    }
