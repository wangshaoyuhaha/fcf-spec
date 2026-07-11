from __future__ import annotations

import hashlib
import json
from copy import deepcopy
from typing import Any, Mapping, Sequence

from .d1_boundary_contract import APP_ID
from .d5_governance_review_packet import (
    require_valid_governance_review_packet,
    validate_governance_review_packet,
)

REVIEW_RECEIPT_SCHEMA_VERSION = "1.0.0"
ARCHIVE_HANDOFF_SCHEMA_VERSION = "1.0.0"
CLOSEOUT_SCHEMA_VERSION = "1.0.0"

OPERATOR_REVIEW_DECISIONS = (
    "PENDING",
    "APPROVED_FOR_MANUAL_ARCHIVE_HANDOFF",
    "RETURN_FOR_REVISION",
    "REJECTED",
)

CHECK_RESULT_STATUSES = (
    "PENDING",
    "CONFIRMED",
    "NOT_CONFIRMED",
)

ACTION_RESULT_STATUSES = (
    "PENDING",
    "REVIEWED",
    "REQUIRES_REVISION",
    "REJECTED",
)

RECEIPT_KEYS = {
    "receipt_type",
    "schema_version",
    "app_id",
    "status",
    "manifest_id",
    "correlation_id",
    "research_run_id",
    "review_packet_sha256",
    "operator_id",
    "operator_decision",
    "review_note",
    "checklist_results",
    "action_results",
    "all_checklist_items_confirmed",
    "all_operator_actions_reviewed",
    "blocking_issue_count",
    "manual_archive_handoff_allowed",
    "operator_review_required",
    "source_artifacts_preserved",
    "original_conclusions_preserved",
    "causal_truth",
    "probability",
    "winner",
    "automatic_approval",
    "automatic_archive_executed",
    "live_model_invoked",
    "prompt_executed",
    "runtime_orchestrator_executed",
    "trade_action_generated",
    "real_execution",
}

CHECK_RESULT_KEYS = {
    "check_id",
    "check_code",
    "status",
    "operator_confirmation_required",
    "automatic_confirmation_allowed",
}

ACTION_RESULT_KEYS = {
    "action_id",
    "issue_id",
    "issue_code",
    "severity",
    "status",
    "operator_action_required",
    "automatic_resolution_allowed",
}

HANDOFF_KEYS = {
    "handoff_type",
    "schema_version",
    "app_id",
    "status",
    "manifest_id",
    "correlation_id",
    "research_run_id",
    "review_packet_sha256",
    "review_receipt_sha256",
    "operator_id",
    "operator_decision",
    "archive_mode",
    "archive_target",
    "archive_operation",
    "archive_execution_status",
    "manual_operator_action_required",
    "automatic_archive_allowed",
    "automatic_archive_executed",
    "source_artifacts_preserved",
    "original_conclusions_preserved",
    "operator_review_completed",
    "causal_truth",
    "probability",
    "winner",
    "live_model_invoked",
    "prompt_executed",
    "runtime_orchestrator_executed",
    "trade_action_generated",
    "real_execution",
}

CLOSEOUT_KEYS = {
    "closeout_type",
    "schema_version",
    "app_id",
    "phase_id",
    "status",
    "completed_stages",
    "next_required_step",
    "operator_review_required",
    "operator_decision",
    "manual_archive_only",
    "automatic_approval",
    "automatic_archive_executed",
    "source_artifacts_preserved",
    "original_conclusions_preserved",
    "causal_truth",
    "probability",
    "winner",
    "live_model_invoked",
    "prompt_executed",
    "runtime_orchestrator_executed",
    "trade_action_generated",
    "real_execution",
    "tag_created",
    "release_created",
    "deployment_performed",
}


class OperatorReviewReceiptViolation(ValueError):
    """Raised when an operator review receipt is invalid."""


class ManualArchiveHandoffViolation(ValueError):
    """Raised when a manual archive handoff is invalid."""


def _canonical_sha256(value: Mapping[str, object]) -> str:
    encoded = json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    ).encode("ascii")

    return hashlib.sha256(encoded).hexdigest()


