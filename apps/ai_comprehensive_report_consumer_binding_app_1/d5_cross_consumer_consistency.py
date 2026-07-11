"""D5 deterministic cross-consumer consistency validation."""

from __future__ import annotations

from copy import deepcopy
from typing import Any, Mapping

from .d1_binding_contract import (
    APP_ID,
    REQUIRED_IDENTITY_FIELDS,
)
from .d2_operator_review_binding import (
    BINDING_PACKET_TYPE,
    CONSUMER_APP_ID,
    build_operator_review_consumer_binding,
    validate_operator_review_consumer_binding,
)
from .d3_ui_binding import (
    UI_BINDING_PACKET_TYPE,
    UI_CONSUMER_APP_ID,
    build_ui_consumer_binding,
    validate_ui_consumer_binding,
)
from .d4_report_archive_binding import (
    ARCHIVE_BINDING_PACKET_TYPE,
    ARCHIVE_CONSUMER_APP_ID,
    build_report_archive_consumer_binding,
    validate_report_archive_consumer_binding,
)

STAGE = "D5"
CONSISTENCY_PACKET_TYPE = (
    "comprehensive_report_cross_consumer_consistency_packet"
)

COMMON_CONTENT_FIELDS = (
    "risk_flags",
    "counterevidence",
    "alternative_explanations",
    "uncertainty_states",
)

CHECKED_CONSUMERS = (
    CONSUMER_APP_ID,
    UI_CONSUMER_APP_ID,
    ARCHIVE_CONSUMER_APP_ID,
)


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


def _failure(errors: list[str]) -> dict[str, Any]:
    return {
        "app_id": APP_ID,
        "stage": STAGE,
        "ok": False,
        "errors": sorted(set(errors)),
        "packet": None,
        "consistency_status": "BLOCKED",
        "operator_review_required": True,
        "manual_archive_required": True,
        "automatic_approval_performed": False,
        "automatic_archive_performed": False,
        "archive_write_performed": False,
        "source_mutation_performed": False,
        "semantic_rewrite_performed": False,
        "visibility_suppression_performed": False,
        "runtime_execution_performed": False,
        "real_execution_performed": False,
    }


