from __future__ import annotations

from dataclasses import dataclass, replace

from apps.v2_r2_historical_factor_baseline_app_1.contracts import instant

from .contracts import RegisteredClockEventState


@dataclass(frozen=True)
class LocalMultiClockEventStateRegistry:
    states: tuple[RegisteredClockEventState, ...] = ()
    capacity: int = 10000

    def __post_init__(self) -> None:
        if isinstance(self.capacity, bool) or not 1 <= self.capacity <= 100000:
            raise ValueError("multi-clock state capacity is invalid")
        states = tuple(self.states)
        if len(states) > self.capacity:
            raise ValueError("multi-clock state capacity exceeded")
        if len({state.state_id for state in states}) != len(states):
            raise ValueError("duplicate clock state id is prohibited")
        if len({state.state_hash for state in states}) != len(states):
            raise ValueError("duplicate clock state hash is prohibited")
        groups: dict[tuple[str, str, str, str, str], list[RegisteredClockEventState]] = {}
        for state in states:
            key = (
                state.clock_type,
                state.source_event.event_id,
                state.hypothesis_id,
                state.market,
                state.horizon,
            )
            groups.setdefault(key, []).append(state)
        for group in groups.values():
            ordered = sorted(group, key=lambda state: instant(state.effective_from_utc))
            for previous, current in zip(ordered, ordered[1:]):
                if instant(current.effective_from_utc) < instant(previous.effective_to_utc):
                    raise ValueError("same event clock states cannot overlap")
        object.__setattr__(self, "states", states)

    def append(
        self, state: RegisteredClockEventState
    ) -> LocalMultiClockEventStateRegistry:
        if not isinstance(state, RegisteredClockEventState):
            raise ValueError("registry accepts RegisteredClockEventState only")
        if len(self.states) >= self.capacity:
            raise ValueError("multi-clock state capacity exceeded")
        return replace(self, states=(*self.states, state))
