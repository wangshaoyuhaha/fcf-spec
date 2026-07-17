from __future__ import annotations

from dataclasses import dataclass, replace

from .ratio import VolumeRatioEvidence


@dataclass(frozen=True)
class VolumeRatioLedger:
    evidence: tuple[VolumeRatioEvidence, ...] = ()
    capacity: int = 1000

    def __post_init__(self) -> None:
        if isinstance(self.capacity, bool) or not 1 <= self.capacity <= 10000:
            raise ValueError("volume-ratio ledger capacity is invalid")
        hashes = tuple(item.evidence_hash for item in self.evidence)
        keys = tuple(
            (
                item.ratio_id,
                item.ratio_version,
                item.observation_id,
                item.baseline_evidence_hash,
            )
            for item in self.evidence
        )
        if len(set(hashes)) != len(hashes) or len(set(keys)) != len(keys):
            raise ValueError("duplicate volume-ratio evidence is prohibited")
        if len(self.evidence) > self.capacity:
            raise ValueError("volume-ratio ledger capacity exceeded")

    def append(self, item: VolumeRatioEvidence) -> VolumeRatioLedger:
        if len(self.evidence) >= self.capacity:
            raise ValueError("volume-ratio ledger capacity exceeded")
        key = (
            item.ratio_id,
            item.ratio_version,
            item.observation_id,
            item.baseline_evidence_hash,
        )
        if any(existing.evidence_hash == item.evidence_hash for existing in self.evidence):
            raise ValueError("duplicate volume-ratio evidence hash is prohibited")
        if any(
            (
                existing.ratio_id,
                existing.ratio_version,
                existing.observation_id,
                existing.baseline_evidence_hash,
            )
            == key
            for existing in self.evidence
        ):
            raise ValueError("duplicate volume-ratio natural key is prohibited")
        return replace(self, evidence=(*self.evidence, item))
