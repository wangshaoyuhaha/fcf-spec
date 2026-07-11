from __future__ import annotations

from copy import deepcopy

from apps.ai_comprehensive_report_consumer_binding_app_1 import (
    CHECKED_CONSUMERS,
    COMMON_CONTENT_FIELDS,
    CONSISTENCY_PACKET_TYPE,
    build_cross_consumer_binding_bundle,
    build_operator_review_consumer_binding,
    build_report_archive_consumer_binding,
    build_ui_consumer_binding,
    validate_cross_consumer_binding_bundle,
    validate_cross_consumer_bindings,
)
from apps.ai_comprehensive_report_integration_app_1 import (
    build_full_chain_closeout_packet,
    build_registered_source_envelope,
)


def source_envelope() -> dict[str, object]:
    payload = {
        "correlation_id": "corr-consumer-d5",
        "source_statements": [
            "Statement A",
            "Statement B",
        ],
        "original_conclusions": [
            "NO_AUTOMATIC_CONCLUSION",
        ],
        "risk_flags": [
            "REVIEW_REQUIRED",
            "UNCERTAINTY_PRESENT",
        ],
        "counterevidence": [
            "Counterevidence A",
        ],
        "alternative_explanations": [
            "Alternative A",
        ],
        "uncertainty_states": [
            "UNRESOLVED",
        ],
        "operator_review_required": True,
    }

    return build_registered_source_envelope(
        source_payload=payload,
        source_artifact_ref=(
            "artifacts/ai_comprehensive_report_synthesis/"
            "consumer-d5.json"
        ),
        source_artifact_version="1.0.0",
        correlation_id="corr-consumer-d5",
    )


def chain() -> tuple[dict[str, object], dict[str, object]]:
    source = source_envelope()
    closeout = build_full_chain_closeout_packet(source)["packet"]

    return source, closeout


def bindings() -> tuple[
    dict[str, object],
    dict[str, object],
    dict[str, object],
    dict[str, object],
    dict[str, object],
]:
    source, closeout = chain()

    operator = build_operator_review_consumer_binding(
        closeout,
        source,
    )["packet"]
    ui = build_ui_consumer_binding(
        closeout,
        source,
    )["packet"]
    archive = build_report_archive_consumer_binding(
        closeout,
        source,
    )["packet"]

    return source, closeout, operator, ui, archive


def test_d5_builds_consistent_bundle() -> None:
    source, closeout = chain()

    result = build_cross_consumer_binding_bundle(
        closeout,
        source,
    )

    assert result["ok"] is True
    assert result["errors"] == []
    assert result["consistency_status"] == "CONSISTENT"
    assert result["packet"]["packet_type"] == CONSISTENCY_PACKET_TYPE


def test_d5_checks_all_consumers() -> None:
    source, closeout = chain()
    packet = build_cross_consumer_binding_bundle(
        closeout,
        source,
    )["packet"]

    assert tuple(packet["checked_consumers"]) == CHECKED_CONSUMERS


def test_d5_preserves_identity_bundle() -> None:
    source, closeout = chain()
    packet = build_cross_consumer_binding_bundle(
        closeout,
        source,
    )["packet"]

    for field, value in packet["identity"].items():
        assert value == closeout[field]


def test_d5_preserves_common_content_bundle() -> None:
    source, closeout = chain()
    packet = build_cross_consumer_binding_bundle(
        closeout,
        source,
    )["packet"]

    operator = packet["operator_review_binding"]

    for field in COMMON_CONTENT_FIELDS:
        assert packet["common_content"][field] == operator[field]


def test_d5_consumer_states_remain_pending() -> None:
    source, closeout = chain()
    packet = build_cross_consumer_binding_bundle(
        closeout,
        source,
    )["packet"]

    assert packet["operator_decision"] == "PENDING"
    assert packet["operator_archive_decision"] == "PENDING"
    assert packet["archive_status"] == "PENDING_MANUAL_ARCHIVE"
    assert packet["binding_status"] == "BOUND_READ_ONLY"


