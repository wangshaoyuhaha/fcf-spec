from __future__ import annotations

from dataclasses import dataclass

from .ingress import BoundedLocalEventIngress
from .replay import ReplayCheckpoint, events_hash


@dataclass(frozen=True)
class V2R3OperatorAcceptance:
    status: str
    event_count: int
    checkpoint_hash: str
    operator_review_required: bool = True
    automatic_approval_allowed: bool = False

    def __post_init__(self) -> None:
        if self.status not in {"READY_FOR_OPERATOR_REVIEW", "BLOCKED"}:
            raise ValueError("invalid Operator acceptance status")
        if self.operator_review_required is not True:
            raise ValueError("Operator review must remain required")
        if self.automatic_approval_allowed is not False:
            raise ValueError("automatic approval is prohibited")


def build_operator_acceptance(
    ingress: BoundedLocalEventIngress,
    checkpoint: ReplayCheckpoint,
) -> V2R3OperatorAcceptance:
    ready = (
        checkpoint.event_count == len(ingress.events)
        and checkpoint.events_hash == events_hash(ingress.events)
        and dict(checkpoint.last_sequences) == dict(ingress.last_sequences)
    )
    return V2R3OperatorAcceptance(
        status="READY_FOR_OPERATOR_REVIEW" if ready else "BLOCKED",
        event_count=len(ingress.events),
        checkpoint_hash=checkpoint.events_hash,
    )
