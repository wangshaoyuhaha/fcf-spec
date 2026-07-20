from __future__ import annotations

from dataclasses import dataclass, replace
from decimal import Decimal, InvalidOperation

from apps.v2_r24_local_multi_clock_event_state_foundation_app_1 import (
    LocalMultiClockEventStateRegistry,
)
from apps.v2_r3_local_event_ingress_foundation_app_1 import (
    BoundedLocalEventIngress,
    IngressReceipt,
    LocalEventEnvelope,
)
from apps.v2_r3_local_event_ingress_foundation_app_1.contracts import identifier, instant

from .contracts import (
    AdapterActivationGate,
    MarketDataFieldMap,
    RegisteredMarketDataObservation,
)


_NUMERIC_FIELDS = {
    "last",
    "volume",
    "open",
    "high",
    "low",
    "close",
    "bid_price_1",
    "bid_size_1",
    "ask_price_1",
    "ask_size_1",
}


def _decimal(value: object, name: str) -> Decimal:
    if isinstance(value, float):
        raise ValueError(f"{name} must not use binary float")
    try:
        result = Decimal(str(value))
    except (InvalidOperation, ValueError) as exc:
        raise ValueError(f"{name} must be decimal-compatible") from exc
    if not result.is_finite() or result < 0:
        raise ValueError(f"{name} must be finite and nonnegative")
    return result


@dataclass(frozen=True)
class NormalizedMarketDataEvent:
    mapping: MarketDataFieldMap
    envelope: LocalEventEnvelope

    def __post_init__(self) -> None:
        if not isinstance(self.mapping, MarketDataFieldMap):
            raise ValueError("mapping must be MarketDataFieldMap")
        if not isinstance(self.envelope, LocalEventEnvelope):
            raise ValueError("envelope must be LocalEventEnvelope")


@dataclass(frozen=True)
class ProviderNeutralMarketDataAdapter:
    mappings: tuple[MarketDataFieldMap, ...]
    ingress: BoundedLocalEventIngress
    clock_registry: LocalMultiClockEventStateRegistry = LocalMultiClockEventStateRegistry()
    activation_gate: AdapterActivationGate = AdapterActivationGate()

    def __post_init__(self) -> None:
        mappings = tuple(self.mappings)
        if not mappings:
            raise ValueError("at least one registered field map is required")
        if len({item.mapping_id for item in mappings}) != len(mappings):
            raise ValueError("mapping IDs must be unique")
        if not isinstance(self.ingress, BoundedLocalEventIngress):
            raise ValueError("ingress must compose V2-R3")
        if not isinstance(self.clock_registry, LocalMultiClockEventStateRegistry):
            raise ValueError("clock_registry must compose V2-R24")
        if not isinstance(self.activation_gate, AdapterActivationGate):
            raise ValueError("activation_gate is invalid")
        object.__setattr__(self, "mappings", mappings)

    def mapping(self, mapping_id: str) -> MarketDataFieldMap:
        safe_id = identifier(mapping_id, "mapping_id")
        matches = tuple(item for item in self.mappings if item.mapping_id == safe_id)
        if len(matches) != 1:
            raise ValueError("mapping_id is not registered exactly once")
        return matches[0]

    def normalize(
        self, observation: RegisteredMarketDataObservation
    ) -> NormalizedMarketDataEvent:
        if not isinstance(observation, RegisteredMarketDataObservation):
            raise ValueError("observation must be registered")
        mapping = self.mapping(observation.mapping_id)
        missing = tuple(
            source
            for source in mapping.canonical_to_source.values()
            if source not in observation.payload
        )
        if missing:
            raise ValueError("registered observation is missing mapped source fields")
        values: dict[str, object] = {}
        for canonical, source in mapping.canonical_to_source.items():
            value = observation.payload[source]
            if canonical in _NUMERIC_FIELDS:
                value = _decimal(value, canonical)
            elif canonical == "instrument_id":
                value = identifier(value, "instrument_id")
            elif canonical == "interval":
                value = identifier(value, "interval")
            else:
                value = str(value).strip()
            values[canonical] = value
        event_at = str(values.pop("event_at"))
        if instant(event_at) > instant(observation.received_at_utc):
            raise ValueError("event time cannot follow receive time")
        if mapping.observation_kind == "MINUTE_BAR":
            prices = tuple(values[name] for name in ("open", "close"))
            if values["high"] < max(prices) or values["low"] > min(prices):
                raise ValueError("minute bar OHLC relation is invalid")
        if mapping.observation_kind == "ORDER_BOOK":
            if values["ask_price_1"] < values["bid_price_1"]:
                raise ValueError("order book is crossed")
        instrument = str(values["instrument_id"])
        envelope = LocalEventEnvelope(
            event_id=observation.observation_id,
            stream_id=(
                f"market:{mapping.market}:{instrument}:{mapping.observation_kind.lower()}"
            ),
            source_id="provider-neutral-local-replay",
            registered_artifact_id=mapping.registered_artifact_id,
            event_type=f"MARKET_DATA_{mapping.observation_kind}",
            source_sequence=observation.source_sequence,
            event_at_utc=event_at,
            received_at_utc=observation.received_at_utc,
            processed_at_utc=observation.processed_at_utc,
            payload=values,
            rights=mapping.rights,
        )
        return NormalizedMarketDataEvent(mapping=mapping, envelope=envelope)

    def replay(
        self,
        observation: RegisteredMarketDataObservation,
        *,
        as_of_utc: str,
    ) -> tuple[ProviderNeutralMarketDataAdapter, NormalizedMarketDataEvent, IngressReceipt]:
        normalized = self.normalize(observation)
        ingress, receipt = self.ingress.accept(normalized.envelope, as_of_utc=as_of_utc)
        return replace(self, ingress=ingress), normalized, receipt
