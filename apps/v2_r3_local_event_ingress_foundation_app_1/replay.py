from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from types import MappingProxyType
from typing import Mapping

from .contracts import LocalEventEnvelope, identifier, instant, utc
from .ingress import BoundedLocalEventIngress, IngressReceipt


def events_hash(events: tuple[LocalEventEnvelope, ...]) -> str:
    encoded = json.dumps(
        [event.event_hash for event in events],
        ensure_ascii=True,
        separators=(",", ":"),
    ).encode("ascii")
    return hashlib.sha256(encoded).hexdigest()


@dataclass(frozen=True)
class ReplayCheckpoint:
    checkpoint_id: str
    created_at_utc: str
    event_count: int
    last_sequences: Mapping[str, int]
    events_hash: str

    def __post_init__(self) -> None:
        object.__setattr__(
            self, "checkpoint_id", identifier(self.checkpoint_id, "checkpoint_id")
        )
        object.__setattr__(
            self, "created_at_utc", utc(self.created_at_utc, "created_at_utc")
        )
        if isinstance(self.event_count, bool) or self.event_count < 0:
            raise ValueError("event_count must be nonnegative")
        sequences = dict(self.last_sequences)
        for stream_id, sequence in sequences.items():
            identifier(stream_id, "stream_id")
            if isinstance(sequence, bool) or sequence <= 0:
                raise ValueError("last sequence must be positive")
        object.__setattr__(
            self,
            "last_sequences",
            MappingProxyType(dict(sorted(sequences.items()))),
        )
        if len(self.events_hash) != 64 or any(
            character not in "0123456789abcdef" for character in self.events_hash
        ):
            raise ValueError("events_hash must be lowercase SHA-256")


def build_checkpoint(
    ingress: BoundedLocalEventIngress,
    *,
    checkpoint_id: str,
    created_at_utc: str,
) -> ReplayCheckpoint:
    created_at = utc(created_at_utc, "created_at_utc")
    if ingress.events and instant(created_at) < instant(
        ingress.events[-1].processed_at_utc
    ):
        raise ValueError("checkpoint cannot precede the latest processed event")
    return ReplayCheckpoint(
        checkpoint_id=checkpoint_id,
        created_at_utc=created_at,
        event_count=len(ingress.events),
        last_sequences=ingress.last_sequences,
        events_hash=events_hash(ingress.events),
    )


def restore_checkpoint(
    events: tuple[LocalEventEnvelope, ...],
    checkpoint: ReplayCheckpoint,
    *,
    capacity: int,
    ttl_seconds: int,
) -> BoundedLocalEventIngress:
    ingress = BoundedLocalEventIngress(
        capacity=capacity,
        ttl_seconds=ttl_seconds,
        events=tuple(events),
    )
    if checkpoint.event_count != len(ingress.events):
        raise ValueError("checkpoint event count mismatch")
    if dict(checkpoint.last_sequences) != dict(ingress.last_sequences):
        raise ValueError("checkpoint sequence mismatch")
    if checkpoint.events_hash != events_hash(ingress.events):
        raise ValueError("checkpoint event hash mismatch")
    return ingress


def replay_local_events(
    events: tuple[LocalEventEnvelope, ...],
    *,
    capacity: int,
    ttl_seconds: int,
    as_of_utc: str,
) -> tuple[BoundedLocalEventIngress, tuple[IngressReceipt, ...]]:
    ingress = BoundedLocalEventIngress(
        capacity=capacity,
        ttl_seconds=ttl_seconds,
    )
    receipts: list[IngressReceipt] = []
    for event in tuple(events):
        ingress, receipt = ingress.accept(event, as_of_utc=as_of_utc)
        receipts.append(receipt)
    return ingress, tuple(receipts)