def _normalize_result_mapping(
    value: Mapping[str, str] | None,
) -> dict[str, str]:
    if value is None:
        return {}

    normalized: dict[str, str] = {}

    for key, status in value.items():
        if not isinstance(key, str) or not key.strip():
            raise ValueError(
                "result mapping keys must be non-empty strings"
            )

        if not isinstance(status, str) or not status.strip():
            raise ValueError(
                "result mapping statuses must be non-empty strings"
            )

        normalized[key.strip()] = status.strip()

    return normalized


def _receipt_status(decision: str) -> str:
    if decision == "PENDING":
        return "OPERATOR_REVIEW_PENDING"

    if decision == "APPROVED_FOR_MANUAL_ARCHIVE_HANDOFF":
        return "OPERATOR_REVIEW_APPROVED"

    if decision == "RETURN_FOR_REVISION":
        return "OPERATOR_REVIEW_RETURNED_FOR_REVISION"

    return "OPERATOR_REVIEW_REJECTED"


def build_operator_review_receipt(
    *,
    packet: Mapping[str, object],
    operator_id: str = "UNASSIGNED",
    operator_decision: str = "PENDING",
    review_note: str = "",
    checklist_results: Mapping[str, str] | None = None,
    action_results: Mapping[str, str] | None = None,
) -> dict[str, Any]:
    """Build an explicit operator review receipt.

    The default receipt remains pending. Approval is accepted only when an
    identified operator confirms every checklist item, reviews every queued
    action, provides a review note, and the packet has no blocking issue.
    """

    require_valid_governance_review_packet(packet)

    if operator_decision not in OPERATOR_REVIEW_DECISIONS:
        raise OperatorReviewReceiptViolation(
            "operator_decision is not registered"
        )

    if not isinstance(operator_id, str) or not operator_id.strip():
        raise OperatorReviewReceiptViolation(
            "operator_id must be a non-empty string"
        )

    if not isinstance(review_note, str):
        raise OperatorReviewReceiptViolation(
            "review_note must be a string"
        )

    normalized_checks = _normalize_result_mapping(
        checklist_results
    )
    normalized_actions = _normalize_result_mapping(
        action_results
    )

    known_check_codes = {
        str(check["check_code"])
        for check in packet["review_checklist"]
    }
    unknown_checks = sorted(
        set(normalized_checks) - known_check_codes
    )

    if unknown_checks:
        raise OperatorReviewReceiptViolation(
            "unregistered checklist result codes: "
            + ", ".join(unknown_checks)
        )

    known_action_ids = {
        str(action["action_id"])
        for action in packet["operator_action_queue"]
    }
    unknown_actions = sorted(
        set(normalized_actions) - known_action_ids
    )

    if unknown_actions:
        raise OperatorReviewReceiptViolation(
            "unregistered action result identifiers: "
            + ", ".join(unknown_actions)
        )

    checklist = []

    for source_check in packet["review_checklist"]:
        check_code = str(source_check["check_code"])
        status = normalized_checks.get(check_code, "PENDING")

        if status not in CHECK_RESULT_STATUSES:
            raise OperatorReviewReceiptViolation(
                f"invalid checklist result status: {status}"
            )

        checklist.append(
            {
                "check_id": source_check["check_id"],
                "check_code": check_code,
                "status": status,
                "operator_confirmation_required": True,
                "automatic_confirmation_allowed": False,
            }
        )

    actions = []

    for source_action in packet["operator_action_queue"]:
        action_id = str(source_action["action_id"])
        status = normalized_actions.get(action_id, "PENDING")

        if status not in ACTION_RESULT_STATUSES:
            raise OperatorReviewReceiptViolation(
                f"invalid action result status: {status}"
            )

        actions.append(
            {
                "action_id": action_id,
                "issue_id": source_action["issue_id"],
                "issue_code": source_action["issue_code"],
                "severity": source_action["severity"],
                "status": status,
                "operator_action_required": True,
                "automatic_resolution_allowed": False,
            }
        )

    all_checks_confirmed = all(
        check["status"] == "CONFIRMED"
        for check in checklist
    )
    all_actions_reviewed = all(
        action["status"] == "REVIEWED"
        for action in actions
    )

    blocking_issue_count = int(
        packet["issue_summary"]["blocking_issue_count"]
    )

    handoff_allowed = (
        operator_decision
        == "APPROVED_FOR_MANUAL_ARCHIVE_HANDOFF"
        and packet["status"]
        == "REVIEW_PACKET_READY_FOR_OPERATOR_REVIEW"
        and blocking_issue_count == 0
        and all_checks_confirmed
        and all_actions_reviewed
        and operator_id.strip() != "UNASSIGNED"
        and bool(review_note.strip())
    )

    if (
        operator_decision
        == "APPROVED_FOR_MANUAL_ARCHIVE_HANDOFF"
        and not handoff_allowed
    ):
        raise OperatorReviewReceiptViolation(
            "approval requires a ready packet, zero blocking issues, "
            "an identified operator, a review note, all checklist "
            "items confirmed, and all actions reviewed"
        )

    receipt = {
        "receipt_type": "OPERATOR_REVIEW_RECEIPT",
        "schema_version": REVIEW_RECEIPT_SCHEMA_VERSION,
        "app_id": APP_ID,
        "status": _receipt_status(operator_decision),
        "manifest_id": packet["manifest_id"],
        "correlation_id": packet["correlation_id"],
        "research_run_id": packet["research_run_id"],
        "review_packet_sha256": _canonical_sha256(packet),
        "operator_id": operator_id.strip(),
        "operator_decision": operator_decision,
        "review_note": review_note.strip(),
        "checklist_results": checklist,
        "action_results": actions,
        "all_checklist_items_confirmed": all_checks_confirmed,
        "all_operator_actions_reviewed": all_actions_reviewed,
        "blocking_issue_count": blocking_issue_count,
        "manual_archive_handoff_allowed": handoff_allowed,
        "operator_review_required": True,
        "source_artifacts_preserved": True,
        "original_conclusions_preserved": True,
        "causal_truth": "UNDETERMINED",
        "probability": "NOT_ASSIGNED",
        "winner": "NOT_SELECTED",
        "automatic_approval": False,
        "automatic_archive_executed": False,
        "live_model_invoked": False,
        "prompt_executed": False,
        "runtime_orchestrator_executed": False,
        "trade_action_generated": False,
        "real_execution": False,
    }

    require_valid_operator_review_receipt(
        receipt,
        packet,
    )
    return receipt


