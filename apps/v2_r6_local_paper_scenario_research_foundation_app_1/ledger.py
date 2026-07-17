from __future__ import annotations

from dataclasses import dataclass, replace

from .evaluator import PaperScenarioEvidence


@dataclass(frozen=True)
class PaperScenarioLedger:
    evidence: tuple[PaperScenarioEvidence, ...] = ()
    capacity: int = 1000

    def __post_init__(self) -> None:
        if isinstance(self.capacity, bool) or not 1 <= self.capacity <= 10000:
            raise ValueError("Paper scenario ledger capacity is invalid")
        hashes = tuple(item.evidence_hash for item in self.evidence)
        natural_keys = tuple(
            (item.scenario_id, item.scenario_version, item.anomaly_evidence_hash)
            for item in self.evidence
        )
        if len(set(hashes)) != len(hashes) or len(set(natural_keys)) != len(natural_keys):
            raise ValueError("duplicate Paper scenario evidence is prohibited")
        if len(self.evidence) > self.capacity:
            raise ValueError("Paper scenario ledger capacity exceeded")

    def append(self, item: PaperScenarioEvidence) -> PaperScenarioLedger:
        if len(self.evidence) >= self.capacity:
            raise ValueError("Paper scenario ledger capacity exceeded")
        natural_key = (item.scenario_id, item.scenario_version, item.anomaly_evidence_hash)
        if any(existing.evidence_hash == item.evidence_hash for existing in self.evidence):
            raise ValueError("duplicate Paper scenario evidence hash is prohibited")
        if any(
            (existing.scenario_id, existing.scenario_version, existing.anomaly_evidence_hash)
            == natural_key
            for existing in self.evidence
        ):
            raise ValueError("duplicate Paper scenario natural key is prohibited")
        return replace(self, evidence=(*self.evidence, item))
