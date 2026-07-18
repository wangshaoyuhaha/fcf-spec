from __future__ import annotations

from dataclasses import dataclass, replace

from .contracts import CalendarFreshnessPolicy, InstitutionalCalendarEvent
from .resolver import InstitutionalCalendarResolution, resolve_institutional_calendar_event


@dataclass(frozen=True)
class LocalInstitutionalCalendarRegistry:
    records: tuple[InstitutionalCalendarEvent, ...] = ()
    capacity: int = 10000

    def __post_init__(self) -> None:
        if isinstance(self.capacity, bool) or not 1 <= self.capacity <= 100000:
            raise ValueError("institutional calendar capacity is invalid")
        records = tuple(self.records)
        if len(records) > self.capacity:
            raise ValueError("institutional calendar capacity exceeded")
        if len({record.record_id for record in records}) != len(records):
            raise ValueError("duplicate calendar record id is prohibited")
        if len({record.record_hash for record in records}) != len(records):
            raise ValueError("duplicate calendar record hash is prohibited")
        histories: dict[tuple[str, str], list[InstitutionalCalendarEvent]] = {}
        for record in records:
            histories.setdefault((record.calendar_id, record.event_id), []).append(record)
        for history in histories.values():
            self._validate_history(tuple(history))
        object.__setattr__(self, "records", records)

    @staticmethod
    def _validate_history(history: tuple[InstitutionalCalendarEvent, ...]) -> None:
        revisions = tuple(record.revision_number for record in history)
        if revisions != tuple(range(len(history))):
            raise ValueError("event revision sequence must be contiguous from zero")
        identity = {
            (record.calendar_id, record.event_id, record.event_type, record.market, record.horizon)
            for record in history
        }
        if len(identity) != 1:
            raise ValueError("event identity cannot change across revisions")
        for previous, current in zip(history, history[1:]):
            if current.revises_record_hash != previous.record_hash:
                raise ValueError("event revision predecessor hash mismatch")

    def append(
        self, record: InstitutionalCalendarEvent
    ) -> LocalInstitutionalCalendarRegistry:
        if not isinstance(record, InstitutionalCalendarEvent):
            raise ValueError("registry accepts InstitutionalCalendarEvent only")
        if len(self.records) >= self.capacity:
            raise ValueError("institutional calendar capacity exceeded")
        if any(existing.record_id == record.record_id for existing in self.records):
            raise ValueError("duplicate calendar record id is prohibited")
        if any(existing.record_hash == record.record_hash for existing in self.records):
            raise ValueError("duplicate calendar record hash is prohibited")
        history = self.history(record.calendar_id, record.event_id)
        expected_revision = len(history)
        if record.revision_number != expected_revision:
            raise ValueError("event revision sequence must be contiguous from zero")
        if history and record.revises_record_hash != history[-1].record_hash:
            raise ValueError("event revision predecessor hash mismatch")
        return replace(self, records=(*self.records, record))

    def history(
        self, calendar_id: str, event_id: str
    ) -> tuple[InstitutionalCalendarEvent, ...]:
        return tuple(
            record
            for record in self.records
            if record.calendar_id == calendar_id and record.event_id == event_id
        )

    def resolve(
        self,
        calendar_id: str,
        event_id: str,
        *,
        as_of_utc: str,
        freshness_policy: CalendarFreshnessPolicy,
    ) -> InstitutionalCalendarResolution:
        return resolve_institutional_calendar_event(
            self.records,
            calendar_id=calendar_id,
            event_id=event_id,
            as_of_utc=as_of_utc,
            freshness_policy=freshness_policy,
        )
