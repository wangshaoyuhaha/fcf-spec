from __future__ import annotations

from dataclasses import dataclass

from .contracts import HistoricalObservation, identifier, instant, utc


@dataclass(frozen=True)
class HistoricalObservationRegistry:
    observations: tuple[HistoricalObservation, ...] = ()

    def __post_init__(self) -> None:
        items = tuple(self.observations)
        if not all(isinstance(item, HistoricalObservation) for item in items):
            raise ValueError("registry accepts HistoricalObservation only")
        ids = [item.observation_id for item in items]
        if len(ids) != len(set(ids)):
            raise ValueError("observation ids must be unique")
        natural_keys = [
            (item.instrument_id, item.field_id, item.event_at_utc) for item in items
        ]
        if len(natural_keys) != len(set(natural_keys)):
            raise ValueError("duplicate instrument field event is prohibited")
        ordered = tuple(
            sorted(
                items,
                key=lambda item: (
                    item.available_at_utc,
                    item.event_at_utc,
                    item.observation_id,
                ),
            )
        )
        object.__setattr__(self, "observations", ordered)

    def register(self, observation: HistoricalObservation) -> HistoricalObservationRegistry:
        return HistoricalObservationRegistry(self.observations + (observation,))

    def available_before(
        self,
        *,
        instrument_id: str,
        field_id: str,
        as_of_utc: str,
    ) -> tuple[HistoricalObservation, ...]:
        cutoff = instant(utc(as_of_utc, "as_of_utc"))
        normalized_instrument = identifier(instrument_id, "instrument_id")
        normalized_field = identifier(field_id, "field_id")
        return tuple(
            item
            for item in self.observations
            if item.instrument_id == normalized_instrument
            and item.field_id == normalized_field
            and instant(item.event_at_utc) < cutoff
            and instant(item.available_at_utc) < cutoff
        )
