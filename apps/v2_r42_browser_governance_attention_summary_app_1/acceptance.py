from dataclasses import dataclass

from .contracts import BrowserGovernanceAttentionSummary


@dataclass(frozen=True)
class V2R42GovernanceAttentionAcceptance:
    status: str
    projection_count: int
    review_required_count: int
    read_only: bool = True
    operator_review_required: bool = True
    action_created: bool = False


def build_governance_attention_acceptance(
    summary: BrowserGovernanceAttentionSummary,
) -> V2R42GovernanceAttentionAcceptance:
    if not isinstance(summary, BrowserGovernanceAttentionSummary):
        raise ValueError("governance attention summary is required")
    return V2R42GovernanceAttentionAcceptance(
        status="PASSED_READ_ONLY_ATTENTION_SUMMARY",
        projection_count=summary.projection_count,
        review_required_count=summary.operator_review_required_count,
    )
