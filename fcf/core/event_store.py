from typing import List

from fcf.contracts.event import FCFEvent


class EventStore:
    def __init__(self) -> None:
        self._events: List[FCFEvent] = []

    def record(self, event: FCFEvent) -> None:
        self._events.append(event)

    def all_events(self) -> List[FCFEvent]:
        return list(self._events)

    def count(self) -> int:
        return len(self._events)
