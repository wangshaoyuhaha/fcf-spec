from __future__ import annotations

from copy import deepcopy

from apps.ai_comprehensive_report_consumer_binding_app_1 import (
    BINDING_PACKET_TYPE,
    CONSUMER_APP_ID,
    build_operator_review_consumer_binding,
    validate_operator_review_consumer_binding,
)
from apps.ai_comprehensive_report_integration_app_1 import (
    build_full_chain_closeout_packet,
    build_registered_source_envelope,
)


def source_envelope() -> dict[str, object]:
    payload = {
        "correlation_id": "corr-consumer-d2",
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
            "consumer-d2.json"
        ),
        source_artifact_version="1.0.0",
        correlation_id="corr-consumer-d2",
    )


def chain() -> tuple[dict[str, object], dict[str, object]]:
    source = source_envelope()
    closeout = build_full_chain_closeout_packet(source)["packet"]

    return source, closeout


def test_d2_builds_operator_review_binding() -> None:
    source, closeout = chain()

    result = build_operator_review_consumer_binding(
        closeout,
        source,
    )

    assert result["ok"] is True
    assert result["errors"] == []
    assert result["packet"]["packet_type"] == BINDING_PACKET_TYPE
    assert result["packet"]["consumer_app_id"] == CONSUMER_APP_ID


def test_d2_preserves_identity() -> None:
    source, closeout = chain()
    packet = build_operator_review_consumer_binding(
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


def test_d2_preserves_review_content() -> None:
    source, closeout = chain()
    packet = build_operator_review_consumer_binding(
        closeout,
        source,
    )["packet"]

    review = closeout["operator_review_packet"]

    for field in (
        "source_statements",
        "original_conclusions",
        "risk_flags",
        "counterevidence",
        "alternative_explanations",
        "uncertainty_states",
    ):
        assert packet[field] == review[field]
        assert packet[field] is not review[field]


def test_d2_keeps_review_pending() -> None:
    source, closeout = chain()
    packet = build_operator_review_consumer_binding(
        closeout,
        source,
    )["packet"]

    assert packet["review_status"] == "REVIEW_REQUIRED"
    assert packet["operator_decision"] == "PENDING"
    assert packet["binding_status"] == "BOUND_READ_ONLY"
    assert packet["operator_review_required"] is True


def test_d2_blocks_unsafe_behavior() -> None:
    source, closeout = chain()
    packet = build_operator_review_consumer_binding(
        closeout,
        source,
    )["packet"]

    assert packet["automatic_approval_allowed"] is False
    assert packet["source_mutation_allowed"] is False
    assert packet["semantic_rewrite_allowed"] is False
    assert packet["risk_suppression_allowed"] is False
    assert packet["runtime_model_invocation_allowed"] is False
    assert packet["prompt_execution_allowed"] is False
    assert packet["automatic_routing_allowed"] is False
    assert packet["real_execution_allowed"] is False


def test_d2_valid_binding_passes() -> None:
    source, closeout = chain()
    packet = build_operator_review_consumer_binding(
        closeout,
        source,
    )["packet"]

    result = validate_operator_review_consumer_binding(
        packet,
        closeout,
        source,
    )

    assert result["ok"] is True
    assert result["errors"] == []


def test_d2_rejects_changed_hash() -> None:
    source, closeout = chain()
    packet = build_operator_review_consumer_binding(
        closeout,
        source,
    )["packet"]

    packet["source_sha256"] = "0" * 64

    result = validate_operator_review_consumer_binding(
        packet,
        closeout,
        source,
    )

    assert result["ok"] is False
    assert "IDENTITY_MISMATCH_SOURCE_SHA256" in result["errors"]


def test_d2_rejects_risk_suppression() -> None:
    source, closeout = chain()
    packet = build_operator_review_consumer_binding(
        closeout,
        source,
    )["packet"]

    packet["risk_flags"] = []

    result = validate_operator_review_consumer_binding(
        packet,
        closeout,
        source,
    )

    assert result["ok"] is False
    assert "CONTENT_MISMATCH_RISK_FLAGS" in result["errors"]


def test_d2_rejects_automatic_approval() -> None:
    source, closeout = chain()
    packet = build_operator_review_consumer_binding(
        closeout,
        source,
    )["packet"]

    packet["automatic_approval_allowed"] = True

    result = validate_operator_review_consumer_binding(
        packet,
        closeout,
        source,
    )

    assert result["ok"] is False
    assert "UNSAFE_AUTOMATIC_APPROVAL_ALLOWED" in result["errors"]


def test_d2_does_not_mutate_inputs() -> None:
    source, closeout = chain()
    original_source = deepcopy(source)
    original_closeout = deepcopy(closeout)

    build_operator_review_consumer_binding(
        closeout,
        source,
    )

    assert source == original_source
    assert closeout == original_closeout
