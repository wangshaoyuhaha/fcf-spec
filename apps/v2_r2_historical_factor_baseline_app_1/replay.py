from __future__ import annotations

from dataclasses import dataclass

from .contracts import instant, utc
from .registry import HistoricalObservationRegistry


@dataclass(frozen=True)
class WalkForwardSplit:
    training_ids: tuple[str, ...]
    evaluation_ids: tuple[str, ...]
    evaluation_start_utc: str
    as_of_utc: str


def build_walk_forward_split(
    registry: HistoricalObservationRegistry,
    *,
    evaluation_start_utc: str,
    as_of_utc: str,
) -> WalkForwardSplit:
    start_text = utc(evaluation_start_utc, "evaluation_start_utc")
    as_of_text = utc(as_of_utc, "as_of_utc")
    start = instant(start_text)
    as_of = instant(as_of_text)
    if start >= as_of:
        raise ValueError("evaluation start must precede as_of_utc")
    visible = tuple(
        item for item in registry.observations if instant(item.available_at_utc) <= as_of
    )
    training = tuple(
        item.observation_id
        for item in visible
        if instant(item.event_at_utc) < start and instant(item.available_at_utc) < start
    )
    evaluation = tuple(
        item.observation_id
        for item in visible
        if start <= instant(item.event_at_utc) <= as_of
    )
    if set(training) & set(evaluation):
        raise ValueError("walk-forward split leaked evaluation observations")
    return WalkForwardSplit(training, evaluation, start_text, as_of_text)
