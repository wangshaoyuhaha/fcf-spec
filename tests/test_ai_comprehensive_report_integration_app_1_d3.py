from __future__ import annotations

from copy import deepcopy

from apps.ai_comprehensive_report_integration_app_1 import (
    CONSUMER_APP_ID,
    PACKET_TYPE,
    build_operator_review_packet,
    build_registered_source_envelope,
    canonical_payload_sha256,
    validate_operator_review_packet,
)


def payload() -> dict[str, object]:
    return {
        "correlation_id": "corr-d3",
        "source_statements": ["Statement A"],
        "original_conclusions": ["NO_AUTOMATIC_CONCLUSION"],
        "risk_flags": ["REVIEW_REQUIRED"],
        "counterevidence": ["Counterevidence A"],
        "alternative_explanations": ["Alternative A"],
        "uncertainty_states": ["UNRESOLVED"],
        "operator_review_required": True,
    }


def envelope() -> dict[str, object]:
    return build_registered_source_envelope(
        source_payload=payload(),
        source_artifact_ref=(
            "artifacts/ai_comprehensive_report_synthesis/"
            "report-d3.json"
        ),
        source_artifact_version="1.0.0",
        correlation_id="corr-d3",
    )


def test_d3_builds_review_packet() -> None:
    source = envelope()

    result = build_operator_review_packet(
        source,
        expected_source_artifact_ref=source["source_artifact_ref"],
        expected_source_artifact_version="1.0.0",
        expected_correlation_id="corr-d3",
        expected_source_sha256=source["source_sha256"],
    )

    assert result["ok"] is True
    assert result["errors"] == []
    assert result["packet"]["packet_type"] == PACKET_TYPE
    assert result["packet"]["consumer_app_id"] == CONSUMER_APP_ID


def test_d3_preserves_source_identity() -> None:
    source = envelope()
    packet = build_operator_review_packet(source)["packet"]

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


def test_d3_preserves_governance_content() -> None:
    source = envelope()
    packet = build_operator_review_packet(source)["packet"]

    for field in (
        "source_statements",
        "original_conclusions",
        "risk_flags",
        "counterevidence",
        "alternative_explanations",
        "uncertainty_states",
    ):
        assert packet[field] == source["source_payload"][field]
        assert packet[field] is not source["source_payload"][field]


def test_d3_review_state_is_manual() -> None:
    packet = build_operator_review_packet(envelope())["packet"]

    assert packet["review_status"] == "REVIEW_REQUIRED"
    assert packet["operator_decision"] == "PENDING"
    assert packet["causal_truth"] == "UNDETERMINED"
    assert packet["probability"] == "NOT_ASSIGNED"
    assert packet["winner"] == "NOT_SELECTED"
    assert packet["operator_review_required"] is True


def test_d3_blocks_automatic_behaviors() -> None:
    packet = build_operator_review_packet(envelope())["packet"]

    assert packet["automatic_approval_allowed"] is False
    assert packet["automatic_archive_execution_allowed"] is False
    assert packet["source_mutation_allowed"] is False
    assert packet["runtime_execution_allowed"] is False
    assert packet["real_execution_allowed"] is False


def test_d3_checklist_is_manual_only() -> None:
    packet = build_operator_review_packet(envelope())["packet"]

    assert len(packet["review_checklist"]) == 10

    for item in packet["review_checklist"]:
        assert item["status"] == "PENDING"
        assert item["operator_action_required"] is True
        assert item["automatic_completion_allowed"] is False


def test_d3_action_queue_is_manual_only() -> None:
    packet = build_operator_review_packet(envelope())["packet"]

    assert len(packet["operator_action_queue"]) == 4

    for item in packet["operator_action_queue"]:
        assert item["status"] == "PENDING"
        assert item["operator_action_required"] is True
        assert item["automatic_execution_allowed"] is False


def test_d3_valid_packet_passes_validation() -> None:
    source = envelope()
    packet = build_operator_review_packet(source)["packet"]

    result = validate_operator_review_packet(packet, source)

    assert result["ok"] is True
    assert result["errors"] == []


def test_d3_rejects_missing_counterevidence() -> None:
    source = envelope()
    del source["source_payload"]["counterevidence"]
    source["source_sha256"] = canonical_payload_sha256(
        source["source_payload"]
    )

    result = build_operator_review_packet(source)

    assert result["ok"] is False
    assert "MISSING_SOURCE_FIELD_COUNTEREVIDENCE" in result["errors"]


def test_d3_rejects_correlation_mismatch() -> None:
    source = envelope()
    source["source_payload"]["correlation_id"] = "wrong"
    source["source_sha256"] = canonical_payload_sha256(
        source["source_payload"]
    )

    result = build_operator_review_packet(source)

    assert result["ok"] is False
    assert "SOURCE_CORRELATION_ID_MISMATCH" in result["errors"]


def test_d3_rejects_source_hash_tampering() -> None:
    source = envelope()
    source["source_payload"]["risk_flags"] = []

    result = build_operator_review_packet(source)

    assert result["ok"] is False
    assert "SOURCE_SHA256_MISMATCH" in result["errors"]


def test_d3_validator_rejects_conclusion_replacement() -> None:
    source = envelope()
    packet = build_operator_review_packet(source)["packet"]
    packet["original_conclusions"] = ["REPLACED"]

    result = validate_operator_review_packet(packet, source)

    assert result["ok"] is False
    assert (
        "PRESERVATION_MISMATCH_ORIGINAL_CONCLUSIONS"
        in result["errors"]
    )


def test_d3_validator_rejects_auto_approval() -> None:
    source = envelope()
    packet = build_operator_review_packet(source)["packet"]
    packet["automatic_approval_allowed"] = True

    result = validate_operator_review_packet(packet, source)

    assert result["ok"] is False
    assert "UNSAFE_AUTOMATIC_APPROVAL_ALLOWED" in result["errors"]


def test_d3_does_not_mutate_source() -> None:
    source = envelope()
    original = deepcopy(source)

    build_operator_review_packet(source)

    assert source == original
