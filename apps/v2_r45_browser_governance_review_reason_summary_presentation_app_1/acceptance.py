from dataclasses import dataclass

from .contracts import BrowserGovernanceReviewReasonSummary


@dataclass(frozen=True)
class V2R45GovernanceReviewReasonSummaryAcceptance:
    status: str
    unique_reason_count: int
    reason_occurrence_count: int
    read_only: bool = True
    operator_review_required: bool = True
    action_created: bool = False


def build_governance_review_reason_summary_acceptance(
    summary: BrowserGovernanceReviewReasonSummary,
) -> V2R45GovernanceReviewReasonSummaryAcceptance:
    if not isinstance(summary, BrowserGovernanceReviewReasonSummary):
        raise ValueError("governance review reason summary is required")
    return V2R45GovernanceReviewReasonSummaryAcceptance(
        status="PASSED_READ_ONLY_REVIEW_REASON_SUMMARY",
        unique_reason_count=summary.unique_reason_count,
        reason_occurrence_count=summary.reason_occurrence_count,
    )
