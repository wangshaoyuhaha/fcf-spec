from __future__ import annotations

from collections import Counter
from copy import deepcopy
from typing import Any, Mapping, Sequence

from .d1_boundary_contract import APP_ID
from .d2_source_manifest import (
    require_valid_source_manifest,
    validate_source_manifest,
)
from .d3_report_assembly import (
    require_valid_report_sections,
    validate_report_sections,
)
from .d4_governance_assessment import (
    require_valid_governance_assessment,
    validate_governance_assessment,
)

REVIEW_PACKET_SCHEMA_VERSION = "1.0.0"

REVIEW_CHECKLIST_ITEMS = (
    "VERIFY_SOURCE_VERSION_LOCKS",
    "REVIEW_BLOCKING_GOVERNANCE_ISSUES",
    "REVIEW_HIGH_SEVERITY_GOVERNANCE_ISSUES",
    "REVIEW_REGISTERED_COUNTEREVIDENCE",
    "REVIEW_ALTERNATIVE_EXPLANATIONS",
    "REVIEW_REGISTERED_RISK_FLAGS",
    "CONFIRM_SOURCE_CONCLUSIONS_PRESERVED",
    "CONFIRM_NO_AUTOMATIC_TRUTH_PROBABILITY_OR_WINNER",
    "RECORD_OPERATOR_DECISION",
    "PREPARE_MANUAL_ARCHIVE_HANDOFF",
)

SEVERITY_PRIORITY = {
    "BLOCKING": "P0",
    "HIGH": "P1",
    "MEDIUM": "P2",
    "LOW": "P3",
}

SEVERITY_ACTION = {
    "BLOCKING": (
        "RESOLVE_BLOCKING_GOVERNANCE_ISSUE_AND_REBUILD_PACKET"
    ),
    "HIGH": "REVIEW_HIGH_SEVERITY_GOVERNANCE_ISSUE",
    "MEDIUM": "REVIEW_REGISTERED_GOVERNANCE_ISSUE",
    "LOW": "ACKNOWLEDGE_REGISTERED_GOVERNANCE_ISSUE",
}

PACKET_KEYS = {
    "review_packet_type",
    "schema_version",
    "app_id",
    "status",
    "manifest_id",
    "correlation_id",
    "research_run_id",
    "source_manifest",
    "report",
    "governance_assessment",
    "source_inventory",
    "section_inventory",
    "issue_summary",
    "operator_action_queue",
    "review_checklist",
    "operator_review_required",
    "operator_decision",
    "archive_handoff_allowed",
    "manual_archive_only",
    "source_artifacts_preserved",
    "original_conclusions_preserved",
    "causal_truth",
    "probability",
    "winner",
    "live_model_invoked",
    "prompt_executed",
    "runtime_orchestrator_executed",
    "automatic_archive_executed",
    "trade_action_generated",
    "real_execution",
}

ACTION_KEYS = {
    "action_type",
    "schema_version",
    "action_id",
    "issue_id",
    "issue_code",
    "severity",
    "priority",
    "required_action",
    "artifact_ids",
    "section_ids",
    "item_ids",
    "status",
    "operator_decision",
    "operator_action_required",
    "automatic_resolution_allowed",
}

CHECKLIST_KEYS = {
    "check_type",
    "schema_version",
    "check_id",
    "check_code",
    "status",
    "operator_confirmation_required",
    "automatic_confirmation_allowed",
}


class GovernanceReviewPacketViolation(ValueError):
    """Raised when a D5 governance review packet is invalid."""


def _build_source_inventory(
    manifest: Mapping[str, object],
) -> list[dict[str, object]]:
    return [
        deepcopy(dict(source))
        for source in manifest["sources"]
    ]


def _build_section_inventory(
    report: Mapping[str, object],
) -> list[dict[str, object]]:
    inventory: list[dict[str, object]] = []

    for section in report["sections"]:
        inventory.append(
            {
                "section_id": section["section_id"],
                "section_title": section["section_title"],
                "section_type": section["section_type"],
                "item_count": len(section["items"]),
            }
        )

    return inventory


def _build_issue_summary(
    assessment: Mapping[str, object],
) -> dict[str, object]:
    severity_counts = dict(
        sorted(
            Counter(
                str(issue["severity"])
                for issue in assessment["issues"]
            ).items()
        )
    )

    return {
        "issue_count": assessment["issue_count"],
        "blocking_issue_count": assessment[
            "blocking_issue_count"
        ],
        "unresolved_issue_count": assessment[
            "unresolved_issue_count"
        ],
        "issue_code_counts": deepcopy(
            assessment["issue_code_counts"]
        ),
        "severity_counts": severity_counts,
    }


