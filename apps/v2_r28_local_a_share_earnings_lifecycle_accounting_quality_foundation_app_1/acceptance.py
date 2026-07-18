from dataclasses import dataclass
from .resolver import EarningsAccountingQualitySnapshot


@dataclass(frozen=True)
class V2R28OperatorAcceptance:
    snapshot_hash: str
    snapshot_state: str
    status: str = "WAITING_FOR_OPERATOR_REVIEW"
    operator_review_required: bool = True
    automatic_approval: bool = False
    fraud_conclusion: bool = False
    factor_activated: bool = False
    action_created: bool = False


def build_operator_acceptance(snapshot: EarningsAccountingQualitySnapshot) -> V2R28OperatorAcceptance:
    return V2R28OperatorAcceptance(snapshot.snapshot_hash, snapshot.state)