def test_d5_blocks_unsafe_bundle_behavior() -> None:
    source, closeout = chain()
    packet = build_cross_consumer_binding_bundle(
        closeout,
        source,
    )["packet"]

    assert packet["automatic_approval_allowed"] is False
    assert packet["automatic_archive_allowed"] is False
    assert packet["archive_execution_allowed"] is False
    assert packet["archive_write_allowed"] is False
    assert packet["source_mutation_allowed"] is False
    assert packet["real_execution_allowed"] is False


def test_d5_valid_raw_bindings_pass() -> None:
    source, closeout, operator, ui, archive = bindings()

    result = validate_cross_consumer_bindings(
        operator,
        ui,
        archive,
        closeout,
        source,
    )

    assert result["ok"] is True
    assert result["errors"] == []
    assert result["consistency_status"] == "CONSISTENT"


def test_d5_valid_bundle_passes() -> None:
    source, closeout = chain()
    packet = build_cross_consumer_binding_bundle(
        closeout,
        source,
    )["packet"]

    result = validate_cross_consumer_binding_bundle(
        packet,
        closeout,
        source,
    )

    assert result["ok"] is True
    assert result["errors"] == []


def test_d5_rejects_operator_hash_change() -> None:
    source, closeout, operator, ui, archive = bindings()
    operator["source_sha256"] = "0" * 64

    result = validate_cross_consumer_bindings(
        operator,
        ui,
        archive,
        closeout,
        source,
    )

    assert result["ok"] is False
    assert (
        "CROSS_IDENTITY_MISMATCH_OPERATOR_SOURCE_SHA256"
        in result["errors"]
    )


def test_d5_rejects_ui_correlation_change() -> None:
    source, closeout, operator, ui, archive = bindings()
    ui["correlation_id"] = "changed-correlation"

    result = validate_cross_consumer_bindings(
        operator,
        ui,
        archive,
        closeout,
        source,
    )

    assert result["ok"] is False
    assert (
        "CROSS_IDENTITY_MISMATCH_UI_CORRELATION_ID"
        in result["errors"]
    )


def test_d5_rejects_ui_risk_change() -> None:
    source, closeout, operator, ui, archive = bindings()
    ui["risk_flags"] = []

    result = validate_cross_consumer_bindings(
        operator,
        ui,
        archive,
        closeout,
        source,
    )

    assert result["ok"] is False
    assert (
        "CROSS_CONTENT_MISMATCH_UI_RISK_FLAGS"
        in result["errors"]
    )


def test_d5_rejects_archive_uncertainty_change() -> None:
    source, closeout, operator, ui, archive = bindings()
    archive["uncertainty_states"] = []

    result = validate_cross_consumer_bindings(
        operator,
        ui,
        archive,
        closeout,
        source,
    )

    assert result["ok"] is False
    assert (
        "CROSS_CONTENT_MISMATCH_ARCHIVE_UNCERTAINTY_STATES"
        in result["errors"]
    )


def test_d5_rejects_hidden_ui_risk_section() -> None:
    source, closeout, operator, ui, archive = bindings()

    risk_section = next(
        section
        for section in ui["sections"]
        if section["section_id"] == "RISK_FLAGS"
    )
    risk_section["visibility"] = "HIDDEN"

    result = validate_cross_consumer_bindings(
        operator,
        ui,
        archive,
        closeout,
        source,
    )

    assert result["ok"] is False
    assert (
        "UI_BOUND_SECTION_NOT_VISIBLE_RISK_FLAGS"
        in result["errors"]
    )


def test_d5_rejects_automatic_archive() -> None:
    source, closeout, operator, ui, archive = bindings()
    archive["automatic_archive_allowed"] = True

    result = validate_cross_consumer_bindings(
        operator,
        ui,
        archive,
        closeout,
        source,
    )

    assert result["ok"] is False
    assert (
        "CROSS_UNSAFE_TRUE_ARCHIVE_AUTOMATIC_ARCHIVE_ALLOWED"
        in result["errors"]
    )


def test_d5_is_deterministic_and_does_not_mutate_inputs() -> None:
    source, closeout = chain()
    original_source = deepcopy(source)
    original_closeout = deepcopy(closeout)

    first = build_cross_consumer_binding_bundle(
        closeout,
        source,
    )
    second = build_cross_consumer_binding_bundle(
        closeout,
        source,
    )

    assert first == second
    assert source == original_source
    assert closeout == original_closeout
