from __future__ import annotations

from dataclasses import dataclass, replace

from .contracts import RegisteredEvidenceArtifact


@dataclass(frozen=True)
class LocalEvidenceIntegrityRegistry:
    records: tuple[RegisteredEvidenceArtifact, ...] = ()
    capacity: int = 10000

    def __post_init__(self) -> None:
        records = tuple(self.records)
        if isinstance(self.capacity, bool) or not 1 <= self.capacity <= 100000:
            raise ValueError("evidence integrity registry capacity is invalid")
        if len(records) > self.capacity:
            raise ValueError("evidence integrity registry capacity exceeded")
        if len({item.record_id for item in records}) != len(records):
            raise ValueError("duplicate evidence record id is prohibited")
        if len({item.record_hash for item in records}) != len(records):
            raise ValueError("duplicate evidence record hash is prohibited")
        histories: dict[str, list[RegisteredEvidenceArtifact]] = {}
        available_hashes: set[str] = set()
        for item in records:
            if item.origin == "INFERRED" and not set(item.source_record_hashes) <= available_hashes:
                raise ValueError("inferred evidence sources must already be registered")
            histories.setdefault(item.evidence_series_id, []).append(item)
            available_hashes.add(item.record_hash)
        for history in histories.values():
            self._validate_history(tuple(history))
        object.__setattr__(self, "records", records)

    @staticmethod
    def _validate_history(history: tuple[RegisteredEvidenceArtifact, ...]) -> None:
        if tuple(item.revision_number for item in history) != tuple(range(len(history))):
            raise ValueError("evidence revision sequence must be contiguous from zero")
        identities = {
            (item.evidence_series_id, item.evidence_type, item.market, item.horizon)
            for item in history
        }
        if len(identities) != 1:
            raise ValueError("evidence identity cannot change across revisions")
        for previous, current in zip(history, history[1:]):
            if current.revises_record_hash != previous.record_hash:
                raise ValueError("evidence revision predecessor hash mismatch")
            if current.available_at_utc < previous.available_at_utc:
                raise ValueError("evidence revision availability cannot move backward")

    def append(self, item: RegisteredEvidenceArtifact) -> "LocalEvidenceIntegrityRegistry":
        if not isinstance(item, RegisteredEvidenceArtifact):
            raise ValueError("registry accepts RegisteredEvidenceArtifact only")
        return replace(self, records=(*self.records, item))

    def history(self, evidence_series_id: str) -> tuple[RegisteredEvidenceArtifact, ...]:
        return tuple(item for item in self.records if item.evidence_series_id == evidence_series_id)
