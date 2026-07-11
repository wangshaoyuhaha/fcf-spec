"""D3 deterministic operator-review integration adapter."""

from __future__ import annotations

from copy import deepcopy
from typing import Any, Mapping

from .d1_boundary_contract import APP_ID
from .d2_registered_source_loader import (
    load_registered_source_from_mapping,
    validate_registered_source_envelope,
)

STAGE = "D3"
CONSUMER_APP_ID = "OPERATOR-REVIEW-APP-1"
PACKET_TYPE = "comprehensive_report_operator_review_packet"

PRESERVED_FIELDS = (
    "source_statements",
    "original_conclusions",
    "risk_flags",
    "counterevidence",
    "alternative_explanations",
    "uncertainty_states",
)

REQUIRED_SOURCE_FIELDS = (
    "correlation_id",
    *PRESERVED_FIELDS,
    "operator_review_required",
)

CHECKLIST_IDS = (
    "VERIFY_SOURCE_IDENTITY",
    "VERIFY_SOURCE_VERSION_LOCK",
    "VERIFY_CORRELATION_ID",
    "REVIEW_SOURCE_STATEMENTS",
    "REVIEW_ORIGINAL_CONCLUSIONS",
    "REVIEW_RISK_FLAGS",
    "REVIEW_COUNTEREVIDENCE",
    "REVIEW_ALTERNATIVE_EXPLANATIONS",
    "REVIEW_UNCERTAINTY_STATES",
    "RECORD_OPERATOR_DECISION",
)

ACTION_IDS = (
    "REVIEW_COMPREHENSIVE_REPORT",
    "REVIEW_RISK_AND_UNCERTAINTY",
    "REVIEW_COUNTEREVIDENCE_AND_ALTERNATIVES",
    "RECORD_OPERATOR_DECISION",
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
        "archive_execution_performed": False,
        "source_mutation_performed": False,
        "runtime_execution_performed": False,
        "real_execution_performed": False,
    }


def _review_checklist() -> list[dict[str, Any]]:
    return [
        {
            "check_id": check_id,
            "status": "PENDING",
            "operator_action_required": True,
            "automatic_completion_allowed": False,
        }
        for check_id in CHECKLIST_IDS
    ]


def _operator_actions() -> list[dict[str, Any]]:
    return [
        {
            "action_id": action_id,
            "status": "PENDING",
            "operator_action_required": True,
            "automatic_execution_allowed": False,
        }
        for action_id in ACTION_IDS
    ]


def build_operator_review_packet(
    envelope: Mapping[str, Any],
    *,
    expected_source_artifact_ref: str | None = None,
    expected_source_artifact_version: str | None = None,
    expected_correlation_id: str | None = None,
    expected_source_sha256: str | None = None,
) -> dict[str, Any]:
    """Build a read-only operator-review packet."""

    loaded = load_registered_source_from_mapping(
        envelope,
        expected_source_artifact_ref=expected_source_artifact_ref,
        expected_source_artifact_version=expected_source_artifact_version,
        expected_correlation_id=expected_correlation_id,
        expected_source_sha256=expected_source_sha256,
    )

    if not loaded["ok"]:
        return _failure(list(loaded["validation"]["errors"]))

    registered = loaded["registered_source"]
    payload = registered.get("source_payload")

    if not isinstance(payload, Mapping):
        return _failure(["INVALID_SOURCE_PAYLOAD"])

    errors: list[str] = []

    for field in REQUIRED_SOURCE_FIELDS:
        if field not in payload:
            errors.append(f"MISSING_SOURCE_FIELD_{field.upper()}")

    if payload.get("operator_review_required") is not True:
        errors.append("SOURCE_REVIEW_REQUIREMENT_REMOVED")

    if payload.get("correlation_id") != registered.get("correlation_id"):
        errors.append("SOURCE_CORRELATION_ID_MISMATCH")

    if errors:
        return _failure(errors)

    packet = {
        "packet_type": PACKET_TYPE,
        "producer_app_id": APP_ID,
        "consumer_app_id": CONSUMER_APP_ID,
        "source_app_id": registered["source_app_id"],
        "source_module": registered["source_module"],
        "source_artifact_type": registered["source_artifact_type"],
        "source_artifact_ref": registered["source_artifact_ref"],
        "source_artifact_version": registered[
            "source_artifact_version"
        ],
        "source_sha256": registered["source_sha256"],
        "correlation_id": registered["correlation_id"],
        "review_status": "REVIEW_REQUIRED",
        "operator_decision": "PENDING",
        "causal_truth": "UNDETERMINED",
        "probability": "NOT_ASSIGNED",
        "winner": "NOT_SELECTED",
        "source_statements": deepcopy(payload["source_statements"]),
        "original_conclusions": deepcopy(
            payload["original_conclusions"]
        ),
        "risk_flags": deepcopy(payload["risk_flags"]),
        "counterevidence": deepcopy(payload["counterevidence"]),
        "alternative_explanations": deepcopy(
            payload["alternative_explanations"]
        ),
        "uncertainty_states": deepcopy(
            payload["uncertainty_states"]
        ),
        "review_checklist": _review_checklist(),
        "operator_action_queue": _operator_actions(),
        "operator_review_required": True,
        "automatic_approval_allowed": False,
        "automatic_archive_execution_allowed": False,
        "source_mutation_allowed": False,
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
        "automatic_approval_performed": False,
        "archive_execution_performed": False,
        "source_mutation_performed": False,
        "runtime_execution_performed": False,
        "real_execution_performed": False,
    }


