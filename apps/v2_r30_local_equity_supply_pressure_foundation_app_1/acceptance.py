from dataclasses import dataclass

from .resolver import EquitySupplyPressureSnapshot


@dataclass(frozen=True)
class V2R30OperatorAcceptance:
    snapshot_hash: str
    snapshot_state: str
    status: str = "WAITING_FOR_OPERATOR_REVIEW"
    operator_review_required: bool = True
    automatic_approval: bool = False
    unlock_equals_sale_claim: bool = False
    forced_sale_claim: bool = False
    holder_intent_claim: bool = False
    factor_activated: bool = False
    action_created: bool = False


def build_operator_acceptance(snapshot: EquitySupplyPressureSnapshot) -> V2R30OperatorAcceptance:
    return V2R30OperatorAcceptance(snapshot.snapshot_hash, snapshot.state)
