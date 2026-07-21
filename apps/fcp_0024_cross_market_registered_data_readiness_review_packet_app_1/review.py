from __future__ import annotations

from apps.fcp_0021_a_share_cross_source_quality_reconciliation_app_1 import (
    AShareCrossSourceReconciliationResult,
)
from apps.fcp_0023_btc_cross_source_venue_quality_reconciliation_app_1 import (
    BTCCrossSourceReconciliationResult,
)

from .contracts import CrossMarketDataReadinessPacket, MarketDataReadinessRow


def _row(market, result):
    return MarketDataReadinessRow(
        market=market,
        reconciliation_result_hash=result.result_hash,
        dataset_hashes=result.dataset_hashes,
        dataset_ids=result.dataset_ids,
        quality_state=result.quality_state,
        blocking_finding_count=sum(item.severity == "BLOCK" for item in result.findings),
        warning_finding_count=sum(item.severity == "WARN" for item in result.findings),
        union_key_count=result.union_key_count,
        overlap_key_count=result.overlap_key_count,
        readiness_state=("READY_FOR_OPERATOR_REVIEW" if result.quality_state == "CONSISTENT" else "QUARANTINE_REVIEW_REQUIRED"),
    )


def build_cross_market_data_readiness_review_packet(a_share_result, btc_result, *, as_of_utc):
    if not isinstance(a_share_result, AShareCrossSourceReconciliationResult):
        raise TypeError("a_share_result must be typed A-share reconciliation evidence")
    if not isinstance(btc_result, BTCCrossSourceReconciliationResult):
        raise TypeError("btc_result must be typed BTC reconciliation evidence")
    rows = (_row("A_SHARE", a_share_result), _row("BTC", btc_result))
    return CrossMarketDataReadinessPacket(
        rows=rows,
        as_of_utc=as_of_utc,
        aggregate_state=("READY_FOR_OPERATOR_REVIEW" if all(item.readiness_state == "READY_FOR_OPERATOR_REVIEW" for item in rows) else "QUARANTINE_REVIEW_REQUIRED"),
    )
