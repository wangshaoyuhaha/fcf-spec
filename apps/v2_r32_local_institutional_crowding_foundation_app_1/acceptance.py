from dataclasses import dataclass

from .resolver import InstitutionalCrowdingSnapshot


@dataclass(frozen=True)
class V2R32OperatorAcceptance:
    snapshot_hash: str
    snapshot_state: str
    status: str = "WAITING_FOR_OPERATOR_REVIEW"
    operator_review_required: bool = True
    automatic_approval: bool = False
    current_manager_action_inference: bool = False
    quarter_end_motive_inference: bool = False
    manipulation_claim: bool = False
    factor_activated: bool = False
    action_created: bool = False


def build_operator_acceptance(
    snapshot: InstitutionalCrowdingSnapshot,
) -> V2R32OperatorAcceptance:
    return V2R32OperatorAcceptance(snapshot.snapshot_hash, snapshot.state)
