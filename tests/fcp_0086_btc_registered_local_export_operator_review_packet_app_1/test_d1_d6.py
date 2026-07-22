from dataclasses import FrozenInstanceError, replace
import json

import pytest

from apps.fcp_0085_btc_registered_local_export_validation_runner_app_1.runner import (
    build_reference_result,
)
from apps.fcp_0086_btc_registered_local_export_operator_review_packet_app_1 import (
    REVIEW_ITEM_IDS,
    BTCLocalExportOperatorReviewItem,
    build_operator_review_packet,
    render_operator_review_packet_json,
)


def packet():
    return build_operator_review_packet(
        build_reference_result(),
        packet_id="btc-local-export-review-packet-v1",
        packet_created_at_utc="2026-07-21T00:00:21Z",
    )


def test_d1_requires_exact_typed_validation_result():
    with pytest.raises(TypeError, match="exact BTCLocalExportValidationResult"):
        build_operator_review_packet(
            object(),
            packet_id="btc-local-export-review-packet-v1",
            packet_created_at_utc="2026-07-21T00:00:21Z",
        )


def test_d1_packet_cannot_precede_validation():
    with pytest.raises(ValueError, match="cannot precede validation"):
        build_operator_review_packet(
            build_reference_result(),
            packet_id="btc-local-export-review-packet-v1",
            packet_created_at_utc="2026-07-21T00:00:19Z",
        )


def test_d2_review_items_use_closed_order_and_remain_undecided():
    result = packet()
    assert tuple(item.item_id for item in result.review_items) == REVIEW_ITEM_IDS
    assert all(item.review_state == "OPERATOR_REVIEW_REQUIRED" for item in result.review_items)
    assert all(item.approved is False and item.rejected is False for item in result.review_items)


def test_d2_unknown_or_decided_review_items_fail_closed():
    digest = "0" * 64
    with pytest.raises(ValueError, match="not registered"):
        BTCLocalExportOperatorReviewItem("unknown-item", digest)
    with pytest.raises(ValueError, match="cannot assign a disposition"):
        BTCLocalExportOperatorReviewItem("source-lineage", digest, approved=True)


def test_d3_packet_is_path_free_and_excludes_market_values():
    rendered = render_operator_review_packet_json(packet())
    lowered = rendered.lower()
    for forbidden in (
        '"file_path":',
        '"local_path":',
        '"price":',
        '"quantity":',
        '"book_levels":',
        '"funding_rate":',
    ):
        assert forbidden not in lowered
    rendered.encode("ascii")


def test_d3_renderer_is_canonical_and_deterministic():
    result = packet()
    rendered = render_operator_review_packet_json(result)
    assert rendered == render_operator_review_packet_json(result)
    assert rendered.endswith("\n")
    assert json.loads(rendered)["packet_hash"] == result.packet_hash


def test_d4_packet_cannot_assign_disposition_or_activate_replay():
    baseline = packet()
    with pytest.raises(ValueError, match="cannot decide, activate, promote, or act"):
        replace(baseline, evidence_approved=True)
    with pytest.raises(ValueError, match="cannot decide, activate, promote, or act"):
        replace(baseline, replay_activation_allowed=True)


def test_d4_packet_is_immutable():
    result = packet()
    with pytest.raises(FrozenInstanceError):
        result.packet_id = "changed"  # type: ignore[misc]


def test_d5_authorities_are_fixed_and_gap_remains_open():
    result = packet()
    assert result.calculation_authority == "DETERMINISTIC_ENGINE"
    assert result.evidence_authority == "REGISTERED_EVIDENCE"
    assert result.ai_role == "ADVISORY_ONLY"
    assert result.operator_review_required is True
    assert result.gap_closed is False
    assert result.provider_selected is False
    assert result.execution_allowed is False


def test_d5_authority_identity_mutation_fails_closed():
    with pytest.raises(ValueError, match="authority identities are immutable"):
        replace(packet(), ai_role="AUTHORITATIVE")


def test_d6_hashes_bind_validation_and_every_review_item():
    result = packet()
    assert result.validation_result_hash == result.validation_result.result_hash
    assert len({item.item_hash for item in result.review_items}) == len(REVIEW_ITEM_IDS)
    assert len(result.packet_hash) == 64
