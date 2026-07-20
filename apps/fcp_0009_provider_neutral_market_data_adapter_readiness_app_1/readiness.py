from __future__ import annotations

from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Mapping

from apps.v2_r24_local_multi_clock_event_state_foundation_app_1 import (
    resolve_multi_clock_event_state,
)
from apps.v2_r3_local_event_ingress_foundation_app_1.contracts import instant, utc

from .adapter import ProviderNeutralMarketDataAdapter
from .contracts import OBSERVATION_KINDS, canonical_sha256


@dataclass(frozen=True)
class MarketDataAdapterReadinessSnapshot:
    market: str
    evaluated_at_utc: str
    mapping_coverage: Mapping[str, str]
    observation_coverage: Mapping[str, str]
    event_count: int
    stream_count: int
    last_sequences: Mapping[str, int]
    heartbeat_age_seconds: int | None
    max_transport_latency_ms: int | None
    clock_state: str
    clock_snapshot_hash: str
    local_replay_state: str
    external_activation_state: str
    entitlement_state: str
    retention_state: str
    provider_selection_state: str
    degradation_codes: tuple[str, ...]
    operator_review_required: bool = True
    snapshot_hash: str = field(init=False)

    def __post_init__(self) -> None:
        if self.local_replay_state not in {
            "READY_FOR_LOCAL_REPLAY",
            "DEGRADED",
            "BLOCKED",
        }:
            raise ValueError("invalid local replay state")
        if (
            self.external_activation_state != "BLOCKED"
            or self.entitlement_state != "UNRESOLVED"
            or self.retention_state != "UNRESOLVED"
            or self.provider_selection_state != "UNSELECTED"
            or self.operator_review_required is not True
        ):
            raise ValueError("readiness snapshot exceeded FCP-0009 authority")
        mapping = MappingProxyType(dict(sorted(self.mapping_coverage.items())))
        observations = MappingProxyType(dict(sorted(self.observation_coverage.items())))
        sequences = MappingProxyType(dict(sorted(self.last_sequences.items())))
        object.__setattr__(self, "mapping_coverage", mapping)
        object.__setattr__(self, "observation_coverage", observations)
        object.__setattr__(self, "last_sequences", sequences)
        payload = {
            "clock_snapshot_hash": self.clock_snapshot_hash,
            "clock_state": self.clock_state,
            "degradation_codes": self.degradation_codes,
            "entitlement_state": self.entitlement_state,
            "evaluated_at_utc": self.evaluated_at_utc,
            "event_count": self.event_count,
            "external_activation_state": self.external_activation_state,
            "heartbeat_age_seconds": self.heartbeat_age_seconds,
            "last_sequences": dict(sequences),
            "local_replay_state": self.local_replay_state,
            "mapping_coverage": dict(mapping),
            "market": self.market,
            "max_transport_latency_ms": self.max_transport_latency_ms,
            "observation_coverage": dict(observations),
            "provider_selection_state": self.provider_selection_state,
            "retention_state": self.retention_state,
            "stream_count": self.stream_count,
        }
        object.__setattr__(self, "snapshot_hash", canonical_sha256(payload))


def evaluate_market_data_adapter_readiness(
    adapter: ProviderNeutralMarketDataAdapter,
    *,
    market: str,
    as_of_utc: str,
    heartbeat_timeout_seconds: int = 120,
    clock_horizon: str = "INTRADAY",
) -> MarketDataAdapterReadinessSnapshot:
    if heartbeat_timeout_seconds <= 0:
        raise ValueError("heartbeat_timeout_seconds must be positive")
    evaluated = utc(as_of_utc, "as_of_utc")
    mappings = tuple(item for item in adapter.mappings if item.market == market)
    events = tuple(
        event
        for event in adapter.ingress.events
        if event.stream_id.startswith(f"market:{market}:")
    )
    mapped_kinds = {item.observation_kind for item in mappings}
    observed_kinds = {
        event.event_type.removeprefix("MARKET_DATA_") for event in events
    }
    mapping_coverage = {
        kind: "REGISTERED" if kind in mapped_kinds else "MISSING"
        for kind in OBSERVATION_KINDS
    }
    observation_coverage = {
        kind: "OBSERVED" if kind in observed_kinds else "MISSING"
        for kind in OBSERVATION_KINDS
    }
    if events:
        latest_received = max(instant(event.received_at_utc) for event in events)
        heartbeat_age = int((instant(evaluated) - latest_received).total_seconds())
        if heartbeat_age < 0:
            raise ValueError("readiness evaluation cannot precede reception")
        latencies = tuple(
            int(
                (instant(event.received_at_utc) - instant(event.event_at_utc)).total_seconds()
                * 1000
            )
            for event in events
        )
        max_latency = max(latencies)
    else:
        heartbeat_age = None
        max_latency = None
    clock = resolve_multi_clock_event_state(
        adapter.clock_registry,
        market=market,
        horizon=clock_horizon,
        observed_at_utc=evaluated,
        as_of_utc=evaluated,
    )
    degradation: list[str] = []
    if len(mapped_kinds) != len(OBSERVATION_KINDS):
        degradation.append("INCOMPLETE_MAPPING_COVERAGE")
    if len(observed_kinds) != len(OBSERVATION_KINDS):
        degradation.append("INCOMPLETE_OBSERVATION_COVERAGE")
    if heartbeat_age is None:
        degradation.append("NO_LOCAL_HEARTBEAT")
    elif heartbeat_age > heartbeat_timeout_seconds:
        degradation.append("STALE_LOCAL_HEARTBEAT")
    if clock.state == "MISSING":
        degradation.append("NO_ACTIVE_MULTI_CLOCK_STATE")
    ready = not any(
        code
        in {
            "INCOMPLETE_MAPPING_COVERAGE",
            "INCOMPLETE_OBSERVATION_COVERAGE",
            "NO_LOCAL_HEARTBEAT",
            "STALE_LOCAL_HEARTBEAT",
        }
        for code in degradation
    )
    local_state = "READY_FOR_LOCAL_REPLAY" if ready else ("DEGRADED" if mappings else "BLOCKED")
    return MarketDataAdapterReadinessSnapshot(
        market=market,
        evaluated_at_utc=evaluated,
        mapping_coverage=mapping_coverage,
        observation_coverage=observation_coverage,
        event_count=len(events),
        stream_count=len({event.stream_id for event in events}),
        last_sequences=adapter.ingress.last_sequences,
        heartbeat_age_seconds=heartbeat_age,
        max_transport_latency_ms=max_latency,
        clock_state=clock.state,
        clock_snapshot_hash=clock.snapshot_hash,
        local_replay_state=local_state,
        external_activation_state="BLOCKED",
        entitlement_state="UNRESOLVED",
        retention_state="UNRESOLVED",
        provider_selection_state="UNSELECTED",
        degradation_codes=tuple(degradation),
    )