def _validate_check_result(
    check: Mapping[str, object],
    source_check: Mapping[str, object],
) -> tuple[str, ...]:
    errors: list[str] = []

    missing = sorted(CHECK_RESULT_KEYS - set(check))
    unexpected = sorted(set(check) - CHECK_RESULT_KEYS)

    for key in missing:
        errors.append(f"{key} is missing")

    for key in unexpected:
        errors.append(f"{key} is not registered")

    expected = {
        "check_id": source_check["check_id"],
        "check_code": source_check["check_code"],
        "operator_confirmation_required": True,
        "automatic_confirmation_allowed": False,
    }

    for key, expected_value in expected.items():
        if check.get(key) != expected_value:
            errors.append(f"{key} must be {expected_value!r}")

    if check.get("status") not in CHECK_RESULT_STATUSES:
        errors.append("status is not registered")

    return tuple(errors)


def _validate_action_result(
    action: Mapping[str, object],
    source_action: Mapping[str, object],
) -> tuple[str, ...]:
    errors: list[str] = []

    missing = sorted(ACTION_RESULT_KEYS - set(action))
    unexpected = sorted(set(action) - ACTION_RESULT_KEYS)

    for key in missing:
        errors.append(f"{key} is missing")

    for key in unexpected:
        errors.append(f"{key} is not registered")

    expected = {
        "action_id": source_action["action_id"],
        "issue_id": source_action["issue_id"],
        "issue_code": source_action["issue_code"],
        "severity": source_action["severity"],
        "operator_action_required": True,
        "automatic_resolution_allowed": False,
    }

    for key, expected_value in expected.items():
        if action.get(key) != expected_value:
            errors.append(f"{key} must be {expected_value!r}")

    if action.get("status") not in ACTION_RESULT_STATUSES:
        errors.append("status is not registered")

    return tuple(errors)


