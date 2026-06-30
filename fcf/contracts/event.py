from dataclasses import dataclass, field
from datetime import datetime, timezone
from itertools import count
from typing import Any, Dict, Optional
from uuid import uuid4


_sequence_counter = count(1)


@dataclass(frozen=True)
class FCFEvent:
    event_id: str
    event_name: str
    event_version: str
    event_time: str
    sequence_id: int
    source_module: str
    correlation_id: str
    causation_id: Optional[str]
    payload: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "event_id": self.event_id,
            "event_name": self.event_name,
            "event_version": self.event_version,
            "event_time": self.event_time,
            "sequence_id": self.sequence_id,
            "source_module": self.source_module,
            "correlation_id": self.correlation_id,
            "causation_id": self.causation_id,
            "payload": self.payload,
            "metadata": self.metadata,
        }


def event_from_dict(data: Dict[str, Any]) -> FCFEvent:
    return FCFEvent(
        event_id=data["event_id"],
        event_name=data["event_name"],
        event_version=data["event_version"],
        event_time=data["event_time"],
        sequence_id=data["sequence_id"],
        source_module=data["source_module"],
        correlation_id=data["correlation_id"],
        causation_id=data.get("causation_id"),
        payload=data.get("payload", {}),
        metadata=data.get("metadata", {}),
    )


def create_event(
    event_name: str,
    source_module: str,
    correlation_id: str,
    payload: Optional[Dict[str, Any]] = None,
    causation_id: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None,
    event_version: str = "1.0",
) -> FCFEvent:
    return FCFEvent(
        event_id=str(uuid4()),
        event_name=event_name,
        event_version=event_version,
        event_time=datetime.now(timezone.utc).isoformat(),
        sequence_id=next(_sequence_counter),
        source_module=source_module,
        correlation_id=correlation_id,
        causation_id=causation_id,
        payload=payload or {},
        metadata=metadata or {},
    )
