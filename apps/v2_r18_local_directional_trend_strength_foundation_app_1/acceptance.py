from dataclasses import dataclass

from .indicator import DirectionalStrengthEvidence


@dataclass(frozen=True)
class DirectionalStrengthAcceptance:
    status: str
    evidence_hash: str
    operator_review_required: bool
    signal_or_recommendation_allowed: bool
    order_or_execution_allowed: bool


def build_operator_acceptance(
    evidence: DirectionalStrengthEvidence,
) -> DirectionalStrengthAcceptance:
    return DirectionalStrengthAcceptance(
        "WAITING_FOR_OPERATOR_REVIEW"
        if evidence.state == "DIRECTIONAL_STRENGTH_READY"
        else "BLOCKED",
        evidence.evidence_hash,
        True,
        False,
        False,
    )
