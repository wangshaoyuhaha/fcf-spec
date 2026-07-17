from dataclasses import dataclass

from .turnover import TurnoverEvidence


@dataclass(frozen=True)
class V2R10OperatorAcceptance:
    evidence_hash: str
    status: str = "WAITING_FOR_OPERATOR_REVIEW"
    operator_review_required: bool = True
    automatic_approval: bool = False
    factor_activated: bool = False


def build_operator_acceptance(evidence: TurnoverEvidence) -> V2R10OperatorAcceptance:
    return V2R10OperatorAcceptance(evidence.evidence_hash)
