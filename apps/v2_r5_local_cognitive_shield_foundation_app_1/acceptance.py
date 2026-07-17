from __future__ import annotations

from dataclasses import dataclass

from .shield import CognitiveShieldEvidence


@dataclass(frozen=True)
class V2R5OperatorAcceptance:
    task_id: str
    shield_evidence_hash: str
    status: str
    operator_review_required: bool = True
    automatic_approval: bool = False


def build_operator_acceptance(
    evidence: CognitiveShieldEvidence,
) -> V2R5OperatorAcceptance:
    return V2R5OperatorAcceptance(
        task_id=evidence.task_id,
        shield_evidence_hash=evidence.shield_evidence_hash,
        status="WAITING_FOR_OPERATOR_REVIEW",
    )
