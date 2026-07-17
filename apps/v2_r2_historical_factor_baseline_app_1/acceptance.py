from __future__ import annotations

from dataclasses import dataclass

from .baseline import HistoricalBaseline


@dataclass(frozen=True)
class V2R2OperatorAcceptance:
    status: str
    replay_hash: str
    operator_review_required: bool = True
    automatic_approval_allowed: bool = False

    def __post_init__(self) -> None:
        if self.status not in {"READY_FOR_OPERATOR_REVIEW", "BLOCKED"}:
            raise ValueError("invalid Operator acceptance status")
        if self.operator_review_required is not True:
            raise ValueError("Operator review must remain required")
        if self.automatic_approval_allowed is not False:
            raise ValueError("automatic approval is prohibited")


def build_operator_acceptance(baseline: HistoricalBaseline) -> V2R2OperatorAcceptance:
    return V2R2OperatorAcceptance(
        status=(
            "READY_FOR_OPERATOR_REVIEW"
            if baseline.status == "READY"
            else "BLOCKED"
        ),
        replay_hash=baseline.replay_hash,
    )
