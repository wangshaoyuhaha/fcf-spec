from __future__ import annotations

from dataclasses import dataclass, field

from apps.fcp_0017_a_share_trusted_daily_data_substrate_local_calibration_app_1.contracts import (
    canonical_sha256,
    digest,
)
from apps.fcp_0043_a_share_cross_source_operator_delta_review_receipt_app_1 import (
    OperatorDeltaReviewReceipt,
    REVIEW_DISPOSITIONS,
)


@dataclass(frozen=True)
class ReviewDispositionCount:
    disposition: str
    count: int
    count_hash: str = field(init=False)

    def __post_init__(self) -> None:
        if self.disposition not in REVIEW_DISPOSITIONS:
            raise ValueError("ledger disposition is not registered")
        if isinstance(self.count, bool) or not isinstance(self.count, int) or self.count < 0:
            raise ValueError("ledger disposition count must be nonnegative")
        object.__setattr__(
            self,
            "count_hash",
            canonical_sha256(
                {"count": self.count, "disposition": self.disposition}
            ),
        )


@dataclass(frozen=True)
class OperatorReviewReceiptLedger:
    receipts: tuple[OperatorDeltaReviewReceipt, ...]
    disposition_counts: tuple[ReviewDispositionCount, ...]
    review_ids: tuple[str, ...]
    receipt_hashes: tuple[str, ...]
    packet_hashes: tuple[str, ...]
    operator_review_required: bool = True
    evidence_validated: bool = False
    evidence_rejected: bool = False
    severity_assigned: bool = False
    recommendation_generated: bool = False
    threshold_set: bool = False
    source_ranked: bool = False
    source_selected: bool = False
    evidence_replaced: bool = False
    receipt_deleted: bool = False
    gap_closed: bool = False
    ledger_hash: str = field(init=False)

    def __post_init__(self) -> None:
        receipts = tuple(self.receipts)
        if not receipts or any(
            not isinstance(item, OperatorDeltaReviewReceipt) for item in receipts
        ):
            raise ValueError("ledger requires typed FCP-0043 receipts")
        expected_order = tuple(
            sorted(receipts, key=lambda item: (item.reviewed_at_utc, item.review_id))
        )
        if receipts != expected_order:
            raise ValueError("ledger receipts must use stable review order")
        expected_review_ids = tuple(item.review_id for item in receipts)
        if len(set(expected_review_ids)) != len(expected_review_ids):
            raise ValueError("ledger review IDs must be unique")
        expected_receipt_hashes = tuple(item.receipt_hash for item in receipts)
        if len(set(expected_receipt_hashes)) != len(expected_receipt_hashes):
            raise ValueError("ledger receipt hashes must be unique")
        expected_packet_hashes = tuple(item.packet_hash for item in receipts)
        counts = tuple(self.disposition_counts)
        if tuple(item.disposition for item in counts) != REVIEW_DISPOSITIONS:
            raise ValueError("ledger counts must use closed disposition order")
        expected_counts = tuple(
            ReviewDispositionCount(
                disposition=disposition,
                count=sum(item.disposition == disposition for item in receipts),
            )
            for disposition in REVIEW_DISPOSITIONS
        )
        if counts != expected_counts:
            raise ValueError("ledger disposition counts disagree with receipts")
        if tuple(self.review_ids) != expected_review_ids:
            raise ValueError("ledger review IDs disagree with receipts")
        if tuple(self.receipt_hashes) != expected_receipt_hashes:
            raise ValueError("ledger receipt hashes disagree with receipts")
        packet_hashes = tuple(digest(item, "packet_hash") for item in self.packet_hashes)
        if packet_hashes != expected_packet_hashes:
            raise ValueError("ledger packet hashes disagree with receipts")
        if (
            self.operator_review_required is not True
            or self.evidence_validated is not False
            or self.evidence_rejected is not False
            or self.severity_assigned is not False
            or self.recommendation_generated is not False
            or self.threshold_set is not False
            or self.source_ranked is not False
            or self.source_selected is not False
            or self.evidence_replaced is not False
            or self.receipt_deleted is not False
            or self.gap_closed is not False
        ):
            raise ValueError("receipt ledger cannot validate, mutate, select, or close")
        object.__setattr__(self, "receipts", receipts)
        object.__setattr__(self, "disposition_counts", counts)
        object.__setattr__(self, "review_ids", expected_review_ids)
        object.__setattr__(self, "receipt_hashes", expected_receipt_hashes)
        object.__setattr__(self, "packet_hashes", packet_hashes)
        object.__setattr__(
            self,
            "ledger_hash",
            canonical_sha256(
                {
                    "count_hashes": [item.count_hash for item in counts],
                    "packet_hashes": list(packet_hashes),
                    "receipt_hashes": list(expected_receipt_hashes),
                    "review_ids": list(expected_review_ids),
                }
            ),
        )
