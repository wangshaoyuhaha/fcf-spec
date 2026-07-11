from __future__ import annotations

from copy import deepcopy

from apps.ai_comprehensive_report_integration_app_1 import (
    UI_CONSUMER_APP_ID,
    UI_PACKET_TYPE,
    build_operator_review_packet,
    build_registered_source_envelope,
    build_ui_visibility_packet,
    validate_ui_visibility_packet,
)


def source_payload() -> dict[str, object]:
    return {
        "correlation_id": "corr-d4",
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
            "report-d4.json"
        ),
        source_artifact_version="1.0.0",
        correlation_id="corr-d4",
    )


def review_packet() -> dict[str, object]:
    return build_operator_review_packet(
        source_envelope()
    )["packet"]


def test_d4_builds_ui_visibility_packet() -> None:
    source = source_envelope()
    review = build_operator_review_packet(source)["packet"]

    result = build_ui_visibility_packet(review, source)

    assert result["ok"] is True
    assert result["errors"] == []
    assert result["packet"]["packet_type"] == UI_PACKET_TYPE
    assert (
        result["packet"]["consumer_app_id"]
        == UI_CONSUMER_APP_ID
    )


def test_d4_preserves_source_identity() -> None:
    source = source_envelope()
    review = build_operator_review_packet(source)["packet"]
    packet = build_ui_visibility_packet(review, source)["packet"]

    for field in (
        "source_app_id",
        "source_module",
        "source_artifact_type",
        "source_artifact_ref",
        "source_artifact_version",
        "source_sha256",
        "correlation_id",
    ):
        assert packet[field] == review[field]


def test_d4_all_required_sections_are_visible() -> None:
    source = source_envelope()
    review = build_operator_review_packet(source)["packet"]
    packet = build_ui_visibility_packet(review, source)["packet"]

    assert packet["visibility_order"] == [
        "SOURCE_STATEMENTS",
        "ORIGINAL_CONCLUSIONS",
        "RISK_FLAGS",
        "COUNTEREVIDENCE",
        "ALTERNATIVE_EXPLANATIONS",
        "UNCERTAINTY_STATES",
    ]

    for section in packet["sections"]:
        assert section["visibility"] == "VISIBLE"
        assert section["suppressed"] is False
        assert section["semantic_rewrite_allowed"] is False
        assert section["summary_replacement_allowed"] is False
        assert section["operator_review_required"] is True


def test_d4_preserves_section_items_exactly() -> None:
    source = source_envelope()
    review = build_operator_review_packet(source)["packet"]
    packet = build_ui_visibility_packet(review, source)["packet"]

    for section in packet["sections"]:
        field = section["source_field"]

        assert section["items"] == review[field]
        assert section["items"] is not review[field]
        assert section["item_count"] == len(review[field])


def test_d4_preserves_protected_visibility_fields() -> None:
    source = source_envelope()
    review = build_operator_review_packet(source)["packet"]
    packet = build_ui_visibility_packet(review, source)["packet"]

    for field in (
        "risk_flags",
        "counterevidence",
        "alternative_explanations",
        "uncertainty_states",
    ):
        assert packet[field] == review[field]
        assert packet[field] is not review[field]


def test_d4_review_banner_is_visible_and_pending() -> None:
    source = source_envelope()
    review = build_operator_review_packet(source)["packet"]
    packet = build_ui_visibility_packet(review, source)["packet"]

    assert packet["review_banner"] == {
        "visibility": "VISIBLE",
        "review_status": "REVIEW_REQUIRED",
        "operator_decision": "PENDING",
        "operator_review_required": True,
        "automatic_approval_allowed": False,
    }


def test_d4_decision_state_remains_undetermined() -> None:
    source = source_envelope()
    review = build_operator_review_packet(source)["packet"]
    packet = build_ui_visibility_packet(review, source)["packet"]

    assert packet["decision_state"] == {
        "causal_truth": "UNDETERMINED",
        "probability": "NOT_ASSIGNED",
        "winner": "NOT_SELECTED",
        "operator_decision": "PENDING",
    }


