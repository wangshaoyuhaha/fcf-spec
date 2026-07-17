from __future__ import annotations

from dataclasses import dataclass, replace

from .indicator import ChannelIndicatorEvidence


@dataclass(frozen=True)
class ChannelIndicatorLedger:
    evidence: tuple[ChannelIndicatorEvidence, ...] = ()
    capacity: int = 1000

    def __post_init__(self) -> None:
        if isinstance(self.capacity, bool) or not 1 <= self.capacity <= 10000:
            raise ValueError("channel indicator ledger capacity is invalid")
        hashes = tuple(item.evidence_hash for item in self.evidence)
        if len(set(hashes)) != len(hashes) or len(self.evidence) > self.capacity:
            raise ValueError("duplicate or excessive channel evidence")

    def append(self, item: ChannelIndicatorEvidence) -> ChannelIndicatorLedger:
        if len(self.evidence) >= self.capacity:
            raise ValueError("channel indicator ledger capacity exceeded")
        if any(existing.evidence_hash == item.evidence_hash for existing in self.evidence):
            raise ValueError("duplicate channel indicator evidence is prohibited")
        return replace(self, evidence=(*self.evidence, item))
