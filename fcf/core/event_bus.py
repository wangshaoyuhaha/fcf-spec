from collections import defaultdict
from typing import Callable, DefaultDict, List

from fcf.contracts.event import FCFEvent


EventHandler = Callable[[FCFEvent], None]


class EventBus:
    def __init__(self) -> None:
        self._subscribers: DefaultDict[str, List[EventHandler]] = defaultdict(list)
        self._global_subscribers: List[EventHandler] = []

    def subscribe(self, event_name: str, handler: EventHandler) -> None:
        self._subscribers[event_name].append(handler)

    def subscribe_all(self, handler: EventHandler) -> None:
        self._global_subscribers.append(handler)

    def publish(self, event: FCFEvent) -> None:
        for handler in self._global_subscribers:
            handler(event)

        for handler in self._subscribers.get(event.event_name, []):
            handler(event)
