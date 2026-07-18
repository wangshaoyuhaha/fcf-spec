from dataclasses import dataclass

from .resolver import FactorLifecycleSnapshot


@dataclass(frozen=True)
class V2R36OperatorAcceptance:
    snapshot_hash: str
    snapshot_state: str
    status: str = "WAITING_FOR_OPERATOR_REVIEW"
    operator_review_required: bool = True
    automatic_approval: bool = False
    factor_activated: bool = False
    score_created: bool = False
    action_created: bool = False


def build_operator_acceptance(snapshot: FactorLifecycleSnapshot) -> V2R36OperatorAcceptance:
    return V2R36OperatorAcceptance(snapshot.snapshot_hash, snapshot.state)