def test_d4_visibility_counts_do_not_replace_content() -> None:
    source = source_envelope()
    review = build_operator_review_packet(source)["packet"]
    packet = build_ui_visibility_packet(review, source)["packet"]

    assert packet["visibility_counts"] == {
        "source_statements_count": 2,
        "original_conclusions_count": 1,
        "risk_flags_count": 2,
        "counterevidence_count": 1,
        "alternative_explanations_count": 1,
        "uncertainty_states_count": 1,
    }

    assert packet["summary_replacement_allowed"] is False


def test_d4_blocks_all_suppression_and_automation() -> None:
    source = source_envelope()
    review = build_operator_review_packet(source)["packet"]
    packet = build_ui_visibility_packet(review, source)["packet"]

    assert packet["risk_suppression_allowed"] is False
    assert packet["counterevidence_suppression_allowed"] is False
    assert (
        packet["alternative_explanation_suppression_allowed"]
        is False
    )
    assert packet["uncertainty_suppression_allowed"] is False
    assert packet["semantic_rewrite_allowed"] is False
    assert packet["summary_replacement_allowed"] is False
    assert packet["automatic_decision_allowed"] is False
    assert packet["automatic_approval_allowed"] is False
    assert packet["source_mutation_allowed"] is False
    assert packet["runtime_execution_allowed"] is False
    assert packet["real_execution_allowed"] is False


def test_d4_valid_packet_passes_validation() -> None:
    source = source_envelope()
    review = build_operator_review_packet(source)["packet"]
    packet = build_ui_visibility_packet(review, source)["packet"]

    result = validate_ui_visibility_packet(
        packet,
        review,
        source,
    )

    assert result["ok"] is True
    assert result["errors"] == []


def test_d4_rejects_hidden_risk_section() -> None:
    source = source_envelope()
    review = build_operator_review_packet(source)["packet"]
    packet = build_ui_visibility_packet(review, source)["packet"]

    risk_section = next(
        section
        for section in packet["sections"]
        if section["section_id"] == "RISK_FLAGS"
    )
    risk_section["visibility"] = "HIDDEN"

    result = validate_ui_visibility_packet(
        packet,
        review,
        source,
    )

    assert result["ok"] is False
    assert "UI_SECTION_NOT_VISIBLE_RISK_FLAGS" in result["errors"]


def test_d4_rejects_counterevidence_suppression() -> None:
    source = source_envelope()
    review = build_operator_review_packet(source)["packet"]
    packet = build_ui_visibility_packet(review, source)["packet"]

    packet["counterevidence_suppression_allowed"] = True

    result = validate_ui_visibility_packet(
        packet,
        review,
        source,
    )

    assert result["ok"] is False
    assert (
        "UNSAFE_COUNTEREVIDENCE_SUPPRESSION_ALLOWED"
        in result["errors"]
    )


def test_d4_rejects_ui_semantic_rewrite() -> None:
    source = source_envelope()
    review = build_operator_review_packet(source)["packet"]
    packet = build_ui_visibility_packet(review, source)["packet"]

    packet["risk_flags"] = ["LOW_RISK"]

    result = validate_ui_visibility_packet(
        packet,
        review,
        source,
    )

    assert result["ok"] is False
    assert (
        "PROTECTED_VISIBILITY_MISMATCH_RISK_FLAGS"
        in result["errors"]
    )


def test_d4_rejects_automatic_winner_selection() -> None:
    source = source_envelope()
    review = build_operator_review_packet(source)["packet"]
    packet = build_ui_visibility_packet(review, source)["packet"]

    packet["decision_state"]["winner"] = "SCENARIO_A"

    result = validate_ui_visibility_packet(
        packet,
        review,
        source,
    )

    assert result["ok"] is False
    assert "UNSAFE_DECISION_STATE" in result["errors"]


def test_d4_does_not_mutate_inputs() -> None:
    source = source_envelope()
    review = build_operator_review_packet(source)["packet"]

    original_source = deepcopy(source)
    original_review = deepcopy(review)

    build_ui_visibility_packet(review, source)

    assert source == original_source
    assert review == original_review
