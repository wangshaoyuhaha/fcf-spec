from __future__ import annotations

from copy import deepcopy

from apps.ai_comprehensive_report_integration_app_1 import (
    CLOSEOUT_PACKET_TYPE,
    build_full_chain_closeout_packet,
    build_registered_source_envelope,
    validate_full_chain_closeout_packet,
)


def source_payload() -> dict[str, object]:
    return {
        "correlation_id": "corr-d6",
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
            "report-d6.json"
        ),
        source_artifact_version="1.0.0",
        correlation_id="corr-d6",
    )


def test_d6_builds_full_chain_closeout_packet() -> None:
    result = build_full_chain_closeout_packet(source_envelope())

    assert result["ok"] is True
    assert result["errors"] == []
    assert result["failed_stage"] is None
    assert result["packet"]["packet_type"] == CLOSEOUT_PACKET_TYPE


def test_d6_records_all_chain_stages() -> None:
    packet = build_full_chain_closeout_packet(
        source_envelope()
    )["packet"]

    assert packet["chain_stage_ids"] == [
        "D1_BOUNDARY_CONTRACT",
        "D2_REGISTERED_SOURCE",
        "D3_OPERATOR_REVIEW",
        "D4_UI_VISIBILITY",
        "D5_MANUAL_ARCHIVE",
        "D6_FULL_CHAIN_CLOSEOUT",
    ]

    for stage in packet["chain_stage_ids"]:
        assert packet["stage_validations"][stage]["ok"] is True


def test_d6_preserves_source_identity() -> None:
    source = source_envelope()
    packet = build_full_chain_closeout_packet(source)["packet"]

    for field in (
        "source_app_id",
        "source_module",
        "source_artifact_type",
        "source_artifact_ref",
        "source_artifact_version",
        "source_sha256",
        "correlation_id",
    ):
        assert packet[field] == source[field]


def test_d6_contains_all_chain_packets() -> None:
    packet = build_full_chain_closeout_packet(
        source_envelope()
    )["packet"]

    assert packet["registered_source"] is not None
    assert packet["operator_review_packet"] is not None
    assert packet["ui_visibility_packet"] is not None
    assert packet["manual_archive_candidate_packet"] is not None


def test_d6_final_state_requires_manual_review() -> None:
    packet = build_full_chain_closeout_packet(
        source_envelope()
    )["packet"]

    assert (
        packet["phase_status"]
        == "D1_D6_COMPLETE_PENDING_MANUAL_MERGE"
    )
    assert packet["final_review_status"] == "REVIEW_REQUIRED"
    assert packet["final_operator_decision"] == "PENDING"
    assert (
        packet["final_archive_status"]
        == "PENDING_MANUAL_ARCHIVE"
    )
    assert (
        packet["merge_readiness"]
        == "READY_FOR_MANUAL_MERGE_REVIEW"
    )


def test_d6_requires_manual_merge_and_archive() -> None:
    packet = build_full_chain_closeout_packet(
        source_envelope()
    )["packet"]

    assert packet["operator_review_required"] is True
    assert packet["manual_merge_review_required"] is True
    assert packet["manual_archive_required"] is True


def test_d6_blocks_automatic_merge_and_archive() -> None:
    packet = build_full_chain_closeout_packet(
        source_envelope()
    )["packet"]

    assert packet["automatic_merge_allowed"] is False
    assert packet["automatic_archive_allowed"] is False
    assert packet["archive_write_allowed"] is False


def test_d6_blocks_runtime_real_release_actions() -> None:
    packet = build_full_chain_closeout_packet(
        source_envelope()
    )["packet"]

    assert packet["source_mutation_allowed"] is False
    assert packet["semantic_rewrite_allowed"] is False
    assert packet["visibility_suppression_allowed"] is False
    assert packet["runtime_execution_allowed"] is False
    assert packet["real_execution_allowed"] is False
    assert packet["tag_allowed"] is False
    assert packet["release_allowed"] is False
    assert packet["deployment_allowed"] is False


def test_d6_closeout_checklist_is_manual() -> None:
    packet = build_full_chain_closeout_packet(
        source_envelope()
    )["packet"]

    assert len(packet["closeout_checklist"]) == 12

    for item in packet["closeout_checklist"]:
        assert (
            item["status"]
            == "PENDING_OPERATOR_CONFIRMATION"
        )
        assert item["operator_action_required"] is True
        assert item["automatic_completion_allowed"] is False


def test_d6_valid_packet_passes_validation() -> None:
    source = source_envelope()
    packet = build_full_chain_closeout_packet(source)["packet"]

    result = validate_full_chain_closeout_packet(
        packet,
        source,
    )

    assert result["ok"] is True
    assert result["errors"] == []


def test_d6_rejects_invalid_source_hash() -> None:
    source = source_envelope()
    source["source_payload"]["risk_flags"] = []

    result = build_full_chain_closeout_packet(source)

    assert result["ok"] is False
    assert result["failed_stage"] == "D2_REGISTERED_SOURCE"
    assert "SOURCE_SHA256_MISMATCH" in result["errors"]


def test_d6_validator_rejects_chain_packet_rewrite() -> None:
    source = source_envelope()
    packet = build_full_chain_closeout_packet(source)["packet"]

    packet["operator_review_packet"]["risk_flags"] = ["LOW_RISK"]

    result = validate_full_chain_closeout_packet(
        packet,
        source,
    )

    assert result["ok"] is False
    assert (
        "CHAIN_MISMATCH_OPERATOR_REVIEW_PACKET"
        in result["errors"]
    )


def test_d6_validator_rejects_automatic_merge() -> None:
    source = source_envelope()
    packet = build_full_chain_closeout_packet(source)["packet"]

    packet["automatic_merge_allowed"] = True

    result = validate_full_chain_closeout_packet(
        packet,
        source,
    )

    assert result["ok"] is False
    assert "UNSAFE_AUTOMATIC_MERGE_ALLOWED" in result["errors"]


def test_d6_validator_rejects_archived_state() -> None:
    source = source_envelope()
    packet = build_full_chain_closeout_packet(source)["packet"]

    packet["final_archive_status"] = "ARCHIVED"

    result = validate_full_chain_closeout_packet(
        packet,
        source,
    )

    assert result["ok"] is False
    assert "INVALID_FINAL_ARCHIVE_STATUS" in result["errors"]


def test_d6_does_not_mutate_source() -> None:
    source = source_envelope()
    original = deepcopy(source)

    build_full_chain_closeout_packet(source)

    assert source == original
