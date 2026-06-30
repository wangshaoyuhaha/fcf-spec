import json
import os
from datetime import datetime
from typing import Dict, Any, List


class EventStore:
    """
    D10 EventStore:
    JSONL 持久化 + 回放基础设施
    """

    def __init__(self, file_path: str = "data/events.jsonl"):
        self.file_path = file_path
        self._ensure_file()

    def _ensure_file(self):
        os.makedirs(os.path.dirname(self.file_path), exist_ok=True)
        if not os.path.exists(self.file_path):
            with open(self.file_path, "w", encoding="utf-8") as f:
                pass

    def append(self, event: Dict[str, Any]):
        event = self._normalize(event)
        with open(self.file_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(event, ensure_ascii=False) + "\n")

    def load_all(self) -> List[Dict[str, Any]]:
        events = []

        if not os.path.exists(self.file_path):
            return events

        with open(self.file_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    events.append(json.loads(line))
                except json.JSONDecodeError:
                    continue

        return events

    def _normalize(self, event: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "event_id": event.get("event_id"),
            "type": event.get("type"),
            "timestamp": event.get("timestamp", self._now()),
            "payload": event.get("payload", {}),
        }

    def _now(self) -> str:
        return datetime.utcnow().isoformat()
