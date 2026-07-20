from __future__ import annotations

from apps.v2_r3_local_event_ingress_foundation_app_1 import (
    BoundedLocalEventIngress,
    LocalEventRights,
)

from .adapter import ProviderNeutralMarketDataAdapter
from .contracts import MarketDataFieldMap, RegisteredMarketDataObservation
from .readiness import (
    MarketDataAdapterReadinessSnapshot,
    evaluate_market_data_adapter_readiness,
)


def build_registered_local_replay_fixture(
    *,
    market: str = "A-SHARE",
) -> tuple[ProviderNeutralMarketDataAdapter, MarketDataAdapterReadinessSnapshot]:
    artifact_id = "registered-local-market-data-fixture"
    rights = LocalEventRights(
        license_id="fcp0009-synthetic-fixture-only",
        permitted_use="synthetic-local-evaluation-only",
        retention_days=1,
    )
    maps = (
        MarketDataFieldMap(
            mapping_id="tick-map-v1",
            market=market,
            observation_kind="TICK",
            registered_artifact_id=artifact_id,
            canonical_to_source={
                "instrument_id": "symbol",
                "event_at": "timestamp",
                "last": "last_price",
                "volume": "volume",
            },
            rights=rights,
        ),
        MarketDataFieldMap(
            mapping_id="minute-map-v1",
            market=market,
            observation_kind="MINUTE_BAR",
            registered_artifact_id=artifact_id,
            canonical_to_source={
                "instrument_id": "symbol",
                "event_at": "timestamp",
                "open": "open_price",
                "high": "high_price",
                "low": "low_price",
                "close": "close_price",
                "volume": "volume",
                "interval": "interval",
            },
            rights=rights,
        ),
        MarketDataFieldMap(
            mapping_id="book-map-v1",
            market=market,
            observation_kind="ORDER_BOOK",
            registered_artifact_id=artifact_id,
            canonical_to_source={
                "instrument_id": "symbol",
                "event_at": "timestamp",
                "bid_price_1": "bid_price_1",
                "bid_size_1": "bid_size_1",
                "ask_price_1": "ask_price_1",
                "ask_size_1": "ask_size_1",
            },
            rights=rights,
        ),
    )
    adapter = ProviderNeutralMarketDataAdapter(
        mappings=maps,
        ingress=BoundedLocalEventIngress(capacity=16, ttl_seconds=3600),
    )
    observations = (
        RegisteredMarketDataObservation(
            observation_id="tick-event-1",
            mapping_id="tick-map-v1",
            source_sequence=1,
            received_at_utc="2026-07-20T06:00:01Z",
            processed_at_utc="2026-07-20T06:00:02Z",
            payload={
                "symbol": "000001.XSHE",
                "timestamp": "2026-07-20T06:00:00Z",
                "last_price": "12.34",
                "volume": "100",
            },
        ),
        RegisteredMarketDataObservation(
            observation_id="minute-event-1",
            mapping_id="minute-map-v1",
            source_sequence=1,
            received_at_utc="2026-07-20T06:00:01Z",
            processed_at_utc="2026-07-20T06:00:02Z",
            payload={
                "symbol": "000001.XSHE",
                "timestamp": "2026-07-20T06:00:00Z",
                "open_price": "12.30",
                "high_price": "12.40",
                "low_price": "12.20",
                "close_price": "12.34",
                "volume": "1000",
                "interval": "1m",
            },
        ),
        RegisteredMarketDataObservation(
            observation_id="book-event-1",
            mapping_id="book-map-v1",
            source_sequence=1,
            received_at_utc="2026-07-20T06:00:01Z",
            processed_at_utc="2026-07-20T06:00:02Z",
            payload={
                "symbol": "000001.XSHE",
                "timestamp": "2026-07-20T06:00:00Z",
                "bid_price_1": "12.33",
                "bid_size_1": "500",
                "ask_price_1": "12.34",
                "ask_size_1": "600",
            },
        ),
    )
    for observation in observations:
        adapter, _, _ = adapter.replay(
            observation,
            as_of_utc="2026-07-20T06:00:03Z",
        )
    snapshot = evaluate_market_data_adapter_readiness(
        adapter,
        market=market,
        as_of_utc="2026-07-20T06:00:03Z",
    )
    return adapter, snapshot
