"""D4 read-only UI visibility projection."""

from __future__ import annotations

from copy import deepcopy
from typing import Any, Mapping

from .d1_boundary_contract import APP_ID
from .d3_operator_review_adapter import (
    PACKET_TYPE as REVIEW_PACKET_TYPE,
    validate_operator_review_packet,
)

STAGE = "D4"
UI_CONSUMER_APP_ID = "UI-APP-1"
UI_PACKET_TYPE = "comprehensive_report_ui_visibility_packet"

VISIBLE_SOURCE_FIELDS = (
    "source_statements",
    "original_conclusions",
    "risk_flags",
    "counterevidence",
    "alternative_explanations",
    "uncertainty_states",
)

SECTION_REGISTRY = (
    ("SOURCE_STATEMENTS", "source_statements"),
    ("ORIGINAL_CONCLUSIONS", "original_conclusions"),
    ("RISK_FLAGS", "risk_flags"),
    ("COUNTEREVIDENCE", "counterevidence"),
    ("ALTERNATIVE_EXPLANATIONS", "alternative_explanations"),
    ("UNCERTAINTY_STATES", "uncertainty_states"),
)

PROTECTED_VISIBILITY_FIELDS = (
    "risk_flags",
    "counterevidence",
    "alternative_explanations",
    "uncertainty_states",
)


def _failure(errors: list[str]) -> dict[str, Any]:
    return {
        "app_id": APP_ID,
        "stage": STAGE,
        "ok": False,
        "errors": sorted(set(errors)),
        "packet": None,
        "operator_review_required": True,
        "source_mutation_performed": False,
        "semantic_rewrite_performed": False,
        "visibility_suppression_performed": False,
        "automatic_decision_performed": False,
        "runtime_execution_performed": False,
        "real_execution_performed": False,
    }


def _build_section(
    section_id: str,
    source_field: str,
    items: list[Any],
) -> dict[str, Any]:
    return {
        "section_id": section_id,
        "source_field": source_field,
        "visibility": "VISIBLE",
        "items": deepcopy(items),
        "item_count": len(items),
        "suppressed": False,
        "semantic_rewrite_allowed": False,
        "summary_replacement_allowed": False,
        "operator_review_required": True,
    }


def build_ui_visibility_packet(
    review_packet: Mapping[str, Any],
    source_envelope: Mapping[str, Any],
) -> dict[str, Any]:
    """Project a validated review packet into a read-only UI packet."""

    review_validation = validate_operator_review_packet(
        review_packet,
        source_envelope,
    )

    if not review_validation["ok"]:
        return _failure(list(review_validation["errors"]))

    errors: list[str] = []

    if review_packet.get("packet_type") != REVIEW_PACKET_TYPE:
        errors.append("INVALID_REVIEW_PACKET_TYPE")

    for field in VISIBLE_SOURCE_FIELDS:
        value = review_packet.get(field)

        if not isinstance(value, list):
            errors.append(f"INVALID_VISIBLE_FIELD_{field.upper()}")

    if review_packet.get("review_status") != "REVIEW_REQUIRED":
        errors.append("INVALID_REVIEW_STATUS")

    if review_packet.get("operator_decision") != "PENDING":
        errors.append("INVALID_OPERATOR_DECISION")

    if review_packet.get("operator_review_required") is not True:
        errors.append("OPERATOR_REVIEW_REQUIREMENT_REMOVED")

    if errors:
        return _failure(errors)

    sections = [
        _build_section(
            section_id,
            source_field,
            review_packet[source_field],
        )
        for section_id, source_field in SECTION_REGISTRY
    ]

    visibility_counts = {
        f"{source_field}_count": len(review_packet[source_field])
        for source_field in VISIBLE_SOURCE_FIELDS
    }

    packet = {
        "packet_type": UI_PACKET_TYPE,
        "producer_app_id": APP_ID,
        "consumer_app_id": UI_CONSUMER_APP_ID,
        "source_review_packet_type": review_packet["packet_type"],
        "source_app_id": review_packet["source_app_id"],
        "source_module": review_packet["source_module"],
        "source_artifact_type": review_packet[
            "source_artifact_type"
        ],
        "source_artifact_ref": review_packet[
            "source_artifact_ref"
        ],
        "source_artifact_version": review_packet[
            "source_artifact_version"
        ],
        "source_sha256": review_packet["source_sha256"],
        "correlation_id": review_packet["correlation_id"],
        "review_banner": {
            "visibility": "VISIBLE",
            "review_status": "REVIEW_REQUIRED",
            "operator_decision": "PENDING",
            "operator_review_required": True,
            "automatic_approval_allowed": False,
        },
        "decision_state": {
            "causal_truth": "UNDETERMINED",
            "probability": "NOT_ASSIGNED",
            "winner": "NOT_SELECTED",
            "operator_decision": "PENDING",
        },
        "sections": sections,
        "visibility_counts": visibility_counts,
        "visibility_order": [
            section_id
            for section_id, _source_field in SECTION_REGISTRY
        ],
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
        "operator_review_required": True,
        "risk_suppression_allowed": False,
        "counterevidence_suppression_allowed": False,
        "alternative_explanation_suppression_allowed": False,
        "uncertainty_suppression_allowed": False,
        "semantic_rewrite_allowed": False,
        "summary_replacement_allowed": False,
        "automatic_decision_allowed": False,
        "automatic_approval_allowed": False,
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
        "source_mutation_performed": False,
        "semantic_rewrite_performed": False,
        "visibility_suppression_performed": False,
        "automatic_decision_performed": False,
        "runtime_execution_performed": False,
        "real_execution_performed": False,
    }