def validate_operator_review_packet(
    packet: Mapping[str, Any],
    envelope: Mapping[str, Any],
) -> dict[str, Any]:
    """Validate identity, preservation, and manual-review boundaries."""

    errors: list[str] = []

    source_validation = validate_registered_source_envelope(envelope)

    if not source_validation["ok"]:
        errors.extend(source_validation["errors"])

    payload = envelope.get("source_payload")

    if not isinstance(payload, Mapping):
        errors.append("INVALID_SOURCE_PAYLOAD")
        payload = {}

    identity_fields = {
        "packet_type": PACKET_TYPE,
        "producer_app_id": APP_ID,
        "consumer_app_id": CONSUMER_APP_ID,
        "source_app_id": envelope.get("source_app_id"),
        "source_module": envelope.get("source_module"),
        "source_artifact_type": envelope.get("source_artifact_type"),
        "source_artifact_ref": envelope.get("source_artifact_ref"),
        "source_artifact_version": envelope.get(
            "source_artifact_version"
        ),
        "source_sha256": envelope.get("source_sha256"),
        "correlation_id": envelope.get("correlation_id"),
    }

    for field, expected in identity_fields.items():
        if packet.get(field) != expected:
            errors.append(f"IDENTITY_MISMATCH_{field.upper()}")

    for field in PRESERVED_FIELDS:
        if packet.get(field) != payload.get(field):
            errors.append(f"PRESERVATION_MISMATCH_{field.upper()}")

    required_states = {
        "review_status": "REVIEW_REQUIRED",
        "operator_decision": "PENDING",
        "causal_truth": "UNDETERMINED",
        "probability": "NOT_ASSIGNED",
        "winner": "NOT_SELECTED",
        "operator_review_required": True,
    }

    for field, expected in required_states.items():
        if packet.get(field) != expected:
            errors.append(f"INVALID_{field.upper()}")

    false_fields = (
        "automatic_approval_allowed",
        "automatic_archive_execution_allowed",
        "source_mutation_allowed",
        "runtime_execution_allowed",
        "real_execution_allowed",
    )

    for field in false_fields:
        if packet.get(field) is not False:
            errors.append(f"UNSAFE_{field.upper()}")

    checklist = packet.get("review_checklist")

    if not isinstance(checklist, list):
        errors.append("INVALID_REVIEW_CHECKLIST")
    else:
        ids = tuple(
            item.get("check_id")
            for item in checklist
            if isinstance(item, Mapping)
        )

        if ids != CHECKLIST_IDS:
            errors.append("INVALID_REVIEW_CHECKLIST_IDS")

        for item in checklist:
            if not isinstance(item, Mapping):
                errors.append("INVALID_REVIEW_CHECKLIST_ITEM")
                continue

            if item.get("status") != "PENDING":
                errors.append("INVALID_REVIEW_CHECKLIST_STATUS")

            if item.get("operator_action_required") is not True:
                errors.append("CHECKLIST_OPERATOR_REQUIREMENT_REMOVED")

            if item.get("automatic_completion_allowed") is not False:
                errors.append("CHECKLIST_AUTO_COMPLETION_ENABLED")

    actions = packet.get("operator_action_queue")

    if not isinstance(actions, list):
        errors.append("INVALID_OPERATOR_ACTION_QUEUE")
    else:
        ids = tuple(
            item.get("action_id")
            for item in actions
            if isinstance(item, Mapping)
        )

        if ids != ACTION_IDS:
            errors.append("INVALID_OPERATOR_ACTION_IDS")

        for item in actions:
            if not isinstance(item, Mapping):
                errors.append("INVALID_OPERATOR_ACTION_ITEM")
                continue

            if item.get("status") != "PENDING":
                errors.append("INVALID_OPERATOR_ACTION_STATUS")

            if item.get("operator_action_required") is not True:
                errors.append("OPERATOR_ACTION_REQUIREMENT_REMOVED")

            if item.get("automatic_execution_allowed") is not False:
                errors.append("OPERATOR_ACTION_AUTO_EXECUTION_ENABLED")

    return {
        "app_id": APP_ID,
        "stage": STAGE,
        "ok": not errors,
        "errors": sorted(set(errors)),
        "operator_review_required": True,
        "automatic_approval_performed": False,
        "archive_execution_performed": False,
        "source_mutation_performed": False,
        "runtime_execution_performed": False,
        "real_execution_performed": False,
    }