def _build_operator_action_queue(
    assessment: Mapping[str, object],
) -> list[dict[str, object]]:
    queue: list[dict[str, object]] = []

    for index, issue in enumerate(
        assessment["issues"],
        start=1,
    ):
        severity = str(issue["severity"])

        queue.append(
            {
                "action_type": (
                    "GOVERNANCE_OPERATOR_REVIEW_ACTION"
                ),
                "schema_version": REVIEW_PACKET_SCHEMA_VERSION,
                "action_id": f"OP-{index:04d}",
                "issue_id": issue["issue_id"],
                "issue_code": issue["issue_code"],
                "severity": severity,
                "priority": SEVERITY_PRIORITY[severity],
                "required_action": SEVERITY_ACTION[severity],
                "artifact_ids": deepcopy(issue["artifact_ids"]),
                "section_ids": deepcopy(issue["section_ids"]),
                "item_ids": deepcopy(issue["item_ids"]),
                "status": "PENDING",
                "operator_decision": "PENDING",
                "operator_action_required": True,
                "automatic_resolution_allowed": False,
            }
        )

    return queue


def _build_review_checklist() -> list[dict[str, object]]:
    return [
        {
            "check_type": "GOVERNANCE_REVIEW_CHECK",
            "schema_version": REVIEW_PACKET_SCHEMA_VERSION,
            "check_id": f"CHECK-{index:02d}",
            "check_code": check_code,
            "status": "PENDING",
            "operator_confirmation_required": True,
            "automatic_confirmation_allowed": False,
        }
        for index, check_code in enumerate(
            REVIEW_CHECKLIST_ITEMS,
            start=1,
        )
    ]


def build_governance_review_packet(
    *,
    manifest: Mapping[str, object],
    report: Mapping[str, object],
    assessment: Mapping[str, object],
) -> dict[str, Any]:
    """Build a deterministic operator governance review packet."""

    require_valid_source_manifest(manifest)
    require_valid_report_sections(report)
    require_valid_governance_assessment(assessment)

    identity_fields = (
        "manifest_id",
        "correlation_id",
        "research_run_id",
    )

    for field_name in identity_fields:
        values = {
            manifest[field_name],
            report[field_name],
            assessment[field_name],
        }

        if len(values) != 1:
            raise GovernanceReviewPacketViolation(
                f"{field_name} is not aligned across D2, D3, and D4"
            )

    status = (
        "REVIEW_PACKET_BLOCKED"
        if assessment["blocking_issue_count"]
        else "REVIEW_PACKET_READY_FOR_OPERATOR_REVIEW"
    )

    packet = {
        "review_packet_type": (
            "COMPREHENSIVE_GOVERNANCE_REVIEW_PACKET"
        ),
        "schema_version": REVIEW_PACKET_SCHEMA_VERSION,
        "app_id": APP_ID,
        "status": status,
        "manifest_id": manifest["manifest_id"],
        "correlation_id": manifest["correlation_id"],
        "research_run_id": manifest["research_run_id"],
        "source_manifest": deepcopy(dict(manifest)),
        "report": deepcopy(dict(report)),
        "governance_assessment": deepcopy(dict(assessment)),
        "source_inventory": _build_source_inventory(manifest),
        "section_inventory": _build_section_inventory(report),
        "issue_summary": _build_issue_summary(assessment),
        "operator_action_queue": _build_operator_action_queue(
            assessment
        ),
        "review_checklist": _build_review_checklist(),
        "operator_review_required": True,
        "operator_decision": "PENDING",
        "archive_handoff_allowed": False,
        "manual_archive_only": True,
        "source_artifacts_preserved": True,
        "original_conclusions_preserved": True,
        "causal_truth": "UNDETERMINED",
        "probability": "NOT_ASSIGNED",
        "winner": "NOT_SELECTED",
        "live_model_invoked": False,
        "prompt_executed": False,
        "runtime_orchestrator_executed": False,
        "automatic_archive_executed": False,
        "trade_action_generated": False,
        "real_execution": False,
    }

    require_valid_governance_review_packet(packet)
    return packet


def _validate_operator_action(
    action: Mapping[str, object],
    expected: Mapping[str, object],
) -> tuple[str, ...]:
    errors: list[str] = []

    missing = sorted(ACTION_KEYS - set(action))
    unexpected = sorted(set(action) - ACTION_KEYS)

    for key in missing:
        errors.append(f"{key} is missing")

    for key in unexpected:
        errors.append(f"{key} is not registered")

    for key, expected_value in expected.items():
        if action.get(key) != expected_value:
            errors.append(f"{key} must be {expected_value!r}")

    return tuple(errors)


def _validate_review_check(
    check: Mapping[str, object],
    expected: Mapping[str, object],
) -> tuple[str, ...]:
    errors: list[str] = []

    missing = sorted(CHECKLIST_KEYS - set(check))
    unexpected = sorted(set(check) - CHECKLIST_KEYS)

    for key in missing:
        errors.append(f"{key} is missing")

    for key in unexpected:
        errors.append(f"{key} is not registered")

    for key, expected_value in expected.items():
        if check.get(key) != expected_value:
            errors.append(f"{key} must be {expected_value!r}")

    return tuple(errors)


