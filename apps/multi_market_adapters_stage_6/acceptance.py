from __future__ import annotations

from dataclasses import dataclass

from .adapters import MARKET_ADAPTER_DEFINITIONS
from .boundary import MULTI_MARKET_ADAPTER_BOUNDARY
from .contracts import (
    AdapterStatus,
    MarketAdapterId,
    MarketAdapterOutcome,
    MarketAdapterReviewPacket,
)


@dataclass(frozen=True)
class MultiMarketStage6Acceptance:
    status: str
    adapter_ids: tuple[str, ...]
    outcome_statuses: tuple[str, ...]
    operator_review_required: bool = True
    automatic_activation_allowed: bool = False


def build_stage6_acceptance(
    outcomes: tuple[MarketAdapterOutcome, ...],
    packets: tuple[MarketAdapterReviewPacket, ...],
) -> MultiMarketStage6Acceptance:
    expected = tuple(item.value for item in MarketAdapterId)
    definitions = tuple(item.value for item in MARKET_ADAPTER_DEFINITIONS)
    actual = tuple(item.adapter_id.value for item in outcomes)
    packet_ids = tuple(str(item.payload["adapter_id"]) for item in packets)
    if definitions != expected:
        raise ValueError("market adapter registry is incomplete or out of order")
    if actual != expected or packet_ids != expected:
        raise ValueError("acceptance requires all six ordered adapters")
    if any(item.status is AdapterStatus.BLOCKED for item in outcomes):
        raise ValueError("blocked adapter outcome cannot pass acceptance")
    if any(
        item.payload["operator_review_required"] is not True
        or item.payload["automatic_activation_allowed"] is not False
        for item in packets
    ):
        raise ValueError("review packet boundary failed")
    if (
        not MULTI_MARKET_ADAPTER_BOUNDARY.registered_artifact_only
        or not MULTI_MARKET_ADAPTER_BOUNDARY.read_only
        or MULTI_MARKET_ADAPTER_BOUNDARY.real_execution_allowed
    ):
        raise ValueError("multi-market acceptance boundary failed")
    return MultiMarketStage6Acceptance(
        status="PASS",
        adapter_ids=actual,
        outcome_statuses=tuple(item.status.value for item in outcomes),
    )
