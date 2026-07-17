from __future__ import annotations

from dataclasses import dataclass
from types import MappingProxyType
from typing import Mapping

from .contracts import LocalEventEnvelope, instant, utc


@dataclass(frozen=True)
class IngressReceipt:
    event_id: str
    stream_id: str
    source_sequence: int
    event_hash: str
    queue_size: int
    status: str = "ACCEPTED"
    operator_review_required: bool = True

    def __post_init__(self) -> None:
        if self.status != "ACCEPTED":
            raise ValueError("receipt status must be ACCEPTED")
        if self.operator_review_required is not True:
            raise ValueError("Operator review must remain required")


@dataclass(frozen=True)
class BoundedLocalEventIngress:
    capacity: int
    ttl_seconds: int
    events: tuple[LocalEventEnvelope, ...] = ()

    def __post_init__(self) -> None:
        if isinstance(self.capacity, bool) or self.capacity <= 0:
            raise ValueError("capacity must be positive")
        if isinstance(self.ttl_seconds, bool) or self.ttl_seconds <= 0:
            raise ValueError("ttl_seconds must be positive")
        events = tuple(self.events)
        if len(events) > self.capacity:
            raise ValueError("ingress capacity exceeded")
        if not all(isinstance(event, LocalEventEnvelope) for event in events):
            raise ValueError("ingress accepts LocalEventEnvelope only")
        ids = [event.event_id for event in events]
        if len(ids) != len(set(ids)):
            raise ValueError("duplicate event_id is prohibited")
        last_sequences: dict[str, int] = {}
        for event in events:
            expected = last_sequences.get(event.stream_id, 0) + 1
            if event.source_sequence != expected:
                raise ValueError("stream sequence must be contiguous from one")
            last_sequences[event.stream_id] = event.source_sequence
        object.__setattr__(self, "events", events)

    @property
    def last_sequences(self) -> Mapping[str, int]:
        values: dict[str, int] = {}
        for event in self.events:
            values[event.stream_id] = event.source_sequence
        return MappingProxyType(dict(sorted(values.items())))

    def accept(
        self,
        event: LocalEventEnvelope,
        *,
        as_of_utc: str,
    ) -> tuple[BoundedLocalEventIngress, IngressReceipt]:
        if not isinstance(event, LocalEventEnvelope):
            raise ValueError("event must be LocalEventEnvelope")
        if any(existing.event_id == event.event_id for existing in self.events):
            raise ValueError("duplicate event_id is prohibited")
        if len(self.events) >= self.capacity:
            raise ValueError("ingress capacity exceeded")
        expected = self.last_sequences.get(event.stream_id, 0) + 1
        if event.source_sequence != expected:
            raise ValueError("duplicate, missing, or out-of-order sequence")
        as_of = instant(utc(as_of_utc, "as_of_utc"))
        processed = instant(event.processed_at_utc)
        received = instant(event.received_at_utc)
        if processed > as_of:
            raise ValueError("event cannot be accepted before processing time")
        if (as_of - received).total_seconds() > self.ttl_seconds:
            raise ValueError("event is expired")
        updated = BoundedLocalEventIngress(
            capacity=self.capacity,
            ttl_seconds=self.ttl_seconds,
            events=self.events + (event,),
        )
        receipt = IngressReceipt(
            event_id=event.event_id,
            stream_id=event.stream_id,
            source_sequence=event.source_sequence,
            event_hash=event.event_hash,
            queue_size=len(updated.events),
        )
        return updated, receipt
