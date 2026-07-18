from dataclasses import dataclass

from .resolver import InstitutionalCalendarResolution


@dataclass(frozen=True)
class V2R23OperatorAcceptance:
    evidence_hash: str
    resolution_state: str
    status: str = "WAITING_FOR_OPERATOR_REVIEW"
    operator_review_required: bool = True
    automatic_approval: bool = False
    action_created: bool = False


def build_operator_acceptance(
    resolution: InstitutionalCalendarResolution,
) -> V2R23OperatorAcceptance:
    return V2R23OperatorAcceptance(
        evidence_hash=resolution.evidence_hash,
        resolution_state=resolution.state,
    )
