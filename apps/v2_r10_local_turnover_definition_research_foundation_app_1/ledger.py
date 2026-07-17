from __future__ import annotations

from dataclasses import dataclass, replace

from .turnover import TurnoverEvidence


@dataclass(frozen=True)
class TurnoverLedger:
    evidence: tuple[TurnoverEvidence, ...] = ()
    capacity: int = 1000

    def __post_init__(self) -> None:
        if isinstance(self.capacity, bool) or not 1 <= self.capacity <= 10000:
            raise ValueError("turnover ledger capacity is invalid")
        hashes = tuple(item.evidence_hash for item in self.evidence)
        keys = tuple(
            (item.definition_id, item.definition_version, item.observation_id)
            for item in self.evidence
        )
        if len(set(hashes)) != len(hashes) or len(set(keys)) != len(keys):
            raise ValueError("duplicate turnover evidence is prohibited")
        if len(self.evidence) > self.capacity:
            raise ValueError("turnover ledger capacity exceeded")

    def append(self, item: TurnoverEvidence) -> TurnoverLedger:
        if len(self.evidence) >= self.capacity:
            raise ValueError("turnover ledger capacity exceeded")
        if any(existing.evidence_hash == item.evidence_hash for existing in self.evidence):
            raise ValueError("duplicate turnover evidence hash is prohibited")
        key = (item.definition_id, item.definition_version, item.observation_id)
        if any(
            (existing.definition_id, existing.definition_version, existing.observation_id)
            == key
            for existing in self.evidence
        ):
            raise ValueError("duplicate turnover evidence natural key is prohibited")
        return replace(self, evidence=(*self.evidence, item))