def validate_operator_review_receipt(
    receipt: Mapping[str, object],
    packet: Mapping[str, object],
) -> tuple[str, ...]:
    """Return deterministic operator review receipt errors."""

    errors: list[str] = []

    for packet_error in validate_governance_review_packet(packet):
        errors.append(f"packet.{packet_error}")

    missing = sorted(RECEIPT_KEYS - set(receipt))
    unexpected = sorted(set(receipt) - RECEIPT_KEYS)

    for key in missing:
        errors.append(f"{key} is missing")

    for key in unexpected:
        errors.append(f"{key} is not registered")

    expected_scalars = {
        "receipt_type": "OPERATOR_REVIEW_RECEIPT",
        "schema_version": REVIEW_RECEIPT_SCHEMA_VERSION,
        "app_id": APP_ID,
        "manifest_id": packet.get("manifest_id"),
        "correlation_id": packet.get("correlation_id"),
        "research_run_id": packet.get("research_run_id"),
        "review_packet_sha256": _canonical_sha256(packet),
        "operator_review_required": True,
        "source_artifacts_preserved": True,
        "original_conclusions_preserved": True,
        "causal_truth": "UNDETERMINED",
        "probability": "NOT_ASSIGNED",
        "winner": "NOT_SELECTED",
        "automatic_approval": False,
        "automatic_archive_executed": False,
        "live_model_invoked": False,
        "prompt_executed": False,
        "runtime_orchestrator_executed": False,
        "trade_action_generated": False,
        "real_execution": False,
    }

    for key, expected_value in expected_scalars.items():
        if receipt.get(key) != expected_value:
            errors.append(f"{key} must be {expected_value!r}")

    decision = receipt.get("operator_decision")

    if decision not in OPERATOR_REVIEW_DECISIONS:
        errors.append("operator_decision is not registered")
        decision = "PENDING"

    expected_status = _receipt_status(str(decision))

    if receipt.get("status") != expected_status:
        errors.append(f"status must be {expected_status!r}")

    operator_id = receipt.get("operator_id")

    if not isinstance(operator_id, str) or not operator_id.strip():
        errors.append("operator_id must be a non-empty string")

    review_note = receipt.get("review_note")

    if not isinstance(review_note, str):
        errors.append("review_note must be a string")

    checklist = receipt.get("checklist_results")

    if not isinstance(checklist, Sequence) or isinstance(
        checklist,
        (str, bytes),
    ):
        errors.append("checklist_results must be a sequence")
        return tuple(errors)

    source_checks = packet.get("review_checklist", [])

    if len(checklist) != len(source_checks):
        errors.append(
            "checklist_results length does not match packet checklist"
        )

    valid_checks: list[Mapping[str, object]] = []

    for index, source_check in enumerate(source_checks):
        if index >= len(checklist):
            break

        check = checklist[index]

        if not isinstance(check, Mapping):
            errors.append(
                f"checklist_results[{index}] must be a mapping"
            )
            continue

        valid_checks.append(check)

        for check_error in _validate_check_result(
            check,
            source_check,
        ):
            errors.append(
                f"checklist_results[{index}].{check_error}"
            )

    actions = receipt.get("action_results")

    if not isinstance(actions, Sequence) or isinstance(
        actions,
        (str, bytes),
    ):
        errors.append("action_results must be a sequence")
        return tuple(errors)

    source_actions = packet.get("operator_action_queue", [])

    if len(actions) != len(source_actions):
        errors.append(
            "action_results length does not match packet actions"
        )

    valid_actions: list[Mapping[str, object]] = []

    for index, source_action in enumerate(source_actions):
        if index >= len(actions):
            break

        action = actions[index]

        if not isinstance(action, Mapping):
            errors.append(
                f"action_results[{index}] must be a mapping"
            )
            continue

        valid_actions.append(action)

        for action_error in _validate_action_result(
            action,
            source_action,
        ):
            errors.append(
                f"action_results[{index}].{action_error}"
            )

    all_checks_confirmed = (
        len(valid_checks) == len(source_checks)
        and all(
            check.get("status") == "CONFIRMED"
            for check in valid_checks
        )
    )
    all_actions_reviewed = (
        len(valid_actions) == len(source_actions)
        and all(
            action.get("status") == "REVIEWED"
            for action in valid_actions
        )
    )

    if (
        receipt.get("all_checklist_items_confirmed")
        is not all_checks_confirmed
    ):
        errors.append(
            "all_checklist_items_confirmed does not match results"
        )

    if (
        receipt.get("all_operator_actions_reviewed")
        is not all_actions_reviewed
    ):
        errors.append(
            "all_operator_actions_reviewed does not match results"
        )

    blocking_count = packet.get(
        "issue_summary",
        {},
    ).get("blocking_issue_count")

    if receipt.get("blocking_issue_count") != blocking_count:
        errors.append(
            "blocking_issue_count does not match review packet"
        )

    expected_handoff_allowed = (
        decision == "APPROVED_FOR_MANUAL_ARCHIVE_HANDOFF"
        and packet.get("status")
        == "REVIEW_PACKET_READY_FOR_OPERATOR_REVIEW"
        and blocking_count == 0
        and all_checks_confirmed
        and all_actions_reviewed
        and isinstance(operator_id, str)
        and operator_id.strip() != "UNASSIGNED"
        and isinstance(review_note, str)
        and bool(review_note.strip())
    )

    if (
        receipt.get("manual_archive_handoff_allowed")
        is not expected_handoff_allowed
    ):
        errors.append(
            "manual_archive_handoff_allowed is inconsistent"
        )

    if (
        decision == "APPROVED_FOR_MANUAL_ARCHIVE_HANDOFF"
        and not expected_handoff_allowed
    ):
        errors.append(
            "approved receipt does not satisfy manual handoff gates"
        )

    return tuple(errors)


