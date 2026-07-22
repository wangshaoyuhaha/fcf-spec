from __future__ import annotations

from apps.fcp_0072_btc_perpetual_paper_stress_trigger_result_operator_review_packet_app_1.contracts import (
    BTCPerpetualPaperStressTriggerResultOperatorReviewPacket,
)

from .contracts import (
    BTCPerpetualPaperStressTriggerResultOperatorReviewReceipt,
)


def record_btc_perpetual_paper_stress_trigger_result_operator_review(
    review_packet: BTCPerpetualPaperStressTriggerResultOperatorReviewPacket,
    *,
    receipt_id: str,
    reviewer_reference: str,
    reviewed_at_utc: str,
    disposition: str,
) -> BTCPerpetualPaperStressTriggerResultOperatorReviewReceipt:
    return BTCPerpetualPaperStressTriggerResultOperatorReviewReceipt(
        receipt_id=receipt_id,
        review_packet=review_packet,
        reviewer_reference=reviewer_reference,
        reviewed_at_utc=reviewed_at_utc,
        disposition=disposition,
    )
