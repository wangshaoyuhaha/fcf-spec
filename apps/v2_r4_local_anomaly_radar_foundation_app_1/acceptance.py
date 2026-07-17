from __future__ import annotations

from dataclasses import dataclass

from .ledger import ResearchAlertLedger


@dataclass(frozen=True)
class V2R4OperatorAcceptance:
    status: str
    record_count: int
    confirmed_count: int
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
    ledger: ResearchAlertLedger,
) -> V2R4OperatorAcceptance:
    confirmed = sum(record.state == "CONFIRMED" for record in ledger.records)
    return V2R4OperatorAcceptance(
        status="READY_FOR_OPERATOR_REVIEW" if ledger.records else "BLOCKED",
        record_count=len(ledger.records),
        confirmed_count=confirmed,
    )
