from __future__ import annotations

from dataclasses import dataclass

from .resolver import SessionResolutionEvidence


@dataclass(frozen=True)
class V2R7OperatorAcceptance:
    evidence_hash: str
    status: str
    operator_review_required: bool = True
    automatic_approval: bool = False
    action_created: bool = False


def build_operator_acceptance(
    evidence: SessionResolutionEvidence,
) -> V2R7OperatorAcceptance:
    return V2R7OperatorAcceptance(
        evidence_hash=evidence.evidence_hash,
        status="WAITING_FOR_OPERATOR_REVIEW",
    )