def require_valid_operator_review_receipt(
    receipt: Mapping[str, object],
    packet: Mapping[str, object],
) -> Mapping[str, object]:
    """Require a valid explicit operator review receipt."""

    errors = validate_operator_review_receipt(receipt, packet)

    if errors:
        raise OperatorReviewReceiptViolation("; ".join(errors))

    return receipt


def build_manual_archive_handoff(
    *,
    packet: Mapping[str, object],
    receipt: Mapping[str, object],
) -> dict[str, Any]:
    """Build a handoff record without performing archive execution."""

    require_valid_governance_review_packet(packet)
    require_valid_operator_review_receipt(receipt, packet)

    if (
        receipt["operator_decision"]
        != "APPROVED_FOR_MANUAL_ARCHIVE_HANDOFF"
        or receipt["manual_archive_handoff_allowed"] is not True
    ):
        raise ManualArchiveHandoffViolation(
            "manual archive handoff requires explicit operator approval"
        )

    handoff = {
        "handoff_type": "MANUAL_ARCHIVE_HANDOFF",
        "schema_version": ARCHIVE_HANDOFF_SCHEMA_VERSION,
        "app_id": APP_ID,
        "status": "MANUAL_ARCHIVE_HANDOFF_READY",
        "manifest_id": packet["manifest_id"],
        "correlation_id": packet["correlation_id"],
        "research_run_id": packet["research_run_id"],
        "review_packet_sha256": _canonical_sha256(packet),
        "review_receipt_sha256": _canonical_sha256(receipt),
        "operator_id": receipt["operator_id"],
        "operator_decision": receipt["operator_decision"],
        "archive_mode": "MANUAL_ONLY",
        "archive_target": "UNASSIGNED",
        "archive_operation": "NOT_PERFORMED",
        "archive_execution_status": "PENDING_MANUAL_OPERATOR_ACTION",
        "manual_operator_action_required": True,
        "automatic_archive_allowed": False,
        "automatic_archive_executed": False,
        "source_artifacts_preserved": True,
        "original_conclusions_preserved": True,
        "operator_review_completed": True,
        "causal_truth": "UNDETERMINED",
        "probability": "NOT_ASSIGNED",
        "winner": "NOT_SELECTED",
        "live_model_invoked": False,
        "prompt_executed": False,
        "runtime_orchestrator_executed": False,
        "trade_action_generated": False,
        "real_execution": False,
    }

    require_valid_manual_archive_handoff(
        handoff,
        packet,
        receipt,
    )
    return handoff


