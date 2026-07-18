from __future__ import annotations
from dataclasses import dataclass, replace
from .normalization import NormalizationEvidence


@dataclass(frozen=True)
class NormalizationLedger:
    evidence: tuple[NormalizationEvidence, ...] = ()
    capacity: int = 1000

    def __post_init__(self) -> None:
        if isinstance(self.capacity, bool) or not 1 <= self.capacity <= 10000: raise ValueError("normalization ledger capacity is invalid")
        hashes = tuple(item.evidence_hash for item in self.evidence)
        if len(set(hashes)) != len(hashes) or len(self.evidence) > self.capacity: raise ValueError("duplicate or excessive normalization evidence")

    def append(self, item: NormalizationEvidence) -> "NormalizationLedger":
        if len(self.evidence) >= self.capacity: raise ValueError("normalization ledger capacity exceeded")
        if any(existing.evidence_hash == item.evidence_hash for existing in self.evidence): raise ValueError("duplicate normalization evidence is prohibited")
        return replace(self, evidence=(*self.evidence, item))
