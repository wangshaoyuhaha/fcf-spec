from dataclasses import dataclass

from .contracts import BrowserGovernanceReviewMarketSummary


@dataclass(frozen=True)
class V2R47GovernanceReviewMarketSummaryAcceptance:
    status: str
    market_count: int
    queue_item_count: int
    covered_item_count: int
    missing_evidence_count: int
    read_only: bool = True
    operator_review_required: bool = True
    action_created: bool = False


def build_governance_review_market_summary_acceptance(summary: BrowserGovernanceReviewMarketSummary) -> V2R47GovernanceReviewMarketSummaryAcceptance:
    if not isinstance(summary, BrowserGovernanceReviewMarketSummary):
        raise ValueError("governance review market summary is required")
    return V2R47GovernanceReviewMarketSummaryAcceptance(
        status="PASSED_READ_ONLY_REVIEW_MARKET_SUMMARY",
        market_count=summary.market_count,
        queue_item_count=summary.queue_item_count,
        covered_item_count=summary.covered_item_count,
        missing_evidence_count=summary.missing_evidence_count,
    )
