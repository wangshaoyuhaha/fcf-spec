from dataclasses import dataclass

from .indicator import PercentageOscillatorEvidence


@dataclass(frozen=True)
class PercentageOscillatorAcceptance:
    status: str
    evidence_hash: str
    operator_review_required: bool
    signal_or_recommendation_allowed: bool
    order_or_execution_allowed: bool


def build_operator_acceptance(
    evidence: PercentageOscillatorEvidence,
) -> PercentageOscillatorAcceptance:
    return PercentageOscillatorAcceptance(
        "WAITING_FOR_OPERATOR_REVIEW"
        if evidence.state == "PERCENTAGE_OSCILLATOR_READY"
        else "BLOCKED",
        evidence.evidence_hash,
        True,
        False,
        False,
    )
