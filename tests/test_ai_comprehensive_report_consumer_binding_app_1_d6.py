from __future__ import annotations

from copy import deepcopy

from apps.ai_comprehensive_report_consumer_binding_app_1 import (
    CHECKED_CONSUMERS,
    CLOSEOUT_PACKET_TYPE,
    COMPLETED_STAGES,
    build_consumer_binding_full_chain_closeout,
    validate_consumer_binding_full_chain_closeout,
)
from apps.ai_comprehensive_report_integration_app_1 import (
    build_registered_source_envelope,
)


def source_envelope() -> dict[str, object]:
    payload = {
        "correlation_id": "corr-consumer-d6",
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
            "consumer-d6.json"
        ),
        source_artifact_version="1.0.0",
        correlation_id="corr-consumer-d6",
    )


def closeout() -> tuple[
    dict[str, object],
    dict[str, object],
]:
    source = source_envelope()
    result = build_consumer_binding_full_chain_closeout(source)

    return source, result["packet"]


def test_d6_builds_complete_closeout() -> None:
    source = source_envelope()

    result = build_consumer_binding_full_chain_closeout(source)

    assert result["ok"] is True
    assert result["errors"] == []
    assert result["closeout_status"] == "COMPLETE_VALIDATED"
    assert result["packet"]["packet_type"] == CLOSEOUT_PACKET_TYPE


def test_d6_records_all_completed_stages() -> None:
    source, packet = closeout()

    assert tuple(packet["completed_stages"]) == COMPLETED_STAGES
    assert len(packet["completed_stages"]) == 6


def test_d6_records_all_consumers() -> None:
    source, packet = closeout()

    assert tuple(packet["completed_consumers"]) == CHECKED_CONSUMERS


def test_d6_preserves_identity() -> None:
    source, packet = closeout()
    integration = packet["integration_closeout_packet"]

    for field, value in packet["identity"].items():
        assert value == integration[field]


def test_d6_contains_validated_nested_chain() -> None:
    source, packet = closeout()

    assert packet["integration_closeout_packet"]
    assert packet["cross_consumer_bundle"]
    assert (
        packet["cross_consumer_bundle"]["consistency_status"]
        == "CONSISTENT"
    )


def test_d6_final_states_remain_pending() -> None:
    source, packet = closeout()

    assert packet["closeout_status"] == "COMPLETE_VALIDATED"
    assert packet["consistency_status"] == "CONSISTENT"
    assert packet["operator_review_status"] == "REVIEW_REQUIRED"
    assert packet["operator_decision"] == "PENDING"
    assert packet["archive_status"] == "PENDING_MANUAL_ARCHIVE"
    assert packet["operator_archive_decision"] == "PENDING"
    assert packet["binding_status"] == "BOUND_READ_ONLY"


def test_d6_blocks_unsafe_actions() -> None:
    source, packet = closeout()

    assert packet["automatic_approval_allowed"] is False
    assert packet["automatic_archive_allowed"] is False
    assert packet["archive_execution_allowed"] is False
    assert packet["archive_write_allowed"] is False
    assert packet["archive_record_creation_allowed"] is False
    assert packet["source_mutation_allowed"] is False
    assert packet["semantic_rewrite_allowed"] is False
    assert packet["visibility_suppression_allowed"] is False
    assert packet["runtime_model_invocation_allowed"] is False
    assert packet["prompt_execution_allowed"] is False
    assert packet["automatic_routing_allowed"] is False
    assert packet["real_execution_allowed"] is False


def test_d6_blocks_release_actions() -> None:
    source, packet = closeout()

    assert packet["tag_allowed"] is False
    assert packet["release_allowed"] is False
    assert packet["deployment_allowed"] is False


def test_d6_valid_closeout_passes() -> None:
    source, packet = closeout()

    result = validate_consumer_binding_full_chain_closeout(
        packet,
        source,
    )

    assert result["ok"] is True
    assert result["errors"] == []
    assert result["closeout_status"] == "COMPLETE_VALIDATED"


def test_d6_rejects_identity_hash_change() -> None:
    source, packet = closeout()
    packet["identity"]["source_sha256"] = "0" * 64

    result = validate_consumer_binding_full_chain_closeout(
        packet,
        source,
    )

    assert result["ok"] is False
    assert "IDENTITY_MISMATCH_SOURCE_SHA256" in result["errors"]


def test_d6_rejects_nested_risk_suppression() -> None:
    source, packet = closeout()

    packet[
        "cross_consumer_bundle"
    ][
        "operator_review_binding"
    ][
        "risk_flags"
    ] = []

    result = validate_consumer_binding_full_chain_closeout(
        packet,
        source,
    )

    assert result["ok"] is False
    assert any(
        error.startswith("BUNDLE_")
        for error in result["errors"]
    )


def test_d6_rejects_automatic_archive() -> None:
    source, packet = closeout()
    packet["automatic_archive_allowed"] = True

    result = validate_consumer_binding_full_chain_closeout(
        packet,
        source,
    )

    assert result["ok"] is False
    assert "UNSAFE_AUTOMATIC_ARCHIVE_ALLOWED" in result["errors"]


def test_d6_rejects_invalid_closeout_state() -> None:
    source, packet = closeout()
    packet["closeout_status"] = "INCOMPLETE"

    result = validate_consumer_binding_full_chain_closeout(
        packet,
        source,
    )

    assert result["ok"] is False
    assert "INVALID_CLOSEOUT_STATUS" in result["errors"]


def test_d6_is_deterministic_and_does_not_mutate_source() -> None:
    source = source_envelope()
    original = deepcopy(source)

    first = build_consumer_binding_full_chain_closeout(source)
    second = build_consumer_binding_full_chain_closeout(source)

    assert first == second
    assert source == original
