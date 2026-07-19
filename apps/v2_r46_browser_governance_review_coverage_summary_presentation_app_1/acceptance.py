from dataclasses import dataclass

from .contracts import BrowserGovernanceReviewCoverageSummary


@dataclass(frozen=True)
class V2R46GovernanceReviewCoverageSummaryAcceptance:
    status: str
    queue_item_count: int
    covered_item_count: int
    missing_evidence_count: int
    source_snapshot_count: int
    read_only: bool = True
    operator_review_required: bool = True
    action_created: bool = False


def build_governance_review_coverage_summary_acceptance(
    summary: BrowserGovernanceReviewCoverageSummary,
) -> V2R46GovernanceReviewCoverageSummaryAcceptance:
    if not isinstance(summary, BrowserGovernanceReviewCoverageSummary):
        raise ValueError("governance review coverage summary is required")
    return V2R46GovernanceReviewCoverageSummaryAcceptance(
        status="PASSED_READ_ONLY_REGISTERED_EVIDENCE_COVERAGE_SUMMARY",
        queue_item_count=summary.queue_item_count,
        covered_item_count=summary.covered_item_count,
        missing_evidence_count=summary.missing_evidence_count,
        source_snapshot_count=summary.source_snapshot_count,
    )
