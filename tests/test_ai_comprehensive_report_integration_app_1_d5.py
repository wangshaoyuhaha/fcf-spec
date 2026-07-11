from __future__ import annotations

from copy import deepcopy

from apps.ai_comprehensive_report_integration_app_1 import (
    ARCHIVE_CONSUMER_APP_ID,
    ARCHIVE_PACKET_TYPE,
    build_manual_archive_candidate_packet,
    build_operator_review_packet,
    build_registered_source_envelope,
    build_ui_visibility_packet,
    validate_manual_archive_candidate_packet,
)


def source_payload() -> dict[str, object]:
    return {
        "correlation_id": "corr-d5",
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


def source_envelope() -> dict[str, object]:
    return build_registered_source_envelope(
        source_payload=source_payload(),
        source_artifact_ref=(
            "artifacts/ai_comprehensive_report_synthesis/"
            "report-d5.json"
        ),
        source_artifact_version="1.0.0",
        correlation_id="corr-d5",
    )


def chain() -> tuple[
    dict[str, object],
    dict[str, object],
    dict[str, object],
]:
    source = source_envelope()
    review = build_operator_review_packet(source)["packet"]
    ui = build_ui_visibility_packet(review, source)["packet"]

    return source, review, ui


def test_d5_builds_manual_archive_candidate() -> None:
    source, review, ui = chain()

    result = build_manual_archive_candidate_packet(
        ui,
        review,
        source,
    )

    assert result["ok"] is True
    assert result["errors"] == []
    assert result["packet"]["packet_type"] == ARCHIVE_PACKET_TYPE
    assert (
        result["packet"]["consumer_app_id"]
        == ARCHIVE_CONSUMER_APP_ID
    )


def test_d5_preserves_source_identity() -> None:
    source, review, ui = chain()
    packet = build_manual_archive_candidate_packet(
        ui,
        review,
        source,
    )["packet"]

    for field in (
        "source_app_id",
        "source_module",
        "source_artifact_type",
        "source_artifact_ref",
        "source_artifact_version",
        "source_sha256",
        "correlation_id",
    ):
        assert packet[field] == ui[field]


def test_d5_preserves_ui_content_exactly() -> None:
    source, review, ui = chain()
    packet = build_manual_archive_candidate_packet(
        ui,
        review,
        source,
    )["packet"]

    for field in (
        "review_banner",
        "decision_state",
        "sections",
        "visibility_counts",
        "visibility_order",
        "risk_flags",
        "counterevidence",
        "alternative_explanations",
        "uncertainty_states",
    ):
        assert packet[field] == ui[field]
        assert packet[field] is not ui[field]


def test_d5_archive_state_remains_pending() -> None:
    source, review, ui = chain()
    packet = build_manual_archive_candidate_packet(
        ui,
        review,
        source,
    )["packet"]

    assert packet["archive_status"] == "PENDING_MANUAL_ARCHIVE"
    assert (
        packet["archive_handoff_state"]
        == "AWAITING_OPERATOR_ARCHIVE_AUTHORIZATION"
    )
    assert packet["operator_archive_decision"] == "PENDING"
    assert packet["archive_destination"] == "UNASSIGNED"
    assert packet["retention_label"] == "UNASSIGNED"
    assert packet["archive_record_id"] == "UNASSIGNED"


def test_d5_requires_manual_archive_and_review() -> None:
    source, review, ui = chain()
    packet = build_manual_archive_candidate_packet(
        ui,
        review,
        source,
    )["packet"]

    assert packet["operator_review_required"] is True
    assert packet["manual_archive_required"] is True


def test_d5_manual_checklist_is_pending() -> None:
    source, review, ui = chain()
    packet = build_manual_archive_candidate_packet(
        ui,
        review,
        source,
    )["packet"]

    assert len(packet["manual_archive_checklist"]) == 7

    for item in packet["manual_archive_checklist"]:
        assert item["status"] == "PENDING"
        assert item["operator_action_required"] is True
        assert item["automatic_completion_allowed"] is False


def test_d5_blocks_archive_execution_and_writes() -> None:
    source, review, ui = chain()
    packet = build_manual_archive_candidate_packet(
        ui,
        review,
        source,
    )["packet"]

    assert packet["automatic_archive_allowed"] is False
    assert packet["archive_execution_allowed"] is False
    assert packet["archive_write_allowed"] is False
    assert packet["archive_record_creation_allowed"] is False


def test_d5_blocks_mutation_and_runtime_actions() -> None:
    source, review, ui = chain()
    packet = build_manual_archive_candidate_packet(
        ui,
        review,
        source,
    )["packet"]

    assert packet["source_mutation_allowed"] is False
    assert packet["semantic_rewrite_allowed"] is False
    assert packet["visibility_suppression_allowed"] is False
    assert packet["runtime_execution_allowed"] is False
    assert packet["real_execution_allowed"] is False


def test_d5_valid_packet_passes_validation() -> None:
    source, review, ui = chain()
    packet = build_manual_archive_candidate_packet(
        ui,
        review,
        source,
    )["packet"]

    result = validate_manual_archive_candidate_packet(
        packet,
        ui,
        review,
        source,
    )

    assert result["ok"] is True
    assert result["errors"] == []


def test_d5_rejects_invalid_ui_source() -> None:
    source, review, ui = chain()

    risk_section = next(
        section
        for section in ui["sections"]
        if section["section_id"] == "RISK_FLAGS"
    )
    risk_section["visibility"] = "HIDDEN"

    result = build_manual_archive_candidate_packet(
        ui,
        review,
        source,
    )

    assert result["ok"] is False
    assert "UI_SECTION_NOT_VISIBLE_RISK_FLAGS" in result["errors"]


def test_d5_validator_rejects_archived_status() -> None:
    source, review, ui = chain()
    packet = build_manual_archive_candidate_packet(
        ui,
        review,
        source,
    )["packet"]

    packet["archive_status"] = "ARCHIVED"

    result = validate_manual_archive_candidate_packet(
        packet,
        ui,
        review,
        source,
    )

    assert result["ok"] is False
    assert "INVALID_ARCHIVE_STATUS" in result["errors"]


def test_d5_validator_rejects_preassigned_destination() -> None:
    source, review, ui = chain()
    packet = build_manual_archive_candidate_packet(
        ui,
        review,
        source,
    )["packet"]

    packet["archive_destination"] = "automatic/archive/path"

    result = validate_manual_archive_candidate_packet(
        packet,
        ui,
        review,
        source,
    )

    assert result["ok"] is False
    assert "INVALID_ARCHIVE_DESTINATION" in result["errors"]


def test_d5_validator_rejects_content_rewrite() -> None:
    source, review, ui = chain()
    packet = build_manual_archive_candidate_packet(
        ui,
        review,
        source,
    )["packet"]

    packet["risk_flags"] = ["LOW_RISK"]

    result = validate_manual_archive_candidate_packet(
        packet,
        ui,
        review,
        source,
    )

    assert result["ok"] is False
    assert (
        "ARCHIVE_PRESERVATION_MISMATCH_RISK_FLAGS"
        in result["errors"]
    )


def test_d5_validator_rejects_automatic_archive() -> None:
    source, review, ui = chain()
    packet = build_manual_archive_candidate_packet(
        ui,
        review,
        source,
    )["packet"]

    packet["automatic_archive_allowed"] = True

    result = validate_manual_archive_candidate_packet(
        packet,
        ui,
        review,
        source,
    )

    assert result["ok"] is False
    assert "UNSAFE_AUTOMATIC_ARCHIVE_ALLOWED" in result["errors"]


def test_d5_does_not_mutate_inputs() -> None:
    source, review, ui = chain()

    original_source = deepcopy(source)
    original_review = deepcopy(review)
    original_ui = deepcopy(ui)

    build_manual_archive_candidate_packet(
        ui,
        review,
        source,
    )

    assert source == original_source
    assert review == original_review
    assert ui == original_ui
