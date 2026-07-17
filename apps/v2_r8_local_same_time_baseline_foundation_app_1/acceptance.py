from __future__ import annotations

from dataclasses import dataclass

from .baseline import SameTimeBaselineEvidence


@dataclass(frozen=True)
class V2R8OperatorAcceptance:
    evidence_hash: str
    status: str
    operator_review_required: bool = True
    automatic_approval: bool = False
    score_activated: bool = False


def build_operator_acceptance(evidence: SameTimeBaselineEvidence) -> V2R8OperatorAcceptance:
    return V2R8OperatorAcceptance(
        evidence_hash=evidence.evidence_hash,
        status="WAITING_FOR_OPERATOR_REVIEW",
    )
