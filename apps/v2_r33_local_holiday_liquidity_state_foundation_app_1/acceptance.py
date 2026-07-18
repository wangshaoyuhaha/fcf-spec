from dataclasses import dataclass

from .resolver import HolidayLiquiditySnapshot


@dataclass(frozen=True)
class V2R33OperatorAcceptance:
    snapshot_hash: str
    snapshot_state: str
    status: str = "WAITING_FOR_OPERATOR_REVIEW"
    operator_review_required: bool = True
    automatic_approval: bool = False
    fixed_last_three_days_rule: bool = False
    fixed_threshold: bool = False
    stress_direction: bool = False
    factor_activated: bool = False
    action_created: bool = False


def build_operator_acceptance(
    snapshot: HolidayLiquiditySnapshot,
) -> V2R33OperatorAcceptance:
    return V2R33OperatorAcceptance(snapshot.snapshot_hash, snapshot.state)
