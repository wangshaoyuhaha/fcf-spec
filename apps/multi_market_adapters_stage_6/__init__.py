"""Deterministic read-only Stage 6 market adapters."""

from .acceptance import MultiMarketStage6Acceptance, build_stage6_acceptance
from .adapters import (
    MARKET_ADAPTER_DEFINITIONS,
    MarketAdapterDefinition,
    MultiMarketAdapterService,
)
from .boundary import (
    MULTI_MARKET_ADAPTER_BOUNDARY,
    MultiMarketAdapterBoundary,
)
from .contracts import (
    AdapterRecordFinding,
    AdapterStatus,
    FindingStatus,
    MarketAdapterId,
    MarketAdapterOutcome,
    MarketAdapterRequest,
    MarketAdapterReviewPacket,
    MarketRuleProfile,
    freeze,
    thaw,
)

__all__ = [
    "AdapterRecordFinding",
    "AdapterStatus",
    "FindingStatus",
    "MARKET_ADAPTER_DEFINITIONS",
    "MULTI_MARKET_ADAPTER_BOUNDARY",
    "MarketAdapterDefinition",
    "MarketAdapterId",
    "MarketAdapterOutcome",
    "MarketAdapterRequest",
    "MarketAdapterReviewPacket",
    "MarketRuleProfile",
    "MultiMarketAdapterBoundary",
    "MultiMarketAdapterService",
    "MultiMarketStage6Acceptance",
    "build_stage6_acceptance",
    "freeze",
    "thaw",
]
