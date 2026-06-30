import json
from pathlib import Path
from typing import List

from fcf.contracts.event import FCFEvent, event_from_dict


class EventStore:
    def __init__(self) -> None:
        self._events: List[FCFEvent] = []

    def record(self, event: FCFEvent) -> None:
        self._events.append(event)

    def all_events(self) -> List[FCFEvent]:
        return list(self._events)

    def count(self) -> int:
        return len(self._events)

    def save_jsonl(self, file_path: str) -> None:
        path = Path(file_path)
        path.parent.mkdir(parents=True, exist_ok=True)

        with path.open("w", encoding="utf-8") as f:
            for event in self._events:
                f.write(json.dumps(event.to_dict(), ensure_ascii=False) + "\n")

    @classmethod
    def load_jsonl(cls, file_path: str) -> "EventStore":
        store = cls()
        path = Path(file_path)

        with path.open("r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                store.record(event_from_dict(json.loads(line)))

        return store