def validate_cross_consumer_bindings(
    operator_binding: Mapping[str, Any],
    ui_binding: Mapping[str, Any],
    archive_binding: Mapping[str, Any],
    closeout_packet: Mapping[str, Any],
    source_envelope: Mapping[str, Any],
) -> dict[str, Any]:
    """Validate identity, content, and state across all consumers."""

    errors: list[str] = []

    if not isinstance(operator_binding, Mapping):
        return _failure(["MISSING_OPERATOR_BINDING"])

    if not isinstance(ui_binding, Mapping):
        return _failure(["MISSING_UI_BINDING"])

    if not isinstance(archive_binding, Mapping):
        return _failure(["MISSING_ARCHIVE_BINDING"])

    operator_validation = validate_operator_review_consumer_binding(
        operator_binding,
        closeout_packet,
        source_envelope,
    )
    ui_validation = validate_ui_consumer_binding(
        ui_binding,
        closeout_packet,
        source_envelope,
    )
    archive_validation = validate_report_archive_consumer_binding(
        archive_binding,
        closeout_packet,
        source_envelope,
    )

    if not operator_validation["ok"]:
        errors.extend(
            _prefixed_errors(
                "OPERATOR",
                operator_validation["errors"],
            )
        )

    if not ui_validation["ok"]:
        errors.extend(
            _prefixed_errors(
                "UI",
                ui_validation["errors"],
            )
        )

    if not archive_validation["ok"]:
        errors.extend(
            _prefixed_errors(
                "ARCHIVE",
                archive_validation["errors"],
            )
        )

    surfaces = {
        "OPERATOR": operator_binding,
        "UI": ui_binding,
        "ARCHIVE": archive_binding,
    }

    for surface_name, surface_packet in surfaces.items():
        for field in REQUIRED_IDENTITY_FIELDS:
            if surface_packet.get(field) != closeout_packet.get(field):
                errors.append(
                    "CROSS_IDENTITY_MISMATCH_"
                    f"{surface_name}_{field.upper()}"
                )

    if operator_binding.get("packet_type") != BINDING_PACKET_TYPE:
        errors.append("INVALID_OPERATOR_PACKET_TYPE")

    if ui_binding.get("packet_type") != UI_BINDING_PACKET_TYPE:
        errors.append("INVALID_UI_PACKET_TYPE")

    if (
        archive_binding.get("packet_type")
        != ARCHIVE_BINDING_PACKET_TYPE
    ):
        errors.append("INVALID_ARCHIVE_PACKET_TYPE")

    if operator_binding.get("consumer_app_id") != CONSUMER_APP_ID:
        errors.append("INVALID_OPERATOR_CONSUMER_APP_ID")

    if ui_binding.get("consumer_app_id") != UI_CONSUMER_APP_ID:
        errors.append("INVALID_UI_CONSUMER_APP_ID")

    if (
        archive_binding.get("consumer_app_id")
        != ARCHIVE_CONSUMER_APP_ID
    ):
        errors.append("INVALID_ARCHIVE_CONSUMER_APP_ID")

    for field in COMMON_CONTENT_FIELDS:
        operator_value = operator_binding.get(field)

        if ui_binding.get(field) != operator_value:
            errors.append(
                f"CROSS_CONTENT_MISMATCH_UI_{field.upper()}"
            )

        if archive_binding.get(field) != operator_value:
            errors.append(
                f"CROSS_CONTENT_MISMATCH_ARCHIVE_{field.upper()}"
            )

    if ui_binding.get("sections") != archive_binding.get("sections"):
        errors.append("CROSS_CONTENT_MISMATCH_ARCHIVE_SECTIONS")

    required_states = (
        (
            operator_binding,
            "operator_decision",
            "PENDING",
            "OPERATOR",
        ),
        (
            operator_binding,
            "binding_status",
            "BOUND_READ_ONLY",
            "OPERATOR",
        ),
        (
            ui_binding,
            "operator_decision",
            "PENDING",
            "UI",
        ),
        (
            ui_binding,
            "binding_status",
            "BOUND_READ_ONLY",
            "UI",
        ),
        (
            archive_binding,
            "operator_archive_decision",
            "PENDING",
            "ARCHIVE",
        ),
        (
            archive_binding,
            "archive_status",
            "PENDING_MANUAL_ARCHIVE",
            "ARCHIVE",
        ),
        (
            archive_binding,
            "binding_status",
            "BOUND_READ_ONLY",
            "ARCHIVE",
        ),
    )

    for packet, field, expected, surface_name in required_states:
        if packet.get(field) != expected:
            errors.append(
                f"CROSS_STATE_MISMATCH_{surface_name}_{field.upper()}"
            )

    required_true_fields = (
        (
            operator_binding,
            "operator_review_required",
            "OPERATOR",
        ),
        (
            ui_binding,
            "operator_review_required",
            "UI",
        ),
        (
            archive_binding,
            "operator_review_required",
            "ARCHIVE",
        ),
        (
            archive_binding,
            "manual_archive_required",
            "ARCHIVE",
        ),
    )

    for packet, field, surface_name in required_true_fields:
        if packet.get(field) is not True:
            errors.append(
                f"CROSS_REQUIRED_TRUE_{surface_name}_{field.upper()}"
            )

    required_false_fields = (
        (
            operator_binding,
            "automatic_approval_allowed",
            "OPERATOR",
        ),
        (
            operator_binding,
            "source_mutation_allowed",
            "OPERATOR",
        ),
        (
            ui_binding,
            "visibility_suppression_allowed",
            "UI",
        ),
        (
            ui_binding,
            "automatic_approval_allowed",
            "UI",
        ),
        (
            archive_binding,
            "automatic_archive_allowed",
            "ARCHIVE",
        ),
        (
            archive_binding,
            "archive_execution_allowed",
            "ARCHIVE",
        ),
        (
            archive_binding,
            "archive_write_allowed",
            "ARCHIVE",
        ),
        (
            archive_binding,
            "archive_record_creation_allowed",
            "ARCHIVE",
        ),
    )

    for packet, field, surface_name in required_false_fields:
        if packet.get(field) is not False:
            errors.append(
                f"CROSS_UNSAFE_TRUE_{surface_name}_{field.upper()}"
            )

    return {
        "app_id": APP_ID,
        "stage": STAGE,
        "ok": not errors,
        "errors": sorted(set(errors)),
        "consistency_status": (
            "CONSISTENT"
            if not errors
            else "BLOCKED"
        ),
        "checked_consumers": list(CHECKED_CONSUMERS),
        "operator_review_required": True,
        "manual_archive_required": True,
        "automatic_approval_performed": False,
        "automatic_archive_performed": False,
        "archive_write_performed": False,
        "source_mutation_performed": False,
        "semantic_rewrite_performed": False,
        "visibility_suppression_performed": False,
        "runtime_execution_performed": False,
        "real_execution_performed": False,
    }


