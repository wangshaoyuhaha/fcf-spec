from __future__ import annotations

from dataclasses import dataclass

from .evaluator import PaperScenarioEvidence


@dataclass(frozen=True)
class V2R6OperatorAcceptance:
    evidence_hash: str
    status: str
    operator_review_required: bool = True
    automatic_approval: bool = False
    order_created: bool = False


def build_operator_acceptance(
    evidence: PaperScenarioEvidence,
) -> V2R6OperatorAcceptance:
    return V2R6OperatorAcceptance(
        evidence_hash=evidence.evidence_hash,
        status="WAITING_FOR_OPERATOR_REVIEW",
    )
