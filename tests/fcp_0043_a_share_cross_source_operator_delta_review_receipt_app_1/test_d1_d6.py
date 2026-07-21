from __future__ import annotations

from dataclasses import replace
from pathlib import Path

import pytest

from apps.fcp_0043_a_share_cross_source_operator_delta_review_receipt_app_1 import (
    REVIEW_DISPOSITIONS,
    record_operator_delta_review,
)
from tests.fcp_0042_a_share_cross_source_operator_delta_review_packet_app_1.test_d1_d6 import (
    _packet,
)


def _receipt(tmp_path: Path, **changes: object):
    packet, *_ = _packet(tmp_path, **changes)
    receipt = record_operator_delta_review(
        packet,
        review_id="review-20260721-001",
        reviewer_reference="operator-local-1",
        reviewed_at_utc="2026-07-21T15:00:00Z",
        disposition="REVIEWED_NO_RESOLUTION",
    )
    return receipt, packet


def test_receipt_binds_exact_packet_and_lineage(tmp_path: Path) -> None:
    receipt, packet = _receipt(tmp_path)

    assert receipt.packet_hash == packet.packet_hash
    assert receipt.ledger_hash == packet.ledger_hash
    assert receipt.packet_review_state == packet.review_state
    assert receipt.finding_codes == packet.finding_codes
    assert receipt.field_fact_hashes == tuple(
        item.fact_hash for item in packet.field_facts
    )


@pytest.mark.parametrize("disposition", REVIEW_DISPOSITIONS)
def test_closed_nondecisional_dispositions(tmp_path: Path, disposition: str) -> None:
    packet, *_ = _packet(tmp_path)
    receipt = record_operator_delta_review(
        packet,
        review_id=f"review-{disposition.lower()}",
        reviewer_reference="operator-local-1",
        reviewed_at_utc="2026-07-21T15:00:00Z",
        disposition=disposition,
    )

    assert receipt.disposition == disposition
    assert receipt.operator_review_completed is True
    assert receipt.evidence_validated is False
    assert receipt.source_selected is False
    assert receipt.gap_closed is False


def test_receipt_is_deterministic(tmp_path: Path) -> None:
    first, packet = _receipt(tmp_path)

    assert first == record_operator_delta_review(
        packet,
        review_id="review-20260721-001",
        reviewer_reference="operator-local-1",
        reviewed_at_utc="2026-07-21T15:00:00Z",
        disposition="REVIEWED_NO_RESOLUTION",
    )


def test_receipt_rejects_unsafe_identifiers_and_clock(tmp_path: Path) -> None:
    packet, *_ = _packet(tmp_path)
    base = {
        "packet": packet,
        "review_id": "review-1",
        "reviewer_reference": "operator-1",
        "reviewed_at_utc": "2026-07-21T15:00:00Z",
        "disposition": "REVIEWED_NO_RESOLUTION",
    }
    for name, value, message in (
        ("review_id", "review has spaces", "safe identifier"),
        ("reviewer_reference", "operator has spaces", "safe identifier"),
        ("reviewed_at_utc", "2026-07-21", "ISO UTC timestamp"),
    ):
        with pytest.raises(ValueError, match=message):
            record_operator_delta_review(**{**base, name: value})


def test_receipt_rejects_unregistered_disposition(tmp_path: Path) -> None:
    packet, *_ = _packet(tmp_path)

    with pytest.raises(ValueError, match="disposition is not registered"):
        record_operator_delta_review(
            packet,
            review_id="review-1",
            reviewer_reference="operator-1",
            reviewed_at_utc="2026-07-21T15:00:00Z",
            disposition="SOURCE_ACCEPTED",
        )


def test_receipt_requires_typed_packet() -> None:
    with pytest.raises(TypeError, match="typed FCP-0042 evidence"):
        record_operator_delta_review(
            object(),
            review_id="review-1",
            reviewer_reference="operator-1",
            reviewed_at_utc="2026-07-21T15:00:00Z",
            disposition="REVIEWED_NO_RESOLUTION",
        )


def test_receipt_rejects_packet_lineage_mutation(tmp_path: Path) -> None:
    receipt, _ = _receipt(tmp_path)

    with pytest.raises(ValueError, match="closed packet order"):
        replace(receipt, finding_codes=tuple(reversed(receipt.finding_codes)))
    with pytest.raises(ValueError, match="unique field fact hashes"):
        replace(receipt, field_fact_hashes=(receipt.field_fact_hashes[0],) * 2)


def test_receipt_authority_boundary_is_immutable(tmp_path: Path) -> None:
    receipt, _ = _receipt(tmp_path)

    for changes in (
        {"operator_review_completed": False},
        {"evidence_validated": True},
        {"evidence_rejected": True},
        {"severity_assigned": True},
        {"recommendation_generated": True},
        {"threshold_set": True},
        {"source_ranked": True},
        {"source_selected": True},
        {"evidence_replaced": True},
        {"gap_closed": True},
    ):
        with pytest.raises(ValueError, match="cannot validate, decide, select, or close"):
            replace(receipt, **changes)
