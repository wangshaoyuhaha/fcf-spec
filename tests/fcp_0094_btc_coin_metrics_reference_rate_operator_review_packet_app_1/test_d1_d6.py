from dataclasses import FrozenInstanceError, replace
import json

import pytest

from apps.fcp_0094_btc_coin_metrics_reference_rate_operator_review_packet_app_1 import (
    REVIEW_ITEM_IDS,
    CoinMetricsBTCReferenceRateOperatorReviewItem,
    build_operator_review_packet,
    build_registered_sample_validation_result,
    render_operator_review_packet_json,
)


def _packet():
    return build_operator_review_packet(
        build_registered_sample_validation_result(),
        packet_id="coin-metrics-btc-reference-review-packet-v1",
        packet_created_at_utc="2026-07-23T04:11:00Z",
    )


def test_d1_requires_exact_fcp_0093_result_and_ordered_time() -> None:
    with pytest.raises(TypeError, match="exact CoinMetrics"):
        build_operator_review_packet(
            object(),  # type: ignore[arg-type]
            packet_id="coin-metrics-btc-reference-review-packet-v1",
            packet_created_at_utc="2026-07-23T04:11:00Z",
        )
    with pytest.raises(ValueError, match="cannot precede validation"):
        build_operator_review_packet(
            build_registered_sample_validation_result(),
            packet_id="coin-metrics-btc-reference-review-packet-v1",
            packet_created_at_utc="2026-07-23T04:09:59Z",
        )


def test_d2_review_items_are_closed_ordered_and_undecided() -> None:
    packet = _packet()
    assert tuple(item.item_id for item in packet.review_items) == REVIEW_ITEM_IDS
    assert all(
        item.review_state == "OPERATOR_REVIEW_REQUIRED"
        and item.approved is False
        and item.rejected is False
        for item in packet.review_items
    )
    with pytest.raises(ValueError, match="not registered"):
        CoinMetricsBTCReferenceRateOperatorReviewItem("unknown", "0" * 64)
    with pytest.raises(ValueError, match="cannot assign"):
        CoinMetricsBTCReferenceRateOperatorReviewItem(
            "source-registration",
            "0" * 64,
            approved=True,
        )


def test_d3_packet_is_ascii_path_free_and_value_free() -> None:
    rendered = render_operator_review_packet_json(_packet())
    rendered.encode("ascii")
    for prohibited in (
        '"file_path":',
        '"local_path":',
        '"price":',
        "65995",
        "65969",
        "65983",
        "ReferenceRateUSD",
    ):
        assert prohibited not in rendered


def test_d4_packet_is_deterministic_and_binds_all_evidence() -> None:
    packet = _packet()
    rendered = render_operator_review_packet_json(packet)
    assert rendered == render_operator_review_packet_json(packet)
    assert json.loads(rendered)["packet_hash"] == packet.packet_hash
    assert packet.validation_result_hash == packet.validation_result.result_hash
    assert len({item.item_hash for item in packet.review_items}) == len(
        REVIEW_ITEM_IDS
    )


def test_d5_packet_cannot_decide_promote_authorize_or_act() -> None:
    baseline = _packet()
    for changes in (
        {"disposition_assigned": True},
        {"evidence_approved": True},
        {"evidence_rejected": True},
        {"data_promotion_allowed": True},
        {"mark_or_index_authority": True},
        {"provider_selected": True},
        {"realtime_activated": True},
        {"signal_authority": True},
        {"product_authority": True},
        {"account_state_allowed": True},
        {"order_allowed": True},
        {"execution_allowed": True},
    ):
        with pytest.raises(ValueError, match="cannot decide"):
            replace(baseline, **changes)
    with pytest.raises(ValueError, match="cannot decide"):
        replace(baseline, gap_095_status="CLOSED")


def test_d6_packet_is_immutable_and_authorities_are_fixed() -> None:
    packet = _packet()
    with pytest.raises(FrozenInstanceError):
        packet.packet_id = "changed"  # type: ignore[misc]
    assert packet.acceptance_gate == "BLOCKED_PENDING_OPERATOR_DISPOSITION"
    assert packet.calculation_authority == "DETERMINISTIC_ENGINE"
    assert packet.evidence_authority == "REGISTERED_EVIDENCE"
    assert packet.ai_role == "ADVISORY_ONLY"
    assert packet.operator_review_required is True
    assert packet.disposition_assigned is False
    with pytest.raises(ValueError, match="authority identities"):
        replace(packet, ai_role="AUTHORITATIVE")


def test_renderer_requires_exact_packet_type() -> None:
    with pytest.raises(TypeError, match="exact CoinMetrics"):
        render_operator_review_packet_json(object())  # type: ignore[arg-type]
