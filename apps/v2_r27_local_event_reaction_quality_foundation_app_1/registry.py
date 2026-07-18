from __future__ import annotations

from dataclasses import dataclass, replace

from .contracts import (
    EventReactionQualityRecord,
    RegisteredReactionObservation,
    RegisteredReactionWindow,
)


@dataclass(frozen=True)
class LocalEventReactionQualityRegistry:
    windows: tuple[RegisteredReactionWindow, ...] = ()
    observations: tuple[RegisteredReactionObservation, ...] = ()
    quality_records: tuple[EventReactionQualityRecord, ...] = ()
    capacity: int = 10000

    def __post_init__(self) -> None:
        if isinstance(self.capacity, bool) or not 1 <= self.capacity <= 100000:
            raise ValueError("event reaction registry capacity is invalid")
        windows = tuple(self.windows)
        observations = tuple(self.observations)
        quality = tuple(self.quality_records)
        if len(windows) + len(observations) + len(quality) > self.capacity:
            raise ValueError("event reaction registry capacity exceeded")
        for values, identity, digest, message in (
            (windows, "window_id", "window_hash", "reaction window"),
            (observations, "observation_id", "observation_hash", "reaction observation"),
            (quality, "quality_id", "quality_hash", "reaction quality"),
        ):
            if len({getattr(item, identity) for item in values}) != len(values):
                raise ValueError(f"duplicate {message} id is prohibited")
            if len({getattr(item, digest) for item in values}) != len(values):
                raise ValueError(f"duplicate {message} hash is prohibited")
        window_hashes = {item.window_hash for item in windows}
        observation_hashes = {item.observation_hash for item in observations}
        for item in observations:
            if item.window.window_hash not in window_hashes:
                raise ValueError("reaction observation window must be registered")
        for item in quality:
            if item.observation.observation_hash not in observation_hashes:
                raise ValueError("reaction quality observation must be registered")
        object.__setattr__(self, "windows", windows)
        object.__setattr__(self, "observations", observations)
        object.__setattr__(self, "quality_records", quality)

    def append_window(self, window: RegisteredReactionWindow) -> LocalEventReactionQualityRegistry:
        if not isinstance(window, RegisteredReactionWindow):
            raise ValueError("registry accepts RegisteredReactionWindow only")
        return replace(self, windows=(*self.windows, window))

    def append_observation(
        self, observation: RegisteredReactionObservation
    ) -> LocalEventReactionQualityRegistry:
        if not isinstance(observation, RegisteredReactionObservation):
            raise ValueError("registry accepts RegisteredReactionObservation only")
        return replace(self, observations=(*self.observations, observation))

    def append_quality(
        self, quality: EventReactionQualityRecord
    ) -> LocalEventReactionQualityRegistry:
        if not isinstance(quality, EventReactionQualityRecord):
            raise ValueError("registry accepts EventReactionQualityRecord only")
        return replace(self, quality_records=(*self.quality_records, quality))
