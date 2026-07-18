from dataclasses import dataclass

from .resolver import PolicyLanguageEvidenceSnapshot


@dataclass(frozen=True)
class V2R34OperatorAcceptance:
    snapshot_hash: str
    snapshot_state: str
    status: str = "WAITING_FOR_OPERATOR_REVIEW"
    operator_review_required: bool = True
    automatic_approval: bool = False
    semantic_direction: bool = False
    industry_benefit: bool = False
    policy_causation: bool = False
    automatic_taxonomy_mapping: bool = False
    factor_activated: bool = False
    action_created: bool = False


def build_operator_acceptance(snapshot: PolicyLanguageEvidenceSnapshot) -> V2R34OperatorAcceptance:
    return V2R34OperatorAcceptance(snapshot.snapshot_hash, snapshot.state)
