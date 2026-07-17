from dataclasses import dataclass

from .registry import FactorRegistryEvidence


@dataclass(frozen=True)
class FactorRegistryAcceptance:
    status: str
    evidence_hash: str
    operator_review_required: bool
    factor_activation_allowed: bool
    order_or_execution_allowed: bool


def build_operator_acceptance(
    evidence: FactorRegistryEvidence,
) -> FactorRegistryAcceptance:
    return FactorRegistryAcceptance(
        "WAITING_FOR_OPERATOR_REVIEW" if evidence.state == "REGISTRY_READY" else "BLOCKED",
        evidence.evidence_hash,
        True,
        False,
        False,
    )
