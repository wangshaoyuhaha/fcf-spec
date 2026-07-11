from __future__ import annotations

from copy import deepcopy

from apps.ai_comprehensive_report_consumer_binding_app_1 import (
    REQUIRED_VISIBLE_SECTION_IDS,
    UI_BINDING_PACKET_TYPE,
    UI_CONSUMER_APP_ID,
    build_ui_consumer_binding,
    validate_ui_consumer_binding,
)
from apps.ai_comprehensive_report_integration_app_1 import (
    build_full_chain_closeout_packet,
    build_registered_source_envelope,
)


def source_envelope() -> dict[str, object]:
    payload = {
        "correlation_id": "corr-consumer-d3",
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
            "consumer-d3.json"
        ),
        source_artifact_version="1.0.0",
        correlation_id="corr-consumer-d3",
    )


def chain() -> tuple[dict[str, object], dict[str, object]]:
    source = source_envelope()
    closeout = build_full_chain_closeout_packet(source)["packet"]

    return source, closeout


def test_d3_builds_ui_binding() -> None:
    source, closeout = chain()

    result = build_ui_consumer_binding(closeout, source)

    assert result["ok"] is True
    assert result["errors"] == []
    assert result["packet"]["packet_type"] == UI_BINDING_PACKET_TYPE
    assert result["packet"]["consumer_app_id"] == UI_CONSUMER_APP_ID


def test_d3_preserves_identity() -> None:
    source, closeout = chain()
    packet = build_ui_consumer_binding(closeout, source)["packet"]

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


def test_d3_preserves_ui_packet_exactly() -> None:
    source, closeout = chain()
    packet = build_ui_consumer_binding(closeout, source)["packet"]
    original = closeout["ui_visibility_packet"]

    assert packet["ui_visibility_packet"] == original
    assert packet["ui_visibility_packet"] is not original


def test_d3_all_required_sections_visible() -> None:
    source, closeout = chain()
    packet = build_ui_consumer_binding(closeout, source)["packet"]

    sections = {
        section["section_id"]: section
        for section in packet["sections"]
    }

    assert tuple(packet["visibility_order"]) == (
        REQUIRED_VISIBLE_SECTION_IDS
    )

    for section_id in REQUIRED_VISIBLE_SECTION_IDS:
        assert sections[section_id]["visibility"] == "VISIBLE"


def test_d3_preserves_risk_and_uncertainty() -> None:
    source, closeout = chain()
    packet = build_ui_consumer_binding(closeout, source)["packet"]
    ui = closeout["ui_visibility_packet"]

    for field in (
        "risk_flags",
        "counterevidence",
        "alternative_explanations",
        "uncertainty_states",
    ):
        assert packet[field] == ui[field]
        assert packet[field] is not ui[field]


def test_d3_keeps_decision_pending() -> None:
    source, closeout = chain()
    packet = build_ui_consumer_binding(closeout, source)["packet"]

    assert packet["display_status"] == "VISIBLE_READ_ONLY"
    assert packet["review_status"] == "REVIEW_REQUIRED"
    assert packet["operator_decision"] == "PENDING"
    assert packet["binding_status"] == "BOUND_READ_ONLY"
    assert packet["operator_review_required"] is True


def test_d3_blocks_unsafe_behavior() -> None:
    source, closeout = chain()
    packet = build_ui_consumer_binding(closeout, source)["packet"]

    assert packet["summary_replacement_allowed"] is False
    assert packet["visibility_suppression_allowed"] is False
    assert packet["semantic_rewrite_allowed"] is False
    assert packet["source_mutation_allowed"] is False
    assert packet["automatic_approval_allowed"] is False
    assert packet["runtime_model_invocation_allowed"] is False
    assert packet["prompt_execution_allowed"] is False
    assert packet["automatic_routing_allowed"] is False
    assert packet["real_execution_allowed"] is False


def test_d3_valid_binding_passes() -> None:
    source, closeout = chain()
    packet = build_ui_consumer_binding(closeout, source)["packet"]

    result = validate_ui_consumer_binding(
        packet,
        closeout,
        source,
    )

    assert result["ok"] is True
    assert result["errors"] == []


def test_d3_rejects_changed_hash() -> None:
    source, closeout = chain()
    packet = build_ui_consumer_binding(closeout, source)["packet"]
    packet["source_sha256"] = "0" * 64

    result = validate_ui_consumer_binding(
        packet,
        closeout,
        source,
    )

    assert result["ok"] is False
    assert "IDENTITY_MISMATCH_SOURCE_SHA256" in result["errors"]


def test_d3_rejects_hidden_risk_section() -> None:
    source, closeout = chain()
    packet = build_ui_consumer_binding(closeout, source)["packet"]

    risk_section = next(
        section
        for section in packet["sections"]
        if section["section_id"] == "RISK_FLAGS"
    )
    risk_section["visibility"] = "HIDDEN"

    result = validate_ui_consumer_binding(
        packet,
        closeout,
        source,
    )

    assert result["ok"] is False
    assert "UI_CONTENT_MISMATCH_SECTIONS" in result["errors"]
    assert "BOUND_SECTION_NOT_VISIBLE_RISK_FLAGS" in result["errors"]


def test_d3_rejects_risk_suppression_flag() -> None:
    source, closeout = chain()
    packet = build_ui_consumer_binding(closeout, source)["packet"]
    packet["visibility_suppression_allowed"] = True

    result = validate_ui_consumer_binding(
        packet,
        closeout,
        source,
    )

    assert result["ok"] is False
    assert (
        "UNSAFE_VISIBILITY_SUPPRESSION_ALLOWED"
        in result["errors"]
    )


def test_d3_does_not_mutate_inputs() -> None:
    source, closeout = chain()
    original_source = deepcopy(source)
    original_closeout = deepcopy(closeout)

    build_ui_consumer_binding(closeout, source)

    assert source == original_source
    assert closeout == original_closeout
