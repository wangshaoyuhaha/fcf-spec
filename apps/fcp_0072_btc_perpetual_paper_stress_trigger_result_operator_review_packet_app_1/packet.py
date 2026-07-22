from __future__ import annotations

from apps.fcp_0071_btc_perpetual_paper_stress_trigger_result_review_registry_app_1.contracts import (
    BTCPerpetualPaperStressTriggerResultReviewRegistry,
)

from .contracts import (
    BTCPerpetualPaperStressTriggerResultOperatorReviewPacket,
)


def build_btc_perpetual_paper_stress_trigger_result_operator_review_packet(
    review_registry: BTCPerpetualPaperStressTriggerResultReviewRegistry,
    *,
    packet_created_at_utc: str,
    packet_id: str = "btc-perpetual-paper-stress-trigger-result-review-packet-v1",
) -> BTCPerpetualPaperStressTriggerResultOperatorReviewPacket:
    return BTCPerpetualPaperStressTriggerResultOperatorReviewPacket(
        packet_id=packet_id,
        review_registry=review_registry,
        packet_created_at_utc=packet_created_at_utc,
    )
