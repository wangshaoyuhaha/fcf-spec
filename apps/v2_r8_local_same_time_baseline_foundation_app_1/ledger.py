from __future__ import annotations

from dataclasses import dataclass, replace

from .baseline import SameTimeBaselineEvidence


@dataclass(frozen=True)
class SameTimeBaselineLedger:
    evidence: tuple[SameTimeBaselineEvidence, ...] = ()
    capacity: int = 1000

    def __post_init__(self) -> None:
        if isinstance(self.capacity, bool) or not 1 <= self.capacity <= 10000:
            raise ValueError("same-time baseline ledger capacity is invalid")
        hashes = tuple(item.evidence_hash for item in self.evidence)
        keys = tuple(
            (item.baseline_id, item.baseline_version, item.target_session_evidence_hash)
            for item in self.evidence
        )
        if len(set(hashes)) != len(hashes) or len(set(keys)) != len(keys):
            raise ValueError("duplicate same-time baseline evidence is prohibited")
        if len(self.evidence) > self.capacity:
            raise ValueError("same-time baseline ledger capacity exceeded")

    def append(self, item: SameTimeBaselineEvidence) -> SameTimeBaselineLedger:
        if len(self.evidence) >= self.capacity:
            raise ValueError("same-time baseline ledger capacity exceeded")
        key = (item.baseline_id, item.baseline_version, item.target_session_evidence_hash)
        if any(existing.evidence_hash == item.evidence_hash for existing in self.evidence):
            raise ValueError("duplicate same-time baseline evidence hash is prohibited")
        if any(
            (existing.baseline_id, existing.baseline_version, existing.target_session_evidence_hash)
            == key
            for existing in self.evidence
        ):
            raise ValueError("duplicate same-time baseline natural key is prohibited")
        return replace(self, evidence=(*self.evidence, item))
