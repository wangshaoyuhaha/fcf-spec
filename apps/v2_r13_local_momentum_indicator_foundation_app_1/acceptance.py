from dataclasses import dataclass

from .indicator import MomentumIndicatorEvidence


@dataclass(frozen=True)
class MomentumIndicatorAcceptance:
    status: str
    evidence_hash: str
    operator_review_required: bool
    signal_or_recommendation_allowed: bool
    order_or_execution_allowed: bool


def build_operator_acceptance(
    evidence: MomentumIndicatorEvidence,
) -> MomentumIndicatorAcceptance:
    return MomentumIndicatorAcceptance(
        "WAITING_FOR_OPERATOR_REVIEW"
        if evidence.state == "MOMENTUM_READY"
        else "BLOCKED",
        evidence.evidence_hash,
        True,
        False,
        False,
    )
