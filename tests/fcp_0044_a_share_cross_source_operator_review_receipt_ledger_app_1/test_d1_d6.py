from __future__ import annotations

from dataclasses import replace
from pathlib import Path

import pytest

from apps.fcp_0043_a_share_cross_source_operator_delta_review_receipt_app_1 import (
    record_operator_delta_review,
)
from apps.fcp_0044_a_share_cross_source_operator_review_receipt_ledger_app_1 import (
    build_operator_review_receipt_ledger,
)
from tests.fcp_0042_a_share_cross_source_operator_delta_review_packet_app_1.test_d1_d6 import (
    _packet,
)


def _receipts(tmp_path: Path):
    packet, *_ = _packet(tmp_path)
    return (
        record_operator_delta_review(
            packet,
            review_id="review-002",
            reviewer_reference="operator-local-2",
            reviewed_at_utc="2026-07-21T15:02:00Z",
            disposition="DEFERRED_PENDING_EVIDENCE",
        ),
        record_operator_delta_review(
            packet,
            review_id="review-001",
            reviewer_reference="operator-local-1",
            reviewed_at_utc="2026-07-21T15:01:00Z",
            disposition="REVIEWED_NO_RESOLUTION",
        ),
        record_operator_delta_review(
            packet,
            review_id="review-003",
            reviewer_reference="operator-local-3",
            reviewed_at_utc="2026-07-21T15:03:00Z",
            disposition="ESCALATED_FOR_RESEARCH",
        ),
    )


def test_ledger_preserves_all_receipts_in_stable_order(tmp_path: Path) -> None:
    source = _receipts(tmp_path)
    ledger = build_operator_review_receipt_ledger(source)

    assert ledger.review_ids == ("review-001", "review-002", "review-003")
    assert ledger.receipts == (source[1], source[0], source[2])
    assert ledger.receipt_hashes == tuple(item.receipt_hash for item in ledger.receipts)
    assert ledger.packet_hashes == tuple(item.packet_hash for item in ledger.receipts)


def test_ledger_counts_closed_dispositions(tmp_path: Path) -> None:
    ledger = build_operator_review_receipt_ledger(_receipts(tmp_path))

    assert tuple((item.disposition, item.count) for item in ledger.disposition_counts) == (
        ("REVIEWED_NO_RESOLUTION", 1),
        ("DEFERRED_PENDING_EVIDENCE", 1),
        ("ESCALATED_FOR_RESEARCH", 1),
    )


def test_ledger_is_deterministic_for_input_order(tmp_path: Path) -> None:
    receipts = _receipts(tmp_path)

    assert build_operator_review_receipt_ledger(receipts) == (
        build_operator_review_receipt_ledger(tuple(reversed(receipts)))
    )


def test_ledger_rejects_empty_or_untyped_input() -> None:
    for value in ((), (object(),)):
        with pytest.raises(TypeError, match="typed FCP-0043 evidence"):
            build_operator_review_receipt_ledger(value)


def test_ledger_rejects_duplicate_review_ids(tmp_path: Path) -> None:
    receipts = _receipts(tmp_path)
    duplicate = replace(
        receipts[2],
        review_id=receipts[0].review_id,
        reviewed_at_utc="2026-07-21T15:04:00Z",
    )

    with pytest.raises(ValueError, match="review IDs must be unique"):
        build_operator_review_receipt_ledger((receipts[0], duplicate))


def test_ledger_rejects_duplicate_receipt_hashes(tmp_path: Path) -> None:
    receipt = _receipts(tmp_path)[0]

    with pytest.raises(ValueError, match="review IDs must be unique"):
        build_operator_review_receipt_ledger((receipt, receipt))


def test_ledger_rejects_derived_field_mutation(tmp_path: Path) -> None:
    ledger = build_operator_review_receipt_ledger(_receipts(tmp_path))

    with pytest.raises(ValueError, match="counts disagree"):
        replace(
            ledger,
            disposition_counts=(
                replace(ledger.disposition_counts[0], count=2),
                *ledger.disposition_counts[1:],
            ),
        )
    with pytest.raises(ValueError, match="packet hashes disagree"):
        replace(
            ledger,
            packet_hashes=("0" * 64, *ledger.packet_hashes[1:]),
        )


def test_ledger_authority_boundary_is_immutable(tmp_path: Path) -> None:
    ledger = build_operator_review_receipt_ledger(_receipts(tmp_path))

    for changes in (
        {"operator_review_required": False},
        {"evidence_validated": True},
        {"evidence_rejected": True},
        {"severity_assigned": True},
        {"recommendation_generated": True},
        {"threshold_set": True},
        {"source_ranked": True},
        {"source_selected": True},
        {"evidence_replaced": True},
        {"receipt_deleted": True},
        {"gap_closed": True},
    ):
        with pytest.raises(ValueError, match="cannot validate, mutate, select, or close"):
            replace(ledger, **changes)