def validate_ui_visibility_packet(
    ui_packet: Mapping[str, Any],
    review_packet: Mapping[str, Any],
    source_envelope: Mapping[str, Any],
) -> dict[str, Any]:
    """Validate exact UI visibility and preservation boundaries."""

    errors: list[str] = []

    review_validation = validate_operator_review_packet(
        review_packet,
        source_envelope,
    )

    if not review_validation["ok"]:
        errors.extend(review_validation["errors"])

    identity_fields = {
        "packet_type": UI_PACKET_TYPE,
        "producer_app_id": APP_ID,
        "consumer_app_id": UI_CONSUMER_APP_ID,
        "source_review_packet_type": review_packet.get("packet_type"),
        "source_app_id": review_packet.get("source_app_id"),
        "source_module": review_packet.get("source_module"),
        "source_artifact_type": review_packet.get(
            "source_artifact_type"
        ),
        "source_artifact_ref": review_packet.get(
            "source_artifact_ref"
        ),
        "source_artifact_version": review_packet.get(
            "source_artifact_version"
        ),
        "source_sha256": review_packet.get("source_sha256"),
        "correlation_id": review_packet.get("correlation_id"),
    }

    for field, expected in identity_fields.items():
        if ui_packet.get(field) != expected:
            errors.append(f"IDENTITY_MISMATCH_{field.upper()}")

    banner = ui_packet.get("review_banner")

    if not isinstance(banner, Mapping):
        errors.append("INVALID_REVIEW_BANNER")
    else:
        expected_banner = {
            "visibility": "VISIBLE",
            "review_status": "REVIEW_REQUIRED",
            "operator_decision": "PENDING",
            "operator_review_required": True,
            "automatic_approval_allowed": False,
        }

        if dict(banner) != expected_banner:
            errors.append("INVALID_REVIEW_BANNER_STATE")

    decision_state = ui_packet.get("decision_state")

    if not isinstance(decision_state, Mapping):
        errors.append("INVALID_DECISION_STATE")
    else:
        expected_decision_state = {
            "causal_truth": "UNDETERMINED",
            "probability": "NOT_ASSIGNED",
            "winner": "NOT_SELECTED",
            "operator_decision": "PENDING",
        }

        if dict(decision_state) != expected_decision_state:
            errors.append("UNSAFE_DECISION_STATE")

    sections = ui_packet.get("sections")

    if not isinstance(sections, list):
        errors.append("INVALID_UI_SECTIONS")
    else:
        section_ids = tuple(
            section.get("section_id")
            for section in sections
            if isinstance(section, Mapping)
        )

        expected_ids = tuple(
            section_id
            for section_id, _source_field in SECTION_REGISTRY
        )

        if section_ids != expected_ids:
            errors.append("INVALID_UI_SECTION_ORDER")

        for expected, section in zip(SECTION_REGISTRY, sections):
            section_id, source_field = expected

            if not isinstance(section, Mapping):
                errors.append("INVALID_UI_SECTION")
                continue

            if section.get("section_id") != section_id:
                errors.append(
                    f"INVALID_UI_SECTION_ID_{section_id}"
                )

            if section.get("source_field") != source_field:
                errors.append(
                    f"INVALID_UI_SOURCE_FIELD_{section_id}"
                )

            if section.get("visibility") != "VISIBLE":
                errors.append(
                    f"UI_SECTION_NOT_VISIBLE_{section_id}"
                )

            if section.get("items") != review_packet.get(source_field):
                errors.append(
                    f"UI_PRESERVATION_MISMATCH_{source_field.upper()}"
                )

            expected_items = review_packet.get(source_field)

            if isinstance(expected_items, list):
                if section.get("item_count") != len(expected_items):
                    errors.append(
                        f"INVALID_UI_COUNT_{source_field.upper()}"
                    )

            if section.get("suppressed") is not False:
                errors.append(
                    f"UI_SECTION_SUPPRESSED_{section_id}"
                )

            if section.get("semantic_rewrite_allowed") is not False:
                errors.append(
                    f"UI_REWRITE_ENABLED_{section_id}"
                )

            if section.get("summary_replacement_allowed") is not False:
                errors.append(
                    f"UI_SUMMARY_REPLACEMENT_ENABLED_{section_id}"
                )

            if section.get("operator_review_required") is not True:
                errors.append(
                    f"UI_REVIEW_REQUIREMENT_REMOVED_{section_id}"
                )

    for field in PROTECTED_VISIBILITY_FIELDS:
        if ui_packet.get(field) != review_packet.get(field):
            errors.append(
                f"PROTECTED_VISIBILITY_MISMATCH_{field.upper()}"
            )

    expected_order = [
        section_id
        for section_id, _source_field in SECTION_REGISTRY
    ]

    if ui_packet.get("visibility_order") != expected_order:
        errors.append("INVALID_VISIBILITY_ORDER")

    expected_counts = {
        f"{field}_count": len(review_packet.get(field, []))
        for field in VISIBLE_SOURCE_FIELDS
    }

    if ui_packet.get("visibility_counts") != expected_counts:
        errors.append("INVALID_VISIBILITY_COUNTS")

    if ui_packet.get("operator_review_required") is not True:
        errors.append("OPERATOR_REVIEW_REQUIREMENT_REMOVED")

    false_fields = (
        "risk_suppression_allowed",
        "counterevidence_suppression_allowed",
        "alternative_explanation_suppression_allowed",
        "uncertainty_suppression_allowed",
        "semantic_rewrite_allowed",
        "summary_replacement_allowed",
        "automatic_decision_allowed",
        "automatic_approval_allowed",
        "source_mutation_allowed",
        "runtime_execution_allowed",
        "real_execution_allowed",
    )

    for field in false_fields:
        if ui_packet.get(field) is not False:
            errors.append(f"UNSAFE_{field.upper()}")

    return {
        "app_id": APP_ID,
        "stage": STAGE,
        "ok": not errors,
        "errors": sorted(set(errors)),
        "operator_review_required": True,
        "source_mutation_performed": False,
        "semantic_rewrite_performed": False,
        "visibility_suppression_performed": False,
        "automatic_decision_performed": False,
        "runtime_execution_performed": False,
        "real_execution_performed": False,
    }
