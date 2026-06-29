from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict
import uuid


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass(frozen=True)
class Event:
    event_type: str
    producer: str
    payload: Dict[str, Any]
    correlation_id: str
    event_version: str = "1.0"
    event_id: str = field(default_factory=lambda: f"evt_{uuid.uuid4().hex[:16]}")
    timestamp: str = field(default_factory=utc_now_iso)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "event_id": self.event_id,
            "event_type": self.event_type,
            "event_version": self.event_version,
            "producer": self.producer,
            "timestamp": self.timestamp,
            "correlation_id": self.correlation_id,
            "payload": self.payload,
        }