def validate_manual_archive_handoff(
    handoff: Mapping[str, object],
    packet: Mapping[str, object],
    receipt: Mapping[str, object],
) -> tuple[str, ...]:
    """Return deterministic manual archive handoff errors."""

    errors: list[str] = []

    for receipt_error in validate_operator_review_receipt(
        receipt,
        packet,
    ):
        errors.append(f"receipt.{receipt_error}")

    missing = sorted(HANDOFF_KEYS - set(handoff))
    unexpected = sorted(set(handoff) - HANDOFF_KEYS)

    for key in missing:
        errors.append(f"{key} is missing")

    for key in unexpected:
        errors.append(f"{key} is not registered")

    expected_scalars = {
        "handoff_type": "MANUAL_ARCHIVE_HANDOFF",
        "schema_version": ARCHIVE_HANDOFF_SCHEMA_VERSION,
        "app_id": APP_ID,
        "status": "MANUAL_ARCHIVE_HANDOFF_READY",
        "manifest_id": packet.get("manifest_id"),
        "correlation_id": packet.get("correlation_id"),
        "research_run_id": packet.get("research_run_id"),
        "review_packet_sha256": _canonical_sha256(packet),
        "review_receipt_sha256": _canonical_sha256(receipt),
        "operator_id": receipt.get("operator_id"),
        "operator_decision": (
            "APPROVED_FOR_MANUAL_ARCHIVE_HANDOFF"
        ),
        "archive_mode": "MANUAL_ONLY",
        "archive_target": "UNASSIGNED",
        "archive_operation": "NOT_PERFORMED",
        "archive_execution_status": (
            "PENDING_MANUAL_OPERATOR_ACTION"
        ),
        "manual_operator_action_required": True,
        "automatic_archive_allowed": False,
        "automatic_archive_executed": False,
        "source_artifacts_preserved": True,
        "original_conclusions_preserved": True,
        "operator_review_completed": True,
        "causal_truth": "UNDETERMINED",
        "probability": "NOT_ASSIGNED",
        "winner": "NOT_SELECTED",
        "live_model_invoked": False,
        "prompt_executed": False,
        "runtime_orchestrator_executed": False,
        "trade_action_generated": False,
        "real_execution": False,
    }

    for key, expected_value in expected_scalars.items():
        if handoff.get(key) != expected_value:
            errors.append(f"{key} must be {expected_value!r}")

    if receipt.get("manual_archive_handoff_allowed") is not True:
        errors.append(
            "receipt does not allow manual archive handoff"
        )

    return tuple(errors)


def require_valid_manual_archive_handoff(
    handoff: Mapping[str, object],
    packet: Mapping[str, object],
    receipt: Mapping[str, object],
) -> Mapping[str, object]:
    """Require a valid non-executing manual archive handoff."""

    errors = validate_manual_archive_handoff(
        handoff,
        packet,
        receipt,
    )

    if errors:
        raise ManualArchiveHandoffViolation("; ".join(errors))

    return handoff


