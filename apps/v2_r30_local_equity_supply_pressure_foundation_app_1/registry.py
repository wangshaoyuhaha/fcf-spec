from __future__ import annotations

from dataclasses import dataclass, replace

from .contracts import EquitySupplyPressureRecord, RegisteredEquitySupplyEvent, RegisteredEquitySupplyObservation


@dataclass(frozen=True)
class LocalEquitySupplyPressureRegistry:
    events: tuple[RegisteredEquitySupplyEvent, ...] = ()
    observations: tuple[RegisteredEquitySupplyObservation, ...] = ()
    records: tuple[EquitySupplyPressureRecord, ...] = ()
    capacity: int = 10000

    def __post_init__(self) -> None:
        if isinstance(self.capacity, bool) or not 1 <= self.capacity <= 100000:
            raise ValueError("equity supply registry capacity is invalid")
        events, observations, records = tuple(self.events), tuple(self.observations), tuple(self.records)
        if len(events) + len(observations) + len(records) > self.capacity:
            raise ValueError("equity supply registry capacity exceeded")
        for values, identity, digest, message in (
            (events, "supply_event_id", "supply_event_hash", "supply event"),
            (observations, "observation_id", "observation_hash", "supply observation"),
            (records, "record_id", "record_hash", "pressure record"),
        ):
            if len({getattr(item, identity) for item in values}) != len(values):
                raise ValueError(f"duplicate {message} id is prohibited")
            if len({getattr(item, digest) for item in values}) != len(values):
                raise ValueError(f"duplicate {message} hash is prohibited")
        event_hashes = {item.supply_event_hash for item in events}
        observation_hashes = {item.observation_hash for item in observations}
        if any(item.supply_event.supply_event_hash not in event_hashes for item in observations):
            raise ValueError("supply observation event must be registered")
        if any(item.observation.observation_hash not in observation_hashes for item in records):
            raise ValueError("pressure record observation must be registered")
        object.__setattr__(self, "events", events)
        object.__setattr__(self, "observations", observations)
        object.__setattr__(self, "records", records)

    def append_event(self, item: RegisteredEquitySupplyEvent) -> LocalEquitySupplyPressureRegistry:
        if not isinstance(item, RegisteredEquitySupplyEvent):
            raise ValueError("registry accepts RegisteredEquitySupplyEvent only")
        return replace(self, events=(*self.events, item))

    def append_observation(self, item: RegisteredEquitySupplyObservation) -> LocalEquitySupplyPressureRegistry:
        if not isinstance(item, RegisteredEquitySupplyObservation):
            raise ValueError("registry accepts RegisteredEquitySupplyObservation only")
        return replace(self, observations=(*self.observations, item))

    def append_record(self, item: EquitySupplyPressureRecord) -> LocalEquitySupplyPressureRegistry:
        if not isinstance(item, EquitySupplyPressureRecord):
            raise ValueError("registry accepts EquitySupplyPressureRecord only")
        return replace(self, records=(*self.records, item))
