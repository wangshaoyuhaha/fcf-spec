from __future__ import annotations

from dataclasses import dataclass, replace

from .contracts import InstitutionalFactorCandidate, OperatorLifecycleDecision


@dataclass(frozen=True)
class LocalInstitutionalFactorLifecycleRegistry:
    candidates: tuple[InstitutionalFactorCandidate, ...] = ()
    decisions: tuple[OperatorLifecycleDecision, ...] = ()
    capacity: int = 10000

    def __post_init__(self) -> None:
        candidates, decisions = tuple(self.candidates), tuple(self.decisions)
        if isinstance(self.capacity, bool) or not 1 <= self.capacity <= 100000 or len(candidates) + len(decisions) > self.capacity:
            raise ValueError("factor lifecycle registry capacity is invalid")
        if len({item.candidate_id for item in candidates}) != len(candidates):
            raise ValueError("duplicate factor candidate is prohibited")
        if len({item.decision_id for item in decisions}) != len(decisions) or len({item.decision_hash for item in decisions}) != len(decisions):
            raise ValueError("duplicate lifecycle decision is prohibited")
        known = {item.candidate_id for item in candidates}
        if any(item.candidate_id not in known for item in decisions):
            raise ValueError("lifecycle decision candidate must be registered")
        for candidate in candidates:
            self._validate_history(candidate, tuple(item for item in decisions if item.candidate_id == candidate.candidate_id))
        object.__setattr__(self, "candidates", candidates)
        object.__setattr__(self, "decisions", decisions)

    @staticmethod
    def _validate_history(candidate: InstitutionalFactorCandidate, history: tuple[OperatorLifecycleDecision, ...]) -> None:
        state, predecessor = "RESEARCH_PROPOSAL", None
        for decision in history:
            if decision.from_state != state:
                raise ValueError("lifecycle decision from_state mismatch")
            if decision.predecessor_decision_hash != predecessor:
                raise ValueError("lifecycle decision predecessor mismatch")
            if decision.decided_at_utc < candidate.submitted_at_utc:
                raise ValueError("lifecycle decision cannot precede candidate")
            state, predecessor = decision.to_state, decision.decision_hash

    def append_candidate(self, item: InstitutionalFactorCandidate) -> "LocalInstitutionalFactorLifecycleRegistry":
        if not isinstance(item, InstitutionalFactorCandidate):
            raise ValueError("registry accepts InstitutionalFactorCandidate only")
        return replace(self, candidates=(*self.candidates, item))

    def append_decision(self, item: OperatorLifecycleDecision) -> "LocalInstitutionalFactorLifecycleRegistry":
        if not isinstance(item, OperatorLifecycleDecision):
            raise ValueError("registry accepts OperatorLifecycleDecision only")
        return replace(self, decisions=(*self.decisions, item))

    def history(self, candidate_id: str) -> tuple[OperatorLifecycleDecision, ...]:
        return tuple(item for item in self.decisions if item.candidate_id == candidate_id)