def build_d6_closeout_record() -> dict[str, Any]:
    """Build the deterministic D1-D6 implementation closeout record."""

    record = {
        "closeout_type": (
            "AI_COMPREHENSIVE_REPORT_SYNTHESIS_D6_CLOSEOUT"
        ),
        "schema_version": CLOSEOUT_SCHEMA_VERSION,
        "app_id": APP_ID,
        "phase_id": "AI-COMPREHENSIVE-REPORT-SYNTHESIS-APP-1",
        "status": "D1_D6_IMPLEMENTATION_COMPLETE",
        "completed_stages": [
            "D1_BOUNDARY_AND_ANTI_OVERLAP_CONTRACT",
            "D2_REGISTERED_SOURCE_MANIFEST_AND_VERSION_LOCK",
            "D3_DETERMINISTIC_REPORT_SECTION_ASSEMBLY",
            "D4_CROSS_ARTIFACT_GOVERNANCE_ASSESSMENT",
            "D5_COMPREHENSIVE_GOVERNANCE_REVIEW_PACKET",
            "D6_OPERATOR_REVIEW_AND_MANUAL_ARCHIVE_HANDOFF",
        ],
        "next_required_step": (
            "FINAL_CURRENT_STATE_AND_MAIN_MERGE_REVIEW"
        ),
        "operator_review_required": True,
        "operator_decision": "PENDING",
        "manual_archive_only": True,
        "automatic_approval": False,
        "automatic_archive_executed": False,
        "source_artifacts_preserved": True,
        "original_conclusions_preserved": True,
        "causal_truth": "UNDETERMINED",
        "probability": "NOT_ASSIGNED",
        "winner": "NOT_SELECTED",
        "live_model_invoked": False,
        "prompt_executed": False,
        "runtime_orchestrator_executed": False,
        "trade_action_generated": False,
        "real_execution": False,
        "tag_created": False,
        "release_created": False,
        "deployment_performed": False,
    }

    require_valid_d6_closeout_record(record)
    return record


def validate_d6_closeout_record(
    record: Mapping[str, object],
) -> tuple[str, ...]:
    """Return deterministic D6 closeout validation errors."""

    errors: list[str] = []

    missing = sorted(CLOSEOUT_KEYS - set(record))
    unexpected = sorted(set(record) - CLOSEOUT_KEYS)

    for key in missing:
        errors.append(f"{key} is missing")

    for key in unexpected:
        errors.append(f"{key} is not registered")

    expected = build_d6_closeout_record.__dict__.get(
        "_validation_expected"
    )

    if expected is None:
        expected = {
            "closeout_type": (
                "AI_COMPREHENSIVE_REPORT_SYNTHESIS_D6_CLOSEOUT"
            ),
            "schema_version": CLOSEOUT_SCHEMA_VERSION,
            "app_id": APP_ID,
            "phase_id": (
                "AI-COMPREHENSIVE-REPORT-SYNTHESIS-APP-1"
            ),
            "status": "D1_D6_IMPLEMENTATION_COMPLETE",
            "completed_stages": [
                "D1_BOUNDARY_AND_ANTI_OVERLAP_CONTRACT",
                "D2_REGISTERED_SOURCE_MANIFEST_AND_VERSION_LOCK",
                "D3_DETERMINISTIC_REPORT_SECTION_ASSEMBLY",
                "D4_CROSS_ARTIFACT_GOVERNANCE_ASSESSMENT",
                "D5_COMPREHENSIVE_GOVERNANCE_REVIEW_PACKET",
                "D6_OPERATOR_REVIEW_AND_MANUAL_ARCHIVE_HANDOFF",
            ],
            "next_required_step": (
                "FINAL_CURRENT_STATE_AND_MAIN_MERGE_REVIEW"
            ),
            "operator_review_required": True,
            "operator_decision": "PENDING",
            "manual_archive_only": True,
            "automatic_approval": False,
            "automatic_archive_executed": False,
            "source_artifacts_preserved": True,
            "original_conclusions_preserved": True,
            "causal_truth": "UNDETERMINED",
            "probability": "NOT_ASSIGNED",
            "winner": "NOT_SELECTED",
            "live_model_invoked": False,
            "prompt_executed": False,
            "runtime_orchestrator_executed": False,
            "trade_action_generated": False,
            "real_execution": False,
            "tag_created": False,
            "release_created": False,
            "deployment_performed": False,
        }
        build_d6_closeout_record.__dict__[
            "_validation_expected"
        ] = expected

    for key, expected_value in expected.items():
        if record.get(key) != expected_value:
            errors.append(f"{key} must be {expected_value!r}")

    return tuple(errors)


def require_valid_d6_closeout_record(
    record: Mapping[str, object],
) -> Mapping[str, object]:
    """Require the registered D6 closeout record."""

    errors = validate_d6_closeout_record(record)

    if errors:
        raise ManualArchiveHandoffViolation("; ".join(errors))

    return record