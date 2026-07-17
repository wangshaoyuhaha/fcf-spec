from __future__ import annotations

from dataclasses import dataclass, replace

from .contracts import CognitiveTask
from .shield import CognitiveShieldEvidence


@dataclass(frozen=True)
class CognitiveShieldLedger:
    tasks: tuple[CognitiveTask, ...] = ()
    evidence: tuple[CognitiveShieldEvidence, ...] = ()
    capacity: int = 1000

    def __post_init__(self) -> None:
        if isinstance(self.capacity, bool) or not 1 <= self.capacity <= 10000:
            raise ValueError("cognitive shield ledger capacity is invalid")
        task_ids = tuple(task.task_id for task in self.tasks)
        evidence_ids = tuple(item.task_id for item in self.evidence)
        if len(set(task_ids)) != len(task_ids) or len(set(evidence_ids)) != len(
            evidence_ids
        ):
            raise ValueError("duplicate cognitive task is prohibited")
        if len(self.tasks) > self.capacity or len(self.evidence) > self.capacity:
            raise ValueError("cognitive shield ledger capacity exceeded")

    def register_task(self, task: CognitiveTask) -> CognitiveShieldLedger:
        if any(existing.task_id == task.task_id for existing in self.tasks):
            raise ValueError("duplicate cognitive task is prohibited")
        if len(self.tasks) >= self.capacity:
            raise ValueError("cognitive shield ledger capacity exceeded")
        return replace(self, tasks=(*self.tasks, task))

    def append_evidence(
        self, item: CognitiveShieldEvidence
    ) -> CognitiveShieldLedger:
        if not any(task.task_id == item.task_id for task in self.tasks):
            raise ValueError("shield evidence requires a registered task")
        if any(existing.task_id == item.task_id for existing in self.evidence):
            raise ValueError("duplicate shield evidence is prohibited")
        if any(
            existing.shield_evidence_hash == item.shield_evidence_hash
            for existing in self.evidence
        ):
            raise ValueError("duplicate shield evidence hash is prohibited")
        if len(self.evidence) >= self.capacity:
            raise ValueError("cognitive shield ledger capacity exceeded")
        return replace(self, evidence=(*self.evidence, item))
