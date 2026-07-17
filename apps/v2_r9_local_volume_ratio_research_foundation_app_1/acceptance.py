from __future__ import annotations

from dataclasses import dataclass

from .ratio import VolumeRatioEvidence


@dataclass(frozen=True)
class V2R9OperatorAcceptance:
    evidence_hash: str
    status: str
    operator_review_required: bool = True
    automatic_approval: bool = False
    factor_activated: bool = False


def build_operator_acceptance(evidence: VolumeRatioEvidence) -> V2R9OperatorAcceptance:
    return V2R9OperatorAcceptance(
        evidence_hash=evidence.evidence_hash,
        status="WAITING_FOR_OPERATOR_REVIEW",
    )
