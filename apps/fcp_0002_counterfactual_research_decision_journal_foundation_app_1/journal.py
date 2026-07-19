from __future__ import annotations

from dataclasses import dataclass

from .contracts import (
    CandidateDisposition,
    CounterfactualFinding,
    RegisteredOutcome,
    ResearchDecisionSnapshot,
    instant,
)


@dataclass(frozen=True)
class CounterfactualDecisionJournal:
    entries: tuple[ResearchDecisionSnapshot, ...]

    def __post_init__(self) -> None:
        entries = tuple(self.entries)
        if not entries:
            raise ValueError("journal must not be empty")
        if len({item.decision_id for item in entries}) != len(entries):
            raise ValueError("journal decision ids must be unique")
        journal_ids = {item.journal_id for item in entries}
        if len(journal_ids) != 1:
            raise ValueError("journal entries must share one journal id")
        for index, entry in enumerate(entries):
            expected = None if index == 0 else entries[index - 1].decision_hash
            if entry.predecessor_hash != expected:
                raise ValueError("journal predecessor hash chain is invalid")
            if index and instant(entry.decided_at_utc) < instant(entries[index - 1].decided_at_utc):
                raise ValueError("journal decision time must be monotonic")
        object.__setattr__(self, "entries", entries)

    @property
    def head_hash(self) -> str:
        return self.entries[-1].decision_hash


def evaluate_counterfactuals(
    decision: ResearchDecisionSnapshot,
    outcomes: tuple[RegisteredOutcome, ...],
) -> tuple[CounterfactualFinding, ...]:
    by_candidate = {}
    candidates = {item.candidate_id: item for item in decision.alternatives}
    for outcome in outcomes:
        if outcome.decision_hash != decision.decision_hash:
            raise ValueError("outcome decision linkage mismatch")
        if outcome.candidate_id not in candidates:
            raise ValueError("outcome candidate is not in the decision")
        if instant(outcome.observed_at_utc) <= instant(decision.decided_at_utc):
            raise ValueError("outcome must be observed after the decision")
        if outcome.candidate_id in by_candidate:
            raise ValueError("candidate outcome must be unique")
        by_candidate[outcome.candidate_id] = outcome
    selected = next(
        (item for item in decision.alternatives if item.disposition is CandidateDisposition.SELECTED),
        None,
    )
    selected_outcome = by_candidate.get(selected.candidate_id) if selected else None
    findings = []
    for alternative in decision.alternatives:
        outcome = by_candidate.get(alternative.candidate_id)
        delta = None
        classification = "NOT_COMPARABLE"
        if outcome is not None and selected_outcome is not None:
            delta = outcome.realized_utility_bps - selected_outcome.realized_utility_bps
            classification = "MISSED_UPSIDE" if delta > 0 else "AVOIDED_DOWNSIDE" if delta < 0 else "NEUTRAL"
        findings.append(CounterfactualFinding(
            candidate_id=alternative.candidate_id,
            disposition=alternative.disposition.value,
            classification=classification,
            realized_utility_bps=outcome.realized_utility_bps if outcome else None,
            selected_delta_bps=delta,
            outcome_evidence_hashes=outcome.evidence_hashes if outcome else (),
        ))
    return tuple(findings)
