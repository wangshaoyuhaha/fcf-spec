from collections import defaultdict
from typing import Awaitable, Callable, Dict, List
from .event_model import Event

Handler = Callable[[Event], Awaitable[None]]


class EventBus:
    def __init__(self):
        self._handlers: Dict[str, List[Handler]] = defaultdict(list)
        self._wildcard_handlers: List[Handler] = []

    def subscribe(self, event_type: str, handler: Handler) -> None:
        if event_type == "*":
            self._wildcard_handlers.append(handler)
        else:
            self._handlers[event_type].append(handler)

    async def publish(self, event: Event) -> None:
        for handler in self._wildcard_handlers:
            await handler(event)
        for handler in self._handlers.get(event.event_type, []):
            await handler(event)
