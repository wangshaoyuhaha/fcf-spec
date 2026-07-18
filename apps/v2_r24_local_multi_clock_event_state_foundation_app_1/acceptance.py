from dataclasses import dataclass

from .resolver import MultiClockEventStateSnapshot


@dataclass(frozen=True)
class V2R24OperatorAcceptance:
    snapshot_hash: str
    snapshot_state: str
    status: str = "WAITING_FOR_OPERATOR_REVIEW"
    operator_review_required: bool = True
    automatic_approval: bool = False
    action_created: bool = False


def build_operator_acceptance(
    snapshot: MultiClockEventStateSnapshot,
) -> V2R24OperatorAcceptance:
    return V2R24OperatorAcceptance(
        snapshot_hash=snapshot.snapshot_hash,
        snapshot_state=snapshot.state,
    )
