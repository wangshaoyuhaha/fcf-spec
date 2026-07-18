from dataclasses import dataclass

from .contracts import OperatorFactorGovernanceProjection


@dataclass(frozen=True)
class V2R38OperatorAcceptance:
    projection_hash: str
    projection_state: str
    status: str = "WAITING_FOR_OPERATOR_REVIEW"
    operator_review_required: bool = True
    read_only: bool = True
    automatic_approval: bool = False
    factor_activated: bool = False
    action_created: bool = False


def build_operator_acceptance(
    projection: OperatorFactorGovernanceProjection,
) -> V2R38OperatorAcceptance:
    return V2R38OperatorAcceptance(projection.projection_hash, projection.state)
