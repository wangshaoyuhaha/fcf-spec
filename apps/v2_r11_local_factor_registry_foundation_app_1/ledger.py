from __future__ import annotations

from dataclasses import dataclass, replace

from .registry import FactorRegistryEvidence


@dataclass(frozen=True)
class FactorRegistryLedger:
    evidence: tuple[FactorRegistryEvidence, ...] = ()
    capacity: int = 1000

    def __post_init__(self) -> None:
        if isinstance(self.capacity, bool) or not 1 <= self.capacity <= 10000:
            raise ValueError("factor registry ledger capacity is invalid")
        hashes = tuple(item.evidence_hash for item in self.evidence)
        keys = tuple(
            (item.registry_id, item.registry_version, item.evaluated_at_utc)
            for item in self.evidence
        )
        if len(set(hashes)) != len(hashes) or len(set(keys)) != len(keys):
            raise ValueError("duplicate factor registry evidence is prohibited")
        if len(self.evidence) > self.capacity:
            raise ValueError("factor registry ledger capacity exceeded")

    def append(self, item: FactorRegistryEvidence) -> FactorRegistryLedger:
        if len(self.evidence) >= self.capacity:
            raise ValueError("factor registry ledger capacity exceeded")
        key = (item.registry_id, item.registry_version, item.evaluated_at_utc)
        if any(existing.evidence_hash == item.evidence_hash for existing in self.evidence):
            raise ValueError("duplicate factor registry evidence hash is prohibited")
        if any(
            (existing.registry_id, existing.registry_version, existing.evaluated_at_utc)
            == key
            for existing in self.evidence
        ):
            raise ValueError("duplicate factor registry evidence natural key is prohibited")
        return replace(self, evidence=(*self.evidence, item))
