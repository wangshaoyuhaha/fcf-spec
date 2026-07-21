from __future__ import annotations

from apps.fcp_0043_a_share_cross_source_operator_delta_review_receipt_app_1 import (
    OperatorDeltaReviewReceipt,
    REVIEW_DISPOSITIONS,
)

from .contracts import OperatorReviewReceiptLedger, ReviewDispositionCount


def build_operator_review_receipt_ledger(
    receipts: tuple[OperatorDeltaReviewReceipt, ...],
) -> OperatorReviewReceiptLedger:
    items = tuple(receipts)
    if not items or any(not isinstance(item, OperatorDeltaReviewReceipt) for item in items):
        raise TypeError("receipts must be typed FCP-0043 evidence")
    ordered = tuple(sorted(items, key=lambda item: (item.reviewed_at_utc, item.review_id)))
    return OperatorReviewReceiptLedger(
        receipts=ordered,
        disposition_counts=tuple(
            ReviewDispositionCount(
                disposition=disposition,
                count=sum(item.disposition == disposition for item in ordered),
            )
            for disposition in REVIEW_DISPOSITIONS
        ),
        review_ids=tuple(item.review_id for item in ordered),
        receipt_hashes=tuple(item.receipt_hash for item in ordered),
        packet_hashes=tuple(item.packet_hash for item in ordered),
    )
