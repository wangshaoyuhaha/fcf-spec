from __future__ import annotations

from copy import deepcopy

from apps.ai_comprehensive_report_consumer_binding_app_1 import (
    ARCHIVE_BINDING_PACKET_TYPE,
    ARCHIVE_CONSUMER_APP_ID,
    build_report_archive_consumer_binding,
    validate_report_archive_consumer_binding,
)
from apps.ai_comprehensive_report_integration_app_1 import (
    build_full_chain_closeout_packet,
    build_registered_source_envelope,
)


def source_envelope() -> dict[str, object]:
    payload = {
        "correlation_id": "corr-consumer-d4",
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
            "consumer-d4.json"
        ),
        source_artifact_version="1.0.0",
        correlation_id="corr-consumer-d4",
    )


def chain() -> tuple[dict[str, object], dict[str, object]]:
    source = source_envelope()
    closeout = build_full_chain_closeout_packet(source)["packet"]

    return source, closeout


def test_d4_builds_archive_binding() -> None:
    source, closeout = chain()

    result = build_report_archive_consumer_binding(
        closeout,
        source,
    )

    assert result["ok"] is True
    assert result["errors"] == []
    assert result["packet"]["packet_type"] == (
        ARCHIVE_BINDING_PACKET_TYPE
    )
    assert result["packet"]["consumer_app_id"] == (
        ARCHIVE_CONSUMER_APP_ID
    )


def test_d4_preserves_identity() -> None:
    source, closeout = chain()
    packet = build_report_archive_consumer_binding(
        closeout,
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
        assert packet[field] == closeout[field]


def test_d4_preserves_archive_candidate_exactly() -> None:
    source, closeout = chain()
    packet = build_report_archive_consumer_binding(
        closeout,
        source,
    )["packet"]

    original = closeout["manual_archive_candidate_packet"]

    assert packet["manual_archive_candidate_packet"] == original
    assert packet["manual_archive_candidate_packet"] is not original


def test_d4_preserves_risk_and_uncertainty() -> None:
    source, closeout = chain()
    packet = build_report_archive_consumer_binding(
        closeout,
        source,
    )["packet"]

    original = closeout["manual_archive_candidate_packet"]

    for field in (
        "risk_flags",
        "counterevidence",
        "alternative_explanations",
        "uncertainty_states",
    ):
        assert packet[field] == original[field]
        assert packet[field] is not original[field]


def test_d4_archive_state_remains_pending() -> None:
    source, closeout = chain()
    packet = build_report_archive_consumer_binding(
        closeout,
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
    assert packet["binding_status"] == "BOUND_READ_ONLY"


def test_d4_checklist_remains_manual() -> None:
    source, closeout = chain()
    packet = build_report_archive_consumer_binding(
        closeout,
        source,
    )["packet"]

    assert packet["manual_archive_checklist"]

    for item in packet["manual_archive_checklist"]:
        assert item["status"] == "PENDING"
        assert item["operator_action_required"] is True
        assert item["automatic_completion_allowed"] is False


def test_d4_blocks_archive_execution_and_write() -> None:
    source, closeout = chain()
    packet = build_report_archive_consumer_binding(
        closeout,
        source,
    )["packet"]

    assert packet["automatic_archive_allowed"] is False
    assert packet["archive_execution_allowed"] is False
    assert packet["archive_write_allowed"] is False
    assert packet["archive_record_creation_allowed"] is False


def test_d4_blocks_runtime_and_mutation() -> None:
    source, closeout = chain()
    packet = build_report_archive_consumer_binding(
        closeout,
        source,
    )["packet"]

    assert packet["source_mutation_allowed"] is False
    assert packet["semantic_rewrite_allowed"] is False
    assert packet["visibility_suppression_allowed"] is False
    assert packet["runtime_model_invocation_allowed"] is False
    assert packet["prompt_execution_allowed"] is False
    assert packet["automatic_routing_allowed"] is False
    assert packet["real_execution_allowed"] is False


def test_d4_valid_binding_passes() -> None:
    source, closeout = chain()
    packet = build_report_archive_consumer_binding(
        closeout,
        source,
    )["packet"]

    result = validate_report_archive_consumer_binding(
        packet,
        closeout,
        source,
    )

    assert result["ok"] is True
    assert result["errors"] == []


def test_d4_rejects_changed_hash() -> None:
    source, closeout = chain()
    packet = build_report_archive_consumer_binding(
        closeout,
        source,
    )["packet"]

    packet["source_sha256"] = "0" * 64

    result = validate_report_archive_consumer_binding(
        packet,
        closeout,
        source,
    )

    assert result["ok"] is False
    assert "IDENTITY_MISMATCH_SOURCE_SHA256" in result["errors"]


def test_d4_rejects_archived_state() -> None:
    source, closeout = chain()
    packet = build_report_archive_consumer_binding(
        closeout,
        source,
    )["packet"]

    packet["archive_status"] = "ARCHIVED"

    result = validate_report_archive_consumer_binding(
        packet,
        closeout,
        source,
    )

    assert result["ok"] is False
    assert "INVALID_ARCHIVE_STATUS" in result["errors"]


def test_d4_rejects_automatic_archive() -> None:
    source, closeout = chain()
    packet = build_report_archive_consumer_binding(
        closeout,
        source,
    )["packet"]

    packet["automatic_archive_allowed"] = True

    result = validate_report_archive_consumer_binding(
        packet,
        closeout,
        source,
    )

    assert result["ok"] is False
    assert "UNSAFE_AUTOMATIC_ARCHIVE_ALLOWED" in result["errors"]


def test_d4_rejects_archive_write() -> None:
    source, closeout = chain()
    packet = build_report_archive_consumer_binding(
        closeout,
        source,
    )["packet"]

    packet["archive_write_allowed"] = True

    result = validate_report_archive_consumer_binding(
        packet,
        closeout,
        source,
    )

    assert result["ok"] is False
    assert "UNSAFE_ARCHIVE_WRITE_ALLOWED" in result["errors"]


def test_d4_does_not_mutate_inputs() -> None:
    source, closeout = chain()
    original_source = deepcopy(source)
    original_closeout = deepcopy(closeout)

    build_report_archive_consumer_binding(
        closeout,
        source,
    )

    assert source == original_source
    assert closeout == original_closeout