def build_cross_consumer_binding_bundle(
    closeout_packet: Mapping[str, Any],
    source_envelope: Mapping[str, Any],
) -> dict[str, Any]:
    """Build and validate all three deterministic bindings."""

    operator_result = build_operator_review_consumer_binding(
        closeout_packet,
        source_envelope,
    )
    ui_result = build_ui_consumer_binding(
        closeout_packet,
        source_envelope,
    )
    archive_result = build_report_archive_consumer_binding(
        closeout_packet,
        source_envelope,
    )

    errors: list[str] = []

    if not operator_result["ok"]:
        errors.extend(
            _prefixed_errors(
                "OPERATOR",
                operator_result["errors"],
            )
        )

    if not ui_result["ok"]:
        errors.extend(
            _prefixed_errors(
                "UI",
                ui_result["errors"],
            )
        )

    if not archive_result["ok"]:
        errors.extend(
            _prefixed_errors(
                "ARCHIVE",
                archive_result["errors"],
            )
        )

    if errors:
        return _failure(errors)

    operator_packet = operator_result["packet"]
    ui_packet = ui_result["packet"]
    archive_packet = archive_result["packet"]

    consistency = validate_cross_consumer_bindings(
        operator_packet,
        ui_packet,
        archive_packet,
        closeout_packet,
        source_envelope,
    )

    if not consistency["ok"]:
        return _failure(list(consistency["errors"]))

    identity = {
        field: deepcopy(closeout_packet[field])
        for field in REQUIRED_IDENTITY_FIELDS
    }

    common_content = {
        field: deepcopy(operator_packet[field])
        for field in COMMON_CONTENT_FIELDS
    }

    packet = {
        "packet_type": CONSISTENCY_PACKET_TYPE,
        "producer_app_id": APP_ID,
        "source_packet_type": closeout_packet["packet_type"],
        "checked_consumers": list(CHECKED_CONSUMERS),
        "identity": identity,
        "common_content": common_content,
        "operator_review_binding": deepcopy(operator_packet),
        "ui_binding": deepcopy(ui_packet),
        "report_archive_binding": deepcopy(archive_packet),
        "consistency_status": "CONSISTENT",
        "operator_review_status": "REVIEW_REQUIRED",
        "operator_decision": "PENDING",
        "archive_status": "PENDING_MANUAL_ARCHIVE",
        "operator_archive_decision": "PENDING",
        "binding_status": "BOUND_READ_ONLY",
        "operator_review_required": True,
        "manual_archive_required": True,
        "automatic_approval_allowed": False,
        "automatic_archive_allowed": False,
        "archive_execution_allowed": False,
        "archive_write_allowed": False,
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
        "consistency_status": "CONSISTENT",
        "operator_review_required": True,
        "manual_archive_required": True,
        "automatic_approval_performed": False,
        "automatic_archive_performed": False,
        "archive_write_performed": False,
        "source_mutation_performed": False,
        "semantic_rewrite_performed": False,
        "visibility_suppression_performed": False,
        "runtime_execution_performed": False,
        "real_execution_performed": False,
    }


