from dataclasses import dataclass

from .resolver import IndexFuturesBasisRollExpirySnapshot


@dataclass(frozen=True)
class V2R29OperatorAcceptance:
    snapshot_hash: str
    snapshot_state: str
    status: str = "WAITING_FOR_OPERATOR_REVIEW"
    operator_review_required: bool = True
    automatic_approval: bool = False
    bottom_claim: bool = False
    participant_intent_claim: bool = False
    factor_activated: bool = False
    action_created: bool = False


def build_operator_acceptance(
    snapshot: IndexFuturesBasisRollExpirySnapshot,
) -> V2R29OperatorAcceptance:
    return V2R29OperatorAcceptance(snapshot.snapshot_hash, snapshot.state)
