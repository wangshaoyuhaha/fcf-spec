from dataclasses import dataclass

from .indicator import TrixEvidence


@dataclass(frozen=True)
class TripleExponentialAcceptance:
    status: str
    evidence_hash: str
    operator_review_required: bool
    signal_or_recommendation_allowed: bool
    order_or_execution_allowed: bool


def build_operator_acceptance(evidence: TrixEvidence) -> TripleExponentialAcceptance:
    return TripleExponentialAcceptance("WAITING_FOR_OPERATOR_REVIEW" if evidence.state == "TRIX_READY" else "BLOCKED", evidence.evidence_hash, True, False, False)
