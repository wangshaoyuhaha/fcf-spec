from dataclasses import FrozenInstanceError, replace
import json

import pytest

from apps.fcp_0085_btc_registered_local_export_validation_runner_app_1.runner import (
    build_reference_result,
)
from apps.fcp_0086_btc_registered_local_export_operator_review_packet_app_1 import (
    build_operator_review_packet,
)
from apps.fcp_0087_btc_registered_local_export_operator_review_receipt_app_1 import (
    REVIEW_DISPOSITIONS,
    BTCLocalExportOperatorReviewReceipt,
    build_reference_receipt,
    render_operator_review_receipt_json,
)


def packet():
    return build_operator_review_packet(
        build_reference_result(),
        packet_id="btc-local-export-review-packet-v1",
        packet_created_at_utc="2026-07-21T00:00:21Z",
    )


def test_d1_requires_exact_typed_packet():
    with pytest.raises(ValueError, match="exact typed FCP-0086 packet"):
        BTCLocalExportOperatorReviewReceipt(
            "btc-local-export-review-receipt-v1",
            object(),  # type: ignore[arg-type]
            "operator-reference-v1",
            "2026-07-21T00:00:22Z",
            "REVIEWED_NO_PROMOTION",
        )


def test_d2_receipt_cannot_precede_packet():
    with pytest.raises(ValueError, match="cannot precede packet evidence"):
        BTCLocalExportOperatorReviewReceipt(
            "btc-local-export-review-receipt-v1",
            packet(),
            "operator-reference-v1",
            "2026-07-21T00:00:20Z",
            "REVIEWED_NO_PROMOTION",
        )


def test_d2_receipt_binds_packet_validation_and_items():
    receipt = build_reference_receipt()
    assert receipt.packet_hash == receipt.review_packet.packet_hash
    assert receipt.validation_result_hash == receipt.review_packet.validation_result_hash
    assert receipt.review_item_hashes == tuple(
        item.item_hash for item in receipt.review_packet.review_items
    )


def test_d3_disposition_vocabulary_is_closed():
    assert REVIEW_DISPOSITIONS == (
        "REVIEWED_NO_PROMOTION",
        "DEFERRED_PENDING_EVIDENCE",
        "ESCALATED_FOR_RESEARCH",
    )
    with pytest.raises(ValueError, match="not registered"):
        replace(build_reference_receipt(), disposition="APPROVED")


def test_d3_every_disposition_remains_non_authorizing():
    baseline = build_reference_receipt()
    for disposition in REVIEW_DISPOSITIONS:
        receipt = replace(baseline, disposition=disposition)
        assert receipt.evidence_approved is False
        assert receipt.evidence_rejected is False
        assert receipt.evidence_promotion_allowed is False
        assert receipt.replay_activation_allowed is False


def test_d4_renderer_is_ascii_canonical_and_path_free():
    receipt = build_reference_receipt()
    rendered = render_operator_review_receipt_json(receipt)
    assert rendered == render_operator_review_receipt_json(receipt)
    assert rendered.endswith("\n")
    rendered.encode("ascii")
    record = json.loads(rendered)
    assert record["receipt_hash"] == receipt.receipt_hash
    for forbidden in ('"file_path":', '"local_path":', '"price":', '"quantity":'):
        assert forbidden not in rendered.lower()


def test_d4_renderer_requires_exact_receipt():
    with pytest.raises(TypeError, match="exact BTCLocalExportOperatorReviewReceipt"):
        render_operator_review_receipt_json(object())  # type: ignore[arg-type]


def test_d5_receipt_cannot_promote_activate_or_act():
    baseline = build_reference_receipt()
    for change in (
        {"evidence_approved": True},
        {"evidence_promotion_allowed": True},
        {"replay_activation_allowed": True},
        {"execution_allowed": True},
    ):
        with pytest.raises(ValueError, match="cannot approve, resolve, promote, activate, or act"):
            replace(baseline, **change)


def test_d5_authority_identities_are_fixed_and_gap_stays_open():
    receipt = build_reference_receipt()
    assert receipt.calculation_authority == "DETERMINISTIC_ENGINE"
    assert receipt.evidence_authority == "REGISTERED_EVIDENCE"
    assert receipt.ai_role == "ADVISORY_ONLY"
    assert receipt.gap_closed is False
    with pytest.raises(ValueError, match="authority identities are immutable"):
        replace(receipt, ai_role="AUTHORITATIVE")


def test_d5_receipt_is_immutable():
    receipt = build_reference_receipt()
    with pytest.raises(FrozenInstanceError):
        receipt.disposition = "CHANGED"  # type: ignore[misc]


def test_d6_receipt_hash_is_deterministic():
    left = build_reference_receipt()
    right = build_reference_receipt()
    assert left.receipt_hash == right.receipt_hash
    assert len(left.receipt_hash) == 64