def validate_cross_consumer_binding_bundle(
    bundle: Mapping[str, Any],
    closeout_packet: Mapping[str, Any],
    source_envelope: Mapping[str, Any],
) -> dict[str, Any]:
    """Validate a complete D5 cross-consumer bundle."""

    errors: list[str] = []

    if bundle.get("packet_type") != CONSISTENCY_PACKET_TYPE:
        errors.append("INVALID_CONSISTENCY_PACKET_TYPE")

    operator_binding = bundle.get("operator_review_binding")
    ui_binding = bundle.get("ui_binding")
    archive_binding = bundle.get("report_archive_binding")

    if not isinstance(operator_binding, Mapping):
        errors.append("MISSING_BUNDLE_OPERATOR_BINDING")

    if not isinstance(ui_binding, Mapping):
        errors.append("MISSING_BUNDLE_UI_BINDING")

    if not isinstance(archive_binding, Mapping):
        errors.append("MISSING_BUNDLE_ARCHIVE_BINDING")

    if errors:
        return _failure(errors)

    raw_validation = validate_cross_consumer_bindings(
        operator_binding,
        ui_binding,
        archive_binding,
        closeout_packet,
        source_envelope,
    )

    if not raw_validation["ok"]:
        errors.extend(list(raw_validation["errors"]))

    expected_result = build_cross_consumer_binding_bundle(
        closeout_packet,
        source_envelope,
    )

    if not expected_result["ok"]:
        errors.extend(list(expected_result["errors"]))
        return _failure(errors)

    expected = expected_result["packet"]

    for field in (
        "producer_app_id",
        "source_packet_type",
        "checked_consumers",
        "identity",
        "common_content",
        "consistency_status",
        "operator_review_status",
        "operator_decision",
        "archive_status",
        "operator_archive_decision",
        "binding_status",
    ):
        if bundle.get(field) != expected.get(field):
            errors.append(f"BUNDLE_MISMATCH_{field.upper()}")

    true_fields = (
        "operator_review_required",
        "manual_archive_required",
    )

    for field in true_fields:
        if bundle.get(field) is not True:
            errors.append(f"BUNDLE_REQUIRED_TRUE_{field.upper()}")

    false_fields = (
        "automatic_approval_allowed",
        "automatic_archive_allowed",
        "archive_execution_allowed",
        "archive_write_allowed",
        "source_mutation_allowed",
        "semantic_rewrite_allowed",
        "visibility_suppression_allowed",
        "runtime_model_invocation_allowed",
        "prompt_execution_allowed",
        "automatic_routing_allowed",
        "real_execution_allowed",
    )

    for field in false_fields:
        if bundle.get(field) is not False:
            errors.append(f"BUNDLE_UNSAFE_TRUE_{field.upper()}")

    return {
        "app_id": APP_ID,
        "stage": STAGE,
        "ok": not errors,
        "errors": sorted(set(errors)),
        "consistency_status": (
            "CONSISTENT"
            if not errors
            else "BLOCKED"
        ),
        "checked_consumers": list(CHECKED_CONSUMERS),
        "operator_review_required": True,
        "manual_archive_required": True,
        "automatic_approval_performed": False,
        "automatic_archive_performed": False,
        "archive_write_performed": False,
        "source_mutation_performed": False,
        "semantic_rewrite_performed": False,
        "visibility_suppression_performed": False,
        "runtime_execution_performed": False,
        "real_execution_performed": False,
    }
