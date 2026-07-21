from __future__ import annotations

from apps.fcp_0042_a_share_cross_source_operator_delta_review_packet_app_1 import (
    CrossSourceOperatorDeltaReviewPacket,
)

from .contracts import OperatorDeltaReviewReceipt


def record_operator_delta_review(
    packet: CrossSourceOperatorDeltaReviewPacket,
    *,
    review_id: str,
    reviewer_reference: str,
    reviewed_at_utc: str,
    disposition: str,
) -> OperatorDeltaReviewReceipt:
    if not isinstance(packet, CrossSourceOperatorDeltaReviewPacket):
        raise TypeError("packet must be typed FCP-0042 evidence")
    return OperatorDeltaReviewReceipt(
        packet_hash=packet.packet_hash,
        ledger_hash=packet.ledger_hash,
        review_id=review_id,
        reviewer_reference=reviewer_reference,
        reviewed_at_utc=reviewed_at_utc,
        disposition=disposition,
        packet_review_state=packet.review_state,
        finding_codes=packet.finding_codes,
        field_fact_hashes=tuple(item.fact_hash for item in packet.field_facts),
    )