def validate_governance_review_packet(
    packet: Mapping[str, object],
) -> tuple[str, ...]:
    """Return deterministic D5 review packet validation errors."""

    errors: list[str] = []

    missing = sorted(PACKET_KEYS - set(packet))
    unexpected = sorted(set(packet) - PACKET_KEYS)

    for key in missing:
        errors.append(f"{key} is missing")

    for key in unexpected:
        errors.append(f"{key} is not registered")

    expected_scalars = {
        "review_packet_type": (
            "COMPREHENSIVE_GOVERNANCE_REVIEW_PACKET"
        ),
        "schema_version": REVIEW_PACKET_SCHEMA_VERSION,
        "app_id": APP_ID,
        "operator_review_required": True,
        "operator_decision": "PENDING",
        "archive_handoff_allowed": False,
        "manual_archive_only": True,
        "source_artifacts_preserved": True,
        "original_conclusions_preserved": True,
        "causal_truth": "UNDETERMINED",
        "probability": "NOT_ASSIGNED",
        "winner": "NOT_SELECTED",
        "live_model_invoked": False,
        "prompt_executed": False,
        "runtime_orchestrator_executed": False,
        "automatic_archive_executed": False,
        "trade_action_generated": False,
        "real_execution": False,
    }

    for key, expected_value in expected_scalars.items():
        if packet.get(key) != expected_value:
            errors.append(f"{key} must be {expected_value!r}")

    manifest = packet.get("source_manifest")
    report = packet.get("report")
    assessment = packet.get("governance_assessment")

    if not isinstance(manifest, Mapping):
        errors.append("source_manifest must be a mapping")
        return tuple(errors)

    if not isinstance(report, Mapping):
        errors.append("report must be a mapping")
        return tuple(errors)

    if not isinstance(assessment, Mapping):
        errors.append(
            "governance_assessment must be a mapping"
        )
        return tuple(errors)

    for manifest_error in validate_source_manifest(manifest):
        errors.append(
            f"source_manifest.{manifest_error}"
        )

    for report_error in validate_report_sections(report):
        errors.append(f"report.{report_error}")

    for assessment_error in validate_governance_assessment(
        assessment
    ):
        errors.append(
            f"governance_assessment.{assessment_error}"
        )

    for field_name in (
        "manifest_id",
        "correlation_id",
        "research_run_id",
    ):
        packet_value = packet.get(field_name)
        values = {
            manifest.get(field_name),
            report.get(field_name),
            assessment.get(field_name),
            packet_value,
        }

        if len(values) != 1:
            errors.append(
                f"{field_name} is not aligned across packet artifacts"
            )

    expected_status = (
        "REVIEW_PACKET_BLOCKED"
        if assessment.get("blocking_issue_count")
        else "REVIEW_PACKET_READY_FOR_OPERATOR_REVIEW"
    )

    if packet.get("status") != expected_status:
        errors.append(f"status must be {expected_status!r}")

    expected_source_inventory = _build_source_inventory(manifest)

    if packet.get("source_inventory") != expected_source_inventory:
        errors.append(
            "source_inventory does not match source_manifest"
        )

    expected_section_inventory = _build_section_inventory(report)

    if packet.get("section_inventory") != expected_section_inventory:
        errors.append(
            "section_inventory does not match report sections"
        )

    expected_issue_summary = _build_issue_summary(assessment)

    if packet.get("issue_summary") != expected_issue_summary:
        errors.append(
            "issue_summary does not match governance_assessment"
        )

    queue = packet.get("operator_action_queue")

    if not isinstance(queue, Sequence) or isinstance(
        queue,
        (str, bytes),
    ):
        errors.append("operator_action_queue must be a sequence")
    else:
        expected_queue = _build_operator_action_queue(
            assessment
        )

        if len(queue) != len(expected_queue):
            errors.append(
                "operator_action_queue length does not match issues"
            )

        for index, expected_action in enumerate(expected_queue):
            if index >= len(queue):
                break

            action = queue[index]

            if not isinstance(action, Mapping):
                errors.append(
                    f"operator_action_queue[{index}] must be a mapping"
                )
                continue

            for action_error in _validate_operator_action(
                action,
                expected_action,
            ):
                errors.append(
                    f"operator_action_queue[{index}].{action_error}"
                )

    checklist = packet.get("review_checklist")

    if not isinstance(checklist, Sequence) or isinstance(
        checklist,
        (str, bytes),
    ):
        errors.append("review_checklist must be a sequence")
    else:
        expected_checklist = _build_review_checklist()

        if len(checklist) != len(expected_checklist):
            errors.append(
                "review_checklist length is invalid"
            )

        for index, expected_check in enumerate(
            expected_checklist
        ):
            if index >= len(checklist):
                break

            check = checklist[index]

            if not isinstance(check, Mapping):
                errors.append(
                    f"review_checklist[{index}] must be a mapping"
                )
                continue

            for check_error in _validate_review_check(
                check,
                expected_check,
            ):
                errors.append(
                    f"review_checklist[{index}].{check_error}"
                )

    return tuple(errors)


def require_valid_governance_review_packet(
    packet: Mapping[str, object],
) -> Mapping[str, object]:
    """Require a valid D5 comprehensive review packet."""

    errors = validate_governance_review_packet(packet)

    if errors:
        raise GovernanceReviewPacketViolation("; ".join(errors))

    return packet