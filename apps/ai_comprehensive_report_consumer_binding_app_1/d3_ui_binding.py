"""D3 deterministic UI production consumer binding."""

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

STAGE = "D3"
UI_CONSUMER_APP_ID = "UI-APP-1"
UI_BINDING_PACKET_TYPE = (
    "comprehensive_report_ui_consumer_binding_packet"
)

REQUIRED_VISIBLE_SECTION_IDS = (
    "SOURCE_STATEMENTS",
    "ORIGINAL_CONCLUSIONS",
    "RISK_FLAGS",
    "COUNTEREVIDENCE",
    "ALTERNATIVE_EXPLANATIONS",
    "UNCERTAINTY_STATES",
)

REQUIRED_UI_FIELDS = (
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


def _failure(errors: list[str]) -> dict[str, Any]:
    return {
        "app_id": APP_ID,
        "stage": STAGE,
        "ok": False,
        "errors": sorted(set(errors)),
        "packet": None,
        "operator_review_required": True,
        "visibility_suppression_performed": False,
        "semantic_rewrite_performed": False,
        "source_mutation_performed": False,
        "runtime_execution_performed": False,
        "real_execution_performed": False,
    }


def _section_map(
    sections: object,
) -> dict[str, Mapping[str, Any]]:
    if not isinstance(sections, list):
        return {}

    result: dict[str, Mapping[str, Any]] = {}

    for section in sections:
        if not isinstance(section, Mapping):
            continue

        section_id = section.get("section_id")

        if isinstance(section_id, str):
            result[section_id] = section

    return result


def build_ui_consumer_binding(
    closeout_packet: Mapping[str, Any],
    source_envelope: Mapping[str, Any],
) -> dict[str, Any]:
    """Bind a validated closeout packet to the UI consumer."""

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

    ui_packet = closeout_packet.get("ui_visibility_packet")

    if not isinstance(ui_packet, Mapping):
        errors.append("MISSING_UI_VISIBILITY_PACKET")
        return _failure(errors)

    for field in REQUIRED_IDENTITY_FIELDS:
        if field not in closeout_packet:
            errors.append(f"MISSING_IDENTITY_FIELD_{field.upper()}")

    for field in REQUIRED_UI_FIELDS:
        if field not in ui_packet:
            errors.append(f"MISSING_UI_FIELD_{field.upper()}")

    sections = _section_map(ui_packet.get("sections"))

    for section_id in REQUIRED_VISIBLE_SECTION_IDS:
        section = sections.get(section_id)

        if section is None:
            errors.append(f"MISSING_VISIBLE_SECTION_{section_id}")
            continue

        if section.get("visibility") != "VISIBLE":
            errors.append(f"SECTION_NOT_VISIBLE_{section_id}")

    visibility_order = ui_packet.get("visibility_order")

    if tuple(visibility_order or ()) != REQUIRED_VISIBLE_SECTION_IDS:
        errors.append("INVALID_VISIBILITY_ORDER")

    review_banner = ui_packet.get("review_banner")

    if not isinstance(review_banner, Mapping):
        errors.append("INVALID_REVIEW_BANNER")
    else:
        if review_banner.get("review_status") != "REVIEW_REQUIRED":
            errors.append("INVALID_REVIEW_STATUS")

        if review_banner.get("operator_decision") != "PENDING":
            errors.append("INVALID_OPERATOR_DECISION")

        if review_banner.get("operator_review_required") is not True:
            errors.append("OPERATOR_REVIEW_REQUIREMENT_REMOVED")

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

    if errors:
        return _failure(errors)

    packet = {
        "packet_type": UI_BINDING_PACKET_TYPE,
        "producer_app_id": APP_ID,
        "consumer_app_id": UI_CONSUMER_APP_ID,
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
        "ui_visibility_packet": deepcopy(dict(ui_packet)),
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
        "display_status": "VISIBLE_READ_ONLY",
        "review_status": "REVIEW_REQUIRED",
        "operator_decision": "PENDING",
        "binding_status": "BOUND_READ_ONLY",
        "operator_review_required": True,
        "registered_artifact_required": True,
        "all_required_sections_visible": True,
        "summary_replacement_allowed": False,
        "visibility_suppression_allowed": False,
        "semantic_rewrite_allowed": False,
        "source_mutation_allowed": False,
        "automatic_approval_allowed": False,
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
        "visibility_suppression_performed": False,
        "semantic_rewrite_performed": False,
        "source_mutation_performed": False,
        "runtime_execution_performed": False,
        "real_execution_performed": False,
    }


def validate_ui_consumer_binding(
    binding_packet: Mapping[str, Any],
    closeout_packet: Mapping[str, Any],
    source_envelope: Mapping[str, Any],
) -> dict[str, Any]:
    """Validate exact UI identity and visibility preservation."""

    errors: list[str] = []

    rebuilt = build_ui_consumer_binding(
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
        "ui_visibility_packet",
        *REQUIRED_UI_FIELDS,
    )

    for field in preserved_fields:
        if binding_packet.get(field) != expected.get(field):
            errors.append(f"UI_CONTENT_MISMATCH_{field.upper()}")

    expected_states = {
        "display_status": "VISIBLE_READ_ONLY",
        "review_status": "REVIEW_REQUIRED",
        "operator_decision": "PENDING",
        "binding_status": "BOUND_READ_ONLY",
        "operator_review_required": True,
        "registered_artifact_required": True,
        "all_required_sections_visible": True,
    }

    for field, expected_value in expected_states.items():
        if binding_packet.get(field) != expected_value:
            errors.append(f"INVALID_{field.upper()}")

    false_fields = (
        "summary_replacement_allowed",
        "visibility_suppression_allowed",
        "semantic_rewrite_allowed",
        "source_mutation_allowed",
        "automatic_approval_allowed",
        "runtime_model_invocation_allowed",
        "prompt_execution_allowed",
        "automatic_routing_allowed",
        "real_execution_allowed",
    )

    for field in false_fields:
        if binding_packet.get(field) is not False:
            errors.append(f"UNSAFE_{field.upper()}")

    sections = _section_map(binding_packet.get("sections"))

    for section_id in REQUIRED_VISIBLE_SECTION_IDS:
        section = sections.get(section_id)

        if section is None:
            errors.append(f"MISSING_BOUND_SECTION_{section_id}")
            continue

        if section.get("visibility") != "VISIBLE":
            errors.append(f"BOUND_SECTION_NOT_VISIBLE_{section_id}")

    return {
        "app_id": APP_ID,
        "stage": STAGE,
        "ok": not errors,
        "errors": sorted(set(errors)),
        "operator_review_required": True,
        "visibility_suppression_performed": False,
        "semantic_rewrite_performed": False,
        "source_mutation_performed": False,
        "runtime_execution_performed": False,
        "real_execution_performed": False,
    }
