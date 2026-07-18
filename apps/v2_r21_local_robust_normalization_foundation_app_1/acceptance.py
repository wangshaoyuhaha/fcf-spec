from dataclasses import dataclass
from .normalization import NormalizationEvidence


@dataclass(frozen=True)
class NormalizationAcceptance:
    status: str
    evidence_hash: str
    operator_review_required: bool
    score_rank_or_recommendation_allowed: bool
    order_or_execution_allowed: bool


def build_operator_acceptance(evidence: NormalizationEvidence) -> NormalizationAcceptance:
    return NormalizationAcceptance("WAITING_FOR_OPERATOR_REVIEW" if evidence.state in {"NORMALIZATION_READY", "MISSING_STATE_RECORDED"} else "BLOCKED", evidence.evidence_hash, True, False, False)
